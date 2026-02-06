"""
Hodgkin-Huxley Neuron Model

Biophysically detailed model with explicit ion channel dynamics
for sodium (Na+) and potassium (K+) currents.

This model reproduces the action potential shape and refractory
periods seen in real neurons.

Equations:
    C * dV/dt = I - g_Na * m³h * (V - E_Na) - g_K * n⁴ * (V - E_K) - g_L * (V - E_L)

Where m, h, n are gating variables with first-order kinetics:
    dx/dt = α_x(V)(1-x) - β_x(V)x

Reference:
    Hodgkin, A.L. & Huxley, A.F. (1952). A quantitative description
    of membrane current and its application to conduction and
    excitation in nerve. Journal of Physiology.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np

from .base import Neuron, NeuronParameters, NeuronType


@dataclass
class HodgkinHuxleyParameters(NeuronParameters):
    """Parameters for Hodgkin-Huxley neuron model."""

    # Membrane capacitance
    C_m: float = 1.0  # μF/cm²

    # Maximum conductances (mS/cm²)
    g_Na: float = 120.0  # Sodium
    g_K: float = 36.0    # Potassium
    g_L: float = 0.3     # Leak

    # Reversal potentials (mV)
    E_Na: float = 50.0   # Sodium
    E_K: float = -77.0   # Potassium
    E_L: float = -54.4   # Leak

    # Initial conditions (mV)
    V_init: float = -65.0

    # Spike detection threshold
    V_threshold: float = 0.0

    # Temperature factor (default is 6.3°C as in original paper)
    temperature: float = 6.3  # °C
    temp_factor: float = 1.0  # Q10 factor (computed)

    def __post_init__(self):
        """Compute temperature factor."""
        # Q10 temperature correction
        self.temp_factor = 3.0 ** ((self.temperature - 6.3) / 10.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "C_m": self.C_m,
            "g_Na": self.g_Na,
            "g_K": self.g_K,
            "g_L": self.g_L,
            "E_Na": self.E_Na,
            "E_K": self.E_K,
            "E_L": self.E_L,
            "V_init": self.V_init,
            "temperature": self.temperature,
        })
        return base


class HodgkinHuxleyNeuron(Neuron):
    """
    Hodgkin-Huxley Neuron Model.

    The classic biophysical model with Na+ and K+ conductances.
    Computationally more expensive but produces realistic action
    potential waveforms.

    Usage:
        >>> neuron = HodgkinHuxleyNeuron()
        >>> results = neuron.simulate(100, input_current=np.ones(1000) * 10.0)
        >>> # Observe realistic action potential shapes
    """

    def __init__(self, params: Optional[HodgkinHuxleyParameters] = None):
        """
        Initialize Hodgkin-Huxley neuron.

        Args:
            params: Model parameters (uses defaults if None)
        """
        super().__init__(params or HodgkinHuxleyParameters())

        # Initialize state
        self.state.V = self.params.V_init

        # Gating variables
        self.m = self._m_inf(self.params.V_init)  # Na activation
        self.h = self._h_inf(self.params.V_init)  # Na inactivation
        self.n = self._n_inf(self.params.V_init)  # K activation

        # History for gating variables
        self.m_history = []
        self.h_history = []
        self.n_history = []

        # Track currents
        self.I_Na_history = []
        self.I_K_history = []

    @property
    def params(self) -> HodgkinHuxleyParameters:
        """Type-hinted access to parameters."""
        return self._params

    @params.setter
    def params(self, value: HodgkinHuxleyParameters):
        self._params = value

    def get_V_rest(self) -> float:
        """Get resting membrane potential."""
        return self.params.V_init

    # --- Rate functions for gating variables ---
    # These are the classic Hodgkin-Huxley rate equations

    def _alpha_m(self, V: float) -> float:
        """Forward rate for Na activation (m)."""
        V_shifted = V + 65  # Shift to original HH convention
        if abs(V_shifted - 25) < 1e-7:
            return 1.0
        return 0.1 * (25 - V_shifted) / (np.exp((25 - V_shifted) / 10) - 1)

    def _beta_m(self, V: float) -> float:
        """Backward rate for Na activation (m)."""
        V_shifted = V + 65
        return 4.0 * np.exp(-V_shifted / 18)

    def _alpha_h(self, V: float) -> float:
        """Forward rate for Na inactivation (h)."""
        V_shifted = V + 65
        return 0.07 * np.exp(-V_shifted / 20)

    def _beta_h(self, V: float) -> float:
        """Backward rate for Na inactivation (h)."""
        V_shifted = V + 65
        return 1.0 / (np.exp((30 - V_shifted) / 10) + 1)

    def _alpha_n(self, V: float) -> float:
        """Forward rate for K activation (n)."""
        V_shifted = V + 65
        if abs(V_shifted - 10) < 1e-7:
            return 0.1
        return 0.01 * (10 - V_shifted) / (np.exp((10 - V_shifted) / 10) - 1)

    def _beta_n(self, V: float) -> float:
        """Backward rate for K activation (n)."""
        V_shifted = V + 65
        return 0.125 * np.exp(-V_shifted / 80)

    # Steady-state values
    def _m_inf(self, V: float) -> float:
        """Steady-state Na activation."""
        return self._alpha_m(V) / (self._alpha_m(V) + self._beta_m(V))

    def _h_inf(self, V: float) -> float:
        """Steady-state Na inactivation."""
        return self._alpha_h(V) / (self._alpha_h(V) + self._beta_h(V))

    def _n_inf(self, V: float) -> float:
        """Steady-state K activation."""
        return self._alpha_n(V) / (self._alpha_n(V) + self._beta_n(V))

    def _compute_dV(self, I_total: float) -> float:
        """
        Compute membrane potential change using HH dynamics.
        """
        p = self.params
        dt = p.dt
        V = self.state.V
        phi = p.temp_factor  # Temperature correction

        # Update gating variables (forward Euler)
        dm = phi * (self._alpha_m(V) * (1 - self.m) - self._beta_m(V) * self.m) * dt
        dh = phi * (self._alpha_h(V) * (1 - self.h) - self._beta_h(V) * self.h) * dt
        dn = phi * (self._alpha_n(V) * (1 - self.n) - self._beta_n(V) * self.n) * dt

        self.m = np.clip(self.m + dm, 0, 1)
        self.h = np.clip(self.h + dh, 0, 1)
        self.n = np.clip(self.n + dn, 0, 1)

        # Compute ionic currents
        I_Na = p.g_Na * (self.m ** 3) * self.h * (V - p.E_Na)
        I_K = p.g_K * (self.n ** 4) * (V - p.E_K)
        I_L = p.g_L * (V - p.E_L)

        # Membrane potential dynamics
        dV = (I_total - I_Na - I_K - I_L) / p.C_m * dt

        return dV

    def _check_spike(self) -> bool:
        """
        Check for spike using threshold crossing.

        HH model doesn't need explicit reset - the dynamics
        naturally produce the action potential shape.
        """
        # Detect upward threshold crossing
        if hasattr(self, '_prev_V'):
            crossed = (self._prev_V < self.params.V_threshold and
                      self.state.V >= self.params.V_threshold)
            self._prev_V = self.state.V
            return crossed
        else:
            self._prev_V = self.state.V
            return False

    def _reset_after_spike(self):
        """HH model doesn't need explicit reset."""
        pass  # Natural dynamics handle refractory period

    def step(self, record_history: bool = True) -> bool:
        """Override step to record gating variable history."""
        result = super().step(record_history)

        if record_history:
            self.m_history.append(self.m)
            self.h_history.append(self.h)
            self.n_history.append(self.n)

            # Compute and store currents
            p = self.params
            V = self.state.V
            I_Na = p.g_Na * (self.m ** 3) * self.h * (V - p.E_Na)
            I_K = p.g_K * (self.n ** 4) * (V - p.E_K)
            self.I_Na_history.append(I_Na)
            self.I_K_history.append(I_K)

        return result

    def reset(self):
        """Reset neuron to initial state."""
        super().reset()
        V_init = self.params.V_init
        self.m = self._m_inf(V_init)
        self.h = self._h_inf(V_init)
        self.n = self._n_inf(V_init)
        self.m_history = []
        self.h_history = []
        self.n_history = []
        self.I_Na_history = []
        self.I_K_history = []
        if hasattr(self, '_prev_V'):
            del self._prev_V

    def simulate(
        self,
        duration: float,
        input_current: Optional[np.ndarray] = None,
        record_history: bool = True
    ) -> Dict[str, np.ndarray]:
        """Run simulation and include ion channel data."""
        results = super().simulate(duration, input_current, record_history)

        if record_history:
            results["m"] = np.array(self.m_history)
            results["h"] = np.array(self.h_history)
            results["n"] = np.array(self.n_history)
            results["I_Na"] = np.array(self.I_Na_history)
            results["I_K"] = np.array(self.I_K_history)

        return results

    def to_dict(self) -> Dict[str, Any]:
        """Serialize neuron to dictionary."""
        data = super().to_dict()
        data["state"].update({
            "m": self.m,
            "h": self.h,
            "n": self.n,
        })
        return data

    @classmethod
    def create_squid_axon(cls) -> "HodgkinHuxleyNeuron":
        """Create classic squid giant axon parameters."""
        params = HodgkinHuxleyParameters(
            temperature=6.3,  # Original experimental temperature
        )
        return cls(params)

    @classmethod
    def create_mammalian(cls) -> "HodgkinHuxleyNeuron":
        """Create parameters typical of mammalian neurons (37°C)."""
        params = HodgkinHuxleyParameters(
            temperature=37.0,
            g_Na=100.0,
            g_K=30.0,
            g_L=0.1,
        )
        return cls(params)
