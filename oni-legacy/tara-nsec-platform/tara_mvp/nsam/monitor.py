"""
Neural Real-time Monitor

Real-time monitoring system for neural interfaces with
integrated anomaly detection and alerting.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum, auto
import threading
import time

from .events import EventStore, NeuralEvent, EventCategory, EventSeverity
from .rules import RuleEngine, DetectionRule, RuleAction, PREDEFINED_RULES
from .detector import AnomalyDetector, DetectionResult, DetectionMethod
from .alerts import AlertManager, Alert, AlertLevel


class MonitorState(Enum):
    """Monitor operational states."""
    STOPPED = auto()
    STARTING = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPING = auto()


@dataclass
class MonitoringSession:
    """
    Record of a monitoring session.

    Attributes:
        session_id: Unique session identifier
        start_time: When monitoring started
        end_time: When monitoring ended
        samples_processed: Total samples processed
        anomalies_detected: Anomaly count
        alerts_generated: Alert count
        metrics_summary: Summary statistics
    """
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    samples_processed: int = 0
    anomalies_detected: int = 0
    alerts_generated: int = 0
    metrics_summary: Dict[str, Dict[str, float]] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Session duration in seconds."""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    @property
    def sample_rate(self) -> float:
        """Samples per second."""
        if self.duration == 0:
            return 0.0
        return self.samples_processed / self.duration


