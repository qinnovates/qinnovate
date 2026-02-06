"""
Detection Rules Engine

Defines detection rules for neural anomaly identification.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from enum import Enum, auto
import re


class RuleType(Enum):
    """Types of detection rules."""
    THRESHOLD = auto()      # Value crosses threshold
    PATTERN = auto()        # Pattern matching
    CORRELATION = auto()    # Multi-event correlation
    STATISTICAL = auto()    # Statistical anomaly
    BEHAVIORAL = auto()     # Behavioral deviation
    SIGNATURE = auto()      # Known attack signature


class RuleAction(Enum):
    """Actions to take when rule triggers."""
    LOG = auto()           # Log the event
    ALERT = auto()         # Generate alert
    BLOCK = auto()         # Block the signal
    QUARANTINE = auto()    # Isolate the source
    ESCALATE = auto()      # Escalate to human review


@dataclass
class DetectionRule:
    """
    A detection rule for neural anomalies.

    Rules define conditions that trigger security events,
    similar to correlation rules but specifically designed for neural signals.

    Attributes:
        rule_id: Unique rule identifier
        name: Human-readable name
        description: Detailed description
        rule_type: Type of detection rule
        conditions: Rule conditions (type-specific)
        actions: Actions when rule triggers
        severity_boost: Added to base severity
        enabled: Whether rule is active
    """
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    conditions: Dict[str, Any]
    actions: List[RuleAction] = field(default_factory=lambda: [RuleAction.ALERT])
    severity_boost: int = 0  # -2 to +2
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RuleEngine:
    """
    Engine for evaluating detection rules.

    Processes neural metrics against defined rules and
    generates events when conditions are met.

    Example:
        >>> engine = RuleEngine()
        >>> engine.add_rule(my_rule)
        >>>
        >>> metrics = {"coherence": 0.3, "spike_rate": 500}
        >>> triggered = engine.evaluate(metrics)
        >>> for rule, context in triggered:
        ...     print(f"Rule triggered: {rule.name}")
    """

    def __init__(self):
        """Initialize the rule engine."""
        self._rules: Dict[str, DetectionRule] = {}
        self._custom_evaluators: Dict[str, Callable] = {}

    def add_rule(self, rule: DetectionRule):
        """Add a detection rule."""
        self._rules[rule.rule_id] = rule

    def remove_rule(self, rule_id: str):
        """Remove a rule by ID."""
        self._rules.pop(rule_id, None)

    def get_rule(self, rule_id: str) -> Optional[DetectionRule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    def list_rules(self) -> List[DetectionRule]:
        """List all rules."""
        return list(self._rules.values())

    def register_evaluator(
        self,
        rule_type: RuleType,
        evaluator: Callable[[DetectionRule, Dict[str, Any]], Optional[Dict[str, Any]]],
    ):
        """
        Register a custom evaluator for a rule type.

        The evaluator receives (rule, metrics) and returns
        context dict if triggered, None otherwise.
        """
        self._custom_evaluators[rule_type.name] = evaluator

    def evaluate(
        self,
        metrics: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[tuple]:
        """
        Evaluate all rules against current metrics.

        Args:
            metrics: Current neural metrics
            context: Additional context (history, etc.)

        Returns:
            List of (rule, trigger_context) for triggered rules
        """
        triggered = []
        context = context or {}

        for rule in self._rules.values():
            if not rule.enabled:
                continue

            result = self._evaluate_rule(rule, metrics, context)
            if result is not None:
                triggered.append((rule, result))

        return triggered

    def _evaluate_rule(
        self,
        rule: DetectionRule,
        metrics: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Evaluate a single rule."""

        # Check for custom evaluator
        if rule.rule_type.name in self._custom_evaluators:
            return self._custom_evaluators[rule.rule_type.name](rule, metrics)

        # Built-in evaluators
        if rule.rule_type == RuleType.THRESHOLD:
            return self._evaluate_threshold(rule, metrics)
        elif rule.rule_type == RuleType.PATTERN:
            return self._evaluate_pattern(rule, metrics)
        elif rule.rule_type == RuleType.STATISTICAL:
            return self._evaluate_statistical(rule, metrics, context)
        elif rule.rule_type == RuleType.SIGNATURE:
            return self._evaluate_signature(rule, metrics)

        return None

    def _evaluate_threshold(
        self,
        rule: DetectionRule,
        metrics: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Evaluate threshold-based rule."""
        conditions = rule.conditions

        metric_name = conditions.get("metric")
        if metric_name not in metrics:
            return None

        value = metrics[metric_name]
        operator = conditions.get("operator", "lt")
        threshold = conditions.get("threshold")

        triggered = False
        if operator == "lt" and value < threshold:
            triggered = True
        elif operator == "gt" and value > threshold:
            triggered = True
        elif operator == "eq" and value == threshold:
            triggered = True
        elif operator == "le" and value <= threshold:
            triggered = True
        elif operator == "ge" and value >= threshold:
            triggered = True
        elif operator == "between":
            low, high = threshold
            triggered = low <= value <= high
        elif operator == "outside":
            low, high = threshold
            triggered = value < low or value > high

        if triggered:
            return {
                "metric": metric_name,
                "value": value,
                "threshold": threshold,
                "operator": operator,
            }
        return None

    def _evaluate_pattern(
        self,
        rule: DetectionRule,
        metrics: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Evaluate pattern-based rule."""
        conditions = rule.conditions

        # Check all required patterns
        patterns = conditions.get("patterns", [])
        matched = []

        for pattern in patterns:
            metric_name = pattern.get("metric")
            if metric_name not in metrics:
                continue

            value = str(metrics[metric_name])
            regex = pattern.get("regex", ".*")

            if re.search(regex, value):
                matched.append({
                    "metric": metric_name,
                    "value": value,
                    "pattern": regex,
                })

        # Check if enough patterns matched
        min_matches = conditions.get("min_matches", len(patterns))
        if len(matched) >= min_matches:
            return {"matched_patterns": matched}

        return None

    def _evaluate_statistical(
        self,
        rule: DetectionRule,
        metrics: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Evaluate statistical anomaly rule."""
        conditions = rule.conditions

        metric_name = conditions.get("metric")
        if metric_name not in metrics:
            return None

        value = metrics[metric_name]

        # Get historical baseline from context
        history_key = f"{metric_name}_history"
        if history_key not in context:
            return None

        history = context[history_key]
        if len(history) < 10:
            return None

        # Calculate statistics
        import numpy as np
        mean = np.mean(history)
        std = np.std(history)

        if std == 0:
            return None

        z_score = (value - mean) / std
        threshold = conditions.get("z_threshold", 3.0)

        if abs(z_score) > threshold:
            return {
                "metric": metric_name,
                "value": value,
                "mean": mean,
                "std": std,
                "z_score": z_score,
                "threshold": threshold,
            }

        return None

    def _evaluate_signature(
        self,
        rule: DetectionRule,
        metrics: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Evaluate signature-based rule (known attack patterns)."""
        conditions = rule.conditions
        signature = conditions.get("signature", {})

        # Check if all signature components match
        matched = True
        matches = {}

        for key, expected in signature.items():
            if key not in metrics:
                matched = False
                break

            actual = metrics[key]

            if isinstance(expected, dict):
                # Range check
                if "min" in expected and actual < expected["min"]:
                    matched = False
                    break
                if "max" in expected and actual > expected["max"]:
                    matched = False
                    break
            elif actual != expected:
                matched = False
                break

            matches[key] = actual

        if matched and matches:
            return {
                "signature_name": conditions.get("name", rule.name),
                "matched_values": matches,
            }

        return None


# Predefined detection rules
PREDEFINED_RULES: Dict[str, DetectionRule] = {}


def _build_rules():
    """Build predefined detection rules."""
    global PREDEFINED_RULES

    # Rule 1: Low coherence warning
    PREDEFINED_RULES["coherence_low"] = DetectionRule(
        rule_id="coherence_low",
        name="Low Coherence Warning",
        description="Triggers when signal coherence falls below safe threshold",
        rule_type=RuleType.THRESHOLD,
        conditions={
            "metric": "coherence",
            "operator": "lt",
            "threshold": 0.5,
        },
        actions=[RuleAction.ALERT],
        severity_boost=0,
        tags=["coherence", "signal_quality"],
    )

    # Rule 2: Critical coherence
    PREDEFINED_RULES["coherence_critical"] = DetectionRule(
        rule_id="coherence_critical",
        name="Critical Coherence Drop",
        description="Triggers when coherence falls to dangerous levels",
        rule_type=RuleType.THRESHOLD,
        conditions={
            "metric": "coherence",
            "operator": "lt",
            "threshold": 0.3,
        },
        actions=[RuleAction.ALERT, RuleAction.BLOCK],
        severity_boost=2,
        tags=["coherence", "critical"],
    )

    # Rule 3: Spike rate surge
    PREDEFINED_RULES["spike_surge"] = DetectionRule(
        rule_id="spike_surge",
        name="Spike Rate Surge",
        description="Detects abnormally high neural firing rates",
        rule_type=RuleType.THRESHOLD,
        conditions={
            "metric": "spike_rate",
            "operator": "gt",
            "threshold": 200.0,  # Hz
        },
        actions=[RuleAction.ALERT],
        severity_boost=1,
        tags=["spike_rate", "dos"],
    )

    # Rule 4: Phase anomaly
    PREDEFINED_RULES["phase_anomaly"] = DetectionRule(
        rule_id="phase_anomaly",
        name="Phase Coherence Anomaly",
        description="Detects unusual phase relationships in signals",
        rule_type=RuleType.STATISTICAL,
        conditions={
            "metric": "phase_coherence",
            "z_threshold": 3.0,
        },
        actions=[RuleAction.ALERT],
        severity_boost=0,
        tags=["phase", "statistical"],
    )

    # Rule 5: DoS attack signature
    PREDEFINED_RULES["dos_signature"] = DetectionRule(
        rule_id="dos_signature",
        name="DoS Attack Signature",
        description="Matches known DoS attack characteristics",
        rule_type=RuleType.SIGNATURE,
        conditions={
            "name": "Neural DoS Flood",
            "signature": {
                "spike_rate": {"min": 500},
                "signal_amplitude": {"min": 80},
                "coherence": {"max": 0.4},
            },
        },
        actions=[RuleAction.ALERT, RuleAction.BLOCK],
        severity_boost=2,
        tags=["dos", "attack", "signature"],
    )

    # Rule 6: Ransomware signature
    PREDEFINED_RULES["ransomware_signature"] = DetectionRule(
        rule_id="ransomware_signature",
        name="Neural Ransomware Signature",
        description="Matches neural ransomware attack pattern",
        rule_type=RuleType.SIGNATURE,
        conditions={
            "name": "Neural Ransomware",
            "signature": {
                "frequency_override": True,
                "target_band_suppressed": True,
                "coherence": {"max": 0.5},
            },
        },
        actions=[RuleAction.ALERT, RuleAction.BLOCK, RuleAction.ESCALATE],
        severity_boost=2,
        tags=["ransomware", "attack", "critical"],
    )

    # Rule 7: Side channel activity
    PREDEFINED_RULES["side_channel"] = DetectionRule(
        rule_id="side_channel",
        name="Side Channel Activity Detected",
        description="Detects potential side channel information leakage",
        rule_type=RuleType.PATTERN,
        conditions={
            "patterns": [
                {"metric": "timing_variance", "regex": "high|abnormal"},
                {"metric": "correlation_score", "regex": "^0\\.[89]"},
            ],
            "min_matches": 2,
        },
        actions=[RuleAction.ALERT],
        severity_boost=1,
        tags=["side_channel", "stealth"],
    )

    # Rule 8: Gateway bypass attempt
    PREDEFINED_RULES["gateway_bypass"] = DetectionRule(
        rule_id="gateway_bypass",
        name="Gateway Bypass Attempt",
        description="Detects attempts to bypass L8 neural firewall",
        rule_type=RuleType.SIGNATURE,
        conditions={
            "name": "Gateway Bypass",
            "signature": {
                "coherence_mimicry": True,
                "gradual_drift": True,
            },
        },
        actions=[RuleAction.ALERT, RuleAction.BLOCK],
        severity_boost=1,
        tags=["gateway", "bypass", "evasion"],
    )

    # Rule 9: Amplitude manipulation
    PREDEFINED_RULES["amplitude_manipulation"] = DetectionRule(
        rule_id="amplitude_manipulation",
        name="Amplitude Manipulation Detected",
        description="Detects sudden amplitude changes suggesting manipulation",
        rule_type=RuleType.THRESHOLD,
        conditions={
            "metric": "amplitude_change_rate",
            "operator": "gt",
            "threshold": 5.0,  # Multiplier per second
        },
        actions=[RuleAction.ALERT],
        severity_boost=1,
        tags=["amplitude", "manipulation"],
    )

    # Rule 10: Multi-layer attack
    PREDEFINED_RULES["multi_layer_attack"] = DetectionRule(
        rule_id="multi_layer_attack",
        name="Multi-Layer Attack Pattern",
        description="Detects coordinated attacks across multiple ONI layers",
        rule_type=RuleType.PATTERN,
        conditions={
            "patterns": [
                {"metric": "layer_8_anomaly", "regex": "true|1"},
                {"metric": "layer_9_anomaly", "regex": "true|1"},
                {"metric": "layer_10_anomaly", "regex": "true|1"},
            ],
            "min_matches": 2,
        },
        actions=[RuleAction.ALERT, RuleAction.ESCALATE],
        severity_boost=2,
        tags=["multi_layer", "coordinated", "critical"],
    )


# Build rules on module load
_build_rules()


def get_rule(rule_id: str) -> DetectionRule:
    """Get a predefined rule by ID."""
    if rule_id not in PREDEFINED_RULES:
        raise KeyError(f"Unknown rule: {rule_id}. "
                      f"Available: {list(PREDEFINED_RULES.keys())}")
    return PREDEFINED_RULES[rule_id]


def list_rules() -> List[str]:
    """List all available rule IDs."""
    return list(PREDEFINED_RULES.keys())


def rules_by_tag(tag: str) -> List[DetectionRule]:
    """Get all rules with a specific tag."""
    return [r for r in PREDEFINED_RULES.values() if tag in r.tags]


def register_kohno_rules() -> int:
    """
    Register Kohno-based neurosecurity detection rules.

    Adds rules based on Kohno et al. (2009) threat taxonomy:
    - ALTERATION (Integrity)
    - BLOCKING (Availability)
    - EAVESDROPPING (Confidentiality)

    Returns:
        Number of rules registered.

    Reference:
        Denning, T., Matsuoka, Y., & Kohno, T. (2009). Neurosecurity: Security
        and privacy for neural devices. Neurosurgical Focus, 27(1), E7.
    """
    try:
        from ..neurosecurity import create_kohno_rules, KOHNO_DETECTION_RULES

        count = 0
        for rule_id, rule in KOHNO_DETECTION_RULES.items():
            if rule_id not in PREDEFINED_RULES:
                PREDEFINED_RULES[rule_id] = rule
                count += 1

        return count
    except ImportError:
        # Neurosecurity module not available
        return 0


def get_kohno_rules() -> List[DetectionRule]:
    """
    Get all Kohno-based detection rules.

    Returns:
        List of Kohno rules (empty if neurosecurity module unavailable).
    """
    return [r for r in PREDEFINED_RULES.values() if "kohno" in r.tags]


def rules_by_cia_category(category: str) -> List[DetectionRule]:
    """
    Get rules by CIA triad category.

    Args:
        category: One of "integrity", "availability", "confidentiality"

    Returns:
        List of rules targeting that CIA property.
    """
    return [
        r for r in PREDEFINED_RULES.values()
        if r.metadata.get("cia_mapping") == category
    ]
