"""
Spike-Timing Dependent Plasticity (STDP) Synapse Model

Implements learning rules based on relative timing of pre- and
postsynaptic spikes. This is a key mechanism for synaptic plasticity
and learning in neural networks.

Classic STDP rule:
    Δw = A+ * exp(-Δt/τ+)  if Δt > 0 (pre before post → LTP)
    Δw = -A- * exp(Δt/τ-)  if Δt < 0 (post before pre → LTD)

Where Δt = t_post - t_pre
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from enum import Enum
import numpy as np

from .base import Synapse, SynapseParameters, SynapseType, SynapseState
from .chemical import ChemicalSynapse, ChemicalSynapseParameters, ReceptorType

if TYPE_CHECKING:
    from ..neurons.base import Neuron


class STDPType(Enum):
    """Types of STDP learning rules."""
    CLASSIC = "classic"           # Asymmetric Hebbian
    SYMMETRIC = "symmetric"       # Symmetric (both LTP)
    ANTI_HEBBIAN = "anti_hebbian" # Inverted classic rule
    TRIPLET = "triplet"           # Triplet-based rule


@dataclass
class STDPParameters(ChemicalSynapseParameters):
    """Parameters for STDP synapse."""

    # STDP rule type
    stdp_type: STDPType = STDPType.CLASSIC

    # Learning rates
    A_plus: float = 0.01      # LTP amplitude
    A_minus: float = 0.012    # LTD amplitude (slightly larger for stability)

    # Time constants (ms)
    tau_plus: float = 20.0    # LTP time constant
    tau_minus: float = 20.0   # LTD time constant

    # Weight bounds
    w_min: float = 0.0        # Minimum weight
    w_max: float = 2.0        # Maximum weight

    # Learning modulation
    learning_rate: float = 1.0  # Global learning rate multiplier
    enabled: bool = True        # Enable/disable plasticity

    # Eligibility trace (for reward-modulated STDP)
    use_eligibility: bool = False
    tau_eligibility: float = 100.0  # Eligibility trace time constant

    # Triplet rule parameters (if stdp_type == TRIPLET)
    A2_plus: float = 0.005    # Triplet LTP term
    A2_minus: float = 0.007   # Triplet LTD term
    tau_x: float = 100.0      # Presynaptic triplet trace
    tau_y: float = 100.0      # Postsynaptic triplet trace

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "stdp_type": self.stdp_type.value,
            "A_plus": self.A_plus,
            "A_minus": self.A_minus,
            "tau_plus": self.tau_plus,
            "tau_minus": self.tau_minus,
            "w_min": self.w_min,
            "w_max": self.w_max,
            "learning_rate": self.learning_rate,
            "enabled": self.enabled,
        })
        return base


@dataclass
class STDPState:
    """State variables for STDP."""

    # Spike traces
    pre_trace: float = 0.0    # Presynaptic trace
    post_trace: float = 0.0   # Postsynaptic trace

    # Triplet traces (for triplet rule)
    pre_trace_slow: float = 0.0
    post_trace_slow: float = 0.0

    # Eligibility trace (for reward-modulated learning)
    eligibility: float = 0.0

    # Learning statistics
    total_ltp: float = 0.0    # Cumulative LTP
    total_ltd: float = 0.0    # Cumulative LTD
    weight_history: List[float] = None

    def __post_init__(self):
        if self.weight_history is None:
            self.weight_history = []

    def reset(self):
        """Reset STDP state."""
        self.pre_trace = 0.0
        self.post_trace = 0.0
        self.pre_trace_slow = 0.0
        self.post_trace_slow = 0.0
        self.eligibility = 0.0
        self.total_ltp = 0.0
        self.total_ltd = 0.0
        self.weight_history = []


class STDPSynapse(ChemicalSynapse):
    """
    Synapse with Spike-Timing Dependent Plasticity.

    Extends ChemicalSynapse with learning capabilities based on
    the relative timing of pre- and postsynaptic spikes.

    The classic STDP rule produces:
    - LTP (Long-Term Potentiation): when pre fires before post
    - LTD (Long-Term Depression): when post fires before pre

    Usage:
        >>> synapse = STDPSynapse(pre, post)
        >>> # Weight will change based on spike timing during simulation
        >>> # After learning:
        >>> print(f"Weight changed from 1.0 to {synapse.weight}")
    """

    def __init__(
        self,
        pre: "Neuron",
        post: "Neuron",
        params: Optional[STDPParameters] = None
    ):
        """
        Initialize STDP synapse.

        Args:
            pre: Presynaptic neuron
            post: Postsynaptic neuron
            params: STDP parameters
        """
        super().__init__(pre, post, params or STDPParameters())

        # STDP-specific state
        self.stdp_state = STDPState()

        # Register for postsynaptic spikes (for STDP)
        post.on_spike(self._on_post_spike)

        # Store initial weight
        self.stdp_state.weight_history.append(self.params.weight)

    @property
    def params(self) -> STDPParameters:
        """Type-hinted access to parameters."""
        return self._params

    @params.setter
    def params(self, value: STDPParameters):
        self._params = value

    def _on_pre_spike(self, neuron: "Neuron", spike_time: float):
        """Handle presynaptic spike - update trace and apply LTD."""
        super()._on_pre_spike(neuron, spike_time)

        if not self.params.enabled:
            return

        p = self.params

        # Update presynaptic trace
        self.stdp_state.pre_trace += 1.0

        # For triplet rule
        if p.stdp_type == STDPType.TRIPLET:
            self.stdp_state.pre_trace_slow += 1.0

        # Apply LTD based on postsynaptic trace
        if p.stdp_type == STDPType.CLASSIC:
            dw = -p.A_minus * self.stdp_state.post_trace * p.learning_rate
            self._update_weight(dw)
            if dw < 0:
                self.stdp_state.total_ltd += abs(dw)

        elif p.stdp_type == STDPType.SYMMETRIC:
            # Symmetric rule: both pre-post and post-pre cause LTP
            dw = p.A_plus * self.stdp_state.post_trace * p.learning_rate
            self._update_weight(dw)
            if dw > 0:
                self.stdp_state.total_ltp += dw

        elif p.stdp_type == STDPType.ANTI_HEBBIAN:
            # Inverted: pre-before-post causes LTD
            dw = p.A_minus * self.stdp_state.post_trace * p.learning_rate
            self._update_weight(dw)
            if dw > 0:
                self.stdp_state.total_ltp += dw

        elif p.stdp_type == STDPType.TRIPLET:
            # Triplet LTD: depends on post trace and slow pre trace
            dw = -p.A_minus * self.stdp_state.post_trace * p.learning_rate
            dw -= p.A2_minus * self.stdp_state.post_trace * self.stdp_state.pre_trace_slow * p.learning_rate
            self._update_weight(dw)
            if dw < 0:
                self.stdp_state.total_ltd += abs(dw)

        # Update eligibility trace if enabled
        if p.use_eligibility:
            self.stdp_state.eligibility += self.stdp_state.post_trace

    def _on_post_spike(self, neuron: "Neuron", spike_time: float):
        """Handle postsynaptic spike - update trace and apply LTP."""
        if not self.params.enabled:
            return

        p = self.params

        # Update postsynaptic trace
        self.stdp_state.post_trace += 1.0

        # For triplet rule
        if p.stdp_type == STDPType.TRIPLET:
            self.stdp_state.post_trace_slow += 1.0

        # Apply LTP based on presynaptic trace
        if p.stdp_type == STDPType.CLASSIC:
            dw = p.A_plus * self.stdp_state.pre_trace * p.learning_rate
            self._update_weight(dw)
            if dw > 0:
                self.stdp_state.total_ltp += dw

        elif p.stdp_type == STDPType.SYMMETRIC:
            dw = p.A_plus * self.stdp_state.pre_trace * p.learning_rate
            self._update_weight(dw)
            if dw > 0:
                self.stdp_state.total_ltp += dw

        elif p.stdp_type == STDPType.ANTI_HEBBIAN:
            # Inverted: post-before-pre causes LTP
            dw = -p.A_plus * self.stdp_state.pre_trace * p.learning_rate
            self._update_weight(dw)
            if dw < 0:
                self.stdp_state.total_ltd += abs(dw)

        elif p.stdp_type == STDPType.TRIPLET:
            # Triplet LTP: depends on pre trace and slow post trace
            dw = p.A_plus * self.stdp_state.pre_trace * p.learning_rate
            dw += p.A2_plus * self.stdp_state.pre_trace * self.stdp_state.post_trace_slow * p.learning_rate
            self._update_weight(dw)
            if dw > 0:
                self.stdp_state.total_ltp += dw

        # Update eligibility trace if enabled
        if p.use_eligibility:
            self.stdp_state.eligibility += self.stdp_state.pre_trace

    def _update_weight(self, dw: float):
        """Update synaptic weight with bounds checking."""
        p = self.params
        new_weight = np.clip(
            self.params.weight + dw,
            p.w_min,
            p.w_max
        )
        self.params.weight = new_weight

    def _compute_current(self, t: float) -> float:
        """Compute synaptic current and decay traces."""
        p = self.params
        dt = p.dt

        # Decay spike traces
        self.stdp_state.pre_trace -= self.stdp_state.pre_trace / p.tau_plus * dt
        self.stdp_state.post_trace -= self.stdp_state.post_trace / p.tau_minus * dt

        # Decay triplet traces
        if p.stdp_type == STDPType.TRIPLET:
            self.stdp_state.pre_trace_slow -= self.stdp_state.pre_trace_slow / p.tau_x * dt
            self.stdp_state.post_trace_slow -= self.stdp_state.post_trace_slow / p.tau_y * dt

        # Decay eligibility trace
        if p.use_eligibility:
            self.stdp_state.eligibility -= self.stdp_state.eligibility / p.tau_eligibility * dt

        # Compute current from parent class
        return super()._compute_current(t)

    def apply_reward(self, reward: float):
        """
        Apply reward signal for reward-modulated STDP.

        In reward-modulated STDP, weight changes are gated by
        a reward signal (e.g., dopamine).

        Args:
            reward: Reward signal (positive or negative)
        """
        if self.params.use_eligibility:
            dw = reward * self.stdp_state.eligibility * self.params.learning_rate
            self._update_weight(dw)

    def step(self, t: float) -> float:
        """Step synapse and record weight."""
        I = super().step(t)

        # Record weight history periodically
        self.stdp_state.weight_history.append(self.params.weight)

        return I

    def reset(self):
        """Reset synapse state including STDP variables."""
        super().reset()
        self.stdp_state.reset()
        self.stdp_state.weight_history.append(self.params.weight)

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics."""
        return {
            "current_weight": self.params.weight,
            "initial_weight": self.stdp_state.weight_history[0] if self.stdp_state.weight_history else 1.0,
            "total_ltp": self.stdp_state.total_ltp,
            "total_ltd": self.stdp_state.total_ltd,
            "net_change": self.stdp_state.total_ltp - self.stdp_state.total_ltd,
            "weight_history": self.stdp_state.weight_history,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize synapse."""
        data = super().to_dict()
        data["stdp_state"] = {
            "pre_trace": self.stdp_state.pre_trace,
            "post_trace": self.stdp_state.post_trace,
            "total_ltp": self.stdp_state.total_ltp,
            "total_ltd": self.stdp_state.total_ltd,
        }
        return data

    @classmethod
    def create_hebbian(
        cls,
        pre: "Neuron",
        post: "Neuron",
        weight: float = 1.0,
        **kwargs
    ) -> "STDPSynapse":
        """Create synapse with classic Hebbian STDP."""
        params = STDPParameters(
            receptor=ReceptorType.AMPA,
            weight=weight,
            stdp_type=STDPType.CLASSIC,
            **kwargs
        )
        return cls(pre, post, params)

    @classmethod
    def create_reward_modulated(
        cls,
        pre: "Neuron",
        post: "Neuron",
        weight: float = 1.0,
        **kwargs
    ) -> "STDPSynapse":
        """Create synapse with reward-modulated STDP."""
        params = STDPParameters(
            receptor=ReceptorType.AMPA,
            weight=weight,
            stdp_type=STDPType.CLASSIC,
            use_eligibility=True,
            tau_eligibility=100.0,
            **kwargs
        )
        return cls(pre, post, params)

    @classmethod
    def create_triplet(
        cls,
        pre: "Neuron",
        post: "Neuron",
        weight: float = 1.0,
        **kwargs
    ) -> "STDPSynapse":
        """Create synapse with triplet STDP rule."""
        params = STDPParameters(
            receptor=ReceptorType.AMPA,
            weight=weight,
            stdp_type=STDPType.TRIPLET,
            **kwargs
        )
        return cls(pre, post, params)
