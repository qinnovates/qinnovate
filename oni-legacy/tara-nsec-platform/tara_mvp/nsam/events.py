"""
Neural Event Management

Defines event types and storage for Neural Signal Assurance Monitoring.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum, auto
from collections import deque
import json


class EventSeverity(Enum):
    """Severity levels for neural events."""
    DEBUG = auto()      # Detailed debugging info
    INFO = auto()       # Normal operational events
    WARNING = auto()    # Potential issues
    ERROR = auto()      # Definite problems
    CRITICAL = auto()   # Severe security events


class EventCategory(Enum):
    """Categories of neural events."""
    COHERENCE = "coherence"           # Coherence changes
    SPIKE = "spike"                   # Spike rate events
    FREQUENCY = "frequency"           # Frequency band events
    FIREWALL = "firewall"             # Firewall decisions
    ATTACK = "attack"                 # Attack detection
    SYSTEM = "system"                 # System events
    AUTHENTICATION = "authentication" # Auth events


@dataclass
class NeuralEvent:
    """
    A neural security event.

    Represents any notable occurrence in the neural monitoring system,
    from routine status updates to critical security alerts.

    Attributes:
        event_id: Unique event identifier
        timestamp: When the event occurred
        category: Event category
        severity: Event severity level
        source: Source of the event (layer, component)
        message: Human-readable description
        data: Additional event data
        correlated_events: IDs of related events
    """
    event_id: str
    timestamp: datetime
    category: EventCategory
    severity: EventSeverity
    source: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    correlated_events: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "category": self.category.value,
            "severity": self.severity.name,
            "source": self.source,
            "message": self.message,
            "data": self.data,
            "correlated_events": self.correlated_events,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "NeuralEvent":
        """Create event from dictionary."""
        return cls(
            event_id=d["event_id"],
            timestamp=datetime.fromisoformat(d["timestamp"]),
            category=EventCategory(d["category"]),
            severity=EventSeverity[d["severity"]],
            source=d["source"],
            message=d["message"],
            data=d.get("data", {}),
            correlated_events=d.get("correlated_events", []),
        )

    def __str__(self) -> str:
        return f"[{self.severity.name}] {self.timestamp:%H:%M:%S} - {self.source}: {self.message}"


class EventStore:
    """
    Storage and retrieval for neural events.

    Provides in-memory event storage with optional file persistence,
    querying capabilities, and event correlation.

    Example:
        >>> store = EventStore(max_events=10000)
        >>> event = store.create_event(
        ...     category=EventCategory.COHERENCE,
        ...     severity=EventSeverity.WARNING,
        ...     source="L8",
        ...     message="Coherence dropped below threshold",
        ...     data={"coherence": 0.45, "threshold": 0.5}
        ... )
        >>> recent = store.get_recent(count=100)
    """

    def __init__(
        self,
        max_events: int = 10000,
        persist_file: Optional[str] = None,
    ):
        """
        Initialize the event store.

        Args:
            max_events: Maximum events to keep in memory
            persist_file: Optional file path for persistence
        """
        self.max_events = max_events
        self.persist_file = persist_file
        self._events: deque = deque(maxlen=max_events)
        self._event_counter = 0
        self._by_category: Dict[EventCategory, List[NeuralEvent]] = {
            cat: [] for cat in EventCategory
        }
        self._by_severity: Dict[EventSeverity, List[NeuralEvent]] = {
            sev: [] for sev in EventSeverity
        }

    def create_event(
        self,
        category: EventCategory,
        severity: EventSeverity,
        source: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        correlated_events: Optional[List[str]] = None,
    ) -> NeuralEvent:
        """
        Create and store a new event.

        Args:
            category: Event category
            severity: Event severity
            source: Event source identifier
            message: Human-readable message
            data: Additional event data
            correlated_events: Related event IDs

        Returns:
            The created NeuralEvent
        """
        self._event_counter += 1
        event_id = f"EVT-{self._event_counter:08d}"

        event = NeuralEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            category=category,
            severity=severity,
            source=source,
            message=message,
            data=data or {},
            correlated_events=correlated_events or [],
        )

        self._store_event(event)
        return event

    def _store_event(self, event: NeuralEvent):
        """Store an event in all indices."""
        self._events.append(event)
        self._by_category[event.category].append(event)
        self._by_severity[event.severity].append(event)

        # Trim category/severity indices if needed
        if len(self._by_category[event.category]) > self.max_events // len(EventCategory):
            self._by_category[event.category] = self._by_category[event.category][-1000:]
        if len(self._by_severity[event.severity]) > self.max_events // len(EventSeverity):
            self._by_severity[event.severity] = self._by_severity[event.severity][-1000:]

        # Persist if configured
        if self.persist_file:
            self._persist_event(event)

    def _persist_event(self, event: NeuralEvent):
        """Append event to persistence file."""
        with open(self.persist_file, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

    def get_recent(self, count: int = 100) -> List[NeuralEvent]:
        """Get most recent events."""
        return list(self._events)[-count:]

    def get_by_category(
        self,
        category: EventCategory,
        count: int = 100,
    ) -> List[NeuralEvent]:
        """Get recent events of a specific category."""
        return self._by_category[category][-count:]

    def get_by_severity(
        self,
        severity: EventSeverity,
        count: int = 100,
    ) -> List[NeuralEvent]:
        """Get recent events of a specific severity."""
        return self._by_severity[severity][-count:]

    def get_by_source(
        self,
        source: str,
        count: int = 100,
    ) -> List[NeuralEvent]:
        """Get recent events from a specific source."""
        matching = [e for e in self._events if e.source == source]
        return matching[-count:]

    def get_time_range(
        self,
        start: datetime,
        end: datetime,
    ) -> List[NeuralEvent]:
        """Get events within a time range."""
        return [
            e for e in self._events
            if start <= e.timestamp <= end
        ]

    def search(
        self,
        category: Optional[EventCategory] = None,
        severity: Optional[EventSeverity] = None,
        source: Optional[str] = None,
        message_contains: Optional[str] = None,
        count: int = 100,
    ) -> List[NeuralEvent]:
        """
        Search events with multiple criteria.

        Args:
            category: Filter by category
            severity: Filter by severity
            source: Filter by source
            message_contains: Filter by message substring
            count: Maximum results

        Returns:
            Matching events
        """
        results = list(self._events)

        if category:
            results = [e for e in results if e.category == category]
        if severity:
            results = [e for e in results if e.severity == severity]
        if source:
            results = [e for e in results if e.source == source]
        if message_contains:
            results = [e for e in results if message_contains.lower() in e.message.lower()]

        return results[-count:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get event statistics."""
        return {
            "total_events": len(self._events),
            "by_category": {
                cat.value: len(events)
                for cat, events in self._by_category.items()
            },
            "by_severity": {
                sev.name: len(events)
                for sev, events in self._by_severity.items()
            },
            "oldest_event": self._events[0].timestamp.isoformat() if self._events else None,
            "newest_event": self._events[-1].timestamp.isoformat() if self._events else None,
        }

    def clear(self):
        """Clear all events."""
        self._events.clear()
        for cat in EventCategory:
            self._by_category[cat] = []
        for sev in EventSeverity:
            self._by_severity[sev] = []

    def export_json(self, filepath: str):
        """Export all events to JSON file."""
        events_data = [e.to_dict() for e in self._events]
        with open(filepath, "w") as f:
            json.dump(events_data, f, indent=2)

    def load_json(self, filepath: str):
        """Load events from JSON file."""
        with open(filepath, "r") as f:
            events_data = json.load(f)
        for d in events_data:
            event = NeuralEvent.from_dict(d)
            self._store_event(event)
