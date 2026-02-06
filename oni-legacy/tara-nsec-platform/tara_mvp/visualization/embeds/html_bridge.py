"""
ONI Visualizations Embedding Bridge

Embeds the ONI Visualization Suite HTML apps into Streamlit
with bidirectional messaging support for data synchronization.

The ONI Visualization Suite includes:
- Coherence Metric Playground
- ONI Layer Explorer
- Neural Kill Chain Visualizer
- NSAM Checkpoint Simulator
- Scale-Frequency Navigator
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import streamlit.components.v1 as components


class ONIVisualizationEmbed:
    """
    Embeds ONI HTML visualizations with bidirectional communication.

    Example:
        >>> embed = ONIVisualizationEmbed("/path/to/visualizations")
        >>> embed.render("coherence", height=600, initial_data={"cs": 0.85})
    """

    # Mapping of visualization keys to HTML files
    VISUALIZATIONS = {
        "coherence": {
            "file": "01-coherence-metric-playground.html",
            "title": "Coherence Metric Playground",
            "description": "Interactive coherence calculation and visualization",
        },
        "layers": {
            "file": "02-oni-layer-explorer.html",
            "title": "ONI Layer Explorer",
            "description": "Navigate the 14-layer ONI model",
        },
        "killchain": {
            "file": "03-neural-killchain-visualizer.html",
            "title": "Neural Kill Chain Visualizer",
            "description": "Attack propagation visualization",
        },
        "nsam": {
            "file": "04-nsam-checkpoint-simulator.html",
            "title": "NSAM Checkpoint Simulator",
            "description": "Signal assurance checkpoint game",
        },
        "scale_freq": {
            "file": "05-scale-frequency-navigator.html",
            "title": "Scale-Frequency Navigator",
            "description": "Temporal scale exploration",
        },
    }

    def __init__(self, base_path: str = None):
        """
        Initialize the embed manager.

        Args:
            base_path: Path to visualizations directory.
                       If None, attempts to find it relative to TARA.
        """
        self._available = True

        if base_path:
            self.base_path = Path(base_path)
        else:
            # Try to find visualizations relative to tara_mvp package
            tara_root = Path(__file__).parent.parent.parent

            # Try multiple possible locations
            # Visualizations canonical location: docs/visualizations/
            possible_paths = [
                tara_root.parent.parent.parent / "docs" / "visualizations",  # Dev: ONI/docs/visualizations
                tara_root.parent.parent / "docs" / "visualizations",         # Alternative
                Path.cwd() / "docs" / "visualizations",                      # Current working directory
                Path.cwd().parent / "docs" / "visualizations",               # Parent of cwd
            ]

            self.base_path = None
            for path in possible_paths:
                if path.exists() and (path / "index.html").exists():
                    self.base_path = path
                    break

            if self.base_path is None:
                self._available = False
                self.base_path = possible_paths[0]  # Set default for error messages

        if self._available:
            self._validate_path()

    def _validate_path(self) -> None:
        """Validate that the visualization files exist."""
        if not self.base_path.exists():
            self._available = False

    @property
    def is_available(self) -> bool:
        """Check if visualizations are available."""
        return self._available

    def get_available(self) -> Dict[str, Dict[str, str]]:
        """Get list of available visualizations."""
        available = {}
        for key, info in self.VISUALIZATIONS.items():
            file_path = self.base_path / info["file"]
            if file_path.exists():
                available[key] = {
                    "title": info["title"],
                    "description": info["description"],
                    "path": str(file_path),
                }
        return available

    def render(
        self,
        visualization: str,
        height: int = 600,
        initial_data: Dict[str, Any] = None,
        scrolling: bool = True,
    ) -> None:
        """
        Render an ONI visualization in Streamlit.

        Args:
            visualization: Key from VISUALIZATIONS (e.g., "coherence")
            height: iframe height in pixels
            initial_data: Data to inject on load
            scrolling: Whether to allow scrolling
        """
        if visualization not in self.VISUALIZATIONS:
            raise ValueError(
                f"Unknown visualization: {visualization}. "
                f"Available: {list(self.VISUALIZATIONS.keys())}"
            )

        if not self._available:
            # Render a helpful message instead of crashing
            error_html = f"""
            <div style="padding: 40px; text-align: center; background: #1e293b; border-radius: 8px; color: #e2e8f0;">
                <h3 style="color: #f97316;">ONI Visualization Suite Not Found</h3>
                <p>The interactive visualizations are not included in the PyPI package.</p>
                <p style="margin-top: 20px;"><strong>To enable visualizations:</strong></p>
                <ol style="text-align: left; max-width: 500px; margin: 20px auto;">
                    <li>Clone the repository: <code>git clone https://github.com/qikevinl/oni</code></li>
                    <li>Navigate to: <code>cd MAIN/legacy-core/tara-nsec-platform</code></li>
                    <li>Install locally: <code>pip install -e .</code></li>
                    <li>Run: <code>tara ui</code></li>
                </ol>
                <p style="margin-top: 20px; color: #94a3b8;">
                    Or open the HTML files directly:<br>
                    <code>docs/visualizations/index.html</code>
                </p>
            </div>
            """
            components.html(error_html, height=300)
            return

        info = self.VISUALIZATIONS[visualization]
        html_file = self.base_path / info["file"]

        if not html_file.exists():
            raise FileNotFoundError(f"Visualization file not found: {html_file}")

        # Read HTML content
        html_content = html_file.read_text(encoding="utf-8")

        # Inject data bridge if initial_data provided
        if initial_data:
            html_content = self._inject_bridge(html_content, initial_data)

        # Render with Streamlit components
        components.html(html_content, height=height, scrolling=scrolling)

    def _inject_bridge(self, html: str, data: Dict[str, Any]) -> str:
        """
        Inject JavaScript bridge for data communication.

        The bridge provides:
        - TARA_BRIDGE.initialData: Data passed from TARA
        - TARA_BRIDGE.sendToStreamlit(event, payload): Send events back

        Args:
            html: Original HTML content
            data: Data to inject

        Returns:
            Modified HTML with bridge script
        """
        bridge_script = f"""
