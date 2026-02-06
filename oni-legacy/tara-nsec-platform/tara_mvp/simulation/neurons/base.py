"""
Base Neuron Model

Abstract base class for all neuron models in NeuroSim.
Provides common interface and utilities for simulation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
import numpy as np
import uuid


class NeuronType(Enum):
    """Types of neurons based on function."""
    EXCITATORY = "excitatory"
    INHIBITORY = "inhibitory"
    MODULATORY = "modulatory"
    SENSORY = "sensory"
    MOTOR = "motor"
    INTERNEURON = "interneuron"


@dataclass
class NeuronParameters:
    """Base parameters for all neuron models."""
    # Identification
    neuron_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    neuron_type: NeuronType = NeuronType.EXCITATORY
    label: str = ""

    # Spatial position (for visualization and distance-based connectivity)
    position: tuple = (0.0, 0.0, 0.0)  # (x, y, z) in μm

    # Layer assignment (for ONI framework integration)
    oni_layer: int = 2  # Default to L2 (Cellular layer)

    # Simulation parameters
    dt: float = 0.1  # Time step (ms)

    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary for serialization."""
        return {
            "neuron_id": self.neuron_id,
            "neuron_type": self.neuron_type.value,
            "label": self.label,
            "position": self.position,
            "oni_layer": self.oni_layer,
            "dt": self.dt,
        }


@dataclass
class NeuronState:
    """
    Current state of a neuron.

    Tracks membrane potential, spike history, and other dynamic variables.
    """
    # Core state
    V: float = 0.0  # Membrane potential (mV)
    fired: bool = False  # Did neuron fire this timestep?
    refractory_remaining: float = 0.0  # Remaining refractory time (ms)

    # Accumulated inputs
    I_syn: float = 0.0  # Synaptic current (nA)
    I_ext: float = 0.0  # External input current (nA)

    # History tracking
    spike_times: List[float] = field(default_factory=list)
    V_history: List[float] = field(default_factory=list)

    # Time tracking
    t: float = 0.0  # Current simulation time (ms)

    def reset(self, V_rest: float = 0.0):
        """Reset neuron state to initial conditions."""
        self.V = V_rest
        self.fired = False
        self.refractory_remaining = 0.0
        self.I_syn = 0.0
        self.I_ext = 0.0
        self.spike_times = []
        self.V_history = []
        self.t = 0.0

    @property
    def spike_count(self) -> int:
        """Total number of spikes."""
        return len(self.spike_times)

    @property
    def firing_rate(self) -> float:
        """Average firing rate in Hz."""
        if self.t <= 0:
            return 0.0
        return (self.spike_count / self.t) * 1000  # Convert to Hz

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "V": self.V,
            "fired": self.fired,
            "t": self.t,
            "spike_count": self.spike_count,
            "firing_rate": self.firing_rate,
            "spike_times": self.spike_times[-100:],  # Last 100 spikes
        }


