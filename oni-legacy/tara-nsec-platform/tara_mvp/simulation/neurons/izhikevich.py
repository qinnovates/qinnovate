"""
Izhikevich Neuron Model

A computationally efficient model that can reproduce many
biological spiking patterns including:
- Regular spiking (RS)
- Intrinsically bursting (IB)
- Chattering (CH)
- Fast spiking (FS)
- Low-threshold spiking (LTS)
- And more...

Equations:
    dv/dt = 0.04v² + 5v + 140 - u + I
    du/dt = a(bv - u)

When v >= 30mV:
    v = c
    u = u + d

Reference:
    Izhikevich, E.M. (2003). Simple Model of Spiking Neurons.
    IEEE Transactions on Neural Networks, 14(6), 1569-1572.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from enum import Enum
import numpy as np

from .base import Neuron, NeuronParameters, NeuronType


class IzhikevichType(Enum):
    """Predefined Izhikevich neuron types."""
    REGULAR_SPIKING = "RS"           # Regular spiking excitatory
    INTRINSIC_BURSTING = "IB"        # Intrinsically bursting
    CHATTERING = "CH"                # Chattering
    FAST_SPIKING = "FS"              # Fast spiking inhibitory
    LOW_THRESHOLD_SPIKING = "LTS"    # Low-threshold spiking
    THALAMO_CORTICAL = "TC"          # Thalamo-cortical
    RESONATOR = "RZ"                 # Resonator
    CUSTOM = "custom"                # Custom parameters


# Predefined parameter sets for different neuron types
IZHIKEVICH_PRESETS: Dict[IzhikevichType, Tuple[float, float, float, float]] = {
    # (a, b, c, d)
    IzhikevichType.REGULAR_SPIKING: (0.02, 0.2, -65.0, 8.0),
    IzhikevichType.INTRINSIC_BURSTING: (0.02, 0.2, -55.0, 4.0),
    IzhikevichType.CHATTERING: (0.02, 0.2, -50.0, 2.0),
    IzhikevichType.FAST_SPIKING: (0.1, 0.2, -65.0, 2.0),
    IzhikevichType.LOW_THRESHOLD_SPIKING: (0.02, 0.25, -65.0, 2.0),
    IzhikevichType.THALAMO_CORTICAL: (0.02, 0.25, -65.0, 0.05),
    IzhikevichType.RESONATOR: (0.1, 0.26, -65.0, 2.0),
}


@dataclass
class IzhikevichParameters(NeuronParameters):
    """Parameters for Izhikevich neuron model."""

    # Model parameters
    a: float = 0.02   # Time scale of recovery variable u
    b: float = 0.2    # Sensitivity of u to subthreshold V
    c: float = -65.0  # After-spike reset value for V (mV)
    d: float = 8.0    # After-spike reset increment for u

    # Initial conditions
    V_init: float = -65.0  # Initial membrane potential (mV)
    u_init: float = None   # Initial recovery variable (computed if None)

    # Spike threshold (fixed for Izhikevich model)
    V_peak: float = 30.0   # Spike cutoff (mV)

    # Noise
    noise_std: float = 0.0

    # Preset type (for documentation/UI)
    preset: IzhikevichType = IzhikevichType.REGULAR_SPIKING

    def __post_init__(self):
        """Initialize derived values."""
        if self.u_init is None:
            self.u_init = self.b * self.V_init

    @classmethod
    def from_preset(cls, preset: IzhikevichType, **kwargs) -> "IzhikevichParameters":
        """Create parameters from preset type."""
        if preset not in IZHIKEVICH_PRESETS:
            raise ValueError(f"Unknown preset: {preset}")

        a, b, c, d = IZHIKEVICH_PRESETS[preset]
        return cls(a=a, b=b, c=c, d=d, preset=preset, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "a": self.a,
            "b": self.b,
            "c": self.c,
            "d": self.d,
            "V_init": self.V_init,
            "V_peak": self.V_peak,
            "noise_std": self.noise_std,
            "preset": self.preset.value,
        })
        return base


class IzhikevichNeuron(Neuron):
    """
    Izhikevich Neuron Model.

    Combines computational efficiency with rich dynamics.
    Can reproduce over 20 different firing patterns seen in
    biological neurons by adjusting 4 parameters.

    Usage:
        >>> # Regular spiking neuron
        >>> neuron = IzhikevichNeuron.from_preset(IzhikevichType.REGULAR_SPIKING)
        >>> results = neuron.simulate(500, input_current=np.ones(5000) * 10.0)

        >>> # Fast spiking inhibitory
        >>> fs_neuron = IzhikevichNeuron.from_preset(IzhikevichType.FAST_SPIKING)
    """

    def __init__(self, params: Optional[IzhikevichParameters] = None):
        """
        Initialize Izhikevich neuron.

        Args:
            params: Model parameters (uses RS defaults if None)
        """
        super().__init__(params or IzhikevichParameters())

        # Initialize state
        self.state.V = self.params.V_init
        self.u = self.params.u_init  # Recovery variable
        self.u_history = []  # Track recovery variable

    @property
    def params(self) -> IzhikevichParameters:
        """Type-hinted access to parameters."""
        return self._params

    @params.setter
    def params(self, value: IzhikevichParameters):
        self._params = value

    def get_V_rest(self) -> float:
        """Get resting membrane potential."""
        return self.params.V_init

    def _compute_dV(self, I_total: float) -> float:
        """
        Compute membrane potential change using Izhikevich dynamics.

        Note: This also updates the recovery variable u.
        """
        p = self.params
        dt = p.dt
        V = self.state.V
        u = self.u

        # Izhikevich equations (using 0.5ms substeps for stability)
        # dv/dt = 0.04v² + 5v + 140 - u + I
        # du/dt = a(bv - u)

        for _ in range(2):  # Two 0.5dt substeps
            dV = (0.04 * V**2 + 5 * V + 140 - u + I_total) * (dt / 2)
            du = p.a * (p.b * V - u) * (dt / 2)

            V += dV
            u += du

        # Add noise if specified
        if p.noise_std > 0:
            V += np.random.normal(0, p.noise_std * np.sqrt(dt))

        # Store updated u
        self.u = u

        # Return change from original V
        return V - self.state.V

    def _check_spike(self) -> bool:
        """Check if membrane potential exceeds peak."""
        return self.state.V >= self.params.V_peak

    def _reset_after_spike(self):
        """Reset V and increment u after spike."""
        self.state.V = self.params.c
        self.u += self.params.d

    def step(self, record_history: bool = True) -> bool:
        """Override step to also record u history."""
        result = super().step(record_history)
        if record_history:
            self.u_history.append(self.u)
        return result

    def reset(self):
        """Reset neuron to initial state."""
        super().reset()
        self.u = self.params.u_init
        self.u_history = []

    def simulate(
        self,
        duration: float,
        input_current: Optional[np.ndarray] = None,
        record_history: bool = True
    ) -> Dict[str, np.ndarray]:
        """Run simulation and include u variable in results."""
        results = super().simulate(duration, input_current, record_history)
        if record_history:
            results["u"] = np.array(self.u_history)
        return results

    @classmethod
    def from_preset(
        cls,
        preset: IzhikevichType,
        **kwargs
    ) -> "IzhikevichNeuron":
        """
        Create neuron from predefined type.

        Args:
            preset: One of the IzhikevichType presets
            **kwargs: Additional parameter overrides

        Returns:
            Configured IzhikevichNeuron
        """
        params = IzhikevichParameters.from_preset(preset, **kwargs)
        return cls(params)

    @classmethod
    def create_random(
        cls,
        excitatory: bool = True,
        **kwargs
    ) -> "IzhikevichNeuron":
        """
        Create neuron with random parameters within typical ranges.

        Used for creating heterogeneous populations.
        """
        if excitatory:
            # Excitatory: random between RS and IB
            r = np.random.random()
            a = 0.02
            b = 0.2
            c = -65.0 + 15 * r**2
            d = 8.0 - 6 * r**2
        else:
            # Inhibitory: random between FS and LTS
            r = np.random.random()
            a = 0.02 + 0.08 * r
            b = 0.25 - 0.05 * r
            c = -65.0
            d = 2.0

        params = IzhikevichParameters(
            a=a, b=b, c=c, d=d,
            preset=IzhikevichType.CUSTOM,
            **kwargs
        )
        return cls(params)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize neuron to dictionary."""
        data = super().to_dict()
        data["state"]["u"] = self.u
        return data


def create_izhikevich_population(
    n: int,
    excitatory_ratio: float = 0.8,
    heterogeneous: bool = True
) -> list:
    """
    Create a population of Izhikevich neurons.

    Args:
        n: Number of neurons
        excitatory_ratio: Fraction of excitatory neurons
        heterogeneous: If True, use random parameters; if False, use presets

    Returns:
        List of IzhikevichNeuron instances
    """
    neurons = []
    n_excitatory = int(n * excitatory_ratio)

    for i in range(n):
        is_excitatory = i < n_excitatory

        if heterogeneous:
            neuron = IzhikevichNeuron.create_random(excitatory=is_excitatory)
        else:
            preset = (
                IzhikevichType.REGULAR_SPIKING if is_excitatory
                else IzhikevichType.FAST_SPIKING
            )
            neuron = IzhikevichNeuron.from_preset(preset)

        neurons.append(neuron)

    return neurons
