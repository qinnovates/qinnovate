"""
ONI Visualizations Embedding

Utilities for embedding the ONI Visualization Suite HTML apps
into the TARA Streamlit dashboard with bidirectional messaging.
"""

from .html_bridge import (
    ONIVisualizationEmbed,
    render_oni_visualization,
    get_visualization_options,
)

__all__ = [
    "ONIVisualizationEmbed",
    "render_oni_visualization",
    "get_visualization_options",
]
