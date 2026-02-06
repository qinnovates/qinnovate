"""
Attack Signal Generator

Generates attack signals based on attack patterns.
Produces time series data that can be injected into simulations.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from .patterns import AttackPattern, AttackType


@dataclass
class AttackSignal:
    """
    Generated attack signal data.

    Attributes:
        times: Time points (ms)
        amplitudes: Signal amplitudes
        target_neurons: List of neuron IDs to target (if applicable)
        metadata: Additional signal metadata
    """
    times: np.ndarray
    amplitudes: np.ndarray
    target_neurons: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Signal duration in ms."""
        return self.times[-1] - self.times[0] if len(self.times) > 0 else 0.0

    @property
    def n_samples(self) -> int:
        """Number of samples."""
        return len(self.times)


class AttackGenerator:
    """
    Generates attack signals from attack patterns.

    Produces realistic attack waveforms that can be used to test
    neural security systems and firewall effectiveness.

    Example:
        >>> from tara_mvp.attacks import AttackGenerator, get_pattern
        >>> generator = AttackGenerator()
        >>> pattern = get_pattern("phase_jitter")
        >>> signal = generator.generate(pattern, duration=1000)
        >>> print(f"Generated {signal.n_samples} samples")
    """

    def __init__(self, dt: float = 0.1, seed: Optional[int] = None):
        """
        Initialize the attack generator.

        Args:
            dt: Time step for signal generation (ms)
            seed: Random seed for reproducibility
        """
        self.dt = dt
        self.rng = np.random.default_rng(seed)

    def generate(
        self,
        pattern: AttackPattern,
        duration: Optional[float] = None,
        target_neurons: Optional[List[str]] = None,
    ) -> AttackSignal:
        """
        Generate attack signal from pattern.

        Args:
            pattern: Attack pattern to use
            duration: Override pattern duration
            target_neurons: Specific neurons to target

        Returns:
            AttackSignal with generated data
        """
        dur = duration or pattern.duration
        n_samples = int(dur / self.dt)
        times = np.arange(0, dur, self.dt)

        # Generate signal based on attack type
        if pattern.attack_type == AttackType.PHASE_DISRUPTION:
            amplitudes = self._generate_phase_jitter(pattern, n_samples)

        elif pattern.attack_type == AttackType.AMPLITUDE_MANIPULATION:
            amplitudes = self._generate_amplitude_surge(pattern, n_samples)

        elif pattern.attack_type == AttackType.DESYNCHRONIZATION:
            amplitudes = self._generate_desync(pattern, n_samples)

        elif pattern.attack_type == AttackType.SIGNAL_INJECTION:
            amplitudes = self._generate_injection(pattern, n_samples)

        elif pattern.attack_type == AttackType.DOS_FLOODING:
            amplitudes = self._generate_dos_flood(pattern, n_samples)

        elif pattern.attack_type == AttackType.SIGNAL_REPLAY:
            amplitudes = self._generate_replay(pattern, n_samples)

        elif pattern.attack_type == AttackType.NEURAL_RANSOMWARE:
            amplitudes = self._generate_ransomware(pattern, n_samples)

        elif pattern.attack_type == AttackType.LAYER_8_GATEWAY:
            amplitudes = self._generate_gateway_bypass(pattern, n_samples)

        else:
            # Default: random noise scaled by intensity
            amplitudes = self._generate_noise(pattern, n_samples)

        # Scale by intensity
        amplitudes = amplitudes * pattern.intensity

        return AttackSignal(
            times=times,
            amplitudes=amplitudes,
            target_neurons=target_neurons or [],
            metadata={
                "pattern_name": pattern.name,
                "attack_type": pattern.attack_type.name,
                "target_layer": pattern.target_layer,
                "intensity": pattern.intensity,
            }
        )

    def _generate_phase_jitter(
        self,
        pattern: AttackPattern,
        n_samples: int
    ) -> np.ndarray:
        """Generate phase jitter attack signal."""
        params = pattern.parameters
        jitter_std = params.get("jitter_std", 5.0)
        freq = params.get("frequency_target", 40.0)

        # Base oscillation with jittered phase
        t = np.arange(n_samples) * self.dt / 1000  # Convert to seconds
        phase_jitter = self.rng.normal(0, jitter_std / 1000, n_samples).cumsum()

        signal = np.sin(2 * np.pi * freq * t + phase_jitter) * 100  # μV scale

        return signal

    def _generate_amplitude_surge(
        self,
        pattern: AttackPattern,
        n_samples: int
    ) -> np.ndarray:
        """Generate amplitude surge attack signal."""
        params = pattern.parameters
        surge_factor = params.get("surge_factor", 10.0)
        surge_duration = params.get("surge_duration", 50.0)
        surge_frequency = params.get("surge_frequency", 5.0)

        # Baseline signal
        signal = self.rng.normal(0, 10, n_samples)

        # Add periodic surges
        surge_samples = int(surge_duration / self.dt)
        surge_interval = int(1000 / surge_frequency / self.dt)

        for start in range(0, n_samples, surge_interval):
            end = min(start + surge_samples, n_samples)
            signal[start:end] *= surge_factor

        return signal

    def _generate_desync(
        self,
        pattern: AttackPattern,
        n_samples: int
    ) -> np.ndarray:
        """Generate desynchronization attack signal."""
        params = pattern.parameters
        phase_range = params.get("phase_offset_range", np.pi)

        # Multiple frequencies with random phase offsets
        t = np.arange(n_samples) * self.dt / 1000
        signal = np.zeros(n_samples)

        frequencies = [8, 12, 20, 40]  # Multiple bands
        for freq in frequencies:
            phase_offset = self.rng.uniform(-phase_range, phase_range)
            signal += np.sin(2 * np.pi * freq * t + phase_offset) * 25

        return signal

    def _generate_injection(
        self,
        pattern: AttackPattern,
        n_samples: int
    ) -> np.ndarray:
        """Generate signal injection attack."""
        # Synthetic "clean" signal that mimics legitimate neural activity
        t = np.arange(n_samples) * self.dt / 1000

        # Multi-frequency composition
        signal = (
            30 * np.sin(2 * np.pi * 10 * t) +  # Alpha
            20 * np.sin(2 * np.pi * 40 * t) +  # Gamma
            self.rng.normal(0, 5, n_samples)    # Noise
        )

        return signal

    def _generate_dos_flood(
        self,
        pattern: AttackPattern,
        n_samples: int
    ) -> np.ndarray:
        """Generate DoS flood attack signal."""
        params = pattern.parameters
        rate = params.get("signal_rate", 1000.0)
        amplitude = params.get("signal_amplitude", 100.0)

        # High-frequency, high-amplitude noise
        signal = self.rng.normal(0, amplitude, n_samples)

        # Add sharp spikes at high rate
        spike_interval = int(1000 / rate / self.dt)
        if spike_interval < 1:
            spike_interval = 1

        for i in range(0, n_samples, spike_interval):
            signal[i] += amplitude * 2

        return signal

    def _generate_replay(
        self,
        pattern: AttackPattern,
        n_samples: int
    ) -> np.ndarray:
        """Generate signal replay attack."""
        params = pattern.parameters
        replay_delay = params.get("replay_delay", 100.0)
        replay_count = params.get("replay_count", 10)

        # Generate a "captured" signal segment
        segment_length = int(replay_delay / self.dt)
        segment = self._generate_injection(pattern, segment_length)

        # Replay the segment multiple times
        signal = np.zeros(n_samples)
        for i in range(min(replay_count, n_samples // segment_length)):
            start = i * segment_length
            end = min(start + segment_length, n_samples)
            signal[start:end] = segment[:end-start]

        return signal

    def _generate_ransomware(
        self,
        pattern: AttackPattern,
        n_samples: int
    ) -> np.ndarray:
        """Generate neural ransomware attack signal."""
        params = pattern.parameters
        target_freq = params.get("target_frequency", 8.0)
        override_freq = params.get("override_frequency", 40.0)

        t = np.arange(n_samples) * self.dt / 1000

        # Phase 1: Suppress target frequency
        suppression = -50 * np.sin(2 * np.pi * target_freq * t)

        # Phase 2: Override with different frequency
        override = 80 * np.sin(2 * np.pi * override_freq * t)

        # Combine with gradual transition
        transition_point = n_samples // 3
        signal = np.zeros(n_samples)
        signal[:transition_point] = suppression[:transition_point]
        signal[transition_point:] = override[transition_point:]

        return signal

    def _generate_gateway_bypass(
        self,
        pattern: AttackPattern,
        n_samples: int
    ) -> np.ndarray:
        """Generate gateway bypass attack signal."""
        params = pattern.parameters
        target_coherence = params.get("target_coherence", 0.7)
        technique = params.get("evasion_technique", "gradual_shift")

        t = np.arange(n_samples) * self.dt / 1000

        if technique == "gradual_shift":
            # Start coherent, gradually become malicious
            base = 50 * np.sin(2 * np.pi * 40 * t)

            # Gradual phase drift
            drift = np.linspace(0, 2 * np.pi, n_samples)
            signal = base * np.cos(drift) + self.rng.normal(0, 5, n_samples)

        else:
            # Mimic coherent signal with hidden payload
            signal = (
                50 * np.sin(2 * np.pi * 40 * t) +  # Legitimate-looking
                10 * np.sin(2 * np.pi * 100 * t)   # Hidden high-freq
            )

        return signal

    def _generate_noise(
        self,
        pattern: AttackPattern,
        n_samples: int
    ) -> np.ndarray:
        """Generate generic noise attack signal."""
        return self.rng.normal(0, 50, n_samples)

    def generate_batch(
        self,
        patterns: List[AttackPattern],
        duration: float = 1000.0,
    ) -> List[AttackSignal]:
        """Generate multiple attack signals."""
        return [self.generate(p, duration) for p in patterns]
