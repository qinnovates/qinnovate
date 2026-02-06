"""
Neural Firewall Pipeline Visualization

ONI-Aligned Signal Validation Pipeline operating at Layer 8 (Neural Gateway).

The Neural Firewall validates signals crossing the bio-digital boundary,
with checkpoints mapped to ONI Framework layers L8-L14:

L8:  Neural Gateway    - Electrode interface validation (impedance, hardware)
L9:  Signal Processing - SNR validation, artifact detection
L10: Protocol          - Biological plausibility (spike rate, LFP bounds)
L11: Transport         - Rate limiting, delivery validation
L12: Session           - Temporal consistency, state validation
L13: Presentation      - Intent coherence (Cs), decoder confidence
L14: Application       - Anomaly detection, privacy filtering

Reference: ONI Framework TechDoc, oni-framework/oni/layers.py
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

try:
    from ..themes.oni_theme import ONI_COLORS, apply_oni_theme, get_layer_color
except ImportError:
    from tara_mvp.visualization.themes.oni_theme import ONI_COLORS, apply_oni_theme, get_layer_color


class CheckpointStatus(Enum):
    """Status of a firewall checkpoint."""
    PASS = "pass"  # nosec B105 - not a password, status enum value
    FAIL = "fail"
    FLAGGED = "flagged"
    PENDING = "pending"
    BYPASSED = "bypassed"


@dataclass
class FirewallCheckpoint:
    """
    Single firewall validation checkpoint aligned with an ONI layer.

    Each checkpoint validates a specific aspect of the neural signal
    at its corresponding ONI Framework layer.
    """
    layer: int  # ONI layer number (8-14)
    name: str
    description: str
    oni_layer_name: str = ""  # Full ONI layer name
    status: CheckpointStatus = CheckpointStatus.PENDING

    # Validation thresholds
    threshold_low: Optional[float] = None
    threshold_high: Optional[float] = None
    unit: str = ""

    # Current signal metrics
    current_value: Optional[float] = None

    # Statistics
    signals_processed: int = 0
    signals_passed: int = 0
    signals_blocked: int = 0
    signals_flagged: int = 0

    # Timing
    avg_latency_ms: float = 0.0
    last_updated: Optional[datetime] = None

    def pass_rate(self) -> float:
        """Calculate pass rate percentage."""
        if self.signals_processed == 0:
            return 0.0
        return (self.signals_passed / self.signals_processed) * 100

    def evaluate(self, value: float) -> CheckpointStatus:
        """
        Evaluate a value against this checkpoint's thresholds.

        Args:
            value: The signal value to evaluate

        Returns:
            CheckpointStatus based on evaluation
        """
        self.current_value = value
        self.signals_processed += 1
        self.last_updated = datetime.now()

        # Check bounds
        if self.threshold_low is not None and value < self.threshold_low:
            self.signals_blocked += 1
            self.status = CheckpointStatus.FAIL
            return CheckpointStatus.FAIL

        if self.threshold_high is not None and value > self.threshold_high:
            self.signals_blocked += 1
            self.status = CheckpointStatus.FAIL
            return CheckpointStatus.FAIL

        # Passed
        self.signals_passed += 1
        self.status = CheckpointStatus.PASS
        return CheckpointStatus.PASS

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "layer": self.layer,
            "name": self.name,
            "oni_layer_name": self.oni_layer_name,
            "description": self.description,
            "status": self.status.value,
            "threshold_low": self.threshold_low,
            "threshold_high": self.threshold_high,
            "unit": self.unit,
            "current_value": self.current_value,
            "signals_processed": self.signals_processed,
            "signals_passed": self.signals_passed,
            "signals_blocked": self.signals_blocked,
            "signals_flagged": self.signals_flagged,
            "pass_rate": self.pass_rate(),
            "avg_latency_ms": self.avg_latency_ms,
        }


# ONI-Aligned firewall configuration (L8-L14)
DEFAULT_FIREWALL_LAYERS: List[FirewallCheckpoint] = [
    FirewallCheckpoint(
        layer=8,
        name="Impedance Validation",
        oni_layer_name="Neural Gateway",
        description="Hardware-level electrode impedance at bio-digital boundary",
        threshold_low=100,    # kOhms
        threshold_high=5000,  # kOhms
        unit="kΩ",
    ),
    FirewallCheckpoint(
        layer=9,
        name="Signal Integrity",
        oni_layer_name="Signal Processing",
        description="SNR validation and artifact detection",
        threshold_low=5,      # dB minimum SNR
        threshold_high=None,
        unit="dB",
    ),
    FirewallCheckpoint(
        layer=10,
        name="Biological Plausibility",
        oni_layer_name="Protocol",
        description="Spike rate bounds, LFP frequency validation",
        threshold_low=0.1,    # Hz minimum
        threshold_high=300,   # Hz maximum
        unit="Hz",
    ),
    FirewallCheckpoint(
        layer=11,
        name="Rate Limiting",
        oni_layer_name="Transport",
        description="Signal rate validation, delivery bounds",
        threshold_low=None,
        threshold_high=1000,  # Max signals/sec
        unit="sig/s",
    ),
    FirewallCheckpoint(
        layer=12,
        name="Temporal Consistency",
        oni_layer_name="Session",
        description="State validation, timing consistency",
        threshold_low=0.8,    # Consistency score
        threshold_high=None,
        unit="score",
    ),
    FirewallCheckpoint(
        layer=13,
        name="Intent Coherence",
        oni_layer_name="Presentation",
        description="Decoder confidence, coherence metric (Cs)",
        threshold_low=0.3,    # Cs minimum
        threshold_high=None,
        unit="Cs",
    ),
    FirewallCheckpoint(
        layer=14,
        name="Anomaly Detection",
        oni_layer_name="Application",
        description="ML-based anomaly scoring and privacy filtering",
        threshold_low=None,
        threshold_high=0.7,   # Anomaly score threshold
        unit="score",
    ),
]


class NeuralFirewall:
    """
    ONI-Aligned Neural Signal Validation Pipeline.

    Implements the Neural Firewall at Layer 8 (Neural Gateway) with
    validation checkpoints spanning L8-L14 of the ONI Framework.

    The firewall validates signals crossing the bio-digital boundary
    using coherence metrics, hardware validation, and anomaly detection.
    """

    def __init__(self, checkpoints: List[FirewallCheckpoint] = None):
        """
        Initialize the firewall.

        Args:
            checkpoints: Custom checkpoint configuration (default: L8-L14)
        """
        if checkpoints:
            self.checkpoints = checkpoints
        else:
            # Deep copy defaults
            self.checkpoints = [
                FirewallCheckpoint(
                    layer=cp.layer,
                    name=cp.name,
                    oni_layer_name=cp.oni_layer_name,
                    description=cp.description,
                    threshold_low=cp.threshold_low,
                    threshold_high=cp.threshold_high,
                    unit=cp.unit,
                )
                for cp in DEFAULT_FIREWALL_LAYERS
            ]

        self.total_signals = 0
        self.total_passed = 0
        self.total_blocked = 0

    def process_signal(self, signal_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Process a signal through all checkpoints (L8-L14).

        Args:
            signal_metrics: Dict with keys matching checkpoint requirements:
                - impedance: For L8 (Neural Gateway)
                - snr: For L9 (Signal Processing)
                - spike_rate: For L10 (Protocol)
                - signal_rate: For L11 (Transport)
                - consistency: For L12 (Session)
                - coherence: For L13 (Presentation)
                - anomaly_score: For L14 (Application)

        Returns:
            Dict with processing results
        """
        self.total_signals += 1
        results = {
            "passed": True,
            "blocked_at": None,
            "checkpoint_results": [],
        }

        # Map ONI layers to signal metrics
        metric_mapping = {
            8: "impedance",
            9: "snr",
            10: "spike_rate",
            11: "signal_rate",
            12: "consistency",
            13: "coherence",
            14: "anomaly_score",
        }

        for checkpoint in self.checkpoints:
            metric_key = metric_mapping.get(checkpoint.layer)
            value = signal_metrics.get(metric_key) if metric_key else None

            if value is None:
                # No metric provided, auto-pass with default
                checkpoint.signals_processed += 1
                checkpoint.signals_passed += 1
                checkpoint.status = CheckpointStatus.PASS
                results["checkpoint_results"].append({
                    "layer": checkpoint.layer,
                    "status": "pass",
                    "value": None,
                })
                continue

            status = checkpoint.evaluate(value)

            results["checkpoint_results"].append({
                "layer": checkpoint.layer,
                "status": status.value,
                "value": value,
            })

            if status == CheckpointStatus.FAIL:
                results["passed"] = False
                results["blocked_at"] = checkpoint.layer
                self.total_blocked += 1
                # Stop processing on first failure
                break

        if results["passed"]:
            self.total_passed += 1

        return results

    def get_checkpoint(self, layer: int) -> Optional[FirewallCheckpoint]:
        """Get checkpoint by ONI layer number."""
        for cp in self.checkpoints:
            if cp.layer == layer:
                return cp
        return None

    def reset_statistics(self):
        """Reset all checkpoint statistics."""
        self.total_signals = 0
        self.total_passed = 0
        self.total_blocked = 0
        for cp in self.checkpoints:
            cp.signals_processed = 0
            cp.signals_passed = 0
            cp.signals_blocked = 0
            cp.signals_flagged = 0
            cp.status = CheckpointStatus.PENDING
            cp.current_value = None

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall firewall statistics."""
        return {
            "total_signals": self.total_signals,
            "total_passed": self.total_passed,
            "total_blocked": self.total_blocked,
            "pass_rate": (self.total_passed / self.total_signals * 100) if self.total_signals > 0 else 0,
            "checkpoints": [cp.to_dict() for cp in self.checkpoints],
        }


class FirewallPipelineVisualization:
    """
    Visualizes the ONI-aligned Neural Firewall pipeline.

    Creates interactive visualizations showing:
    - L8-L14 checkpoint status
    - Signal flow through the pipeline
    - Pass/block statistics per layer
    """

    STATUS_COLORS = {
        CheckpointStatus.PASS: ONI_COLORS["oni_green"],
        CheckpointStatus.FAIL: ONI_COLORS["oni_red"],
        CheckpointStatus.FLAGGED: ONI_COLORS["oni_yellow"],
        CheckpointStatus.PENDING: ONI_COLORS["oni_gray"],
        CheckpointStatus.BYPASSED: ONI_COLORS["oni_muted"],
    }

    def __init__(self, firewall: NeuralFirewall):
        """Initialize with a firewall instance."""
        self.firewall = firewall

    def create_pipeline_figure(
        self,
        show_stats: bool = True,
        height: int = 400,
    ) -> go.Figure:
        """
        Create the main pipeline visualization.

        Shows L8-L14 checkpoints as a horizontal flow with
        status indicators and statistics.
        """
        checkpoints = self.firewall.checkpoints
        n_checkpoints = len(checkpoints)

        if show_stats:
            fig = make_subplots(
                rows=2, cols=1,
                row_heights=[0.6, 0.4],
                vertical_spacing=0.15,
                subplot_titles=("ONI Firewall Pipeline (L8-L14)", "Checkpoint Statistics"),
            )
        else:
            fig = go.Figure()

        # Pipeline nodes
        x_positions = list(range(n_checkpoints))
        y_positions = [0] * n_checkpoints

        # Node colors based on status
        colors = [self.STATUS_COLORS.get(cp.status, ONI_COLORS["oni_gray"]) for cp in checkpoints]

        # Node labels
        labels = [f"L{cp.layer}" for cp in checkpoints]

        # Hover text
        hover_texts = []
        for cp in checkpoints:
            hover_texts.append(
                f"<b>L{cp.layer}: {cp.oni_layer_name}</b><br>"
                f"{cp.name}<br>"
                f"<br>"
                f"Status: {cp.status.value.upper()}<br>"
                f"Processed: {cp.signals_processed}<br>"
                f"Passed: {cp.signals_passed}<br>"
                f"Blocked: {cp.signals_blocked}<br>"
                f"Pass Rate: {cp.pass_rate():.1f}%"
            )

        # Draw connection lines
        for i in range(n_checkpoints - 1):
            fig.add_trace(go.Scatter(
                x=[x_positions[i], x_positions[i + 1]],
                y=[0, 0],
                mode="lines",
                line=dict(color=ONI_COLORS["oni_muted"], width=3),
                showlegend=False,
                hoverinfo="skip",
            ), row=1, col=1) if show_stats else fig.add_trace(go.Scatter(
                x=[x_positions[i], x_positions[i + 1]],
                y=[0, 0],
                mode="lines",
                line=dict(color=ONI_COLORS["oni_muted"], width=3),
                showlegend=False,
                hoverinfo="skip",
            ))

        # Draw checkpoint nodes
        node_trace = go.Scatter(
            x=x_positions,
            y=y_positions,
            mode="markers+text",
            marker=dict(
                size=50,
                color=colors,
                line=dict(width=3, color="white"),
            ),
            text=labels,
            textposition="middle center",
            textfont=dict(color="white", size=12, family="monospace"),
            hoverinfo="text",
            hovertext=hover_texts,
            showlegend=False,
        )

        if show_stats:
            fig.add_trace(node_trace, row=1, col=1)
        else:
            fig.add_trace(node_trace)

        # Add checkpoint names below
        name_trace = go.Scatter(
            x=x_positions,
            y=[-0.3] * n_checkpoints,
            mode="text",
            text=[cp.name for cp in checkpoints],
            textposition="bottom center",
            textfont=dict(color=ONI_COLORS["oni_light"], size=9),
            showlegend=False,
            hoverinfo="skip",
        )

        if show_stats:
            fig.add_trace(name_trace, row=1, col=1)
        else:
            fig.add_trace(name_trace)

        # Add ONI layer names above
        oni_name_trace = go.Scatter(
            x=x_positions,
            y=[0.3] * n_checkpoints,
            mode="text",
            text=[cp.oni_layer_name for cp in checkpoints],
            textposition="top center",
            textfont=dict(color=ONI_COLORS["oni_muted"], size=8),
            showlegend=False,
            hoverinfo="skip",
        )

        if show_stats:
            fig.add_trace(oni_name_trace, row=1, col=1)
        else:
            fig.add_trace(oni_name_trace)

        # Statistics bar chart
        if show_stats:
            # Pass/Block bars
            fig.add_trace(go.Bar(
                x=labels,
                y=[cp.signals_passed for cp in checkpoints],
                name="Passed",
                marker_color=ONI_COLORS["oni_green"],
            ), row=2, col=1)

            fig.add_trace(go.Bar(
                x=labels,
                y=[cp.signals_blocked for cp in checkpoints],
                name="Blocked",
                marker_color=ONI_COLORS["oni_red"],
            ), row=2, col=1)

        # Layout
        fig.update_layout(
            height=height,
            paper_bgcolor=ONI_COLORS["oni_dark"],
            plot_bgcolor=ONI_COLORS["oni_dark"],
            font=dict(color=ONI_COLORS["oni_light"]),
            margin=dict(l=40, r=40, t=60, b=40),
            barmode="stack",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        if show_stats:
            fig.update_xaxes(visible=False, row=1, col=1)
            fig.update_yaxes(visible=False, range=[-0.6, 0.5], row=1, col=1)
            fig.update_xaxes(title_text="ONI Layer", row=2, col=1)
            fig.update_yaxes(title_text="Signals", row=2, col=1)
        else:
            fig.update_xaxes(visible=False)
            fig.update_yaxes(visible=False, range=[-0.6, 0.5])

        return fig

    def create_checkpoint_detail(self, layer: int) -> go.Figure:
        """Create detailed view for a single checkpoint."""
        cp = self.firewall.get_checkpoint(layer)
        if not cp:
            return go.Figure()

        fig = go.Figure()

        # Gauge showing pass rate
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=cp.pass_rate(),
            title={"text": f"L{cp.layer}: {cp.name}<br><sup>{cp.oni_layer_name}</sup>"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": ONI_COLORS["oni_blue"]},
                "steps": [
                    {"range": [0, 50], "color": ONI_COLORS["oni_red"]},
                    {"range": [50, 80], "color": ONI_COLORS["oni_yellow"]},
                    {"range": [80, 100], "color": ONI_COLORS["oni_green"]},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 2},
                    "thickness": 0.75,
                    "value": 90,
                },
            },
            number={"suffix": "%"},
        ))

        fig.update_layout(
            height=250,
            paper_bgcolor=ONI_COLORS["oni_dark"],
            plot_bgcolor=ONI_COLORS["oni_dark"],
            font=dict(color=ONI_COLORS["oni_light"]),
            margin=dict(l=20, r=20, t=60, b=20),
        )

        return fig

    def create_flow_animation(self) -> go.Figure:
        """Create animated signal flow visualization."""
        # Placeholder for animated flow
        return self.create_pipeline_figure(show_stats=False, height=200)
