"""
Brain Region and BCI Node Definitions

Defines brain regions commonly targeted by brain-computer interfaces,
along with electrode/node data structures for visualization.

Coordinates are in millimeters, using MNI (Montreal Neurological Institute)
standard space conventions:
- X: Left (-) to Right (+)
- Y: Posterior (-) to Anterior (+)
- Z: Inferior (-) to Superior (+)

BCI node specifications are derived from published research on various
BCI systems including Utah arrays, ECoG grids, and thread-based implants.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto


class RegionFunction(Enum):
    """Primary function of a brain region."""
    MOTOR = auto()           # Movement control
    SENSORY = auto()         # Sensory processing
    COGNITIVE = auto()       # Higher cognition
    LANGUAGE = auto()        # Speech and language
    VISUAL = auto()          # Visual processing
    AUDITORY = auto()        # Auditory processing
    MEMORY = auto()          # Memory formation
    EXECUTIVE = auto()       # Executive function


class ElectrodeStatus(Enum):
    """Status of an individual electrode."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


@dataclass
class BrainRegion:
    """
    Defines a brain region for BCI node visualization.

    Attributes:
        name: Full anatomical name
        abbreviation: Short code (e.g., M1, S1)
        center: (x, y, z) coordinates in mm (MNI space)
        radius: Approximate region radius in mm
        color: Hex color for visualization
        oni_layer: Corresponding ONI layer (1-14)
        function: Primary function category
        description: Brief description of region function
        bci_relevance: Why this region is targeted by BCIs
    """
    name: str
    abbreviation: str
    center: Tuple[float, float, float]
    radius: float
    color: str
    oni_layer: int
    function: RegionFunction
    description: str
    bci_relevance: str = ""


# Standard brain regions targeted by BCI systems
BRAIN_REGIONS: Dict[str, BrainRegion] = {
    "M1": BrainRegion(
        name="Primary Motor Cortex",
        abbreviation="M1",
        center=(-35.0, -20.0, 55.0),
        radius=15.0,
        color="#ef4444",  # Red
        oni_layer=13,  # Whole-Brain Networks (motor intention)
        function=RegionFunction.MOTOR,
        description="Controls voluntary movement execution",
        bci_relevance="Primary target for motor BCIs; decodes movement intention",
    ),
    "S1": BrainRegion(
        name="Primary Somatosensory Cortex",
        abbreviation="S1",
        center=(-35.0, -35.0, 50.0),
        radius=12.0,
        color="#3b82f6",  # Blue
        oni_layer=12,  # Regional Processing
        function=RegionFunction.SENSORY,
        description="Processes tactile and proprioceptive information",
        bci_relevance="Target for sensory feedback; enables closed-loop control",
    ),
    "PMC": BrainRegion(
        name="Premotor Cortex",
        abbreviation="PMC",
        center=(-45.0, 5.0, 50.0),
        radius=12.0,
        color="#f97316",  # Orange
        oni_layer=13,
        function=RegionFunction.MOTOR,
        description="Movement planning and preparation",
        bci_relevance="Complements M1 for enhanced movement prediction",
    ),
    "SMA": BrainRegion(
        name="Supplementary Motor Area",
        abbreviation="SMA",
        center=(0.0, -5.0, 60.0),
        radius=10.0,
        color="#eab308",  # Yellow
        oni_layer=13,
        function=RegionFunction.MOTOR,
        description="Sequential movement planning, bilateral coordination",
        bci_relevance="Decoding complex movement sequences",
    ),
    "PFC": BrainRegion(
        name="Prefrontal Cortex",
        abbreviation="PFC",
        center=(35.0, 45.0, 25.0),
        radius=20.0,
        color="#8b5cf6",  # Purple
        oni_layer=14,  # Identity & Ethics
        function=RegionFunction.EXECUTIVE,
        description="Executive function, decision making, working memory",
        bci_relevance="Cognitive state decoding; attention and intent",
    ),
    "BROCA": BrainRegion(
        name="Broca's Area",
        abbreviation="BROCA",
        center=(-50.0, 20.0, 15.0),
        radius=8.0,
        color="#ec4899",  # Pink
        oni_layer=14,
        function=RegionFunction.LANGUAGE,
        description="Speech production and language processing",
        bci_relevance="Speech BCIs; decoding intended speech",
    ),
    "WERNICKE": BrainRegion(
        name="Wernicke's Area",
        abbreviation="WERNICKE",
        center=(-55.0, -55.0, 20.0),
        radius=10.0,
        color="#d946ef",  # Fuchsia
        oni_layer=14,
        function=RegionFunction.LANGUAGE,
        description="Language comprehension",
        bci_relevance="Understanding speech intent; language BCIs",
    ),
    "V1": BrainRegion(
        name="Primary Visual Cortex",
        abbreviation="V1",
        center=(0.0, -85.0, 5.0),
        radius=15.0,
        color="#06b6d4",  # Cyan
        oni_layer=12,
        function=RegionFunction.VISUAL,
        description="Primary visual processing",
        bci_relevance="Visual prosthetics; phosphene generation",
    ),
    "A1": BrainRegion(
        name="Primary Auditory Cortex",
        abbreviation="A1",
        center=(-55.0, -20.0, 10.0),
        radius=8.0,
        color="#14b8a6",  # Teal
        oni_layer=12,
        function=RegionFunction.AUDITORY,
        description="Primary auditory processing",
        bci_relevance="Auditory BCIs; cochlear implant integration",
    ),
    "HIPP": BrainRegion(
        name="Hippocampus",
        abbreviation="HIPP",
        center=(-25.0, -20.0, -15.0),
        radius=8.0,
        color="#22c55e",  # Green
        oni_layer=11,  # Circuit Dynamics
        function=RegionFunction.MEMORY,
        description="Memory formation and spatial navigation",
        bci_relevance="Memory prosthetics; seizure detection/prevention",
    ),
}


