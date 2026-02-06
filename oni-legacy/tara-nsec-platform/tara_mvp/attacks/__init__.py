"""
TARA Attack Simulator Module

Simulates various neural attack patterns for security testing:
- Attack pattern definitions
- Attack signal generation
- Predefined attack scenarios
- Attack injection into simulations
"""

from .patterns import AttackPattern, AttackType
from .generator import AttackGenerator
from .scenarios import AttackScenario, PREDEFINED_SCENARIOS
from .simulator import AttackSimulator

__all__ = [
    "AttackPattern",
    "AttackType",
    "AttackGenerator",
    "AttackScenario",
    "AttackSimulator",
    "PREDEFINED_SCENARIOS",
]
