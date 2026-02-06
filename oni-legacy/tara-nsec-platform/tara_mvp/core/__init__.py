"""
TARA Core Module

Security validation and ONI Framework components:
- Coherence metrics (Cₛ calculation)
- 14-layer ONI model
- Neural firewall
- Scale-frequency invariant
"""

from .coherence import CoherenceMetric, calculate_cs, VarianceComponents
from .layers import ONIStack, Layer, Domain
from .firewall import NeuralFirewall, Signal, FilterResult, Decision, AlertLevel
from .scale_freq import ScaleFrequencyInvariant

__all__ = [
    # Coherence
    "CoherenceMetric",
    "calculate_cs",
    "VarianceComponents",
    # Layers
    "ONIStack",
    "Layer",
    "Domain",
    # Firewall
    "NeuralFirewall",
    "Signal",
    "FilterResult",
    "Decision",
    "AlertLevel",
    # Scale-Frequency
    "ScaleFrequencyInvariant",
]
