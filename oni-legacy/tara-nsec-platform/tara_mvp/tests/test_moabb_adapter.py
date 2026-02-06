"""
Tests for MOABB Adapter

These tests verify the MOABB adapter works correctly for loading
real EEG datasets and integrating with TARA's security components.

Note: Tests requiring MOABB are skipped if MOABB is not installed.
Install with: pip install oni-tara[moabb]
"""

import pytest
import numpy as np

from tara_mvp.data.moabb_adapter import (
    is_moabb_available,
    get_moabb_version,
    BCIParadigm,
    DatasetInfo,
    EEGSignal,
    AVAILABLE_DATASETS,
    SUPPORTED_PARADIGMS,
)


class TestMOABBAvailability:
    """Test MOABB availability checking."""

    def test_is_moabb_available_returns_bool(self):
        """is_moabb_available should return a boolean."""
        result = is_moabb_available()
        assert isinstance(result, bool)

    def test_get_moabb_version(self):
        """get_moabb_version returns string or None."""
        version = get_moabb_version()
        if is_moabb_available():
            assert isinstance(version, str)
            assert len(version) > 0
        else:
            assert version is None


class TestDatasetInfo:
    """Test dataset information registry."""

    def test_available_datasets_not_empty(self):
        """Should have at least some datasets registered."""
        assert len(AVAILABLE_DATASETS) > 0

    def test_supported_paradigms(self):
        """Should support standard BCI paradigms."""
        assert "MOTOR_IMAGERY" in SUPPORTED_PARADIGMS
        assert "P300" in SUPPORTED_PARADIGMS
        assert "SSVEP" in SUPPORTED_PARADIGMS

    def test_get_info_valid_dataset(self):
        """Should return info for valid dataset."""
        info = DatasetInfo.get_info("BNCI2014_001")
        assert info is not None
        assert info["paradigm"] == BCIParadigm.MOTOR_IMAGERY
        assert info["subjects"] == 9
        assert "sampling_rate" in info

    def test_get_info_invalid_dataset(self):
        """Should return None for invalid dataset."""
        info = DatasetInfo.get_info("INVALID_DATASET")
        assert info is None

    def test_list_datasets_all(self):
        """Should list all datasets when no filter."""
        datasets = DatasetInfo.list_datasets()
        assert "BNCI2014_001" in datasets
        assert len(datasets) == len(AVAILABLE_DATASETS)

    def test_list_datasets_by_paradigm(self):
        """Should filter datasets by paradigm."""
        mi_datasets = DatasetInfo.list_datasets(BCIParadigm.MOTOR_IMAGERY)
        assert "BNCI2014_001" in mi_datasets
        assert "EPFLP300" not in mi_datasets  # This is P300


class TestEEGSignal:
    """Test EEGSignal data container."""

    def test_eeg_signal_creation(self):
        """Should create EEGSignal with valid data."""
        data = np.random.randn(22, 250)  # 22 channels, 250 samples
        signal = EEGSignal(
            data=data,
            sampling_rate=250.0,
            channels=[f"Ch{i}" for i in range(22)],
            label="left_hand",
            subject=1,
            session="train",
            paradigm=BCIParadigm.MOTOR_IMAGERY,
        )
        assert signal.n_channels == 22
        assert signal.n_samples == 250
        assert signal.duration == 1.0  # 250 samples at 250 Hz

    def test_eeg_signal_to_tara_format(self):
        """Should convert to TARA-compatible format."""
        data = np.random.randn(8, 128)
        signal = EEGSignal(
            data=data,
            sampling_rate=256.0,
            channels=[f"Ch{i}" for i in range(8)],
            label="target",
            subject=2,
            session="test",
            paradigm=BCIParadigm.P300,
        )
        tara_format = signal.to_tara_format()

        assert "data" in tara_format
        assert "frequency" in tara_format
        assert tara_format["frequency"] == 256.0
        assert "metadata" in tara_format
        assert tara_format["metadata"]["subject"] == 2
        assert tara_format["metadata"]["paradigm"] == "P300"


class TestBCIParadigm:
    """Test BCI paradigm enum."""

    def test_paradigm_values(self):
        """Should have expected paradigm values."""
        assert BCIParadigm.MOTOR_IMAGERY is not None
        assert BCIParadigm.P300 is not None
        assert BCIParadigm.SSVEP is not None


