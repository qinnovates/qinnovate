"""
Attack Simulator

Main attack simulation engine that executes attack patterns
and scenarios against neural networks.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import numpy as np

from .patterns import AttackPattern, AttackType
from .generator import AttackGenerator, AttackSignal
from .scenarios import AttackScenario, AttackStage


@dataclass
class AttackEvent:
    """Record of an attack event during simulation."""
    timestamp: float          # Simulation time (ms)
    stage_name: str           # Name of attack stage
    pattern_name: str         # Name of attack pattern
    attack_type: AttackType   # Type of attack
    target_layer: int         # ONI layer targeted
    intensity: float          # Attack intensity
    detected: bool = False    # Whether attack was detected
    blocked: bool = False     # Whether attack was blocked
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationResult:
    """Results from an attack simulation."""
    scenario_name: str
    duration: float           # Total simulation time (ms)
    events: List[AttackEvent] = field(default_factory=list)
    signals: Dict[str, AttackSignal] = field(default_factory=dict)

    # Statistics
    total_attacks: int = 0
    detected_count: int = 0
    blocked_count: int = 0

    # Network impact metrics
    coherence_impact: float = 0.0    # Change in coherence
    spike_rate_impact: float = 0.0   # Change in firing rate

    @property
    def detection_rate(self) -> float:
        """Fraction of attacks detected."""
        return self.detected_count / max(self.total_attacks, 1)

    @property
    def block_rate(self) -> float:
        """Fraction of attacks blocked."""
        return self.blocked_count / max(self.total_attacks, 1)


class AttackSimulator:
    """
    Neural Attack Simulator.

    Executes attack patterns and scenarios against neural networks,
    measuring effectiveness and detection rates.

    Example:
        >>> from tara_mvp.attacks import AttackSimulator, get_scenario
        >>> from tara_mvp.simulation import LayeredNetwork

        >>> # Create network and simulator
        >>> network = LayeredNetwork.create_oni_model()
        >>> simulator = AttackSimulator()

        >>> # Run ransomware scenario
        >>> scenario = get_scenario("ransomware")
        >>> result = simulator.run_scenario(scenario, network)

        >>> print(f"Detection rate: {result.detection_rate:.1%}")
    """

    def __init__(
        self,
        dt: float = 0.1,
        seed: Optional[int] = None,
    ):
        """
        Initialize the attack simulator.

        Args:
            dt: Time step (ms)
            seed: Random seed for reproducibility
        """
        self.dt = dt
        self.generator = AttackGenerator(dt=dt, seed=seed)

        # Callbacks for detection simulation
        self._detection_callbacks: List[Callable] = []
        self._event_callbacks: List[Callable] = []

    def run_pattern(
        self,
        pattern: AttackPattern,
        network=None,
        duration: Optional[float] = None,
        inject: bool = True,
    ) -> SimulationResult:
        """
        Run a single attack pattern.

        Args:
            pattern: Attack pattern to execute
            network: Optional network to inject attacks into
            duration: Override pattern duration
            inject: Whether to inject attacks into network

        Returns:
            SimulationResult with attack events and signals
        """
        dur = duration or pattern.duration

        # Generate attack signal
        signal = self.generator.generate(pattern, dur)

        # Create attack event
        event = AttackEvent(
            timestamp=0.0,
            stage_name="Single Attack",
            pattern_name=pattern.name,
            attack_type=pattern.attack_type,
            target_layer=pattern.target_layer,
            intensity=pattern.intensity,
        )

        # Simulate detection
        event.detected, event.blocked = self._simulate_detection(
            pattern, signal, network
        )

        # Inject into network if requested
        if inject and network:
            self._inject_signal(signal, network, pattern)

        # Notify callbacks
        for callback in self._event_callbacks:
            callback(event)

        result = SimulationResult(
            scenario_name=pattern.name,
            duration=dur,
            events=[event],
            signals={"attack": signal},
            total_attacks=1,
            detected_count=1 if event.detected else 0,
            blocked_count=1 if event.blocked else 0,
        )

        return result

    def run_scenario(
        self,
        scenario: AttackScenario,
        network=None,
        inject: bool = True,
    ) -> SimulationResult:
        """
        Run a complete attack scenario.

        Args:
            scenario: Attack scenario to execute
            network: Optional network to inject attacks into
            inject: Whether to inject attacks into network

        Returns:
            SimulationResult with all events and signals
        """
        events = []
        signals = {}
        detected = 0
        blocked = 0

        for i, stage in enumerate(scenario.stages):
            # Generate signal for this stage
            dur = stage.duration or stage.pattern.duration
            signal = self.generator.generate(stage.pattern, dur)
            signals[f"stage_{i}_{stage.name}"] = signal

            # Create event
            event = AttackEvent(
                timestamp=stage.start_time,
                stage_name=stage.name,
                pattern_name=stage.pattern.name,
                attack_type=stage.pattern.attack_type,
                target_layer=stage.pattern.target_layer,
                intensity=stage.pattern.intensity,
            )

            # Simulate detection
            event.detected, event.blocked = self._simulate_detection(
                stage.pattern, signal, network
            )

            if event.detected:
                detected += 1
            if event.blocked:
                blocked += 1

            events.append(event)

            # Notify callbacks
            for callback in self._event_callbacks:
                callback(event)

            # Inject if requested and not blocked
            if inject and network and not event.blocked:
                self._inject_signal(signal, network, stage.pattern)

        result = SimulationResult(
            scenario_name=scenario.name,
            duration=scenario.total_duration,
            events=events,
            signals=signals,
            total_attacks=len(events),
            detected_count=detected,
            blocked_count=blocked,
        )

        return result

    def _simulate_detection(
        self,
        pattern: AttackPattern,
        signal: AttackSignal,
        network=None,
    ) -> tuple:
        """
        Simulate attack detection.

        Returns:
            Tuple of (detected, blocked)
        """
        # Base detection probability based on intensity
        # Higher intensity = easier to detect
        base_detection = pattern.intensity * 0.7

        # Adjust based on attack type
        type_factor = {
            AttackType.DOS_FLOODING: 0.95,      # Very obvious
            AttackType.AMPLITUDE_MANIPULATION: 0.8,
            AttackType.PHASE_DISRUPTION: 0.6,
            AttackType.DESYNCHRONIZATION: 0.5,
            AttackType.SIGNAL_INJECTION: 0.4,
            AttackType.SIGNAL_REPLAY: 0.3,
            AttackType.SIDE_CHANNEL: 0.2,       # Stealthy
            AttackType.LAYER_8_GATEWAY: 0.3,    # Designed to evade
        }.get(pattern.attack_type, 0.5)

        detection_prob = min(base_detection + type_factor * 0.3, 0.99)

        # Run custom detection callbacks
        for callback in self._detection_callbacks:
            custom_detection = callback(pattern, signal, network)
            if custom_detection is not None:
                detection_prob = max(detection_prob, custom_detection)

        # Simulate detection
        detected = np.random.random() < detection_prob

        # If detected, simulate blocking (80% of detected attacks blocked)
        blocked = detected and (np.random.random() < 0.8)

        return detected, blocked

    def _inject_signal(
        self,
        signal: AttackSignal,
        network,
        pattern: AttackPattern,
    ):
        """Inject attack signal into network."""
        # Get target neurons based on attack layer
        target_layer = pattern.target_layer - 1  # Convert to 0-indexed

        if hasattr(network, 'get_layer_neurons'):
            # LayeredNetwork
            target_neurons = network.get_layer_neurons(target_layer)
        elif hasattr(network, 'excitatory_neurons'):
            # RecurrentNetwork - target excitatory neurons
            target_neurons = network.excitatory_neurons[:10]
        else:
            # Generic network - target random subset
            all_neurons = list(network.neurons.values())
            n_targets = min(10, len(all_neurons))
            target_neurons = all_neurons[:n_targets]

        # Apply attack signal as input current
        for neuron in target_neurons:
            if hasattr(neuron, 'receive_input'):
                # Use mean of attack signal as input
                attack_current = np.mean(np.abs(signal.amplitudes)) * 0.01
                neuron.receive_input(attack_current)

    def register_detection_callback(
        self,
        callback: Callable[[AttackPattern, AttackSignal, Any], Optional[float]],
    ):
        """
        Register a custom detection callback.

        Callback receives (pattern, signal, network) and returns
        detection probability (0-1) or None to use default.
        """
        self._detection_callbacks.append(callback)

    def on_event(self, callback: Callable[[AttackEvent], None]):
        """Register callback for attack events."""
        self._event_callbacks.append(callback)

    def generate_report(self, result: SimulationResult) -> str:
        """Generate a text report from simulation results."""
        lines = [
            "=" * 60,
            f"ATTACK SIMULATION REPORT",
            f"Scenario: {result.scenario_name}",
            "=" * 60,
            "",
            f"Duration: {result.duration:.1f} ms",
            f"Total Attacks: {result.total_attacks}",
            f"Detected: {result.detected_count} ({result.detection_rate:.1%})",
            f"Blocked: {result.blocked_count} ({result.block_rate:.1%})",
            "",
            "ATTACK TIMELINE",
            "-" * 40,
        ]

        for event in result.events:
            status = "BLOCKED" if event.blocked else ("DETECTED" if event.detected else "UNDETECTED")
            lines.append(
                f"  {event.timestamp:8.1f}ms | {event.stage_name:20} | "
                f"L{event.target_layer:2} | {status}"
            )

        lines.extend([
            "",
            "=" * 60,
        ])

        return "\n".join(lines)
