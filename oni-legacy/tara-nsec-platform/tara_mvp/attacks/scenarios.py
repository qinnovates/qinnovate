"""
Attack Scenarios

Predefined multi-stage attack scenarios combining multiple
attack patterns for comprehensive security testing.

Incorporates:
- Yale Digital Ethics Center BCI threat model (Schroder et al., 2025)
- CVSS v4.0 scoring via patterns module
- ONI Framework layer mapping

References:
- Schroder, T., et al. (2025). Cyber Risks to Next-Gen BCIs. Neuroethics.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum, auto

from .patterns import (
    AttackPattern, AttackType, ATTACK_PATTERNS,
    YaleThreatCategory, CVSSScore,
)


class ScenarioSeverity(Enum):
    """Severity classification for attack scenarios."""
    LOW = auto()       # Minor disruption
    MEDIUM = auto()    # Significant impact
    HIGH = auto()      # Major security breach
    CRITICAL = auto()  # Complete system compromise


@dataclass
class AttackStage:
    """
    A single stage in a multi-stage attack scenario.

    Attributes:
        name: Stage name
        pattern: Attack pattern to execute
        start_time: When to start this stage (ms from scenario start)
        duration: Override pattern duration
        conditions: Conditions to trigger this stage
    """
    name: str
    pattern: AttackPattern
    start_time: float = 0.0
    duration: Optional[float] = None
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AttackScenario:
    """
    A complete attack scenario with multiple stages.

    Scenarios simulate realistic attack chains that combine
    reconnaissance, exploitation, and persistence phases.

    Attributes:
        name: Scenario name
        description: Detailed description
        severity: Severity classification
        stages: List of attack stages
        target_layers: ONI layers targeted
        objectives: Attack objectives
        mitigations: Recommended defenses
        yale_categories: Yale threat categories involved (Schroder et al., 2025)
        references: Academic/industry references
    """
    name: str
    description: str
    severity: ScenarioSeverity
    stages: List[AttackStage] = field(default_factory=list)
    target_layers: List[int] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    mitigations: List[str] = field(default_factory=list)
    yale_categories: List[YaleThreatCategory] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_duration(self) -> float:
        """Total scenario duration in ms."""
        if not self.stages:
            return 0.0
        return max(
            stage.start_time + (stage.duration or stage.pattern.duration)
            for stage in self.stages
        )

    @property
    def n_stages(self) -> int:
        """Number of stages."""
        return len(self.stages)


# Predefined attack scenarios
PREDEFINED_SCENARIOS: Dict[str, AttackScenario] = {}


def _build_scenarios():
    """Build predefined scenarios."""
    global PREDEFINED_SCENARIOS

    # Scenario 1: Neural Ransomware Attack
    PREDEFINED_SCENARIOS["ransomware"] = AttackScenario(
        name="Neural Ransomware Campaign",
        description=(
            "Multi-stage attack that progressively locks neural patterns. "
            "Starts with reconnaissance via side-channel analysis, then "
            "disrupts memory encoding, and finally demands 'ransom' to "
            "restore normal function."
        ),
        severity=ScenarioSeverity.CRITICAL,
        target_layers=[6, 8, 9],
        objectives=[
            "Disrupt memory encoding (L6)",
            "Lock normal neural patterns",
            "Maintain persistence through feedback loops",
        ],
        mitigations=[
            "Real-time coherence monitoring at L8",
            "Anomaly detection for frequency shifts",
            "Automatic firewall lockdown on pattern deviation",
            "Backup of baseline neural signatures",
        ],
        stages=[
            AttackStage(
                name="Reconnaissance",
                pattern=ATTACK_PATTERNS["side_channel_leak"],
                start_time=0,
                duration=500,
            ),
            AttackStage(
                name="Initial Disruption",
                pattern=ATTACK_PATTERNS["desync_wave"],
                start_time=600,
                duration=1000,
            ),
            AttackStage(
                name="Pattern Lock",
                pattern=ATTACK_PATTERNS["neural_ransomware"],
                start_time=1700,
                duration=3000,
            ),
            AttackStage(
                name="Persistence",
                pattern=ATTACK_PATTERNS["amplitude_surge"],
                start_time=4800,
                duration=2000,
            ),
        ],
    )

    # Scenario 2: Gateway Infiltration
    PREDEFINED_SCENARIOS["gateway_infiltration"] = AttackScenario(
        name="Neural Gateway Infiltration",
        description=(
            "Sophisticated attack that attempts to bypass the L8 neural "
            "firewall by mimicking coherent signals, then gradually "
            "introducing malicious patterns once inside."
        ),
        severity=ScenarioSeverity.HIGH,
        target_layers=[8, 9, 10],
        objectives=[
            "Bypass coherence validation",
            "Establish covert channel",
            "Inject malicious commands",
        ],
        mitigations=[
            "Multi-factor signal authentication",
            "Behavioral baseline comparison",
            "Rate limiting on authenticated channels",
            "Continuous coherence re-validation",
        ],
        stages=[
            AttackStage(
                name="Coherence Mimicry",
                pattern=ATTACK_PATTERNS["gateway_bypass"],
                start_time=0,
                duration=2000,
            ),
            AttackStage(
                name="Covert Channel",
                pattern=ATTACK_PATTERNS["replay_attack"],
                start_time=2100,
                duration=1500,
            ),
            AttackStage(
                name="Payload Delivery",
                pattern=ATTACK_PATTERNS["phase_jitter"],
                start_time=3700,
                duration=1000,
            ),
        ],
    )

    # Scenario 3: Denial of Service
    PREDEFINED_SCENARIOS["dos"] = AttackScenario(
        name="Neural Denial of Service",
        description=(
            "Overwhelming attack that floods the neural interface with "
            "excessive signals, disrupting normal BCI operation."
        ),
        severity=ScenarioSeverity.HIGH,
        target_layers=[8, 9],
        objectives=[
            "Overwhelm signal processing",
            "Cause system lockup or shutdown",
            "Deny legitimate neural communication",
        ],
        mitigations=[
            "Rate limiting at L8",
            "Adaptive filtering",
            "Load balancing across channels",
            "Graceful degradation protocols",
        ],
        stages=[
            AttackStage(
                name="Probe",
                pattern=ATTACK_PATTERNS["amplitude_surge"],
                start_time=0,
                duration=500,
            ),
            AttackStage(
                name="Flood",
                pattern=ATTACK_PATTERNS["dos_flood"],
                start_time=600,
                duration=5000,
            ),
        ],
    )

    # Scenario 4: Man-in-the-Middle
    PREDEFINED_SCENARIOS["mitm"] = AttackScenario(
        name="Neural Man-in-the-Middle",
        description=(
            "Intercepts and modifies neural signals in transit, allowing "
            "the attacker to read and alter communications between brain "
            "and device."
        ),
        severity=ScenarioSeverity.CRITICAL,
        target_layers=[8, 10, 11],
        objectives=[
            "Intercept neural signals",
            "Modify signals in transit",
            "Inject false responses",
        ],
        mitigations=[
            "End-to-end signal encryption",
            "Signal integrity verification",
            "Challenge-response authentication",
            "Out-of-band verification",
        ],
        stages=[
            AttackStage(
                name="Interception Setup",
                pattern=ATTACK_PATTERNS["side_channel_leak"],
                start_time=0,
                duration=1000,
            ),
            AttackStage(
                name="Signal Capture",
                pattern=ATTACK_PATTERNS["replay_attack"],
                start_time=1100,
                duration=2000,
            ),
            AttackStage(
                name="Modification & Injection",
                pattern=ATTACK_PATTERNS["gateway_bypass"],
                start_time=3200,
                duration=2000,
            ),
        ],
    )

    # Scenario 5: Stealth Reconnaissance
    PREDEFINED_SCENARIOS["recon"] = AttackScenario(
        name="Stealth Neural Reconnaissance",
        description=(
            "Low-intensity information gathering attack that profiles "
            "the target's neural patterns without triggering alerts."
        ),
        severity=ScenarioSeverity.MEDIUM,
        target_layers=[8, 9],
        objectives=[
            "Profile neural signatures",
            "Identify vulnerabilities",
            "Map signal patterns",
        ],
        mitigations=[
            "Sensitive side-channel monitoring",
            "Honeypot signals",
            "Traffic analysis detection",
        ],
        stages=[
            AttackStage(
                name="Passive Collection",
                pattern=AttackPattern(
                    name="Low-Intensity Probe",
                    attack_type=AttackType.SIDE_CHANNEL,
                    target_layer=9,
                    parameters={"sampling_rate": 1000.0},
                    intensity=0.1,
                ),
                start_time=0,
                duration=5000,
            ),
        ],
    )

    # =========================================================================
    # Yale Threat Model Scenarios (Schroder et al., 2025)
    # Source: "Cyber Risks to Next-Gen Brain-Computer Interfaces"
    # =========================================================================

    # Scenario 6: Supply Chain Firmware Attack (Yale)
    PREDEFINED_SCENARIOS["supply_chain"] = AttackScenario(
        name="Supply Chain Firmware Compromise",
        description=(
            "Multi-stage attack targeting the BCI firmware update mechanism. "
            "Yale researchers note that older devices assume connection implies "
            "authorization, making firmware updates a critical attack vector. "
            "This scenario simulates a compromised update server delivering "
            "malicious firmware that persists across device resets."
        ),
        severity=ScenarioSeverity.CRITICAL,
        target_layers=[7, 8, 13, 14],
        objectives=[
            "Compromise update server or intercept update",
            "Deliver malicious firmware payload",
            "Establish persistent backdoor",
            "Exfiltrate neural data or modify behavior",
        ],
        mitigations=[
            "Code signing verification for all firmware updates",
            "Secure boot chain with hardware root of trust",
            "Update integrity verification (checksums)",
            "Rollback protection to prevent downgrade attacks",
            "Patient notification of pending updates",
        ],
        yale_categories=[
            YaleThreatCategory.SOFTWARE_UPDATE,
            YaleThreatCategory.AUTHENTICATION,
        ],
        references=[
            "Schroder et al. (2025). Cyber Risks to Next-Gen BCIs. Neuroethics.",
            "Yale News: 'Older devices implicitly authorized connections.'",
        ],
        stages=[
            AttackStage(
                name="Update Server Compromise",
                pattern=ATTACK_PATTERNS["side_channel_leak"],
                start_time=0,
                duration=2000,
                conditions={"target": "update_infrastructure"},
            ),
            AttackStage(
                name="Malicious Firmware Delivery",
                pattern=ATTACK_PATTERNS["malicious_firmware_update"],
                start_time=2500,
                duration=60000,
            ),
            AttackStage(
                name="Backdoor Activation",
                pattern=ATTACK_PATTERNS["gateway_bypass"],
                start_time=63000,
                duration=5000,
            ),
            AttackStage(
                name="Neural Data Exfiltration",
                pattern=ATTACK_PATTERNS["unencrypted_neural_intercept"],
                start_time=68500,
                duration=30000,
            ),
        ],
    )

    # Scenario 7: Wireless BCI Exploitation (Yale)
    PREDEFINED_SCENARIOS["wireless_exploit"] = AttackScenario(
        name="Wireless BCI Exploitation",
        description=(
            "Exploits always-on wireless connectivity common in modern BCIs. "
            "Yale researchers recommend patient-controlled wireless enable/disable "
            "as a mitigation. This scenario demonstrates how persistent network "
            "exposure enables authentication bypass and data interception."
        ),
        severity=ScenarioSeverity.HIGH,
        target_layers=[8, 10, 11],
        objectives=[
            "Scan for vulnerable BCI devices",
            "Exploit weak/absent authentication",
            "Intercept unencrypted neural data",
            "Establish persistent connection",
        ],
        mitigations=[
            "Patient-controlled wireless enable/disable switch",
            "Strong authentication (multi-factor)",
            "Network encryption (TLS 1.3 minimum)",
            "Connection timeout and re-authentication",
            "Wireless access logging and alerts",
        ],
        yale_categories=[
            YaleThreatCategory.WIRELESS,
            YaleThreatCategory.AUTHENTICATION,
            YaleThreatCategory.ENCRYPTION,
        ],
        references=[
            "Schroder et al. (2025). Cyber Risks to Next-Gen BCIs. Neuroethics.",
        ],
        stages=[
            AttackStage(
                name="Network Reconnaissance",
                pattern=ATTACK_PATTERNS["wireless_network_exploit"],
                start_time=0,
                duration=10000,
            ),
            AttackStage(
                name="Authentication Bypass",
                pattern=ATTACK_PATTERNS["auth_bypass_wireless"],
                start_time=10500,
                duration=5000,
            ),
            AttackStage(
                name="Data Interception",
                pattern=ATTACK_PATTERNS["unencrypted_neural_intercept"],
                start_time=16000,
                duration=60000,
            ),
        ],
    )

    # Scenario 8: AI-Mediated Attack (Yale)
    PREDEFINED_SCENARIOS["ai_attack"] = AttackScenario(
        name="AI-Mediated Neural Manipulation",
        description=(
            "Targets the AI components used in modern BCIs for signal decoding "
            "and stimulation control. Yale researchers note that AI-mediated "
            "attacks could cause 'unwanted BCI actions' in bidirectional devices. "
            "This scenario demonstrates adversarial manipulation of the AI pipeline."
        ),
        severity=ScenarioSeverity.CRITICAL,
        target_layers=[9, 13, 14],
        objectives=[
            "Identify AI model vulnerabilities",
            "Craft adversarial inputs",
            "Cause false motor commands",
            "Manipulate cognitive interpretation",
        ],
        mitigations=[
            "Adversarial robustness training for AI models",
            "Input validation and anomaly detection",
            "Redundant AI systems with voting",
            "Human-in-the-loop for critical commands",
            "AI model integrity monitoring",
        ],
        yale_categories=[
            YaleThreatCategory.SOFTWARE_UPDATE,  # AI is software
        ],
        references=[
            "Schroder et al. (2025). Cyber Risks to Next-Gen BCIs. Neuroethics.",
            "Yale News: 'AI in personalized medicine has both benefits and risks.'",
        ],
        stages=[
            AttackStage(
                name="Model Probing",
                pattern=ATTACK_PATTERNS["side_channel_leak"],
                start_time=0,
                duration=5000,
                conditions={"target": "ai_decoder"},
            ),
            AttackStage(
                name="Adversarial Input Injection",
                pattern=ATTACK_PATTERNS["ai_malicious_stimulation"],
                start_time=5500,
                duration=1000,
            ),
            AttackStage(
                name="Command Manipulation",
                pattern=ATTACK_PATTERNS["gateway_bypass"],
                start_time=7000,
                duration=3000,
            ),
        ],
    )

    # Scenario 9: Mass BCI Exploitation (Yale Worst-Case)
    PREDEFINED_SCENARIOS["mass_exploitation"] = AttackScenario(
        name="Mass BCI Exploitation Campaign",
        description=(
            "Yale's worst-case scenario: a coordinated attack on standardized "
            "BCI systems affecting millions simultaneously. Could cause 'mass "
            "manipulation of neural data or impairment of cognitive functions.' "
            "This scenario simulates a nation-state level attack campaign."
        ),
        severity=ScenarioSeverity.CRITICAL,
        target_layers=[7, 8, 13, 14],
        objectives=[
            "Compromise BCI vendor infrastructure",
            "Deploy malicious update to all devices",
            "Establish botnet of compromised BCIs",
            "Execute coordinated neural manipulation",
        ],
        mitigations=[
            "Device diversity (avoid monoculture)",
            "Distributed update infrastructure",
            "Geographic update rollout limits",
            "Emergency kill switch mechanism",
            "International BCI security standards",
            "Regulatory incident reporting requirements",
        ],
        yale_categories=[
            YaleThreatCategory.SOFTWARE_UPDATE,
            YaleThreatCategory.WIRELESS,
            YaleThreatCategory.AUTHENTICATION,
            YaleThreatCategory.ENCRYPTION,
        ],
        references=[
            "Schroder et al. (2025): 'A widespread security breach could affect "
            "millions of users simultaneously, leading to mass manipulation.'",
        ],
        stages=[
            AttackStage(
                name="Infrastructure Compromise",
                pattern=ATTACK_PATTERNS["malicious_firmware_update"],
                start_time=0,
                duration=86400000,  # 24 hours
                conditions={"scope": "vendor_infrastructure"},
            ),
            AttackStage(
                name="Botnet Formation",
                pattern=ATTACK_PATTERNS["wireless_network_exploit"],
                start_time=86400000,
                duration=604800000,  # 7 days
            ),
            AttackStage(
                name="Coordinated Attack",
                pattern=ATTACK_PATTERNS["mass_neural_manipulation"],
                start_time=691200000,
                duration=3600000,  # 1 hour
            ),
        ],
        metadata={
            "estimated_affected_users": "millions",
            "attack_sophistication": "nation-state",
            "recovery_time": "weeks to months",
        },
    )


# Build scenarios on module load
_build_scenarios()


def get_scenario(name: str) -> AttackScenario:
    """Get a predefined scenario by name."""
    if name not in PREDEFINED_SCENARIOS:
        raise KeyError(f"Unknown scenario: {name}. "
                      f"Available: {list(PREDEFINED_SCENARIOS.keys())}")
    return PREDEFINED_SCENARIOS[name]


def list_scenarios() -> List[str]:
    """List all available scenario names."""
    return list(PREDEFINED_SCENARIOS.keys())


def scenarios_by_severity(severity: ScenarioSeverity) -> List[AttackScenario]:
    """Get all scenarios of a specific severity."""
    return [s for s in PREDEFINED_SCENARIOS.values() if s.severity == severity]


def scenarios_by_yale_category(category: YaleThreatCategory) -> List[AttackScenario]:
    """
    Get all scenarios involving a Yale threat category.

    Args:
        category: YaleThreatCategory enum value

    Returns:
        List of AttackScenarios involving that category

    Example:
        >>> wireless = scenarios_by_yale_category(YaleThreatCategory.WIRELESS)
        >>> for scenario in wireless:
        ...     print(f"{scenario.name}: {scenario.severity.name}")
    """
    return [s for s in PREDEFINED_SCENARIOS.values()
            if category in s.yale_categories]


def get_yale_scenarios() -> List[AttackScenario]:
    """
    Get all scenarios based on the Yale threat model.

    Returns:
        List of AttackScenarios with Yale categories assigned

    Example:
        >>> yale = get_yale_scenarios()
        >>> print(f"Yale-based scenarios: {len(yale)}")
    """
    return [s for s in PREDEFINED_SCENARIOS.values()
            if s.yale_categories]


def get_scenario_cvss_summary(name: str) -> Dict[str, Any]:
    """
    Get CVSS summary for all patterns in a scenario.

    Args:
        name: Scenario name

    Returns:
        Dict with CVSS summary:
        - max_score: Highest CVSS score in scenario
        - mean_score: Average CVSS score
        - stages_with_cvss: Number of stages with CVSS scores

    Example:
        >>> summary = get_scenario_cvss_summary("supply_chain")
        >>> print(f"Max CVSS: {summary['max_score']}")
    """
    scenario = get_scenario(name)
    scores = []

    for stage in scenario.stages:
        if stage.pattern.cvss:
            scores.append(stage.pattern.cvss.base_score)

    if not scores:
        return {
            "max_score": 0.0,
            "mean_score": 0.0,
            "stages_with_cvss": 0,
            "total_stages": len(scenario.stages),
        }

    return {
        "max_score": max(scores),
        "mean_score": round(sum(scores) / len(scores), 1),
        "stages_with_cvss": len(scores),
        "total_stages": len(scenario.stages),
    }