@dataclass
class Electrode:
    """
    Individual electrode/recording site on a BCI node.

    Attributes:
        electrode_id: Unique identifier (e.g., "T01-E05")
        position: (x, y, z) coordinates in mm
        depth: Depth from cortical surface in mm
        thread_id: Parent thread/shank identifier
        region: Brain region abbreviation

        # Real-time metrics (updated during monitoring)
        spike_rate: Firing rate in Hz
        lfp_power: Local field potential power (normalized)
        impedance: Electrode impedance in kOhms
        snr: Signal-to-noise ratio in dB
        status: Current electrode status
    """
    electrode_id: str
    position: Tuple[float, float, float]
    depth: float = 0.0
    thread_id: str = ""
    region: str = ""

    # Real-time metrics
    spike_rate: float = 0.0
    lfp_power: float = 0.0
    impedance: float = 300.0  # kOhms (typical healthy range: 100-500)
    snr: float = 10.0         # dB (acceptable: >5)
    status: ElectrodeStatus = ElectrodeStatus.NORMAL

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "electrode_id": self.electrode_id,
            "position": self.position,
            "depth": self.depth,
            "thread_id": self.thread_id,
            "region": self.region,
            "spike_rate": self.spike_rate,
            "lfp_power": self.lfp_power,
            "impedance": self.impedance,
            "snr": self.snr,
            "status": self.status.value,
        }

    def is_healthy(self) -> bool:
        """Check if electrode is within healthy operating parameters."""
        return (
            self.status == ElectrodeStatus.NORMAL
            and 100 <= self.impedance <= 500
            and self.snr >= 5
        )


@dataclass
class ElectrodeThread:
    """
    A thread/shank of electrodes (common in thread-based BCIs).

    Thread-based BCIs (e.g., Neuralink N1) use flexible polymer threads
    with multiple electrodes distributed along their length.

    Typical specs (derived from published research):
    - 16-32 electrodes per thread
    - 3-8mm insertion depth
    - 50-100 micron inter-electrode spacing
    """
    thread_id: str
    region: str
    insertion_point: Tuple[float, float, float]
    direction: Tuple[float, float, float]  # Unit vector pointing into cortex
    electrodes: List[Electrode] = field(default_factory=list)

    # Thread metrics
    active_electrodes: int = 0
    avg_impedance: float = 0.0
    avg_snr: float = 0.0

    def update_metrics(self) -> None:
        """Update aggregate thread metrics from electrodes."""
        if not self.electrodes:
            return

        self.active_electrodes = sum(
            1 for e in self.electrodes if e.status != ElectrodeStatus.OFFLINE
        )

        active = [e for e in self.electrodes if e.status != ElectrodeStatus.OFFLINE]
        if active:
            self.avg_impedance = sum(e.impedance for e in active) / len(active)
            self.avg_snr = sum(e.snr for e in active) / len(active)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "thread_id": self.thread_id,
            "region": self.region,
            "insertion_point": self.insertion_point,
            "direction": self.direction,
            "electrodes": [e.to_dict() for e in self.electrodes],
            "active_electrodes": self.active_electrodes,
            "avg_impedance": self.avg_impedance,
            "avg_snr": self.avg_snr,
        }


