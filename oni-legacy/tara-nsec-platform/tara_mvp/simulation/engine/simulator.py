"""
Main Simulation Engine

Coordinates the simulation of neural networks with:
- Time-stepping or event-driven simulation
- External input handling
- Progress reporting
- Data recording
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable, Union
import numpy as np
from enum import Enum
import time

from .events import EventQueue, Event, EventType, StimulusProtocol, PoissonInputGenerator
from .recorder import Recorder, RecordingConfig


class SimulationMode(Enum):
    """Simulation modes."""
    TIME_STEPPED = "time_stepped"     # Fixed time step
    EVENT_DRIVEN = "event_driven"     # Event-driven (not yet implemented)
    HYBRID = "hybrid"                 # Combination of both


@dataclass
class SimulationConfig:
    """Configuration for simulation."""

    # Timing
    duration: float = 1000.0          # Simulation duration (ms)
    dt: float = 0.1                   # Time step (ms)
    warmup: float = 0.0               # Warmup period (discarded)

    # Mode
    mode: SimulationMode = SimulationMode.TIME_STEPPED

    # Recording
    record: bool = True
    recording_config: Optional[RecordingConfig] = None

    # Progress reporting
    report_interval: float = 100.0    # Progress report every N ms
    verbose: bool = True

    # Random seed
    seed: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "duration": self.duration,
            "dt": self.dt,
            "warmup": self.warmup,
            "mode": self.mode.value,
            "record": self.record,
            "seed": self.seed,
        }


@dataclass
class SimulationResult:
    """Results from a simulation run."""

    # Timing info
    duration: float = 0.0
    dt: float = 0.1
    n_steps: int = 0
    wall_time: float = 0.0            # Actual elapsed time

    # Network info
    n_neurons: int = 0
    n_synapses: int = 0

    # Activity summary
    total_spikes: int = 0
    mean_firing_rate: float = 0.0     # Hz

    # Recorded data (if recording enabled)
    t: np.ndarray = None
    voltages: Dict[str, np.ndarray] = None
    spike_times: Dict[str, List[float]] = None
    spike_counts: Dict[str, int] = None

    # Additional metrics
    metrics: Dict[str, Any] = None


class SimulationEngine:
    """
    Main simulation engine for NeuroSim.

    Coordinates network simulation including:
    - Network stepping
    - Event processing
    - Input injection
    - Data recording
    - Progress reporting

    Usage:
        >>> from neurosim.core import LayeredNetwork
        >>> from neurosim.engine import SimulationEngine, SimulationConfig

        >>> # Create network
        >>> network = LayeredNetwork.create_simple(n_layers=3)

        >>> # Configure simulation
        >>> config = SimulationConfig(duration=1000, dt=0.1)

        >>> # Run simulation
        >>> engine = SimulationEngine(network, config)
        >>> result = engine.run()

        >>> # Analyze results
        >>> print(f"Total spikes: {result.total_spikes}")
    """

    def __init__(
        self,
        network,
        config: Optional[SimulationConfig] = None
    ):
        """
        Initialize simulation engine.

        Args:
            network: Neural network to simulate
            config: Simulation configuration
        """
        self.network = network
        self.config = config or SimulationConfig()

        # Set random seed
        if self.config.seed is not None:
            np.random.seed(self.config.seed)

        # Synchronize dt between network and config
        self.network.params.dt = self.config.dt

        # Initialize event queue
        self.event_queue = EventQueue()

        # Initialize recorder
        if self.config.record:
            rec_config = self.config.recording_config or RecordingConfig()
            self.recorder = Recorder(rec_config)
            self.recorder.setup(network)
        else:
            self.recorder = None

        # Stimulus protocols
        self._stimulus_protocols: List[StimulusProtocol] = []
        self._input_generators: List[PoissonInputGenerator] = []

        # Progress callbacks
        self._progress_callbacks: List[Callable] = []
        self._step_callbacks: List[Callable] = []

        # State
        self._running = False
        self._paused = False
        self._t = 0.0

    @property
    def t(self) -> float:
        """Current simulation time."""
        return self._t

    def add_stimulus(self, protocol: StimulusProtocol):
        """
        Add a stimulus protocol.

        Args:
            protocol: Stimulus protocol to add
        """
        self._stimulus_protocols.append(protocol)
        protocol.generate_events(self.event_queue)

    def add_poisson_input(self, generator: PoissonInputGenerator):
        """
        Add Poisson spike input generator.

        Args:
            generator: Input generator to add
        """
        self._input_generators.append(generator)
        generator.generate_events(self.event_queue)

    def add_input_current(
        self,
        neuron_ids: Union[str, List[str]],
        current: Union[float, np.ndarray],
        onset: float = 0.0,
        duration: Optional[float] = None
    ):
        """
        Add constant or time-varying input current.

        Args:
            neuron_ids: Target neuron(s)
            current: Current value(s) in nA
            onset: Start time (ms)
            duration: Duration (ms), None = entire simulation
        """
        if duration is None:
            duration = self.config.duration - onset

        protocol = StimulusProtocol(
            target_ids=neuron_ids,
            onset=onset,
            duration=duration,
            amplitude=current if isinstance(current, float) else float(np.mean(current)),
            pattern="constant"
        )
        self.add_stimulus(protocol)

    def on_progress(self, callback: Callable[[float, float], None]):
        """
        Register progress callback.

        Args:
            callback: Function(current_time, total_duration)
        """
        self._progress_callbacks.append(callback)

    def on_step(self, callback: Callable[[float, dict], None]):
        """
        Register step callback.

        Args:
            callback: Function(time, network)
        """
        self._step_callbacks.append(callback)

    def run(self) -> SimulationResult:
        """
        Run the simulation.

        Returns:
            SimulationResult with recorded data and metrics
        """
        self._running = True
        self._paused = False

        config = self.config
        start_wall_time = time.time()

        # Calculate number of steps
        n_steps = int(config.duration / config.dt)
        report_steps = int(config.report_interval / config.dt)

        # Track warmup
        warmup_steps = int(config.warmup / config.dt)
        recording_started = config.warmup <= 0

        if config.verbose:
            print(f"Starting simulation: {config.duration}ms, dt={config.dt}ms")
            print(f"Network: {self.network.n_neurons} neurons, {self.network.n_synapses} synapses")

        # Main simulation loop
        for step in range(n_steps):
            if not self._running:
                break

            while self._paused:
                time.sleep(0.01)

            self._t = step * config.dt

            # Process events for this timestep
            self._process_events(self._t)

            # Apply stimulus currents
            self._apply_stimuli(self._t)

            # Step the network
            spikes = self.network.step(record_history=self.config.record)

            # Record data (after warmup)
            if self._t >= config.warmup:
                if not recording_started:
                    recording_started = True
                    if self.recorder:
                        self.recorder.reset()
                        self.recorder.setup(self.network)

                if self.recorder:
                    self.recorder.record_step(self._t, self.network)

            # Step callbacks
            for callback in self._step_callbacks:
                callback(self._t, self.network)

            # Progress reporting
            if config.verbose and step > 0 and step % report_steps == 0:
                progress = (step / n_steps) * 100
                print(f"Progress: {progress:.1f}% ({self._t:.1f}ms)")

                for callback in self._progress_callbacks:
                    callback(self._t, config.duration)

        # Compute results
        wall_time = time.time() - start_wall_time
        result = self._compile_results(wall_time)

        if config.verbose:
            print(f"Simulation complete: {wall_time:.2f}s wall time")
            print(f"Total spikes: {result.total_spikes}")
            print(f"Mean firing rate: {result.mean_firing_rate:.2f} Hz")

        self._running = False
        return result

    def _process_events(self, t: float):
        """Process events up to current time."""
        events = self.event_queue.pop_until(t)

        for event in events:
            if event.event_type == EventType.INPUT:
                # Direct input event
                neuron = self.network.neurons.get(event.target_id)
                if neuron:
                    weight = event.data.get("weight", 1.0)
                    neuron.receive_input(weight)

            elif event.event_type == EventType.STIMULUS_ON:
                # Stimulus onset - handled by apply_stimuli
                pass

            elif event.event_type == EventType.STIMULUS_OFF:
                # Stimulus offset - handled by apply_stimuli
                pass

            # Execute event callback if present
            event.execute(self)

    def _apply_stimuli(self, t: float):
        """Apply stimulus currents to neurons."""
        for protocol in self._stimulus_protocols:
            current = protocol.get_current(t)
            if abs(current) > 1e-12:
                for target_id in protocol.target_ids:
                    neuron = self.network.neurons.get(target_id)
                    if neuron:
                        neuron.receive_input(current)

    def _compile_results(self, wall_time: float) -> SimulationResult:
        """Compile simulation results."""
        result = SimulationResult(
            duration=self.config.duration,
            dt=self.config.dt,
            n_steps=int(self.config.duration / self.config.dt),
            wall_time=wall_time,
            n_neurons=self.network.n_neurons,
            n_synapses=self.network.n_synapses,
        )

        # Compile spike data
        if self.recorder:
            data = self.recorder.get_data()
            result.t = np.array(data.t)
            result.voltages = {k: np.array(v) for k, v in data.voltages.items()}
            result.spike_times = dict(data.spike_times)

        # Count spikes
        result.spike_counts = {}
        result.total_spikes = 0

        for neuron_id, neuron in self.network.neurons.items():
            count = len(neuron.state.spike_times)
            result.spike_counts[neuron_id] = count
            result.total_spikes += count

        # Compute firing rate
        effective_duration = self.config.duration - self.config.warmup
        if effective_duration > 0 and self.network.n_neurons > 0:
            result.mean_firing_rate = (
                result.total_spikes /
                self.network.n_neurons /
                (effective_duration / 1000)  # Convert to seconds
            )

        return result

    def pause(self):
        """Pause simulation."""
        self._paused = True

    def resume(self):
        """Resume simulation."""
        self._paused = False

    def stop(self):
        """Stop simulation."""
        self._running = False

    def reset(self):
        """Reset simulation state."""
        self._t = 0.0
        self._running = False
        self._paused = False
        self.network.reset()
        self.event_queue.clear()

        if self.recorder:
            self.recorder.reset()

        # Re-generate events for protocols
        for protocol in self._stimulus_protocols:
            protocol.generate_events(self.event_queue)
        for generator in self._input_generators:
            generator.generate_events(self.event_queue)


def run_simulation(
    network,
    duration: float = 1000.0,
    input_current: Optional[Dict[str, np.ndarray]] = None,
    dt: float = 0.1,
    record: bool = True,
    verbose: bool = False,
    **kwargs
) -> SimulationResult:
    """
    Convenience function to run a simulation.

    Args:
        network: Network to simulate
        duration: Simulation duration (ms)
        input_current: Dictionary mapping neuron IDs to current arrays
        dt: Time step (ms)
        record: Whether to record data
        verbose: Print progress
        **kwargs: Additional SimulationConfig parameters

    Returns:
        SimulationResult
    """
    config = SimulationConfig(
        duration=duration,
        dt=dt,
        record=record,
        verbose=verbose,
        **kwargs
    )

    engine = SimulationEngine(network, config)

    # Add input currents if provided
    if input_current:
        for neuron_id, current in input_current.items():
            engine.add_input_current(neuron_id, current)

    return engine.run()
