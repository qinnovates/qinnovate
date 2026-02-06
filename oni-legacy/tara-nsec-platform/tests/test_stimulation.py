"""
Stimulation Filtering Tests

Tests for bidirectional BCI security at the Neural Gateway (L8).
Validates stimulation command safety checks including amplitude bounds,
frequency limits, charge density, and region authorization.

These tests verify:
1. Stimulation command validation
2. Safety bounds enforcement
3. Region authorization
4. Rate limiting
5. Charge density calculations
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from tara_mvp.core.firewall import (
    NeuralFirewall,
    StimulationCommand,
    StimulationResult,
    FlowDirection,
    Decision,
    AlertLevel,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def basic_firewall():
    """Create a basic firewall with default settings."""
    return NeuralFirewall()


@pytest.fixture
def configured_firewall():
    """Create a firewall configured for stimulation with authorized regions."""
    return NeuralFirewall(
        stim_amplitude_bounds=(0.0, 3000.0),  # 0-3 mA
        stim_frequency_bounds=(1.0, 200.0),   # 1-200 Hz
        stim_pulse_width_bounds=(100.0, 500.0),  # 100-500 us
        charge_density_limit=25.0,  # 25 uC/cm^2/phase
        authorized_regions={"M1", "S1", "PMC"},
        stim_rate_limit=10,  # 10 commands per second
    )


@pytest.fixture
def valid_stim_command():
    """Create a valid stimulation command."""
    return StimulationCommand(
        target_region="M1",
        amplitude_uA=1000.0,  # 1 mA
        frequency_Hz=100.0,
        pulse_width_us=200.0,
        duration_ms=1000.0,
        waveform="biphasic",
        authenticated=True,
        source_id="clinical_device_001",
    )


@pytest.fixture
def unauthorized_stim_command():
    """Create an unauthenticated stimulation command."""
    return StimulationCommand(
        target_region="M1",
        amplitude_uA=1000.0,
        frequency_Hz=100.0,
        pulse_width_us=200.0,
        authenticated=False,  # Not authenticated
    )


# =============================================================================
# StimulationCommand Tests
# =============================================================================

class TestStimulationCommand:
    """Tests for StimulationCommand dataclass."""

    def test_charge_per_phase_calculation(self):
        """Test charge per phase is calculated correctly."""
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=1000.0,  # 1 mA
            frequency_Hz=100.0,
            pulse_width_us=200.0,  # 200 us
        )
        # Q = I * t = 1000 uA * 200 us = 200,000 uA*us = 200 nC
        expected_nC = 1000.0 * 200.0 / 1000.0  # 200 nC
        assert cmd.charge_per_phase_nC == pytest.approx(expected_nC)

    def test_default_waveform(self):
        """Test default waveform is biphasic."""
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=100.0,
            frequency_Hz=50.0,
        )
        assert cmd.waveform == "biphasic"

    def test_metadata_storage(self):
        """Test metadata is stored correctly."""
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=100.0,
            frequency_Hz=50.0,
            metadata={"trial": 1, "condition": "active"}
        )
        assert cmd.metadata["trial"] == 1
        assert cmd.metadata["condition"] == "active"


# =============================================================================
# Basic Stimulation Filtering Tests
# =============================================================================

class TestStimulationFiltering:
    """Tests for basic stimulation filtering functionality."""

    def test_reject_when_no_regions_authorized(self, basic_firewall, valid_stim_command):
        """Test rejection when no regions are authorized (fail-closed)."""
        result = basic_firewall.filter_stimulation(valid_stim_command)
        assert result.rejected
        assert not result.safety_checks.get("region_authorized", True)
        assert "no authorized regions" in result.reason.lower()

    def test_accept_valid_command(self, configured_firewall, valid_stim_command):
        """Test acceptance of valid authenticated command to authorized region."""
        result = configured_firewall.filter_stimulation(valid_stim_command)
        assert result.accepted
        assert result.all_checks_passed
        assert result.alert_level == AlertLevel.ROUTINE

    def test_reject_unauthenticated(self, configured_firewall, unauthorized_stim_command):
        """Test rejection of unauthenticated command."""
        result = configured_firewall.filter_stimulation(unauthorized_stim_command)
        assert result.rejected
        assert not result.safety_checks["authenticated"]
        assert "authentication" in result.reason.lower()

    def test_reject_unauthorized_region(self, configured_firewall):
        """Test rejection of command targeting unauthorized region."""
        cmd = StimulationCommand(
            target_region="PFC",  # Not in authorized set
            amplitude_uA=1000.0,
            frequency_Hz=100.0,
            pulse_width_us=200.0,
            authenticated=True,
        )
        result = configured_firewall.filter_stimulation(cmd)
        assert result.rejected
        assert not result.safety_checks["region_authorized"]
        assert "unauthorized region" in result.reason.lower()


# =============================================================================
# Safety Bounds Tests
# =============================================================================

class TestSafetyBounds:
    """Tests for amplitude, frequency, and pulse width safety bounds."""

    def test_amplitude_too_high(self, configured_firewall):
        """Test rejection when amplitude exceeds upper bound."""
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=5000.0,  # 5 mA - above 3 mA limit
            frequency_Hz=100.0,
            pulse_width_us=200.0,
            authenticated=True,
        )
        result = configured_firewall.filter_stimulation(cmd)
        assert result.rejected
        assert not result.safety_checks["amplitude_in_bounds"]
        assert result.alert_level == AlertLevel.CRITICAL

    def test_amplitude_negative(self, configured_firewall):
        """Test rejection of negative amplitude."""
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=-100.0,  # Negative
            frequency_Hz=100.0,
            pulse_width_us=200.0,
            authenticated=True,
        )
        result = configured_firewall.filter_stimulation(cmd)
        assert result.rejected
        assert not result.safety_checks["amplitude_in_bounds"]

    def test_frequency_too_high(self, configured_firewall):
        """Test rejection when frequency exceeds upper bound."""
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=1000.0,
            frequency_Hz=300.0,  # Above 200 Hz limit
            pulse_width_us=200.0,
            authenticated=True,
        )
        result = configured_firewall.filter_stimulation(cmd)
        assert result.rejected
        assert not result.safety_checks["frequency_in_bounds"]

    def test_frequency_too_low(self, configured_firewall):
        """Test rejection when frequency below lower bound."""
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=1000.0,
            frequency_Hz=0.05,  # Below 1 Hz limit
            pulse_width_us=200.0,
            authenticated=True,
        )
        result = configured_firewall.filter_stimulation(cmd)
        assert result.rejected
        assert not result.safety_checks["frequency_in_bounds"]

    def test_pulse_width_too_long(self, configured_firewall):
        """Test rejection when pulse width exceeds upper bound."""
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=1000.0,
            frequency_Hz=100.0,
            pulse_width_us=800.0,  # Above 500 us limit
            authenticated=True,
        )
        result = configured_firewall.filter_stimulation(cmd)
        assert result.rejected
        assert not result.safety_checks["pulse_width_in_bounds"]

    def test_pulse_width_too_short(self, configured_firewall):
        """Test rejection when pulse width below lower bound."""
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=1000.0,
            frequency_Hz=100.0,
            pulse_width_us=50.0,  # Below 100 us limit
            authenticated=True,
        )
        result = configured_firewall.filter_stimulation(cmd)
        assert result.rejected
        assert not result.safety_checks["pulse_width_in_bounds"]


# =============================================================================
# Charge Density Tests
# =============================================================================

class TestChargeDensity:
    """Tests for charge density safety calculations."""

    def test_charge_density_exceeded(self, configured_firewall):
        """Test rejection when charge density exceeds limit."""
        # High amplitude + long pulse = high charge
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=2500.0,  # 2.5 mA
            frequency_Hz=100.0,
            pulse_width_us=400.0,  # 400 us
            authenticated=True,
        )
        # Charge = 2500 * 400 / 1000 = 1000 nC = 1 uC per phase
        # This exceeds 25 uC/cm^2 limit (assuming 1 cm^2 electrode)
        # Actually 2500 * 400 / 1000 / 1000 = 1 uC, which is below 25
        # Let me create one that actually exceeds
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=3000.0,  # Max amplitude
            frequency_Hz=100.0,
            pulse_width_us=500.0,  # Max pulse width
            authenticated=True,
        )
        # Charge = 3000 * 500 / 1000 / 1000 = 1.5 uC
        # Still below 25 uC limit - need a custom firewall

        firewall = NeuralFirewall(
            stim_amplitude_bounds=(0.0, 3000.0),
            stim_frequency_bounds=(1.0, 200.0),
            stim_pulse_width_bounds=(100.0, 500.0),
            charge_density_limit=0.5,  # Very strict: 0.5 uC/cm^2
            authorized_regions={"M1"},
        )
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=2000.0,
            frequency_Hz=100.0,
            pulse_width_us=400.0,  # Charge = 0.8 uC
            authenticated=True,
        )
        result = firewall.filter_stimulation(cmd)
        assert result.rejected
        assert not result.safety_checks["charge_density_safe"]

    def test_charge_density_within_limit(self, configured_firewall):
        """Test acceptance when charge density is within limit."""
        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=500.0,  # Low amplitude
            frequency_Hz=100.0,
            pulse_width_us=100.0,  # Short pulse
            authenticated=True,
        )
        result = configured_firewall.filter_stimulation(cmd)
        assert result.safety_checks["charge_density_safe"]


# =============================================================================
# Rate Limiting Tests
# =============================================================================

class TestRateLimiting:
    """Tests for stimulation rate limiting."""

    def test_rate_limit_not_exceeded(self, configured_firewall, valid_stim_command):
        """Test acceptance when rate limit not exceeded."""
        # Send 5 commands (below 10/second limit)
        for _ in range(5):
            result = configured_firewall.filter_stimulation(valid_stim_command)
            assert result.safety_checks["rate_limit_ok"]

    def test_rate_limit_exceeded(self, configured_firewall, valid_stim_command):
        """Test rejection when rate limit is exceeded."""
        # Send more commands than the limit
        results = []
        for _ in range(15):
            result = configured_firewall.filter_stimulation(valid_stim_command)
            results.append(result)

        # At least some should be rejected for rate limit
        rate_limit_failures = [
            r for r in results if not r.safety_checks.get("rate_limit_ok", True)
        ]
        assert len(rate_limit_failures) > 0

    def test_no_rate_limit_when_disabled(self, basic_firewall):
        """Test no rate limiting when stim_rate_limit is None."""
        # Basic firewall has no rate limit configured
        basic_firewall.authorized_regions.add("M1")  # Authorize region

        cmd = StimulationCommand(
            target_region="M1",
            amplitude_uA=1000.0,
            frequency_Hz=100.0,
            pulse_width_us=200.0,
            authenticated=True,
        )

        # Send many commands - none should fail on rate limit
        for _ in range(100):
            result = basic_firewall.filter_stimulation(cmd)
            assert result.safety_checks.get("rate_limit_ok", True)


# =============================================================================
# Region Authorization Tests
# =============================================================================

class TestRegionAuthorization:
    """Tests for dynamic region authorization."""

    def test_authorize_region(self, basic_firewall):
        """Test adding a region to authorized set."""
        assert "M1" not in basic_firewall.authorized_regions
        basic_firewall.authorize_region("M1")
        assert "M1" in basic_firewall.authorized_regions

    def test_revoke_region(self, configured_firewall):
        """Test removing a region from authorized set."""
        assert "M1" in configured_firewall.authorized_regions
        configured_firewall.revoke_region("M1")
        assert "M1" not in configured_firewall.authorized_regions

    def test_revoke_nonexistent_region(self, configured_firewall):
        """Test revoking a region that isn't authorized (no error)."""
        # Should not raise error
        configured_firewall.revoke_region("NONEXISTENT")
        assert "NONEXISTENT" not in configured_firewall.authorized_regions


