"""
MOABB Adapter for TARA

Integrates the Mother of All BCI Benchmarks (MOABB) dataset framework with TARA's
neural security platform. Enables testing of ONI security algorithms against real
EEG data from standardized BCI experiments.

License:
    MOABB is licensed under BSD 3-Clause License
    See: https://github.com/NeuroTechX/moabb/blob/develop/LICENSE

Citation:
    When using MOABB data through this adapter, cite:

    Jayaram, V., & Barachant, A. (2018). MOABB: Trustworthy algorithm benchmarking
    for BCIs. Journal of Neural Engineering, 15(6), 066011.
    https://doi.org/10.1088/1741-2552/aadea0

Usage:
    >>> from tara_mvp.data.moabb_adapter import MOABBAdapter, BCIParadigm
    >>>
    >>> # Initialize adapter
    >>> adapter = MOABBAdapter()
    >>>
    >>> # Load motor imagery dataset
    >>> dataset = adapter.load_dataset("BNCI2014_001")
    >>> signals, labels = adapter.get_signals(dataset, subject=1)
    >>>
    >>> # Process through Neural Firewall
    >>> from tara_mvp import NeuralFirewall
    >>> firewall = NeuralFirewall()
    >>> for signal in signals:
    ...     result = firewall.process_signal(signal)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)

# Check if MOABB is available
_MOABB_AVAILABLE = False
_moabb = None

try:
    import moabb
    from moabb.datasets import BNCI2014_001, BNCI2014_002, BNCI2014_004
    from moabb.paradigms import MotorImagery, P300, SSVEP
    _MOABB_AVAILABLE = True
    _moabb = moabb
    logger.info(f"MOABB v{moabb.__version__} loaded successfully")
except ImportError:
    logger.warning(
        "MOABB not installed. Install with: pip install moabb\n"
        "Or install TARA with MOABB support: pip install oni-tara[moabb]"
    )


class BCIParadigm(Enum):
    """BCI paradigms supported by MOABB.

    Each paradigm represents a different approach to brain-computer
    interaction, with different security considerations.
    """
    MOTOR_IMAGERY = auto()      # Imagined movements (most common)
    P300 = auto()               # Oddball response (spelling)
    SSVEP = auto()              # Steady-state visual evoked potentials
    C_VEP = auto()              # Code-modulated VEP
    ERPCOV = auto()             # ERP covariance


class DatasetInfo:
    """Information about a MOABB dataset."""

    # Dataset registry with metadata
    REGISTRY: Dict[str, Dict[str, Any]] = {
        "BNCI2014_001": {
            "paradigm": BCIParadigm.MOTOR_IMAGERY,
            "subjects": 9,
            "sessions": 2,
            "channels": 22,
            "sampling_rate": 250,
            "classes": ["left_hand", "right_hand", "feet", "tongue"],
            "description": "Motor imagery 4-class dataset",
            "oni_relevance": "Test motor cortex (L13) signal injection attacks",
        },
        "BNCI2014_002": {
            "paradigm": BCIParadigm.MOTOR_IMAGERY,
            "subjects": 14,
            "sessions": 5,
            "channels": 15,
            "sampling_rate": 512,
            "classes": ["right_hand", "feet"],
            "description": "Motor imagery 2-class longitudinal",
            "oni_relevance": "Longitudinal attack detection validation",
        },
        "BNCI2014_004": {
            "paradigm": BCIParadigm.MOTOR_IMAGERY,
            "subjects": 9,
            "sessions": 5,
            "channels": 3,
            "sampling_rate": 250,
            "classes": ["left_hand", "right_hand"],
            "description": "Motor imagery 2-class minimal channels",
            "oni_relevance": "Minimal-channel firewall testing",
        },
        "EPFLP300": {
            "paradigm": BCIParadigm.P300,
            "subjects": 8,
            "sessions": 4,
            "channels": 32,
            "sampling_rate": 2048,
            "classes": ["target", "non-target"],
            "description": "P300 speller dataset",
            "oni_relevance": "Privacy-sensitive ERP detection (Kohno threats)",
        },
        "SSVEP_Exo": {
            "paradigm": BCIParadigm.SSVEP,
            "subjects": 12,
            "sessions": 1,
            "channels": 8,
            "sampling_rate": 256,
            "classes": ["12Hz", "10Hz", "8.57Hz", "7.5Hz"],
            "description": "SSVEP for exoskeleton control",
            "oni_relevance": "Frequency injection attack vectors",
        },
    }

    @classmethod
    def get_info(cls, dataset_name: str) -> Optional[Dict[str, Any]]:
        """Get dataset information by name."""
        return cls.REGISTRY.get(dataset_name)

    @classmethod
    def list_datasets(cls, paradigm: Optional[BCIParadigm] = None) -> List[str]:
        """List available datasets, optionally filtered by paradigm."""
        if paradigm is None:
            return list(cls.REGISTRY.keys())
        return [
            name for name, info in cls.REGISTRY.items()
            if info["paradigm"] == paradigm
        ]


@dataclass
class EEGSignal:
    """Container for EEG signal data from MOABB.

    Attributes:
        data: Raw EEG data array (channels x samples)
        sampling_rate: Sampling frequency in Hz
        channels: List of channel names
        label: Class label for this epoch
        subject: Subject ID
        session: Session identifier
        paradigm: BCI paradigm type
        metadata: Additional metadata
    """
    data: np.ndarray
    sampling_rate: float
    channels: List[str]
    label: str
    subject: int
    session: str
    paradigm: BCIParadigm
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Duration of signal in seconds."""
        return self.data.shape[1] / self.sampling_rate

    @property
    def n_channels(self) -> int:
        """Number of channels."""
        return self.data.shape[0]

    @property
    def n_samples(self) -> int:
        """Number of samples."""
        return self.data.shape[1]

    def to_tara_format(self) -> Dict[str, Any]:
        """Convert to TARA signal format for firewall processing.

        Returns:
            Dictionary compatible with tara.core.firewall.Signal
        """
        return {
            "data": self.data.tolist(),
            "frequency": self.sampling_rate,
            "amplitude": float(np.abs(self.data).mean()),
            "timestamp": 0.0,  # Will be set during processing
            "source": f"moabb_{self.paradigm.name}",
            "metadata": {
                "subject": self.subject,
                "session": self.session,
                "label": self.label,
                "channels": self.channels,
                "paradigm": self.paradigm.name,
                **self.metadata,
            }
        }


