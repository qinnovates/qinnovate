"""
NeuroSim Synapse Models

Implements various synapse types for neural connectivity:
- ChemicalSynapse: Standard AMPA/GABA-like synapses
- ElectricalSynapse: Gap junctions
- STDPSynapse: Spike-timing dependent plasticity
"""

from .base import Synapse, SynapseParameters, SynapseState
from .chemical import ChemicalSynapse, ChemicalSynapseParameters
from .electrical import ElectricalSynapse, ElectricalSynapseParameters
from .stdp import STDPSynapse, STDPParameters

__all__ = [
    "Synapse",
    "SynapseParameters",
    "SynapseState",
    "ChemicalSynapse",
    "ChemicalSynapseParameters",
    "ElectricalSynapse",
    "ElectricalSynapseParameters",
    "STDPSynapse",
    "STDPParameters",
]
