"""
ONI Framework Color Theme

Consistent visual language for all TARA visualizations,
derived from the ONI Visualization Suite design system.
"""

from typing import Dict, Any
import plotly.graph_objects as go

# ONI Color Palette
ONI_COLORS: Dict[str, str] = {
    # Primary accent colors
    "oni_blue": "#00d4ff",
    "oni_purple": "#8b5cf6",
    "oni_pink": "#ec4899",

    # Status colors
    "oni_green": "#10b981",   # Success, secure, pass
    "oni_yellow": "#f59e0b",  # Warning, caution, flagged
    "oni_red": "#ef4444",     # Danger, critical, blocked
    "oni_orange": "#f97316",  # Alert, attention

    # Background colors
    "oni_dark": "#0a0e17",    # Primary background
    "oni_darker": "#060912",  # Deeper background
    "oni_gray": "#1e293b",    # Surface/card background

    # Text colors
    "oni_light": "#e2e8f0",   # Primary text
    "oni_muted": "#64748b",   # Secondary/muted text
    "oni_subtle": "#94a3b8",  # Subtle text

    # Domain colors (ONI 14-layer model)
    "domain_silicon": "#3b82f6",     # L1-L7: Silicon/OSI layers (blue)
    "domain_gateway": "#10b981",     # L8: Neural Gateway (green)
    "domain_interface": "#8b5cf6",   # L9-L10: Interface layers (purple)
    "domain_cognitive": "#ec4899",   # L11-L14: Cognitive layers (pink)

    # Signal status
    "signal_normal": "#10b981",
    "signal_warning": "#f59e0b",
    "signal_critical": "#ef4444",
    "signal_offline": "#64748b",

    # Firewall checkpoint status
    "checkpoint_pass": "#10b981",  # nosec B105 - not a password, color value
    "checkpoint_fail": "#ef4444",
    "checkpoint_flagged": "#f59e0b",
    "checkpoint_pending": "#64748b",
    "checkpoint_bypassed": "#8b5cf6",
}

# Layer-to-color mapping for ONI 14-layer model
LAYER_COLORS: Dict[int, str] = {
    # Silicon layers (L1-L7) - OSI model
    1: "#1e40af",   # Physical Carrier
    2: "#1d4ed8",   # Data Link (Signal Processing)
    3: "#2563eb",   # Network (Protocol)
    4: "#3b82f6",   # Transport
    5: "#60a5fa",   # Session
    6: "#93c5fd",   # Presentation
    7: "#bfdbfe",   # Application Interface

    # Gateway layer (L8)
    8: "#10b981",   # Neural Gateway (Firewall)

    # Cognitive layers (L9-L14) - ONI Extension
    9: "#7c3aed",   # Signal Processing (Filtering)
    10: "#8b5cf6",  # Neural Protocol (Encoding)
    11: "#c026d3",  # Cognitive Transport (Delivery)
    12: "#db2777",  # Cognitive Session (Context)
    13: "#ec4899",  # Semantic Layer (Intent)
    14: "#f472b6",  # Identity Layer (Self)
}

# Default colorway for Plotly charts
DEFAULT_COLORWAY = [
    ONI_COLORS["oni_blue"],
    ONI_COLORS["oni_green"],
    ONI_COLORS["oni_purple"],
    ONI_COLORS["oni_pink"],
    ONI_COLORS["oni_yellow"],
    ONI_COLORS["oni_red"],
    ONI_COLORS["oni_orange"],
]


def apply_oni_theme(fig: go.Figure, height: int = None) -> go.Figure:
    """
    Apply ONI theme to a Plotly figure.

    Args:
        fig: Plotly figure to style
        height: Optional height override

    Returns:
        Styled figure
    """
    layout_updates = {
        "paper_bgcolor": ONI_COLORS["oni_dark"],
        "plot_bgcolor": ONI_COLORS["oni_dark"],
        "font": {
            "color": ONI_COLORS["oni_light"],
            "family": "SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif",
        },
        "colorway": DEFAULT_COLORWAY,
        "margin": {"l": 40, "r": 40, "t": 40, "b": 40},
    }

    if height:
        layout_updates["height"] = height

    fig.update_layout(**layout_updates)

    # Style axes
    axis_style = {
        "gridcolor": ONI_COLORS["oni_gray"],
        "linecolor": ONI_COLORS["oni_gray"],
        "tickcolor": ONI_COLORS["oni_muted"],
        "tickfont": {"color": ONI_COLORS["oni_muted"]},
        "title_font": {"color": ONI_COLORS["oni_light"]},
    }

    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)

    return fig


def get_status_color(status: str) -> str:
    """Get color for a status string."""
    status_map = {
        "normal": ONI_COLORS["signal_normal"],
        "healthy": ONI_COLORS["signal_normal"],
        "pass": ONI_COLORS["checkpoint_pass"],
        "success": ONI_COLORS["oni_green"],

        "warning": ONI_COLORS["signal_warning"],
        "caution": ONI_COLORS["signal_warning"],
        "flagged": ONI_COLORS["checkpoint_flagged"],

        "critical": ONI_COLORS["signal_critical"],
        "danger": ONI_COLORS["signal_critical"],
        "fail": ONI_COLORS["checkpoint_fail"],
        "blocked": ONI_COLORS["oni_red"],

        "offline": ONI_COLORS["signal_offline"],
        "inactive": ONI_COLORS["signal_offline"],
        "pending": ONI_COLORS["checkpoint_pending"],

        "bypassed": ONI_COLORS["checkpoint_bypassed"],
    }
    return status_map.get(status.lower(), ONI_COLORS["oni_muted"])


def get_layer_color(layer: int) -> str:
    """Get color for an ONI layer number (1-14)."""
    return LAYER_COLORS.get(layer, ONI_COLORS["oni_muted"])


def get_domain_color(layer: int) -> str:
    """Get domain color for an ONI layer (silicon, gateway, interface, cognitive)."""
    if 1 <= layer <= 7:
        return ONI_COLORS["domain_silicon"]
    elif layer == 8:
        return ONI_COLORS["domain_gateway"]
    elif 9 <= layer <= 10:
        return ONI_COLORS["domain_interface"]
    elif 11 <= layer <= 14:
        return ONI_COLORS["domain_cognitive"]
    return ONI_COLORS["oni_muted"]
