"""
Base Network Model

Abstract base class for neural network architectures.
Manages collections of neurons and synapses.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Optional, Dict, Any, List, Tuple, Callable,
    Union, TYPE_CHECKING, Iterator
)
from enum import Enum
import uuid
import numpy as np

if TYPE_CHECKING:
    from ..neurons.base import Neuron
    from ..synapses.base import Synapse


class ConnectionPattern(Enum):
    """Common connection patterns."""
    ALL_TO_ALL = "all_to_all"         # Every neuron connects to every other
    ONE_TO_ONE = "one_to_one"         # i connects to i only
    RANDOM = "random"                  # Random sparse connections
    DISTANCE_DEPENDENT = "distance"    # Connection probability decays with distance
    SMALL_WORLD = "small_world"       # High clustering, short path length


@dataclass
class NetworkParameters:
    """Base parameters for networks."""

    # Identification
    network_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = "Network"

    # Simulation
    dt: float = 0.1  # Time step (ms)

    # Random seed for reproducibility
    seed: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "network_id": self.network_id,
            "name": self.name,
            "dt": self.dt,
            "seed": self.seed,
        }


@dataclass
class NetworkState:
    """Current state of a network."""

    # Timing
    t: float = 0.0               # Current simulation time
    step_count: int = 0          # Number of steps taken

    # Activity tracking
    spike_times: List[Tuple[str, float]] = field(default_factory=list)
    spike_counts: Dict[str, int] = field(default_factory=dict)

    # Population activity
    firing_rates: Dict[str, float] = field(default_factory=dict)

    def reset(self):
        """Reset network state."""
        self.t = 0.0
        self.step_count = 0
        self.spike_times = []
        self.spike_counts = {}
        self.firing_rates = {}


class Network(ABC):
    """
    Abstract base class for neural networks.

    A network manages collections of neurons and synapses,
    providing methods for simulation and analysis.

    Usage:
        >>> # Subclass to create specific network types
        >>> class MyNetwork(Network):
        ...     def _create_neurons(self): ...
        ...     def _create_synapses(self): ...
    """

    def __init__(self, params: Optional[NetworkParameters] = None):
        """
        Initialize network.

        Args:
            params: Network parameters
        """
        self.params = params or NetworkParameters()
        self.state = NetworkState()

        # Neuron storage
        self._neurons: Dict[str, "Neuron"] = {}
        self._neuron_groups: Dict[str, List[str]] = {}

        # Synapse storage
        self._synapses: List["Synapse"] = []
        self._synapse_map: Dict[Tuple[str, str], List["Synapse"]] = {}

        # Random state
        if self.params.seed is not None:
            np.random.seed(self.params.seed)

        # Callbacks
        self._spike_callbacks: List[Callable] = []

        # Build network
        self._create_neurons()
        self._create_synapses()

    @property
    def id(self) -> str:
        """Unique identifier."""
        return self.params.network_id

    @property
    def neurons(self) -> Dict[str, "Neuron"]:
        """All neurons in the network."""
        return self._neurons

    @property
    def synapses(self) -> List["Synapse"]:
        """All synapses in the network."""
        return self._synapses

    @property
    def n_neurons(self) -> int:
        """Number of neurons."""
        return len(self._neurons)

    @property
    def n_synapses(self) -> int:
        """Number of synapses."""
        return len(self._synapses)

    @abstractmethod
    def _create_neurons(self):
        """Create neurons for this network. Must be implemented by subclass."""
        pass

    @abstractmethod
    def _create_synapses(self):
        """Create synapses for this network. Must be implemented by subclass."""
        pass

    def add_neuron(self, neuron: "Neuron", group: Optional[str] = None):
        """
        Add a neuron to the network.

        Args:
            neuron: Neuron to add
            group: Optional group name for organization
        """
        self._neurons[neuron.id] = neuron

        # Register spike callback
        neuron.on_spike(self._on_neuron_spike)

        # Add to group
        if group:
            if group not in self._neuron_groups:
                self._neuron_groups[group] = []
            self._neuron_groups[group].append(neuron.id)

    def add_neurons(self, neurons: List["Neuron"], group: Optional[str] = None):
        """Add multiple neurons."""
        for neuron in neurons:
            self.add_neuron(neuron, group)

    def get_neuron(self, neuron_id: str) -> Optional["Neuron"]:
        """Get neuron by ID."""
        return self._neurons.get(neuron_id)

    def get_group(self, group_name: str) -> List["Neuron"]:
        """Get all neurons in a group."""
        ids = self._neuron_groups.get(group_name, [])
        return [self._neurons[nid] for nid in ids if nid in self._neurons]

    def add_synapse(self, synapse: "Synapse"):
        """
        Add a synapse to the network.

        Args:
            synapse: Synapse to add
        """
        self._synapses.append(synapse)

        # Index by pre/post pair
        key = (synapse.pre.id, synapse.post.id)
        if key not in self._synapse_map:
            self._synapse_map[key] = []
        self._synapse_map[key].append(synapse)

    def add_synapses(self, synapses: List["Synapse"]):
        """Add multiple synapses."""
        for synapse in synapses:
            self.add_synapse(synapse)

    def get_synapses_between(
        self,
        pre_id: str,
        post_id: str
    ) -> List["Synapse"]:
        """Get all synapses between two neurons."""
        return self._synapse_map.get((pre_id, post_id), [])

    def get_incoming_synapses(self, neuron_id: str) -> List["Synapse"]:
        """Get all synapses projecting to a neuron."""
        return [s for s in self._synapses if s.post.id == neuron_id]

    def get_outgoing_synapses(self, neuron_id: str) -> List["Synapse"]:
        """Get all synapses originating from a neuron."""
        return [s for s in self._synapses if s.pre.id == neuron_id]

    def connect(
        self,
        source: Union[str, List[str], "Neuron", List["Neuron"]],
        target: Union[str, List[str], "Neuron", List["Neuron"]],
        synapse_class,
        pattern: ConnectionPattern = ConnectionPattern.ALL_TO_ALL,
        p_connect: float = 1.0,
        weight: Optional[float] = None,
        **synapse_kwargs
    ) -> List["Synapse"]:
        """
        Connect neurons using specified pattern.

        Args:
            source: Source neuron(s) or ID(s)
            target: Target neuron(s) or ID(s)
            synapse_class: Class to use for synapses
            pattern: Connection pattern
            p_connect: Connection probability (for random patterns)
            weight: Synaptic weight (optional)
            **synapse_kwargs: Additional synapse parameters

        Returns:
            List of created synapses
        """
        # Normalize inputs to lists of neurons
        source_neurons = self._normalize_neurons(source)
        target_neurons = self._normalize_neurons(target)

        created_synapses = []

        if pattern == ConnectionPattern.ALL_TO_ALL:
            for pre in source_neurons:
                for post in target_neurons:
                    if pre.id != post.id:  # No self-connections
                        syn = self._create_synapse(
                            pre, post, synapse_class, weight, **synapse_kwargs
                        )
                        created_synapses.append(syn)

        elif pattern == ConnectionPattern.ONE_TO_ONE:
            for pre, post in zip(source_neurons, target_neurons):
                syn = self._create_synapse(
                    pre, post, synapse_class, weight, **synapse_kwargs
                )
                created_synapses.append(syn)

        elif pattern == ConnectionPattern.RANDOM:
            for pre in source_neurons:
                for post in target_neurons:
                    if pre.id != post.id and np.random.random() < p_connect:
                        syn = self._create_synapse(
                            pre, post, synapse_class, weight, **synapse_kwargs
                        )
                        created_synapses.append(syn)

        elif pattern == ConnectionPattern.DISTANCE_DEPENDENT:
            # Use position if available
            for pre in source_neurons:
                for post in target_neurons:
                    if pre.id == post.id:
                        continue
                    dist = self._compute_distance(pre, post)
                    p = p_connect * np.exp(-dist / 100)  # 100 unit length scale
                    if np.random.random() < p:
                        syn = self._create_synapse(
                            pre, post, synapse_class, weight, **synapse_kwargs
                        )
                        created_synapses.append(syn)

        self.add_synapses(created_synapses)
        return created_synapses

    def _normalize_neurons(
        self,
        neurons: Union[str, List[str], "Neuron", List["Neuron"]]
    ) -> List["Neuron"]:
        """Convert various neuron specifications to list of neurons."""
        if isinstance(neurons, str):
            return [self._neurons[neurons]]
        elif hasattr(neurons, 'id'):  # Single neuron
            return [neurons]
        elif isinstance(neurons, list):
            if len(neurons) == 0:
                return []
            if isinstance(neurons[0], str):
                return [self._neurons[nid] for nid in neurons]
            else:
                return neurons
        return []

    def _create_synapse(
        self,
        pre: "Neuron",
        post: "Neuron",
        synapse_class,
        weight: Optional[float],
        **kwargs
    ) -> "Synapse":
        """Create a single synapse."""
        if weight is not None:
            kwargs["weight"] = weight
        if hasattr(synapse_class, "from_receptor"):
            # ChemicalSynapse or similar
            return synapse_class(pre, post, synapse_class.Parameters(**kwargs))
        else:
            return synapse_class(pre, post)

    def _compute_distance(self, pre: "Neuron", post: "Neuron") -> float:
        """Compute Euclidean distance between neurons."""
        if pre.params.position and post.params.position:
            p1 = np.array(pre.params.position)
            p2 = np.array(post.params.position)
            return np.linalg.norm(p1 - p2)
        return 0.0

    def _on_neuron_spike(self, neuron: "Neuron", spike_time: float):
        """Handle spike from any neuron."""
        self.state.spike_times.append((neuron.id, spike_time))

        if neuron.id not in self.state.spike_counts:
            self.state.spike_counts[neuron.id] = 0
        self.state.spike_counts[neuron.id] += 1

        # Notify callbacks
        for callback in self._spike_callbacks:
            callback(neuron, spike_time)

    def on_spike(self, callback: Callable[["Neuron", float], None]):
        """Register callback for network spikes."""
        self._spike_callbacks.append(callback)

    def step(self, record_history: bool = True) -> Dict[str, bool]:
        """
        Advance network by one timestep.

        Args:
            record_history: Whether to record voltage history

        Returns:
            Dictionary mapping neuron IDs to spike status
        """
        spikes = {}

        # Update all neurons
        for neuron_id, neuron in self._neurons.items():
            spiked = neuron.step(record_history)
            spikes[neuron_id] = spiked

        # Update all synapses
        for synapse in self._synapses:
            synapse.step(self.state.t)

        # Update time
        self.state.t += self.params.dt
        self.state.step_count += 1

        return spikes

    def simulate(
        self,
        duration: float,
        inputs: Optional[Dict[str, np.ndarray]] = None,
        record_history: bool = True
    ) -> Dict[str, Any]:
        """
        Run network simulation.

        Args:
            duration: Simulation duration (ms)
            inputs: Dictionary mapping neuron IDs to input current arrays
            record_history: Whether to record voltage history

        Returns:
            Dictionary with simulation results
        """
        n_steps = int(duration / self.params.dt)

        # Prepare inputs
        input_dict = inputs or {}

        # Run simulation
        for step in range(n_steps):
            # Apply inputs
            for neuron_id, current in input_dict.items():
                if neuron_id in self._neurons:
                    idx = min(step, len(current) - 1)
                    self._neurons[neuron_id].receive_input(current[idx])

            # Step network
            self.step(record_history)

        # Collect results
        results = {
            "t": np.arange(0, duration, self.params.dt),
            "duration": duration,
            "n_steps": n_steps,
            "spike_times": self.state.spike_times,
            "spike_counts": self.state.spike_counts,
            "neurons": {},
        }

        # Collect neuron data
        if record_history:
            for neuron_id, neuron in self._neurons.items():
                results["neurons"][neuron_id] = {
                    "V": np.array(neuron.state.V_history),
                    "spike_times": neuron.state.spike_times,
                }

        return results

    def reset(self):
        """Reset network to initial state."""
        self.state.reset()

        for neuron in self._neurons.values():
            neuron.reset()

        for synapse in self._synapses:
            synapse.reset()

    def get_connectivity_matrix(self) -> np.ndarray:
        """Get weight matrix of connections."""
        n = self.n_neurons
        ids = list(self._neurons.keys())
        id_to_idx = {nid: i for i, nid in enumerate(ids)}

        W = np.zeros((n, n))
        for synapse in self._synapses:
            i = id_to_idx.get(synapse.pre.id)
            j = id_to_idx.get(synapse.post.id)
            if i is not None and j is not None:
                W[i, j] += synapse.weight

        return W

    def get_spike_raster(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get spike times and neuron indices for raster plot."""
        ids = list(self._neurons.keys())
        id_to_idx = {nid: i for i, nid in enumerate(ids)}

        times = []
        indices = []
        for neuron_id, spike_time in self.state.spike_times:
            times.append(spike_time)
            indices.append(id_to_idx.get(neuron_id, -1))

        return np.array(times), np.array(indices)

    def compute_firing_rates(self, window: float = 100.0) -> Dict[str, float]:
        """
        Compute firing rates for all neurons.

        Args:
            window: Time window for rate computation (ms)

        Returns:
            Dictionary mapping neuron IDs to firing rates (Hz)
        """
        rates = {}
        t_current = self.state.t

        for neuron_id, neuron in self._neurons.items():
            # Count spikes in window
            spikes_in_window = sum(
                1 for st in neuron.state.spike_times
                if t_current - window <= st <= t_current
            )
            rates[neuron_id] = spikes_in_window / (window / 1000)  # Convert to Hz

        self.state.firing_rates = rates
        return rates

    def to_dict(self) -> Dict[str, Any]:
        """Serialize network."""
        return {
            "model": self.__class__.__name__,
            "params": self.params.to_dict(),
            "n_neurons": self.n_neurons,
            "n_synapses": self.n_synapses,
            "groups": {k: len(v) for k, v in self._neuron_groups.items()},
            "state": {
                "t": self.state.t,
                "step_count": self.state.step_count,
                "total_spikes": len(self.state.spike_times),
            },
        }

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"neurons={self.n_neurons}, "
                f"synapses={self.n_synapses})")

    def __iter__(self) -> Iterator["Neuron"]:
        """Iterate over neurons."""
        return iter(self._neurons.values())
