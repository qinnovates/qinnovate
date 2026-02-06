"""
Anomaly Detection Engine

Detects anomalies in neural signals using multiple techniques.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum, auto
import numpy as np
from collections import deque


class DetectionMethod(Enum):
    """Anomaly detection methods."""
    THRESHOLD = auto()      # Static threshold crossing
    STATISTICAL = auto()    # Statistical deviation (z-score)
    MOVING_AVERAGE = auto() # Deviation from moving average
    RATE_OF_CHANGE = auto() # Rapid change detection
    SPECTRAL = auto()       # Frequency domain anomalies
    PATTERN = auto()        # Known pattern matching
    ENSEMBLE = auto()       # Combination of methods


@dataclass
class DetectionResult:
    """
    Result from anomaly detection.

    Attributes:
        detected: Whether anomaly was detected
        confidence: Detection confidence (0-1)
        method: Detection method used
        anomaly_type: Type of anomaly detected
        metrics: Relevant metrics values
        details: Additional detection details
    """
    detected: bool
    confidence: float
    method: DetectionMethod
    anomaly_type: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        if self.detected:
            return f"ANOMALY [{self.anomaly_type}] conf={self.confidence:.2f} via {self.method.name}"
        return "No anomaly detected"


class AnomalyDetector:
    """
    Multi-method anomaly detector for neural signals.

    Implements various detection techniques to identify
    abnormal patterns that may indicate attacks or malfunctions.

    Example:
        >>> detector = AnomalyDetector()
        >>> detector.configure_threshold("coherence", low=0.3, high=0.95)
        >>>
        >>> metrics = {"coherence": 0.25, "spike_rate": 150.0}
        >>> result = detector.analyze(metrics)
        >>> if result.detected:
        ...     print(f"Anomaly: {result.anomaly_type}")
    """

    def __init__(
        self,
        history_size: int = 1000,
        baseline_window: int = 100,
    ):
        """
        Initialize the detector.

        Args:
            history_size: Number of samples to retain in history
            baseline_window: Window size for baseline calculations
        """
        self.history_size = history_size
        self.baseline_window = baseline_window

        # Metric histories
        self._history: Dict[str, deque] = {}

        # Thresholds
        self._thresholds: Dict[str, Dict[str, float]] = {}

        # Baselines (calculated from history)
        self._baselines: Dict[str, Dict[str, float]] = {}

        # Detection weights for ensemble
        self._method_weights: Dict[DetectionMethod, float] = {
            DetectionMethod.THRESHOLD: 1.0,
            DetectionMethod.STATISTICAL: 0.8,
            DetectionMethod.MOVING_AVERAGE: 0.6,
            DetectionMethod.RATE_OF_CHANGE: 0.7,
            DetectionMethod.SPECTRAL: 0.5,
        }

        # Default thresholds for common metrics
        self._configure_defaults()

    def _configure_defaults(self):
        """Configure default thresholds."""
        # Coherence thresholds
        self.configure_threshold("coherence", low=0.3, high=0.99)

        # Spike rate thresholds
        self.configure_threshold("spike_rate", low=1.0, high=300.0)

        # Signal amplitude
        self.configure_threshold("amplitude", low=-200.0, high=200.0)

        # Phase coherence
        self.configure_threshold("phase_coherence", low=0.2, high=1.0)

        # Signal-to-noise ratio
        self.configure_threshold("snr", low=5.0, high=100.0)

    def configure_threshold(
        self,
        metric: str,
        low: Optional[float] = None,
        high: Optional[float] = None,
        critical_low: Optional[float] = None,
        critical_high: Optional[float] = None,
    ):
        """
        Configure thresholds for a metric.

        Args:
            metric: Metric name
            low: Low warning threshold
            high: High warning threshold
            critical_low: Critical low threshold
            critical_high: Critical high threshold
        """
        self._thresholds[metric] = {
            "low": low,
            "high": high,
            "critical_low": critical_low or (low * 0.5 if low else None),
            "critical_high": critical_high or (high * 1.5 if high else None),
        }

    def update(self, metrics: Dict[str, float]):
        """
        Update metric history with new values.

        Args:
            metrics: Current metric values
        """
        for name, value in metrics.items():
            if name not in self._history:
                self._history[name] = deque(maxlen=self.history_size)
            self._history[name].append(value)

            # Update baseline if enough history
            if len(self._history[name]) >= self.baseline_window:
                self._update_baseline(name)

    def _update_baseline(self, metric: str):
        """Update baseline statistics for a metric."""
        recent = list(self._history[metric])[-self.baseline_window:]
        self._baselines[metric] = {
            "mean": np.mean(recent),
            "std": np.std(recent),
            "min": np.min(recent),
            "max": np.max(recent),
        }

    def analyze(
        self,
        metrics: Dict[str, float],
        methods: Optional[List[DetectionMethod]] = None,
    ) -> DetectionResult:
        """
        Analyze metrics for anomalies.

        Args:
            metrics: Current metric values
            methods: Detection methods to use (default: all)

        Returns:
            DetectionResult with findings
        """
        # Update history
        self.update(metrics)

        # Use all methods if not specified
        if methods is None:
            methods = [
                DetectionMethod.THRESHOLD,
                DetectionMethod.STATISTICAL,
                DetectionMethod.MOVING_AVERAGE,
                DetectionMethod.RATE_OF_CHANGE,
            ]

        # Run each detection method
        results = []
        for method in methods:
            result = self._run_detection(method, metrics)
            if result.detected:
                results.append(result)

        # No anomalies
        if not results:
            return DetectionResult(
                detected=False,
                confidence=0.0,
                method=DetectionMethod.ENSEMBLE,
            )

        # Single result
        if len(results) == 1:
            return results[0]

        # Multiple results - ensemble
        return self._ensemble_results(results, metrics)

    def _run_detection(
        self,
        method: DetectionMethod,
        metrics: Dict[str, float],
    ) -> DetectionResult:
        """Run a specific detection method."""
        if method == DetectionMethod.THRESHOLD:
            return self._detect_threshold(metrics)
        elif method == DetectionMethod.STATISTICAL:
            return self._detect_statistical(metrics)
        elif method == DetectionMethod.MOVING_AVERAGE:
            return self._detect_moving_average(metrics)
        elif method == DetectionMethod.RATE_OF_CHANGE:
            return self._detect_rate_of_change(metrics)
        elif method == DetectionMethod.SPECTRAL:
            return self._detect_spectral(metrics)

        return DetectionResult(
            detected=False,
            confidence=0.0,
            method=method,
        )

    def _detect_threshold(
        self,
        metrics: Dict[str, float],
    ) -> DetectionResult:
        """Detect anomalies using static thresholds."""
        anomalies = []

        for name, value in metrics.items():
            if name not in self._thresholds:
                continue

            thresh = self._thresholds[name]

            # Check critical thresholds first
            if thresh.get("critical_low") and value < thresh["critical_low"]:
                anomalies.append({
                    "metric": name,
                    "value": value,
                    "threshold": thresh["critical_low"],
                    "type": "critical_low",
                    "severity": 1.0,
                })
            elif thresh.get("critical_high") and value > thresh["critical_high"]:
                anomalies.append({
                    "metric": name,
                    "value": value,
                    "threshold": thresh["critical_high"],
                    "type": "critical_high",
                    "severity": 1.0,
                })
            elif thresh.get("low") and value < thresh["low"]:
                anomalies.append({
                    "metric": name,
                    "value": value,
                    "threshold": thresh["low"],
                    "type": "low",
                    "severity": 0.6,
                })
            elif thresh.get("high") and value > thresh["high"]:
                anomalies.append({
                    "metric": name,
                    "value": value,
                    "threshold": thresh["high"],
                    "type": "high",
                    "severity": 0.6,
                })

        if not anomalies:
            return DetectionResult(
                detected=False,
                confidence=0.0,
                method=DetectionMethod.THRESHOLD,
            )

        # Return most severe anomaly
        worst = max(anomalies, key=lambda x: x["severity"])
        return DetectionResult(
            detected=True,
            confidence=worst["severity"],
            method=DetectionMethod.THRESHOLD,
            anomaly_type=f"{worst['metric']}_{worst['type']}",
            metrics={a["metric"]: a["value"] for a in anomalies},
            details={"anomalies": anomalies},
        )

    def _detect_statistical(
        self,
        metrics: Dict[str, float],
    ) -> DetectionResult:
        """Detect anomalies using statistical deviation."""
        anomalies = []
        z_threshold = 3.0

        for name, value in metrics.items():
            if name not in self._baselines:
                continue

            baseline = self._baselines[name]
            if baseline["std"] == 0:
                continue

            z_score = abs(value - baseline["mean"]) / baseline["std"]

            if z_score > z_threshold:
                anomalies.append({
                    "metric": name,
                    "value": value,
                    "z_score": z_score,
                    "mean": baseline["mean"],
                    "std": baseline["std"],
                })

        if not anomalies:
            return DetectionResult(
                detected=False,
                confidence=0.0,
                method=DetectionMethod.STATISTICAL,
            )

        worst = max(anomalies, key=lambda x: x["z_score"])
        # Confidence based on z-score (3 = 0.5, 6 = 1.0)
        confidence = min((worst["z_score"] - z_threshold) / z_threshold + 0.5, 1.0)

        return DetectionResult(
            detected=True,
            confidence=confidence,
            method=DetectionMethod.STATISTICAL,
            anomaly_type="statistical_deviation",
            metrics={a["metric"]: a["value"] for a in anomalies},
            details={"anomalies": anomalies, "z_threshold": z_threshold},
        )

    def _detect_moving_average(
        self,
        metrics: Dict[str, float],
    ) -> DetectionResult:
        """Detect deviation from moving average."""
        anomalies = []
        deviation_threshold = 2.0  # Standard deviations

        for name, value in metrics.items():
            if name not in self._history or len(self._history[name]) < 10:
                continue

            recent = list(self._history[name])[-10:]
            ma = np.mean(recent[:-1])  # Exclude current
            ma_std = np.std(recent[:-1])

            if ma_std == 0:
                continue

            deviation = abs(value - ma) / ma_std

            if deviation > deviation_threshold:
                anomalies.append({
                    "metric": name,
                    "value": value,
                    "moving_average": ma,
                    "deviation": deviation,
                })

        if not anomalies:
            return DetectionResult(
                detected=False,
                confidence=0.0,
                method=DetectionMethod.MOVING_AVERAGE,
            )

        worst = max(anomalies, key=lambda x: x["deviation"])
        confidence = min(worst["deviation"] / (deviation_threshold * 2), 1.0)

        return DetectionResult(
            detected=True,
            confidence=confidence,
            method=DetectionMethod.MOVING_AVERAGE,
            anomaly_type="moving_average_deviation",
            metrics={a["metric"]: a["value"] for a in anomalies},
            details={"anomalies": anomalies},
        )

    def _detect_rate_of_change(
        self,
        metrics: Dict[str, float],
    ) -> DetectionResult:
        """Detect rapid changes in metrics."""
        anomalies = []
        change_threshold = 0.5  # 50% change

        for name, value in metrics.items():
            if name not in self._history or len(self._history[name]) < 2:
                continue

            prev = self._history[name][-2]
            if prev == 0:
                continue

            rate_of_change = abs(value - prev) / abs(prev)

            if rate_of_change > change_threshold:
                anomalies.append({
                    "metric": name,
                    "current": value,
                    "previous": prev,
                    "rate_of_change": rate_of_change,
                })

        if not anomalies:
            return DetectionResult(
                detected=False,
                confidence=0.0,
                method=DetectionMethod.RATE_OF_CHANGE,
            )

        worst = max(anomalies, key=lambda x: x["rate_of_change"])
        confidence = min(worst["rate_of_change"] / change_threshold * 0.5, 1.0)

        return DetectionResult(
            detected=True,
            confidence=confidence,
            method=DetectionMethod.RATE_OF_CHANGE,
            anomaly_type="rapid_change",
            metrics={a["metric"]: a["current"] for a in anomalies},
            details={"anomalies": anomalies},
        )

    def _detect_spectral(
        self,
        metrics: Dict[str, float],
    ) -> DetectionResult:
        """Detect spectral anomalies (frequency domain)."""
        # Check for spectral metrics
        spectral_metrics = ["power_alpha", "power_beta", "power_gamma", "power_theta"]
        available = {k: v for k, v in metrics.items() if k in spectral_metrics}

        if len(available) < 2:
            return DetectionResult(
                detected=False,
                confidence=0.0,
                method=DetectionMethod.SPECTRAL,
            )

        # Check for abnormal power distribution
        total_power = sum(available.values())
        if total_power == 0:
            return DetectionResult(
                detected=False,
                confidence=0.0,
                method=DetectionMethod.SPECTRAL,
            )

        # Normalize
        normalized = {k: v / total_power for k, v in available.items()}

        # Check for abnormal dominance (one band > 80%)
        max_band = max(normalized.items(), key=lambda x: x[1])
        if max_band[1] > 0.8:
            return DetectionResult(
                detected=True,
                confidence=max_band[1] - 0.5,
                method=DetectionMethod.SPECTRAL,
                anomaly_type=f"{max_band[0]}_dominance",
                metrics=available,
                details={"normalized_power": normalized, "dominant_band": max_band[0]},
            )

        return DetectionResult(
            detected=False,
            confidence=0.0,
            method=DetectionMethod.SPECTRAL,
        )

    def _ensemble_results(
        self,
        results: List[DetectionResult],
        metrics: Dict[str, float],
    ) -> DetectionResult:
        """Combine multiple detection results."""
        # Weighted average of confidences
        total_weight = 0.0
        weighted_confidence = 0.0

        for result in results:
            weight = self._method_weights.get(result.method, 0.5)
            weighted_confidence += result.confidence * weight
            total_weight += weight

        ensemble_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.0

        # Collect all anomaly types
        anomaly_types = [r.anomaly_type for r in results if r.anomaly_type]

        return DetectionResult(
            detected=True,
            confidence=min(ensemble_confidence * 1.2, 1.0),  # Boost for multiple detections
            method=DetectionMethod.ENSEMBLE,
            anomaly_type=", ".join(anomaly_types) if anomaly_types else "multiple_anomalies",
            metrics=metrics,
            details={
                "individual_results": [
                    {
                        "method": r.method.name,
                        "confidence": r.confidence,
                        "type": r.anomaly_type,
                    }
                    for r in results
                ],
                "methods_triggered": len(results),
            },
        )

    def get_baseline(self, metric: str) -> Optional[Dict[str, float]]:
        """Get baseline statistics for a metric."""
        return self._baselines.get(metric)

    def get_history(self, metric: str, count: int = 100) -> List[float]:
        """Get recent history for a metric."""
        if metric not in self._history:
            return []
        return list(self._history[metric])[-count:]

    def reset_baseline(self, metric: Optional[str] = None):
        """Reset baseline for metric(s)."""
        if metric:
            self._baselines.pop(metric, None)
        else:
            self._baselines.clear()

    def reset_history(self, metric: Optional[str] = None):
        """Reset history for metric(s)."""
        if metric:
            self._history.pop(metric, None)
            self._baselines.pop(metric, None)
        else:
            self._history.clear()
            self._baselines.clear()
