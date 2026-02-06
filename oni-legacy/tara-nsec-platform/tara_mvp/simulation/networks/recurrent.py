"""
Recurrent Network Model

Implements networks with feedback connections, allowing for
temporal dynamics and memory-like behavior.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Type
import numpy as np

from .base import Network, NetworkParameters, ConnectionPattern
from ..neurons.base import Neuron, NeuronType
from ..neurons.lif import LIFNeuron
from ..neurons.izhikevich import IzhikevichNeuron, IzhikevichType
from ..synapses.chemical import ChemicalSynapse, ChemicalSynapseParameters, ReceptorType
from ..synapses.stdp import STDPSynapse, STDPParameters


@dataclass
class RecurrentNetworkParameters(NetworkParameters):
    """Parameters for recurrent network."""

    # Network size
    n_excitatory: int = 800           # Number of excitatory neurons
    n_inhibitory: int = 200           # Number of inhibitory neurons

    # Connectivity
    p_ee: float = 0.1                 # E -> E connection probability
    p_ei: float = 0.3                 # E -> I connection probability
    p_ie: float = 0.3                 # I -> E connection probability
    p_ii: float = 0.1                 # I -> I connection probability

    # Synaptic weights
    w_ee: float = 0.5                 # E -> E weight
    w_ei: float = 0.5                 # E -> I weight
    w_ie: float = -1.0                # I -> E weight (inhibitory)
    w_ii: float = -0.5                # I -> I weight (inhibitory)

    # Plasticity
    use_stdp: bool = False            # Enable STDP on E -> E connections
    stdp_lr: float = 0.01             # STDP learning rate

    # External input
    external_rate: float = 1.0        # Background input rate (spikes/ms)
    external_weight: float = 0.5      # Weight of external inputs

    # Neuron model
    use_izhikevich: bool = False      # Use Izhikevich instead of LIF

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "n_excitatory": self.n_excitatory,
            "n_inhibitory": self.n_inhibitory,
            "p_ee": self.p_ee,
            "p_ei": self.p_ei,
            "p_ie": self.p_ie,
            "p_ii": self.p_ii,
            "use_stdp": self.use_stdp,
        })
        return base


class RecurrentNetwork(Network):
    """
    Recurrent Neural Network with E/I Balance.

    Implements a network with both excitatory and inhibitory
    populations, recurrent connections, and optional STDP
    plasticity. This type of network can exhibit rich dynamics
    including oscillations and attractor states.

    The E/I balance is crucial for stable network activity
    and is a key feature in biological neural circuits.

    Usage:
        >>> net = RecurrentNetwork()
        >>> results = net.simulate(1000)  # 1 second simulation
        >>> # Analyze spike patterns and firing rates
    """

    def __init__(self, params: Optional[RecurrentNetworkParameters] = None):
        """
        Initialize recurrent network.

        Args:
            params: Network parameters
        """
        self._exc_neurons: List[str] = []
        self._inh_neurons: List[str] = []
        super().__init__(params or RecurrentNetworkParameters())

    @property
    def params(self) -> RecurrentNetworkParameters:
        """Type-hinted access to parameters."""
        return self._params

    @params.setter
    def params(self, value: RecurrentNetworkParameters):
        self._params = value

    @property
    def excitatory_neurons(self) -> List[Neuron]:
        """Get excitatory population."""
        return [self._neurons[nid] for nid in self._exc_neurons]

    @property
    def inhibitory_neurons(self) -> List[Neuron]:
        """Get inhibitory population."""
        return [self._neurons[nid] for nid in self._inh_neurons]

    def _create_neurons(self):
        """Create excitatory and inhibitory populations."""
        p = self.params

        # Create excitatory neurons
        for i in range(p.n_excitatory):
            if p.use_izhikevich:
                # Use regular spiking for excitatory
                neuron = IzhikevichNeuron.from_preset(IzhikevichType.RS)
            else:
                neuron = LIFNeuron.create_excitatory()

            # Random position
            neuron.params.position = (
                np.random.uniform(0, 100),
                np.random.uniform(0, 100),
                0
            )

            self.add_neuron(neuron, group="excitatory")
            self._exc_neurons.append(neuron.id)

        # Create inhibitory neurons
        for i in range(p.n_inhibitory):
            if p.use_izhikevich:
                # Use fast spiking for inhibitory
                neuron = IzhikevichNeuron.from_preset(IzhikevichType.FS)
            else:
                neuron = LIFNeuron.create_inhibitory()

            neuron.params.position = (
                np.random.uniform(0, 100),
                np.random.uniform(0, 100),
                0
            )

            self.add_neuron(neuron, group="inhibitory")
            self._inh_neurons.append(neuron.id)

    def _create_synapses(self):
        """Create recurrent connections."""
        p = self.params

        # E -> E connections
        self._create_population_connections(
            self._exc_neurons, self._exc_neurons,
            p.p_ee, p.w_ee,
            receptor=ReceptorType.AMPA,
            use_stdp=p.use_stdp
        )

        # E -> I connections
        self._create_population_connections(
            self._exc_neurons, self._inh_neurons,
            p.p_ei, p.w_ei,
            receptor=ReceptorType.AMPA
        )

        # I -> E connections
        self._create_population_connections(
            self._inh_neurons, self._exc_neurons,
            p.p_ie, abs(p.w_ie),
            receptor=ReceptorType.GABA_A
        )

        # I -> I connections
        self._create_population_connections(
            self._inh_neurons, self._inh_neurons,
            p.p_ii, abs(p.w_ii),
            receptor=ReceptorType.GABA_A
        )

    def _create_population_connections(
        self,
        source_ids: List[str],
        target_ids: List[str],
        prob: float,
        weight: float,
        receptor: ReceptorType,
        use_stdp: bool = False
    ):
        """Create connections between two populations."""
        for pre_id in source_ids:
            pre = self._neurons[pre_id]
            for post_id in target_ids:
                if pre_id == post_id:
                    continue  # No self-connections

                if np.random.random() < prob:
                    post = self._neurons[post_id]

                    if use_stdp and receptor == ReceptorType.AMPA:
                        # Use STDP synapse
                        params = STDPParameters(
                            receptor=receptor,
                            weight=weight,
                            dt=self.params.dt,
                            learning_rate=self.params.stdp_lr
                        )
                        synapse = STDPSynapse(pre, post, params)
                    else:
                        # Regular chemical synapse
                        params = ChemicalSynapseParameters.from_receptor(
                            receptor,
                            weight=weight,
                            dt=self.params.dt
                        )
                        synapse = ChemicalSynapse(pre, post, params)

                    self.add_synapse(synapse)

    def apply_external_input(self):
        """Apply Poisson-distributed external input."""
        p = self.params

        for neuron in self._neurons.values():
            # Poisson spike arrival
            if np.random.random() < p.external_rate * p.dt:
                neuron.receive_input(p.external_weight)

    def step(self, record_history: bool = True) -> Dict[str, bool]:
        """Step with external input."""
        self.apply_external_input()
        return super().step(record_history)

    def get_population_rates(self, window: float = 100.0) -> Dict[str, float]:
        """
        Compute firing rates for E and I populations.

        Args:
            window: Time window (ms)

        Returns:
            Dictionary with E and I rates
        """
        t_current = self.state.t

        def compute_rate(neuron_ids):
            total_spikes = 0
            for nid in neuron_ids:
                neuron = self._neurons[nid]
                spikes = sum(
                    1 for st in neuron.state.spike_times
                    if t_current - window <= st <= t_current
                )
                total_spikes += spikes
            n_neurons = len(neuron_ids)
            if n_neurons == 0:
                return 0.0
            return total_spikes / (n_neurons * window / 1000)  # Hz

        return {
            "excitatory_rate": compute_rate(self._exc_neurons),
            "inhibitory_rate": compute_rate(self._inh_neurons),
        }

    def compute_ei_balance(self) -> Dict[str, float]:
        """
        Compute E/I balance metrics.

        Returns:
            Dictionary with balance metrics
        """
        # Total synaptic weights
        total_exc = 0.0
        total_inh = 0.0

        for synapse in self._synapses:
            if synapse.params.synapse_type.value == "excitatory":
                total_exc += synapse.weight
            else:
                total_inh += abs(synapse.weight)

        balance = total_exc / (total_inh + 1e-10)

        return {
            "total_excitation": total_exc,
            "total_inhibition": total_inh,
            "ei_ratio": balance,
        }

    def get_weight_distribution(self) -> Dict[str, np.ndarray]:
        """Get distribution of synaptic weights."""
        exc_weights = []
        inh_weights = []

        for synapse in self._synapses:
            if synapse.params.synapse_type.value == "excitatory":
                exc_weights.append(synapse.weight)
            else:
                inh_weights.append(synapse.weight)

        return {
            "excitatory": np.array(exc_weights),
            "inhibitory": np.array(inh_weights),
        }

    def get_connectivity_stats(self) -> Dict[str, Any]:
        """Get connectivity statistics."""
        # Count connections by type
        n_ee = n_ei = n_ie = n_ii = 0

        for synapse in self._synapses:
            pre_exc = synapse.pre.id in self._exc_neurons
            post_exc = synapse.post.id in self._exc_neurons

            if pre_exc and post_exc:
                n_ee += 1
            elif pre_exc and not post_exc:
                n_ei += 1
            elif not pre_exc and post_exc:
                n_ie += 1
            else:
                n_ii += 1

        # Compute actual probabilities
        n_e = len(self._exc_neurons)
        n_i = len(self._inh_neurons)

        return {
            "n_ee": n_ee,
            "n_ei": n_ei,
            "n_ie": n_ie,
            "n_ii": n_ii,
            "p_ee_actual": n_ee / (n_e * (n_e - 1) + 1e-10),
            "p_ei_actual": n_ei / (n_e * n_i + 1e-10),
            "p_ie_actual": n_ie / (n_i * n_e + 1e-10),
            "p_ii_actual": n_ii / (n_i * (n_i - 1) + 1e-10),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize network."""
        data = super().to_dict()
        data["populations"] = {
            "excitatory": len(self._exc_neurons),
            "inhibitory": len(self._inh_neurons),
        }
        data["ei_balance"] = self.compute_ei_balance()
        data["connectivity"] = self.get_connectivity_stats()
        return data

    @classmethod
    def create_balanced(
        cls,
        n_neurons: int = 1000,
        g: float = 4.0,
        **kwargs
    ) -> "RecurrentNetwork":
        """
        Create a balanced E/I network.

        The inhibitory weight is scaled by factor g to achieve
        balance between excitation and inhibition.

        Args:
            n_neurons: Total number of neurons (80% E, 20% I)
            g: Relative strength of inhibition
            **kwargs: Additional parameters

        Returns:
            Balanced RecurrentNetwork
        """
        n_exc = int(n_neurons * 0.8)
        n_inh = n_neurons - n_exc

        # Scale inhibitory weights for balance
        # Theory: g * J_E * N_E * p = g * J_I * N_I * p
        # With 4:1 E:I ratio, g ≈ 4 for balance

        params = RecurrentNetworkParameters(
            n_excitatory=n_exc,
            n_inhibitory=n_inh,
            w_ie=-g * 0.5,  # Scale inhibitory weight
            w_ii=-g * 0.25,
            **kwargs
        )
        return cls(params)

    @classmethod
    def create_plastic(
        cls,
        n_neurons: int = 500,
        stdp_lr: float = 0.01,
        **kwargs
    ) -> "RecurrentNetwork":
        """
        Create a network with STDP plasticity.

        Args:
            n_neurons: Total number of neurons
            stdp_lr: STDP learning rate
            **kwargs: Additional parameters

        Returns:
            RecurrentNetwork with STDP
        """
        n_exc = int(n_neurons * 0.8)
        n_inh = n_neurons - n_exc

        params = RecurrentNetworkParameters(
            n_excitatory=n_exc,
            n_inhibitory=n_inh,
            use_stdp=True,
            stdp_lr=stdp_lr,
            **kwargs
        )
        return cls(params)