# =============================================================================
# Statistics Tests
# =============================================================================

class TestStimulationStats:
    """Tests for stimulation statistics."""

    def test_stats_empty(self, basic_firewall):
        """Test stats with no stimulation activity."""
        stats = basic_firewall.get_stats()
        assert stats["stimulation"]["total"] == 0
        assert stats["stimulation"]["accepted"] == 0
        assert stats["flow_direction"] == "INACTIVE"

    def test_stats_with_stimulation(self, configured_firewall, valid_stim_command):
        """Test stats after stimulation activity."""
        # Send some commands
        for _ in range(5):
            configured_firewall.filter_stimulation(valid_stim_command)

        stats = configured_firewall.get_stats()
        assert stats["stimulation"]["total"] == 5
        assert stats["stimulation"]["accepted"] == 5
        assert stats["flow_direction"] == FlowDirection.WRITE.name

    def test_stats_mixed_results(self, configured_firewall, valid_stim_command, unauthorized_stim_command):
        """Test stats with mixed accept/reject results."""
        configured_firewall.filter_stimulation(valid_stim_command)  # Accept
        configured_firewall.filter_stimulation(valid_stim_command)  # Accept
        configured_firewall.filter_stimulation(unauthorized_stim_command)  # Reject

        stats = configured_firewall.get_stats()
        assert stats["stimulation"]["total"] == 3
        assert stats["stimulation"]["accepted"] == 2
        assert stats["stimulation"]["rejected"] == 1

    def test_bidirectional_flow_detection(self, configured_firewall, valid_stim_command):
        """Test detection of bidirectional flow."""
        from tara_mvp.core.firewall import Signal

        # Send a read signal
        read_signal = Signal(
            arrival_times=[0.0, 0.025, 0.050],
            amplitudes=[100.0, 98.0, 102.0],
            authenticated=True,
        )
        configured_firewall.filter(read_signal)

        # Send a stimulation command
        configured_firewall.filter_stimulation(valid_stim_command)

        stats = configured_firewall.get_stats()
        assert stats["flow_direction"] == FlowDirection.BIDIRECTIONAL.name