class NeuralMonitor:
    """
    Real-time Neural Monitoring System.

    Integrates anomaly detection, rule evaluation, event logging,
    and alert generation into a unified monitoring solution.

    Example:
        >>> monitor = NeuralMonitor()
        >>> monitor.start()
        >>>
        >>> # In your processing loop:
        >>> metrics = {
        ...     "coherence": 0.75,
        ...     "spike_rate": 45.0,
        ...     "amplitude": 50.0,
        ... }
        >>> monitor.process(metrics)
        >>>
        >>> # When done:
        >>> session = monitor.stop()
        >>> print(f"Processed {session.samples_processed} samples")
    """

    def __init__(
        self,
        name: str = "NeuralMonitor",
        enable_detection: bool = True,
        enable_rules: bool = True,
        enable_alerts: bool = True,
    ):
        """
        Initialize the neural monitor.

        Args:
            name: Monitor name
            enable_detection: Enable anomaly detection
            enable_rules: Enable rule evaluation
            enable_alerts: Enable alert generation
        """
        self.name = name
        self.enable_detection = enable_detection
        self.enable_rules = enable_rules
        self.enable_alerts = enable_alerts

        # State
        self._state = MonitorState.STOPPED
        self._session_counter = 0
        self._current_session: Optional[MonitoringSession] = None

        # Components
        self.event_store = EventStore()
        self.rule_engine = RuleEngine()
        self.detector = AnomalyDetector()
        self.alert_manager = AlertManager()

        # Load default rules
        for rule in PREDEFINED_RULES.values():
            self.rule_engine.add_rule(rule)

        # Current metrics
        self._current_metrics: Dict[str, float] = {}
        self._metric_history: Dict[str, List[float]] = {}

        # Callbacks
        self._metrics_callbacks: List[Callable[[Dict[str, float]], None]] = []
        self._detection_callbacks: List[Callable[[DetectionResult], None]] = []

        # Thread safety
        self._lock = threading.Lock()

    @property
    def state(self) -> MonitorState:
        """Current monitor state."""
        return self._state

    @property
    def is_running(self) -> bool:
        """Whether monitor is actively processing."""
        return self._state == MonitorState.RUNNING

    @property
    def current_metrics(self) -> Dict[str, float]:
        """Most recent metric values."""
        return self._current_metrics.copy()

    def start(self) -> MonitoringSession:
        """
        Start a monitoring session.

        Returns:
            The new MonitoringSession
        """
        with self._lock:
            if self._state != MonitorState.STOPPED:
                raise RuntimeError(f"Monitor is {self._state.name}, cannot start")

            self._state = MonitorState.STARTING

            # Create new session
            self._session_counter += 1
            session_id = f"MON-{self._session_counter:06d}"

            self._current_session = MonitoringSession(
                session_id=session_id,
                start_time=datetime.now(),
            )

            # Log start event
            self.event_store.create_event(
                category=EventCategory.SYSTEM,
                severity=EventSeverity.INFO,
                source=self.name,
                message=f"Monitoring session {session_id} started",
            )

            self._state = MonitorState.RUNNING
            return self._current_session

    def stop(self) -> MonitoringSession:
        """
        Stop the current monitoring session.

        Returns:
            The completed MonitoringSession
        """
        with self._lock:
            if self._state not in [MonitorState.RUNNING, MonitorState.PAUSED]:
                raise RuntimeError(f"Monitor is {self._state.name}, cannot stop")

            self._state = MonitorState.STOPPING

            session = self._current_session
            session.end_time = datetime.now()

            # Calculate summary statistics
            session.metrics_summary = self._calculate_summary()

            # Log stop event
            self.event_store.create_event(
                category=EventCategory.SYSTEM,
                severity=EventSeverity.INFO,
                source=self.name,
                message=f"Monitoring session {session.session_id} ended - "
                       f"{session.samples_processed} samples processed",
                data={
                    "duration": session.duration,
                    "anomalies": session.anomalies_detected,
                    "alerts": session.alerts_generated,
                },
            )

            self._current_session = None
            self._state = MonitorState.STOPPED
            return session

    def pause(self):
        """Pause monitoring (still accepts data but skips processing)."""
        with self._lock:
            if self._state != MonitorState.RUNNING:
                return
            self._state = MonitorState.PAUSED

    def resume(self):
        """Resume monitoring."""
        with self._lock:
            if self._state != MonitorState.PAUSED:
                return
            self._state = MonitorState.RUNNING

    def process(self, metrics: Dict[str, float]) -> Optional[DetectionResult]:
        """
        Process a set of metrics.

        Args:
            metrics: Current metric values

        Returns:
            DetectionResult if anomaly detected, None otherwise
        """
        if self._state != MonitorState.RUNNING:
            return None

        with self._lock:
            self._current_metrics = metrics.copy()
            self._current_session.samples_processed += 1

            # Update metric history
            for name, value in metrics.items():
                if name not in self._metric_history:
                    self._metric_history[name] = []
                self._metric_history[name].append(value)
                # Keep last 1000
                if len(self._metric_history[name]) > 1000:
                    self._metric_history[name] = self._metric_history[name][-1000:]

            # Notify metrics callbacks
            for callback in self._metrics_callbacks:
                try:
                    callback(metrics)
                except Exception:  # nosec B110
                    pass  # Don't let callback errors affect monitoring

            result = None

            # Run anomaly detection
            if self.enable_detection:
                result = self._run_detection(metrics)

            # Run rule evaluation
            if self.enable_rules:
                self._run_rules(metrics)

            return result

    def _run_detection(self, metrics: Dict[str, float]) -> Optional[DetectionResult]:
        """Run anomaly detection on metrics."""
        result = self.detector.analyze(metrics)

        if result.detected:
            self._current_session.anomalies_detected += 1

            # Log event
            self.event_store.create_event(
                category=EventCategory.ATTACK,
                severity=self._detection_to_severity(result),
                source=self.name,
                message=f"Anomaly detected: {result.anomaly_type}",
                data={
                    "confidence": result.confidence,
                    "method": result.method.name,
                    "metrics": result.metrics,
                },
            )

            # Generate alert if enabled
            if self.enable_alerts:
                self._generate_detection_alert(result)

            # Notify callbacks
            for callback in self._detection_callbacks:
                try:
                    callback(result)
                except Exception:  # nosec B110
                    pass  # Don't let callback errors affect detection

        return result if result.detected else None

    def _run_rules(self, metrics: Dict[str, float]):
        """Run rule evaluation on metrics."""
        # Prepare context with history
        context = {}
        for name, history in self._metric_history.items():
            context[f"{name}_history"] = history

        triggered = self.rule_engine.evaluate(metrics, context)

        for rule, rule_context in triggered:
            # Log event
            event = self.event_store.create_event(
                category=EventCategory.FIREWALL,
                severity=self._rule_to_severity(rule),
                source=f"{self.name}/Rules",
                message=f"Rule triggered: {rule.name}",
                data={
                    "rule_id": rule.rule_id,
                    "context": rule_context,
                },
            )

            # Handle rule actions
            if self.enable_alerts and RuleAction.ALERT in rule.actions:
                self._generate_rule_alert(rule, rule_context, metrics)

    def _detection_to_severity(self, result: DetectionResult) -> EventSeverity:
        """Map detection confidence to event severity."""
        if result.confidence > 0.9:
            return EventSeverity.CRITICAL
        elif result.confidence > 0.7:
            return EventSeverity.ERROR
        elif result.confidence > 0.5:
            return EventSeverity.WARNING
        return EventSeverity.INFO

    def _rule_to_severity(self, rule: DetectionRule) -> EventSeverity:
        """Map rule severity boost to event severity."""
        base = EventSeverity.WARNING
        boost = rule.severity_boost

        if boost >= 2:
            return EventSeverity.CRITICAL
        elif boost >= 1:
            return EventSeverity.ERROR
        elif boost <= -1:
            return EventSeverity.INFO
        return base

    def _generate_detection_alert(self, result: DetectionResult):
        """Generate alert from detection result."""
        level = AlertLevel.INFO
        if result.confidence > 0.9:
            level = AlertLevel.CRITICAL
        elif result.confidence > 0.7:
            level = AlertLevel.HIGH
        elif result.confidence > 0.5:
            level = AlertLevel.MEDIUM
        elif result.confidence > 0.3:
            level = AlertLevel.LOW

        alert = self.alert_manager.create_alert(
            level=level,
            title=f"Anomaly: {result.anomaly_type}",
            description=f"Anomaly detected via {result.method.name} with "
                       f"{result.confidence:.1%} confidence",
            source=self.name,
            metrics=result.metrics,
            metadata={
                "detection_method": result.method.name,
                "confidence": result.confidence,
                "details": result.details,
            },
        )

        if alert:
            self._current_session.alerts_generated += 1

    def _generate_rule_alert(
        self,
        rule: DetectionRule,
        context: Dict[str, Any],
        metrics: Dict[str, float],
    ):
        """Generate alert from rule trigger."""
        level = AlertLevel.MEDIUM
        if rule.severity_boost >= 2:
            level = AlertLevel.CRITICAL
        elif rule.severity_boost >= 1:
            level = AlertLevel.HIGH
        elif rule.severity_boost <= -1:
            level = AlertLevel.LOW

        alert = self.alert_manager.create_alert(
            level=level,
            title=f"Rule: {rule.name}",
            description=rule.description,
            source=f"{self.name}/Rules",
            metrics=metrics,
            metadata={
                "rule_id": rule.rule_id,
                "rule_type": rule.rule_type.name,
                "context": context,
                "tags": rule.tags,
            },
        )

        if alert:
            self._current_session.alerts_generated += 1

    def _calculate_summary(self) -> Dict[str, Dict[str, float]]:
        """Calculate summary statistics for session."""
        import numpy as np

        summary = {}
        for name, values in self._metric_history.items():
            if not values:
                continue
            arr = np.array(values)
            summary[name] = {
                "mean": float(np.mean(arr)),
                "std": float(np.std(arr)),
                "min": float(np.min(arr)),
                "max": float(np.max(arr)),
                "samples": len(values),
            }
        return summary

    def add_rule(self, rule: DetectionRule):
        """Add a detection rule."""
        self.rule_engine.add_rule(rule)

    def configure_threshold(
        self,
        metric: str,
        low: Optional[float] = None,
        high: Optional[float] = None,
    ):
        """Configure detection threshold for a metric."""
        self.detector.configure_threshold(metric, low=low, high=high)

    def on_metrics(self, callback: Callable[[Dict[str, float]], None]):
        """Register callback for metric updates."""
        self._metrics_callbacks.append(callback)

    def on_detection(self, callback: Callable[[DetectionResult], None]):
        """Register callback for anomaly detections."""
        self._detection_callbacks.append(callback)

    def on_alert(self, callback: Callable[[Alert], None]):
        """Register callback for alerts."""
        self.alert_manager.on_alert(callback)

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard display."""
        session = self._current_session

        return {
            "monitor_name": self.name,
            "state": self._state.name,
            "session": {
                "id": session.session_id if session else None,
                "duration": session.duration if session else 0,
                "samples": session.samples_processed if session else 0,
                "anomalies": session.anomalies_detected if session else 0,
                "alerts": session.alerts_generated if session else 0,
                "sample_rate": session.sample_rate if session else 0,
            } if session else None,
            "current_metrics": self._current_metrics,
            "recent_events": [
                e.to_dict() for e in self.event_store.get_recent(20)
            ],
            "active_alerts": [
                a.to_dict() for a in self.alert_manager.get_active_alerts()[:10]
            ],
            "alert_stats": self.alert_manager.get_statistics(),
            "event_stats": self.event_store.get_statistics(),
        }

    def generate_report(self) -> str:
        """Generate monitoring status report."""
        lines = [
            "=" * 60,
            f"NEURAL MONITOR STATUS: {self.name}",
            "=" * 60,
            "",
            f"State: {self._state.name}",
        ]

        session = self._current_session
        if session:
            lines.extend([
                "",
                f"Current Session: {session.session_id}",
                f"  Duration: {session.duration:.1f}s",
                f"  Samples: {session.samples_processed}",
                f"  Rate: {session.sample_rate:.1f} samples/sec",
                f"  Anomalies: {session.anomalies_detected}",
                f"  Alerts: {session.alerts_generated}",
            ])

        lines.extend([
            "",
            "Current Metrics:",
        ])
        for name, value in self._current_metrics.items():
            lines.append(f"  {name}: {value:.4f}")

        # Alert summary
        alert_stats = self.alert_manager.get_statistics()
        lines.extend([
            "",
            f"Active Alerts: {alert_stats['active_alerts']}",
            "",
            "Alerts by Level:",
        ])
        for level, count in alert_stats['by_level'].items():
            lines.append(f"  {level}: {count}")

        # Recent events
        recent = self.event_store.get_recent(5)
        if recent:
            lines.extend([
                "",
                "Recent Events:",
            ])
            for event in recent:
                lines.append(f"  {event}")

        lines.extend([
            "",
            "=" * 60,
        ])

        return "\n".join(lines)
