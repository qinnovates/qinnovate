"""
Electrical Synapse (Gap Junction) Model

Models bidirectional electrical coupling between neurons.
Current flows based on voltage difference.

I = g_gap * (V_pre - V_post)
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, TYPE_CHECKING

from .base import Synapse, SynapseParameters, SynapseType

if TYPE_CHECKING:
    from ..neurons.base import Neuron


@dataclass
class ElectricalSynapseParameters(SynapseParameters):
    """Parameters for electrical synapse (gap junction)."""

    # Conductance
    g_gap: float = 0.5         # Gap junction conductance (nS)

    # Rectification (optional)
    rectifying: bool = False   # If True, current only flows in one direction

    def __post_init__(self):
        self.synapse_type = SynapseType.ELECTRICAL

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "g_gap": self.g_gap,
            "rectifying": self.rectifying,
        })
        return base


class ElectricalSynapse(Synapse):
    """
    Electrical Synapse (Gap Junction).

    Provides direct electrical coupling between neurons.
    Current is proportional to voltage difference.

    Usage:
        >>> synapse = ElectricalSynapse(neuron1, neuron2)
        >>> # Creates bidirectional coupling
    """

    def __init__(
        self,
        pre: "Neuron",
        post: "Neuron",
        params: Optional[ElectricalSynapseParameters] = None
    ):
        # Don't call parent __init__ to avoid spike callback
        self.pre = pre
        self.post = post
        self.params = params or ElectricalSynapseParameters()

        from .base import SynapseState
        self.state = SynapseState()

    @property
    def params(self) -> ElectricalSynapseParameters:
        return self._params

    @params.setter
    def params(self, value: ElectricalSynapseParameters):
        self._params = value

    def _on_spike_arrival(self, spike_time: float):
        """Not used for electrical synapses."""
        pass

    def _compute_current(self, t: float) -> float:
        """Compute gap junction current."""
        p = self.params

        # Voltage difference
        V_diff = self.pre.V - self.post.V

        # Compute current
        I = p.g_gap * p.weight * V_diff

        # Apply rectification if enabled
        if p.rectifying and I < 0:
            I = 0

        self.state.g = p.g_gap * p.weight
        return I

    def step(self, t: float) -> float:
        """Step without spike delivery (continuous coupling)."""
        I = self._compute_current(t)
        self.state.I = I

        if abs(I) > 1e-12:
            self.post.receive_input(I, input_type="synaptic")

        return I
