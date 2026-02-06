"""
Neural Firewall Module

Implements signal filtering based on coherence scores at the Neural Gateway (L8).
Provides zero-trust security validation for brain-computer interface signals.

===============================================================================
IMPORTANT: FOR NON-TECHNICAL COLLABORATORS
===============================================================================
This module acts like a security guard for neural signals.

WHAT IT DOES:
- Takes a signal (timing data + amplitudes + whether source is verified)
- Calculates a coherence/trust score
- Decides: ACCEPT (let it through), ACCEPT_FLAG (let through but log), or REJECT

BIDIRECTIONAL BCI SUPPORT:
- For READ operations: validates incoming neural signals from the brain
- For WRITE/STIMULATION operations: validates outgoing commands to the brain
- Stimulation commands have ADDITIONAL safety constraints (amplitude, frequency limits)

REAL-WORLD ANALOGY:
Like a firewall on your computer that blocks suspicious network traffic, this
would block suspicious neural signals before they reach the brain or before
fake brain signals are processed by a computer.

THIS IS A SIMULATION/FRAMEWORK:
- It does NOT connect to any hardware
- The "signals" are data YOU provide (from a real BCI device, if you have one)
- It demonstrates the logic that WOULD be used in a real security system

DECISION MATRIX FOR READ (how it decides):
┌────────────────┬──────────────┬─────────────────────┐
│ Coherence Score│ Authenticated│ Decision            │
├────────────────┼──────────────┼─────────────────────┤
│ High (>0.6)    │ Yes          │ ACCEPT              │
│ High (>0.6)    │ No           │ REJECT + alert      │
│ Medium (0.3-0.6│ Yes          │ ACCEPT + flag       │
│ Medium         │ No           │ REJECT + alert      │
│ Low (<0.3)     │ Any          │ REJECT + critical   │
└────────────────┴──────────────┴─────────────────────┘

DECISION MATRIX FOR STIMULATION (stricter):
┌────────────────────┬──────────────┬─────────────────────┐
│ Safety Check       │ Pass         │ Decision            │
├────────────────────┼──────────────┼─────────────────────┤
│ Amplitude bounds   │ No           │ REJECT + critical   │
│ Frequency bounds   │ No           │ REJECT + critical   │
│ Rate limit         │ No           │ REJECT + alert      │
│ Target region      │ Unauthorized │ REJECT + critical   │
│ All checks pass    │ Yes          │ ACCEPT              │
└────────────────────┴──────────────┴─────────────────────┘
===============================================================================

Reference: TechDoc-Neural_Firewall_Architecture.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional, Callable, Dict, Any, Set

from .coherence import CoherenceMetric, VarianceComponents


class Decision(Enum):
    """Firewall decision outcomes."""
    ACCEPT = auto()
    ACCEPT_FLAG = auto()
    REJECT = auto()


class AlertLevel(Enum):
    """Alert severity levels."""
    NONE = auto()
    ROUTINE = auto()
    ENHANCED = auto()
    ALERT = auto()
    CRITICAL = auto()


@dataclass
class Signal:
    """
    Represents a signal to be validated by the firewall.

    Attributes:
        arrival_times: Timestamps of signal events (seconds)
        amplitudes: Signal amplitudes at each event
        authenticated: Whether signal has valid authentication
        source_id: Optional identifier for signal source
        metadata: Additional signal metadata
    """
    arrival_times: List[float]
    amplitudes: List[float]
    authenticated: bool = False
    source_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class FlowDirection(Enum):
    """Direction of data flow through the Neural Gateway (L8)."""
    READ = auto()       # Brain → Computer (recording/sensing)
    WRITE = auto()      # Computer → Brain (stimulation)
    BIDIRECTIONAL = auto()  # Both directions (closed-loop BCI)


@dataclass
class FilterResult:
    """
    Result of firewall signal filtering.

    Attributes:
        decision: Accept, accept with flag, or reject
        coherence: Calculated coherence score
        variances: Individual variance components
        alert_level: Severity of logging/alerting
        reason: Human-readable explanation
        timestamp: When the decision was made
    """
    decision: Decision
    coherence: float
    variances: VarianceComponents
    alert_level: AlertLevel
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def accepted(self) -> bool:
        """Whether the signal was accepted (with or without flag)."""
        return self.decision in (Decision.ACCEPT, Decision.ACCEPT_FLAG)

    @property
    def rejected(self) -> bool:
        """Whether the signal was rejected."""
        return self.decision == Decision.REJECT

    @property
    def flagged(self) -> bool:
        """Whether the signal was flagged for review."""
        return self.decision == Decision.ACCEPT_FLAG


@dataclass
class StimulationCommand:
    """
    Represents a stimulation command to be validated by the firewall.

    This is used for WRITE/stimulation operations in bidirectional BCIs.
    All stimulation commands must pass safety validation before being
    delivered to neural tissue.

    Attributes:
        target_region: Brain region identifier (e.g., "M1", "PFC", "HIPP")
        amplitude_uA: Stimulation amplitude in microamperes
        frequency_Hz: Stimulation frequency in Hertz
        pulse_width_us: Pulse width in microseconds
        duration_ms: Total stimulation duration in milliseconds
        waveform: Waveform type ("biphasic", "monophasic", "burst")
        authenticated: Whether command has valid authentication
        source_id: Identifier for command source
        metadata: Additional command metadata
    """
    target_region: str
    amplitude_uA: float
    frequency_Hz: float
    pulse_width_us: float = 200.0
    duration_ms: float = 1000.0
    waveform: str = "biphasic"
    authenticated: bool = False
    source_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def charge_per_phase_nC(self) -> float:
        """Calculate charge per phase in nanocoulombs."""
        # Q = I * t, where I is in uA and t is in us
        # Result is in nC (uA * us = nC)
        return self.amplitude_uA * self.pulse_width_us / 1000.0


@dataclass
class StimulationResult:
    """
    Result of stimulation command validation.

    Attributes:
        decision: Accept or reject
        alert_level: Severity of logging/alerting
        reason: Human-readable explanation
        safety_checks: Dict of individual safety check results
        timestamp: When the decision was made
    """
    decision: Decision
    alert_level: AlertLevel
    reason: str
    safety_checks: Dict[str, bool] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def accepted(self) -> bool:
        """Whether the stimulation was accepted."""
        return self.decision == Decision.ACCEPT

    @property
    def rejected(self) -> bool:
        """Whether the stimulation was rejected."""
        return self.decision == Decision.REJECT

    @property
    def all_checks_passed(self) -> bool:
        """Whether all safety checks passed."""
        return all(self.safety_checks.values())


class NeuralFirewall:
    """
    Zero-trust neural signal firewall operating at ONI Layer 8.

    Validates signals using coherence metrics and authentication status.
    Implements the defense-in-depth principle with multiple validation layers.

    Example:
        >>> firewall = NeuralFirewall(threshold_high=0.6, threshold_low=0.3)
        >>> signal = Signal(
        ...     arrival_times=[0.0, 0.025, 0.050],
        ...     amplitudes=[100, 98, 102],
        ...     authenticated=True
        ... )
        >>> result = firewall.filter(signal)
        >>> print(f"Decision: {result.decision.name}, Cs={result.coherence:.3f}")
    """

    # Default safety bounds for stimulation (conservative, based on literature)
    # Reference: Shannon (1992), Merrill et al. (2005) - charge density limits
    DEFAULT_STIM_AMPLITUDE_BOUNDS = (0.0, 5000.0)  # 0-5 mA (5000 uA)
    DEFAULT_STIM_FREQUENCY_BOUNDS = (0.1, 500.0)   # 0.1-500 Hz
    DEFAULT_STIM_PULSE_WIDTH_BOUNDS = (50.0, 1000.0)  # 50-1000 us
    DEFAULT_CHARGE_DENSITY_LIMIT = 30.0  # uC/cm^2/phase (Shannon limit k=1.5)

    def __init__(
        self,
        threshold_high: float = 0.6,
        threshold_low: float = 0.3,
        reference_freq: float = 40.0,
        amplitude_bounds: Optional[tuple] = None,
        rate_limit: Optional[int] = None,
        # Bidirectional BCI settings
        stim_amplitude_bounds: Optional[tuple] = None,
        stim_frequency_bounds: Optional[tuple] = None,
        stim_pulse_width_bounds: Optional[tuple] = None,
        charge_density_limit: Optional[float] = None,
        authorized_regions: Optional[Set[str]] = None,
        stim_rate_limit: Optional[int] = None,
    ):
        """
        Initialize the neural firewall.

        Args:
            threshold_high: Coherence threshold for unconditional accept (default: 0.6)
            threshold_low: Coherence threshold below which to reject (default: 0.3)
            reference_freq: Reference oscillation frequency for phase calculation
            amplitude_bounds: Optional (min, max) amplitude bounds for read signals
            rate_limit: Optional maximum read signals per second

            Bidirectional BCI settings (for stimulation/write operations):
            stim_amplitude_bounds: (min, max) stimulation amplitude in uA
            stim_frequency_bounds: (min, max) stimulation frequency in Hz
            stim_pulse_width_bounds: (min, max) pulse width in microseconds
            charge_density_limit: Maximum charge density in uC/cm^2/phase
            authorized_regions: Set of authorized brain region identifiers
            stim_rate_limit: Maximum stimulation commands per second
        """
        if threshold_low >= threshold_high:
            raise ValueError("threshold_low must be less than threshold_high")
        if not (0 < threshold_low < 1 and 0 < threshold_high < 1):
            raise ValueError("Thresholds must be between 0 and 1")

        # Read (recording) settings
        self.threshold_high = threshold_high
        self.threshold_low = threshold_low
        self.amplitude_bounds = amplitude_bounds
        self.rate_limit = rate_limit

        # Write (stimulation) settings - use defaults if not provided
        self.stim_amplitude_bounds = stim_amplitude_bounds or self.DEFAULT_STIM_AMPLITUDE_BOUNDS
        self.stim_frequency_bounds = stim_frequency_bounds or self.DEFAULT_STIM_FREQUENCY_BOUNDS
        self.stim_pulse_width_bounds = stim_pulse_width_bounds or self.DEFAULT_STIM_PULSE_WIDTH_BOUNDS
        self.charge_density_limit = charge_density_limit or self.DEFAULT_CHARGE_DENSITY_LIMIT
        self.authorized_regions = authorized_regions or set()  # Empty = no regions authorized
        self.stim_rate_limit = stim_rate_limit

        self._coherence_metric = CoherenceMetric(reference_freq=reference_freq)
        self._signal_log: List[FilterResult] = []
        self._stimulation_log: List[StimulationResult] = []
        self._callbacks: Dict[AlertLevel, List[Callable]] = {
            level: [] for level in AlertLevel
        }
        self._last_stim_time: Optional[datetime] = None
        self._stim_count_window: List[datetime] = []

    def filter(self, signal: Signal) -> FilterResult:
        """
        Filter a signal through the firewall.

        Applies coherence validation and authentication checks to determine
        whether to accept, flag, or reject the signal.

        Args:
            signal: Signal to validate

        Returns:
            FilterResult with decision, coherence score, and alert level
        """
        # Check hardware bounds first (fast path rejection)
        if self.amplitude_bounds:
            min_amp, max_amp = self.amplitude_bounds
            if any(a < min_amp or a > max_amp for a in signal.amplitudes):
                result = FilterResult(
                    decision=Decision.REJECT,
                    coherence=0.0,
                    variances=VarianceComponents(phase=0, transport=0, gain=float('inf')),
                    alert_level=AlertLevel.CRITICAL,
                    reason=f"Amplitude outside hardware bounds [{min_amp}, {max_amp}]",
                )
                self._log_and_alert(result)
                return result

        # Calculate coherence
        variances = self._coherence_metric.calculate_variances(
            signal.arrival_times,
            signal.amplitudes,
        )
        coherence = self._coherence_metric.calculate(
            signal.arrival_times,
            signal.amplitudes,
        )

        # Apply decision matrix
        decision, alert_level, reason = self._apply_decision_matrix(
            coherence, signal.authenticated
        )

        result = FilterResult(
            decision=decision,
            coherence=coherence,
            variances=variances,
            alert_level=alert_level,
            reason=reason,
        )

        self._log_and_alert(result)
        return result

    def _apply_decision_matrix(
        self,
        coherence: float,
        authenticated: bool,
    ) -> tuple:
        """
        Apply the firewall decision matrix.

        Returns:
            Tuple of (Decision, AlertLevel, reason_string)
        """
        if coherence > self.threshold_high:
            # High coherence
            if authenticated:
                return (
                    Decision.ACCEPT,
                    AlertLevel.ROUTINE,
                    f"High coherence ({coherence:.3f}) with valid authentication",
                )
            else:
                return (
                    Decision.REJECT,
                    AlertLevel.ALERT,
                    f"High coherence ({coherence:.3f}) but missing authentication",
                )

        elif coherence > self.threshold_low:
            # Medium coherence
            if authenticated:
                return (
                    Decision.ACCEPT_FLAG,
                    AlertLevel.ENHANCED,
                    f"Medium coherence ({coherence:.3f}), flagged for review",
                )
            else:
                return (
                    Decision.REJECT,
                    AlertLevel.ALERT,
                    f"Medium coherence ({coherence:.3f}) without authentication",
                )

        else:
            # Low coherence - reject regardless of authentication
            return (
                Decision.REJECT,
                AlertLevel.CRITICAL,
                f"Low coherence ({coherence:.3f}), signal incoherent",
            )

    def _log_and_alert(self, result: FilterResult):
        """Log the result and trigger any registered callbacks."""
        self._signal_log.append(result)

        # Trigger callbacks for this alert level and above
        for level in AlertLevel:
            if level.value >= result.alert_level.value:
                for callback in self._callbacks.get(level, []):
                    callback(result)

    def register_callback(
        self,
        alert_level: AlertLevel,
        callback: Callable[[FilterResult], None],
    ):
        """
        Register a callback for a specific alert level.

        Callbacks are triggered when a signal generates an alert at or above
        the specified level.

        Args:
            alert_level: Minimum alert level to trigger callback
            callback: Function to call with FilterResult
        """
        self._callbacks[alert_level].append(callback)

    def filter_batch(self, signals: List[Signal]) -> List[FilterResult]:
        """
        Filter multiple signals.

        Args:
            signals: List of signals to validate

        Returns:
            List of FilterResults in same order
        """
        return [self.filter(signal) for signal in signals]

    # =========================================================================
    # Bidirectional BCI: Stimulation Filtering
    # =========================================================================

    def filter_stimulation(self, command: StimulationCommand) -> StimulationResult:
        """
        Filter a stimulation command through the firewall.

        Applies safety validation to ensure stimulation parameters are within
        safe bounds before allowing delivery to neural tissue. This is the
        WRITE direction of the bidirectional BCI firewall.

        Args:
            command: Stimulation command to validate

        Returns:
            StimulationResult with decision and safety check details

        Safety Checks:
            1. Authentication - command must be authenticated
            2. Target region - must be in authorized regions list
            3. Amplitude bounds - within configured uA limits
            4. Frequency bounds - within configured Hz limits
            5. Pulse width bounds - within configured us limits
            6. Charge density - below Shannon limit
            7. Rate limit - not exceeding commands per second
        """
        safety_checks = {}
        failed_checks = []

        # 1. Authentication check
        safety_checks["authenticated"] = command.authenticated
        if not command.authenticated:
            failed_checks.append("missing authentication")

        # 2. Target region authorization
        if self.authorized_regions:
            safety_checks["region_authorized"] = command.target_region in self.authorized_regions
            if not safety_checks["region_authorized"]:
                failed_checks.append(f"unauthorized region: {command.target_region}")
        else:
            # If no regions configured, reject all (fail-closed)
            safety_checks["region_authorized"] = False
            failed_checks.append("no authorized regions configured")

        # 3. Amplitude bounds
        min_amp, max_amp = self.stim_amplitude_bounds
        safety_checks["amplitude_in_bounds"] = min_amp <= command.amplitude_uA <= max_amp
        if not safety_checks["amplitude_in_bounds"]:
            failed_checks.append(
                f"amplitude {command.amplitude_uA} uA outside bounds [{min_amp}, {max_amp}]"
            )

        # 4. Frequency bounds
        min_freq, max_freq = self.stim_frequency_bounds
        safety_checks["frequency_in_bounds"] = min_freq <= command.frequency_Hz <= max_freq
        if not safety_checks["frequency_in_bounds"]:
            failed_checks.append(
                f"frequency {command.frequency_Hz} Hz outside bounds [{min_freq}, {max_freq}]"
            )

        # 5. Pulse width bounds
        min_pw, max_pw = self.stim_pulse_width_bounds
        safety_checks["pulse_width_in_bounds"] = min_pw <= command.pulse_width_us <= max_pw
        if not safety_checks["pulse_width_in_bounds"]:
            failed_checks.append(
                f"pulse width {command.pulse_width_us} us outside bounds [{min_pw}, {max_pw}]"
            )

        # 6. Charge density check (simplified - assumes 1 cm^2 electrode)
        # Real implementation would use actual electrode geometry
        charge_per_phase = command.charge_per_phase_nC / 1000.0  # Convert to uC
        safety_checks["charge_density_safe"] = charge_per_phase <= self.charge_density_limit
        if not safety_checks["charge_density_safe"]:
            failed_checks.append(
                f"charge density {charge_per_phase:.2f} uC exceeds limit {self.charge_density_limit}"
            )

        # 7. Rate limit check
        if self.stim_rate_limit:
            now = datetime.now()
            # Clean old entries (older than 1 second)
            self._stim_count_window = [
                t for t in self._stim_count_window
                if (now - t).total_seconds() < 1.0
            ]
            safety_checks["rate_limit_ok"] = len(self._stim_count_window) < self.stim_rate_limit
            if not safety_checks["rate_limit_ok"]:
                failed_checks.append(
                    f"rate limit exceeded: {len(self._stim_count_window)} >= {self.stim_rate_limit}/s"
                )
            # Add current command to window
            self._stim_count_window.append(now)
        else:
            safety_checks["rate_limit_ok"] = True

        # Determine result
        if not failed_checks:
            result = StimulationResult(
                decision=Decision.ACCEPT,
                alert_level=AlertLevel.ROUTINE,
                reason="All safety checks passed",
                safety_checks=safety_checks,
            )
        else:
            # Determine severity based on which checks failed
            if any(c in str(failed_checks) for c in ["unauthorized region", "charge density", "amplitude"]):
                alert_level = AlertLevel.CRITICAL
            elif "authentication" in str(failed_checks):
                alert_level = AlertLevel.ALERT
            else:
                alert_level = AlertLevel.ENHANCED

            result = StimulationResult(
                decision=Decision.REJECT,
                alert_level=alert_level,
                reason=f"Safety check(s) failed: {'; '.join(failed_checks)}",
                safety_checks=safety_checks,
            )

        self._log_stimulation_and_alert(result)
        return result

    def filter_stimulation_batch(
        self,
        commands: List[StimulationCommand]
    ) -> List[StimulationResult]:
        """
        Filter multiple stimulation commands.

        Args:
            commands: List of stimulation commands to validate

        Returns:
            List of StimulationResults in same order
        """
        return [self.filter_stimulation(cmd) for cmd in commands]

    def authorize_region(self, region: str):
        """
        Add a region to the authorized stimulation targets.

        Args:
            region: Brain region identifier (e.g., "M1", "PFC")
        """
        self.authorized_regions.add(region)

    def revoke_region(self, region: str):
        """
        Remove a region from authorized stimulation targets.

        Args:
            region: Brain region identifier to revoke
        """
        self.authorized_regions.discard(region)

    def _log_stimulation_and_alert(self, result: StimulationResult):
        """Log the stimulation result and trigger callbacks."""
        self._stimulation_log.append(result)
        self._last_stim_time = result.timestamp

        # Trigger callbacks for this alert level and above
        for level in AlertLevel:
            if level.value >= result.alert_level.value:
                for callback in self._callbacks.get(level, []):
                    callback(result)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get firewall statistics for both read and stimulation operations.

        Returns:
            Dict with accept/reject counts, average coherence, stimulation stats, etc.
        """
        stats = {
            "read": self._get_read_stats(),
            "stimulation": self._get_stimulation_stats(),
            "flow_direction": self._determine_flow_direction(),
        }
        return stats

    def _get_read_stats(self) -> Dict[str, Any]:
        """Get statistics for read (recording) operations."""
        if not self._signal_log:
            return {
                "total": 0,
                "accepted": 0,
                "rejected": 0,
                "flagged": 0,
                "avg_coherence": 0.0,
            }

        accepted = sum(1 for r in self._signal_log if r.accepted)
        rejected = sum(1 for r in self._signal_log if r.rejected)
        flagged = sum(1 for r in self._signal_log if r.flagged)
        avg_coherence = sum(r.coherence for r in self._signal_log) / len(self._signal_log)

        return {
            "total": len(self._signal_log),
            "accepted": accepted,
            "rejected": rejected,
            "flagged": flagged,
            "accept_rate": accepted / len(self._signal_log),
            "reject_rate": rejected / len(self._signal_log),
            "avg_coherence": avg_coherence,
            "alerts": {
                level.name: sum(1 for r in self._signal_log if r.alert_level == level)
                for level in AlertLevel
            },
        }

    def _get_stimulation_stats(self) -> Dict[str, Any]:
        """Get statistics for stimulation (write) operations."""
        if not self._stimulation_log:
            return {
                "total": 0,
                "accepted": 0,
                "rejected": 0,
                "authorized_regions": list(self.authorized_regions),
            }

        accepted = sum(1 for r in self._stimulation_log if r.accepted)
        rejected = sum(1 for r in self._stimulation_log if r.rejected)

        # Count failed checks by type
        failed_check_counts = {}
        for result in self._stimulation_log:
            for check_name, passed in result.safety_checks.items():
                if not passed:
                    failed_check_counts[check_name] = failed_check_counts.get(check_name, 0) + 1

        return {
            "total": len(self._stimulation_log),
            "accepted": accepted,
            "rejected": rejected,
            "accept_rate": accepted / len(self._stimulation_log) if self._stimulation_log else 0,
            "reject_rate": rejected / len(self._stimulation_log) if self._stimulation_log else 0,
            "authorized_regions": list(self.authorized_regions),
            "failed_check_counts": failed_check_counts,
            "alerts": {
                level.name: sum(1 for r in self._stimulation_log if r.alert_level == level)
                for level in AlertLevel
            },
        }

    def _determine_flow_direction(self) -> str:
        """Determine the predominant flow direction based on activity."""
        has_read = len(self._signal_log) > 0
        has_stim = len(self._stimulation_log) > 0

        if has_read and has_stim:
            return FlowDirection.BIDIRECTIONAL.name
        elif has_stim:
            return FlowDirection.WRITE.name
        elif has_read:
            return FlowDirection.READ.name
        else:
            return "INACTIVE"

    def clear_log(self):
        """Clear all logs (read and stimulation)."""
        self._signal_log.clear()
        self._stimulation_log.clear()
        self._stim_count_window.clear()

    def clear_read_log(self):
        """Clear only the read (recording) signal log."""
        self._signal_log.clear()

    def clear_stimulation_log(self):
        """Clear only the stimulation log."""
        self._stimulation_log.clear()
        self._stim_count_window.clear()

    @property
    def log(self) -> List[FilterResult]:
        """Access the read signal log (read-only copy)."""
        return list(self._signal_log)

    @property
    def stimulation_log(self) -> List[StimulationResult]:
        """Access the stimulation log (read-only copy)."""
        return list(self._stimulation_log)