@dataclass
class AttackInjectedSignal:
    """EEG signal with injected attack pattern.

    Used for testing attack detection and firewall robustness.
    """
    original: EEGSignal
    attacked: np.ndarray
    attack_type: str
    attack_params: Dict[str, Any]
    injection_channels: List[int]
    injection_start_sample: int
    injection_duration_samples: int

    @property
    def attack_window(self) -> Tuple[int, int]:
        """Return start and end sample of attack window."""
        return (
            self.injection_start_sample,
            self.injection_start_sample + self.injection_duration_samples
        )


class MOABBAdapter:
    """Adapter for loading and processing MOABB datasets for TARA.

    This adapter provides a bridge between the MOABB benchmarking framework
    and TARA's neural security platform, enabling:

    1. Loading standardized BCI datasets
    2. Converting signals to TARA-compatible format
    3. Injecting attack patterns for security testing
    4. Benchmarking coherence metric and firewall performance

    Example:
        >>> adapter = MOABBAdapter()
        >>>
        >>> # List available datasets
        >>> print(adapter.list_datasets())
        ['BNCI2014_001', 'BNCI2014_002', ...]
        >>>
        >>> # Load dataset
        >>> dataset = adapter.load_dataset("BNCI2014_001")
        >>>
        >>> # Get signals for a subject
        >>> signals = adapter.get_signals(dataset, subject=1, session="0train")
        >>>
        >>> # Process through TARA
        >>> from tara_mvp import NeuralFirewall, CoherenceMetric
        >>> firewall = NeuralFirewall()
        >>> coherence = CoherenceMetric()
        >>>
        >>> for signal in signals:
        ...     cs_score = coherence.calculate(signal.data)
        ...     result = firewall.process_signal(signal.to_tara_format())
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the MOABB adapter.

        Args:
            cache_dir: Directory for caching downloaded datasets.
                      If None, uses MOABB's default cache location.
        """
        if not _MOABB_AVAILABLE:
            raise ImportError(
                "MOABB is required but not installed. "
                "Install with: pip install moabb"
            )

        self.cache_dir = cache_dir
        self._loaded_datasets: Dict[str, Any] = {}
        self._paradigms: Dict[BCIParadigm, Any] = {}

        logger.info("MOABBAdapter initialized")

    @property
    def is_available(self) -> bool:
        """Check if MOABB is available."""
        return _MOABB_AVAILABLE

    def list_datasets(
        self,
        paradigm: Optional[BCIParadigm] = None
    ) -> List[Dict[str, Any]]:
        """List available datasets with metadata.

        Args:
            paradigm: Filter by paradigm type (optional)

        Returns:
            List of dataset info dictionaries
        """
        datasets = DatasetInfo.list_datasets(paradigm)
        return [
            {"name": name, **DatasetInfo.get_info(name)}
            for name in datasets
        ]

    def load_dataset(self, name: str) -> Any:
        """Load a MOABB dataset.

        Args:
            name: Dataset name (e.g., "BNCI2014_001")

        Returns:
            MOABB dataset object

        Raises:
            ValueError: If dataset is not found
        """
        if name in self._loaded_datasets:
            logger.debug(f"Using cached dataset: {name}")
            return self._loaded_datasets[name]

        info = DatasetInfo.get_info(name)
        if info is None:
            available = DatasetInfo.list_datasets()
            raise ValueError(
                f"Unknown dataset: {name}. "
                f"Available: {available}"
            )

        # Load dataset based on name
        dataset_classes = {
            "BNCI2014_001": BNCI2014_001 if _MOABB_AVAILABLE else None,
            "BNCI2014_002": BNCI2014_002 if _MOABB_AVAILABLE else None,
            "BNCI2014_004": BNCI2014_004 if _MOABB_AVAILABLE else None,
        }

        dataset_class = dataset_classes.get(name)
        if dataset_class is None:
            raise ValueError(
                f"Dataset {name} is registered but loader not implemented. "
                f"Implemented: {list(dataset_classes.keys())}"
            )

        logger.info(f"Loading dataset: {name}")
        dataset = dataset_class()
        self._loaded_datasets[name] = dataset

        return dataset

    def _get_paradigm(self, paradigm: BCIParadigm) -> Any:
        """Get or create a MOABB paradigm object."""
        if paradigm in self._paradigms:
            return self._paradigms[paradigm]

        paradigm_classes = {
            BCIParadigm.MOTOR_IMAGERY: MotorImagery if _MOABB_AVAILABLE else None,
            BCIParadigm.P300: P300 if _MOABB_AVAILABLE else None,
            BCIParadigm.SSVEP: SSVEP if _MOABB_AVAILABLE else None,
        }

        paradigm_class = paradigm_classes.get(paradigm)
        if paradigm_class is None:
            raise ValueError(f"Paradigm not implemented: {paradigm}")

        self._paradigms[paradigm] = paradigm_class()
        return self._paradigms[paradigm]

    def get_signals(
        self,
        dataset: Any,
        subject: int,
        session: Optional[str] = None,
        max_epochs: Optional[int] = None,
    ) -> List[EEGSignal]:
        """Extract EEG signals from a loaded dataset.

        Args:
            dataset: Loaded MOABB dataset
            subject: Subject ID (1-indexed)
            session: Session name (optional, loads all if None)
            max_epochs: Maximum number of epochs to load (optional)

        Returns:
            List of EEGSignal objects
        """
        dataset_name = dataset.__class__.__name__
        info = DatasetInfo.get_info(dataset_name)

        if info is None:
            # Try to infer paradigm from dataset
            paradigm = BCIParadigm.MOTOR_IMAGERY  # Default
        else:
            paradigm = info["paradigm"]

        paradigm_obj = self._get_paradigm(paradigm)

        # Get data using MOABB's get_data method
        logger.info(f"Loading subject {subject} from {dataset_name}")
        X, labels, meta = paradigm_obj.get_data(
            dataset,
            subjects=[subject],
            return_epochs=False
        )

        signals = []
        channels = dataset.ch_names if hasattr(dataset, "ch_names") else [
            f"Ch{i}" for i in range(X.shape[1])
        ]

        n_epochs = min(len(X), max_epochs) if max_epochs else len(X)

        for i in range(n_epochs):
            signal = EEGSignal(
                data=X[i],
                sampling_rate=info["sampling_rate"] if info else 250.0,
                channels=channels,
                label=str(labels[i]),
                subject=subject,
                session=meta.iloc[i]["session"] if "session" in meta.columns else "unknown",
                paradigm=paradigm,
                metadata={
                    "dataset": dataset_name,
                    "epoch_index": i,
                    "run": meta.iloc[i].get("run", "unknown"),
                }
            )
            signals.append(signal)

        logger.info(f"Loaded {len(signals)} epochs for subject {subject}")
        return signals

    def inject_attack(
        self,
        signal: EEGSignal,
        attack_type: str,
        channels: Optional[List[int]] = None,
        start_ratio: float = 0.3,
        duration_ratio: float = 0.2,
        intensity: float = 1.0,
        **attack_params,
    ) -> AttackInjectedSignal:
        """Inject an attack pattern into a signal.

        This method is used to test TARA's attack detection and firewall
        capabilities against realistic BCI signals.

        Args:
            signal: Original EEG signal
            attack_type: Type of attack ("spike", "noise", "frequency", "phase")
            channels: Channels to attack (None = all)
            start_ratio: Start position as ratio of signal length (0-1)
            duration_ratio: Duration as ratio of signal length (0-1)
            intensity: Attack intensity multiplier
            **attack_params: Additional attack-specific parameters

        Returns:
            AttackInjectedSignal containing original and attacked signal
        """
        data = signal.data.copy()
        n_channels, n_samples = data.shape

        # Determine attack window
        start_sample = int(n_samples * start_ratio)
        duration_samples = int(n_samples * duration_ratio)
        end_sample = min(start_sample + duration_samples, n_samples)

        # Determine channels to attack
        if channels is None:
            channels = list(range(n_channels))

        # Generate attack pattern based on type
        attack_window = end_sample - start_sample

        if attack_type == "spike":
            # Inject high-amplitude spikes (potential ransomware signature)
            spike_interval = attack_params.get("spike_interval", 10)
            spike_amplitude = intensity * np.abs(data).max() * 5
            for ch in channels:
                for t in range(0, attack_window, spike_interval):
                    if start_sample + t < n_samples:
                        data[ch, start_sample + t] = spike_amplitude

        elif attack_type == "noise":
            # Inject Gaussian noise (eavesdropping masking attempt)
            noise_amplitude = intensity * np.abs(data).std() * 3
            noise = np.random.randn(len(channels), attack_window) * noise_amplitude
            for i, ch in enumerate(channels):
                data[ch, start_sample:end_sample] += noise[i, :end_sample-start_sample]

        elif attack_type == "frequency":
            # Inject frequency component (SSVEP hijacking)
            inject_freq = attack_params.get("frequency", 10.0)  # Hz
            t = np.arange(attack_window) / signal.sampling_rate
            freq_signal = intensity * np.abs(data).max() * np.sin(2 * np.pi * inject_freq * t)
            for ch in channels:
                data[ch, start_sample:end_sample] += freq_signal[:end_sample-start_sample]

        elif attack_type == "phase":
            # Phase shift attack (timing manipulation)
            shift = attack_params.get("shift_samples", 5)
            for ch in channels:
                original = data[ch, start_sample:end_sample].copy()
                shifted = np.roll(original, shift)
                data[ch, start_sample:end_sample] = shifted

        elif attack_type == "dc_shift":
            # DC offset injection (amplifier saturation attack)
            dc_offset = intensity * np.abs(data).max() * 2
            for ch in channels:
                data[ch, start_sample:end_sample] += dc_offset

        else:
            raise ValueError(f"Unknown attack type: {attack_type}")

        return AttackInjectedSignal(
            original=signal,
            attacked=data,
            attack_type=attack_type,
            attack_params={"intensity": intensity, **attack_params},
            injection_channels=channels,
            injection_start_sample=start_sample,
            injection_duration_samples=duration_samples,
        )

    def _calculate_signal_coherence(
        self,
        data: np.ndarray,
        sampling_rate: float,
        coherence_metric: Any,
    ) -> float:
        """Calculate coherence score for multichannel EEG data.

        Converts 2D EEG array (channels x samples) to the format expected
        by CoherenceMetric (arrival_times, amplitudes).

        Args:
            data: EEG data array (channels x samples)
            sampling_rate: Sampling rate in Hz
            coherence_metric: CoherenceMetric instance

        Returns:
            Coherence score (0-1)
        """
        # Average across channels to get a single time series
        mean_signal = np.mean(data, axis=0)
        n_samples = len(mean_signal)

        # Generate arrival times based on sampling rate
        arrival_times = np.arange(n_samples) / sampling_rate

        # Use the signal amplitudes directly
        amplitudes = mean_signal.tolist()
        times = arrival_times.tolist()

        return coherence_metric.calculate(times, amplitudes)

    def benchmark_coherence(
        self,
        signals: List[EEGSignal],
        attacked_signals: Optional[List[AttackInjectedSignal]] = None,
    ) -> Dict[str, Any]:
        """Benchmark coherence metric against real and attacked signals.

        Args:
            signals: List of clean EEG signals
            attacked_signals: List of attacked signals (optional)

        Returns:
            Benchmark results including accuracy, false positive/negative rates
        """
        from ..core.coherence import CoherenceMetric

        coherence = CoherenceMetric()

        results = {
            "clean_signals": {
                "count": len(signals),
                "scores": [],
                "mean_score": 0.0,
                "std_score": 0.0,
            },
            "attacked_signals": None,
            "detection_metrics": None,
        }

        # Analyze clean signals
        for signal in signals:
            score = self._calculate_signal_coherence(signal.data, signal.sampling_rate, coherence)
            results["clean_signals"]["scores"].append(score)

        results["clean_signals"]["mean_score"] = float(np.mean(results["clean_signals"]["scores"]))
        results["clean_signals"]["std_score"] = float(np.std(results["clean_signals"]["scores"]))

        # Analyze attacked signals if provided
        if attacked_signals:
            results["attacked_signals"] = {
                "count": len(attacked_signals),
                "scores": [],
                "mean_score": 0.0,
                "std_score": 0.0,
                "by_attack_type": {},
            }

            for attacked in attacked_signals:
                score = self._calculate_signal_coherence(
                    attacked.attacked,
                    attacked.original.sampling_rate,
                    coherence
                )
                results["attacked_signals"]["scores"].append(score)

                # Group by attack type
                attack_type = attacked.attack_type
                if attack_type not in results["attacked_signals"]["by_attack_type"]:
                    results["attacked_signals"]["by_attack_type"][attack_type] = []
                results["attacked_signals"]["by_attack_type"][attack_type].append(score)

            results["attacked_signals"]["mean_score"] = float(
                np.mean(results["attacked_signals"]["scores"])
            )
            results["attacked_signals"]["std_score"] = float(
                np.std(results["attacked_signals"]["scores"])
            )

            # Calculate detection metrics
            # Using 2 standard deviations from clean mean as threshold
            threshold = (
                results["clean_signals"]["mean_score"] -
                2 * results["clean_signals"]["std_score"]
            )

            clean_below_threshold = sum(
                1 for s in results["clean_signals"]["scores"] if s < threshold
            )
            attacked_below_threshold = sum(
                1 for s in results["attacked_signals"]["scores"] if s < threshold
            )

            results["detection_metrics"] = {
                "threshold": threshold,
                "true_positives": attacked_below_threshold,
                "false_positives": clean_below_threshold,
                "true_negatives": len(signals) - clean_below_threshold,
                "false_negatives": len(attacked_signals) - attacked_below_threshold,
            }

            # Calculate rates
            tp = results["detection_metrics"]["true_positives"]
            fp = results["detection_metrics"]["false_positives"]
            tn = results["detection_metrics"]["true_negatives"]
            fn = results["detection_metrics"]["false_negatives"]

            results["detection_metrics"]["accuracy"] = (tp + tn) / (tp + tn + fp + fn)
            results["detection_metrics"]["precision"] = tp / (tp + fp) if (tp + fp) > 0 else 0
            results["detection_metrics"]["recall"] = tp / (tp + fn) if (tp + fn) > 0 else 0

            f1_denom = results["detection_metrics"]["precision"] + results["detection_metrics"]["recall"]
            results["detection_metrics"]["f1_score"] = (
                2 * results["detection_metrics"]["precision"] * results["detection_metrics"]["recall"] / f1_denom
                if f1_denom > 0 else 0
            )

        return results


# Convenience function for checking MOABB availability
def is_moabb_available() -> bool:
    """Check if MOABB is installed and available."""
    return _MOABB_AVAILABLE


def get_moabb_version() -> Optional[str]:
    """Get MOABB version if installed."""
    if _MOABB_AVAILABLE and _moabb:
        return _moabb.__version__
    return None


# Dataset information exports
AVAILABLE_DATASETS = DatasetInfo.REGISTRY
SUPPORTED_PARADIGMS = [p.name for p in BCIParadigm]
