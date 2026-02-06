"""
Data Recording Module

Handles recording of simulation data including:
- Membrane potentials
- Spike times
- Synaptic currents
- Network activity metrics

Supports various output formats for analysis and visualization.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Set, Callable
import numpy as np
from enum import Enum
import json


class RecordingVariable(Enum):
    """Variables that can be recorded."""
    VOLTAGE = "V"                     # Membrane potential
    SPIKE_TIMES = "spike_times"       # Spike times
    CURRENT = "I"                     # Total input current
    CONDUCTANCE = "g"                 # Synaptic conductance
    FIRING_RATE = "rate"              # Instantaneous firing rate
    WEIGHT = "weight"                 # Synaptic weight (for STDP)


@dataclass
class RecordingConfig:
    """Configuration for data recording."""

    # What to record
    variables: List[RecordingVariable] = field(default_factory=lambda: [
        RecordingVariable.VOLTAGE,
        RecordingVariable.SPIKE_TIMES
    ])

    # Which neurons to record (None = all)
    neuron_ids: Optional[List[str]] = None

    # Which synapses to record (None = none, [] = all if specified)
    synapse_ids: Optional[List[str]] = None

    # Recording resolution
    sample_every: int = 1             # Record every N steps
    downsample_voltage: int = 1       # Downsample voltage traces

    # Memory management
    max_samples: int = 100000         # Max samples to keep in memory
    flush_interval: int = 10000       # Samples before flushing to disk

    # Output settings
    output_dir: Optional[str] = None
    output_format: str = "numpy"      # numpy, json, csv


@dataclass
class RecordedData:
    """Container for recorded simulation data."""

    # Time vector
    t: List[float] = field(default_factory=list)

    # Neuron data
    voltages: Dict[str, List[float]] = field(default_factory=dict)
    spike_times: Dict[str, List[float]] = field(default_factory=dict)
    currents: Dict[str, List[float]] = field(default_factory=dict)
    firing_rates: Dict[str, List[float]] = field(default_factory=dict)

    # Synapse data
    conductances: Dict[str, List[float]] = field(default_factory=dict)
    weights: Dict[str, List[float]] = field(default_factory=dict)

    # Network-level metrics
    population_rates: Dict[str, List[float]] = field(default_factory=dict)
    total_spikes: List[int] = field(default_factory=list)

    # Metadata
    duration: float = 0.0
    dt: float = 0.1
    n_steps: int = 0


class Recorder:
    """
    Records simulation data for analysis.

    Handles efficient storage of neural data and provides
    methods for accessing and exporting recorded data.

    Usage:
        >>> recorder = Recorder(config)
        >>> # During simulation:
        >>> recorder.record_step(t, network)
        >>> # After simulation:
        >>> data = recorder.get_data()
        >>> recorder.save("simulation_data")
    """

    def __init__(self, config: Optional[RecordingConfig] = None):
        """
        Initialize recorder.

        Args:
            config: Recording configuration
        """
        self.config = config or RecordingConfig()
        self.data = RecordedData()

        self._step_count = 0
        self._last_flush = 0

        # Track which neurons/synapses to record
        self._record_neurons: Set[str] = set()
        self._record_synapses: Set[str] = set()

        # Callbacks for custom recording
        self._callbacks: List[Callable] = []

    def setup(self, network):
        """
        Configure recorder for a network.

        Args:
            network: Network to record from
        """
        # Determine which neurons to record
        if self.config.neuron_ids is None:
            # Record all neurons
            self._record_neurons = set(network.neurons.keys())
        else:
            self._record_neurons = set(self.config.neuron_ids)

        # Initialize data structures
        for nid in self._record_neurons:
            if RecordingVariable.VOLTAGE in self.config.variables:
                self.data.voltages[nid] = []
            if RecordingVariable.SPIKE_TIMES in self.config.variables:
                self.data.spike_times[nid] = []
            if RecordingVariable.CURRENT in self.config.variables:
                self.data.currents[nid] = []
            if RecordingVariable.FIRING_RATE in self.config.variables:
                self.data.firing_rates[nid] = []

        # Setup synapse recording if specified
        if self.config.synapse_ids is not None:
            if len(self.config.synapse_ids) == 0:
                # Record all synapses
                self._record_synapses = set(s.id for s in network.synapses)
            else:
                self._record_synapses = set(self.config.synapse_ids)

            for sid in self._record_synapses:
                if RecordingVariable.CONDUCTANCE in self.config.variables:
                    self.data.conductances[sid] = []
                if RecordingVariable.WEIGHT in self.config.variables:
                    self.data.weights[sid] = []

    def record_step(self, t: float, network):
        """
        Record data for current timestep.

        Args:
            t: Current simulation time
            network: Network to record from
        """
        self._step_count += 1

        # Check if we should record this step
        if self._step_count % self.config.sample_every != 0:
            return

        # Record time
        self.data.t.append(t)

        # Record neuron data
        for nid in self._record_neurons:
            neuron = network.neurons.get(nid)
            if neuron is None:
                continue

            if RecordingVariable.VOLTAGE in self.config.variables:
                self.data.voltages[nid].append(neuron.state.V)

            if RecordingVariable.SPIKE_TIMES in self.config.variables:
                # Check for new spikes
                if neuron.state.fired:
                    self.data.spike_times[nid].append(t)

            if RecordingVariable.CURRENT in self.config.variables:
                self.data.currents[nid].append(neuron.state.I_total)

        # Record synapse data
        for synapse in network.synapses:
            if synapse.id not in self._record_synapses:
                continue

            if RecordingVariable.CONDUCTANCE in self.config.variables:
                self.data.conductances[synapse.id].append(synapse.state.g)

            if RecordingVariable.WEIGHT in self.config.variables:
                self.data.weights[synapse.id].append(synapse.weight)

        # Record network-level metrics
        total_spikes = sum(
            1 for nid in self._record_neurons
            if network.neurons.get(nid) and network.neurons[nid].state.fired
        )
        self.data.total_spikes.append(total_spikes)

        # Run custom callbacks
        for callback in self._callbacks:
            callback(t, network, self.data)

        # Check for flush
        if (self._step_count - self._last_flush) >= self.config.flush_interval:
            self._maybe_flush()

    def record_spike(self, neuron_id: str, spike_time: float):
        """
        Record a spike event directly.

        Args:
            neuron_id: ID of spiking neuron
            spike_time: Time of spike
        """
        if neuron_id in self._record_neurons:
            if neuron_id not in self.data.spike_times:
                self.data.spike_times[neuron_id] = []
            self.data.spike_times[neuron_id].append(spike_time)

    def add_callback(self, callback: Callable):
        """
        Add custom recording callback.

        Args:
            callback: Function(t, network, data) called each recorded step
        """
        self._callbacks.append(callback)

    def _maybe_flush(self):
        """Flush data to disk if configured."""
        if self.config.output_dir:
            # TODO: Implement incremental flushing
            pass
        self._last_flush = self._step_count

    def get_data(self) -> RecordedData:
        """Get recorded data."""
        return self.data

    def get_voltage_traces(self) -> Dict[str, np.ndarray]:
        """Get voltage traces as numpy arrays."""
        return {
            nid: np.array(v) for nid, v in self.data.voltages.items()
        }

    def get_spike_trains(self) -> Dict[str, np.ndarray]:
        """Get spike trains as numpy arrays."""
        return {
            nid: np.array(times) for nid, times in self.data.spike_times.items()
        }

    def get_raster_data(self) -> tuple:
        """
        Get data for raster plot.

        Returns:
            Tuple of (spike_times, neuron_indices)
        """
        times = []
        indices = []
        neuron_ids = list(self._record_neurons)
        id_to_idx = {nid: i for i, nid in enumerate(neuron_ids)}

        for nid, spike_times in self.data.spike_times.items():
            idx = id_to_idx.get(nid, -1)
            for t in spike_times:
                times.append(t)
                indices.append(idx)

        return np.array(times), np.array(indices)

    def compute_firing_rates(
        self,
        window: float = 100.0,
        step: float = 10.0
    ) -> Dict[str, np.ndarray]:
        """
        Compute time-resolved firing rates.

        Args:
            window: Sliding window size (ms)
            step: Step size for sliding window (ms)

        Returns:
            Dictionary mapping neuron IDs to rate arrays
        """
        if not self.data.t:
            return {}

        t_max = max(self.data.t)
        t_centers = np.arange(window / 2, t_max - window / 2, step)
        rates = {}

        for nid, spikes in self.data.spike_times.items():
            spikes = np.array(spikes)
            neuron_rates = []

            for t_center in t_centers:
                t_start = t_center - window / 2
                t_end = t_center + window / 2
                n_spikes = np.sum((spikes >= t_start) & (spikes < t_end))
                rate = n_spikes / (window / 1000)  # Convert to Hz
                neuron_rates.append(rate)

            rates[nid] = np.array(neuron_rates)

        return rates

    def compute_population_rate(
        self,
        neuron_ids: Optional[List[str]] = None,
        window: float = 10.0
    ) -> tuple:
        """
        Compute population firing rate over time.

        Args:
            neuron_ids: Subset of neurons (None = all)
            window: Binning window (ms)

        Returns:
            Tuple of (time_centers, population_rate)
        """
        if not self.data.t:
            return np.array([]), np.array([])

        ids = neuron_ids or list(self._record_neurons)
        t_max = max(self.data.t)
        n_bins = int(t_max / window)

        # Collect all spikes
        all_spikes = []
        for nid in ids:
            if nid in self.data.spike_times:
                all_spikes.extend(self.data.spike_times[nid])

        if not all_spikes:
            return np.arange(0, t_max, window), np.zeros(n_bins)

        all_spikes = np.array(all_spikes)

        # Bin spikes
        hist, bin_edges = np.histogram(all_spikes, bins=n_bins, range=(0, t_max))
        t_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        # Convert to rate (spikes/s per neuron)
        rate = hist / (window / 1000) / len(ids)

        return t_centers, rate

    def to_dict(self) -> Dict[str, Any]:
        """Convert recorded data to dictionary."""
        return {
            "t": list(self.data.t),
            "voltages": {k: list(v) for k, v in self.data.voltages.items()},
            "spike_times": {k: list(v) for k, v in self.data.spike_times.items()},
            "currents": {k: list(v) for k, v in self.data.currents.items()},
            "total_spikes": list(self.data.total_spikes),
            "metadata": {
                "duration": self.data.duration,
                "dt": self.data.dt,
                "n_steps": self._step_count,
                "n_neurons": len(self._record_neurons),
            }
        }

    def save(self, filename: str, format: str = None):
        """
        Save recorded data to file.

        Args:
            filename: Output filename (without extension)
            format: Output format (numpy, json, csv)
        """
        fmt = format or self.config.output_format

        if fmt == "numpy":
            self._save_numpy(filename)
        elif fmt == "json":
            self._save_json(filename)
        elif fmt == "csv":
            self._save_csv(filename)

    def _save_numpy(self, filename: str):
        """Save data as numpy archive."""
        save_dict = {
            "t": np.array(self.data.t),
            "total_spikes": np.array(self.data.total_spikes),
        }

        # Add voltage traces
        for nid, v in self.data.voltages.items():
            save_dict[f"V_{nid}"] = np.array(v)

        # Add spike times (as object array)
        spike_ids = list(self.data.spike_times.keys())
        save_dict["spike_neuron_ids"] = np.array(spike_ids, dtype=object)
        for nid, times in self.data.spike_times.items():
            save_dict[f"spikes_{nid}"] = np.array(times)

        np.savez(f"{filename}.npz", **save_dict)

    def _save_json(self, filename: str):
        """Save data as JSON."""
        data = self.to_dict()
        with open(f"{filename}.json", 'w') as f:
            json.dump(data, f, indent=2)

    def _save_csv(self, filename: str):
        """Save voltage traces as CSV."""
        if not self.data.voltages:
            return

        # Create header
        neuron_ids = list(self.data.voltages.keys())
        header = "t," + ",".join(neuron_ids)

        # Create data matrix
        n_samples = len(self.data.t)
        data_matrix = np.zeros((n_samples, len(neuron_ids) + 1))
        data_matrix[:, 0] = self.data.t

        for i, nid in enumerate(neuron_ids):
            data_matrix[:, i + 1] = self.data.voltages[nid]

        np.savetxt(
            f"{filename}_voltages.csv",
            data_matrix,
            delimiter=",",
            header=header,
            comments=""
        )

    def reset(self):
        """Reset recorder for new simulation."""
        self.data = RecordedData()
        self._step_count = 0
        self._last_flush = 0

        # Re-initialize data structures
        for nid in self._record_neurons:
            if RecordingVariable.VOLTAGE in self.config.variables:
                self.data.voltages[nid] = []
            if RecordingVariable.SPIKE_TIMES in self.config.variables:
                self.data.spike_times[nid] = []
