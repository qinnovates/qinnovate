"""
ONI Framework Layer Model

Implements the 14-layer Open Neurosecurity Interoperability model that extends
the OSI networking model into biological neural systems.

===============================================================================
IMPORTANT: FOR NON-TECHNICAL COLLABORATORS
===============================================================================
This module defines a conceptual MODEL — think of it as a map or blueprint.

WHAT IT IS:
A way to organize and talk about the different "layers" between a brain and
a computer. Just like a building has floors, the ONI Framework has 14 layers.

WHY 14 LAYERS?
The traditional OSI network model (used in internet/networking) has 7 layers.
ONI extends this with:
- 7 biological layers (brain side: molecules → cells → behavior)
- 1 bridge layer (where electrodes meet neurons)
- 6 silicon layers (computer side: signals → applications)

THIS IS A REFERENCE MODEL, NOT SIGNAL PROCESSING:
This module doesn't calculate anything about signals. It's a vocabulary tool
that helps researchers and engineers agree on terminology:
- "The attack happened at Layer 8" = the electrode interface
- "We need defenses at Layer 3" = local neural circuits

HOW TO USE IT:
- Explore the model with stack.ascii_diagram()
- Look up attack surfaces for each layer
- Use as a framework for discussing BCI security

Nothing here connects to hardware. It's purely educational and organizational.
===============================================================================

Layers 1-7:  Biological domain (molecular to behavioral)
Layer 8:     Neural Gateway (bio-digital boundary, firewall location)
Layers 9-14: Silicon domain (signal processing to application)

Reference: TechDoc-ONI_Framework.md
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any


class Domain(Enum):
    """Domain classification for ONI layers."""
    BIOLOGICAL = auto()
    BRIDGE = auto()
    SILICON = auto()


@dataclass
class Layer:
    """
    Represents a single layer in the ONI Framework.

    Attributes:
        number: Layer number (1-14)
        name: Layer name
        domain: Domain classification (biological, bridge, silicon)
        function: Primary function description
        attack_surfaces: Known attack vectors at this layer
        defenses: Recommended security measures
    """
    number: int
    name: str
    domain: Domain
    function: str
    attack_surfaces: List[str] = field(default_factory=list)
    defenses: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"Layer({self.number}, '{self.name}', {self.domain.name})"

    @property
    def is_biological(self) -> bool:
        return self.domain == Domain.BIOLOGICAL

    @property
    def is_bridge(self) -> bool:
        return self.domain == Domain.BRIDGE

    @property
    def is_silicon(self) -> bool:
        return self.domain == Domain.SILICON


class ONIStack:
    """
    The complete 14-layer ONI Framework model.

    Extends OSI's 7-layer network model into biological neural systems,
    creating a unified architecture for brain-computer interface security.

    Example:
        >>> stack = ONIStack()
        >>> print(stack.layer(8))  # Neural Gateway
        >>> for layer in stack.biological_layers():
        ...     print(f"L{layer.number}: {layer.name}")
    """

    def __init__(self):
        """Initialize the ONI stack with all 14 layers."""
        self._layers: Dict[int, Layer] = {}
        self._build_stack()

    def _build_stack(self):
        """Build the complete 14-layer ONI stack."""

        # Biological Domain (L1-L7)
        self._layers[1] = Layer(
            number=1,
            name="Molecular",
            domain=Domain.BIOLOGICAL,
            function="Ion channels, neurotransmitters, molecular signaling",
            attack_surfaces=["Ion channel manipulation", "Neurotransmitter interference"],
            defenses=["Receptor specificity", "Enzymatic degradation"],
        )

        self._layers[2] = Layer(
            number=2,
            name="Cellular",
            domain=Domain.BIOLOGICAL,
            function="Action potentials, synaptic transmission",
            attack_surfaces=["Membrane potential manipulation", "Synaptic flooding"],
            defenses=["Refractory periods", "Synaptic fatigue"],
        )

        self._layers[3] = Layer(
            number=3,
            name="Microcircuit",
            domain=Domain.BIOLOGICAL,
            function="Local neural computation, pattern generation",
            attack_surfaces=["Local circuit hijacking", "Oscillation disruption"],
            defenses=["Lateral inhibition", "Homeostatic plasticity"],
        )

        self._layers[4] = Layer(
            number=4,
            name="Regional",
            domain=Domain.BIOLOGICAL,
            function="Brain region specialization, modular processing",
            attack_surfaces=["Region-specific targeting", "Cross-region desynchronization"],
            defenses=["Functional redundancy", "Region isolation"],
        )

        self._layers[5] = Layer(
            number=5,
            name="Systems",
            domain=Domain.BIOLOGICAL,
            function="Distributed neural networks, system integration",
            attack_surfaces=["Network topology attacks", "Hub disruption"],
            defenses=["Network redundancy", "Dynamic routing"],
        )

        self._layers[6] = Layer(
            number=6,
            name="Whole-Brain",
            domain=Domain.BIOLOGICAL,
            function="Global integration patterns, consciousness",
            attack_surfaces=["Global state manipulation", "Consciousness interference"],
            defenses=["Integration thresholds", "State monitoring"],
        )

        self._layers[7] = Layer(
            number=7,
            name="Behavioral",
            domain=Domain.BIOLOGICAL,
            function="Observable outputs, motor commands, behavior",
            attack_surfaces=["Motor hijacking", "Behavioral manipulation"],
            defenses=["Volitional override", "Behavioral anomaly detection"],
        )

        # Bridge Layer (L8)
        self._layers[8] = Layer(
            number=8,
            name="Neural Gateway",
            domain=Domain.BRIDGE,
            function="BCI hardware boundary, electrode interface, FIREWALL LOCATION",
            attack_surfaces=[
                "Signal injection", "Electrode tampering", "Side-channel attacks",
                "RF interference", "Firmware exploits"
            ],
            defenses=[
                "Coherence validation", "Hardware bounds", "Signal authentication",
                "Anomaly detection", "Rate limiting"
            ],
            metadata={"firewall_layer": True, "critical": True},
        )

        # Silicon Domain (L9-L14)
        self._layers[9] = Layer(
            number=9,
            name="Signal Processing",
            domain=Domain.SILICON,
            function="Filtering, amplification, digitization",
            attack_surfaces=["Filter bypass", "ADC manipulation", "Gain attacks"],
            defenses=["Hardware limits", "Calibration verification"],
        )

        self._layers[10] = Layer(
            number=10,
            name="Protocol",
            domain=Domain.SILICON,
            function="Data formatting, transmission rules",
            attack_surfaces=["Protocol exploits", "Packet injection", "Replay attacks"],
            defenses=["Protocol validation", "Sequence checking", "Cryptographic signing"],
        )

        self._layers[11] = Layer(
            number=11,
            name="Transport",
            domain=Domain.SILICON,
            function="Reliable data delivery",
            attack_surfaces=["Connection hijacking", "DoS attacks", "MITM"],
            defenses=["Encryption", "Authentication", "Connection monitoring"],
        )

        self._layers[12] = Layer(
            number=12,
            name="Session",
            domain=Domain.SILICON,
            function="Connection management, state tracking",
            attack_surfaces=["Session hijacking", "State manipulation"],
            defenses=["Session tokens", "State validation", "Timeout enforcement"],
        )

        self._layers[13] = Layer(
            number=13,
            name="Presentation",
            domain=Domain.SILICON,
            function="Data interpretation, format conversion",
            attack_surfaces=["Data corruption", "Format exploits"],
            defenses=["Format validation", "Integrity checks"],
        )

        self._layers[14] = Layer(
            number=14,
            name="Application",
            domain=Domain.SILICON,
            function="End-user interfaces, clinical applications",
            attack_surfaces=["UI manipulation", "Application exploits", "Social engineering"],
            defenses=["Access control", "Audit logging", "User verification"],
        )

    def layer(self, number: int) -> Layer:
        """
        Get a specific layer by number.

        Args:
            number: Layer number (1-14)

        Returns:
            Layer object

        Raises:
            KeyError: If layer number is invalid
        """
        if number not in self._layers:
            raise KeyError(f"Invalid layer number: {number}. Must be 1-14.")
        return self._layers[number]

    def __getitem__(self, number: int) -> Layer:
        """Allow indexing: stack[8] returns Layer 8."""
        return self.layer(number)

    def __iter__(self):
        """Iterate through all layers in order."""
        for i in range(1, 15):
            yield self._layers[i]

    def __len__(self) -> int:
        return 14

    def biological_layers(self) -> List[Layer]:
        """Return all biological domain layers (L1-L7)."""
        return [self._layers[i] for i in range(1, 8)]

    def silicon_layers(self) -> List[Layer]:
        """Return all silicon domain layers (L9-L14)."""
        return [self._layers[i] for i in range(9, 15)]

    def bridge_layer(self) -> Layer:
        """Return the bridge layer (L8 - Neural Gateway)."""
        return self._layers[8]

    def firewall_layer(self) -> Layer:
        """Return the firewall layer (L8 - Neural Gateway)."""
        return self._layers[8]

    def get_attack_surfaces(self, layer_range: Optional[tuple] = None) -> Dict[int, List[str]]:
        """
        Get attack surfaces for specified layers.

        Args:
            layer_range: Optional (start, end) tuple, defaults to all layers

        Returns:
            Dict mapping layer numbers to attack surface lists
        """
        start, end = layer_range or (1, 14)
        return {
            i: self._layers[i].attack_surfaces
            for i in range(start, end + 1)
        }

    def get_defenses(self, layer_range: Optional[tuple] = None) -> Dict[int, List[str]]:
        """
        Get defenses for specified layers.

        Args:
            layer_range: Optional (start, end) tuple, defaults to all layers

        Returns:
            Dict mapping layer numbers to defense lists
        """
        start, end = layer_range or (1, 14)
        return {
            i: self._layers[i].defenses
            for i in range(start, end + 1)
        }

    def ascii_diagram(self) -> str:
        """Generate an ASCII representation of the ONI stack."""
        lines = [
            "┌────────────────────────────────────────────────┐",
            "│              ONI FRAMEWORK (L1-L14)            │",
            "├────────────────────────────────────────────────┤",
        ]

        for layer in reversed(list(self)):
            domain_marker = {
                Domain.BIOLOGICAL: "BIO",
                Domain.BRIDGE: ">>>",
                Domain.SILICON: "SIL",
            }[layer.domain]

            # Highlight firewall layer
            if layer.number == 8:
                lines.append(f"│ L{layer.number:2d} │ {domain_marker} │ *** {layer.name.upper():14} *** │")
            else:
                lines.append(f"│ L{layer.number:2d} │ {domain_marker} │ {layer.name:22} │")

        lines.append("└────────────────────────────────────────────────┘")
        return "\n".join(lines)

    def summary(self) -> str:
        """Generate a text summary of the stack."""
        bio_count = len(self.biological_layers())
        sil_count = len(self.silicon_layers())
        total_attacks = sum(len(l.attack_surfaces) for l in self)
        total_defenses = sum(len(l.defenses) for l in self)

        return (
            f"ONI Framework Summary:\n"
            f"  Total Layers: 14\n"
            f"  Biological (L1-L7): {bio_count} layers\n"
            f"  Bridge (L8): Neural Gateway (Firewall)\n"
            f"  Silicon (L9-L14): {sil_count} layers\n"
            f"  Attack Surfaces: {total_attacks}\n"
            f"  Defenses: {total_defenses}"
        )
