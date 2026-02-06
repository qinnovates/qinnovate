"""
TARA Neurosecurity Integration

Provides integration between ONI neurosecurity components and TARA's
NSAM (Neural Signal Assurance Monitoring) system.

Implements Kohno et al. (2009) threat taxonomy as detection rules
compatible with TARA's rule engine.

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

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from enum import Enum

# Import TARA's rule types
from ..nsam.rules import DetectionRule, RuleType, RuleAction


class KohnoThreatCategory(Enum):
    """
    Kohno's three fundamental BCI threat categories (2009).

    Maps to CIA triad:
    - ALTERATION -> Integrity
    - BLOCKING -> Availability
    - EAVESDROPPING -> Confidentiality
    """
    ALTERATION = "alteration"  # Integrity attacks
    BLOCKING = "blocking"      # Availability attacks
    EAVESDROPPING = "eavesdropping"  # Confidentiality attacks


# Kohno-based detection rules for TARA NSAM
KOHNO_DETECTION_RULES: Dict[str, DetectionRule] = {}


def _build_kohno_rules():
    """
    Build detection rules based on Kohno's threat taxonomy.

    Reference: Denning, T., Matsuoka, Y., & Kohno, T. (2009).
    Neurosecurity: Security and privacy for neural devices.
    """
    global KOHNO_DETECTION_RULES

    # ==========================================================================
    # ALTERATION ATTACKS (Integrity - Kohno Category 1)
    # ==========================================================================

    # Signal Injection Detection
    KOHNO_DETECTION_RULES["kohno_signal_injection"] = DetectionRule(
        rule_id="kohno_signal_injection",
        name="Signal Injection Attack",
        description="Detects unauthorized signal injection (Kohno: Alteration)",
        rule_type=RuleType.SIGNATURE,
        conditions={
            "name": "Signal Injection",
            "signature": {
                "signal_origin": "external",
                "coherence_mismatch": True,
                "timing_anomaly": True,
            },
        },
        actions=[RuleAction.ALERT, RuleAction.BLOCK],
        severity_boost=2,
        tags=["kohno", "alteration", "integrity", "injection"],
        metadata={
            "kohno_category": "alteration",
            "cia_mapping": "integrity",
            "reference": "Kohno et al. (2009)",
        },
    )

    # Command Modification Detection
    KOHNO_DETECTION_RULES["kohno_command_modification"] = DetectionRule(
        rule_id="kohno_command_modification",
        name="Command Modification Attack",
        description="Detects tampering with motor commands (Kohno: Alteration)",
        rule_type=RuleType.SIGNATURE,
        conditions={
            "name": "Command Modification",
            "signature": {
                "command_checksum_mismatch": True,
                "source_layer": {"min": 13, "max": 14},  # L13-L14 (Semantic/Identity)
            },
        },
        actions=[RuleAction.ALERT, RuleAction.BLOCK, RuleAction.ESCALATE],
        severity_boost=2,
        tags=["kohno", "alteration", "integrity", "motor", "critical"],
        metadata={
            "kohno_category": "alteration",
            "cia_mapping": "integrity",
            "affected_layers": ["L13", "L14"],
        },
    )

    # Stimulation Parameter Tampering
    KOHNO_DETECTION_RULES["kohno_stimulation_tampering"] = DetectionRule(
        rule_id="kohno_stimulation_tampering",
        name="Stimulation Parameter Tampering",
        description="Detects unsafe stimulation parameters (Kohno: Alteration)",
        rule_type=RuleType.THRESHOLD,
        conditions={
            "metric": "stimulation_amplitude",
            "operator": "gt",
            "threshold": 10.0,  # mA - dangerous threshold
        },
        actions=[RuleAction.ALERT, RuleAction.BLOCK],
        severity_boost=2,
        tags=["kohno", "alteration", "integrity", "stimulation", "safety"],
        metadata={
            "kohno_category": "alteration",
            "cia_mapping": "integrity",
            "safety_critical": True,
        },
    )

    # ==========================================================================
    # BLOCKING ATTACKS (Availability - Kohno Category 2)
    # ==========================================================================

    # Neural DoS Detection
    KOHNO_DETECTION_RULES["kohno_neural_dos"] = DetectionRule(
        rule_id="kohno_neural_dos",
        name="Neural Denial of Service",
        description="Detects signal flooding attacks (Kohno: Blocking)",
        rule_type=RuleType.SIGNATURE,
        conditions={
            "name": "Neural DoS",
            "signature": {
                "spike_rate": {"min": 500},
                "signal_entropy": {"min": 0.9},
                "coherence": {"max": 0.3},
            },
        },
        actions=[RuleAction.ALERT, RuleAction.BLOCK],
        severity_boost=2,
        tags=["kohno", "blocking", "availability", "dos", "flood"],
        metadata={
            "kohno_category": "blocking",
            "cia_mapping": "availability",
        },
    )

    # Signal Suppression Detection
    KOHNO_DETECTION_RULES["kohno_signal_suppression"] = DetectionRule(
        rule_id="kohno_signal_suppression",
        name="Signal Suppression Attack",
        description="Detects malicious signal blocking (Kohno: Blocking)",
        rule_type=RuleType.THRESHOLD,
        conditions={
            "metric": "signal_amplitude",
            "operator": "lt",
            "threshold": 0.01,  # Near-zero amplitude
        },
        actions=[RuleAction.ALERT],
        severity_boost=1,
        tags=["kohno", "blocking", "availability", "suppression"],
        metadata={
            "kohno_category": "blocking",
            "cia_mapping": "availability",
        },
    )

    # Jamming Detection
    KOHNO_DETECTION_RULES["kohno_jamming"] = DetectionRule(
        rule_id="kohno_jamming",
        name="Neural Jamming Attack",
        description="Detects RF/EM jamming of neural interface (Kohno: Blocking)",
        rule_type=RuleType.SIGNATURE,
        conditions={
            "name": "Neural Jamming",
            "signature": {
                "noise_floor": {"min": 0.8},
                "snr": {"max": 1.0},
                "packet_loss": {"min": 0.5},
            },
        },
        actions=[RuleAction.ALERT, RuleAction.ESCALATE],
        severity_boost=2,
        tags=["kohno", "blocking", "availability", "jamming", "rf"],
        metadata={
            "kohno_category": "blocking",
            "cia_mapping": "availability",
            "external_threat": True,
        },
    )

    # Motor Lockout Detection
    KOHNO_DETECTION_RULES["kohno_motor_lockout"] = DetectionRule(
        rule_id="kohno_motor_lockout",
        name="Motor Lockout Attack",
        description="Detects suppression of motor signals (Kohno: Blocking)",
        rule_type=RuleType.SIGNATURE,
        conditions={
            "name": "Motor Lockout",
            "signature": {
                "motor_intent_detected": True,
                "motor_output_blocked": True,
                "coherence": {"max": 0.4},
            },
        },
        actions=[RuleAction.ALERT, RuleAction.BLOCK, RuleAction.ESCALATE],
        severity_boost=2,
        tags=["kohno", "blocking", "availability", "motor", "critical"],
        metadata={
            "kohno_category": "blocking",
            "cia_mapping": "availability",
            "affected_layers": ["L13"],
            "safety_critical": True,
        },
    )

    # ==========================================================================
    # EAVESDROPPING ATTACKS (Confidentiality - Kohno Category 3)
    # ==========================================================================

    # Cognitive State Leakage
    KOHNO_DETECTION_RULES["kohno_cognitive_leakage"] = DetectionRule(
        rule_id="kohno_cognitive_leakage",
        name="Cognitive State Leakage",
        description="Detects unauthorized cognitive state extraction (Kohno: Eavesdropping)",
        rule_type=RuleType.SIGNATURE,
        conditions={
            "name": "Cognitive Leakage",
            "signature": {
                "erp_p300_detected": True,
                "external_query_pattern": True,
            },
        },
        actions=[RuleAction.ALERT, RuleAction.BLOCK],
        severity_boost=2,
        tags=["kohno", "eavesdropping", "confidentiality", "cognitive", "privacy"],
        metadata={
            "kohno_category": "eavesdropping",
            "cia_mapping": "confidentiality",
            "privacy_sensitive": True,
        },
    )

    # Memory Content Extraction
    KOHNO_DETECTION_RULES["kohno_memory_extraction"] = DetectionRule(
        rule_id="kohno_memory_extraction",
        name="Memory Content Extraction",
        description="Detects attempts to extract memory content (Kohno: Eavesdropping)",
        rule_type=RuleType.SIGNATURE,
        conditions={
            "name": "Memory Extraction",
            "signature": {
                "hippocampus_activation": True,
                "erp_n400_detected": True,
                "semantic_probe_pattern": True,
            },
        },
        actions=[RuleAction.ALERT, RuleAction.BLOCK, RuleAction.ESCALATE],
        severity_boost=2,
        tags=["kohno", "eavesdropping", "confidentiality", "memory", "critical"],
        metadata={
            "kohno_category": "eavesdropping",
            "cia_mapping": "confidentiality",
            "affected_layers": ["L11", "L14"],
            "privacy_critical": True,
        },
    )

    # Face Recognition Probe
    KOHNO_DETECTION_RULES["kohno_face_recognition_probe"] = DetectionRule(
        rule_id="kohno_face_recognition_probe",
        name="Face Recognition Probe",
        description="Detects covert face recognition probes via N170 (Kohno: Eavesdropping)",
        rule_type=RuleType.SIGNATURE,
        conditions={
            "name": "Face Recognition Probe",
            "signature": {
                "erp_n170_detected": True,
                "visual_stimulus_external": True,
            },
        },
        actions=[RuleAction.ALERT],
        severity_boost=1,
        tags=["kohno", "eavesdropping", "confidentiality", "face", "n170"],
        metadata={
            "kohno_category": "eavesdropping",
            "cia_mapping": "confidentiality",
            "erp_type": "N170",
            "reference": "Bonaci et al. (2015)",
        },
    )

    # Emotional State Inference
    KOHNO_DETECTION_RULES["kohno_emotional_inference"] = DetectionRule(
        rule_id="kohno_emotional_inference",
        name="Emotional State Inference",
        description="Detects unauthorized emotional state extraction (Kohno: Eavesdropping)",
        rule_type=RuleType.SIGNATURE,
        conditions={
            "name": "Emotional Inference",
            "signature": {
                "amygdala_activation": True,
                "affective_pattern_detected": True,
            },
        },
        actions=[RuleAction.ALERT],
        severity_boost=1,
        tags=["kohno", "eavesdropping", "confidentiality", "emotional", "privacy"],
        metadata={
            "kohno_category": "eavesdropping",
            "cia_mapping": "confidentiality",
            "privacy_sensitive": True,
        },
    )

    # Side Channel Attack
    KOHNO_DETECTION_RULES["kohno_side_channel"] = DetectionRule(
        rule_id="kohno_side_channel",
        name="Side Channel Information Leakage",
        description="Detects information leakage via timing/power (Kohno: Eavesdropping)",
        rule_type=RuleType.PATTERN,
        conditions={
            "patterns": [
                {"metric": "timing_variance", "regex": "high|abnormal"},
                {"metric": "power_consumption_anomaly", "regex": "true|1"},
            ],
            "min_matches": 1,
        },
        actions=[RuleAction.ALERT],
        severity_boost=1,
        tags=["kohno", "eavesdropping", "confidentiality", "side_channel"],
        metadata={
            "kohno_category": "eavesdropping",
            "cia_mapping": "confidentiality",
        },
    )


# Build rules on module load
_build_kohno_rules()


def create_kohno_rules() -> List[DetectionRule]:
    """
    Get all Kohno-based detection rules.

    Returns:
        List of DetectionRule objects implementing Kohno's threat taxonomy.
    """
    return list(KOHNO_DETECTION_RULES.values())


def get_rules_by_category(category: KohnoThreatCategory) -> List[DetectionRule]:
    """
    Get rules for a specific Kohno threat category.

    Args:
        category: KohnoThreatCategory (ALTERATION, BLOCKING, EAVESDROPPING)

    Returns:
        List of rules matching the category.
    """
    return [
        rule for rule in KOHNO_DETECTION_RULES.values()
        if rule.metadata.get("kohno_category") == category.value
    ]


@dataclass
class NeurosecurityMonitorConfig:
    """Configuration for NeurosecurityMonitor."""

    enable_kohno_rules: bool = True
    """Enable Kohno-based threat detection rules."""

    enable_privacy_filtering: bool = True
    """Enable BCI Anonymizer privacy filtering."""

    privacy_threshold: float = 0.5
    """Privacy score threshold for filtering (0-1)."""

    integrity_check_interval_ms: int = 100
    """Interval for integrity checks in milliseconds."""

    block_on_critical: bool = True
    """Automatically block signals on critical threats."""


class NeurosecurityMonitor:
    """
    Real-time neurosecurity monitor integrating Kohno threat detection
    with TARA's NSAM system.

    Provides:
    - Kohno-based threat detection (Alteration, Blocking, Eavesdropping)
    - Privacy score calculation
    - Optional BCI Anonymizer integration

    Example:
        >>> from tara_mvp.neurosecurity import NeurosecurityMonitor
        >>> monitor = NeurosecurityMonitor()
        >>>
        >>> # Process incoming signal
        >>> result = monitor.process(signal_data, metrics)
        >>> if result.threat_detected:
        ...     print(f"Threat: {result.threat_type}")
        ...     print(f"Action: {result.recommended_action}")

    Reference:
        Denning, T., Matsuoka, Y., & Kohno, T. (2009). Neurosecurity: Security
        and privacy for neural devices. Neurosurgical Focus, 27(1), E7.
    """

    def __init__(self, config: Optional[NeurosecurityMonitorConfig] = None):
        """
        Initialize the neurosecurity monitor.

        Args:
            config: Monitor configuration. Uses defaults if not provided.
        """
        self.config = config or NeurosecurityMonitorConfig()
        self._rules_loaded = False
        self._privacy_calculator = None
        self._anonymizer = None

        # Try to initialize ONI components
        self._init_oni_components()

    def _init_oni_components(self):
        """Initialize ONI Framework components if available."""
        try:
            from oni.neurosecurity import (
                PrivacyScoreCalculator,
                BCIAnonymizer,
                AnonymizerConfig,
                ERPType,
            )

            self._privacy_calculator = PrivacyScoreCalculator()

            if self.config.enable_privacy_filtering:
                # Configure anonymizer for motor commands only (default safe mode)
                anon_config = AnonymizerConfig(
                    allowed_erp_types={ERPType.LRP, ERPType.CNV}
                )
                self._anonymizer = BCIAnonymizer(anon_config)

            self._oni_available = True
        except ImportError:
            self._oni_available = False

    @property
    def oni_available(self) -> bool:
        """Check if ONI Framework components are available."""
        return getattr(self, '_oni_available', False)

    def load_kohno_rules(self, rule_engine) -> int:
        """
        Load Kohno detection rules into a TARA rule engine.

        Args:
            rule_engine: TARA RuleEngine instance

        Returns:
            Number of rules loaded.
        """
        if not self.config.enable_kohno_rules:
            return 0

        count = 0
        for rule in create_kohno_rules():
            rule_engine.add_rule(rule)
            count += 1

        self._rules_loaded = True
        return count

    def calculate_privacy_score(
        self,
        signal_data: List[float],
        detected_erps: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate privacy risk score for a signal.

        Args:
            signal_data: Raw neural signal data.
            detected_erps: List of detected ERP component names.

        Returns:
            Privacy score result dict, or None if ONI not available.
        """
        if not self._oni_available or not self._privacy_calculator:
            return None

        result = self._privacy_calculator.calculate(
            signal_data=signal_data,
            detected_erps=detected_erps,
        )

        return {
            "score": result.score,
            "interpretation": result.interpretation,
            "entropy_ratio": result.entropy_ratio,
            "sensitive_features": result.sensitive_features,
            "category_risks": result.category_risks,
        }

    def anonymize_signal(
        self,
        signal_data: List[float],
        timestamp: float = 0.0,
        channel: int = 0,
    ) -> Optional[Dict[str, Any]]:
        """
        Apply privacy filtering to a signal.

        Args:
            signal_data: Raw neural signal data.
            timestamp: Signal timestamp.
            channel: Electrode channel.

        Returns:
            Anonymized signal result dict, or None if not available.
        """
        if not self._oni_available or not self._anonymizer:
            return None

        result = self._anonymizer.anonymize(signal_data, timestamp, channel)

        return {
            "data": result.data,
            "timestamp": result.timestamp,
            "channel": result.channel,
            "privacy_score": result.metrics.privacy_score,
            "entropy_reduction": result.metrics.entropy_reduction,
            "components_removed": result.metrics.sensitive_components_removed,
            "components_allowed": result.metrics.components_allowed,
        }

    def classify_threat(
        self,
        metrics: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Classify threat based on Kohno taxonomy.

        Args:
            metrics: Signal metrics to analyze.

        Returns:
            Threat classification result.
        """
        if not self._oni_available:
            return None

        try:
            from oni.neurosecurity import KohnoThreatModel, ThreatType

            model = KohnoThreatModel()

            # Check for each threat type
            detected_threats = []

            # Check integrity (Alteration)
            if self._check_alteration_indicators(metrics):
                detected_threats.append({
                    "type": ThreatType.ALTERATION.value,
                    "category": "integrity",
                    "description": "Signal alteration detected",
                })

            # Check availability (Blocking)
            if self._check_blocking_indicators(metrics):
                detected_threats.append({
                    "type": ThreatType.BLOCKING.value,
                    "category": "availability",
                    "description": "Signal blocking detected",
                })

            # Check confidentiality (Eavesdropping)
            if self._check_eavesdropping_indicators(metrics):
                detected_threats.append({
                    "type": ThreatType.EAVESDROPPING.value,
                    "category": "confidentiality",
                    "description": "Information leakage detected",
                })

            return {
                "threats_detected": len(detected_threats) > 0,
                "threats": detected_threats,
                "metrics_analyzed": list(metrics.keys()),
            }

        except ImportError:
            return None

    def _check_alteration_indicators(self, metrics: Dict[str, Any]) -> bool:
        """Check for alteration (integrity) attack indicators."""
        indicators = [
            metrics.get("signal_origin") == "external",
            metrics.get("coherence_mismatch", False),
            metrics.get("command_checksum_mismatch", False),
            metrics.get("stimulation_amplitude", 0) > 10.0,
        ]
        return any(indicators)

    def _check_blocking_indicators(self, metrics: Dict[str, Any]) -> bool:
        """Check for blocking (availability) attack indicators."""
        indicators = [
            metrics.get("spike_rate", 0) > 500,
            metrics.get("signal_amplitude", 1) < 0.01,
            metrics.get("noise_floor", 0) > 0.8,
            metrics.get("motor_output_blocked", False),
        ]
        return any(indicators)

    def _check_eavesdropping_indicators(self, metrics: Dict[str, Any]) -> bool:
        """Check for eavesdropping (confidentiality) attack indicators."""
        indicators = [
            metrics.get("erp_p300_detected", False) and metrics.get("external_query_pattern", False),
            metrics.get("erp_n170_detected", False) and metrics.get("visual_stimulus_external", False),
            metrics.get("semantic_probe_pattern", False),
            metrics.get("timing_variance") == "high",
        ]
        return any(indicators)


# Type alias for backward compatibility
from typing import List
