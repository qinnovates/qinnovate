"""
Chemical Synapse Model

Models standard chemical synaptic transmission with:
- Exponential or double-exponential conductance dynamics
- Reversal potential (for AMPA, NMDA, GABA types)
- Short-term plasticity (facilitation/depression)
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, TYPE_CHECKING
from enum import Enum
import numpy as np

from .base import Synapse, SynapseParameters, SynapseType

if TYPE_CHECKING:
    from ..neurons.base import Neuron


class ReceptorType(Enum):
    """Common receptor types with typical parameters."""
    AMPA = "ampa"           # Fast excitatory
    NMDA = "nmda"           # Slow excitatory, voltage-dependent
    GABA_A = "gaba_a"       # Fast inhibitory
    GABA_B = "gaba_b"       # Slow inhibitory


# Default parameters for receptor types
RECEPTOR_DEFAULTS = {
    ReceptorType.AMPA: {
        "tau_rise": 0.5,
        "tau_decay": 2.0,
        "E_rev": 0.0,
        "g_max": 0.5,
    },
    ReceptorType.NMDA: {
        "tau_rise": 2.0,
        "tau_decay": 100.0,
        "E_rev": 0.0,
        "g_max": 0.2,
    },
    ReceptorType.GABA_A: {
        "tau_rise": 0.5,
        "tau_decay": 5.0,
        "E_rev": -70.0,
        "g_max": 0.5,
    },
    ReceptorType.GABA_B: {
        "tau_rise": 10.0,
        "tau_decay": 100.0,
        "E_rev": -90.0,
        "g_max": 0.1,
    },
}


@dataclass
class ChemicalSynapseParameters(SynapseParameters):
    """Parameters for chemical synapse."""

    # Receptor type
    receptor: ReceptorType = ReceptorType.AMPA

    # Conductance dynamics
    tau_rise: float = 0.5      # Rise time constant (ms)
    tau_decay: float = 2.0     # Decay time constant (ms)
    g_max: float = 0.5         # Maximum conductance (nS)

    # Reversal potential
    E_rev: float = 0.0         # Reversal potential (mV)

    # Short-term plasticity (optional)
    use_stp: bool = False
    U: float = 0.5             # Baseline release probability
    tau_rec: float = 100.0     # Recovery time constant (ms)
    tau_fac: float = 50.0      # Facilitation time constant (ms)

    @classmethod
    def from_receptor(
        cls,
        receptor: ReceptorType,
        **kwargs
    ) -> "ChemicalSynapseParameters":
        """Create parameters from receptor type."""
        defaults = RECEPTOR_DEFAULTS.get(receptor, {})
        synapse_type = (
            SynapseType.EXCITATORY if receptor in [ReceptorType.AMPA, ReceptorType.NMDA]
            else SynapseType.INHIBITORY
        )
        return cls(
            receptor=receptor,
            synapse_type=synapse_type,
            **{**defaults, **kwargs}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "receptor": self.receptor.value,
            "tau_rise": self.tau_rise,
            "tau_decay": self.tau_decay,
            "g_max": self.g_max,
            "E_rev": self.E_rev,
            "use_stp": self.use_stp,
        })
        return base


class ChemicalSynapse(Synapse):
    """
    Chemical Synapse with conductance-based dynamics.

    Models standard chemical synaptic transmission using
    double-exponential conductance waveform:

        g(t) = g_max * (exp(-t/τ_decay) - exp(-t/τ_rise))

    Current is computed as:
        I = g(t) * (V_post - E_rev)

    Usage:
        >>> synapse = ChemicalSynapse.create_ampa(pre, post)
        >>> synapse = ChemicalSynapse.create_gaba(pre, post)
    """

    def __init__(
        self,
        pre: "Neuron",
        post: "Neuron",
        params: Optional[ChemicalSynapseParameters] = None
    ):
        """
        Initialize chemical synapse.

        Args:
            pre: Presynaptic neuron
            post: Postsynaptic neuron
            params: Synapse parameters
        """
        super().__init__(pre, post, params or ChemicalSynapseParameters())

        # Conductance state variables (for double-exponential)
        self.g_rise = 0.0
        self.g_decay = 0.0

        # Short-term plasticity variables
        self.x = 1.0    # Available resources
        self.u = self.params.U  # Release probability

    @property
    def params(self) -> ChemicalSynapseParameters:
        """Type-hinted access to parameters."""
        return self._params

    @params.setter
    def params(self, value: ChemicalSynapseParameters):
        self._params = value

    def _on_spike_arrival(self, spike_time: float):
        """Handle spike arrival - increase conductance."""
        p = self.params

        # Compute synaptic efficacy with STP
        if p.use_stp:
            # Facilitation
            self.u = self.u + p.U * (1 - self.u)
            # Depression
            efficacy = self.u * self.x
            self.x = self.x - efficacy
        else:
            efficacy = 1.0

        # Increment conductances
        delta_g = p.g_max * p.weight * efficacy
        self.g_rise += delta_g
        self.g_decay += delta_g

    def _compute_current(self, t: float) -> float:
        """Compute synaptic current."""
        p = self.params
        dt = p.dt

        # Update conductance dynamics
        self.g_rise -= self.g_rise / p.tau_rise * dt
        self.g_decay -= self.g_decay / p.tau_decay * dt

        # Net conductance (double exponential)
        self.state.g = self.g_decay - self.g_rise

        # Update STP variables
        if p.use_stp:
            self.x += (1 - self.x) / p.tau_rec * dt
            self.u += (p.U - self.u) / p.tau_fac * dt

        # Compute current
        V_post = self.post.V
        I = self.state.g * (V_post - p.E_rev)

        # Sign convention: positive current = depolarizing for excitatory
        if p.synapse_type == SynapseType.INHIBITORY:
            I = -I

        return I

    def reset(self):
        """Reset synapse state."""
        super().reset()
        self.g_rise = 0.0
        self.g_decay = 0.0
        self.x = 1.0
        self.u = self.params.U

    @classmethod
    def create_ampa(
        cls,
        pre: "Neuron",
        post: "Neuron",
        weight: float = 1.0,
        **kwargs
    ) -> "ChemicalSynapse":
        """Create AMPA-type excitatory synapse."""
        params = ChemicalSynapseParameters.from_receptor(
            ReceptorType.AMPA,
            weight=weight,
            **kwargs
        )
        return cls(pre, post, params)

    @classmethod
    def create_gaba(
        cls,
        pre: "Neuron",
        post: "Neuron",
        weight: float = 1.0,
        **kwargs
    ) -> "ChemicalSynapse":
        """Create GABA-A type inhibitory synapse."""
        params = ChemicalSynapseParameters.from_receptor(
            ReceptorType.GABA_A,
            weight=weight,
            **kwargs
        )
        return cls(pre, post, params)

    @classmethod
    def create_nmda(
        cls,
        pre: "Neuron",
        post: "Neuron",
        weight: float = 1.0,
        **kwargs
    ) -> "ChemicalSynapse":
        """Create NMDA-type excitatory synapse."""
        params = ChemicalSynapseParameters.from_receptor(
            ReceptorType.NMDA,
            weight=weight,
            **kwargs
        )
        return cls(pre, post, params)
