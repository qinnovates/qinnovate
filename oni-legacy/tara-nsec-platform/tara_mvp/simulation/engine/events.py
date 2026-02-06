"""
Event-Driven Simulation Support

Implements an event queue for hybrid time-stepping and event-driven
simulation. Events can include:
- Spike events
- External input events
- Recording triggers
- Custom user events
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable, Union
from enum import Enum
import heapq


class EventType(Enum):
    """Types of simulation events."""
    SPIKE = "spike"                   # Neuron spike
    INPUT = "input"                   # External input
    STIMULUS_ON = "stimulus_on"       # Stimulus onset
    STIMULUS_OFF = "stimulus_off"     # Stimulus offset
    RECORD = "record"                 # Recording trigger
    CHECKPOINT = "checkpoint"         # Simulation checkpoint
    CUSTOM = "custom"                 # User-defined event


@dataclass(order=True)
class Event:
    """
    A simulation event.

    Events are ordered by time for priority queue operations.
    """
    time: float
    event_type: EventType = field(compare=False)
    target_id: Optional[str] = field(default=None, compare=False)
    data: Dict[str, Any] = field(default_factory=dict, compare=False)
    callback: Optional[Callable] = field(default=None, compare=False)

    def __post_init__(self):
        # Ensure data is always a dict
        if self.data is None:
            self.data = {}

    def execute(self, engine: "SimulationEngine" = None):
        """Execute event callback if present."""
        if self.callback:
            self.callback(self, engine)


class EventQueue:
    """
    Priority queue for simulation events.

    Maintains events sorted by time for efficient retrieval
    of the next event to process.

    Usage:
        >>> queue = EventQueue()
        >>> queue.push(Event(10.0, EventType.INPUT, data={"current": 5.0}))
        >>> queue.push(Event(5.0, EventType.SPIKE, target_id="neuron_1"))
        >>> event = queue.pop()  # Returns the 5.0 spike event
    """

    def __init__(self):
        """Initialize empty event queue."""
        self._heap: List[Event] = []
        self._event_count = 0

    def push(self, event: Event):
        """
        Add event to queue.

        Args:
            event: Event to add
        """
        heapq.heappush(self._heap, event)
        self._event_count += 1

    def pop(self) -> Optional[Event]:
        """
        Remove and return earliest event.

        Returns:
            Next event or None if queue is empty
        """
        if self._heap:
            return heapq.heappop(self._heap)
        return None

    def peek(self) -> Optional[Event]:
        """
        Return earliest event without removing.

        Returns:
            Next event or None if queue is empty
        """
        if self._heap:
            return self._heap[0]
        return None

    def pop_until(self, t: float) -> List[Event]:
        """
        Pop all events up to and including time t.

        Args:
            t: Time threshold

        Returns:
            List of events with time <= t
        """
        events = []
        while self._heap and self._heap[0].time <= t:
            events.append(heapq.heappop(self._heap))
        return events

    def clear(self):
        """Clear all events."""
        self._heap = []

    def __len__(self) -> int:
        """Number of events in queue."""
        return len(self._heap)

    def __bool__(self) -> bool:
        """True if queue has events."""
        return len(self._heap) > 0


class StimulusProtocol:
    """
    Defines a stimulus pattern over time.

    Generates events for stimulus onset/offset and manages
    the stimulus waveform.
    """

    def __init__(
        self,
        target_ids: Union[str, List[str]],
        onset: float = 0.0,
        duration: float = 100.0,
        amplitude: float = 1.0,
        frequency: float = 0.0,      # For oscillating stimuli
        noise_std: float = 0.0,      # Noise level
        pattern: str = "constant"    # constant, pulse, ramp, sine
    ):
        """
        Initialize stimulus protocol.

        Args:
            target_ids: Neuron(s) to stimulate
            onset: Stimulus onset time (ms)
            duration: Stimulus duration (ms)
            amplitude: Peak amplitude (nA)
            frequency: Oscillation frequency (Hz) for sine pattern
            noise_std: Standard deviation of noise
            pattern: Stimulus pattern type
        """
        if isinstance(target_ids, str):
            target_ids = [target_ids]

        self.target_ids = target_ids
        self.onset = onset
        self.duration = duration
        self.amplitude = amplitude
        self.frequency = frequency
        self.noise_std = noise_std
        self.pattern = pattern

    def get_current(self, t: float) -> float:
        """
        Get stimulus current at time t.

        Args:
            t: Current time (ms)

        Returns:
            Current value (nA)
        """
        import numpy as np

        # Check if within stimulus window
        if t < self.onset or t > self.onset + self.duration:
            return 0.0

        t_relative = t - self.onset

        if self.pattern == "constant":
            current = self.amplitude

        elif self.pattern == "pulse":
            # 50% duty cycle pulse
            period = 1000 / max(self.frequency, 1e-6)  # ms
            current = self.amplitude if (t_relative % period) < (period / 2) else 0.0

        elif self.pattern == "ramp":
            # Linear ramp from 0 to amplitude
            current = self.amplitude * (t_relative / self.duration)

        elif self.pattern == "sine":
            # Sinusoidal oscillation
            current = self.amplitude * np.sin(2 * np.pi * self.frequency * t_relative / 1000)

        else:
            current = self.amplitude

        # Add noise
        if self.noise_std > 0:
            current += np.random.normal(0, self.noise_std)

        return current

    def generate_events(self, queue: EventQueue):
        """
        Generate events for this protocol.

        Args:
            queue: Event queue to add events to
        """
        # Onset event
        onset_event = Event(
            time=self.onset,
            event_type=EventType.STIMULUS_ON,
            data={
                "target_ids": self.target_ids,
                "amplitude": self.amplitude,
                "pattern": self.pattern,
            }
        )
        queue.push(onset_event)

        # Offset event
        offset_event = Event(
            time=self.onset + self.duration,
            event_type=EventType.STIMULUS_OFF,
            data={
                "target_ids": self.target_ids,
            }
        )
        queue.push(offset_event)


class PoissonInputGenerator:
    """
    Generates Poisson-distributed spike inputs.

    Useful for simulating background synaptic input
    or sensory input with variable rate.
    """

    def __init__(
        self,
        target_ids: Union[str, List[str]],
        rate: float = 10.0,          # Spikes per second per target
        weight: float = 0.5,         # Input weight
        start_time: float = 0.0,
        end_time: float = 1000.0
    ):
        """
        Initialize Poisson generator.

        Args:
            target_ids: Neuron(s) to receive input
            rate: Firing rate (Hz)
            weight: Input weight (nA equivalent)
            start_time: When to start generating (ms)
            end_time: When to stop generating (ms)
        """
        if isinstance(target_ids, str):
            target_ids = [target_ids]

        self.target_ids = target_ids
        self.rate = rate
        self.weight = weight
        self.start_time = start_time
        self.end_time = end_time

    def generate_events(self, queue: EventQueue):
        """
        Generate Poisson input events.

        Args:
            queue: Event queue to add events to
        """
        import numpy as np

        for target_id in self.target_ids:
            t = self.start_time

            # Generate spike times using Poisson process
            while t < self.end_time:
                # Inter-spike interval from exponential distribution
                isi = np.random.exponential(1000 / max(self.rate, 1e-6))
                t += isi

                if t < self.end_time:
                    event = Event(
                        time=t,
                        event_type=EventType.INPUT,
                        target_id=target_id,
                        data={"weight": self.weight}
                    )
                    queue.push(event)