class Neuron(ABC):
    """
    Abstract base class for all neuron models.

    Provides common interface for:
    - State updates
    - Input handling
    - Spike detection
    - History tracking
    - Serialization
    """

    def __init__(self, params: Optional[NeuronParameters] = None):
        """
        Initialize neuron with parameters.

        Args:
            params: Neuron parameters (uses defaults if None)
        """
        self.params = params or NeuronParameters()
        self.state = NeuronState()
        self._input_callbacks: List[Callable] = []
        self._spike_callbacks: List[Callable] = []

    @property
    def id(self) -> str:
        """Unique identifier for this neuron."""
        return self.params.neuron_id

    @property
    def V(self) -> float:
        """Current membrane potential."""
        return self.state.V

    @property
    def fired(self) -> bool:
        """Whether neuron fired this timestep."""
        return self.state.fired

    @abstractmethod
    def _compute_dV(self, I_total: float) -> float:
        """
        Compute change in membrane potential.

        Args:
            I_total: Total input current (nA)

        Returns:
            Change in membrane potential (mV)
        """
        pass

    @abstractmethod
    def _check_spike(self) -> bool:
        """
        Check if neuron should fire.

        Returns:
            True if spike occurred
        """
        pass

    @abstractmethod
    def _reset_after_spike(self):
        """Reset neuron state after spike."""
        pass

    @abstractmethod
    def get_V_rest(self) -> float:
        """Get resting membrane potential."""
        pass

    def receive_input(self, current: float, input_type: str = "synaptic"):
        """
        Receive input current from synapse or external source.

        Args:
            current: Input current (nA)
            input_type: "synaptic" or "external"
        """
        if input_type == "synaptic":
            self.state.I_syn += current
        else:
            self.state.I_ext += current

        # Notify callbacks
        for callback in self._input_callbacks:
            callback(self, current, input_type)

    def step(self, record_history: bool = True) -> bool:
        """
        Advance simulation by one time step.

        Args:
            record_history: Whether to record voltage history

        Returns:
            True if neuron fired this step
        """
        dt = self.params.dt
        self.state.fired = False

        # Handle refractory period
        if self.state.refractory_remaining > 0:
            self.state.refractory_remaining -= dt
            self.state.I_syn = 0.0
            self.state.I_ext = 0.0
            self.state.t += dt
            if record_history:
                self.state.V_history.append(self.state.V)
            return False

        # Compute total input current
        I_total = self.state.I_syn + self.state.I_ext

        # Update membrane potential
        dV = self._compute_dV(I_total)
        self.state.V += dV

        # Check for spike
        if self._check_spike():
            self.state.fired = True
            self.state.spike_times.append(self.state.t)
            self._reset_after_spike()

            # Notify spike callbacks
            for callback in self._spike_callbacks:
                callback(self, self.state.t)

        # Record history
        if record_history:
            self.state.V_history.append(self.state.V)

        # Reset inputs for next step
        self.state.I_syn = 0.0
        self.state.I_ext = 0.0

        # Advance time
        self.state.t += dt

        return self.state.fired

    def simulate(
        self,
        duration: float,
        input_current: Optional[np.ndarray] = None,
        record_history: bool = True
    ) -> Dict[str, np.ndarray]:
        """
        Run simulation for specified duration.

        Args:
            duration: Simulation duration (ms)
            input_current: External input current array (optional)
            record_history: Whether to record voltage history

        Returns:
            Dictionary with simulation results
        """
        dt = self.params.dt
        n_steps = int(duration / dt)

        # Reset state
        self.state.reset(self.get_V_rest())

        # Prepare input current
        if input_current is None:
            input_current = np.zeros(n_steps)
        elif len(input_current) != n_steps:
            # Resample input to match timesteps
            input_current = np.interp(
                np.linspace(0, 1, n_steps),
                np.linspace(0, 1, len(input_current)),
                input_current
            )

        # Run simulation
        spikes = np.zeros(n_steps, dtype=bool)
        for i in range(n_steps):
            self.receive_input(input_current[i], input_type="external")
            spikes[i] = self.step(record_history=record_history)

        # Prepare results
        time = np.arange(0, duration, dt)
        results = {
            "time": time,
            "V": np.array(self.state.V_history) if record_history else None,
            "spikes": spikes,
            "spike_times": np.array(self.state.spike_times),
            "input_current": input_current,
            "firing_rate": self.state.firing_rate,
        }

        return results

    def on_input(self, callback: Callable):
        """Register callback for input events."""
        self._input_callbacks.append(callback)

    def on_spike(self, callback: Callable):
        """Register callback for spike events."""
        self._spike_callbacks.append(callback)

    def reset(self):
        """Reset neuron to initial state."""
        self.state.reset(self.get_V_rest())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize neuron to dictionary."""
        return {
            "model": self.__class__.__name__,
            "params": self.params.to_dict(),
            "state": self.state.to_dict(),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, V={self.V:.2f}mV)"