@dataclass
class ElectrodeArray:
    """
    Complete BCI electrode array configuration.

    Supports various BCI form factors:
    - Thread-based: Multiple flexible threads (e.g., Neuralink N1)
    - Utah array: Rigid grid of microelectrodes
    - ECoG: Surface electrode grids
    - Depth electrodes: Stereo-EEG style

    Example configurations (derived from published specs):
    - Thread-based: 64 threads x 32 electrodes = 2048 total
    - Utah array: 10x10 grid = 100 electrodes
    - ECoG grid: 8x8 = 64 electrodes
    """
    array_id: str
    name: str
    array_type: str  # "thread", "utah", "ecog", "depth"
    threads: List[ElectrodeThread] = field(default_factory=list)

    # Array-level metrics
    total_electrodes: int = 0
    active_electrodes: int = 0
    regions_covered: List[str] = field(default_factory=list)

    def update_metrics(self) -> None:
        """Update aggregate array metrics."""
        self.total_electrodes = sum(len(t.electrodes) for t in self.threads)

        for thread in self.threads:
            thread.update_metrics()

        self.active_electrodes = sum(t.active_electrodes for t in self.threads)
        self.regions_covered = list(set(t.region for t in self.threads if t.region))

    def get_electrodes_by_region(self, region: str) -> List[Electrode]:
        """Get all electrodes in a specific brain region."""
        electrodes = []
        for thread in self.threads:
            if thread.region == region:
                electrodes.extend(thread.electrodes)
        return electrodes

    def get_threads_by_region(self, region: str) -> List[ElectrodeThread]:
        """Get all threads in a specific brain region."""
        return [t for t in self.threads if t.region == region]

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "array_id": self.array_id,
            "name": self.name,
            "array_type": self.array_type,
            "threads": [t.to_dict() for t in self.threads],
            "total_electrodes": self.total_electrodes,
            "active_electrodes": self.active_electrodes,
            "regions_covered": self.regions_covered,
        }


def get_region_by_oni_layer(layer: int) -> List[BrainRegion]:
    """Get brain regions mapped to a specific ONI layer."""
    return [r for r in BRAIN_REGIONS.values() if r.oni_layer == layer]


def create_demo_array(
    n_threads_per_region: int = 4,
    n_electrodes_per_thread: int = 16,
    regions: List[str] = None,
) -> ElectrodeArray:
    """
    Create a demonstration electrode array for visualization.

    Args:
        n_threads_per_region: Number of threads per brain region
        n_electrodes_per_thread: Electrodes per thread
        regions: List of region abbreviations (default: M1, S1)

    Returns:
        Configured ElectrodeArray
    """
    import numpy as np

    if regions is None:
        regions = ["M1", "S1"]

    array = ElectrodeArray(
        array_id="DEMO-001",
        name="Demo BCI Array",
        array_type="thread",
    )

    for region_abbr in regions:
        if region_abbr not in BRAIN_REGIONS:
            continue

        region = BRAIN_REGIONS[region_abbr]
        cx, cy, cz = region.center

        for t_idx in range(n_threads_per_region):
            # Distribute threads around region center
            angle = 2 * np.pi * t_idx / n_threads_per_region
            offset_x = region.radius * 0.5 * np.cos(angle)
            offset_y = region.radius * 0.5 * np.sin(angle)

            insertion = (cx + offset_x, cy + offset_y, cz)
            direction = (0.0, 0.0, -1.0)  # Pointing down into cortex

            thread = ElectrodeThread(
                thread_id=f"{region_abbr}-T{t_idx:02d}",
                region=region_abbr,
                insertion_point=insertion,
                direction=direction,
            )

            # Create electrodes along thread
            for e_idx in range(n_electrodes_per_thread):
                depth = 0.5 + (e_idx * 0.25)  # 0.5mm to ~4mm depth
                pos = (
                    insertion[0],
                    insertion[1],
                    insertion[2] - depth,
                )

                electrode = Electrode(
                    electrode_id=f"{thread.thread_id}-E{e_idx:02d}",
                    position=pos,
                    depth=depth,
                    thread_id=thread.thread_id,
                    region=region_abbr,
                    # Simulate realistic initial values
                    spike_rate=np.random.uniform(5, 30),
                    lfp_power=np.random.uniform(0.3, 0.8),
                    impedance=np.random.uniform(200, 400),
                    snr=np.random.uniform(8, 15),
                    status=ElectrodeStatus.NORMAL,
                )
                thread.electrodes.append(electrode)

            array.threads.append(thread)

    array.update_metrics()
    return array
