"""
Tests for TARA data models.

Tests brain regions, BCI nodes, and electrode arrays.
"""

import pytest


class TestBrainRegions:
    """Tests for brain region definitions."""

    def test_brain_regions_import(self):
        """Test that brain_regions module can be imported."""
        from tara_mvp.data import brain_regions
        assert hasattr(brain_regions, "BRAIN_REGIONS")

    def test_all_regions_present(self):
        """Test that all 10 brain regions are defined."""
        from tara_mvp.data.brain_regions import BRAIN_REGIONS

        expected_regions = ["M1", "S1", "PMC", "SMA", "PFC", "BROCA", "WERNICKE", "V1", "A1", "HIPP"]

        for region in expected_regions:
            assert region in BRAIN_REGIONS, f"Missing region: {region}"

    def test_region_has_required_fields(self):
        """Test that each region has required fields."""
        from tara_mvp.data.brain_regions import BRAIN_REGIONS

        for abbr, region in BRAIN_REGIONS.items():
            assert hasattr(region, "name") or "name" in region.__dict__
            assert hasattr(region, "center") or "center" in region.__dict__
            assert hasattr(region, "oni_layer") or "oni_layer" in region.__dict__

    def test_region_oni_layers_valid(self, oni_layer_mapping):
        """Test that ONI layer assignments are valid (11-14 for silicon domain)."""
        from tara_mvp.data.brain_regions import BRAIN_REGIONS

        for abbr, expected_layer in oni_layer_mapping.items():
            if abbr in BRAIN_REGIONS:
                region = BRAIN_REGIONS[abbr]
                layer = getattr(region, "oni_layer", None) or region.get("oni_layer")
                assert layer == expected_layer, f"{abbr} should be L{expected_layer}"

    def test_region_positions_in_brain(self, brain_region_positions):
        """Test that region positions are within brain bounds."""
        from tara_mvp.data.brain_regions import BRAIN_REGIONS

        # Brain is approximately 170x140x140mm, centered roughly at origin
        for abbr, (x, y, z) in brain_region_positions.items():
            assert -100 <= x <= 100, f"{abbr} x position out of bounds"
            assert -100 <= y <= 100, f"{abbr} y position out of bounds"
            assert -80 <= z <= 80, f"{abbr} z position out of bounds"


class TestBCINodes:
    """Tests for BCI node network models."""

    def test_bci_nodes_import(self):
        """Test that bci_nodes module can be imported."""
        from tara_mvp.data import bci_nodes
        assert hasattr(bci_nodes, "BCINode")
        assert hasattr(bci_nodes, "BCINodeNetwork")

    def test_create_demo_network(self):
        """Test creating a demo BCI node network."""
        from tara_mvp.data.bci_nodes import create_demo_network

        network = create_demo_network(n_nodes=4)

        assert network.total_nodes == 4
        assert network.online_nodes <= network.total_nodes

    def test_node_at_layer_8(self):
        """Test that BCI nodes operate at L8 (Neural Gateway)."""
        from tara_mvp.data.bci_nodes import BCINode

        node = BCINode(node_id="test_1", name="Test Node")

        assert node.oni_layer == 8

    def test_node_network_connections(self):
        """Test node network connectivity."""
        from tara_mvp.data.bci_nodes import create_demo_network

        network = create_demo_network(n_nodes=4)

        # Check that nodes are connected
        assert len(network.connections) > 0

        # Check that we can get connections for a node
        first_node_id = list(network.nodes.keys())[0]
        connections = network.get_connections(first_node_id)
        assert len(connections) > 0

    def test_node_health_score(self):
        """Test node health score calculation."""
        from tara_mvp.data.bci_nodes import create_demo_network

        network = create_demo_network(n_nodes=4)

        for node in network.nodes.values():
            health = node.health_score
            assert 0.0 <= health <= 1.0

    def test_network_topology_data(self):
        """Test getting topology data for visualization."""
        from tara_mvp.data.bci_nodes import create_demo_network

        network = create_demo_network(n_nodes=4)
        topo = network.get_topology_data()

        assert "nodes" in topo
        assert "edges" in topo
        assert len(topo["nodes"]) == 4


class TestElectrodes:
    """Tests for electrode models."""

    def test_electrode_import(self):
        """Test that electrode classes can be imported."""
        from tara_mvp.data.brain_regions import Electrode, ElectrodeThread, ElectrodeArray

    def test_create_demo_array(self):
        """Test creating a demo electrode array."""
        from tara_mvp.data.brain_regions import create_demo_array

        array = create_demo_array(
            n_threads_per_region=2,
            n_electrodes_per_thread=8,
            regions=["M1", "S1"],
        )

        # Should have 2 regions × 2 threads × 8 electrodes = 32 total
        total_electrodes = sum(len(t.electrodes) for t in array.threads)
        assert total_electrodes == 32

    def test_electrode_status_enum(self):
        """Test electrode status enumeration."""
        from tara_mvp.data.brain_regions import ElectrodeStatus

        assert hasattr(ElectrodeStatus, "NORMAL")
        assert hasattr(ElectrodeStatus, "WARNING")
        assert hasattr(ElectrodeStatus, "CRITICAL")
        assert hasattr(ElectrodeStatus, "OFFLINE")

    def test_electrode_metrics(self):
        """Test electrode metric ranges."""
        from tara_mvp.data.brain_regions import create_demo_array

        array = create_demo_array(
            n_threads_per_region=1,
            n_electrodes_per_thread=8,
            regions=["M1"],
        )

        for thread in array.threads:
            for electrode in thread.electrodes:
                # Spike rate should be non-negative
                assert electrode.spike_rate >= 0

                # Impedance should be positive
                assert electrode.impedance > 0

                # SNR can be any value but typically positive for good electrodes
                assert electrode.snr >= 0 or electrode.snr > -10
