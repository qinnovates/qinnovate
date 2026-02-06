"""
OpenBCI Hardware Adapter for TARA

Provides real-time integration with OpenBCI hardware (Cyton, Ganglion, and synthetic
boards) for live neural signal acquisition and security testing.

This adapter uses BrainFlow as the underlying library, which provides a unified
interface for multiple EEG hardware devices.

Installation:
    pip install brainflow

Supported Hardware:
    - OpenBCI Cyton (8 channels, 250Hz)
    - OpenBCI Cyton + Daisy (16 channels, 250Hz)
    - OpenBCI Ganglion (4 channels, 200Hz)
    - Synthetic Board (for testing without hardware)

Usage:
    >>> from tara_mvp.data import OpenBCIAdapter
    >>>
    >>> # Connect to hardware (or use synthetic for testing)
    >>> adapter = OpenBCIAdapter(board_type="synthetic")
    >>> adapter.connect()
    >>>
    >>> # Start streaming
    >>> adapter.start_stream()
    >>>
    >>> # Get signal data
    >>> signal = adapter.get_current_signal()
    >>> print(f"Channels: {signal.n_channels}, Samples: {signal.n_samples}")
    >>>
    >>> # Process through TARA firewall
    >>> from tara_mvp import NeuralFirewall
    >>> firewall = NeuralFirewall()
    >>> result = firewall.process_signal(signal.to_tara_format())
    >>>
    >>> # Stop and disconnect
    >>> adapter.stop_stream()
    >>> adapter.disconnect()

Note:
    This is a skeleton implementation. Full hardware support requires BrainFlow
    installation and physical OpenBCI hardware for non-synthetic modes.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Check if BrainFlow is available
_BRAINFLOW_AVAILABLE = False
_brainflow = None
_BoardIds = None
_BoardShim = None
_BrainFlowInputParams = None

try:
    import brainflow
    from brainflow.board_shim import BoardShim, BrainFlowInputParams
    from brainflow.data_filter import DataFilter
    from brainflow import BoardIds
    _BRAINFLOW_AVAILABLE = True
    _brainflow = brainflow
    _BoardIds = BoardIds
    _BoardShim = BoardShim
    _BrainFlowInputParams = BrainFlowInputParams
    logger.info(f"BrainFlow v{brainflow.__version__} loaded successfully")
except ImportError:
    logger.warning(
        "BrainFlow not installed. Install with: pip install brainflow\n"
        "Required for OpenBCI hardware support."
    )


class BoardType(Enum):
    """Supported OpenBCI board types."""
    CYTON = auto()           # 8-channel, 250Hz
    CYTON_DAISY = auto()     # 16-channel, 250Hz
    GANGLION = auto()        # 4-channel, 200Hz
    SYNTHETIC = auto()       # Simulated board for testing


class ConnectionState(Enum):
    """Connection states for the hardware."""
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    STREAMING = auto()
    ERROR = auto()


@dataclass
class BoardInfo:
    """Information about an OpenBCI board."""
    board_type: BoardType
    name: str
    channels: int
    sampling_rate: float
    brainflow_id: int
    description: str
    oni_relevance: str


# Board registry (class variable cannot be mutable default in dataclass)
BOARD_REGISTRY: Dict[BoardType, "BoardInfo"] = {}


# Initialize board registry
BOARD_REGISTRY = {
    BoardType.CYTON: BoardInfo(
        board_type=BoardType.CYTON,
        name="OpenBCI Cyton",
        channels=8,
        sampling_rate=250.0,
        brainflow_id=0 if _BoardIds is None else _BoardIds.CYTON_BOARD.value,
        description="8-channel EEG with 24-bit resolution",
        oni_relevance="Real-time L8-L14 signal validation",
    ),
    BoardType.CYTON_DAISY: BoardInfo(
        board_type=BoardType.CYTON_DAISY,
        name="OpenBCI Cyton + Daisy",
        channels=16,
        sampling_rate=250.0,
        brainflow_id=2 if _BoardIds is None else _BoardIds.CYTON_DAISY_BOARD.value,
        description="16-channel EEG with daisy chain expansion",
        oni_relevance="Full cortical coverage for comprehensive threat detection",
    ),
    BoardType.GANGLION: BoardInfo(
        board_type=BoardType.GANGLION,
        name="OpenBCI Ganglion",
        channels=4,
        sampling_rate=200.0,
        brainflow_id=1 if _BoardIds is None else _BoardIds.GANGLION_BOARD.value,
        description="4-channel compact BLE board",
        oni_relevance="Portable firewall testing and demos",
    ),
    BoardType.SYNTHETIC: BoardInfo(
        board_type=BoardType.SYNTHETIC,
        name="Synthetic Board",
        channels=8,
        sampling_rate=250.0,
        brainflow_id=-1 if _BoardIds is None else _BoardIds.SYNTHETIC_BOARD.value,
        description="Software-generated signals for testing",
        oni_relevance="Development and CI/CD without hardware",
    ),
}


@dataclass
class LiveEEGSignal:
    """Container for live EEG data from OpenBCI hardware.

    Similar to EEGSignal from MOABB adapter but for real-time data.

    Attributes:
        data: Raw EEG data array (channels x samples)
        sampling_rate: Sampling frequency in Hz
        channels: List of channel names
        timestamp: Acquisition timestamp
        board_type: Type of board that captured this data
        sequence_number: Packet sequence for continuity checking
        metadata: Additional metadata
    """
    data: np.ndarray
    sampling_rate: float
    channels: List[str]
    timestamp: float
    board_type: BoardType
    sequence_number: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Duration of signal in seconds."""
        return self.data.shape[1] / self.sampling_rate

    @property
    def n_channels(self) -> int:
        """Number of channels."""
        return self.data.shape[0]

    @property
    def n_samples(self) -> int:
        """Number of samples."""
        return self.data.shape[1]

    def to_tara_format(self) -> Dict[str, Any]:
        """Convert to TARA signal format for firewall processing.

        Returns:
            Dictionary compatible with tara.core.firewall.Signal
        """
        return {
            "data": self.data.tolist(),
            "frequency": self.sampling_rate,
            "amplitude": float(np.abs(self.data).mean()),
            "timestamp": self.timestamp,
            "source": f"openbci_{self.board_type.name.lower()}",
            "metadata": {
                "board_type": self.board_type.name,
                "channels": self.channels,
                "sequence": self.sequence_number,
                "live": True,
                **self.metadata,
            }
        }


