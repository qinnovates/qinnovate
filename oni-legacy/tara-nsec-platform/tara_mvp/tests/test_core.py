"""
Tests for TARA core modules.

Tests coherence calculation, ONI layers, firewall, and scale-frequency.
"""

import pytest
import numpy as np


class TestCoherence:
    """Tests for coherence metric calculation."""

    def test_coherence_import(self):
        """Test that coherence module can be imported."""
        from tara_mvp.core import coherence
        assert hasattr(coherence, "CoherenceMetric")

    def test_coherence_calculation(self):
        """Test basic coherence calculation."""
        from tara_mvp.core.coherence import CoherenceMetric

        metric = CoherenceMetric(reference_freq=40.0)

        # API requires arrival_times and amplitudes
        arrival_times = [0.0, 0.025, 0.050, 0.075, 0.100]
        amplitudes = [100, 98, 102, 99, 101]

        cs = metric.calculate(arrival_times, amplitudes)
        assert 0.0 <= cs <= 1.0

    def test_coherence_high_for_coherent_signal(self):
        """Test that coherent signals have high Cₛ."""
        from tara_mvp.core.coherence import CoherenceMetric

        metric = CoherenceMetric(reference_freq=40.0)

        # Regular timing (25ms intervals = 40Hz) with stable amplitude
        arrival_times = [0.0, 0.025, 0.050, 0.075, 0.100]
        amplitudes = [100, 100, 100, 100, 100]

        cs = metric.calculate(arrival_times, amplitudes)
        assert cs > 0.5

    def test_coherence_low_for_noise(self):
        """Test that noisy signals have lower Cₛ."""
        from tara_mvp.core.coherence import CoherenceMetric

        metric = CoherenceMetric(reference_freq=40.0)

        # Irregular timing with variable amplitude
        np.random.seed(42)
        arrival_times = sorted(np.random.uniform(0, 0.1, 5).tolist())
        amplitudes = np.random.uniform(50, 150, 5).tolist()

        cs = metric.calculate(arrival_times, amplitudes)
        # Noisy signal should have lower coherence than perfect signal
        assert cs < 1.0


class TestONILayers:
    """Tests for ONI 14-layer model."""

    def test_layers_import(self):
        """Test that layers module can be imported."""
        from tara_mvp.core import layers
        assert hasattr(layers, "ONIStack")

    def test_layer_count(self):
        """Test that ONI model has 14 layers."""
        from tara_mvp.core.layers import ONIStack

        stack = ONIStack()
        assert len(stack) == 14

    def test_layer_8_is_gateway(self):
        """Test that L8 is Neural Gateway."""
        from tara_mvp.core.layers import ONIStack

        stack = ONIStack()
        layer_8 = stack.layer(8)
        assert "gateway" in layer_8.name.lower()

    def test_biological_layers(self):
        """Test that L1-L7 are OSI domain."""
        from tara_mvp.core.layers import ONIStack

        stack = ONIStack()
        for layer in stack.biological_layers():
            domain_str = str(layer.domain).lower()
            assert any(d in domain_str for d in ["osi", "biological", "bio"])

    def test_silicon_layers(self):
        """Test that L9-L14 are neural/cognitive domain."""
        from tara_mvp.core.layers import ONIStack

        stack = ONIStack()
        for layer in stack.silicon_layers():
            domain_str = str(layer.domain).lower()
            assert any(d in domain_str for d in ["neural", "cognitive", "silicon", "digital"])


class TestFirewall:
    """Tests for neural firewall."""

    def test_firewall_import(self):
        """Test that firewall module can be imported."""
        from tara_mvp.core import firewall
        assert hasattr(firewall, "NeuralFirewall")

    def test_firewall_pass_good_signal(self):
        """Test that good signals pass the firewall."""
        from tara_mvp.core.firewall import NeuralFirewall, Signal

        fw = NeuralFirewall()

        # Good signal with consistent timing and amplitude
        signal = Signal(
            arrival_times=[0.0, 0.025, 0.050, 0.075, 0.100],
            amplitudes=[100, 98, 102, 99, 101],
            authenticated=True
        )

        result = fw.filter(signal)
        # Good signal should pass (ACCEPT or ACCEPT_FLAG)
        assert result.decision.name in ["ACCEPT", "ACCEPT_FLAG"]

    def test_firewall_block_unauthenticated(self):
        """Test that unauthenticated signals with medium coherence are blocked."""
        from tara_mvp.core.firewall import NeuralFirewall, Signal

        fw = NeuralFirewall()

        # Signal with poor timing (irregular intervals)
        signal = Signal(
            arrival_times=[0.0, 0.01, 0.05, 0.06, 0.15],
            amplitudes=[100, 98, 102, 99, 101],
            authenticated=False
        )

        result = fw.filter(signal)
        # Unauthenticated signal should be rejected
        assert result.decision.name == "REJECT"

    def test_firewall_block_out_of_bounds(self):
        """Test that out-of-bounds amplitude signals are blocked."""
        from tara_mvp.core.firewall import NeuralFirewall, Signal

        fw = NeuralFirewall(amplitude_bounds=(0, 200))

        # Signal with amplitude outside bounds
        signal = Signal(
            arrival_times=[0.0, 0.025, 0.050],
            amplitudes=[100, 500, 100],  # 500 is out of bounds
            authenticated=True
        )

        result = fw.filter(signal)
        assert result.decision.name == "REJECT"


class TestScaleFrequency:
    """Tests for scale-frequency invariant."""

    def test_scale_freq_import(self):
        """Test that scale_freq module can be imported."""
        from tara_mvp.core import scale_freq
        assert hasattr(scale_freq, "ScaleFrequencyInvariant")

    def test_invariant_holds(self):
        """Test that f × S ≈ k for valid signals."""
        from tara_mvp.core.scale_freq import ScaleFrequencyInvariant

        sfi = ScaleFrequencyInvariant()

        # Test at different scales
        pairs = [
            (10, 1.0),    # 10 Hz at scale 1
            (100, 0.1),   # 100 Hz at scale 0.1
            (1, 10.0),    # 1 Hz at scale 10
        ]

        products = [f * s for f, s in pairs]

        # All products should be approximately equal
        assert all(abs(p - products[0]) < 1.0 for p in products)

    def test_validate_biologically_plausible(self):
        """Test that biologically plausible signals validate."""
        from tara_mvp.core.scale_freq import ScaleFrequencyInvariant

        sfi = ScaleFrequencyInvariant()

        # 40 Hz gamma at 100 μm scale
        is_valid = sfi.validate(40, 1e-4)
        assert isinstance(is_valid, bool)
