"""
TARA Neurosecurity Integration

Integrates neurosecurity principles from foundational BCI security research
into TARA's real-time monitoring and threat detection capabilities.

Implements:
- Kohno et al. (2009) threat taxonomy (Alteration, Blocking, Eavesdropping)
- BCI privacy filtering concepts from Bonaci et al. (2015)

This module wraps the ONI Framework's neurosecurity components and provides
TARA-specific integration with the NSAM detection engine.

Note on Patent Status:
    The BCI Anonymizer patent application (US20140228701A1) was ABANDONED
    and never granted. The concepts from the academic research are freely
    available for implementation.

References:
    Denning, T., Matsuoka, Y., & Kohno, T. (2009). Neurosecurity: Security
    and privacy for neural devices. Neurosurgical Focus, 27(1), E7.

    Bonaci, T., Calo, R., & Chizeck, H. J. (2015). App stores for the brain:
    Privacy and security in brain-computer interfaces. IEEE Technology and
    Society Magazine, 34(2), 32-39.
"""

import sys
from pathlib import Path

# Add oni-framework to path if not already available
_oni_framework_path = Path(__file__).parent.parent.parent / "oni-framework"
if _oni_framework_path.exists() and str(_oni_framework_path) not in sys.path:
    sys.path.insert(0, str(_oni_framework_path))

# Import from ONI Framework neurosecurity module
try:
    from oni.neurosecurity import (
        # Threats (Kohno 2009)
        ThreatType,
        SecurityDecision,
        KohnoThreatModel,
        # Firewall
        NeurosecurityFirewall,
        NeurosecurityConfig,
        # Anonymizer (BCI Privacy Research)
        BCIAnonymizer,
        AnonymizerConfig,
        ERPType,
        PrivacySensitivity,
        # Privacy Score
        PrivacyScoreCalculator,
        PrivacyScoreResult,
    )
    _ONI_AVAILABLE = True
except ImportError:
    _ONI_AVAILABLE = False
    # Provide stub classes if ONI not available
    ThreatType = None
    SecurityDecision = None
    KohnoThreatModel = None
    NeurosecurityFirewall = None
    NeurosecurityConfig = None
    BCIAnonymizer = None
    AnonymizerConfig = None
    ERPType = None
    PrivacySensitivity = None
    PrivacyScoreCalculator = None
    PrivacyScoreResult = None

# TARA-specific integration
from .integration import (
    NeurosecurityMonitor,
    create_kohno_rules,
    KOHNO_DETECTION_RULES,
)

__all__ = [
    # Availability flag
    "_ONI_AVAILABLE",
    # Kohno Threats
    "ThreatType",
    "SecurityDecision",
    "KohnoThreatModel",
    # Firewall
    "NeurosecurityFirewall",
    "NeurosecurityConfig",
    # BCI Privacy
    "BCIAnonymizer",
    "AnonymizerConfig",
    "ERPType",
    "PrivacySensitivity",
    # Privacy Score
    "PrivacyScoreCalculator",
    "PrivacyScoreResult",
    # TARA Integration
    "NeurosecurityMonitor",
    "create_kohno_rules",
    "KOHNO_DETECTION_RULES",
]
