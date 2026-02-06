"""
Brain Topology Visualization

3D brain visualization with BCI node monitoring, supporting:
- Semi-transparent brain mesh
- Brain region highlighting
- Electrode threads with real-time metrics
- Drill-down from region to thread to electrode
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

try:
    from ..themes.oni_theme import ONI_COLORS, apply_oni_theme, get_status_color
    from ...data.brain_regions import (
        BrainRegion,
        BRAIN_REGIONS,
        Electrode,
        ElectrodeThread,
        ElectrodeArray,
        ElectrodeStatus,
    )
except ImportError:
    # Fallback for direct imports
    from tara_mvp.visualization.themes.oni_theme import ONI_COLORS, apply_oni_theme, get_status_color
    from tara_mvp.data.brain_regions import (
        BrainRegion,
        BRAIN_REGIONS,
        Electrode,
        ElectrodeThread,
        ElectrodeArray,
        ElectrodeStatus,
    )


class BrainTopologyVisualization:
    """
    3D brain visualization with BCI node monitoring.

    Renders:
    - Semi-transparent brain surface mesh
    - Color-coded brain regions
    - Electrode threads with metric-based coloring
    - Interactive drill-down support

    Example:
        >>> from tara_mvp.data.brain_regions import create_demo_array
        >>> viz = BrainTopologyVisualization()
        >>> viz.set_electrode_array(create_demo_array())
        >>> fig = viz.render(color_by="spike_rate")
        >>> fig.show()
    """

    def __init__(self, regions: Dict[str, BrainRegion] = None):
        """
        Initialize the visualization.

        Args:
            regions: Brain region definitions (default: BRAIN_REGIONS)
        """
        self.regions = regions or BRAIN_REGIONS
        self.electrode_array: Optional[ElectrodeArray] = None
        self._fig: Optional[go.Figure] = None

    def set_electrode_array(self, array: ElectrodeArray) -> None:
        """Set the electrode array to visualize."""
        self.electrode_array = array
        self._fig = None  # Invalidate cached figure

    def create_brain_mesh(self, opacity: float = 0.08) -> go.Mesh3d:
        """
        Generate a simplified brain surface mesh.

        Creates an ellipsoid approximation of the brain surface.
        Brain dimensions approximately 170 x 140 x 140 mm.

        Args:
            opacity: Surface opacity (0-1)

        Returns:
            Plotly Mesh3d trace
        """
        # Generate ellipsoid points
        u = np.linspace(0, 2 * np.pi, 40)
        v = np.linspace(0, np.pi, 20)

        # Brain dimensions in mm (half-axes)
        a, b, c = 85, 70, 70

        x = a * np.outer(np.cos(u), np.sin(v))
        y = b * np.outer(np.sin(u), np.sin(v))
        z = c * np.outer(np.ones(np.size(u)), np.cos(v))

        # Flatten for mesh
        x_flat = x.flatten()
        y_flat = y.flatten()
        z_flat = z.flatten()

        return go.Mesh3d(
            x=x_flat,
            y=y_flat,
            z=z_flat,
            opacity=opacity,
            color=ONI_COLORS["oni_gray"],
            alphahull=0,
            name="Brain Surface",
            hoverinfo="skip",
            showlegend=False,
        )

    def create_region_markers(
        self,
        highlight_region: str = None,
        show_labels: bool = True,
    ) -> List[go.Scatter3d]:
        """
        Create markers for brain regions.

        Args:
            highlight_region: Region abbreviation to highlight
            show_labels: Whether to show region labels

        Returns:
            List of Scatter3d traces
        """
        traces = []

        for abbr, region in self.regions.items():
            # Generate sphere surface points
            n_points = 15
            phi = np.linspace(0, 2 * np.pi, n_points)
            theta = np.linspace(0, np.pi, n_points // 2)

            cx, cy, cz = region.center
            r = region.radius

            x = cx + r * np.outer(np.cos(phi), np.sin(theta))
            y = cy + r * np.outer(np.sin(phi), np.sin(theta))
            z = cz + r * np.outer(np.ones(n_points), np.cos(theta))

            # Determine opacity
            is_highlighted = abbr == highlight_region
            opacity = 0.5 if is_highlighted else 0.2

            # Create surface trace
            traces.append(go.Scatter3d(
                x=x.flatten(),
                y=y.flatten(),
                z=z.flatten(),
                mode="markers",
                marker=dict(
                    size=2,
                    color=region.color,
                    opacity=opacity,
                ),
                name=f"{abbr}: {region.name}",
                hovertemplate=(
                    f"<b>{region.name}</b> ({abbr})<br>"
                    f"Function: {region.function.name}<br>"
                    f"ONI Layer: L{region.oni_layer}<br>"
                    f"{region.description}<extra></extra>"
                ),
                showlegend=True,
            ))

            # Add center label
            if show_labels:
                traces.append(go.Scatter3d(
                    x=[cx],
                    y=[cy],
                    z=[cz + r + 5],  # Above the region
                    mode="text",
                    text=[abbr],
                    textfont=dict(
                        size=12,
                        color=region.color,
                    ),
                    hoverinfo="skip",
                    showlegend=False,
                ))

        return traces

    def create_electrode_traces(
        self,
        color_by: str = "spike_rate",
        show_threads: bool = True,
        filter_region: str = None,
    ) -> List[go.Scatter3d]:
        """
        Create electrode visualization traces.

        Args:
            color_by: Metric to color by (spike_rate, impedance, snr, status)
            show_threads: Whether to show thread lines
            filter_region: Only show electrodes in this region

        Returns:
            List of Scatter3d traces
        """
        if not self.electrode_array:
            return []

        traces = []

        # Colorscale selection
        colorscales = {
            "spike_rate": "RdYlGn",      # Red (low) to Green (high)
            "impedance": "RdYlGn_r",     # Green (low/good) to Red (high/bad)
            "snr": "Viridis",
            "lfp_power": "Plasma",
        }

        for thread in self.electrode_array.threads:
            # Skip if filtering by region
            if filter_region and thread.region != filter_region:
                continue

            if not thread.electrodes:
                continue

            # Get electrode positions
            positions = [e.position for e in thread.electrodes]

            # Thread line
            if show_threads:
                thread_x = [thread.insertion_point[0]] + [p[0] for p in positions]
                thread_y = [thread.insertion_point[1]] + [p[1] for p in positions]
                thread_z = [thread.insertion_point[2]] + [p[2] for p in positions]

                traces.append(go.Scatter3d(
                    x=thread_x,
                    y=thread_y,
                    z=thread_z,
                    mode="lines",
                    line=dict(
                        color=ONI_COLORS["oni_muted"],
                        width=2,
                    ),
                    name=f"Thread {thread.thread_id}",
                    hoverinfo="skip",
                    showlegend=False,
                ))

            # Electrode markers
            if color_by == "status":
                colors = [get_status_color(e.status.value) for e in thread.electrodes]
                colorscale = None
                showscale = False
            else:
                colors = [getattr(e, color_by, 0) for e in thread.electrodes]
                colorscale = colorscales.get(color_by, "Viridis")
                showscale = True

            hover_text = [
                f"<b>{e.electrode_id}</b><br>"
                f"Region: {e.region}<br>"
                f"Depth: {e.depth:.1f}mm<br>"
                f"Spike Rate: {e.spike_rate:.1f} Hz<br>"
                f"Impedance: {e.impedance:.0f} kΩ<br>"
                f"SNR: {e.snr:.1f} dB<br>"
                f"Status: {e.status.value}"
                for e in thread.electrodes
            ]

            marker_config = dict(
                size=6,
                color=colors,
                opacity=0.9,
                line=dict(width=1, color="white"),
            )

            if colorscale:
                marker_config["colorscale"] = colorscale
                marker_config["showscale"] = showscale
                marker_config["colorbar"] = dict(
                    title=dict(
                        text=color_by.replace("_", " ").title(),
                        font=dict(color=ONI_COLORS["oni_light"]),
                    ),
                    tickfont=dict(color=ONI_COLORS["oni_light"]),
                )

            traces.append(go.Scatter3d(
                x=[p[0] for p in positions],
                y=[p[1] for p in positions],
                z=[p[2] for p in positions],
                mode="markers",
                marker=marker_config,
                text=hover_text,
                hoverinfo="text",
                name=f"{thread.thread_id} Electrodes",
                showlegend=False,
            ))

        return traces

    def render(
        self,
        highlight_region: str = None,
        color_by: str = "spike_rate",
        show_brain: bool = True,
        show_regions: bool = True,
        show_electrodes: bool = True,
        show_threads: bool = True,
        filter_region: str = None,
        camera: Dict = None,
        height: int = 600,
    ) -> go.Figure:
        """
        Render the complete brain topology visualization.

        Args:
            highlight_region: Region to highlight
            color_by: Metric for electrode coloring
            show_brain: Show brain surface mesh
            show_regions: Show region markers
            show_electrodes: Show electrode markers
            show_threads: Show thread lines
            filter_region: Only show this region's electrodes
            camera: Custom camera position
            height: Figure height in pixels

        Returns:
            Plotly Figure
        """
        fig = go.Figure()

        # Add brain mesh
        if show_brain:
            fig.add_trace(self.create_brain_mesh())

        # Add region markers
        if show_regions:
            for trace in self.create_region_markers(
                highlight_region=highlight_region,
                show_labels=True,
            ):
                fig.add_trace(trace)

        # Add electrodes
        if show_electrodes and self.electrode_array:
            for trace in self.create_electrode_traces(
                color_by=color_by,
                show_threads=show_threads,
                filter_region=filter_region,
            ):
                fig.add_trace(trace)

        # Default camera
        if camera is None:
            camera = dict(
                eye=dict(x=1.5, y=1.5, z=0.8),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1),
            )

        # Layout
        fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False, showgrid=False),
                yaxis=dict(visible=False, showgrid=False),
                zaxis=dict(visible=False, showgrid=False),
                bgcolor=ONI_COLORS["oni_dark"],
                camera=camera,
                aspectmode="data",
            ),
            paper_bgcolor=ONI_COLORS["oni_dark"],
            plot_bgcolor=ONI_COLORS["oni_dark"],
            font=dict(color=ONI_COLORS["oni_light"]),
            margin=dict(l=0, r=0, t=30, b=0),
            height=height,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(10, 14, 23, 0.8)",
                bordercolor=ONI_COLORS["oni_gray"],
                borderwidth=1,
            ),
        )

        self._fig = fig
        return fig

    def render_region_detail(
        self,
        region: str,
        color_by: str = "spike_rate",
        height: int = 500,
    ) -> go.Figure:
        """
        Render a zoomed view of a specific region.

        Args:
            region: Region abbreviation
            color_by: Metric for electrode coloring
            height: Figure height

        Returns:
            Plotly Figure
        """
        if region not in self.regions:
            raise ValueError(f"Unknown region: {region}")

        region_data = self.regions[region]
        cx, cy, cz = region_data.center

        # Camera focused on region
        camera = dict(
            eye=dict(
                x=cx / 50 + 0.5,
                y=cy / 50 + 0.5,
                z=cz / 50 + 0.3,
            ),
            center=dict(
                x=cx / 100,
                y=cy / 100,
                z=cz / 100,
            ),
        )

        return self.render(
            highlight_region=region,
            color_by=color_by,
            filter_region=region,
            show_brain=False,
            camera=camera,
            height=height,
        )

    def create_metrics_summary(self, region: str = None) -> go.Figure:
        """
        Create a metrics summary panel for electrodes.

        Args:
            region: Optional region filter

        Returns:
            Plotly Figure with metric gauges
        """
        if not self.electrode_array:
            return go.Figure()

        # Collect electrode data
        electrodes = []
        for thread in self.electrode_array.threads:
            if region and thread.region != region:
                continue
            electrodes.extend(thread.electrodes)

        if not electrodes:
            return go.Figure()

        # Calculate statistics
        active = [e for e in electrodes if e.status != ElectrodeStatus.OFFLINE]
        avg_spike_rate = np.mean([e.spike_rate for e in active]) if active else 0
        avg_impedance = np.mean([e.impedance for e in active]) if active else 0
        avg_snr = np.mean([e.snr for e in active]) if active else 0
        health_pct = len([e for e in electrodes if e.is_healthy()]) / len(electrodes) * 100

        # Create gauge subplot
        fig = make_subplots(
            rows=1, cols=4,
            specs=[[{"type": "indicator"}] * 4],
            subplot_titles=["Spike Rate", "Impedance", "SNR", "Health"],
        )

        # Spike rate gauge
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=avg_spike_rate,
            title={"text": "Hz"},
            gauge=dict(
                axis=dict(range=[0, 50]),
                bar=dict(color=ONI_COLORS["oni_blue"]),
                steps=[
                    {"range": [0, 5], "color": ONI_COLORS["oni_red"]},
                    {"range": [5, 30], "color": ONI_COLORS["oni_green"]},
                    {"range": [30, 50], "color": ONI_COLORS["oni_yellow"]},
                ],
            ),
        ), row=1, col=1)

        # Impedance gauge
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=avg_impedance,
            title={"text": "kΩ"},
            gauge=dict(
                axis=dict(range=[0, 1000]),
                bar=dict(color=ONI_COLORS["oni_purple"]),
                steps=[
                    {"range": [0, 300], "color": ONI_COLORS["oni_green"]},
                    {"range": [300, 500], "color": ONI_COLORS["oni_yellow"]},
                    {"range": [500, 1000], "color": ONI_COLORS["oni_red"]},
                ],
            ),
        ), row=1, col=2)

        # SNR gauge
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=avg_snr,
            title={"text": "dB"},
            gauge=dict(
                axis=dict(range=[0, 30]),
                bar=dict(color=ONI_COLORS["oni_pink"]),
                steps=[
                    {"range": [0, 5], "color": ONI_COLORS["oni_red"]},
                    {"range": [5, 10], "color": ONI_COLORS["oni_yellow"]},
                    {"range": [10, 30], "color": ONI_COLORS["oni_green"]},
                ],
            ),
        ), row=1, col=3)

        # Health percentage
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=health_pct,
            title={"text": "%"},
            gauge=dict(
                axis=dict(range=[0, 100]),
                bar=dict(color=ONI_COLORS["oni_green"]),
                steps=[
                    {"range": [0, 70], "color": ONI_COLORS["oni_red"]},
                    {"range": [70, 90], "color": ONI_COLORS["oni_yellow"]},
                    {"range": [90, 100], "color": ONI_COLORS["oni_green"]},
                ],
            ),
        ), row=1, col=4)

        fig.update_layout(
            paper_bgcolor=ONI_COLORS["oni_dark"],
            plot_bgcolor=ONI_COLORS["oni_dark"],
            font=dict(color=ONI_COLORS["oni_light"]),
            height=200,
            margin=dict(l=20, r=20, t=40, b=20),
        )

        return fig
