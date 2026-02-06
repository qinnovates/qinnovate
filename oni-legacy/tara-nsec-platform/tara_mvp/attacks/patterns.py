"""
Attack Pattern Definitions

Defines various neural attack patterns based on the ONI Framework
threat model, including attacks at different layers.

Incorporates:
- Yale Digital Ethics Center BCI threat model (Schroder et al., 2025)
- CVSS v4.0 scoring for vulnerability assessment
- Kohno (2009) neurosecurity CIA taxonomy

References:
- Schroder, T., et al. (2025). Cyber Risks to Next-Gen BCIs. Neuroethics.
- FIRST. (2023). Common Vulnerability Scoring System v4.0.
- Kohno, T., et al. (2009). Neurosecurity. J Neurosurg Focus.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from enum import Enum, auto
import numpy as np


class AttackType(Enum):
    """Categories of neural attacks."""

    # Signal-level attacks
    SIGNAL_INJECTION = auto()       # Inject fake signals
    SIGNAL_JAMMING = auto()         # Disrupt signal transmission
    SIGNAL_REPLAY = auto()          # Replay captured signals

    # Coherence attacks
    PHASE_DISRUPTION = auto()       # Disrupt timing/phase coherence
    AMPLITUDE_MANIPULATION = auto() # Manipulate signal amplitudes
    DESYNCHRONIZATION = auto()      # Break neural synchrony

    # Network-level attacks
    NEURAL_RANSOMWARE = auto()      # Lock neural patterns
    NETWORK_HIJACKING = auto()      # Take control of neural pathways
    DOS_FLOODING = auto()           # Overwhelm with excessive signals

    # Layer-specific attacks
    LAYER_8_GATEWAY = auto()        # Attack the neural gateway
    LAYER_TRAVERSAL = auto()        # Cross-layer attack
    SIDE_CHANNEL = auto()           # Information leakage

    # Yale Threat Model Categories (Schroder et al., 2025)
    MALICIOUS_UPDATE = auto()       # Compromised firmware/software update
    AUTH_BYPASS = auto()            # Authentication/authorization bypass
    WIRELESS_EXPLOIT = auto()       # Wireless connection exploitation
    ENCRYPTION_ATTACK = auto()      # Attack on unencrypted data
    AI_MANIPULATION = auto()        # Malicious AI-mediated stimuli


class YaleThreatCategory(Enum):
    """
    Yale Digital Ethics Center BCI Threat Categories.

    From: Schroder, T., et al. (2025). Cyber Risks to Next-Gen BCIs.

    The four key vulnerability areas identified by Yale researchers:
    1. SOFTWARE_UPDATE - Malicious firmware/software modifications
    2. AUTHENTICATION - Weak or absent access controls
    3. WIRELESS - Exposure through network connections
    4. ENCRYPTION - Unprotected data in transit/at rest
    """
    SOFTWARE_UPDATE = "software_update"
    AUTHENTICATION = "authentication"
    WIRELESS = "wireless"
    ENCRYPTION = "encryption"


class CVSSMetric(Enum):
    """
    CVSS v4.0 Base Metric Values.

    Reference: FIRST CVSS v4.0 Specification (2023)
    https://www.first.org/cvss/v4.0/
    """
    # Attack Vector (AV)
    AV_NETWORK = "N"      # Network - remotely exploitable
    AV_ADJACENT = "A"     # Adjacent network
    AV_LOCAL = "L"        # Local access required
    AV_PHYSICAL = "P"     # Physical access required

    # Attack Complexity (AC)
    AC_LOW = "L"          # No special conditions
    AC_HIGH = "H"         # Specialized conditions required

    # Attack Requirements (AT) - New in CVSS 4.0
    AT_NONE = "N"         # No prerequisites
    AT_PRESENT = "P"      # Specific deployment conditions needed

    # Privileges Required (PR)
    PR_NONE = "N"         # No privileges needed
    PR_LOW = "L"          # Basic privileges
    PR_HIGH = "H"         # Administrative privileges

    # User Interaction (UI)
    UI_NONE = "N"         # No user interaction
    UI_PASSIVE = "P"      # Passive interaction
    UI_ACTIVE = "A"       # Active user participation

    # Impact: Confidentiality/Integrity/Availability
    IMPACT_NONE = "N"
    IMPACT_LOW = "L"
    IMPACT_HIGH = "H"


class AttackVector(Enum):
    """Attack entry points in the ONI model."""
    ELECTRODE_INTERFACE = "L8"      # Physical interface
    SIGNAL_PROCESSING = "L9"        # Signal processing
    PROTOCOL_LAYER = "L10"          # Protocol exploits
    TRANSPORT_LAYER = "L11"         # Connection attacks
    APPLICATION_LAYER = "L14"       # Application exploits


@dataclass
class CVSSScore:
    """
    CVSS v4.0 Base Score for vulnerability assessment.

    Reference: https://www.first.org/cvss/v4.0/

    CVSS (Common Vulnerability Scoring System) provides a standardized
    way to assess the severity of security vulnerabilities. While no
    CVEs currently exist specifically for BCIs (as of 2025), CVSS
    provides a framework for prospective risk assessment.

    Note on CVE: Common Vulnerabilities and Exposures (CVE) is a
    dictionary of publicly known security vulnerabilities. As BCIs
    are still emerging (~60 implants as of 2024), no CVEs have been
    formally catalogued. TARA uses CVSS for prospective scoring.

    Attributes:
        attack_vector: How the vulnerability can be exploited
        attack_complexity: Conditions beyond attacker control
        attack_requirements: Prerequisites at target (CVSS 4.0)
        privileges_required: Level of privileges needed
        user_interaction: User involvement required
        vuln_conf_impact: Confidentiality impact on vulnerable system
        vuln_integ_impact: Integrity impact on vulnerable system
        vuln_avail_impact: Availability impact on vulnerable system
        subseq_conf_impact: Confidentiality impact on subsequent systems
        subseq_integ_impact: Integrity impact on subsequent systems
        subseq_avail_impact: Availability impact on subsequent systems
    """
    # Exploitability Metrics
    attack_vector: str = CVSSMetric.AV_NETWORK.value
    attack_complexity: str = CVSSMetric.AC_LOW.value
    attack_requirements: str = CVSSMetric.AT_NONE.value
    privileges_required: str = CVSSMetric.PR_NONE.value
    user_interaction: str = CVSSMetric.UI_NONE.value

    # Vulnerable System Impact
    vuln_conf_impact: str = CVSSMetric.IMPACT_LOW.value
    vuln_integ_impact: str = CVSSMetric.IMPACT_LOW.value
    vuln_avail_impact: str = CVSSMetric.IMPACT_LOW.value

    # Subsequent System Impact (CVSS 4.0 - replaces Scope)
    subseq_conf_impact: str = CVSSMetric.IMPACT_NONE.value
    subseq_integ_impact: str = CVSSMetric.IMPACT_NONE.value
    subseq_avail_impact: str = CVSSMetric.IMPACT_NONE.value

    @property
    def vector_string(self) -> str:
        """Generate CVSS v4.0 vector string."""
        return (
            f"CVSS:4.0/AV:{self.attack_vector}/AC:{self.attack_complexity}/"
            f"AT:{self.attack_requirements}/PR:{self.privileges_required}/"
            f"UI:{self.user_interaction}/VC:{self.vuln_conf_impact}/"
            f"VI:{self.vuln_integ_impact}/VA:{self.vuln_avail_impact}/"
            f"SC:{self.subseq_conf_impact}/SI:{self.subseq_integ_impact}/"
            f"SA:{self.subseq_avail_impact}"
        )

    @property
    def base_score(self) -> float:
        """
        Calculate approximate CVSS v4.0 base score.

        This is a simplified calculation. Full CVSS 4.0 scoring
        uses complex equivalence classes. See:
        https://www.first.org/cvss/v4.0/specification-document

        Returns:
            float: Score from 0.0 to 10.0
        """
        # Impact weights
        impact_weights = {"N": 0.0, "L": 0.22, "H": 0.56}

        # Exploitability weights
        av_weights = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
        ac_weights = {"L": 0.77, "H": 0.44}
        at_weights = {"N": 1.0, "P": 0.91}
        pr_weights = {"N": 0.85, "L": 0.62, "H": 0.27}
        ui_weights = {"N": 0.85, "P": 0.62, "A": 0.27}

        # Calculate exploitability
        exploitability = (
            8.22 *
            av_weights.get(self.attack_vector, 0.5) *
            ac_weights.get(self.attack_complexity, 0.5) *
            at_weights.get(self.attack_requirements, 0.5) *
            pr_weights.get(self.privileges_required, 0.5) *
            ui_weights.get(self.user_interaction, 0.5)
        )

        # Calculate impact (vulnerable system)
        vuln_impact = 1 - (
            (1 - impact_weights.get(self.vuln_conf_impact, 0)) *
            (1 - impact_weights.get(self.vuln_integ_impact, 0)) *
            (1 - impact_weights.get(self.vuln_avail_impact, 0))
        )

        # Calculate impact (subsequent systems)
        subseq_impact = 1 - (
            (1 - impact_weights.get(self.subseq_conf_impact, 0)) *
            (1 - impact_weights.get(self.subseq_integ_impact, 0)) *
            (1 - impact_weights.get(self.subseq_avail_impact, 0))
        )

        # Combined impact
        total_impact = max(vuln_impact, vuln_impact + 0.5 * subseq_impact)

        if total_impact <= 0:
            return 0.0

        # Base score calculation
        score = min(10.0, exploitability + 5.0 * total_impact)
        return round(score, 1)

    @property
    def severity(self) -> str:
        """
        Get qualitative severity rating.

        Returns:
            str: None, Low, Medium, High, or Critical
        """
        score = self.base_score
        if score == 0.0:
            return "None"
        elif score < 4.0:
            return "Low"
        elif score < 7.0:
            return "Medium"
        elif score < 9.0:
            return "High"
        else:
            return "Critical"


@dataclass
class AttackPattern:
    """
    Defines a specific attack pattern.

    An attack pattern specifies how malicious signals are generated
    and what neural characteristics they target.

    Attributes:
        name: Human-readable attack name
        attack_type: Category of attack
        target_layer: ONI layer targeted (1-14)
        description: Detailed description
        parameters: Attack-specific parameters
        duration: Attack duration in ms
        intensity: Attack intensity (0-1)
        cvss: CVSS v4.0 score for vulnerability assessment
        yale_category: Yale threat category (if applicable)
        references: Academic/industry references
    """
    name: str
    attack_type: AttackType
    target_layer: int
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    duration: float = 1000.0  # ms
    intensity: float = 0.5    # 0-1 scale
    cvss: Optional[CVSSScore] = None
    yale_category: Optional[YaleThreatCategory] = None
    references: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not 1 <= self.target_layer <= 14:
            raise ValueError(f"target_layer must be 1-14, got {self.target_layer}")
        if not 0 <= self.intensity <= 1:
            raise ValueError(f"intensity must be 0-1, got {self.intensity}")

    @property
    def cvss_score(self) -> float:
        """Get CVSS base score, or 0.0 if not set."""
        return self.cvss.base_score if self.cvss else 0.0

    @property
    def cvss_severity(self) -> str:
        """Get CVSS severity rating, or 'Unknown' if not set."""
        return self.cvss.severity if self.cvss else "Unknown"


# Predefined attack patterns
ATTACK_PATTERNS = {
    "phase_jitter": AttackPattern(
        name="Phase Jitter Attack",
        attack_type=AttackType.PHASE_DISRUPTION,
        target_layer=8,
        description="Introduces timing jitter to disrupt phase coherence",
        parameters={
            "jitter_std": 5.0,        # ms standard deviation
            "frequency_target": 40.0,  # Hz (gamma band)
        },
        intensity=0.7,
    ),

    "amplitude_surge": AttackPattern(
        name="Amplitude Surge Attack",
        attack_type=AttackType.AMPLITUDE_MANIPULATION,
        target_layer=9,
        description="Sudden amplitude spikes to overwhelm signal processing",
        parameters={
            "surge_factor": 10.0,      # Amplitude multiplier
            "surge_duration": 50.0,    # ms
            "surge_frequency": 5.0,    # Surges per second
        },
        intensity=0.8,
    ),

    "desync_wave": AttackPattern(
        name="Desynchronization Wave",
        attack_type=AttackType.DESYNCHRONIZATION,
        target_layer=3,
        description="Disrupts local neural circuit synchronization",
        parameters={
            "phase_offset_range": np.pi,  # Max phase offset
            "spread_rate": 10.0,          # Neurons per ms
        },
        intensity=0.6,
    ),

    "neural_ransomware": AttackPattern(
        name="Neural Ransomware",
        attack_type=AttackType.NEURAL_RANSOMWARE,
        target_layer=6,
        description="Locks neural patterns by disrupting memory encoding",
        parameters={
            "lock_pattern": "oscillation_override",
            "target_frequency": 8.0,   # Theta (memory)
            "override_frequency": 40.0, # Replace with gamma
        },
        duration=5000.0,  # 5 seconds
        intensity=0.9,
    ),

    "replay_attack": AttackPattern(
        name="Signal Replay Attack",
        attack_type=AttackType.SIGNAL_REPLAY,
        target_layer=8,
        description="Replays previously captured neural signals",
        parameters={
            "replay_delay": 100.0,     # ms delay
            "replay_count": 10,        # Number of replays
        },
        intensity=0.5,
    ),

    "dos_flood": AttackPattern(
        name="Neural DoS Flood",
        attack_type=AttackType.DOS_FLOODING,
        target_layer=8,
        description="Overwhelms the neural gateway with excessive signals",
        parameters={
            "signal_rate": 1000.0,     # Signals per second
            "signal_amplitude": 100.0, # μV
        },
        intensity=1.0,
    ),

    "side_channel_leak": AttackPattern(
        name="Side Channel Information Leak",
        attack_type=AttackType.SIDE_CHANNEL,
        target_layer=9,
        description="Extracts information through signal timing analysis",
        parameters={
            "sampling_rate": 10000.0,  # Hz
            "correlation_window": 100.0, # ms
        },
        intensity=0.3,
    ),

    "gateway_bypass": AttackPattern(
        name="Gateway Bypass Attack",
        attack_type=AttackType.LAYER_8_GATEWAY,
        target_layer=8,
        description="Attempts to bypass neural firewall validation",
        parameters={
            "mimic_coherence": True,   # Try to fake coherent signals
            "target_coherence": 0.7,   # Target Cs to mimic
            "evasion_technique": "gradual_shift",
        },
        intensity=0.6,
    ),

    # =========================================================================
    # Yale Threat Model Attack Patterns (Schroder et al., 2025)
    # Source: "Cyber Risks to Next-Gen Brain-Computer Interfaces"
    # https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5138265
    # =========================================================================

    "malicious_firmware_update": AttackPattern(
        name="Malicious Firmware Update",
        attack_type=AttackType.MALICIOUS_UPDATE,
        target_layer=7,  # Application layer
        description=(
            "Compromised firmware update that modifies BCI behavior. "
            "Yale researchers note older devices assume connection implies authorization."
        ),
        parameters={
            "payload_type": "behavior_modification",
            "persistence": True,
            "recovery_blocked": True,
        },
        duration=60000.0,  # 60 seconds
        intensity=0.95,
        cvss=CVSSScore(
            attack_vector="N",      # Network
            attack_complexity="L",  # Low - no special conditions
            attack_requirements="N", # None
            privileges_required="L", # Low - needs some access
            user_interaction="N",   # None required
            vuln_conf_impact="H",   # High - full device control
            vuln_integ_impact="H",  # High - modifies behavior
            vuln_avail_impact="H",  # High - can brick device
            subseq_conf_impact="H", # Neural data exposed
            subseq_integ_impact="H", # Brain signals modified
            subseq_avail_impact="L", # Some cognitive impact
        ),
        yale_category=YaleThreatCategory.SOFTWARE_UPDATE,
        references=[
            "Schroder et al. (2025). Cyber Risks to Next-Gen BCIs. Neuroethics.",
            "Yale News (2025). Study offers measures for safeguarding brain implants.",
        ],
    ),

    "auth_bypass_wireless": AttackPattern(
        name="Wireless Authentication Bypass",
        attack_type=AttackType.AUTH_BYPASS,
        target_layer=8,  # Neural Gateway
        description=(
            "Exploits weak/absent authentication on BCI wireless interface. "
            "Many older devices assume connection implies authorization to make changes."
        ),
        parameters={
            "exploit_type": "default_credentials",
            "connection_method": "bluetooth_le",
            "privilege_escalation": True,
        },
        duration=5000.0,
        intensity=0.8,
        cvss=CVSSScore(
            attack_vector="A",      # Adjacent network (Bluetooth range)
            attack_complexity="L",  # Low
            attack_requirements="N", # None
            privileges_required="N", # None - that's the vulnerability
            user_interaction="N",
            vuln_conf_impact="H",
            vuln_integ_impact="H",
            vuln_avail_impact="L",
            subseq_conf_impact="H", # Can access neural data
            subseq_integ_impact="H", # Can modify settings
            subseq_avail_impact="N",
        ),
        yale_category=YaleThreatCategory.AUTHENTICATION,
        references=[
            "Schroder et al. (2025). Cyber Risks to Next-Gen BCIs. Neuroethics.",
        ],
    ),

    "wireless_network_exploit": AttackPattern(
        name="Wireless Network Exploitation",
        attack_type=AttackType.WIRELESS_EXPLOIT,
        target_layer=8,
        description=(
            "Exploits constant wireless network connections that expose BCIs to attack. "
            "Yale recommends patient-controlled wireless enable/disable feature."
        ),
        parameters={
            "attack_surface": "always_on_wifi",
            "exploit_chain": ["network_scan", "vulnerability_probe", "exploit"],
            "target_protocol": "802.11",
        },
        duration=30000.0,
        intensity=0.7,
        cvss=CVSSScore(
            attack_vector="N",      # Network
            attack_complexity="H",  # High - needs specific conditions
            attack_requirements="P", # Present - device must be connected
            privileges_required="N",
            user_interaction="N",
            vuln_conf_impact="H",
            vuln_integ_impact="L",
            vuln_avail_impact="H",  # Can disrupt service
            subseq_conf_impact="L",
            subseq_integ_impact="L",
            subseq_avail_impact="L",
        ),
        yale_category=YaleThreatCategory.WIRELESS,
        references=[
            "Schroder et al. (2025). Cyber Risks to Next-Gen BCIs. Neuroethics.",
        ],
    ),

    "unencrypted_neural_intercept": AttackPattern(
        name="Unencrypted Neural Data Interception",
        attack_type=AttackType.ENCRYPTION_ATTACK,
        target_layer=10,  # Neural Protocol
        description=(
            "Intercepts unencrypted neural data in transit. Most BCIs lack encryption "
            "due to power constraints, despite FDA requirements for health data encryption."
        ),
        parameters={
            "intercept_method": "wireless_sniffing",
            "data_types": ["neural_signals", "commands", "settings"],
            "realtime": True,
        },
        duration=60000.0,
        intensity=0.6,
        cvss=CVSSScore(
            attack_vector="A",      # Adjacent (wireless range)
            attack_complexity="L",  # Low - just sniff traffic
            attack_requirements="P", # Device transmitting
            privileges_required="N",
            user_interaction="N",
            vuln_conf_impact="H",   # Full data exposure
            vuln_integ_impact="N",  # Read-only attack
            vuln_avail_impact="N",
            subseq_conf_impact="H", # Neural privacy breach
            subseq_integ_impact="N",
            subseq_avail_impact="N",
        ),
        yale_category=YaleThreatCategory.ENCRYPTION,
        references=[
            "Schroder et al. (2025). Cyber Risks to Next-Gen BCIs. Neuroethics.",
            "FDA Medical Device Cybersecurity Guidelines (2023).",
        ],
    ),

    "ai_malicious_stimulation": AttackPattern(
        name="AI-Mediated Malicious Stimulation",
        attack_type=AttackType.AI_MANIPULATION,
        target_layer=13,  # Semantic - intent/action
        description=(
            "Uses compromised AI to send malicious stimuli to patient's implant, "
            "causing unwanted BCI actions. Particularly dangerous for bidirectional BCIs."
        ),
        parameters={
            "ai_component": "decoder_model",
            "attack_vector": "adversarial_input",
            "target_action": "motor_command",
            "reversible": False,
        },
        duration=1000.0,
        intensity=1.0,
        cvss=CVSSScore(
            attack_vector="N",
            attack_complexity="H",  # Requires AI expertise
            attack_requirements="P", # AI system must be in use
            privileges_required="L", # Need access to AI pipeline
            user_interaction="N",
            vuln_conf_impact="L",
            vuln_integ_impact="H",  # False commands sent
            vuln_avail_impact="H",  # Patient safety
            subseq_conf_impact="N",
            subseq_integ_impact="H", # Physical movement affected
            subseq_avail_impact="H", # Potential injury
        ),
        yale_category=YaleThreatCategory.SOFTWARE_UPDATE,  # AI is software
        references=[
            "Schroder et al. (2025). Cyber Risks to Next-Gen BCIs. Neuroethics.",
            "Yale News: 'AI in personalized medicine like BCIs has both benefits and risks.'",
        ],
    ),

    "mass_neural_manipulation": AttackPattern(
        name="Mass Neural Manipulation",
        attack_type=AttackType.NETWORK_HIJACKING,
        target_layer=14,  # Identity - cognitive function
        description=(
            "Worst-case scenario: widespread attack on standardized BCI systems "
            "affecting millions simultaneously. Could cause mass disorientation "
            "or harvest thoughts/memories across populations."
        ),
        parameters={
            "scope": "population_scale",
            "target_systems": "standardized_bci",
            "objectives": ["cognitive_disruption", "data_harvesting"],
            "coordination": "botnet",
        },
        duration=3600000.0,  # 1 hour
        intensity=1.0,
        cvss=CVSSScore(
            attack_vector="N",
            attack_complexity="H",  # Requires massive coordination
            attack_requirements="P", # Standardized systems needed
            privileges_required="H", # High-level access required
            user_interaction="N",
            vuln_conf_impact="H",
            vuln_integ_impact="H",
            vuln_avail_impact="H",
            subseq_conf_impact="H", # Population-level data breach
            subseq_integ_impact="H", # Social disruption
            subseq_avail_impact="H", # Critical infrastructure impact
        ),
        yale_category=YaleThreatCategory.WIRELESS,
        references=[
            "Schroder et al. (2025): 'A widespread security breach could affect "
            "millions of users simultaneously, leading to mass manipulation of "
            "neural data or the impairment of cognitive functions.'",
        ],
    ),
}


def get_pattern(name: str) -> AttackPattern:
    """Get a predefined attack pattern by name."""
    if name not in ATTACK_PATTERNS:
        raise KeyError(f"Unknown attack pattern: {name}. "
                      f"Available: {list(ATTACK_PATTERNS.keys())}")
    return ATTACK_PATTERNS[name]


def list_patterns() -> List[str]:
    """List all available attack pattern names."""
    return list(ATTACK_PATTERNS.keys())


def patterns_by_layer(layer: int) -> List[AttackPattern]:
    """Get all attack patterns targeting a specific layer."""
    return [p for p in ATTACK_PATTERNS.values() if p.target_layer == layer]


def patterns_by_type(attack_type: AttackType) -> List[AttackPattern]:
    """Get all attack patterns of a specific type."""
    return [p for p in ATTACK_PATTERNS.values() if p.attack_type == attack_type]


def patterns_by_yale_category(category: YaleThreatCategory) -> List[AttackPattern]:
    """
    Get all attack patterns matching a Yale threat category.

    Args:
        category: YaleThreatCategory enum value

    Returns:
        List of AttackPatterns with that Yale category

    Example:
        >>> wireless_attacks = patterns_by_yale_category(YaleThreatCategory.WIRELESS)
        >>> for attack in wireless_attacks:
        ...     print(f"{attack.name}: CVSS {attack.cvss_score}")
    """
    return [p for p in ATTACK_PATTERNS.values() if p.yale_category == category]


def patterns_by_cvss_severity(severity: str) -> List[AttackPattern]:
    """
    Get all attack patterns matching a CVSS severity level.

    Args:
        severity: One of "None", "Low", "Medium", "High", "Critical"

    Returns:
        List of AttackPatterns with that severity

    Example:
        >>> critical = patterns_by_cvss_severity("Critical")
        >>> for attack in critical:
        ...     print(f"{attack.name}: {attack.cvss.vector_string}")
    """
    severity = severity.title()  # Normalize case
    return [p for p in ATTACK_PATTERNS.values()
            if p.cvss and p.cvss.severity == severity]


def get_yale_patterns() -> Dict[str, List[AttackPattern]]:
    """
    Get all Yale threat model patterns grouped by category.

    Returns:
        Dict mapping category names to lists of patterns

    Example:
        >>> yale = get_yale_patterns()
        >>> print(f"Software update attacks: {len(yale['software_update'])}")
    """
    result = {}
    for category in YaleThreatCategory:
        patterns = patterns_by_yale_category(category)
        if patterns:
            result[category.value] = patterns
    return result


def get_cvss_summary() -> Dict[str, Any]:
    """
    Get summary statistics of CVSS scores across all patterns.

    Returns:
        Dict with summary statistics:
        - total_patterns: Number of patterns with CVSS scores
        - by_severity: Count per severity level
        - highest_score: Maximum score and pattern name
        - mean_score: Average CVSS score

    Example:
        >>> summary = get_cvss_summary()
        >>> print(f"Critical vulnerabilities: {summary['by_severity']['Critical']}")
    """
    cvss_patterns = [(name, p) for name, p in ATTACK_PATTERNS.items() if p.cvss]

    if not cvss_patterns:
        return {"total_patterns": 0, "by_severity": {}, "highest_score": None, "mean_score": 0.0}

    scores = [p.cvss.base_score for _, p in cvss_patterns]
    severities = [p.cvss.severity for _, p in cvss_patterns]

    # Count by severity
    severity_counts = {}
    for sev in ["None", "Low", "Medium", "High", "Critical"]:
        severity_counts[sev] = severities.count(sev)

    # Find highest
    max_idx = scores.index(max(scores))
    highest_name, highest_pattern = cvss_patterns[max_idx]

    return {
        "total_patterns": len(cvss_patterns),
        "by_severity": severity_counts,
        "highest_score": {
            "score": highest_pattern.cvss.base_score,
            "pattern": highest_name,
            "severity": highest_pattern.cvss.severity,
        },
        "mean_score": round(sum(scores) / len(scores), 1),
    }


# =============================================================================
# CVE Note
# =============================================================================
#
# Common Vulnerabilities and Exposures (CVE) is a standardized system for
# identifying publicly known cybersecurity vulnerabilities.
#
# As of 2025, NO CVEs have been formally catalogued for Brain-Computer
# Interfaces. This is because:
#
# 1. BCIs are still emerging technology (~60 implants as of 2024)
# 2. No publicly documented security incidents have occurred
# 3. Vulnerability disclosure is nascent in the BCI industry
#
# TARA uses CVSS for PROSPECTIVE risk assessment, scoring theoretical
# vulnerabilities based on the Yale Digital Ethics Center threat model.
# This allows security researchers to:
#
# - Quantify risk before incidents occur
# - Compare relative severity of different attack vectors
# - Prioritize defensive measures
# - Establish baseline security metrics for the BCI industry
#
# When CVEs are eventually assigned to BCI vulnerabilities, TARA can
# be extended to reference them via the `references` field in AttackPattern.
#
# Reference: https://cve.mitre.org/
# =============================================================================