<script>
    // TARA-ONI Visualization Bridge
    window.TARA_BRIDGE = {{
        // Initial data from TARA
        initialData: {json.dumps(data)},

        // Send event back to Streamlit (for future use with custom components)
        sendToStreamlit: function(eventType, payload) {{
            window.parent.postMessage({{
                type: 'tara_event',
                event: eventType,
                data: payload,
                timestamp: Date.now()
            }}, '*');
        }},

        // Update data (can be called from TARA via postMessage)
        updateData: function(newData) {{
            this.initialData = {{...this.initialData, ...newData}};
            if (this.onDataUpdate) {{
                this.onDataUpdate(this.initialData);
            }}
        }},

        // Register callback for data updates
        onDataUpdate: null
    }};

    // Listen for updates from parent (Streamlit)
    window.addEventListener('message', function(event) {{
        if (event.data && event.data.type === 'tara_update') {{
            window.TARA_BRIDGE.updateData(event.data.data);
        }}
    }});

    // Notify parent that bridge is ready
    window.parent.postMessage({{
        type: 'tara_bridge_ready',
        visualization: '{data.get("_visualization", "unknown")}'
    }}, '*');
</script>
"""
        # Insert before closing </head> tag
        if "</head>" in html:
            return html.replace("</head>", f"{bridge_script}</head>")
        else:
            # Fallback: insert at beginning of body
            return html.replace("<body>", f"<body>{bridge_script}")

    def render_inline_frame(
        self,
        visualization: str,
        height: int = 600,
        border: bool = False,
    ) -> str:
        """
        Get an iframe HTML string for manual embedding.

        Useful for embedding in custom Streamlit components or
        external HTML pages.

        Args:
            visualization: Key from VISUALIZATIONS
            height: iframe height in pixels
            border: Whether to show border

        Returns:
            HTML iframe string
        """
        if visualization not in self.VISUALIZATIONS:
            raise ValueError(f"Unknown visualization: {visualization}")

        info = self.VISUALIZATIONS[visualization]
        file_path = self.base_path / info["file"]

        border_style = "1px solid #1e293b" if border else "none"

        return f'''
<iframe
    src="file://{file_path}"
    width="100%"
    height="{height}px"
    style="border: {border_style}; border-radius: 8px;"
    title="{info['title']}"
></iframe>
'''


def render_oni_visualization(
    key: str,
    height: int = 600,
    data: Dict[str, Any] = None,
    base_path: str = None,
) -> None:
    """
    Convenience function to render an ONI visualization.

    Args:
        key: Visualization key (coherence, layers, killchain, nsam, scale_freq)
        height: Display height in pixels
        data: Initial data to pass to visualization
        base_path: Path to visualizations directory
    """
    embed = ONIVisualizationEmbed(base_path)
    embed.render(key, height=height, initial_data=data)


def get_visualization_options() -> Dict[str, str]:
    """Get visualization options for Streamlit selectbox."""
    return {
        "coherence": "Coherence Metric Playground",
        "layers": "ONI Layer Explorer",
        "killchain": "Neural Kill Chain Visualizer",
        "nsam": "NSAM Checkpoint Simulator",
        "scale_freq": "Scale-Frequency Navigator",
    }