class OpenBCIAdapter:
    """Adapter for OpenBCI hardware integration with TARA.

    Provides real-time EEG acquisition for live security monitoring,
    attack detection, and firewall validation.

    Example:
        >>> adapter = OpenBCIAdapter(board_type="synthetic")
        >>> adapter.connect()
        >>> adapter.start_stream()
        >>>
        >>> # Get 1 second of data
        >>> signal = adapter.get_current_signal(duration_sec=1.0)
        >>>
        >>> # Process through firewall
        >>> firewall = NeuralFirewall()
        >>> result = firewall.process_signal(signal.to_tara_format())
        >>> print(f"Decision: {result.decision}")
        >>>
        >>> adapter.stop_stream()
        >>> adapter.disconnect()

    Note:
        For hardware boards (Cyton, Ganglion), you need:
        - Physical OpenBCI hardware
        - USB dongle (Cyton) or Bluetooth (Ganglion)
        - Correct serial port configured

        For testing, use board_type="synthetic" which requires no hardware.
    """

    def __init__(
        self,
        board_type: str = "synthetic",
        serial_port: Optional[str] = None,
        mac_address: Optional[str] = None,
    ):
        """Initialize the OpenBCI adapter.

        Args:
            board_type: Type of board ("cyton", "cyton_daisy", "ganglion", "synthetic")
            serial_port: Serial port for Cyton boards (e.g., "/dev/ttyUSB0", "COM3")
            mac_address: MAC address for Ganglion (Bluetooth)
        """
        self.board_type = self._parse_board_type(board_type)
        self.serial_port = serial_port
        self.mac_address = mac_address

        self.board_info = BOARD_REGISTRY[self.board_type]
        self.state = ConnectionState.DISCONNECTED
        self._board: Optional[Any] = None  # BoardShim instance
        self._sequence = 0
        self._callbacks: List[Callable[[LiveEEGSignal], None]] = []

        logger.info(
            f"OpenBCIAdapter initialized: {self.board_info.name} "
            f"({self.board_info.channels} channels @ {self.board_info.sampling_rate}Hz)"
        )

    @staticmethod
    def _parse_board_type(board_type: str) -> BoardType:
        """Parse board type string to enum."""
        mapping = {
            "cyton": BoardType.CYTON,
            "cyton_daisy": BoardType.CYTON_DAISY,
            "ganglion": BoardType.GANGLION,
            "synthetic": BoardType.SYNTHETIC,
        }
        board_type_lower = board_type.lower()
        if board_type_lower not in mapping:
            raise ValueError(
                f"Unknown board type: {board_type}. "
                f"Available: {list(mapping.keys())}"
            )
        return mapping[board_type_lower]

    @property
    def is_connected(self) -> bool:
        """Check if board is connected."""
        return self.state in (ConnectionState.CONNECTED, ConnectionState.STREAMING)

    @property
    def is_streaming(self) -> bool:
        """Check if board is currently streaming data."""
        return self.state == ConnectionState.STREAMING

    def connect(self) -> bool:
        """Connect to the OpenBCI board.

        Returns:
            True if connection successful, False otherwise

        Raises:
            ImportError: If BrainFlow is not installed
            RuntimeError: If connection fails
        """
        if not _BRAINFLOW_AVAILABLE:
            raise ImportError(
                "BrainFlow is required for OpenBCI hardware support. "
                "Install with: pip install brainflow"
            )

        if self.is_connected:
            logger.warning("Already connected")
            return True

        self.state = ConnectionState.CONNECTING

        try:
            # Configure board parameters
            params = _BrainFlowInputParams()

            if self.board_type == BoardType.GANGLION and self.mac_address:
                params.mac_address = self.mac_address
            elif self.serial_port:
                params.serial_port = self.serial_port

            # Create board instance
            board_id = self.board_info.brainflow_id
            self._board = _BoardShim(board_id, params)

            # Prepare session
            self._board.prepare_session()

            self.state = ConnectionState.CONNECTED
            logger.info(f"Connected to {self.board_info.name}")
            return True

        except Exception as e:
            self.state = ConnectionState.ERROR
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Failed to connect to {self.board_info.name}: {e}")

    def disconnect(self) -> bool:
        """Disconnect from the OpenBCI board.

        Returns:
            True if disconnection successful
        """
        if self.state == ConnectionState.DISCONNECTED:
            return True

        if self.is_streaming:
            self.stop_stream()

        if self._board is not None:
            try:
                self._board.release_session()
            except Exception as e:
                logger.warning(f"Error releasing session: {e}")

        self._board = None
        self.state = ConnectionState.DISCONNECTED
        logger.info("Disconnected from board")
        return True

    def start_stream(self) -> bool:
        """Start data streaming from the board.

        Returns:
            True if streaming started successfully
        """
        if not self.is_connected:
            raise RuntimeError("Board not connected. Call connect() first.")

        if self.is_streaming:
            logger.warning("Already streaming")
            return True

        try:
            self._board.start_stream()
            self.state = ConnectionState.STREAMING
            logger.info("Started streaming")
            return True
        except Exception as e:
            logger.error(f"Failed to start stream: {e}")
            return False

    def stop_stream(self) -> bool:
        """Stop data streaming from the board.

        Returns:
            True if streaming stopped successfully
        """
        if not self.is_streaming:
            return True

        try:
            self._board.stop_stream()
            self.state = ConnectionState.CONNECTED
            logger.info("Stopped streaming")
            return True
        except Exception as e:
            logger.warning(f"Error stopping stream: {e}")
            return False

    def get_current_signal(
        self,
        duration_sec: float = 1.0,
        clear_buffer: bool = True,
    ) -> LiveEEGSignal:
        """Get the current signal from the board buffer.

        Args:
            duration_sec: Duration of signal to return (seconds)
            clear_buffer: Whether to clear the buffer after reading

        Returns:
            LiveEEGSignal containing the acquired data

        Raises:
            RuntimeError: If not streaming
        """
        if not self.is_streaming:
            raise RuntimeError("Board not streaming. Call start_stream() first.")

        num_samples = int(duration_sec * self.board_info.sampling_rate)

        # Get data from board
        data = self._board.get_board_data(num_samples)

        # Extract EEG channels only
        eeg_channels = _BoardShim.get_eeg_channels(self.board_info.brainflow_id)
        eeg_data = data[eeg_channels, :]

        # Generate channel names
        channel_names = [f"Ch{i+1}" for i in range(len(eeg_channels))]

        self._sequence += 1

        return LiveEEGSignal(
            data=eeg_data,
            sampling_rate=self.board_info.sampling_rate,
            channels=channel_names,
            timestamp=time.time(),
            board_type=self.board_type,
            sequence_number=self._sequence,
            metadata={
                "raw_shape": data.shape,
                "eeg_channels": eeg_channels,
            }
        )

    def get_impedance(self) -> Optional[Dict[str, float]]:
        """Get electrode impedance values (if supported).

        Returns:
            Dictionary of channel name to impedance in kOhms, or None if not supported
        """
        # Note: Impedance checking requires specific board support
        # This is a placeholder for the full implementation
        logger.warning("Impedance checking not yet implemented")
        return None

    def on_data(self, callback: Callable[[LiveEEGSignal], None]) -> None:
        """Register a callback for real-time data processing.

        Args:
            callback: Function to call with each new signal chunk
        """
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[LiveEEGSignal], None]) -> None:
        """Remove a registered callback.

        Args:
            callback: The callback function to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def list_boards(self) -> List[Dict[str, Any]]:
        """List all supported board types with metadata.

        Returns:
            List of board information dictionaries
        """
        return [
            {
                "type": info.board_type.name,
                "name": info.name,
                "channels": info.channels,
                "sampling_rate": info.sampling_rate,
                "description": info.description,
                "oni_relevance": info.oni_relevance,
            }
            for info in BOARD_REGISTRY.values()
        ]

    def __enter__(self) -> "OpenBCIAdapter":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.disconnect()


# Convenience functions
def is_brainflow_available() -> bool:
    """Check if BrainFlow is installed and available."""
    return _BRAINFLOW_AVAILABLE


def get_brainflow_version() -> Optional[str]:
    """Get BrainFlow version if installed."""
    if _BRAINFLOW_AVAILABLE and _brainflow:
        return _brainflow.__version__
    return None


def list_serial_ports() -> List[str]:
    """List available serial ports for OpenBCI connection.

    Returns:
        List of serial port names (e.g., ["/dev/ttyUSB0", "COM3"])
    """
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    except ImportError:
        logger.warning("pyserial not installed. Install with: pip install pyserial")
        return []


# Exports
SUPPORTED_BOARDS = {
    board_type.name.lower(): info
    for board_type, info in BOARD_REGISTRY.items()
}
