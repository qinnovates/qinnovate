"""
NeuroSim Neuron Models

Implements various neuron models with increasing biological realism:
- LIF (Leaky Integrate-and-Fire): Simple, fast, good for large networks
- Adaptive LIF: LIF with spike-frequency adaptation
- Izhikevich: Rich dynamics, computationally efficient
- Hodgkin-Huxley: Biophysically detailed, ion channel dynamics
"""

from .base import Neuron, NeuronState, NeuronParameters
from .lif import LIFNeuron, LIFParameters
from .adaptive_lif import AdaptiveLIFNeuron, AdaptiveLIFParameters
from .izhikevich import IzhikevichNeuron, IzhikevichParameters
from .hodgkin_huxley import HodgkinHuxleyNeuron, HodgkinHuxleyParameters

__all__ = [
    "Neuron",
    "NeuronState",
    "NeuronParameters",
    "LIFNeuron",
    "LIFParameters",
    "AdaptiveLIFNeuron",
    "AdaptiveLIFParameters",
    "IzhikevichNeuron",
    "IzhikevichParameters",
    "HodgkinHuxleyNeuron",
    "HodgkinHuxleyParameters",
]