# Tests requiring MOABB installation
@pytest.mark.skipif(
    not is_moabb_available(),
    reason="MOABB not installed. Install with: pip install oni-tara[moabb]"
)
class TestMOABBAdapter:
    """Tests that require MOABB to be installed."""

    def test_adapter_initialization(self):
        """Should initialize adapter when MOABB available."""
        from tara_mvp.data.moabb_adapter import MOABBAdapter
        adapter = MOABBAdapter()
        assert adapter.is_available

    def test_list_datasets(self):
        """Should list available datasets with metadata."""
        from tara_mvp.data.moabb_adapter import MOABBAdapter
        adapter = MOABBAdapter()
        datasets = adapter.list_datasets()
        assert len(datasets) > 0
        assert "name" in datasets[0]
        assert "paradigm" in datasets[0]

    def test_load_dataset(self):
        """Should load a dataset."""
        from tara_mvp.data.moabb_adapter import MOABBAdapter
        adapter = MOABBAdapter()
        dataset = adapter.load_dataset("BNCI2014_001")
        assert dataset is not None

    def test_get_signals(self):
        """Should extract signals from dataset."""
        from tara_mvp.data.moabb_adapter import MOABBAdapter
        adapter = MOABBAdapter()
        dataset = adapter.load_dataset("BNCI2014_001")
        signals = adapter.get_signals(dataset, subject=1, max_epochs=5)

        assert len(signals) == 5
        assert all(isinstance(s, EEGSignal) for s in signals)
        assert signals[0].paradigm == BCIParadigm.MOTOR_IMAGERY

    def test_inject_attack_spike(self):
        """Should inject spike attack into signal."""
        from tara_mvp.data.moabb_adapter import MOABBAdapter
        adapter = MOABBAdapter()
        dataset = adapter.load_dataset("BNCI2014_001")
        signals = adapter.get_signals(dataset, subject=1, max_epochs=1)

        attacked = adapter.inject_attack(
            signals[0],
            attack_type="spike",
            intensity=2.0,
        )

        assert attacked.attack_type == "spike"
        assert attacked.attacked.shape == signals[0].data.shape
        # Attacked signal should have higher amplitude
        assert np.abs(attacked.attacked).max() > np.abs(signals[0].data).max()

    def test_inject_attack_noise(self):
        """Should inject noise attack into signal."""
        from tara_mvp.data.moabb_adapter import MOABBAdapter
        adapter = MOABBAdapter()
        dataset = adapter.load_dataset("BNCI2014_001")
        signals = adapter.get_signals(dataset, subject=1, max_epochs=1)

        attacked = adapter.inject_attack(
            signals[0],
            attack_type="noise",
            intensity=1.5,
        )

        assert attacked.attack_type == "noise"
        # Attacked signal should have higher variance in attack window
        start, end = attacked.attack_window
        attack_std = np.std(attacked.attacked[:, start:end])
        original_std = np.std(signals[0].data[:, start:end])
        assert attack_std > original_std

    def test_benchmark_coherence(self):
        """Should benchmark coherence metric against signals."""
        from tara_mvp.data.moabb_adapter import MOABBAdapter
        adapter = MOABBAdapter()
        dataset = adapter.load_dataset("BNCI2014_001")
        signals = adapter.get_signals(dataset, subject=1, max_epochs=5)

        results = adapter.benchmark_coherence(signals)

        assert "clean_signals" in results
        assert results["clean_signals"]["count"] == 5
        assert "mean_score" in results["clean_signals"]
        assert "std_score" in results["clean_signals"]

    def test_benchmark_coherence_with_attacks(self):
        """Should benchmark coherence with attack detection metrics."""
        from tara_mvp.data.moabb_adapter import MOABBAdapter
        adapter = MOABBAdapter()
        dataset = adapter.load_dataset("BNCI2014_001")
        signals = adapter.get_signals(dataset, subject=1, max_epochs=5)

        # Create attacked versions
        attacked_signals = [
            adapter.inject_attack(s, "spike", intensity=3.0)
            for s in signals
        ]

        results = adapter.benchmark_coherence(signals, attacked_signals)

        assert results["attacked_signals"] is not None
        assert results["detection_metrics"] is not None
        assert "accuracy" in results["detection_metrics"]
        assert "precision" in results["detection_metrics"]
        assert "recall" in results["detection_metrics"]
        assert "f1_score" in results["detection_metrics"]
