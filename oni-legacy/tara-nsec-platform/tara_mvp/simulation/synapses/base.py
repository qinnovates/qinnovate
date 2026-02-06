"""
Base Synapse Model

Abstract base class for all synapse types in NeuroSim.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, TYPE_CHECKING
from enum import Enum
import uuid

if TYPE_CHECKING:
    from ..neurons.base import Neuron


class SynapseType(Enum):
    """Types of synapses."""
    EXCITATORY = "excitatory"     # Depolarizing (e.g., glutamatergic)
    INHIBITORY = "inhibitory"     # Hyperpolarizing (e.g., GABAergic)
    MODULATORY = "modulatory"     # Neuromodulatory (e.g., dopaminergic)
    ELECTRICAL = "electrical"     # Gap junction


@dataclass
class SynapseParameters:
    """Base parameters for all synapse models."""

    # Identification
    synapse_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    synapse_type: SynapseType = SynapseType.EXCITATORY

    # Connection strength
    weight: float = 1.0           # Synaptic weight
    delay: float = 1.0            # Transmission delay (ms)

    # Simulation
    dt: float = 0.1               # Time step (ms)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "synapse_id": self.synapse_id,
            "synapse_type": self.synapse_type.value,
            "weight": self.weight,
            "delay": self.delay,
            "dt": self.dt,
        }


@dataclass
class SynapseState:
    """Current state of a synapse."""

    # Conductance/current state
    g: float = 0.0            # Synaptic conductance (nS)
    I: float = 0.0            # Synaptic current (nA)

    # Spike queue for delays
    pending_spikes: list = field(default_factory=list)

    # Statistics
    spike_count: int = 0       # Number of transmitted spikes
    last_spike_time: float = -1000.0  # Time of last presynaptic spike

    def reset(self):
        """Reset synapse state."""
        self.g = 0.0
        self.I = 0.0
        self.pending_spikes = []
        self.spike_count = 0
        self.last_spike_time = -1000.0


class Synapse(ABC):
    """
    Abstract base class for synapses.

    Synapses connect a presynaptic neuron to a postsynaptic neuron,
    transmitting signals with optional delay and plasticity.
    """

    def __init__(
        self,
        pre: "Neuron",
        post: "Neuron",
        params: Optional[SynapseParameters] = None
    ):
        """
        Initialize synapse.

        Args:
            pre: Presynaptic neuron
            post: Postsynaptic neuron
            params: Synapse parameters
        """
        self.pre = pre
        self.post = post
        self.params = params or SynapseParameters()
        self.state = SynapseState()

        # Register for presynaptic spikes
        pre.on_spike(self._on_pre_spike)

    @property
    def id(self) -> str:
        """Unique identifier."""
        return self.params.synapse_id

    @property
    def weight(self) -> float:
        """Current synaptic weight."""
        return self.params.weight

    @weight.setter
    def weight(self, value: float):
        """Set synaptic weight."""
        self.params.weight = value

    def _on_pre_spike(self, neuron: "Neuron", spike_time: float):
        """Handle presynaptic spike event."""
        # Queue spike for delivery after delay
        delivery_time = spike_time + self.params.delay
        self.state.pending_spikes.append(delivery_time)
        self.state.spike_count += 1
        self.state.last_spike_time = spike_time

    @abstractmethod
    def _compute_current(self, t: float) -> float:
        """
        Compute synaptic current at time t.

        Args:
            t: Current simulation time (ms)

        Returns:
            Synaptic current (nA)
        """
        pass

    def step(self, t: float) -> float:
        """
        Advance synapse by one timestep.

        Args:
            t: Current simulation time (ms)

        Returns:
            Synaptic current delivered to postsynaptic neuron
        """
        # Check for spike deliveries
        self._deliver_spikes(t)

        # Compute current
        I = self._compute_current(t)
        self.state.I = I

        # Deliver to postsynaptic neuron
        if abs(I) > 1e-12:
            self.post.receive_input(I, input_type="synaptic")

        return I

    def _deliver_spikes(self, t: float):
        """Process pending spike deliveries."""
        delivered = []
        for spike_time in self.state.pending_spikes:
            if spike_time <= t:
                self._on_spike_arrival(spike_time)
                delivered.append(spike_time)

        for spike_time in delivered:
            self.state.pending_spikes.remove(spike_time)

    @abstractmethod
    def _on_spike_arrival(self, spike_time: float):
        """Handle arrival of a presynaptic spike."""
        pass

    def reset(self):
        """Reset synapse state."""
        self.state.reset()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize synapse."""
        return {
            "model": self.__class__.__name__,
            "pre_id": self.pre.id,
            "post_id": self.post.id,
            "params": self.params.to_dict(),
            "state": {
                "g": self.state.g,
                "spike_count": self.state.spike_count,
            },
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.pre.id} -> {self.post.id}, w={self.weight:.3f})"