# =============================================================================
# Log Management Tests
# =============================================================================

class TestLogManagement:
    """Tests for log clearing and access."""

    def test_clear_stimulation_log(self, configured_firewall, valid_stim_command):
        """Test clearing only stimulation log."""
        configured_firewall.filter_stimulation(valid_stim_command)
        assert len(configured_firewall.stimulation_log) == 1

        configured_firewall.clear_stimulation_log()
        assert len(configured_firewall.stimulation_log) == 0

    def test_clear_all_logs(self, configured_firewall, valid_stim_command):
        """Test clearing all logs."""
        from tara_mvp.core.firewall import Signal

        read_signal = Signal(
            arrival_times=[0.0, 0.025],
            amplitudes=[100.0, 98.0],
            authenticated=True,
        )
        configured_firewall.filter(read_signal)
        configured_firewall.filter_stimulation(valid_stim_command)

        assert len(configured_firewall.log) == 1
        assert len(configured_firewall.stimulation_log) == 1

        configured_firewall.clear_log()
        assert len(configured_firewall.log) == 0
        assert len(configured_firewall.stimulation_log) == 0

    def test_stimulation_log_readonly(self, configured_firewall, valid_stim_command):
        """Test that stimulation_log property returns a copy."""
        configured_firewall.filter_stimulation(valid_stim_command)
        log_copy = configured_firewall.stimulation_log
        log_copy.clear()  # Clear the copy

        # Original should be unchanged
        assert len(configured_firewall.stimulation_log) == 1


