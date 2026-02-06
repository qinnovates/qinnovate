"""
TARA Neural Signal Assurance Monitoring (NSAM) Module

Neural Signal Assurance Monitoring for neural interfaces:
- Real-time neural activity monitoring
- Anomaly detection using coherence metrics
- Alert generation and management
- Event logging and correlation
"""

from .events import NeuralEvent, EventSeverity, EventStore
from .rules import DetectionRule, RuleEngine, PREDEFINED_RULES
from .detector import AnomalyDetector, DetectionResult
from .alerts import Alert, AlertManager, AlertLevel
from .monitor import NeuralMonitor, MonitoringSession

__all__ = [
    # Events
    "NeuralEvent",
    "EventSeverity",
    "EventStore",
    # Rules
    "DetectionRule",
    "RuleEngine",
    "PREDEFINED_RULES",
    # Detection
    "AnomalyDetector",
    "DetectionResult",
    # Alerts
    "Alert",
    "AlertManager",
    "AlertLevel",
    # Monitoring
    "NeuralMonitor",
    "MonitoringSession",
]
