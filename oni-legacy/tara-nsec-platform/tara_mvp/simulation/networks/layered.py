"""
Layered Network Model

Implements feedforward layered network architecture.
Can be configured to match the ONI Framework's 14-layer model.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple, Type
import numpy as np

from .base import Network, NetworkParameters, ConnectionPattern
from ..neurons.base import Neuron, NeuronType
from ..neurons.lif import LIFNeuron, LIFParameters
from ..synapses.chemical import ChemicalSynapse, ChemicalSynapseParameters, ReceptorType


# ONI Framework 14-layer model mapping
ONI_LAYERS = {
    1: {"name": "Physical Interface", "abbrev": "PHY", "type": "sensory"},
    2: {"name": "Signal Transduction", "abbrev": "SIG", "type": "processing"},
    3: {"name": "Pattern Recognition", "abbrev": "PAT", "type": "processing"},
    4: {"name": "Feature Integration", "abbrev": "FEA", "type": "processing"},
    5: {"name": "Temporal Processing", "abbrev": "TMP", "type": "processing"},
    6: {"name": "Memory Encoding", "abbrev": "MEM", "type": "memory"},
    7: {"name": "Contextual Association", "abbrev": "CTX", "type": "processing"},
    8: {"name": "Decision Making", "abbrev": "DEC", "type": "executive"},
    9: {"name": "Motor Planning", "abbrev": "MTR", "type": "motor"},
    10: {"name": "Action Selection", "abbrev": "ACT", "type": "motor"},
    11: {"name": "Feedback Integration", "abbrev": "FBK", "type": "processing"},
    12: {"name": "Error Correction", "abbrev": "ERR", "type": "processing"},
    13: {"name": "Learning/Adaptation", "abbrev": "LRN", "type": "plasticity"},
    14: {"name": "Meta-Cognition", "abbrev": "META", "type": "executive"},
}


@dataclass
class LayerConfig:
    """Configuration for a single layer."""

    n_neurons: int = 100            # Number of neurons
    neuron_type: NeuronType = NeuronType.EXCITATORY
    excitatory_ratio: float = 0.8   # Fraction excitatory (rest inhibitory)
    neuron_class: Type[Neuron] = None  # Will default to LIFNeuron
    neuron_params: Dict[str, Any] = field(default_factory=dict)
    oni_layer: Optional[int] = None  # ONI layer mapping


@dataclass
class LayeredNetworkParameters(NetworkParameters):
    """Parameters for layered network."""

    # Layer configuration
    n_layers: int = 3
    neurons_per_layer: int = 100
    layer_configs: List[LayerConfig] = None

    # Inter-layer connectivity
    feedforward_prob: float = 0.3     # P(connection) between adjacent layers
    feedforward_weight: float = 0.5
    skip_connections: bool = False     # Allow non-adjacent connections
    skip_prob: float = 0.05

    # Intra-layer connectivity
    lateral_connections: bool = True
    lateral_prob: float = 0.1
    lateral_weight: float = 0.3
    lateral_inhibitory_weight: float = -0.5

    # Use ONI layer mapping
    use_oni_layers: bool = False

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "n_layers": self.n_layers,
            "neurons_per_layer": self.neurons_per_layer,
            "feedforward_prob": self.feedforward_prob,
            "feedforward_weight": self.feedforward_weight,
            "lateral_connections": self.lateral_connections,
            "use_oni_layers": self.use_oni_layers,
        })
        return base


class LayeredNetwork(Network):
    """
    Layered Feedforward Neural Network.

    Implements a network with distinct layers, feedforward connections
    between layers, and optional lateral connections within layers.

    Can be configured to match the ONI Framework's 14-layer neural
    security model.

    Usage:
        >>> # Simple 3-layer network
        >>> net = LayeredNetwork(LayeredNetworkParameters(
        ...     n_layers=3, neurons_per_layer=100
        ... ))

        >>> # ONI 14-layer model
        >>> net = LayeredNetwork.create_oni_model()
    """

    def __init__(self, params: Optional[LayeredNetworkParameters] = None):
        """
        Initialize layered network.

        Args:
            params: Network parameters
        """
        self._layer_neurons: Dict[int, List[str]] = {}
        self._layer_configs: Dict[int, LayerConfig] = {}
        super().__init__(params or LayeredNetworkParameters())

    @property
    def params(self) -> LayeredNetworkParameters:
        """Type-hinted access to parameters."""
        return self._params

    @params.setter
    def params(self, value: LayeredNetworkParameters):
        self._params = value

    @property
    def n_layers(self) -> int:
        """Number of layers."""
        return len(self._layer_neurons)

    def _create_neurons(self):
        """Create neurons organized in layers."""
        p = self.params

        # Use custom layer configs or generate defaults
        if p.layer_configs:
            configs = p.layer_configs
        else:
            configs = [
                LayerConfig(
                    n_neurons=p.neurons_per_layer,
                    oni_layer=i + 1 if p.use_oni_layers else None
                )
                for i in range(p.n_layers)
            ]

        # Create neurons for each layer
        for layer_idx, config in enumerate(configs):
            self._layer_configs[layer_idx] = config
            self._layer_neurons[layer_idx] = []

            n_exc = int(config.n_neurons * config.excitatory_ratio)
            n_inh = config.n_neurons - n_exc

            # Create excitatory neurons
            for i in range(n_exc):
                neuron_class = config.neuron_class or LIFNeuron
                if neuron_class == LIFNeuron:
                    neuron = LIFNeuron.create_excitatory()
                else:
                    neuron = neuron_class()

                # Set ONI layer if applicable
                if config.oni_layer:
                    neuron.params.oni_layer = config.oni_layer

                # Set position (for visualization)
                neuron.params.position = (
                    layer_idx * 100,  # x: layer position
                    i * 10,           # y: neuron position in layer
                    0                 # z
                )

                self.add_neuron(neuron, group=f"layer_{layer_idx}")
                self._layer_neurons[layer_idx].append(neuron.id)

            # Create inhibitory neurons
            for i in range(n_inh):
                neuron_class = config.neuron_class or LIFNeuron
                if neuron_class == LIFNeuron:
                    neuron = LIFNeuron.create_inhibitory()
                else:
                    neuron = neuron_class()
                    neuron.params.neuron_type = NeuronType.INHIBITORY

                if config.oni_layer:
                    neuron.params.oni_layer = config.oni_layer

                neuron.params.position = (
                    layer_idx * 100,
                    (n_exc + i) * 10,
                    0
                )

                self.add_neuron(neuron, group=f"layer_{layer_idx}")
                self._layer_neurons[layer_idx].append(neuron.id)

    def _create_synapses(self):
        """Create connections between and within layers."""
        p = self.params

        # Feedforward connections (layer i -> layer i+1)
        for layer_idx in range(self.n_layers - 1):
            self._create_layer_connections(
                source_layer=layer_idx,
                target_layer=layer_idx + 1,
                prob=p.feedforward_prob,
                weight=p.feedforward_weight
            )

        # Skip connections (if enabled)
        if p.skip_connections:
            for source in range(self.n_layers - 2):
                for target in range(source + 2, self.n_layers):
                    self._create_layer_connections(
                        source_layer=source,
                        target_layer=target,
                        prob=p.skip_prob,
                        weight=p.feedforward_weight * 0.5
                    )

        # Lateral connections within layers
        if p.lateral_connections:
            for layer_idx in range(self.n_layers):
                self._create_lateral_connections(layer_idx)

    def _create_layer_connections(
        self,
        source_layer: int,
        target_layer: int,
        prob: float,
        weight: float
    ):
        """Create connections between two layers."""
        source_ids = self._layer_neurons[source_layer]
        target_ids = self._layer_neurons[target_layer]

        for pre_id in source_ids:
            pre = self._neurons[pre_id]
            for post_id in target_ids:
                if np.random.random() < prob:
                    post = self._neurons[post_id]

                    # Determine synapse type based on presynaptic neuron
                    if pre.params.neuron_type == NeuronType.INHIBITORY:
                        params = ChemicalSynapseParameters.from_receptor(
                            ReceptorType.GABA_A,
                            weight=abs(weight),
                            dt=self.params.dt
                        )
                    else:
                        params = ChemicalSynapseParameters.from_receptor(
                            ReceptorType.AMPA,
                            weight=weight,
                            dt=self.params.dt
                        )

                    synapse = ChemicalSynapse(pre, post, params)
                    self.add_synapse(synapse)

    def _create_lateral_connections(self, layer_idx: int):
        """Create lateral connections within a layer."""
        p = self.params
        neuron_ids = self._layer_neurons[layer_idx]

        for pre_id in neuron_ids:
            pre = self._neurons[pre_id]
            for post_id in neuron_ids:
                if pre_id == post_id:
                    continue

                if np.random.random() < p.lateral_prob:
                    post = self._neurons[post_id]

                    # Inhibitory neurons make inhibitory synapses
                    if pre.params.neuron_type == NeuronType.INHIBITORY:
                        params = ChemicalSynapseParameters.from_receptor(
                            ReceptorType.GABA_A,
                            weight=abs(p.lateral_inhibitory_weight),
                            dt=self.params.dt
                        )
                    else:
                        params = ChemicalSynapseParameters.from_receptor(
                            ReceptorType.AMPA,
                            weight=p.lateral_weight,
                            dt=self.params.dt
                        )

                    synapse = ChemicalSynapse(pre, post, params)
                    self.add_synapse(synapse)

    def get_layer_neurons(self, layer_idx: int) -> List[Neuron]:
        """Get all neurons in a specific layer."""
        ids = self._layer_neurons.get(layer_idx, [])
        return [self._neurons[nid] for nid in ids]

    def get_layer_activity(self, layer_idx: int) -> Dict[str, float]:
        """Get mean activity metrics for a layer."""
        neurons = self.get_layer_neurons(layer_idx)
        if not neurons:
            return {}

        voltages = [n.state.V for n in neurons]
        spike_counts = [len(n.state.spike_times) for n in neurons]

        return {
            "mean_voltage": np.mean(voltages),
            "std_voltage": np.std(voltages),
            "total_spikes": sum(spike_counts),
            "mean_spikes": np.mean(spike_counts),
        }

    def inject_input(
        self,
        layer_idx: int,
        current: float,
        fraction: float = 1.0
    ):
        """
        Inject current into a layer.

        Args:
            layer_idx: Layer index
            current: Current amplitude (nA)
            fraction: Fraction of neurons to stimulate
        """
        neurons = self.get_layer_neurons(layer_idx)
        n_stimulate = int(len(neurons) * fraction)

        for neuron in neurons[:n_stimulate]:
            neuron.receive_input(current)

    def get_inter_layer_weights(
        self,
        source_layer: int,
        target_layer: int
    ) -> np.ndarray:
        """Get weight matrix between two layers."""
        source_ids = self._layer_neurons.get(source_layer, [])
        target_ids = self._layer_neurons.get(target_layer, [])

        W = np.zeros((len(source_ids), len(target_ids)))

        for i, pre_id in enumerate(source_ids):
            for j, post_id in enumerate(target_ids):
                synapses = self.get_synapses_between(pre_id, post_id)
                for syn in synapses:
                    W[i, j] += syn.weight

        return W

    def to_dict(self) -> Dict[str, Any]:
        """Serialize network."""
        data = super().to_dict()
        data["layers"] = {}
        for layer_idx in range(self.n_layers):
            data["layers"][layer_idx] = {
                "n_neurons": len(self._layer_neurons.get(layer_idx, [])),
                "activity": self.get_layer_activity(layer_idx),
            }
        return data

    @classmethod
    def create_oni_model(
        cls,
        neurons_per_layer: int = 50,
        **kwargs
    ) -> "LayeredNetwork":
        """
        Create network matching ONI Framework 14-layer model.

        Args:
            neurons_per_layer: Base neurons per layer
            **kwargs: Additional network parameters

        Returns:
            LayeredNetwork configured for ONI model
        """
        # Create layer configs for each ONI layer
        layer_configs = []
        for layer_num in range(1, 15):
            layer_info = ONI_LAYERS[layer_num]

            # Adjust size based on layer type
            if layer_info["type"] == "sensory":
                n = int(neurons_per_layer * 1.5)  # More sensory neurons
            elif layer_info["type"] == "motor":
                n = int(neurons_per_layer * 0.8)  # Fewer motor neurons
            elif layer_info["type"] == "executive":
                n = int(neurons_per_layer * 0.5)  # Sparse executive layers
            else:
                n = neurons_per_layer

            config = LayerConfig(
                n_neurons=n,
                oni_layer=layer_num,
                excitatory_ratio=0.8 if layer_info["type"] != "executive" else 0.6,
            )
            layer_configs.append(config)

        params = LayeredNetworkParameters(
            name="ONI_14Layer_Model",
            n_layers=14,
            layer_configs=layer_configs,
            use_oni_layers=True,
            feedforward_prob=0.2,
            feedforward_weight=0.5,
            skip_connections=True,
            skip_prob=0.02,
            lateral_connections=True,
            lateral_prob=0.15,
            **kwargs
        )

        return cls(params)

    @classmethod
    def create_simple(
        cls,
        n_layers: int = 3,
        neurons_per_layer: int = 100,
        **kwargs
    ) -> "LayeredNetwork":
        """Create a simple feedforward network."""
        params = LayeredNetworkParameters(
            n_layers=n_layers,
            neurons_per_layer=neurons_per_layer,
            **kwargs
        )
        return cls(params)
