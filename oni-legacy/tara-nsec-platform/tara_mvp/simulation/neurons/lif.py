"""
Leaky Integrate-and-Fire (LIF) Neuron Model

The simplest spiking neuron model. Computationally efficient,
suitable for large-scale network simulations.

Equation:
    τ_m * dV/dt = -(V - V_rest) + R_m * I

When V >= V_threshold:
    - Emit spike
    - V = V_reset
    - Enter refractory period
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import numpy as np

from .base import Neuron, NeuronParameters, NeuronState, NeuronType


@dataclass
class LIFParameters(NeuronParameters):
    """Parameters for Leaky Integrate-and-Fire neuron."""

    # Membrane properties
    R_m: float = 10.0  # Membrane resistance (MΩ)
    C_m: float = 1.0   # Membrane capacitance (nF)
    tau_m: float = None  # Membrane time constant (ms), computed from R*C

    # Voltage thresholds
    V_rest: float = -65.0      # Resting potential (mV)
    V_threshold: float = -50.0  # Spike threshold (mV)
    V_reset: float = -65.0      # Reset potential after spike (mV)

    # Refractory period
    t_refractory: float = 2.0  # Absolute refractory period (ms)

    # Noise
    noise_std: float = 0.0  # Gaussian noise standard deviation (mV)

    def __post_init__(self):
        """Compute derived parameters."""
        if self.tau_m is None:
            self.tau_m = self.R_m * self.C_m

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "R_m": self.R_m,
            "C_m": self.C_m,
            "tau_m": self.tau_m,
            "V_rest": self.V_rest,
            "V_threshold": self.V_threshold,
            "V_reset": self.V_reset,
            "t_refractory": self.t_refractory,
            "noise_std": self.noise_std,
        })
        return base


class LIFNeuron(Neuron):
    """
    Leaky Integrate-and-Fire Neuron.

    Simple point neuron model with exponential decay toward rest
    and instantaneous spike generation at threshold.

    Usage:
        >>> neuron = LIFNeuron()
        >>> results = neuron.simulate(100, input_current=np.ones(1000) * 2.0)
        >>> print(f"Fired {len(results['spike_times'])} spikes")
    """

    def __init__(self, params: Optional[LIFParameters] = None):
        """
        Initialize LIF neuron.

        Args:
            params: LIF parameters (uses defaults if None)
        """
        super().__init__(params or LIFParameters())
        self.state.V = self.params.V_rest

    @property
    def params(self) -> LIFParameters:
        """Type-hinted access to parameters."""
        return self._params

    @params.setter
    def params(self, value: LIFParameters):
        self._params = value

    def get_V_rest(self) -> float:
        """Get resting membrane potential."""
        return self.params.V_rest

    def _compute_dV(self, I_total: float) -> float:
        """
        Compute membrane potential change using LIF dynamics.

        dV/dt = (-(V - V_rest) + R_m * I) / tau_m
        """
        p = self.params
        dt = p.dt

        # LIF equation
        dV = (-(self.state.V - p.V_rest) + p.R_m * I_total) / p.tau_m * dt

        # Add noise if specified
        if p.noise_std > 0:
            dV += np.random.normal(0, p.noise_std * np.sqrt(dt))

        return dV

    def _check_spike(self) -> bool:
        """Check if membrane potential exceeds threshold."""
        return self.state.V >= self.params.V_threshold

    def _reset_after_spike(self):
        """Reset membrane potential and enter refractory period."""
        self.state.V = self.params.V_reset
        self.state.refractory_remaining = self.params.t_refractory

    @classmethod
    def create_excitatory(cls, **kwargs) -> "LIFNeuron":
        """Factory method to create excitatory LIF neuron."""
        params = LIFParameters(neuron_type=NeuronType.EXCITATORY, **kwargs)
        return cls(params)

    @classmethod
    def create_inhibitory(cls, **kwargs) -> "LIFNeuron":
        """Factory method to create inhibitory LIF neuron with typical parameters."""
        params = LIFParameters(
            neuron_type=NeuronType.INHIBITORY,
            tau_m=8.0,  # Faster time constant
            t_refractory=1.0,  # Shorter refractory
            **kwargs
        )
        return cls(params)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LIFNeuron":
        """Create LIF neuron from dictionary."""
        params = LIFParameters(**data.get("params", {}))
        neuron = cls(params)
        if "state" in data:
            neuron.state.V = data["state"].get("V", params.V_rest)
        return neuron


# Convenience function for quick neuron creation
def create_lif_population(
    n: int,
    excitatory_ratio: float = 0.8,
    **kwargs
) -> list:
    """
    Create a population of LIF neurons.

    Args:
        n: Number of neurons
        excitatory_ratio: Fraction of excitatory neurons (default 80%)
        **kwargs: Additional parameters for neurons

    Returns:
        List of LIFNeuron instances
    """
    neurons = []
    n_excitatory = int(n * excitatory_ratio)

    for i in range(n):
        if i < n_excitatory:
            neuron = LIFNeuron.create_excitatory(**kwargs)
        else:
            neuron = LIFNeuron.create_inhibitory(**kwargs)
        neurons.append(neuron)

    return neurons