# =============================================================================
# Callback Tests
# =============================================================================

class TestStimulationCallbacks:
    """Tests for alert callbacks on stimulation events."""

    def test_callback_triggered_on_critical(self, configured_firewall):
        """Test callback is triggered on critical alert."""
        callback_called = []

        def my_callback(result):
            callback_called.append(result)

        configured_firewall.register_callback(AlertLevel.CRITICAL, my_callback)

        # Send command that will fail critically (unauthorized region)
        cmd = StimulationCommand(
            target_region="UNKNOWN",
            amplitude_uA=1000.0,
            frequency_Hz=100.0,
            pulse_width_us=200.0,
            authenticated=True,
        )
        configured_firewall.filter_stimulation(cmd)

        assert len(callback_called) == 1
        assert callback_called[0].rejected


# =============================================================================
# Batch Processing Tests
# =============================================================================

class TestBatchStimulation:
    """Tests for batch stimulation filtering."""

    def test_filter_batch(self, configured_firewall, valid_stim_command):
        """Test filtering multiple stimulation commands."""
        commands = [valid_stim_command] * 5
        results = configured_firewall.filter_stimulation_batch(commands)

        assert len(results) == 5
        assert all(r.accepted for r in results)

    def test_batch_mixed_results(self, configured_firewall, valid_stim_command, unauthorized_stim_command):
        """Test batch with mixed valid/invalid commands."""
        commands = [valid_stim_command, unauthorized_stim_command, valid_stim_command]
        results = configured_firewall.filter_stimulation_batch(commands)

        assert len(results) == 3
        assert results[0].accepted
        assert results[1].rejected
        assert results[2].accepted


# =============================================================================
# FlowDirection Tests
# =============================================================================

class TestFlowDirection:
    """Tests for FlowDirection enum."""

    def test_flow_direction_values(self):
        """Test FlowDirection enum has expected values."""
        assert FlowDirection.READ.name == "READ"
        assert FlowDirection.WRITE.name == "WRITE"
        assert FlowDirection.BIDIRECTIONAL.name == "BIDIRECTIONAL"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
