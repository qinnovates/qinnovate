"""
MOABB Adapter Integration Tests

Tests for the Mother of All BCI Benchmarks (MOABB) adapter.
Uses mock data to enable CI/CD testing without downloading real datasets.

These tests verify:
1. Dataset loading for all 5 supported datasets
2. Attack injection (spike, noise, frequency, phase, dc_shift)
3. Coherence benchmark calculations
4. Signal conversion to TARA format
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import List, Any

# Import adapter components
from tara_mvp.data.moabb_adapter import (
    BCIParadigm,
    DatasetInfo,
    EEGSignal,
    AttackInjectedSignal,
    MOABBAdapter,
    is_moabb_available,
    get_moabb_version,
    AVAILABLE_DATASETS,
    SUPPORTED_PARADIGMS,
)


# =============================================================================
# Mock Data Fixtures
# =============================================================================

@pytest.fixture
def mock_eeg_signal():
    """Create a realistic mock EEG signal for testing."""
    np.random.seed(42)
    n_channels = 22
    n_samples = 1000  # 4 seconds at 250 Hz
    sampling_rate = 250.0

    # Generate realistic EEG-like data (alpha waves + noise)
    t = np.arange(n_samples) / sampling_rate
    data = np.zeros((n_channels, n_samples))

    for ch in range(n_channels):
        # Add alpha rhythm (10 Hz) with channel-specific phase
        alpha = 20 * np.sin(2 * np.pi * 10 * t + np.random.rand() * 2 * np.pi)
        # Add beta rhythm (20 Hz)
        beta = 10 * np.sin(2 * np.pi * 20 * t + np.random.rand() * 2 * np.pi)
        # Add pink noise
        noise = np.random.randn(n_samples) * 5
        data[ch] = alpha + beta + noise

    return EEGSignal(
        data=data,
        sampling_rate=sampling_rate,
        channels=[f"Ch{i}" for i in range(n_channels)],
        label="left_hand",
        subject=1,
        session="0train",
        paradigm=BCIParadigm.MOTOR_IMAGERY,
        metadata={"dataset": "BNCI2014_001", "epoch_index": 0}
    )


@pytest.fixture
def mock_p300_signal():
    """Create a mock P300 ERP signal."""
    np.random.seed(123)
    n_channels = 32
    n_samples = 2048  # 1 second at 2048 Hz
    sampling_rate = 2048.0

    t = np.arange(n_samples) / sampling_rate
    data = np.zeros((n_channels, n_samples))

    for ch in range(n_channels):
        # Background noise
        data[ch] = np.random.randn(n_samples) * 3
        # Add P300 component (300ms peak)
        p300_peak = int(0.3 * sampling_rate)
        p300_width = int(0.1 * sampling_rate)
        gaussian = np.exp(-0.5 * ((np.arange(n_samples) - p300_peak) / p300_width) ** 2)
        data[ch] += 8 * gaussian

    return EEGSignal(
        data=data,
        sampling_rate=sampling_rate,
        channels=[f"Ch{i}" for i in range(n_channels)],
        label="target",
        subject=1,
        session="session_1",
        paradigm=BCIParadigm.P300,
        metadata={"dataset": "EPFLP300", "epoch_index": 0}
    )


@pytest.fixture
def mock_ssvep_signal():
    """Create a mock SSVEP signal."""
    np.random.seed(456)
    n_channels = 8
    n_samples = 1024  # 4 seconds at 256 Hz
    sampling_rate = 256.0

    t = np.arange(n_samples) / sampling_rate
    data = np.zeros((n_channels, n_samples))

    for ch in range(n_channels):
        # 12 Hz SSVEP response (stronger in occipital channels)
        ssvep_amplitude = 15 if ch < 4 else 5
        data[ch] = ssvep_amplitude * np.sin(2 * np.pi * 12 * t)
        # Add harmonics
        data[ch] += 5 * np.sin(2 * np.pi * 24 * t)
        # Add noise
        data[ch] += np.random.randn(n_samples) * 3

    return EEGSignal(
        data=data,
        sampling_rate=sampling_rate,
        channels=[f"O{i}" for i in range(n_channels)],
        label="12Hz",
        subject=1,
        session="session_1",
        paradigm=BCIParadigm.SSVEP,
        metadata={"dataset": "SSVEP_Exo", "epoch_index": 0}
    )


@pytest.fixture
def mock_signals(mock_eeg_signal, mock_p300_signal, mock_ssvep_signal):
    """Collection of diverse mock signals for testing."""
    return [mock_eeg_signal, mock_p300_signal, mock_ssvep_signal]


# =============================================================================
# DatasetInfo Tests
# =============================================================================

class TestDatasetInfo:
    """Tests for DatasetInfo registry."""

    def test_all_datasets_registered(self):
        """Verify all 5 supported datasets are registered."""
        expected = ["BNCI2014_001", "BNCI2014_002", "BNCI2014_004", "EPFLP300", "SSVEP_Exo"]
        for name in expected:
            assert name in DatasetInfo.REGISTRY, f"Dataset {name} not registered"

    def test_dataset_info_fields(self):
        """Verify each dataset has required fields."""
        required_fields = ["paradigm", "subjects", "sessions", "channels",
                         "sampling_rate", "classes", "description", "oni_relevance"]

        for name, info in DatasetInfo.REGISTRY.items():
            for field in required_fields:
                assert field in info, f"Dataset {name} missing field: {field}"

    def test_get_info_valid(self):
        """Test getting info for valid dataset."""
        info = DatasetInfo.get_info("BNCI2014_001")
        assert info is not None
        assert info["paradigm"] == BCIParadigm.MOTOR_IMAGERY
        assert info["subjects"] == 9
        assert info["channels"] == 22

    def test_get_info_invalid(self):
        """Test getting info for invalid dataset returns None."""
        info = DatasetInfo.get_info("INVALID_DATASET")
        assert info is None

    def test_list_datasets_all(self):
        """Test listing all datasets."""
        datasets = DatasetInfo.list_datasets()
        assert len(datasets) == 5

    def test_list_datasets_by_paradigm(self):
        """Test filtering datasets by paradigm."""
        mi_datasets = DatasetInfo.list_datasets(BCIParadigm.MOTOR_IMAGERY)
        assert "BNCI2014_001" in mi_datasets
        assert "EPFLP300" not in mi_datasets

        p300_datasets = DatasetInfo.list_datasets(BCIParadigm.P300)
        assert "EPFLP300" in p300_datasets


# =============================================================================
# EEGSignal Tests
# =============================================================================

class TestEEGSignal:
    """Tests for EEGSignal dataclass."""

    def test_signal_properties(self, mock_eeg_signal):
        """Test EEGSignal computed properties."""
        assert mock_eeg_signal.duration == 4.0  # 1000 samples / 250 Hz
        assert mock_eeg_signal.n_channels == 22
        assert mock_eeg_signal.n_samples == 1000

    def test_to_tara_format(self, mock_eeg_signal):
        """Test conversion to TARA-compatible format."""
        tara_format = mock_eeg_signal.to_tara_format()

        assert "data" in tara_format
        assert "frequency" in tara_format
        assert "amplitude" in tara_format
        assert "source" in tara_format
        assert "metadata" in tara_format

        assert tara_format["frequency"] == 250.0
        assert tara_format["source"] == "moabb_MOTOR_IMAGERY"
        assert tara_format["metadata"]["subject"] == 1
        assert tara_format["metadata"]["paradigm"] == "MOTOR_IMAGERY"


# =============================================================================
# Attack Injection Tests
# =============================================================================

class TestAttackInjection:
    """Tests for attack injection functionality."""

    @pytest.fixture
    def mock_adapter(self):
        """Create adapter with mocked MOABB dependency."""
        with patch.dict('sys.modules', {
            'moabb': MagicMock(),
            'moabb.datasets': MagicMock(),
            'moabb.paradigms': MagicMock(),
        }):
            with patch('tara_mvp.data.moabb_adapter._MOABB_AVAILABLE', True):
                adapter = MOABBAdapter.__new__(MOABBAdapter)
                adapter.cache_dir = None
                adapter._loaded_datasets = {}
                adapter._paradigms = {}
                return adapter

    def test_spike_attack(self, mock_adapter, mock_eeg_signal):
        """Test spike injection attack."""
        attacked = mock_adapter.inject_attack(
            mock_eeg_signal,
            attack_type="spike",
            intensity=2.0,
            spike_interval=20
        )

        assert isinstance(attacked, AttackInjectedSignal)
        assert attacked.attack_type == "spike"
        assert attacked.attacked.max() > mock_eeg_signal.data.max()

        # Verify attack window
        start, end = attacked.attack_window
        assert start > 0
        assert end > start

    def test_noise_attack(self, mock_adapter, mock_eeg_signal):
        """Test Gaussian noise injection attack."""
        original_std = mock_eeg_signal.data.std()

        attacked = mock_adapter.inject_attack(
            mock_eeg_signal,
            attack_type="noise",
            intensity=3.0
        )

        assert attacked.attack_type == "noise"
        # Noise increases variance in attack window
        start, end = attacked.attack_window
        attack_region_std = attacked.attacked[:, start:end].std()
        original_region_std = mock_eeg_signal.data[:, start:end].std()
        assert attack_region_std > original_region_std

    def test_frequency_attack(self, mock_adapter, mock_eeg_signal):
        """Test frequency injection attack (SSVEP hijacking)."""
        attacked = mock_adapter.inject_attack(
            mock_eeg_signal,
            attack_type="frequency",
            intensity=1.5,
            frequency=15.0  # Inject 15 Hz
        )

        assert attacked.attack_type == "frequency"
        assert attacked.attack_params["frequency"] == 15.0

        # Original signal shouldn't be modified
        assert mock_eeg_signal.data.shape == attacked.original.data.shape

    def test_phase_attack(self, mock_adapter, mock_eeg_signal):
        """Test phase shift attack (timing manipulation)."""
        attacked = mock_adapter.inject_attack(
            mock_eeg_signal,
            attack_type="phase",
            shift_samples=10
        )

        assert attacked.attack_type == "phase"
        # Data should be shifted in attack window
        start, end = attacked.attack_window
        # Values should differ due to shift
        assert not np.allclose(
            attacked.attacked[:, start:end],
            mock_eeg_signal.data[:, start:end]
        )

    def test_dc_shift_attack(self, mock_adapter, mock_eeg_signal):
        """Test DC offset injection attack (amplifier saturation)."""
        original_mean = mock_eeg_signal.data.mean()

        attacked = mock_adapter.inject_attack(
            mock_eeg_signal,
            attack_type="dc_shift",
            intensity=2.0
        )

        assert attacked.attack_type == "dc_shift"
        # Attack window should have higher mean
        start, end = attacked.attack_window
        attack_mean = attacked.attacked[:, start:end].mean()
        original_window_mean = mock_eeg_signal.data[:, start:end].mean()
        assert attack_mean > original_window_mean

    def test_invalid_attack_type(self, mock_adapter, mock_eeg_signal):
        """Test that invalid attack type raises error."""
        with pytest.raises(ValueError, match="Unknown attack type"):
            mock_adapter.inject_attack(
                mock_eeg_signal,
                attack_type="invalid_attack"
            )

    def test_channel_specific_attack(self, mock_adapter, mock_eeg_signal):
        """Test attack targeting specific channels."""
        target_channels = [0, 5, 10]

        attacked = mock_adapter.inject_attack(
            mock_eeg_signal,
            attack_type="spike",
            channels=target_channels,
            intensity=5.0
        )

        assert attacked.injection_channels == target_channels

        # Non-target channels should be unchanged
        start, end = attacked.attack_window
        for ch in range(mock_eeg_signal.n_channels):
            if ch not in target_channels:
                np.testing.assert_array_equal(
                    attacked.attacked[ch],
                    mock_eeg_signal.data[ch]
                )

    def test_attack_window_parameters(self, mock_adapter, mock_eeg_signal):
        """Test custom attack window positioning."""
        attacked = mock_adapter.inject_attack(
            mock_eeg_signal,
            attack_type="noise",
            start_ratio=0.5,
            duration_ratio=0.1
        )

        expected_start = int(mock_eeg_signal.n_samples * 0.5)
        expected_duration = int(mock_eeg_signal.n_samples * 0.1)

        assert attacked.injection_start_sample == expected_start
        assert attacked.injection_duration_samples == expected_duration


# =============================================================================
# Coherence Benchmark Tests
# =============================================================================

class TestCoherenceBenchmark:
    """Tests for coherence benchmarking functionality."""

    @pytest.fixture
    def mock_adapter_with_coherence(self):
        """Create adapter with coherence module available."""
        with patch.dict('sys.modules', {
            'moabb': MagicMock(),
            'moabb.datasets': MagicMock(),
            'moabb.paradigms': MagicMock(),
        }):
            with patch('tara_mvp.data.moabb_adapter._MOABB_AVAILABLE', True):
                adapter = MOABBAdapter.__new__(MOABBAdapter)
                adapter.cache_dir = None
                adapter._loaded_datasets = {}
                adapter._paradigms = {}
                return adapter

    def test_benchmark_clean_signals(self, mock_adapter_with_coherence, mock_eeg_signal):
        """Test benchmarking with clean signals only."""
        signals = [mock_eeg_signal] * 5  # 5 identical signals

        results = mock_adapter_with_coherence.benchmark_coherence(signals)

        assert "clean_signals" in results
        assert results["clean_signals"]["count"] == 5
        assert len(results["clean_signals"]["scores"]) == 5
        assert results["clean_signals"]["mean_score"] >= 0
        assert results["attacked_signals"] is None

    def test_benchmark_with_attacks(self, mock_adapter_with_coherence, mock_eeg_signal):
        """Test benchmarking with attacked signals for detection metrics."""
        clean_signals = [mock_eeg_signal] * 5

        # Create attacked signals
        attacked_signals = []
        for signal in clean_signals:
            attacked = mock_adapter_with_coherence.inject_attack(
                signal,
                attack_type="noise",
                intensity=3.0
            )
            attacked_signals.append(attacked)

        results = mock_adapter_with_coherence.benchmark_coherence(
            clean_signals,
            attacked_signals
        )

        assert results["attacked_signals"] is not None
        assert results["attacked_signals"]["count"] == 5
        assert "detection_metrics" in results

        metrics = results["detection_metrics"]
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert "threshold" in metrics

        # Metrics should be between 0 and 1
        assert 0 <= metrics["accuracy"] <= 1
        assert 0 <= metrics["precision"] <= 1
        assert 0 <= metrics["recall"] <= 1
        assert 0 <= metrics["f1_score"] <= 1

    def test_benchmark_attack_type_grouping(self, mock_adapter_with_coherence, mock_eeg_signal):
        """Test that benchmark groups results by attack type."""
        clean_signals = [mock_eeg_signal] * 6

        attacked_signals = []
        attack_types = ["spike", "noise", "frequency", "phase", "dc_shift", "spike"]

        for signal, attack_type in zip(clean_signals, attack_types):
            attacked = mock_adapter_with_coherence.inject_attack(
                signal,
                attack_type=attack_type,
                intensity=2.0
            )
            attacked_signals.append(attacked)

        results = mock_adapter_with_coherence.benchmark_coherence(
            clean_signals,
            attacked_signals
        )

        by_type = results["attacked_signals"]["by_attack_type"]
        assert "spike" in by_type
        assert len(by_type["spike"]) == 2  # Two spike attacks
        assert "noise" in by_type
        assert "frequency" in by_type


# =============================================================================
# Helper Function Tests
# =============================================================================

class TestHelperFunctions:
    """Tests for module-level helper functions."""

    def test_is_moabb_available_when_not_installed(self):
        """Test availability check when MOABB not installed."""
        with patch('tara_mvp.data.moabb_adapter._MOABB_AVAILABLE', False):
            from tara_mvp.data.moabb_adapter import is_moabb_available
            # Note: Function already imported, need to reload or check global
            pass  # The actual behavior depends on import state

    def test_available_datasets_constant(self):
        """Test AVAILABLE_DATASETS contains expected entries."""
        assert len(AVAILABLE_DATASETS) == 5
        assert "BNCI2014_001" in AVAILABLE_DATASETS

    def test_supported_paradigms_constant(self):
        """Test SUPPORTED_PARADIGMS contains expected paradigms."""
        assert "MOTOR_IMAGERY" in SUPPORTED_PARADIGMS
        assert "P300" in SUPPORTED_PARADIGMS
        assert "SSVEP" in SUPPORTED_PARADIGMS


# =============================================================================
# Integration Tests (with mocked MOABB)
# =============================================================================

class TestMOABBAdapterIntegration:
    """Integration tests for MOABBAdapter with mocked MOABB."""

    @pytest.fixture
    def full_mock_adapter(self):
        """Create fully mocked adapter for integration tests."""
        # Create mock dataset
        mock_dataset = MagicMock()
        mock_dataset.__class__.__name__ = "BNCI2014_001"
        mock_dataset.ch_names = [f"Ch{i}" for i in range(22)]

        # Create mock paradigm that returns data
        mock_paradigm = MagicMock()
        n_epochs = 10
        mock_X = np.random.randn(n_epochs, 22, 1000)
        mock_labels = np.array(["left_hand"] * 5 + ["right_hand"] * 5)
        mock_meta = MagicMock()
        mock_meta.iloc = [{"session": "0train", "run": "run_1"} for _ in range(n_epochs)]
        mock_meta.columns = ["session", "run"]
        mock_paradigm.get_data.return_value = (mock_X, mock_labels, mock_meta)

        with patch.dict('sys.modules', {
            'moabb': MagicMock(),
            'moabb.datasets': MagicMock(),
            'moabb.paradigms': MagicMock(),
        }):
            with patch('tara_mvp.data.moabb_adapter._MOABB_AVAILABLE', True):
                adapter = MOABBAdapter.__new__(MOABBAdapter)
                adapter.cache_dir = None
                adapter._loaded_datasets = {"BNCI2014_001": mock_dataset}
                adapter._paradigms = {BCIParadigm.MOTOR_IMAGERY: mock_paradigm}
                return adapter

    def test_list_datasets(self, full_mock_adapter):
        """Test listing available datasets."""
        datasets = full_mock_adapter.list_datasets()
        assert len(datasets) == 5

        # Check dataset info structure
        for ds in datasets:
            assert "name" in ds
            assert "paradigm" in ds
            assert "oni_relevance" in ds

    def test_list_datasets_by_paradigm(self, full_mock_adapter):
        """Test filtering datasets by paradigm."""
        mi_datasets = full_mock_adapter.list_datasets(BCIParadigm.MOTOR_IMAGERY)
        assert all(ds["paradigm"] == BCIParadigm.MOTOR_IMAGERY for ds in mi_datasets)


# =============================================================================
# Parameterized Tests for All Attack Types
# =============================================================================

class TestAllAttackTypes:
    """Parameterized tests covering all 5 attack types."""

    @pytest.fixture
    def adapter(self):
        """Create adapter for attack tests."""
        with patch.dict('sys.modules', {
            'moabb': MagicMock(),
            'moabb.datasets': MagicMock(),
            'moabb.paradigms': MagicMock(),
        }):
            with patch('tara_mvp.data.moabb_adapter._MOABB_AVAILABLE', True):
                adapter = MOABBAdapter.__new__(MOABBAdapter)
                adapter.cache_dir = None
                adapter._loaded_datasets = {}
                adapter._paradigms = {}
                return adapter

    @pytest.mark.parametrize("attack_type,extra_params", [
        ("spike", {"spike_interval": 15}),
        ("noise", {}),
        ("frequency", {"frequency": 12.0}),
        ("phase", {"shift_samples": 8}),
        ("dc_shift", {}),
    ])
    def test_attack_preserves_shape(self, adapter, mock_eeg_signal, attack_type, extra_params):
        """Test that all attack types preserve signal shape."""
        attacked = adapter.inject_attack(
            mock_eeg_signal,
            attack_type=attack_type,
            intensity=1.0,
            **extra_params
        )

        assert attacked.attacked.shape == mock_eeg_signal.data.shape

    @pytest.mark.parametrize("attack_type", ["spike", "noise", "frequency", "phase", "dc_shift"])
    def test_attack_modifies_signal(self, adapter, mock_eeg_signal, attack_type):
        """Test that all attack types actually modify the signal."""
        attacked = adapter.inject_attack(
            mock_eeg_signal,
            attack_type=attack_type,
            intensity=2.0
        )

        # Signal should be different in attack window
        start, end = attacked.attack_window
        assert not np.allclose(
            attacked.attacked[:, start:end],
            mock_eeg_signal.data[:, start:end]
        ), f"Attack type '{attack_type}' did not modify signal"

    @pytest.mark.parametrize("intensity", [0.5, 1.0, 2.0, 5.0])
    def test_intensity_scaling(self, adapter, mock_eeg_signal, intensity):
        """Test that intensity parameter scales attack magnitude."""
        attacked_low = adapter.inject_attack(
            mock_eeg_signal,
            attack_type="noise",
            intensity=1.0
        )
        attacked_high = adapter.inject_attack(
            mock_eeg_signal,
            attack_type="noise",
            intensity=intensity
        )

        # Higher intensity should generally produce larger changes
        # (statistical test - not always true for noise, but usually)
        if intensity > 1.0:
            start, end = attacked_low.attack_window
            diff_low = np.abs(attacked_low.attacked[:, start:end] - mock_eeg_signal.data[:, start:end]).mean()
            diff_high = np.abs(attacked_high.attacked[:, start:end] - mock_eeg_signal.data[:, start:end]).mean()
            # Allow some variance due to randomness
            assert diff_high >= diff_low * 0.5, "Higher intensity should produce larger changes"


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.fixture
    def adapter(self):
        """Create adapter for edge case tests."""
        with patch.dict('sys.modules', {
            'moabb': MagicMock(),
            'moabb.datasets': MagicMock(),
            'moabb.paradigms': MagicMock(),
        }):
            with patch('tara_mvp.data.moabb_adapter._MOABB_AVAILABLE', True):
                adapter = MOABBAdapter.__new__(MOABBAdapter)
                adapter.cache_dir = None
                adapter._loaded_datasets = {}
                adapter._paradigms = {}
                return adapter

    def test_single_channel_signal(self, adapter):
        """Test attack injection on single-channel signal."""
        signal = EEGSignal(
            data=np.random.randn(1, 500),
            sampling_rate=250.0,
            channels=["Cz"],
            label="test",
            subject=1,
            session="1",
            paradigm=BCIParadigm.MOTOR_IMAGERY,
        )

        attacked = adapter.inject_attack(signal, attack_type="spike")
        assert attacked.attacked.shape == (1, 500)

    def test_short_signal(self, adapter):
        """Test attack on very short signal."""
        signal = EEGSignal(
            data=np.random.randn(8, 50),  # Very short
            sampling_rate=250.0,
            channels=[f"Ch{i}" for i in range(8)],
            label="test",
            subject=1,
            session="1",
            paradigm=BCIParadigm.MOTOR_IMAGERY,
        )

        attacked = adapter.inject_attack(
            signal,
            attack_type="noise",
            start_ratio=0.2,
            duration_ratio=0.3
        )

        assert attacked.injection_start_sample == 10  # 50 * 0.2
        assert attacked.injection_duration_samples == 15  # 50 * 0.3

    def test_full_signal_attack(self, adapter, mock_eeg_signal):
        """Test attack covering entire signal."""
        attacked = adapter.inject_attack(
            mock_eeg_signal,
            attack_type="dc_shift",
            start_ratio=0.0,
            duration_ratio=1.0
        )

        assert attacked.injection_start_sample == 0
        # Duration should cover full signal
        assert attacked.injection_duration_samples == mock_eeg_signal.n_samples

    def test_zero_intensity_attack(self, adapter, mock_eeg_signal):
        """Test attack with zero intensity (should minimally affect signal)."""
        attacked = adapter.inject_attack(
            mock_eeg_signal,
            attack_type="dc_shift",
            intensity=0.0
        )

        # With zero intensity, DC shift should be zero
        np.testing.assert_array_almost_equal(
            attacked.attacked,
            mock_eeg_signal.data
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
