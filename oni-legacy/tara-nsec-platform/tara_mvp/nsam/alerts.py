"""
Alert Management System

Handles alert generation, routing, and management for Neural Signal Assurance Monitoring.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum, auto
from collections import defaultdict
import json


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = 1          # Informational
    LOW = 2           # Low priority
    MEDIUM = 3        # Medium priority
    HIGH = 4          # High priority
    CRITICAL = 5      # Critical - immediate action needed


class AlertStatus(Enum):
    """Alert lifecycle status."""
    NEW = auto()           # Just created
    ACKNOWLEDGED = auto()  # Seen by operator
    INVESTIGATING = auto() # Under investigation
    RESOLVED = auto()      # Issue resolved
    FALSE_POSITIVE = auto() # Marked as false positive
    ESCALATED = auto()     # Escalated to higher tier


@dataclass
class Alert:
    """
    A neural security alert.

    Represents a significant security event requiring attention,
    with full lifecycle tracking and correlation capabilities.

    Attributes:
        alert_id: Unique alert identifier
        timestamp: When alert was generated
        level: Alert severity level
        status: Current alert status
        title: Brief alert title
        description: Detailed description
        source: Alert source (layer, component)
        metrics: Relevant metrics at time of alert
        correlated_alerts: Related alert IDs
        actions_taken: Actions performed on this alert
    """
    alert_id: str
    timestamp: datetime
    level: AlertLevel
    status: AlertStatus
    title: str
    description: str
    source: str
    metrics: Dict[str, float] = field(default_factory=dict)
    correlated_alerts: List[str] = field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    @property
    def age(self) -> timedelta:
        """Time since alert creation."""
        return datetime.now() - self.timestamp

    @property
    def is_active(self) -> bool:
        """Whether alert is still active (not resolved)."""
        return self.status not in [
            AlertStatus.RESOLVED,
            AlertStatus.FALSE_POSITIVE,
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.name,
            "status": self.status.name,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "metrics": self.metrics,
            "correlated_alerts": self.correlated_alerts,
            "actions_taken": self.actions_taken,
            "metadata": self.metadata,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }

    def __str__(self) -> str:
        return f"[{self.level.name}] {self.alert_id}: {self.title} ({self.status.name})"


class AlertManager:
    """
    Manages alerts for Neural Signal Assurance Monitoring.

    Handles alert creation, lifecycle management, correlation,
    and notification routing.

    Example:
        >>> manager = AlertManager()
        >>> manager.on_alert(lambda a: print(f"New alert: {a.title}"))
        >>>
        >>> alert = manager.create_alert(
        ...     level=AlertLevel.HIGH,
        ...     title="Coherence Drop Detected",
        ...     description="Coherence fell below 0.3 threshold",
        ...     source="L8",
        ...     metrics={"coherence": 0.25}
        ... )
        >>>
        >>> manager.acknowledge(alert.alert_id, "operator1")
    """

    def __init__(
        self,
        max_alerts: int = 10000,
        dedup_window: float = 60.0,  # seconds
    ):
        """
        Initialize the alert manager.

        Args:
            max_alerts: Maximum alerts to retain
            dedup_window: Window for deduplicating similar alerts
        """
        self.max_alerts = max_alerts
        self.dedup_window = dedup_window

        self._alerts: Dict[str, Alert] = {}
        self._alert_counter = 0

        # Callbacks
        self._alert_callbacks: List[Callable[[Alert], None]] = []
        self._escalation_callbacks: List[Callable[[Alert], None]] = []

        # Deduplication tracking
        self._recent_signatures: Dict[str, datetime] = {}

        # Statistics
        self._stats = defaultdict(int)

        # Alert rules (for suppression, auto-escalation, etc.)
        self._suppression_rules: List[Callable[[Alert], bool]] = []
        self._auto_escalation_rules: List[Callable[[Alert], bool]] = []

    def create_alert(
        self,
        level: AlertLevel,
        title: str,
        description: str,
        source: str,
        metrics: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        deduplicate: bool = True,
    ) -> Optional[Alert]:
        """
        Create a new alert.

        Args:
            level: Alert severity level
            title: Brief title
            description: Detailed description
            source: Alert source
            metrics: Relevant metrics
            metadata: Additional metadata
            deduplicate: Whether to check for duplicates

        Returns:
            Created Alert, or None if deduplicated
        """
        # Check deduplication
        if deduplicate:
            signature = f"{level.name}:{title}:{source}"
            if self._is_duplicate(signature):
                self._stats["deduplicated"] += 1
                return None

        # Create alert
        self._alert_counter += 1
        alert_id = f"ALT-{self._alert_counter:08d}"

        alert = Alert(
            alert_id=alert_id,
            timestamp=datetime.now(),
            level=level,
            status=AlertStatus.NEW,
            title=title,
            description=description,
            source=source,
            metrics=metrics or {},
            metadata=metadata or {},
        )

        # Check suppression rules
        for rule in self._suppression_rules:
            if rule(alert):
                self._stats["suppressed"] += 1
                return None

        # Store alert
        self._alerts[alert_id] = alert
        self._stats[level.name] += 1
        self._stats["total"] += 1

        # Trim if needed
        self._trim_alerts()

        # Check auto-escalation
        for rule in self._auto_escalation_rules:
            if rule(alert):
                self.escalate(alert_id, "Auto-escalation rule triggered")
                break

        # Notify callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception:  # nosec B110
                pass  # Don't let callback errors stop processing

        return alert

    def _is_duplicate(self, signature: str) -> bool:
        """Check if alert is duplicate within dedup window."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.dedup_window)

        # Clean old signatures
        self._recent_signatures = {
            sig: ts for sig, ts in self._recent_signatures.items()
            if ts > cutoff
        }

        if signature in self._recent_signatures:
            return True

        self._recent_signatures[signature] = now
        return False

    def _trim_alerts(self):
        """Remove oldest alerts if over limit."""
        if len(self._alerts) <= self.max_alerts:
            return

        # Sort by timestamp, keep newest
        sorted_alerts = sorted(
            self._alerts.values(),
            key=lambda a: a.timestamp,
            reverse=True,
        )

        # Keep only max_alerts
        self._alerts = {
            a.alert_id: a for a in sorted_alerts[:self.max_alerts]
        }

    def acknowledge(
        self,
        alert_id: str,
        acknowledged_by: str,
        notes: Optional[str] = None,
    ) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: Alert to acknowledge
            acknowledged_by: Who acknowledged
            notes: Optional notes

        Returns:
            True if successful
        """
        alert = self._alerts.get(alert_id)
        if not alert:
            return False

        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.now()

        if notes:
            alert.actions_taken.append({
                "action": "acknowledge",
                "by": acknowledged_by,
                "at": datetime.now().isoformat(),
                "notes": notes,
            })

        self._stats["acknowledged"] += 1
        return True

    def resolve(
        self,
        alert_id: str,
        resolved_by: str,
        resolution: str,
        false_positive: bool = False,
    ) -> bool:
        """
        Resolve an alert.

        Args:
            alert_id: Alert to resolve
            resolved_by: Who resolved
            resolution: Resolution description
            false_positive: Whether this was a false positive

        Returns:
            True if successful
        """
        alert = self._alerts.get(alert_id)
        if not alert:
            return False

        alert.status = AlertStatus.FALSE_POSITIVE if false_positive else AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        alert.actions_taken.append({
            "action": "resolve",
            "by": resolved_by,
            "at": datetime.now().isoformat(),
            "resolution": resolution,
            "false_positive": false_positive,
        })

        self._stats["resolved"] += 1
        if false_positive:
            self._stats["false_positives"] += 1

        return True

    def escalate(
        self,
        alert_id: str,
        reason: str,
        escalated_by: Optional[str] = None,
    ) -> bool:
        """
        Escalate an alert.

        Args:
            alert_id: Alert to escalate
            reason: Escalation reason
            escalated_by: Who escalated (None for auto)

        Returns:
            True if successful
        """
        alert = self._alerts.get(alert_id)
        if not alert:
            return False

        alert.status = AlertStatus.ESCALATED
        alert.actions_taken.append({
            "action": "escalate",
            "by": escalated_by or "system",
            "at": datetime.now().isoformat(),
            "reason": reason,
        })

        # Notify escalation callbacks
        for callback in self._escalation_callbacks:
            try:
                callback(alert)
            except Exception:  # nosec B110
                pass  # Don't let callback errors affect escalation

        self._stats["escalated"] += 1
        return True

    def correlate(self, alert_id: str, related_alert_id: str) -> bool:
        """Link two related alerts."""
        alert = self._alerts.get(alert_id)
        related = self._alerts.get(related_alert_id)

        if not alert or not related:
            return False

        if related_alert_id not in alert.correlated_alerts:
            alert.correlated_alerts.append(related_alert_id)
        if alert_id not in related.correlated_alerts:
            related.correlated_alerts.append(alert_id)

        return True

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get an alert by ID."""
        return self._alerts.get(alert_id)

    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts."""
        return [a for a in self._alerts.values() if a.is_active]

    def get_alerts_by_level(self, level: AlertLevel) -> List[Alert]:
        """Get alerts of a specific level."""
        return [a for a in self._alerts.values() if a.level == level]

    def get_alerts_by_source(self, source: str) -> List[Alert]:
        """Get alerts from a specific source."""
        return [a for a in self._alerts.values() if a.source == source]

    def get_recent_alerts(self, count: int = 100) -> List[Alert]:
        """Get most recent alerts."""
        sorted_alerts = sorted(
            self._alerts.values(),
            key=lambda a: a.timestamp,
            reverse=True,
        )
        return sorted_alerts[:count]

    def get_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        active = len([a for a in self._alerts.values() if a.is_active])
        by_level = defaultdict(int)
        by_status = defaultdict(int)

        for alert in self._alerts.values():
            by_level[alert.level.name] += 1
            by_status[alert.status.name] += 1

        return {
            "total_alerts": len(self._alerts),
            "active_alerts": active,
            "by_level": dict(by_level),
            "by_status": dict(by_status),
            "cumulative": dict(self._stats),
        }

    def on_alert(self, callback: Callable[[Alert], None]):
        """Register callback for new alerts."""
        self._alert_callbacks.append(callback)

    def on_escalation(self, callback: Callable[[Alert], None]):
        """Register callback for escalations."""
        self._escalation_callbacks.append(callback)

    def add_suppression_rule(self, rule: Callable[[Alert], bool]):
        """Add a suppression rule (return True to suppress)."""
        self._suppression_rules.append(rule)

    def add_auto_escalation_rule(self, rule: Callable[[Alert], bool]):
        """Add auto-escalation rule (return True to escalate)."""
        self._auto_escalation_rules.append(rule)

    def export_alerts(self, filepath: str, active_only: bool = False):
        """Export alerts to JSON file."""
        alerts = self.get_active_alerts() if active_only else list(self._alerts.values())
        data = {
            "exported_at": datetime.now().isoformat(),
            "alert_count": len(alerts),
            "alerts": [a.to_dict() for a in alerts],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def generate_summary(self) -> str:
        """Generate text summary of current alert status."""
        stats = self.get_statistics()
        active = self.get_active_alerts()

        lines = [
            "=" * 50,
            "NEURAL SIGNAL ASSURANCE ALERT SUMMARY",
            "=" * 50,
            "",
            f"Total Alerts: {stats['total_alerts']}",
            f"Active Alerts: {stats['active_alerts']}",
            "",
            "By Level:",
        ]

        for level in AlertLevel:
            count = stats['by_level'].get(level.name, 0)
            lines.append(f"  {level.name}: {count}")

        lines.extend([
            "",
            "By Status:",
        ])

        for status in AlertStatus:
            count = stats['by_status'].get(status.name, 0)
            lines.append(f"  {status.name}: {count}")

        if active:
            lines.extend([
                "",
                "Active Alerts (most recent):",
                "-" * 40,
            ])
            for alert in sorted(active, key=lambda a: a.timestamp, reverse=True)[:10]:
                lines.append(f"  [{alert.level.name}] {alert.title}")
                lines.append(f"    Source: {alert.source} | Age: {alert.age}")

        lines.extend([
            "",
            "=" * 50,
        ])

        return "\n".join(lines)
