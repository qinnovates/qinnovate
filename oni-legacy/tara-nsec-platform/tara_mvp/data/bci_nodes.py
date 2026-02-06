"""
BCI Node Data Model

Defines BCI (Brain-Computer Interface) nodes as ONI-aligned systems.
Each node operates at Layer 8 (Neural Gateway) as an ONI Firewall node,
monitoring and validating signals crossing the bio-digital boundary.

ONI Framework Alignment:
- L1-L7: Silicon domain (OSI networking - computer side)
- L8: Neural Gateway - WHERE BCI NODES OPERATE (Firewall location)
- L9-L14: Biology domain (neural processing - brain side)

Each BCI Node:
- Acts as an ONI Firewall checkpoint at Layer 8
- Monitors coherence of signals crossing the boundary
- Connects to other nodes for distributed monitoring
- Maps to physical electrode threads/regions
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np


class NodeStatus(Enum):
    """Operational status of a BCI node."""
    ONLINE = "online"
    DEGRADED = "degraded"
    WARNING = "warning"
    OFFLINE = "offline"
    INITIALIZING = "initializing"


class ConnectionStatus(Enum):
    """Status of connection between nodes."""
    CONNECTED = "connected"
    DEGRADED = "degraded"
    DISCONNECTED = "disconnected"
    SYNCING = "syncing"


@dataclass
class NodeMetrics:
    """
    Real-time metrics for a BCI node.

    These metrics reflect the node's role as an ONI Firewall
    at Layer 8, monitoring signal coherence and integrity.
    """
    # ONI Firewall metrics
    signals_processed: int = 0
    signals_passed: int = 0
    signals_blocked: int = 0
    signals_flagged: int = 0

    # Coherence metrics
    avg_coherence: float = 0.85
    min_coherence: float = 0.0
    max_coherence: float = 1.0

    # Hardware metrics
    avg_impedance: float = 250.0  # kOhms
    avg_snr: float = 15.0  # dB
    temperature: float = 37.0  # Celsius

    # Performance metrics
    latency_ms: float = 5.0
    throughput_hz: float = 30000.0  # samples/sec
    uptime_pct: float = 99.9

    # Timestamp
    last_update: datetime = field(default_factory=datetime.now)

    @property
    def pass_rate(self) -> float:
        """Calculate signal pass rate percentage."""
        if self.signals_processed == 0:
            return 100.0
        return (self.signals_passed / self.signals_processed) * 100

    @property
    def block_rate(self) -> float:
        """Calculate signal block rate percentage."""
        if self.signals_processed == 0:
            return 0.0
        return (self.signals_blocked / self.signals_processed) * 100


@dataclass
class NodeConnection:
    """
    Connection between two BCI nodes.

    Represents the communication link used for distributed
    monitoring, state synchronization, and coordinated filtering.
    """
    source_node_id: str
    target_node_id: str
    status: ConnectionStatus = ConnectionStatus.CONNECTED

    # Connection quality metrics
    latency_ms: float = 2.0
    packet_loss_pct: float = 0.0
    bandwidth_mbps: float = 100.0
    jitter_ms: float = 0.5

    # Synchronization
    sync_offset_us: float = 0.0  # Microseconds offset
    last_sync: datetime = field(default_factory=datetime.now)

    # Traffic stats
    packets_sent: int = 0
    packets_received: int = 0
    bytes_transferred: int = 0

    @property
    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        return (
            self.status == ConnectionStatus.CONNECTED and
            self.latency_ms < 10.0 and
            self.packet_loss_pct < 1.0
        )

    @property
    def quality_score(self) -> float:
        """Calculate connection quality score (0-1)."""
        latency_score = max(0, 1 - (self.latency_ms / 50))
        loss_score = max(0, 1 - (self.packet_loss_pct / 10))
        jitter_score = max(0, 1 - (self.jitter_ms / 5))
        return (latency_score + loss_score + jitter_score) / 3


@dataclass
class BCINode:
    """
    BCI Node - An ONI Firewall system operating at Layer 8.

    Each BCI node represents a discrete monitoring point at the
    Neural Gateway (L8), validating signals as they cross the
    bio-digital boundary.

    Attributes:
        node_id: Unique identifier (e.g., "Node 1")
        name: Display name for the node
        oni_layer: ONI Framework layer (always 8 for Neural Gateway)
        brain_region: Associated brain region (if applicable)
        status: Current operational status
        metrics: Real-time node metrics
        threads: Associated electrode threads
        position: 3D position for visualization (optional)
    """
    node_id: str
    name: str
    oni_layer: int = 8  # Layer 8: Neural Gateway
    brain_region: Optional[str] = None
    status: NodeStatus = NodeStatus.ONLINE
    metrics: NodeMetrics = field(default_factory=NodeMetrics)

    # Physical mapping
    threads: List[str] = field(default_factory=list)  # Thread IDs
    electrode_count: int = 0
    position: Optional[Tuple[float, float, float]] = None  # For visualization

    # Metadata
    firmware_version: str = "1.0.0"
    serial_number: Optional[str] = None
    installed_date: Optional[datetime] = None
    last_calibration: Optional[datetime] = None

    @property
    def layer_name(self) -> str:
        """Get the ONI layer name."""
        return "Neural Gateway"

    @property
    def is_online(self) -> bool:
        """Check if node is online."""
        return self.status == NodeStatus.ONLINE

    @property
    def health_score(self) -> float:
        """Calculate overall node health (0-1)."""
        if self.status == NodeStatus.OFFLINE:
            return 0.0
        if self.status == NodeStatus.INITIALIZING:
            return 0.5

        # Factor in metrics
        coherence_score = self.metrics.avg_coherence
        uptime_score = self.metrics.uptime_pct / 100

        # Impedance score (lower is better, 100-500 kOhm ideal)
        if self.metrics.avg_impedance < 100:
            impedance_score = 0.5
        elif self.metrics.avg_impedance < 500:
            impedance_score = 1.0
        else:
            impedance_score = max(0, 1 - (self.metrics.avg_impedance - 500) / 500)

        # SNR score (higher is better, >10 dB ideal)
        snr_score = min(1.0, self.metrics.avg_snr / 20)

        # Weighted average
        health = (
            coherence_score * 0.3 +
            uptime_score * 0.2 +
            impedance_score * 0.25 +
            snr_score * 0.25
        )

        if self.status == NodeStatus.DEGRADED:
            health *= 0.7
        elif self.status == NodeStatus.WARNING:
            health *= 0.85

        return health

    def process_signal(self, coherence: float) -> str:
        """
        Process a signal through the node's firewall.

        Returns: "pass", "flag", or "block"
        """
        self.metrics.signals_processed += 1
        self.metrics.last_update = datetime.now()

        # Update coherence tracking
        self.metrics.avg_coherence = (
            self.metrics.avg_coherence * 0.95 + coherence * 0.05
        )

        if coherence > 0.6:
            self.metrics.signals_passed += 1
            return "pass"
        elif coherence > 0.3:
            self.metrics.signals_flagged += 1
            return "flag"
        else:
            self.metrics.signals_blocked += 1
            return "block"


class BCINodeNetwork:
    """
    Network of connected BCI nodes forming a distributed ONI Firewall.

    Manages multiple BCI nodes and their interconnections for
    coordinated neural signal monitoring and validation.
    """

    def __init__(self):
        """Initialize an empty node network."""
        self.nodes: Dict[str, BCINode] = {}
        self.connections: List[NodeConnection] = []

    def add_node(self, node: BCINode) -> None:
        """Add a node to the network."""
        self.nodes[node.node_id] = node

    def remove_node(self, node_id: str) -> None:
        """Remove a node and its connections."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            # Remove associated connections
            self.connections = [
                c for c in self.connections
                if c.source_node_id != node_id and c.target_node_id != node_id
            ]

    def connect_nodes(
        self,
        source_id: str,
        target_id: str,
        bidirectional: bool = True,
    ) -> NodeConnection:
        """
        Create a connection between two nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            bidirectional: If True, create connection in both directions

        Returns:
            The created NodeConnection
        """
        connection = NodeConnection(
            source_node_id=source_id,
            target_node_id=target_id,
        )
        self.connections.append(connection)

        if bidirectional:
            reverse = NodeConnection(
                source_node_id=target_id,
                target_node_id=source_id,
            )
            self.connections.append(reverse)

        return connection

    def get_node(self, node_id: str) -> Optional[BCINode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_connections(self, node_id: str) -> List[NodeConnection]:
        """Get all connections for a node."""
        return [
            c for c in self.connections
            if c.source_node_id == node_id or c.target_node_id == node_id
        ]

    def get_connected_nodes(self, node_id: str) -> List[BCINode]:
        """Get all nodes connected to a given node."""
        connected_ids = set()
        for conn in self.connections:
            if conn.source_node_id == node_id:
                connected_ids.add(conn.target_node_id)
            elif conn.target_node_id == node_id:
                connected_ids.add(conn.source_node_id)

        return [self.nodes[nid] for nid in connected_ids if nid in self.nodes]

    @property
    def total_nodes(self) -> int:
        """Total number of nodes in network."""
        return len(self.nodes)

    @property
    def online_nodes(self) -> int:
        """Number of online nodes."""
        return sum(1 for n in self.nodes.values() if n.is_online)

    @property
    def network_health(self) -> float:
        """Overall network health (0-1)."""
        if not self.nodes:
            return 0.0

        node_health = sum(n.health_score for n in self.nodes.values()) / len(self.nodes)

        if self.connections:
            conn_health = sum(c.quality_score for c in self.connections) / len(self.connections)
            return (node_health * 0.7 + conn_health * 0.3)

        return node_health

    def get_topology_data(self) -> Dict:
        """
        Get network topology data for visualization.

        Returns dict with nodes and edges for graph visualization.
        """
        nodes_data = []
        for node in self.nodes.values():
            nodes_data.append({
                "id": node.node_id,
                "name": node.name,
                "status": node.status.value,
                "health": node.health_score,
                "region": node.brain_region,
                "position": node.position,
            })

        edges_data = []
        seen_edges = set()
        for conn in self.connections:
            edge_key = tuple(sorted([conn.source_node_id, conn.target_node_id]))
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edges_data.append({
                    "source": conn.source_node_id,
                    "target": conn.target_node_id,
                    "status": conn.status.value,
                    "quality": conn.quality_score,
                    "latency": conn.latency_ms,
                })

        return {"nodes": nodes_data, "edges": edges_data}


def create_demo_network(n_nodes: int = 4) -> BCINodeNetwork:
    """
    Create a demo BCI node network for testing.

    Creates nodes named "Node 1", "Node 2", etc., with
    connections forming a mesh network.

    Args:
        n_nodes: Number of nodes to create (default: 4)

    Returns:
        Configured BCINodeNetwork
    """
    network = BCINodeNetwork()

    # Brain regions to assign to nodes
    regions = ["M1", "S1", "PMC", "PFC", "SMA", "BROCA"]

    # Create nodes
    for i in range(1, n_nodes + 1):
        region = regions[(i - 1) % len(regions)] if i <= len(regions) else None

        # Simulate some variation in metrics
        metrics = NodeMetrics(
            signals_processed=np.random.randint(1000, 10000),
            signals_passed=np.random.randint(800, 9500),
            signals_blocked=np.random.randint(10, 200),
            signals_flagged=np.random.randint(50, 500),
            avg_coherence=np.random.uniform(0.75, 0.95),
            avg_impedance=np.random.uniform(150, 400),
            avg_snr=np.random.uniform(12, 22),
            latency_ms=np.random.uniform(2, 8),
            throughput_hz=np.random.uniform(28000, 32000),
            uptime_pct=np.random.uniform(98, 100),
        )

        # Ensure consistent counts
        metrics.signals_passed = min(
            metrics.signals_passed,
            metrics.signals_processed - metrics.signals_blocked - metrics.signals_flagged
        )

        # Assign status based on metrics
        if metrics.avg_coherence < 0.7 or metrics.avg_impedance > 600:
            status = NodeStatus.WARNING
        elif metrics.avg_coherence < 0.6:
            status = NodeStatus.DEGRADED
        else:
            status = NodeStatus.ONLINE

        node = BCINode(
            node_id=f"node_{i}",
            name=f"Node {i}",
            brain_region=region,
            status=status,
            metrics=metrics,
            electrode_count=np.random.randint(16, 64),
        )
        network.add_node(node)

    # Create mesh connections (each node connects to adjacent nodes)
    node_ids = list(network.nodes.keys())
    for i, node_id in enumerate(node_ids):
        # Connect to next node (circular)
        next_id = node_ids[(i + 1) % len(node_ids)]
        if node_id != next_id:
            conn = network.connect_nodes(node_id, next_id, bidirectional=True)
            # Simulate connection quality
            conn.latency_ms = np.random.uniform(1, 5)
            conn.packet_loss_pct = np.random.uniform(0, 0.5)
            conn.jitter_ms = np.random.uniform(0.1, 1.0)

    # Add some cross-connections for larger networks
    if n_nodes >= 4:
        # Connect Node 1 to Node 3
        conn = network.connect_nodes(node_ids[0], node_ids[2], bidirectional=True)
        conn.latency_ms = np.random.uniform(2, 6)

    return network
