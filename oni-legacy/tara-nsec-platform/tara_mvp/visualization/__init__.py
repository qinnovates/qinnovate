"""
TARA Visualization Module

Provides visualization components for neural security monitoring:
- Brain topology with BCI node visualization
- Neural firewall pipeline visualization
- ONI-visualizations embedding
- Real-time signal displays
"""

from .themes.oni_theme import (
    ONI_COLORS,
    apply_oni_theme,
    get_status_color,
    get_layer_color,
    get_domain_color,
    LAYER_COLORS,
)

from .components import (
    BrainTopologyVisualization,
    FirewallPipelineVisualization,
    NeuralFirewall,
    FirewallCheckpoint,
    CheckpointStatus,
)

from .embeds import (
    ONIVisualizationEmbed,
    render_oni_visualization,
    get_visualization_options,
)

__all__ = [
    # Theme
    "ONI_COLORS",
    "LAYER_COLORS",
    "apply_oni_theme",
    "get_status_color",
    "get_layer_color",
    "get_domain_color",
    # Components
    "BrainTopologyVisualization",
    "FirewallPipelineVisualization",
    "NeuralFirewall",
    "FirewallCheckpoint",
    "CheckpointStatus",
    # Embeds
    "ONIVisualizationEmbed",
    "render_oni_visualization",
    "get_visualization_options",
]
