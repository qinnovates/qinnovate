"""
Adaptive Leaky Integrate-and-Fire (AdEx/ALIF) Neuron Model

Extends LIF with spike-frequency adaptation, allowing neurons
to decrease their firing rate over sustained input.

Equations:
    τ_m * dV/dt = -(V - V_rest) + R_m * I - w
    τ_w * dw/dt = a(V - V_rest) - w

After spike:
    w = w + b

Reference:
    Brette, R., & Gerstner, W. (2005). Adaptive exponential
    integrate-and-fire model. Journal of Neurophysiology.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np

from .base import Neuron, NeuronParameters, NeuronType


@dataclass
class AdaptiveLIFParameters(NeuronParameters):
    """Parameters for Adaptive LIF neuron."""

    # Membrane properties
    R_m: float = 10.0     # Membrane resistance (MΩ)
    C_m: float = 1.0      # Membrane capacitance (nF)
    tau_m: float = None   # Membrane time constant (ms)

    # Voltage thresholds
    V_rest: float = -65.0      # Resting potential (mV)
    V_threshold: float = -50.0  # Spike threshold (mV)
    V_reset: float = -65.0      # Reset potential (mV)

    # Adaptation parameters
    a: float = 0.0        # Subthreshold adaptation conductance (nS)
    b: float = 0.5        # Spike-triggered adaptation increment (nA)
    tau_w: float = 100.0  # Adaptation time constant (ms)

    # Exponential spike (for AdEx variant)
    delta_T: float = 0.0  # Slope factor (mV), 0 = no exponential
    V_T: float = -50.0    # Soft threshold for exponential (mV)

    # Refractory period
    t_refractory: float = 2.0  # Absolute refractory period (ms)

    # Noise
    noise_std: float = 0.0

    def __post_init__(self):
        """Compute derived parameters."""
        if self.tau_m is None:
            self.tau_m = self.R_m * self.C_m

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "R_m": self.R_m,
            "tau_m": self.tau_m,
            "V_rest": self.V_rest,
            "V_threshold": self.V_threshold,
            "V_reset": self.V_reset,
            "a": self.a,
            "b": self.b,
            "tau_w": self.tau_w,
            "delta_T": self.delta_T,
            "t_refractory": self.t_refractory,
        })
        return base


class AdaptiveLIFNeuron(Neuron):
    """
    Adaptive Leaky Integrate-and-Fire Neuron.

    Includes spike-frequency adaptation where repeated spiking
    leads to decreased excitability. This produces more realistic
    responses to sustained input.

    The adaptation current w:
    - Increases after each spike by amount b
    - Decays exponentially with time constant tau_w
    - Acts as a hyperpolarizing current

    Usage:
        >>> neuron = AdaptiveLIFNeuron()
        >>> results = neuron.simulate(1000, input_current=np.ones(10000) * 3.0)
        >>> # Note how firing rate decreases over time (adaptation)
    """

    def __init__(self, params: Optional[AdaptiveLIFParameters] = None):
        """
        Initialize Adaptive LIF neuron.

        Args:
            params: Model parameters (uses defaults if None)
        """
        super().__init__(params or AdaptiveLIFParameters())

        # Initialize state
        self.state.V = self.params.V_rest
        self.w = 0.0  # Adaptation current
        self.w_history = []

    @property
    def params(self) -> AdaptiveLIFParameters:
        """Type-hinted access to parameters."""
        return self._params

    @params.setter
    def params(self, value: AdaptiveLIFParameters):
        self._params = value

    def get_V_rest(self) -> float:
        """Get resting membrane potential."""
        return self.params.V_rest

    def _compute_dV(self, I_total: float) -> float:
        """
        Compute membrane potential change with adaptation.
        """
        p = self.params
        dt = p.dt
        V = self.state.V

        # Compute exponential term if delta_T > 0 (AdEx model)
        if p.delta_T > 0:
            exp_term = p.delta_T * np.exp((V - p.V_T) / p.delta_T)
        else:
            exp_term = 0.0

        # Membrane potential dynamics
        # τ_m * dV/dt = -(V - V_rest) + exp_term + R_m * I - R_m * w
        dV = (
            -(V - p.V_rest)
            + exp_term
            + p.R_m * I_total
            - p.R_m * self.w
        ) / p.tau_m * dt

        # Adaptation dynamics
        # τ_w * dw/dt = a(V - V_rest) - w
        dw = (p.a * (V - p.V_rest) - self.w) / p.tau_w * dt
        self.w += dw

        # Add noise if specified
        if p.noise_std > 0:
            dV += np.random.normal(0, p.noise_std * np.sqrt(dt))

        return dV

    def _check_spike(self) -> bool:
        """Check if membrane potential exceeds threshold."""
        return self.state.V >= self.params.V_threshold

    def _reset_after_spike(self):
        """Reset V and increment adaptation after spike."""
        self.state.V = self.params.V_reset
        self.w += self.params.b  # Spike-triggered adaptation
        self.state.refractory_remaining = self.params.t_refractory

    def step(self, record_history: bool = True) -> bool:
        """Override step to also record w history."""
        result = super().step(record_history)
        if record_history:
            self.w_history.append(self.w)
        return result

    def reset(self):
        """Reset neuron to initial state."""
        super().reset()
        self.w = 0.0
        self.w_history = []

    def simulate(
        self,
        duration: float,
        input_current: Optional[np.ndarray] = None,
        record_history: bool = True
    ) -> Dict[str, np.ndarray]:
        """Run simulation and include adaptation variable."""
        results = super().simulate(duration, input_current, record_history)
        if record_history:
            results["w"] = np.array(self.w_history)
        return results

    @classmethod
    def create_adapting(cls, **kwargs) -> "AdaptiveLIFNeuron":
        """Create neuron with strong adaptation."""
        params = AdaptiveLIFParameters(
            a=0.0,
            b=1.0,
            tau_w=150.0,
            **kwargs
        )
        return cls(params)

    @classmethod
    def create_bursting(cls, **kwargs) -> "AdaptiveLIFNeuron":
        """Create neuron with bursting behavior (AdEx variant)."""
        params = AdaptiveLIFParameters(
            delta_T=2.0,
            V_T=-55.0,
            V_threshold=-40.0,
            a=0.5,
            b=0.1,
            tau_w=50.0,
            **kwargs
        )
        return cls(params)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize neuron to dictionary."""
        data = super().to_dict()
        data["state"]["w"] = self.w
        return data
