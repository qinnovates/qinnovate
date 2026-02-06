"""
TARA Test Fixtures

Shared fixtures for TARA test suite.
"""

import pytest
import numpy as np


@pytest.fixture
def sample_signal():
    """Generate a sample neural signal for testing."""
    np.random.seed(42)
    duration = 1.0  # seconds
    sample_rate = 1000  # Hz
    t = np.linspace(0, duration, int(duration * sample_rate))

    # Simulated LFP signal (mix of frequencies)
    signal = (
        0.5 * np.sin(2 * np.pi * 10 * t) +  # Alpha (10 Hz)
        0.3 * np.sin(2 * np.pi * 40 * t) +  # Gamma (40 Hz)
        0.1 * np.random.randn(len(t))        # Noise
    )
    return {"time": t, "signal": signal, "sample_rate": sample_rate}


@pytest.fixture
def sample_metrics():
    """Generate sample metrics for NSAM testing."""
    return {
        "coherence": 0.85,
        "spike_rate": 45.0,
        "amplitude": 0.5,
        "phase": 1.2,
        "frequency": 10.0,
    }


@pytest.fixture
def sample_firewall_signal():
    """Generate sample signal for firewall testing."""
    return {
        "impedance": 250.0,      # kOhms (good range: 100-500)
        "snr": 15.0,             # dB (good: > 5)
        "spike_rate": 50.0,      # Hz (normal: 5-100)
        "signal_rate": 500.0,    # Hz
        "consistency": 0.9,      # 0-1
        "coherence": 0.8,        # 0-1 (Cₛ)
        "anomaly_score": 0.2,    # 0-1 (low is good)
    }


@pytest.fixture
def brain_region_positions():
    """Brain region MNI coordinates for testing."""
    return {
        "M1": (-35, -20, 55),
        "S1": (-35, -35, 50),
        "PMC": (-45, 5, 50),
        "SMA": (0, -5, 60),
        "PFC": (35, 45, 25),
        "BROCA": (-50, 20, 15),
        "WERNICKE": (-55, -55, 20),
        "V1": (0, -85, 5),
        "A1": (-55, -20, 10),
        "HIPP": (-25, -20, -15),
    }


@pytest.fixture
def oni_layer_mapping():
    """ONI layer mapping for brain regions."""
    return {
        "M1": 13,      # Presentation
        "S1": 12,      # Session
        "PMC": 13,     # Presentation
        "SMA": 13,     # Presentation
        "PFC": 14,     # Application
        "BROCA": 14,   # Application
        "WERNICKE": 14, # Application
        "V1": 12,      # Session
        "A1": 12,      # Session
        "HIPP": 11,    # Transport
    }
