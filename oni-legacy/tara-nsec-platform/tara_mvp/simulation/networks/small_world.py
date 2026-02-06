"""
Small-World Network Model

Implements networks with small-world topology, characterized by:
- High local clustering (like regular lattices)
- Short average path length (like random networks)

This topology is observed in many biological neural networks and
provides efficient information processing.

Reference:
    Watts, D.J. & Strogatz, S.H. (1998). Collective dynamics of
    'small-world' networks. Nature, 393(6684), 440-442.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
import numpy as np

from .base import Network, NetworkParameters
from ..neurons.base import Neuron, NeuronType
from ..neurons.lif import LIFNeuron
from ..synapses.chemical import ChemicalSynapse, ChemicalSynapseParameters, ReceptorType
from ..synapses.electrical import ElectricalSynapse, ElectricalSynapseParameters


@dataclass
class SmallWorldParameters(NetworkParameters):
    """Parameters for small-world network."""

    # Network size
    n_neurons: int = 500              # Total neurons
    excitatory_ratio: float = 0.8     # Fraction excitatory

    # Small-world topology
    k: int = 4                        # Initial neighbors (each side) in ring
    p_rewire: float = 0.1             # Rewiring probability

    # Synaptic parameters
    exc_weight: float = 0.5           # Excitatory synapse weight
    inh_weight: float = -1.0          # Inhibitory synapse weight

    # Use electrical synapses (gap junctions) for local connections
    use_gap_junctions: bool = False
    gap_junction_conductance: float = 0.1

    # Distance-dependent delays
    use_delays: bool = True
    min_delay: float = 1.0            # Minimum delay (ms)
    max_delay: float = 10.0           # Maximum delay (ms)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "n_neurons": self.n_neurons,
            "k": self.k,
            "p_rewire": self.p_rewire,
            "excitatory_ratio": self.excitatory_ratio,
            "use_gap_junctions": self.use_gap_junctions,
        })
        return base


class SmallWorldNetwork(Network):
    """
    Small-World Neural Network.

    Creates a network with small-world topology using the
    Watts-Strogatz algorithm:
    1. Start with a ring lattice where each node connects to k neighbors
    2. Rewire each edge with probability p

    This produces networks with:
    - High clustering coefficient (local connectivity)
    - Short characteristic path length (global efficiency)

    These properties are observed in cortical networks and are
    thought to support efficient information integration.

    Usage:
        >>> net = SmallWorldNetwork(SmallWorldParameters(
        ...     n_neurons=500, k=4, p_rewire=0.1
        ... ))
        >>> metrics = net.compute_topology_metrics()
        >>> print(f"Clustering: {metrics['clustering']:.3f}")
    """

    def __init__(self, params: Optional[SmallWorldParameters] = None):
        """
        Initialize small-world network.

        Args:
            params: Network parameters
        """
        self._adjacency: Dict[str, List[str]] = {}
        self._neuron_indices: Dict[str, int] = {}
        super().__init__(params or SmallWorldParameters())

    @property
    def params(self) -> SmallWorldParameters:
        """Type-hinted access to parameters."""
        return self._params

    @params.setter
    def params(self, value: SmallWorldParameters):
        self._params = value

    def _create_neurons(self):
        """Create neurons arranged in a ring."""
        p = self.params
        n_exc = int(p.n_neurons * p.excitatory_ratio)

        for i in range(p.n_neurons):
            # Determine neuron type
            if i < n_exc:
                neuron = LIFNeuron.create_excitatory()
            else:
                neuron = LIFNeuron.create_inhibitory()

            # Position on a ring (for visualization)
            angle = 2 * np.pi * i / p.n_neurons
            radius = 100
            neuron.params.position = (
                radius * np.cos(angle),
                radius * np.sin(angle),
                0
            )

            group = "excitatory" if i < n_exc else "inhibitory"
            self.add_neuron(neuron, group=group)

            # Store index mapping
            self._neuron_indices[neuron.id] = i
            self._adjacency[neuron.id] = []

    def _create_synapses(self):
        """Create small-world connectivity using Watts-Strogatz algorithm."""
        p = self.params
        neuron_list = list(self._neurons.values())
        n = len(neuron_list)

        # Step 1: Create ring lattice with k neighbors on each side
        for i, neuron in enumerate(neuron_list):
            for j in range(1, p.k + 1):
                # Connect to neighbors on the right (mod n for wrapping)
                target_idx = (i + j) % n
                self._add_connection(neuron, neuron_list[target_idx])

        # Step 2: Rewire edges with probability p
        # For each edge, consider rewiring the target
        edges_to_rewire = []
        for i, neuron in enumerate(neuron_list):
            for j in range(1, p.k + 1):
                if np.random.random() < p.p_rewire:
                    old_target_idx = (i + j) % n
                    edges_to_rewire.append((i, old_target_idx))

        # Perform rewiring
        for source_idx, old_target_idx in edges_to_rewire:
            source = neuron_list[source_idx]
            old_target = neuron_list[old_target_idx]

            # Remove old connection
            self._remove_connection(source, old_target)

            # Find new target (not self, not already connected)
            available = [
                k for k in range(n)
                if k != source_idx
                and neuron_list[k].id not in self._adjacency[source.id]
            ]

            if available:
                new_target_idx = np.random.choice(available)
                new_target = neuron_list[new_target_idx]
                self._add_connection(source, new_target)

    def _add_connection(self, pre: Neuron, post: Neuron):
        """Add a connection between two neurons."""
        p = self.params

        # Track adjacency
        self._adjacency[pre.id].append(post.id)

        # Compute delay based on distance if enabled
        if p.use_delays:
            dist = self._compute_ring_distance(pre, post)
            max_dist = np.pi * 100  # Half circumference
            delay = p.min_delay + (p.max_delay - p.min_delay) * (dist / max_dist)
        else:
            delay = p.min_delay

        # Create synapse based on neuron type
        if p.use_gap_junctions and pre.params.neuron_type == post.params.neuron_type:
            # Gap junction for same-type local connections
            params = ElectricalSynapseParameters(
                g_gap=p.gap_junction_conductance,
                dt=self.params.dt
            )
            synapse = ElectricalSynapse(pre, post, params)
        else:
            # Chemical synapse
            if pre.params.neuron_type == NeuronType.INHIBITORY:
                syn_params = ChemicalSynapseParameters.from_receptor(
                    ReceptorType.GABA_A,
                    weight=abs(p.inh_weight),
                    delay=delay,
                    dt=self.params.dt
                )
            else:
                syn_params = ChemicalSynapseParameters.from_receptor(
                    ReceptorType.AMPA,
                    weight=p.exc_weight,
                    delay=delay,
                    dt=self.params.dt
                )
            synapse = ChemicalSynapse(pre, post, syn_params)

        self.add_synapse(synapse)

    def _remove_connection(self, pre: Neuron, post: Neuron):
        """Remove connection between neurons."""
        if post.id in self._adjacency[pre.id]:
            self._adjacency[pre.id].remove(post.id)

        # Remove synapse
        synapses_to_remove = self.get_synapses_between(pre.id, post.id)
        for syn in synapses_to_remove:
            self._synapses.remove(syn)
            key = (pre.id, post.id)
            if key in self._synapse_map:
                self._synapse_map[key].remove(syn)

    def _compute_ring_distance(self, n1: Neuron, n2: Neuron) -> float:
        """Compute distance along the ring."""
        if n1.params.position and n2.params.position:
            p1 = np.array(n1.params.position[:2])
            p2 = np.array(n2.params.position[:2])
            return np.linalg.norm(p1 - p2)
        return 0.0

    def compute_clustering_coefficient(self) -> float:
        """
        Compute global clustering coefficient.

        The clustering coefficient measures the degree to which
        neighbors of a node are connected to each other.

        Returns:
            Average clustering coefficient
        """
        coefficients = []

        for neuron_id in self._neurons:
            neighbors = self._adjacency.get(neuron_id, [])
            k = len(neighbors)

            if k < 2:
                continue

            # Count edges between neighbors
            edges = 0
            for i, n1 in enumerate(neighbors):
                for n2 in neighbors[i+1:]:
                    if n2 in self._adjacency.get(n1, []):
                        edges += 1
                    if n1 in self._adjacency.get(n2, []):
                        edges += 1

            # Maximum possible edges between k neighbors
            max_edges = k * (k - 1)

            if max_edges > 0:
                coefficients.append(edges / max_edges)

        return np.mean(coefficients) if coefficients else 0.0

    def compute_path_length(self, sample_size: int = 100) -> float:
        """
        Estimate average shortest path length.

        Uses BFS from a sample of nodes for efficiency.

        Args:
            sample_size: Number of source nodes to sample

        Returns:
            Average shortest path length
        """
        neuron_ids = list(self._neurons.keys())
        n = len(neuron_ids)

        if n <= 1:
            return 0.0

        sample_ids = np.random.choice(
            neuron_ids,
            size=min(sample_size, n),
            replace=False
        )

        path_lengths = []

        for source_id in sample_ids:
            # BFS for shortest paths
            distances = {source_id: 0}
            queue = [source_id]

            while queue:
                current = queue.pop(0)
                current_dist = distances[current]

                for neighbor in self._adjacency.get(current, []):
                    if neighbor not in distances:
                        distances[neighbor] = current_dist + 1
                        queue.append(neighbor)

            # Collect distances to all reachable nodes
            for target_id, dist in distances.items():
                if target_id != source_id and dist > 0:
                    path_lengths.append(dist)

        return np.mean(path_lengths) if path_lengths else float('inf')

    def compute_topology_metrics(self) -> Dict[str, float]:
        """
        Compute small-world topology metrics.

        Returns:
            Dictionary with clustering, path length, and small-world coefficient
        """
        C = self.compute_clustering_coefficient()
        L = self.compute_path_length()

        # Compare to random network expectations
        n = self.n_neurons
        k = 2 * self.params.k  # Total degree

        # Random network values (Erdos-Renyi)
        p_random = k / (n - 1)
        C_random = p_random
        L_random = np.log(n) / np.log(k) if k > 1 else float('inf')

        # Small-world coefficient (sigma)
        # sigma > 1 indicates small-world topology
        if C_random > 0 and L_random > 0 and L > 0:
            gamma = C / C_random
            lambda_ = L / L_random
            sigma = gamma / lambda_
        else:
            gamma = lambda_ = sigma = float('nan')

        return {
            "clustering": C,
            "path_length": L,
            "C_random": C_random,
            "L_random": L_random,
            "gamma": gamma,
            "lambda": lambda_,
            "sigma": sigma,  # Small-world coefficient
        }

    def get_degree_distribution(self) -> Dict[str, Any]:
        """Get degree distribution statistics."""
        degrees = [len(self._adjacency.get(nid, [])) for nid in self._neurons]

        return {
            "degrees": np.array(degrees),
            "mean": np.mean(degrees),
            "std": np.std(degrees),
            "min": np.min(degrees),
            "max": np.max(degrees),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize network."""
        data = super().to_dict()
        data["topology"] = self.compute_topology_metrics()
        data["degree_stats"] = {
            k: v for k, v in self.get_degree_distribution().items()
            if k != "degrees"
        }
        return data

    @classmethod
    def create_watts_strogatz(
        cls,
        n: int = 500,
        k: int = 4,
        p: float = 0.1,
        **kwargs
    ) -> "SmallWorldNetwork":
        """
        Create classic Watts-Strogatz small-world network.

        Args:
            n: Number of neurons
            k: Number of neighbors on each side in initial ring
            p: Rewiring probability

        Returns:
            SmallWorldNetwork with Watts-Strogatz topology
        """
        params = SmallWorldParameters(
            n_neurons=n,
            k=k,
            p_rewire=p,
            **kwargs
        )
        return cls(params)

    @classmethod
    def create_cortical_module(
        cls,
        n_neurons: int = 200,
        **kwargs
    ) -> "SmallWorldNetwork":
        """
        Create network mimicking cortical microcolumn.

        Cortical circuits exhibit small-world properties with
        high local clustering and some long-range connections.

        Args:
            n_neurons: Number of neurons
            **kwargs: Additional parameters

        Returns:
            SmallWorldNetwork with cortical-like topology
        """
        params = SmallWorldParameters(
            n_neurons=n_neurons,
            k=6,                      # ~6 local neighbors
            p_rewire=0.05,            # 5% long-range connections
            excitatory_ratio=0.8,     # 80% excitatory (cortical ratio)
            use_gap_junctions=True,   # Gap junctions in interneurons
            gap_junction_conductance=0.2,
            use_delays=True,
            min_delay=0.5,
            max_delay=5.0,
            **kwargs
        )
        return cls(params)
