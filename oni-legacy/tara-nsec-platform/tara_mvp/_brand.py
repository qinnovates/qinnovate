"""
TARA Brand Loader

Loads brand identity from brand.json (single source of truth at repo root).
This allows TARA to access brand constants without requiring oni-framework.

Usage:
    from tara_mvp._brand import TARA, ONI
    print(TARA.name)  # "TARA Stack"
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class ProjectBrand:
    """Immutable brand identity for a project."""
    acronym: str
    full_name: str
    name: str
    slogan: str
    mission: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None


def _load_brand_json() -> dict:
    """Load brand.json from MAIN/legacy-core/resources/brand/."""
    possible_paths = [
        Path(__file__).parent.parent.parent / "resources" / "brand" / "brand.json",  # tara_mvp -> tara-platform -> MAIN/legacy-core/resources/brand
        Path(__file__).parent.parent.parent.parent / "MAIN" / "resources" / "brand" / "brand.json",  # From repo root
        Path(__file__).parent.parent / "resources" / "brand" / "brand.json",  # If restructured
    ]

    for path in possible_paths:
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
    return None


def _create_brand(data: dict) -> ProjectBrand:
    """Create ProjectBrand from JSON data."""
    return ProjectBrand(
        acronym=data.get("acronym", ""),
        full_name=data.get("full_name", ""),
        name=data.get("name", ""),
        tagline=data.get("tagline"),
        slogan=data.get("slogan", ""),
        mission=data.get("mission", ""),
        description=data.get("description"),
        version=data.get("version"),
    )


# Load from brand.json
_brand_data = _load_brand_json()

if _brand_data:
    ONI = _create_brand(_brand_data["oni"])
    TARA = _create_brand(_brand_data["tara"])
    ONI_VERSION = _brand_data["oni"].get("version", "0.2.0")
    TARA_VERSION = _brand_data["tara"].get("version", "0.8.0")
else:
    # Fallback for pip-installed package
    ONI = ProjectBrand(
        acronym="ONI",
        full_name="Open Neurosecurity Interoperability",
        name="ONI Framework",
        tagline="The OSI of Mind",
        slogan="Our minds. Our rules. Our future.",
        mission="The mind is the last frontier.",
        version="0.2.0",
    )
    TARA = ProjectBrand(
        acronym="TARA",
        full_name="Telemetry Analysis & Response Automation",
        name="TARA Stack",
        tagline="Protection for the neural frontier",
        slogan="Named after the Buddhist goddess of protection.",
        mission="Real-time neural security monitoring aligned with ONI.",
        version="0.8.0",
    )
    ONI_VERSION = "0.2.0"
    TARA_VERSION = "0.8.0"

# Quick access
TARA_HEADER = f"{TARA.name} — {TARA.tagline}"
TARA_FOOTER = f"{TARA.name} | {TARA.slogan}"
