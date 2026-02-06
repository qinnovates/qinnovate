"""
TARA Data Models

Data definitions for brain regions, electrode templates,
BCI nodes, export functionality, and external dataset adapters.
"""

from .brain_regions import (
    BrainRegion,
    BRAIN_REGIONS,
    Electrode,
    ElectrodeThread,
    ElectrodeArray,
    ElectrodeStatus,
    get_region_by_oni_layer,
    create_demo_array,
)

from .bci_nodes import (
    BCINode,
    BCINodeNetwork,
    NodeConnection,
    NodeMetrics,
    NodeStatus,
    ConnectionStatus,
    create_demo_network,
)

# MOABB adapter (optional dependency)
from .moabb_adapter import (
    MOABBAdapter,
    BCIParadigm,
    EEGSignal,
    AttackInjectedSignal,
    DatasetInfo,
    is_moabb_available,
    get_moabb_version,
    AVAILABLE_DATASETS,
    SUPPORTED_PARADIGMS,
)

# OpenBCI hardware adapter (optional dependency - requires brainflow)
from .openbci_adapter import (
    OpenBCIAdapter,
    BoardType,
    ConnectionState,
    BoardInfo,
    BOARD_REGISTRY,
    LiveEEGSignal,
    is_brainflow_available,
    get_brainflow_version,
    list_serial_ports,
    SUPPORTED_BOARDS,
)

__all__ = [
    # Brain regions
    "BrainRegion",
    "BRAIN_REGIONS",
    "Electrode",
    "ElectrodeThread",
    "ElectrodeArray",
    "ElectrodeStatus",
    "get_region_by_oni_layer",
    "create_demo_array",
    # BCI Nodes
    "BCINode",
    "BCINodeNetwork",
    "NodeConnection",
    "NodeMetrics",
    "NodeStatus",
    "ConnectionStatus",
    "create_demo_network",
    # MOABB Adapter (external datasets)
    "MOABBAdapter",
    "BCIParadigm",
    "EEGSignal",
    "AttackInjectedSignal",
    "DatasetInfo",
    "is_moabb_available",
    "get_moabb_version",
    "AVAILABLE_DATASETS",
    "SUPPORTED_PARADIGMS",
    # OpenBCI Hardware Adapter
    "OpenBCIAdapter",
    "BoardType",
    "ConnectionState",
    "BoardInfo",
    "BOARD_REGISTRY",
    "LiveEEGSignal",
    "is_brainflow_available",
    "get_brainflow_version",
    "list_serial_ports",
    "SUPPORTED_BOARDS",
]
