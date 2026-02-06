"""
TARA Simulation Module

Neural network simulation components:
- Neuron models (LIF, Izhikevich, Hodgkin-Huxley, Adaptive LIF)
- Synapse models (Chemical, Electrical, STDP)
- Network architectures (Layered, Recurrent, Small-World)
- Simulation engine
"""

# Neurons
from .neurons import (
    Neuron,
    LIFNeuron,
    IzhikevichNeuron,
    HodgkinHuxleyNeuron,
    AdaptiveLIFNeuron,
)

# Synapses
from .synapses import (
    Synapse,
    ChemicalSynapse,
    ElectricalSynapse,
    STDPSynapse,
)

# Networks
from .networks import (
    Network,
    LayeredNetwork,
    RecurrentNetwork,
    SmallWorldNetwork,
)

# Engine
from .engine import (
    SimulationEngine,
    SimulationConfig,
    Recorder,
    RecordingConfig,
)

__all__ = [
    # Neurons
    "Neuron",
    "LIFNeuron",
    "IzhikevichNeuron",
    "HodgkinHuxleyNeuron",
    "AdaptiveLIFNeuron",
    # Synapses
    "Synapse",
    "ChemicalSynapse",
    "ElectricalSynapse",
    "STDPSynapse",
    # Networks
    "Network",
    "LayeredNetwork",
    "RecurrentNetwork",
    "SmallWorldNetwork",
    # Engine
    "SimulationEngine",
    "SimulationConfig",
    "Recorder",
    "RecordingConfig",
]
