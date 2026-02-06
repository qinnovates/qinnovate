"""
TARA Unified Dashboard

Telemetry Analysis & Response Automation

Streamlit-based dashboard combining:
- Neural network simulation
- Attack simulation and testing
- Real-time Neural Signal Assurance Monitoring
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# TARA UI styles (cyberpunk theme)
from tara_mvp.ui.styles import inject_styles, header_section, status_card, metric_display

# TARA visualization imports
try:
    from tara_mvp.visualization.components.brain_topology import BrainTopologyVisualization
    from tara_mvp.visualization.components.firewall_pipeline import (
        NeuralFirewall,
        FirewallPipelineVisualization,
        CheckpointStatus,
    )
    from tara_mvp.visualization.themes.oni_theme import ONI_COLORS, apply_oni_theme
    from tara_mvp.data.brain_regions import (
        BRAIN_REGIONS,
        create_demo_array,
        ElectrodeStatus,
    )
    from tara_mvp.data.bci_nodes import (
        BCINode,
        BCINodeNetwork,
        NodeStatus,
        ConnectionStatus,
        create_demo_network,
    )
    from tara_mvp.visualization.embeds.html_bridge import (
        ONIVisualizationEmbed,
        get_visualization_options,
    )
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    VISUALIZATION_AVAILABLE = False
    print(f"Visualization modules not available: {e}")

# Page configuration
st.set_page_config(
    page_title="TARA - Neural Security Platform",
    page_icon="T",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject cyberpunk styles
inject_styles()


def init_session_state():
    """Initialize session state variables."""
    if "monitor_running" not in st.session_state:
        st.session_state.monitor_running = False
    if "simulation_data" not in st.session_state:
        st.session_state.simulation_data = None
    if "attack_results" not in st.session_state:
        st.session_state.attack_results = None
    if "metrics_history" not in st.session_state:
        st.session_state.metrics_history = {
            "timestamps": [],
            "coherence": [],
            "spike_rate": [],
            "amplitude": [],
        }
    if "alerts" not in st.session_state:
        st.session_state.alerts = []
    if "events" not in st.session_state:
        st.session_state.events = []

    # Brain topology state
    if "electrode_array" not in st.session_state:
        if VISUALIZATION_AVAILABLE:
            st.session_state.electrode_array = create_demo_array(
                n_threads_per_region=4,
                n_electrodes_per_thread=16,
                regions=["M1", "S1", "PMC"],
            )
        else:
            st.session_state.electrode_array = None
    if "topology_view" not in st.session_state:
        st.session_state.topology_view = "overview"
    if "selected_region" not in st.session_state:
        st.session_state.selected_region = None

    # Neural firewall state
    if "neural_firewall" not in st.session_state:
        if VISUALIZATION_AVAILABLE:
            st.session_state.neural_firewall = NeuralFirewall()
        else:
            st.session_state.neural_firewall = None
    if "firewall_signals_processed" not in st.session_state:
        st.session_state.firewall_signals_processed = 0

    # BCI Node network state (ONI Firewall nodes at Layer 8)
    if "bci_network" not in st.session_state:
        if VISUALIZATION_AVAILABLE:
            st.session_state.bci_network = create_demo_network(n_nodes=4)
        else:
            st.session_state.bci_network = None

    # Neurosecurity page state
    if "privacy_score_result" not in st.session_state:
        st.session_state.privacy_score_result = None
    if "selected_erps" not in st.session_state:
        st.session_state.selected_erps = []
    if "threat_classification" not in st.session_state:
        st.session_state.threat_classification = None

    # Real EEG Data page state
    if "moabb_signals" not in st.session_state:
        st.session_state.moabb_signals = None
    if "moabb_dataset" not in st.session_state:
        st.session_state.moabb_dataset = None
    if "moabb_benchmark_results" not in st.session_state:
        st.session_state.moabb_benchmark_results = None

    # Attack animation state
    if "attack_animation_state" not in st.session_state:
        st.session_state.attack_animation_state = None
    if "attack_animation_frame" not in st.session_state:
        st.session_state.attack_animation_frame = 0


def render_sidebar():
    """Render the sidebar navigation."""
    st.sidebar.title("TARA")
    st.sidebar.caption("Neural Security Platform")
    st.sidebar.divider()

    # Navigation
    st.sidebar.markdown("**Monitoring**")

    # Use session state to track current page
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    # Monitoring section
    monitoring_pages = ["Dashboard", "Brain Topology", "Neural Firewall", "Signal Assurance", "Neurosecurity"]
    for p in monitoring_pages:
        if st.sidebar.button(p, key=f"nav_{p}", width="stretch",
                            type="primary" if st.session_state.current_page == p else "secondary"):
            st.session_state.current_page = p
            st.rerun()

    st.sidebar.markdown("")
    st.sidebar.markdown("**Data**")

    # Data section
    data_pages = ["Real EEG Data"]
    for p in data_pages:
        if st.sidebar.button(p, key=f"nav_{p}", width="stretch",
                            type="primary" if st.session_state.current_page == p else "secondary"):
            st.session_state.current_page = p
            st.rerun()

    st.sidebar.markdown("")
    st.sidebar.markdown("**Simulations**")

    # Simulations section
    simulations_pages = ["Neural Simulator", "Attack Simulator"]
    for p in simulations_pages:
        if st.sidebar.button(p, key=f"nav_{p}", width="stretch",
                            type="primary" if st.session_state.current_page == p else "secondary"):
            st.session_state.current_page = p
            st.rerun()

    st.sidebar.markdown("")
    st.sidebar.markdown("**Configuration**")

    # Config section
    if st.sidebar.button("Settings", key="nav_Settings", width="stretch",
                        type="primary" if st.session_state.current_page == "Settings" else "secondary"):
        st.session_state.current_page = "Settings"
        st.rerun()


def _create_node_network_viz(network: BCINodeNetwork) -> go.Figure:
    """
    Create a network topology visualization for BCI nodes.

    Shows nodes as circles with connections between them.
    Color indicates health status.
    """
    # Get topology data
    topo = network.get_topology_data()
    nodes = topo["nodes"]
    edges = topo["edges"]

    # Position nodes in a circle
    n_nodes = len(nodes)
    angles = np.linspace(0, 2 * np.pi, n_nodes, endpoint=False)
    radius = 1.0

    node_x = [radius * np.cos(a) for a in angles]
    node_y = [radius * np.sin(a) for a in angles]

    # Map node IDs to positions
    pos_map = {nodes[i]["id"]: (node_x[i], node_y[i]) for i in range(n_nodes)}

    fig = go.Figure()

    # Draw edges (connections)
    for edge in edges:
        src_pos = pos_map.get(edge["source"])
        tgt_pos = pos_map.get(edge["target"])
        if src_pos and tgt_pos:
            # Color based on connection quality
            quality = edge.get("quality", 0.5)
            if quality > 0.8:
                line_color = "#10b981"  # Green
            elif quality > 0.5:
                line_color = "#f59e0b"  # Yellow
            else:
                line_color = "#ef4444"  # Red

            fig.add_trace(go.Scatter(
                x=[src_pos[0], tgt_pos[0]],
                y=[src_pos[1], tgt_pos[1]],
                mode="lines",
                line=dict(color=line_color, width=2),
                hoverinfo="text",
                hovertext=f"Latency: {edge.get('latency', 0):.1f}ms",
                showlegend=False,
            ))

    # Draw nodes
    node_colors = []
    node_text = []
    for node in nodes:
        health = node.get("health", 0.5)
        if health > 0.8:
            node_colors.append("#10b981")  # Green
        elif health > 0.5:
            node_colors.append("#f59e0b")  # Yellow
        else:
            node_colors.append("#ef4444")  # Red

        node_text.append(
            f"<b>{node['name']}</b><br>"
            f"Status: {node['status']}<br>"
            f"Health: {health:.0%}<br>"
            f"Region: {node.get('region', 'N/A')}"
        )

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        marker=dict(
            size=30,
            color=node_colors,
            line=dict(width=2, color="white"),
        ),
        text=[n["name"].replace("Node ", "N") for n in nodes],
        textposition="middle center",
        textfont=dict(color="white", size=10),
        hoverinfo="text",
        hovertext=node_text,
        showlegend=False,
    ))

    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False, range=[-1.5, 1.5]),
        yaxis=dict(visible=False, range=[-1.5, 1.5], scaleanchor="x"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=180,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def render_dashboard():
    """Render the main dashboard page."""
    st.title("TARA Dashboard")
    st.caption("*Telemetry Analysis & Response Automation*")

    # Real-time Signal Monitor at top
    st.subheader("Real-time Signal Monitor")

    # Generate sample data if no history
    if not st.session_state.metrics_history["timestamps"]:
        _generate_sample_data()

    # Create real-time plot
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Signal Coherence", "Spike Rate"),
    )

    timestamps = st.session_state.metrics_history["timestamps"]
    coherence = st.session_state.metrics_history["coherence"]
    spike_rate = st.session_state.metrics_history["spike_rate"]

    fig.add_trace(
        go.Scatter(
            x=timestamps, y=coherence,
            mode="lines",
            name="Coherence",
            line=dict(color="#00CC96", width=2),
            fill="tozeroy",
            fillcolor="rgba(0, 204, 150, 0.1)",
        ),
        row=1, col=1,
    )

    # Add threshold line
    fig.add_hline(
        y=0.5, line_dash="dash", line_color="red",
        annotation_text="Threshold",
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=timestamps, y=spike_rate,
            mode="lines",
            name="Spike Rate",
            line=dict(color="#636EFA", width=2),
        ),
        row=2, col=1,
    )

    fig.update_layout(
        height=350,
        showlegend=False,
        margin=dict(l=50, r=20, t=40, b=20),
    )
    fig.update_yaxes(title_text="Cs", row=1, col=1)
    fig.update_yaxes(title_text="Hz", row=2, col=1)

    # Interactive chart with click to expand
    with st.expander("Click to expand signal details", expanded=True):
        st.plotly_chart(fig, width="stretch")

        # Detailed metrics when expanded
        detail_cols = st.columns(4)
        with detail_cols[0]:
            current_coherence = coherence[-1] if coherence else 0.85
            st.metric("Current Coherence", f"{current_coherence:.3f}")
        with detail_cols[1]:
            avg_coherence = np.mean(coherence) if coherence else 0.85
            st.metric("Avg Coherence", f"{avg_coherence:.3f}")
        with detail_cols[2]:
            current_spike = spike_rate[-1] if spike_rate else 50
            st.metric("Current Spike Rate", f"{current_spike:.1f} Hz")
        with detail_cols[3]:
            avg_spike = np.mean(spike_rate) if spike_rate else 50
            st.metric("Avg Spike Rate", f"{avg_spike:.1f} Hz")

    st.divider()

    # System Status row
    st.subheader("System Status")
    status_cols = st.columns(5)

    with status_cols[0]:
        status = "🟢 Online" if st.session_state.monitor_running else "⚪ Idle"
        st.metric("Monitor", status)

    with status_cols[1]:
        alert_count = len([a for a in st.session_state.alerts if a.get("active", True)])
        st.metric("Active Alerts", alert_count)

    with status_cols[2]:
        if VISUALIZATION_AVAILABLE and st.session_state.bci_network:
            network = st.session_state.bci_network
            st.metric("BCI Nodes", f"{network.online_nodes}/{network.total_nodes}")
        else:
            st.metric("BCI Nodes", "N/A")

    with status_cols[3]:
        if VISUALIZATION_AVAILABLE and st.session_state.bci_network:
            health_pct = st.session_state.bci_network.network_health * 100
            st.metric("Network Health", f"{health_pct:.0f}%")
        else:
            st.metric("Network Health", "N/A")

    with status_cols[4]:
        if VISUALIZATION_AVAILABLE and st.session_state.neural_firewall:
            fw = st.session_state.neural_firewall
            pass_rate = (fw.total_passed / fw.total_signals * 100) if fw.total_signals > 0 else 100
            st.metric("Firewall Pass Rate", f"{pass_rate:.0f}%")
        else:
            st.metric("Firewall Pass Rate", "N/A")

    st.divider()

    # Two column layout: Alerts and BCI Nodes
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Recent Alerts")

        if st.session_state.alerts:
            for alert in st.session_state.alerts[-5:]:
                level = alert.get("level", "INFO")
                label = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(level, "⚪")
                with st.container():
                    st.markdown(f"{label} **{alert.get('title', 'Alert')}**")
                    st.caption(alert.get("description", "")[:100])
                    st.divider()
        else:
            st.info("No recent alerts")

    with col_right:
        st.subheader("BCI Node Network")

        # Node connectivity visualization
        if VISUALIZATION_AVAILABLE and st.session_state.bci_network:
            network = st.session_state.bci_network

            # Create node network visualization
            fig = _create_node_network_viz(network)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

            # Connection status summary
            st.caption("Node Connections (L8 Neural Gateway)")
            seen = set()
            for conn in network.connections:
                edge_key = tuple(sorted([conn.source_node_id, conn.target_node_id]))
                if edge_key in seen:
                    continue
                seen.add(edge_key)
                status_label = "🟢" if conn.is_healthy else "🟡" if conn.status == ConnectionStatus.DEGRADED else "🔴"
                source = conn.source_node_id.replace("node_", "N")
                target = conn.target_node_id.replace("node_", "N")
                st.markdown(f"{status_label} {source} - {target} ({conn.latency_ms:.1f}ms)")

            # Expandable node details
            st.markdown("**Node Details**")
            for node_id, node in network.nodes.items():
                status_label = {
                    NodeStatus.ONLINE: "🟢",
                    NodeStatus.DEGRADED: "🟡",
                    NodeStatus.WARNING: "🟠",
                    NodeStatus.OFFLINE: "🔴",
                    NodeStatus.INITIALIZING: "⚪",
                }.get(node.status, "⚪")

                with st.expander(f"{status_label} {node.name} - {node.brain_region or 'Unassigned'}", expanded=False):
                    detail_cols = st.columns(2)
                    with detail_cols[0]:
                        st.markdown(f"**Status:** {node.status.value.title()}")
                        st.markdown(f"**Health:** {node.health_score:.0%}")
                        st.markdown(f"**Region:** {node.brain_region or 'Unassigned'}")
                    with detail_cols[1]:
                        st.markdown(f"**Processed:** {node.metrics.signals_processed:,}")
                        st.markdown(f"**Pass Rate:** {node.metrics.pass_rate:.1f}%")
                        st.markdown(f"**Coherence:** {node.metrics.avg_coherence:.2f}")

                    # Show connections
                    connections = network.get_connections(node_id)
                    if connections:
                        connected_to = set()
                        for conn in connections:
                            other = conn.target_node_id if conn.source_node_id == node_id else conn.source_node_id
                            connected_to.add(other)
                        st.caption(f"Connected to: {', '.join(n.replace('node_', 'Node ') for n in connected_to)}")
        else:
            st.info("No BCI nodes configured")


# Region security data: functions, attack vectors, defenses mapped to ONI
REGION_SECURITY_DATA = {
    "M1": {
        "name": "Primary Motor Cortex",
        "function": "Executes voluntary movements by sending motor commands to muscles",
        "oni_layer": 13,
        "oni_name": "Presentation",
        "neuron_types": ["Pyramidal", "Interneurons", "Betz Cells"],
        "connections": ["PMC", "SMA", "S1", "Thalamus"],
        "attack_vectors": [
            {"name": "Motor Hijacking", "severity": "CRITICAL", "description": "Unauthorized motor command injection causing involuntary movements"},
            {"name": "Tremor Induction", "severity": "HIGH", "description": "Oscillatory signal injection causing tremors"},
            {"name": "Motor Lockout", "severity": "CRITICAL", "description": "Signal suppression causing temporary paralysis"},
        ],
        "defenses": [
            {"name": "Intent Verification", "layer": "L13", "description": "Validates motor commands match decoded intent"},
            {"name": "Rate Limiting", "layer": "L11", "description": "Prevents rapid unauthorized command sequences"},
            {"name": "Coherence Check", "layer": "L8", "description": "Ensures signal coherence matches biological patterns"},
        ],
    },
    "S1": {
        "name": "Primary Somatosensory Cortex",
        "function": "Processes tactile information, proprioception, and body awareness",
        "oni_layer": 12,
        "oni_name": "Session",
        "neuron_types": ["Pyramidal", "Stellate", "Interneurons"],
        "connections": ["M1", "PFC", "Thalamus"],
        "attack_vectors": [
            {"name": "Phantom Sensation", "severity": "MEDIUM", "description": "Injection of false tactile signals"},
            {"name": "Pain Amplification", "severity": "HIGH", "description": "Amplifying pain pathway signals"},
            {"name": "Proprioceptive Confusion", "severity": "HIGH", "description": "Distorting body position awareness"},
        ],
        "defenses": [
            {"name": "Session Validation", "layer": "L12", "description": "Validates sensory session integrity"},
            {"name": "Amplitude Bounds", "layer": "L9", "description": "Hardware limits on signal amplitude"},
            {"name": "Cross-Modal Check", "layer": "L5", "description": "Verifies sensory consistency across modalities"},
        ],
    },
    "PMC": {
        "name": "Premotor Cortex",
        "function": "Plans and prepares movements before execution",
        "oni_layer": 13,
        "oni_name": "Presentation",
        "neuron_types": ["Pyramidal", "Mirror Neurons", "Interneurons"],
        "connections": ["M1", "SMA", "PFC", "Parietal"],
        "attack_vectors": [
            {"name": "Movement Planning Corruption", "severity": "HIGH", "description": "Altering planned movement sequences"},
            {"name": "Mirror Neuron Exploitation", "severity": "MEDIUM", "description": "Triggering unintended imitative actions"},
            {"name": "Preparation Delay", "severity": "MEDIUM", "description": "Disrupting movement timing preparation"},
        ],
        "defenses": [
            {"name": "Sequence Validation", "layer": "L13", "description": "Validates movement sequence integrity"},
            {"name": "Temporal Consistency", "layer": "L12", "description": "Ensures timing matches expected patterns"},
            {"name": "Intent Correlation", "layer": "L14", "description": "Correlates plans with higher-level intent"},
        ],
    },
    "SMA": {
        "name": "Supplementary Motor Area",
        "function": "Coordinates complex movement sequences and bilateral coordination",
        "oni_layer": 13,
        "oni_name": "Presentation",
        "neuron_types": ["Pyramidal", "Interneurons"],
        "connections": ["M1", "PMC", "PFC", "Basal Ganglia"],
        "attack_vectors": [
            {"name": "Sequence Disruption", "severity": "HIGH", "description": "Breaking coordinated movement sequences"},
            {"name": "Bilateral Desync", "severity": "MEDIUM", "description": "Disrupting left-right coordination"},
            {"name": "Initiation Block", "severity": "HIGH", "description": "Preventing voluntary movement initiation"},
        ],
        "defenses": [
            {"name": "Bilateral Sync Monitor", "layer": "L13", "description": "Monitors bilateral coordination integrity"},
            {"name": "Sequence Checksum", "layer": "L10", "description": "Validates movement sequence checksums"},
            {"name": "Initiation Authentication", "layer": "L14", "description": "Authenticates movement initiation signals"},
        ],
    },
    "PFC": {
        "name": "Prefrontal Cortex",
        "function": "Executive function, decision-making, personality, and social behavior",
        "oni_layer": 14,
        "oni_name": "Application",
        "neuron_types": ["Pyramidal", "Interneurons", "VEN Neurons"],
        "connections": ["All cortical regions", "Limbic System", "Thalamus"],
        "attack_vectors": [
            {"name": "Decision Manipulation", "severity": "CRITICAL", "description": "Influencing decision-making processes"},
            {"name": "Impulse Injection", "severity": "HIGH", "description": "Triggering impulsive behaviors"},
            {"name": "Cognitive Fog", "severity": "MEDIUM", "description": "Disrupting executive function clarity"},
            {"name": "Identity Erosion", "severity": "CRITICAL", "description": "Long-term personality alteration"},
        ],
        "defenses": [
            {"name": "Identity Anchor", "layer": "L14", "description": "Maintains core identity pattern baseline"},
            {"name": "Decision Audit", "layer": "L14", "description": "Logs and validates decision patterns"},
            {"name": "Cognitive Integrity", "layer": "L6", "description": "Monitors whole-brain cognitive coherence"},
            {"name": "Ethics Filter", "layer": "L14", "description": "Screens for ethically anomalous patterns"},
        ],
    },
    "BROCA": {
        "name": "Broca's Area",
        "function": "Speech production and language processing",
        "oni_layer": 14,
        "oni_name": "Application",
        "neuron_types": ["Pyramidal", "Interneurons"],
        "connections": ["WERNICKE", "M1", "PFC", "Auditory"],
        "attack_vectors": [
            {"name": "Speech Hijacking", "severity": "CRITICAL", "description": "Forcing unintended speech production"},
            {"name": "Aphasia Induction", "severity": "HIGH", "description": "Disrupting speech production capability"},
            {"name": "Word Substitution", "severity": "MEDIUM", "description": "Replacing intended words during speech"},
        ],
        "defenses": [
            {"name": "Speech Intent Verify", "layer": "L14", "description": "Verifies speech matches intended communication"},
            {"name": "Language Pattern Auth", "layer": "L13", "description": "Authenticates language production patterns"},
            {"name": "Articulation Monitor", "layer": "L7", "description": "Monitors motor output for speech"},
        ],
    },
    "WERNICKE": {
        "name": "Wernicke's Area",
        "function": "Language comprehension and semantic processing",
        "oni_layer": 14,
        "oni_name": "Application",
        "neuron_types": ["Pyramidal", "Interneurons"],
        "connections": ["BROCA", "Auditory Cortex", "PFC", "Angular Gyrus"],
        "attack_vectors": [
            {"name": "Comprehension Scramble", "severity": "HIGH", "description": "Disrupting language understanding"},
            {"name": "Semantic Injection", "severity": "MEDIUM", "description": "Inserting false semantic associations"},
            {"name": "Meaning Distortion", "severity": "HIGH", "description": "Altering perceived meaning of input"},
        ],
        "defenses": [
            {"name": "Semantic Validation", "layer": "L14", "description": "Validates semantic processing integrity"},
            {"name": "Context Consistency", "layer": "L12", "description": "Ensures contextual understanding consistency"},
            {"name": "Cross-Reference Check", "layer": "L5", "description": "Cross-references with memory systems"},
        ],
    },
    "V1": {
        "name": "Primary Visual Cortex",
        "function": "Initial visual processing of shapes, colors, and motion",
        "oni_layer": 12,
        "oni_name": "Session",
        "neuron_types": ["Simple Cells", "Complex Cells", "Hypercomplex"],
        "connections": ["LGN", "V2", "V4", "MT"],
        "attack_vectors": [
            {"name": "Visual Hallucination", "severity": "HIGH", "description": "Injecting false visual percepts"},
            {"name": "Blindspot Creation", "severity": "MEDIUM", "description": "Suppressing visual field regions"},
            {"name": "Motion Sickness", "severity": "LOW", "description": "Inducing vestibular-visual mismatch"},
        ],
        "defenses": [
            {"name": "Visual Consistency", "layer": "L12", "description": "Validates visual stream consistency"},
            {"name": "Retinotopic Mapping", "layer": "L9", "description": "Verifies proper spatial mapping"},
            {"name": "Multi-Sensory Cross-Check", "layer": "L5", "description": "Cross-validates with other senses"},
        ],
    },
    "A1": {
        "name": "Primary Auditory Cortex",
        "function": "Initial auditory processing of sounds and frequencies",
        "oni_layer": 12,
        "oni_name": "Session",
        "neuron_types": ["Pyramidal", "Stellate", "Interneurons"],
        "connections": ["MGN", "A2", "WERNICKE", "Limbic"],
        "attack_vectors": [
            {"name": "Auditory Hallucination", "severity": "HIGH", "description": "Injecting phantom sounds or voices"},
            {"name": "Tinnitus Induction", "severity": "MEDIUM", "description": "Creating persistent phantom tones"},
            {"name": "Speech Masking", "severity": "MEDIUM", "description": "Obscuring speech comprehension"},
        ],
        "defenses": [
            {"name": "Tonotopic Validation", "layer": "L12", "description": "Validates frequency mapping integrity"},
            {"name": "Temporal Pattern Check", "layer": "L9", "description": "Verifies temporal signal patterns"},
            {"name": "Source Localization", "layer": "L5", "description": "Validates sound source consistency"},
        ],
    },
    "HIPP": {
        "name": "Hippocampus",
        "function": "Memory formation, spatial navigation, and contextual learning",
        "oni_layer": 11,
        "oni_name": "Transport",
        "neuron_types": ["Pyramidal", "Granule Cells", "Place Cells", "Grid Cells"],
        "connections": ["Entorhinal Cortex", "PFC", "Amygdala", "Thalamus"],
        "attack_vectors": [
            {"name": "False Memory Implant", "severity": "CRITICAL", "description": "Creating fabricated memory traces"},
            {"name": "Memory Erasure", "severity": "CRITICAL", "description": "Disrupting memory consolidation"},
            {"name": "Spatial Disorientation", "severity": "HIGH", "description": "Corrupting spatial navigation maps"},
            {"name": "Context Confusion", "severity": "MEDIUM", "description": "Mixing contextual memory associations"},
        ],
        "defenses": [
            {"name": "Memory Encryption", "layer": "L11", "description": "Encrypts memory trace formation"},
            {"name": "Consolidation Checksum", "layer": "L10", "description": "Validates memory consolidation integrity"},
            {"name": "Spatial Calibration", "layer": "L12", "description": "Maintains spatial reference frames"},
            {"name": "Context Tagging", "layer": "L11", "description": "Authenticates contextual associations"},
        ],
    },
}


def _create_brain_3d_with_regions() -> go.Figure:
    """Create a 3D brain visualization with region spheres and connections."""
    fig = go.Figure()

    # Brain mesh (ellipsoid approximation)
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 20)
    x_brain = 85 * np.outer(np.cos(u), np.sin(v))
    y_brain = 70 * np.outer(np.sin(u), np.sin(v))
    z_brain = 70 * np.outer(np.ones(np.size(u)), np.cos(v))

    fig.add_trace(go.Surface(
        x=x_brain, y=y_brain, z=z_brain,
        opacity=0.1,
        colorscale=[[0, 'rgb(200,200,200)'], [1, 'rgb(200,200,200)']],
        showscale=False,
        name="Brain",
        hoverinfo="skip",
    ))

    # Region positions (approximate MNI coordinates)
    region_positions = {
        "M1": (-35, -20, 55),
        "S1": (-35, -35, 50),
        "PMC": (-45, 5, 50),
        "SMA": (0, -5, 60),
        "PFC": (35, 45, 25),
        "BROCA": (-50, 20, 15),
        "WERNICKE": (-55, -55, 20),
        "V1": (0, -85, 5),
        "A1": (-55, -20, 10),
        "HIPP": (-25, -20, -15),
    }

    # ONI layer colors
    layer_colors = {
        11: "#22c55e",  # Transport - Green
        12: "#3b82f6",  # Session - Blue
        13: "#f97316",  # Presentation - Orange
        14: "#8b5cf6",  # Application - Purple
    }

    # Draw region spheres
    region_x, region_y, region_z = [], [], []
    region_colors, region_text, region_names = [], [], []

    for abbr, data in REGION_SECURITY_DATA.items():
        pos = region_positions.get(abbr, (0, 0, 0))
        region_x.append(pos[0])
        region_y.append(pos[1])
        region_z.append(pos[2])
        region_colors.append(layer_colors.get(data["oni_layer"], "#888888"))
        region_names.append(abbr)

        attacks = len(data["attack_vectors"])
        defenses = len(data["defenses"])
        region_text.append(
            f"<b>{abbr}: {data['name']}</b><br>"
            f"<i>{data['function'][:60]}...</i><br>"
            f"ONI Layer: L{data['oni_layer']} ({data['oni_name']})<br>"
            f"Attack Vectors: {attacks}<br>"
            f"Defenses: {defenses}"
        )

    fig.add_trace(go.Scatter3d(
        x=region_x, y=region_y, z=region_z,
        mode="markers+text",
        marker=dict(
            size=15,
            color=region_colors,
            opacity=0.9,
            line=dict(width=2, color="white"),
        ),
        text=region_names,
        textposition="top center",
        textfont=dict(size=10, color="white"),
        hoverinfo="text",
        hovertext=region_text,
        name="Brain Regions",
    ))

    # Draw connections between regions
    connection_pairs = [
        ("M1", "S1"), ("M1", "PMC"), ("M1", "SMA"),
        ("PMC", "SMA"), ("PMC", "PFC"),
        ("PFC", "BROCA"), ("PFC", "HIPP"),
        ("BROCA", "WERNICKE"), ("BROCA", "A1"),
        ("WERNICKE", "A1"),
        ("S1", "PFC"),
        ("V1", "PFC"),
    ]

    for src, tgt in connection_pairs:
        if src in region_positions and tgt in region_positions:
            src_pos = region_positions[src]
            tgt_pos = region_positions[tgt]
            fig.add_trace(go.Scatter3d(
                x=[src_pos[0], tgt_pos[0]],
                y=[src_pos[1], tgt_pos[1]],
                z=[src_pos[2], tgt_pos[2]],
                mode="lines",
                line=dict(color="rgba(100,100,255,0.4)", width=2),
                hoverinfo="skip",
                showlegend=False,
            ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-100, 100]),
            yaxis=dict(visible=False, range=[-100, 100]),
            zaxis=dict(visible=False, range=[-80, 80]),
            aspectmode="data",
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )

    return fig


def _create_neuron_network_viz(region: str, n_neurons: int = 30) -> go.Figure:
    """Create a visualization of neurons and connections within a region."""
    np.random.seed(hash(region) % 2**32)

    # Generate neuron positions in a sphere
    theta = np.random.uniform(0, 2*np.pi, n_neurons)
    phi = np.random.uniform(0, np.pi, n_neurons)
    r = np.random.uniform(0.3, 1.0, n_neurons)

    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)

    # Neuron types for coloring
    region_data = REGION_SECURITY_DATA.get(region, {})
    neuron_types = region_data.get("neuron_types", ["Pyramidal", "Interneuron"])
    colors = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b"][:len(neuron_types)]
    neuron_colors = [colors[i % len(colors)] for i in range(n_neurons)]

    fig = go.Figure()

    # Draw connections (random subset)
    n_connections = n_neurons * 3
    for _ in range(n_connections):
        i, j = np.random.choice(n_neurons, 2, replace=False)
        # Excitatory (blue) or inhibitory (red)
        is_excitatory = np.random.random() > 0.2
        line_color = "rgba(59,130,246,0.2)" if is_excitatory else "rgba(239,68,68,0.2)"
        fig.add_trace(go.Scatter3d(
            x=[x[i], x[j]], y=[y[i], y[j]], z=[z[i], z[j]],
            mode="lines",
            line=dict(color=line_color, width=1),
            hoverinfo="skip",
            showlegend=False,
        ))

    # Draw neurons
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode="markers",
        marker=dict(
            size=6,
            color=neuron_colors,
            opacity=0.9,
            line=dict(width=1, color="white"),
        ),
        hoverinfo="text",
        hovertext=[f"Neuron {i+1}<br>Type: {neuron_types[i % len(neuron_types)]}" for i in range(n_neurons)],
        name="Neurons",
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="cube",
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )

    return fig


def render_neural_simulator_page():
    """Render the Neural Simulator page with brain regions, attacks, and defenses."""
    st.title("Neural Simulator")
    st.markdown("*Interactive Brain Region Security Analysis - ONI Framework Mapped*")

    # Initialize session state for selected region
    if "selected_sim_region" not in st.session_state:
        st.session_state.selected_sim_region = "M1"

    # Main layout
    col_brain, col_details = st.columns([3, 2])

    with col_brain:
        st.subheader("Brain Regions (ONI Layer Mapped)")

        # 3D Brain visualization
        brain_fig = _create_brain_3d_with_regions()
        st.plotly_chart(brain_fig, width="stretch", config={"displayModeBar": False})

        # Region selector
        regions = list(REGION_SECURITY_DATA.keys())
        selected = st.selectbox(
            "Select Region to Analyze",
            regions,
            index=regions.index(st.session_state.selected_sim_region),
            format_func=lambda x: f"{x} - {REGION_SECURITY_DATA[x]['name']}",
        )
        if selected != st.session_state.selected_sim_region:
            st.session_state.selected_sim_region = selected
            st.rerun()

        # Legend
        st.markdown("**ONI Layer Legend:**")
        legend_cols = st.columns(4)
        with legend_cols[0]:
            st.markdown("🟢 **L11** Transport")
        with legend_cols[1]:
            st.markdown("🔵 **L12** Session")
        with legend_cols[2]:
            st.markdown("🟠 **L13** Presentation")
        with legend_cols[3]:
            st.markdown("🟣 **L14** Application")

    with col_details:
        region = st.session_state.selected_sim_region
        data = REGION_SECURITY_DATA.get(region, {})

        # Region header
        st.subheader(f"{region}: {data.get('name', 'Unknown')}")
        st.markdown(f"*{data.get('function', 'No description')}*")

        # ONI mapping
        oni_layer = data.get("oni_layer", 0)
        oni_name = data.get("oni_name", "Unknown")
        layer_color = {"Transport": "green", "Session": "blue", "Presentation": "orange", "Application": "purple"}.get(oni_name, "gray")
        st.markdown(f"**ONI Layer:** L{oni_layer} ({oni_name}) :{layer_color}_circle:")

        # Neuron types
        st.markdown("**Neuron Types:**")
        for nt in data.get("neuron_types", []):
            st.markdown(f"- {nt}")

        # Connections
        st.markdown("**Connections:**")
        st.markdown(", ".join(data.get("connections", [])))

    st.divider()

    # Neuron Network and Attack/Defense panels
    col_network, col_security = st.columns([1, 1])

    with col_network:
        st.subheader("Neural Network Visualization")
        region = st.session_state.selected_sim_region

        n_neurons = st.slider("Neuron Count", 20, 100, 40, key="neuron_count")
        neuron_fig = _create_neuron_network_viz(region, n_neurons)
        st.plotly_chart(neuron_fig, width="stretch", config={"displayModeBar": False})

        data = REGION_SECURITY_DATA.get(region, {})
        st.caption(f"Showing simulated {', '.join(data.get('neuron_types', ['neurons']))[:50]}...")

    with col_security:
        st.subheader("Security Analysis")

        security_tab1, security_tab2 = st.tabs(["Attack Vectors", "Defenses"])

        region = st.session_state.selected_sim_region
        data = REGION_SECURITY_DATA.get(region, {})

        with security_tab1:
            attacks = data.get("attack_vectors", [])
            if attacks:
                for attack in attacks:
                    severity = attack.get("severity", "UNKNOWN")
                    severity_color = {
                        "CRITICAL": "🔴",
                        "HIGH": "🟠",
                        "MEDIUM": "🟡",
                        "LOW": "🟢",
                    }.get(severity, "⚪")

                    with st.expander(f"{severity_color} {attack['name']} ({severity})", expanded=False):
                        st.markdown(attack.get("description", "No description"))
                        st.markdown(f"**Target:** {region} ({data.get('name', '')})")
                        st.markdown(f"**ONI Layer:** L{data.get('oni_layer', '?')}")
            else:
                st.info("No attack vectors defined")

        with security_tab2:
            defenses = data.get("defenses", [])
            if defenses:
                for defense in defenses:
                    layer = defense.get("layer", "L?")
                    with st.expander(f"🛡️ {defense['name']} ({layer})", expanded=False):
                        st.markdown(defense.get("description", "No description"))
                        st.markdown(f"**Protection Layer:** {layer}")
            else:
                st.info("No defenses defined")

    st.divider()

    # ONI Layer Stack visualization
    st.subheader("ONI Framework Layer Stack")

    # Create layer stack visualization
    layers_data = [
        {"layer": "L14", "name": "Identity", "domain": "Biology", "regions": ["PFC", "BROCA", "WERNICKE"], "color": "#8b5cf6"},
        {"layer": "L13", "name": "Semantic", "domain": "Biology", "regions": ["M1", "PMC", "SMA"], "color": "#f97316"},
        {"layer": "L12", "name": "Cognitive Session", "domain": "Biology", "regions": ["S1", "V1", "A1"], "color": "#3b82f6"},
        {"layer": "L11", "name": "Cognitive Transport", "domain": "Biology", "regions": ["HIPP"], "color": "#22c55e"},
        {"layer": "L10", "name": "Neural Protocol", "domain": "Biology", "regions": [], "color": "#06b6d4"},
        {"layer": "L9", "name": "Signal Processing", "domain": "Biology", "regions": [], "color": "#14b8a6"},
        {"layer": "L8", "name": "Neural Gateway", "domain": "Bridge", "regions": ["FIREWALL"], "color": "#ec4899"},
        {"layer": "L7", "name": "Application", "domain": "Silicon", "regions": [], "color": "#64748b"},
        {"layer": "L6", "name": "Presentation", "domain": "Silicon", "regions": [], "color": "#64748b"},
        {"layer": "L5", "name": "Session", "domain": "Silicon", "regions": [], "color": "#64748b"},
    ]

    # Highlight current region's layer
    current_region = st.session_state.selected_sim_region
    current_layer = REGION_SECURITY_DATA.get(current_region, {}).get("oni_layer", 0)

    layer_cols = st.columns(len(layers_data))
    for i, layer in enumerate(layers_data):
        with layer_cols[i]:
            is_current = int(layer["layer"][1:]) == current_layer
            border = "3px solid white" if is_current else "1px solid gray"
            regions_str = ", ".join(layer["regions"]) if layer["regions"] else "-"

            st.markdown(
                f"""<div style="background-color:{layer['color']}; padding:10px; border-radius:5px;
                border:{border}; text-align:center; min-height:120px;">
                <b>{layer['layer']}</b><br>
                <small>{layer['name']}</small><br>
                <small style="color:#ddd">{layer['domain']}</small><br>
                <small>{regions_str}</small>
                </div>""",
                unsafe_allow_html=True,
            )

    st.caption("*L8 (Neural Gateway) is the critical firewall boundary between biological (L1-L7) and silicon (L9-L14) domains*")


# Neural ATT&CK Matrix - MITRE-style tactics and techniques for BCI
NEURAL_ATTACK_MATRIX = {
    "Reconnaissance": {
        "color": "#6366f1",
        "oni_layers": ["L7", "L8"],
        "techniques": [
            {"id": "RECON-01", "name": "Signal Profiling", "description": "Passive monitoring of neural signal patterns"},
            {"id": "RECON-02", "name": "Side-Channel Analysis", "description": "Extracting info from power/timing signatures"},
            {"id": "RECON-03", "name": "Network Mapping", "description": "Discovering BCI node topology"},
        ],
    },
    "Initial Access": {
        "color": "#8b5cf6",
        "oni_layers": ["L8", "L9"],
        "techniques": [
            {"id": "ACCESS-01", "name": "Electrode Compromise", "description": "Physical access to neural electrodes"},
            {"id": "ACCESS-02", "name": "RF Exploitation", "description": "Exploiting wireless BCI protocols"},
            {"id": "ACCESS-03", "name": "Firmware Backdoor", "description": "Compromising BCI firmware update"},
        ],
    },
    "Execution": {
        "color": "#ec4899",
        "oni_layers": ["L9", "L10", "L11"],
        "techniques": [
            {"id": "EXEC-01", "name": "Signal Injection", "description": "Injecting crafted neural signals"},
            {"id": "EXEC-02", "name": "Protocol Manipulation", "description": "Exploiting neural protocol weaknesses"},
            {"id": "EXEC-03", "name": "Command Hijacking", "description": "Intercepting motor commands"},
        ],
    },
    "Persistence": {
        "color": "#f59e0b",
        "oni_layers": ["L10", "L11"],
        "techniques": [
            {"id": "PERSIST-01", "name": "Pattern Lock", "description": "Embedding recurring attack patterns"},
            {"id": "PERSIST-02", "name": "Memory Implant", "description": "Persistent neural pathway modification"},
        ],
    },
    "Defense Evasion": {
        "color": "#10b981",
        "oni_layers": ["L8", "L9"],
        "techniques": [
            {"id": "EVADE-01", "name": "Coherence Mimicry", "description": "Matching legitimate signal coherence"},
            {"id": "EVADE-02", "name": "Gradual Drift", "description": "Slow parameter changes below threshold"},
        ],
    },
    "Collection": {
        "color": "#3b82f6",
        "oni_layers": ["L12", "L13", "L14"],
        "techniques": [
            {"id": "COLLECT-01", "name": "ERP Harvesting", "description": "Extracting event-related potentials"},
            {"id": "COLLECT-02", "name": "Cognitive Capture", "description": "Recording cognitive state patterns"},
            {"id": "COLLECT-03", "name": "Memory Extraction", "description": "Reading memory-related signals"},
        ],
    },
    "Impact": {
        "color": "#ef4444",
        "oni_layers": ["L11", "L12", "L13", "L14"],
        "techniques": [
            {"id": "IMPACT-01", "name": "Neural DoS", "description": "Overwhelming neural pathways"},
            {"id": "IMPACT-02", "name": "Motor Hijacking", "description": "Forcing involuntary movements"},
            {"id": "IMPACT-03", "name": "Identity Erosion", "description": "Long-term personality alteration"},
        ],
    },
}


def render_attack_simulator_page():
    """Render the Attack Simulator page with Neural ATT&CK matrix and pew-pew animation."""
    st.title("Attack Simulator")
    st.markdown("*MITRE ATT&CK-style Neural Security Testing*")

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Neural ATT&CK Matrix", "Attack Simulation", "Pew-Pew Visualization"])

    with tab1:
        _render_neural_attack_matrix()

    with tab2:
        _render_attack_simulation_panel()

    with tab3:
        _render_pew_pew_animation()


def _render_neural_attack_matrix():
    """Render the Neural ATT&CK matrix in MITRE style."""
    st.subheader("Neural ATT&CK Matrix")
    st.markdown("*10 Tactics | 46 Techniques | Mapped to ONI Layers*")

    # Matrix header
    tactics = list(NEURAL_ATTACK_MATRIX.keys())
    cols = st.columns(len(tactics))

    # Render tactic headers
    for i, (tactic, data) in enumerate(NEURAL_ATTACK_MATRIX.items()):
        with cols[i]:
            st.markdown(
                f"""<div style="background-color:{data['color']}; padding:10px; border-radius:5px;
                text-align:center; margin-bottom:5px;">
                <b style="color:white;">{tactic}</b><br>
                <small style="color:white;">{', '.join(data['oni_layers'])}</small>
                </div>""",
                unsafe_allow_html=True,
            )

    # Render techniques
    max_techniques = max(len(data["techniques"]) for data in NEURAL_ATTACK_MATRIX.values())

    for row in range(max_techniques):
        cols = st.columns(len(tactics))
        for i, (tactic, data) in enumerate(NEURAL_ATTACK_MATRIX.items()):
            with cols[i]:
                if row < len(data["techniques"]):
                    tech = data["techniques"][row]
                    with st.expander(tech["name"], expanded=False):
                        st.markdown(f"**ID:** {tech['id']}")
                        st.markdown(f"**Description:** {tech['description']}")
                        st.markdown(f"**Target Layers:** {', '.join(data['oni_layers'])}")

                        if st.button(f"Simulate", key=f"sim_{tech['id']}"):
                            st.session_state.selected_technique = tech
                            st.session_state.current_page = "Attack Simulator"
                            st.rerun()

    st.divider()

    # Legend
    st.markdown("### ONI Layer Mapping")
    layer_info = {
        "L7": ("Application Interface", "🔵"),
        "L8": ("Neural Gateway", "🟣"),
        "L9": ("Signal Processing", "🟢"),
        "L10": ("Neural Protocol", "🟡"),
        "L11": ("Cognitive Transport", "🟠"),
        "L12": ("Cognitive Session", "🔴"),
        "L13": ("Semantic", "⭕"),
        "L14": ("Identity & Ethics", "⚫"),
    }

    legend_cols = st.columns(4)
    for i, (layer, (name, icon)) in enumerate(layer_info.items()):
        with legend_cols[i % 4]:
            st.markdown(f"{icon} **{layer}**: {name}")


def _render_attack_simulation_panel():
    """Render the attack simulation configuration and results panel."""
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Attack Configuration")

        # If technique was selected from matrix
        if "selected_technique" in st.session_state and st.session_state.selected_technique:
            tech = st.session_state.selected_technique
            st.info(f"Selected: {tech['name']} ({tech['id']})")

        attack_type = st.selectbox(
            "Attack Scenario",
            [
                "Neural Ransomware Campaign",
                "Gateway Infiltration",
                "Denial of Service",
                "Man-in-the-Middle",
                "Stealth Reconnaissance",
            ],
        )

        target_layer = st.selectbox(
            "Target Layer",
            ["L8 - Neural Gateway", "L9 - Signal Processing", "L10 - Protocol",
             "L11 - Transport", "L12 - Session", "L13 - Semantic", "L14 - Identity"],
        )

        intensity = st.slider("Attack Intensity", 0.0, 1.0, 0.7, step=0.1)

        duration = st.number_input("Attack Duration (ms)", 500, 10000, 2000, step=500)

        st.divider()

        if st.button("Launch Attack", type="primary", width="stretch"):
            # Set animation state
            st.session_state.attack_animation_state = {
                "attack_type": attack_type,
                "target_layer": target_layer,
                "intensity": intensity,
                "duration": duration,
                "phase": "launching",
                "frame": 0,
            }
            _run_attack_simulation(attack_type, target_layer, intensity, duration)

        st.warning("Controlled simulation for security testing only.")

    with col2:
        st.subheader("Attack Results")

        if st.session_state.attack_results:
            results = st.session_state.attack_results

            # Status indicator
            if results["blocked"]:
                st.success("Attack BLOCKED by Neural Firewall (L8)")
            elif results["detected"]:
                st.warning("Attack DETECTED but not fully blocked")
            else:
                st.error("Attack UNDETECTED - Security Gap Found")

            # Timeline visualization
            st.markdown("### Attack Timeline")

            fig = go.Figure()

            stages = results.get("stages", [])
            for i, stage in enumerate(stages):
                color = "#22c55e" if stage.get("blocked") else "#f59e0b" if stage.get("detected") else "#ef4444"
                fig.add_trace(go.Bar(
                    x=[stage["duration"]],
                    y=[stage["name"]],
                    orientation="h",
                    marker_color=color,
                    text=f"{stage['status']}",
                    textposition="inside",
                    showlegend=False,
                ))

            fig.update_layout(
                title="Attack Stage Timeline",
                xaxis_title="Duration (ms)",
                height=250,
                margin=dict(l=150, r=20, t=50, b=50),
                barmode="stack",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, width="stretch")

            # Metrics
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("Detection Rate", f"{results['detection_rate']:.0%}")
            with col_b:
                st.metric("Block Rate", f"{results['block_rate']:.0%}")
            with col_c:
                st.metric("Response Time", f"{results['response_time']:.0f} ms")
            with col_d:
                st.metric("Impact Score", f"{results['impact']:.1f}/10")

            # Detailed report
            with st.expander("View Full Report"):
                st.text(results.get("report", "No report available"))

            # Export button
            if st.button("Export Report"):
                st.download_button(
                    "Download Report",
                    data=results.get("report", ""),
                    file_name=f"attack_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                )

        else:
            st.info("Configure an attack scenario and launch to see results.")


def _render_pew_pew_animation():
    """Render the pew-pew attack animation visualization."""
    st.subheader("Attack Visualization")
    st.markdown("*Real-time attack packet propagation across ONI layers*")

    # Animation controls
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        animation_speed = st.slider("Animation Speed", 0.1, 2.0, 1.0, 0.1)

    with col2:
        show_shield = st.checkbox("Show L8 Shield", value=True)

    # Create the attack visualization
    if st.session_state.attack_animation_state:
        state = st.session_state.attack_animation_state
        fig = _create_attack_animation_frame(state, show_shield)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

        # Animation info
        st.markdown("### Attack Path")
        st.markdown(f"**Type:** {state.get('attack_type', 'Unknown')}")
        st.markdown(f"**Target:** {state.get('target_layer', 'Unknown')}")
        st.markdown(f"**Intensity:** {state.get('intensity', 0):.0%}")

    else:
        # Show static demo
        st.info("Launch an attack from the 'Attack Simulation' tab to see the animation.")

        # Demo visualization
        fig = _create_demo_attack_viz()
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    st.divider()

    # Legend
    st.markdown("### Legend")
    legend_cols = st.columns(4)
    with legend_cols[0]:
        st.markdown("🔴 **Attack Origin** - External threat source")
    with legend_cols[1]:
        st.markdown("🟣 **L8 Shield** - Neural Gateway firewall")
    with legend_cols[2]:
        st.markdown("🟢 **Clean Signal** - Legitimate neural traffic")
    with legend_cols[3]:
        st.markdown("🟡 **Impact Zone** - Compromised layer")


def _create_attack_animation_frame(state: dict, show_shield: bool = True) -> go.Figure:
    """Create a single frame of the attack animation."""
    fig = go.Figure()

    # ONI Layer positions (vertical stack)
    layers = ["External", "L7", "L8", "L9", "L10", "L11", "L12", "L13", "L14"]
    layer_y = {layer: i for i, layer in enumerate(layers)}
    layer_colors = {
        "External": "#6b7280",
        "L7": "#3b82f6",
        "L8": "#8b5cf6",
        "L9": "#22c55e",
        "L10": "#eab308",
        "L11": "#f97316",
        "L12": "#ef4444",
        "L13": "#ec4899",
        "L14": "#6366f1",
    }

    # Draw layer bars
    for layer in layers:
        fig.add_trace(go.Bar(
            x=[1],
            y=[layer],
            orientation="h",
            marker_color=layer_colors.get(layer, "#888888"),
            opacity=0.3,
            showlegend=False,
            hoverinfo="text",
            hovertext=f"{layer}: {'Neural Gateway (Firewall)' if layer == 'L8' else layer}",
        ))

    # Draw L8 shield effect
    if show_shield:
        fig.add_trace(go.Scatter(
            x=[0.5],
            y=["L8"],
            mode="markers",
            marker=dict(
                size=40,
                color="rgba(139, 92, 246, 0.5)",
                symbol="diamond",
                line=dict(width=3, color="#8b5cf6"),
            ),
            showlegend=False,
            hoverinfo="text",
            hovertext="L8 Neural Gateway Shield",
        ))

    # Draw attack packets based on state
    target_layer = state.get("target_layer", "L8 - Neural Gateway").split(" - ")[0]
    blocked = state.get("blocked", False)

    # Attack origin
    fig.add_trace(go.Scatter(
        x=[0.1],
        y=["External"],
        mode="markers+text",
        marker=dict(size=20, color="#ef4444", symbol="circle"),
        text=["Attack"],
        textposition="middle right",
        showlegend=False,
    ))

    # Attack path line
    path_layers = ["External", "L7", "L8"]
    if not blocked:
        # Attack penetrated further
        target_idx = layers.index(target_layer) if target_layer in layers else 3
        path_layers = layers[:target_idx + 1]

    path_x = [0.2 + i * 0.1 for i in range(len(path_layers))]
    path_y = path_layers

    line_color = "#ef4444" if not blocked else "#22c55e"
    fig.add_trace(go.Scatter(
        x=path_x,
        y=path_y,
        mode="lines+markers",
        line=dict(color=line_color, width=3, dash="dot"),
        marker=dict(size=10, color=line_color),
        showlegend=False,
    ))

    # Impact zone (if attack succeeded)
    if not blocked:
        fig.add_trace(go.Scatter(
            x=[0.8],
            y=[target_layer],
            mode="markers",
            marker=dict(
                size=50,
                color="rgba(239, 68, 68, 0.3)",
                symbol="circle",
                line=dict(width=2, color="#ef4444"),
            ),
            showlegend=False,
            hoverinfo="text",
            hovertext=f"Impact Zone: {target_layer}",
        ))

    # Block indicator
    if blocked:
        fig.add_trace(go.Scatter(
            x=[0.4],
            y=["L8"],
            mode="markers+text",
            marker=dict(size=30, color="#22c55e", symbol="x"),
            text=["BLOCKED"],
            textposition="middle right",
            textfont=dict(color="#22c55e", size=14),
            showlegend=False,
        ))

    fig.update_layout(
        title="Attack Propagation Visualization",
        xaxis=dict(visible=False, range=[0, 1.2]),
        yaxis=dict(categoryorder="array", categoryarray=list(reversed(layers))),
        height=400,
        margin=dict(l=100, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        barmode="overlay",
    )

    return fig


def _create_demo_attack_viz() -> go.Figure:
    """Create a demo attack visualization."""
    fig = go.Figure()

    layers = ["External", "L7", "L8", "L9", "L10", "L11", "L12", "L13", "L14"]

    # Draw layer bars
    for i, layer in enumerate(layers):
        opacity = 0.8 if layer == "L8" else 0.3
        color = "#8b5cf6" if layer == "L8" else "#6b7280"

        fig.add_trace(go.Bar(
            x=[1],
            y=[layer],
            orientation="h",
            marker_color=color,
            opacity=opacity,
            showlegend=False,
        ))

    # L8 Shield
    fig.add_trace(go.Scatter(
        x=[0.5],
        y=["L8"],
        mode="markers+text",
        marker=dict(size=50, color="rgba(139, 92, 246, 0.5)", symbol="diamond"),
        text=["FIREWALL"],
        textfont=dict(color="white"),
        showlegend=False,
    ))

    fig.update_layout(
        title="ONI Layer Stack (Launch attack to animate)",
        xaxis=dict(visible=False, range=[0, 1.2]),
        yaxis=dict(categoryorder="array", categoryarray=list(reversed(layers))),
        height=400,
        margin=dict(l=100, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def _run_attack_simulation(attack_type, target_layer, intensity, duration):
    """Run attack simulation with animated visualization."""
    with st.spinner("Running attack simulation..."):
        time.sleep(1.5)

        # Generate mock attack results
        detection_prob = 0.7 + (1 - intensity) * 0.3
        detected = np.random.random() < detection_prob
        blocked = detected and np.random.random() < 0.8

        stages = [
            {"name": "Reconnaissance", "duration": 500, "detected": True, "blocked": False, "status": "DETECTED"},
            {"name": "Initial Access", "duration": 800, "detected": detected, "blocked": blocked,
             "status": "BLOCKED" if blocked else ("DETECTED" if detected else "UNDETECTED")},
            {"name": "Execution", "duration": duration - 1300, "detected": detected, "blocked": blocked,
             "status": "BLOCKED" if blocked else ("DETECTED" if detected else "UNDETECTED")},
        ]

        st.session_state.attack_results = {
            "attack_type": attack_type,
            "target_layer": target_layer,
            "intensity": intensity,
            "detected": detected,
            "blocked": blocked,
            "detection_rate": 0.85 if detected else 0.15,
            "block_rate": 0.80 if blocked else 0.0,
            "response_time": np.random.uniform(50, 200),
            "impact": 2.5 if blocked else (5.0 if detected else 8.0),
            "stages": stages,
            "report": _generate_attack_report(attack_type, detected, blocked),
        }

        # Update animation state
        st.session_state.attack_animation_state = {
            "attack_type": attack_type,
            "target_layer": target_layer,
            "intensity": intensity,
            "duration": duration,
            "phase": "complete",
            "blocked": blocked,
            "detected": detected,
        }

        # Add alert
        if detected:
            st.session_state.alerts.append({
                "level": "HIGH" if not blocked else "MEDIUM",
                "title": f"Attack Detected: {attack_type}",
                "description": f"Attack targeting {target_layer} was {'blocked' if blocked else 'detected'}",
                "timestamp": datetime.now().isoformat(),
                "active": True,
            })

    st.success("Attack simulation complete!")
    st.rerun()


def _generate_attack_report(attack_type, detected, blocked):
    """Generate attack simulation report."""
    status = "BLOCKED" if blocked else ("DETECTED" if detected else "UNDETECTED")
    return f"""
{'='*60}
ATTACK SIMULATION REPORT
{'='*60}

Scenario: {attack_type}
Status: {status}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
The simulated attack was {'successfully blocked by the neural firewall' if blocked else
('detected but not fully blocked' if detected else 'not detected - SECURITY GAP')}.

RECOMMENDATIONS
---------------
1. {'Maintain current security posture' if blocked else 'Review detection rules'}
2. {'Continue monitoring' if blocked else 'Update firewall thresholds'}
3. {'Document for compliance' if blocked else 'Investigate detection gaps'}

{'='*60}
"""


def render_nsam_page():
    """Render the Neural Signal Assurance Monitoring page."""
    st.title("Neural Signal Assurance Monitor")

    # Control bar
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        if st.session_state.monitor_running:
            if st.button("Stop Monitoring", type="secondary"):
                st.session_state.monitor_running = False
                st.rerun()
        else:
            if st.button("Start Monitoring", type="primary"):
                st.session_state.monitor_running = True
                st.rerun()

    with col2:
        st.metric("Events", len(st.session_state.events))

    with col3:
        active_alerts = len([a for a in st.session_state.alerts if a.get("active", True)])
        st.metric("Active Alerts", active_alerts)

    with col4:
        st.metric("Status", "ACTIVE" if st.session_state.monitor_running else "IDLE")

    st.divider()

    # Main content
    tab1, tab2, tab3 = st.tabs(["Live Metrics", "Alerts", "Events"])

    with tab1:
        _render_live_metrics()

    with tab2:
        _render_alerts_panel()

    with tab3:
        _render_events_panel()


def _render_live_metrics():
    """Render live metrics visualization."""
    if not st.session_state.metrics_history["timestamps"]:
        _generate_sample_data()

    # Metrics grid
    col1, col2 = st.columns(2)

    with col1:
        # Coherence gauge
        coherence = st.session_state.metrics_history["coherence"]
        current = coherence[-1] if coherence else 0.85

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current,
            title={"text": "Signal Coherence (Cs)"},
            delta={"reference": 0.85},
            gauge={
                "axis": {"range": [0, 1]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 0.3], "color": "red"},
                    {"range": [0.3, 0.5], "color": "orange"},
                    {"range": [0.5, 0.8], "color": "yellow"},
                    {"range": [0.8, 1], "color": "green"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 0.5,
                },
            },
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, width="stretch")

    with col2:
        # Spike rate gauge
        spike_rate = st.session_state.metrics_history["spike_rate"]
        current_spike = spike_rate[-1] if spike_rate else 50

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=current_spike,
            title={"text": "Spike Rate (Hz)"},
            gauge={
                "axis": {"range": [0, 300]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 100], "color": "green"},
                    {"range": [100, 200], "color": "yellow"},
                    {"range": [200, 300], "color": "red"},
                ],
            },
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, width="stretch")

    # Time series
    st.subheader("Metric History")

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=("Coherence", "Spike Rate", "Amplitude"),
    )

    timestamps = st.session_state.metrics_history["timestamps"]

    fig.add_trace(
        go.Scatter(x=timestamps, y=st.session_state.metrics_history["coherence"],
                  mode="lines", name="Coherence", line=dict(color="#00CC96")),
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(x=timestamps, y=st.session_state.metrics_history["spike_rate"],
                  mode="lines", name="Spike Rate", line=dict(color="#636EFA")),
        row=2, col=1,
    )

    fig.add_trace(
        go.Scatter(x=timestamps, y=st.session_state.metrics_history["amplitude"],
                  mode="lines", name="Amplitude", line=dict(color="#EF553B")),
        row=3, col=1,
    )

    fig.update_layout(height=450, showlegend=False, margin=dict(l=50, r=20, t=30, b=20))
    st.plotly_chart(fig, width="stretch")


def _render_alerts_panel():
    """Render alerts management panel."""
    st.subheader("Alert Management")

    # Filter controls
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        level_filter = st.selectbox("Level", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"])
    with col2:
        status_filter = st.selectbox("Status", ["Active", "All", "Resolved"])

    # Alerts list
    alerts = st.session_state.alerts.copy()

    if level_filter != "All":
        alerts = [a for a in alerts if a.get("level") == level_filter]
    if status_filter == "Active":
        alerts = [a for a in alerts if a.get("active", True)]
    elif status_filter == "Resolved":
        alerts = [a for a in alerts if not a.get("active", True)]

    if alerts:
        for i, alert in enumerate(reversed(alerts[-20:])):
            level = alert.get("level", "INFO")
            label = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(level, "⚪")

            with st.expander(f"{label} {alert.get('title', 'Alert')}", expanded=(i == 0)):
                st.markdown(f"**Description:** {alert.get('description', 'N/A')}")
                st.markdown(f"**Timestamp:** {alert.get('timestamp', 'N/A')}")

                col_a, col_b = st.columns(2)
                with col_a:
                    if alert.get("active", True):
                        if st.button("Acknowledge", key=f"ack_{i}"):
                            alert["active"] = False
                            st.rerun()
                with col_b:
                    if st.button("View Details", key=f"details_{i}"):
                        st.json(alert)
    else:
        st.info("No alerts matching the current filter.")

    # Add sample alerts button
    if st.button("Generate Sample Alerts"):
        _generate_sample_alerts()
        st.rerun()


def _render_events_panel():
    """Render events log panel."""
    st.subheader("Event Log")

    # Sample events
    if not st.session_state.events:
        _generate_sample_events()

    # Events table
    events_data = []
    for event in st.session_state.events[-50:]:
        events_data.append({
            "Timestamp": event.get("timestamp", ""),
            "Category": event.get("category", ""),
            "Severity": event.get("severity", ""),
            "Source": event.get("source", ""),
            "Message": event.get("message", "")[:60],
        })

    if events_data:
        st.dataframe(events_data, width="stretch", height=400)
    else:
        st.info("No events recorded.")

    # Export button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Export Events"):
            st.download_button(
                "Download CSV",
                data="\n".join([str(e) for e in st.session_state.events]),
                file_name="tara_events.csv",
                mime="text/csv",
            )


def render_brain_topology_page():
    """Render the Brain Topology visualization page."""
    st.title("Brain Topology Monitor")
    st.markdown("*Real-time BCI node monitoring with 3D brain visualization*")

    if not VISUALIZATION_AVAILABLE:
        st.error("Visualization modules not available. Please check installation.")
        return

    # Controls row
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

    with col1:
        color_by = st.selectbox(
            "Color electrodes by",
            ["spike_rate", "impedance", "snr", "status"],
            format_func=lambda x: x.replace("_", " ").title(),
        )

    with col2:
        regions = list(BRAIN_REGIONS.keys())
        selected_region = st.selectbox(
            "Focus on region",
            ["All Regions"] + regions,
        )
        if selected_region == "All Regions":
            selected_region = None

    with col3:
        show_threads = st.checkbox("Show threads", value=True)

    with col4:
        if st.button("Simulate Activity", type="secondary"):
            _simulate_electrode_activity()
            st.rerun()

    # Main visualization
    viz = BrainTopologyVisualization()

    if st.session_state.electrode_array:
        viz.set_electrode_array(st.session_state.electrode_array)

        # Render 3D brain
        fig = viz.render(
            highlight_region=selected_region,
            color_by=color_by,
            show_threads=show_threads,
            filter_region=selected_region,
            height=500,
        )
        st.plotly_chart(fig, width="stretch")

        # Metrics summary
        st.subheader("Electrode Array Metrics")
        metrics_fig = viz.create_metrics_summary(region=selected_region)
        st.plotly_chart(metrics_fig, width="stretch")

        # Region/Thread details
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Regions Summary")
            region_data = []
            for abbr, region in BRAIN_REGIONS.items():
                threads = st.session_state.electrode_array.get_threads_by_region(abbr)
                electrodes = st.session_state.electrode_array.get_electrodes_by_region(abbr)
                if threads:
                    active = len([e for e in electrodes if e.status != ElectrodeStatus.OFFLINE])
                    region_data.append({
                        "Region": f"{abbr} - {region.name}",
                        "Threads": len(threads),
                        "Electrodes": len(electrodes),
                        "Active": active,
                        "ONI Layer": f"L{region.oni_layer}",
                    })
            if region_data:
                st.dataframe(region_data, width="stretch", hide_index=True)
            else:
                st.info("No electrodes placed in defined regions")

        with col2:
            st.subheader("Thread Status")
            thread_data = []
            for thread in st.session_state.electrode_array.threads[:10]:
                thread.update_metrics()
                thread_data.append({
                    "Thread ID": thread.thread_id,
                    "Region": thread.region,
                    "Electrodes": len(thread.electrodes),
                    "Active": thread.active_electrodes,
                    "Avg Impedance": f"{thread.avg_impedance:.0f} kOhm",
                    "Avg SNR": f"{thread.avg_snr:.1f} dB",
                })
            if thread_data:
                st.dataframe(thread_data, width="stretch", hide_index=True)

    else:
        st.warning("No electrode array configured. Initialize one in settings.")


def _simulate_electrode_activity():
    """Simulate random electrode activity changes."""
    if not st.session_state.electrode_array:
        return

    for thread in st.session_state.electrode_array.threads:
        for electrode in thread.electrodes:
            # Random fluctuations
            electrode.spike_rate = np.clip(
                electrode.spike_rate + np.random.normal(0, 3), 0, 100
            )
            electrode.impedance = np.clip(
                electrode.impedance + np.random.normal(0, 20), 100, 1000
            )
            electrode.snr = np.clip(
                electrode.snr + np.random.normal(0, 1), 0, 30
            )

            # Occasionally change status
            if np.random.random() < 0.05:
                statuses = [ElectrodeStatus.NORMAL, ElectrodeStatus.WARNING]
                electrode.status = np.random.choice(statuses)


def render_neural_firewall_page():
    """Render the Neural Firewall visualization page."""
    st.title("Neural Firewall")
    st.markdown("*ONI-Aligned Signal Validation Pipeline (L8-L14)*")

    if not VISUALIZATION_AVAILABLE:
        st.error("Visualization modules not available. Please check installation.")
        return

    firewall = st.session_state.neural_firewall
    if not firewall:
        st.error("Neural firewall not initialized.")
        return

    # Control row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Process Signal", type="primary"):
            # Simulate a signal going through the firewall (L8-L14)
            signal = {
                "impedance": np.random.uniform(150, 600),       # L8: Neural Gateway
                "snr": np.random.uniform(3, 20),                # L9: Signal Processing
                "spike_rate": np.random.uniform(5, 250),        # L10: Protocol
                "signal_rate": np.random.uniform(100, 800),     # L11: Transport
                "consistency": np.random.uniform(0.7, 1.0),     # L12: Session
                "coherence": np.random.uniform(0.2, 0.95),      # L13: Presentation
                "anomaly_score": np.random.uniform(0, 1),       # L14: Application
            }
            result = firewall.process_signal(signal)
            st.session_state.last_signal_result = result
            st.session_state.last_signal = signal
            st.session_state.firewall_signals_processed += 1
            st.rerun()

    with col2:
        if st.button("Batch Process (10)", type="secondary"):
            for _ in range(10):
                signal = {
                    "impedance": np.random.uniform(100, 800),
                    "snr": np.random.uniform(2, 25),
                    "spike_rate": np.random.uniform(0, 350),
                    "signal_rate": np.random.uniform(50, 1200),
                    "consistency": np.random.uniform(0.5, 1.0),
                    "coherence": np.random.uniform(0.1, 0.99),
                    "anomaly_score": np.random.uniform(0, 1),
                }
                firewall.process_signal(signal)
            st.session_state.firewall_signals_processed += 10
            st.rerun()

    with col3:
        if st.button("Reset Stats"):
            firewall.reset_statistics()
            st.session_state.firewall_signals_processed = 0
            st.rerun()

    with col4:
        st.metric("Signals Processed", st.session_state.firewall_signals_processed)

    # Pipeline visualization
    st.subheader("Validation Pipeline")
    pipeline_viz = FirewallPipelineVisualization(firewall)
    pipeline_fig = pipeline_viz.create_pipeline_figure(show_stats=True, height=500)
    st.plotly_chart(pipeline_fig, width="stretch")

    # Last signal result
    if "last_signal_result" in st.session_state:
        result = st.session_state.last_signal_result
        signal = st.session_state.get("last_signal", {})

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Last Signal")
            if result["passed"]:
                st.success("Signal PASSED all checkpoints")
            else:
                st.error(f"Signal BLOCKED at Layer {result['blocked_at']}")

            # Show signal values
            signal_data = []
            for key, value in signal.items():
                signal_data.append({"Metric": key.replace("_", " ").title(), "Value": f"{value:.3f}"})
            st.dataframe(signal_data, width="stretch", hide_index=True)

        with col2:
            st.subheader("Checkpoint Results")
            for cp_result in result["checkpoint_results"]:
                layer = cp_result["layer"]
                status = cp_result["status"]

                label = "✓" if status == "pass" else "✗" if status == "fail" else "○"
                checkpoint = firewall.get_checkpoint(layer)
                st.markdown(f"{label} **L{layer}: {checkpoint.name}** - {status.upper()}")

    # Checkpoint details
    st.subheader("Checkpoint Details")
    checkpoint_tabs = st.tabs([f"L{cp.layer}" for cp in firewall.checkpoints])

    for i, tab in enumerate(checkpoint_tabs):
        with tab:
            cp = firewall.checkpoints[i]
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"**{cp.name}**")
                st.markdown(f"_{cp.description}_")
                if cp.threshold_low is not None:
                    st.markdown(f"Min: {cp.threshold_low} {cp.unit}")
                if cp.threshold_high is not None:
                    st.markdown(f"Max: {cp.threshold_high} {cp.unit}")

            with col2:
                st.metric("Processed", cp.signals_processed)
                st.metric("Passed", cp.signals_passed)

            with col3:
                st.metric("Blocked", cp.signals_blocked)
                st.metric("Pass Rate", f"{cp.pass_rate():.1f}%")


def render_settings_page():
    """Render settings page."""
    st.title("Settings")

    tab1, tab2, tab3 = st.tabs(["Detection Rules", "Thresholds", "System"])

    with tab1:
        st.subheader("Detection Rules")

        rules = [
            ("coherence_low", "Low Coherence Warning", True),
            ("coherence_critical", "Critical Coherence Drop", True),
            ("spike_surge", "Spike Rate Surge", True),
            ("dos_signature", "DoS Attack Signature", True),
            ("ransomware_signature", "Neural Ransomware Signature", True),
            ("gateway_bypass", "Gateway Bypass Attempt", True),
        ]

        for rule_id, rule_name, enabled in rules:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.checkbox(rule_name, value=enabled, key=f"rule_{rule_id}")
            with col2:
                st.button("Edit", key=f"edit_{rule_id}")

    with tab2:
        st.subheader("Detection Thresholds")

        st.markdown("### Coherence")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Warning Threshold", 0.0, 1.0, 0.5, 0.05, key="thresh_coh_warn")
        with col2:
            st.number_input("Critical Threshold", 0.0, 1.0, 0.3, 0.05, key="thresh_coh_crit")

        st.markdown("### Spike Rate")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Warning Threshold (Hz)", 0, 500, 200, 10, key="thresh_spike_warn")
        with col2:
            st.number_input("Critical Threshold (Hz)", 0, 500, 300, 10, key="thresh_spike_crit")

    with tab3:
        st.subheader("System Settings")

        st.markdown("### Data Retention")
        st.slider("Keep events for (days)", 1, 90, 30)
        st.slider("Keep alerts for (days)", 1, 365, 90)

        st.markdown("### Performance")
        st.slider("Update interval (seconds)", 0.1, 5.0, 1.0, 0.1)
        st.number_input("Max events in memory", 1000, 100000, 10000)

        st.divider()

        if st.button("Save Settings", type="primary"):
            st.success("Settings saved successfully!")


# ============================================================================
# NEUROSECURITY PAGE (Kohno Threat Rules + Privacy Calculator)
# ============================================================================

# Kohno (2009) Threat Rules - 11 rules across 3 categories
KOHNO_THREAT_RULES = [
    # ALTERATION (Integrity threats)
    {"id": "ALT-01", "category": "ALTERATION", "name": "Signal Injection", "description": "Unauthorized signal injection to alter neural processing", "cia": "Integrity", "severity": "CRITICAL"},
    {"id": "ALT-02", "category": "ALTERATION", "name": "Motor Hijacking", "description": "Forced motor output through unauthorized commands", "cia": "Integrity", "severity": "CRITICAL"},
    {"id": "ALT-03", "category": "ALTERATION", "name": "Memory Tampering", "description": "Modification of memory formation or recall", "cia": "Integrity", "severity": "CRITICAL"},
    {"id": "ALT-04", "category": "ALTERATION", "name": "Perception Distortion", "description": "Altering sensory processing pathways", "cia": "Integrity", "severity": "HIGH"},
    # BLOCKING (Availability threats)
    {"id": "BLK-01", "category": "BLOCKING", "name": "Neural DoS", "description": "Overwhelming neural pathways to cause dysfunction", "cia": "Availability", "severity": "CRITICAL"},
    {"id": "BLK-02", "category": "BLOCKING", "name": "Signal Jamming", "description": "Interference preventing legitimate signal transmission", "cia": "Availability", "severity": "HIGH"},
    {"id": "BLK-03", "category": "BLOCKING", "name": "Motor Lockout", "description": "Blocking motor command execution", "cia": "Availability", "severity": "CRITICAL"},
    {"id": "BLK-04", "category": "BLOCKING", "name": "Communication Block", "description": "Preventing BCI communication channels", "cia": "Availability", "severity": "HIGH"},
    # EAVESDROPPING (Confidentiality threats)
    {"id": "EVD-01", "category": "EAVESDROPPING", "name": "Neural Wiretapping", "description": "Unauthorized reading of neural signals", "cia": "Confidentiality", "severity": "HIGH"},
    {"id": "EVD-02", "category": "EAVESDROPPING", "name": "Cognitive State Extraction", "description": "Inferring mental states from neural patterns", "cia": "Confidentiality", "severity": "CRITICAL"},
    {"id": "EVD-03", "category": "EAVESDROPPING", "name": "Memory Exfiltration", "description": "Extracting memories or learned patterns", "cia": "Confidentiality", "severity": "CRITICAL"},
]

# ERP Types for Privacy Score (Bonaci et al., 2015)
ERP_TYPES = {
    "P300": {"name": "P300", "sensitivity": 0.9, "description": "Recognition, familiarity, lies"},
    "N170": {"name": "N170", "sensitivity": 0.85, "description": "Face recognition, identity"},
    "N400": {"name": "N400", "sensitivity": 0.8, "description": "Semantic processing, meaning"},
    "ERN": {"name": "ERN", "sensitivity": 0.75, "description": "Error detection, self-monitoring"},
    "LPP": {"name": "LPP", "sensitivity": 0.7, "description": "Emotional arousal, attention"},
    "MMN": {"name": "MMN", "sensitivity": 0.6, "description": "Deviance detection, attention"},
    "CNV": {"name": "CNV", "sensitivity": 0.55, "description": "Expectation, preparation"},
    "SSVEP": {"name": "SSVEP", "sensitivity": 0.4, "description": "Visual attention (less sensitive)"},
}


def render_neurosecurity_page():
    """Render the Neurosecurity page with Kohno threat rules and privacy calculator."""
    st.title("Neurosecurity Monitor")
    st.markdown("*Kohno (2009) Threat Taxonomy + Bonaci (2015) BCI Privacy*")

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Threat Rules", "Privacy Calculator", "BCI Anonymizer", "Threat Classifier"])

    with tab1:
        _render_kohno_rules_grid()

    with tab2:
        _render_privacy_calculator()

    with tab3:
        _render_bci_anonymizer_demo()

    with tab4:
        _render_threat_classifier()


def _render_kohno_rules_grid():
    """Render Kohno threat rules as an interactive grid."""
    st.subheader("Kohno (2009) Threat Taxonomy")
    st.markdown("*11 Neural Security Threat Rules across CIA Triad*")

    # Category tabs
    categories = ["ALTERATION", "BLOCKING", "EAVESDROPPING"]
    category_colors = {"ALTERATION": "#ef4444", "BLOCKING": "#f59e0b", "EAVESDROPPING": "#3b82f6"}

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        alt_count = len([r for r in KOHNO_THREAT_RULES if r["category"] == "ALTERATION"])
        st.metric("Alteration (Integrity)", f"{alt_count} rules", delta="CRITICAL")
    with col2:
        blk_count = len([r for r in KOHNO_THREAT_RULES if r["category"] == "BLOCKING"])
        st.metric("Blocking (Availability)", f"{blk_count} rules", delta="HIGH")
    with col3:
        evd_count = len([r for r in KOHNO_THREAT_RULES if r["category"] == "EAVESDROPPING"])
        st.metric("Eavesdropping (Confidentiality)", f"{evd_count} rules", delta="HIGH")

    st.divider()

    # Display rules by category
    for category in categories:
        color = category_colors[category]
        cia = {"ALTERATION": "Integrity", "BLOCKING": "Availability", "EAVESDROPPING": "Confidentiality"}[category]

        st.markdown(f"### {category} ({cia})")

        rules = [r for r in KOHNO_THREAT_RULES if r["category"] == category]
        for rule in rules:
            severity_icon = "🔴" if rule["severity"] == "CRITICAL" else "🟠"
            with st.expander(f"{severity_icon} {rule['id']}: {rule['name']}", expanded=False):
                st.markdown(f"**Description:** {rule['description']}")
                st.markdown(f"**CIA Mapping:** {rule['cia']}")
                st.markdown(f"**Severity:** {rule['severity']}")
                st.markdown(f"**ONI Layers:** L8-L14 (Neural Gateway and above)")

                # Detection status (mock)
                detection_col1, detection_col2 = st.columns(2)
                with detection_col1:
                    st.markdown("**Detection Status:** 🟢 Active")
                with detection_col2:
                    st.markdown("**Last Triggered:** Never")

        st.markdown("")


def _render_privacy_calculator():
    """Render privacy score calculator with ERP checkboxes."""
    st.subheader("Privacy Score Calculator")
    st.markdown("*Based on Bonaci et al. (2015) BCI Privacy Research*")

    st.info("Select detected ERPs to calculate privacy risk score. Higher sensitivity = higher privacy risk.")

    # ERP selection checkboxes
    st.markdown("### Detected ERPs")

    selected_erps = []
    erp_cols = st.columns(4)

    for i, (erp_id, erp_info) in enumerate(ERP_TYPES.items()):
        with erp_cols[i % 4]:
            if st.checkbox(f"{erp_id}", key=f"erp_{erp_id}"):
                selected_erps.append(erp_id)
            st.caption(erp_info["description"][:30])

    st.divider()

    # Calculate score
    if st.button("Calculate Privacy Score", type="primary"):
        if selected_erps:
            # Calculate weighted privacy score
            total_sensitivity = sum(ERP_TYPES[erp]["sensitivity"] for erp in selected_erps)
            max_possible = sum(erp["sensitivity"] for erp in ERP_TYPES.values())
            score = total_sensitivity / max_possible

            # Store result
            st.session_state.privacy_score_result = {
                "score": score,
                "selected_erps": selected_erps,
                "interpretation": _interpret_privacy_score(score),
            }
        else:
            st.session_state.privacy_score_result = {
                "score": 0,
                "selected_erps": [],
                "interpretation": "LOW",
            }

    # Display results
    if st.session_state.privacy_score_result:
        result = st.session_state.privacy_score_result

        col1, col2 = st.columns(2)

        with col1:
            # Privacy score gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=result["score"] * 100,
                title={"text": "Privacy Risk Score"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "darkred"},
                    "steps": [
                        {"range": [0, 25], "color": "#22c55e"},
                        {"range": [25, 50], "color": "#f59e0b"},
                        {"range": [50, 75], "color": "#ef4444"},
                        {"range": [75, 100], "color": "#7f1d1d"},
                    ],
                },
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, width="stretch")

        with col2:
            st.markdown("### Risk Interpretation")
            interp = result["interpretation"]
            interp_colors = {"LOW": "🟢", "MODERATE": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}
            st.markdown(f"**Level:** {interp_colors.get(interp, '⚪')} {interp}")

            st.markdown("**Selected ERPs:**")
            for erp in result["selected_erps"]:
                st.markdown(f"- {erp}: {ERP_TYPES[erp]['description']}")

            st.markdown("**Recommendations:**")
            if interp == "CRITICAL":
                st.markdown("- Immediate BCI Anonymizer activation required")
                st.markdown("- Consider temporal smearing and frequency masking")
            elif interp == "HIGH":
                st.markdown("- Enable ERP filtering at L8")
                st.markdown("- Monitor for pattern extraction attempts")
            elif interp == "MODERATE":
                st.markdown("- Standard privacy protocols sufficient")
                st.markdown("- Continue monitoring")
            else:
                st.markdown("- Low risk - standard operation")


def _interpret_privacy_score(score: float) -> str:
    """Interpret privacy score into risk level."""
    if score >= 0.75:
        return "CRITICAL"
    elif score >= 0.50:
        return "HIGH"
    elif score >= 0.25:
        return "MODERATE"
    else:
        return "LOW"


def _render_bci_anonymizer_demo():
    """Render BCI Anonymizer demo with before/after visualization."""
    st.subheader("BCI Anonymizer Demo")
    st.markdown("*Privacy-preserving signal transformation (Bonaci et al., 2015)*")

    st.info("The BCI Anonymizer removes privacy-sensitive ERP components while preserving functional utility.")

    # Configuration
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Anonymization Settings")
        temporal_blur = st.slider("Temporal Smearing (ms)", 0, 50, 20)
        freq_mask = st.slider("Frequency Masking (%)", 0, 100, 30)
        erp_filter = st.multiselect("ERPs to Filter", list(ERP_TYPES.keys()), default=["P300", "N170"])

    with col2:
        st.markdown("### Utility Preservation")
        st.metric("Motor Command Accuracy", "98%", delta="-2%")
        st.metric("Latency Impact", "+15ms", delta=None)
        st.metric("Signal Quality", "92%", delta="-8%")

    st.divider()

    # Generate demo visualization
    if st.button("Run Anonymization Demo", type="primary"):
        st.markdown("### Before/After Comparison")

        # Generate sample signal
        np.random.seed(42)
        t = np.linspace(0, 1, 500)
        original = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 40 * t)
        original += 2 * np.exp(-((t - 0.3) ** 2) / 0.01)  # P300-like component

        # Anonymized (remove P300 component, add blur)
        anonymized = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 40 * t)
        anonymized += np.random.normal(0, 0.1 * temporal_blur / 50, len(t))

        # Create comparison plot
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           subplot_titles=("Original Signal (Privacy-Sensitive)", "Anonymized Signal"))

        fig.add_trace(
            go.Scatter(x=t * 1000, y=original, mode="lines", name="Original",
                      line=dict(color="#ef4444")),
            row=1, col=1,
        )

        # Highlight P300 region
        fig.add_vrect(x0=250, x1=350, fillcolor="rgba(239,68,68,0.2)",
                     line_width=0, row=1, col=1,
                     annotation_text="P300", annotation_position="top left")

        fig.add_trace(
            go.Scatter(x=t * 1000, y=anonymized, mode="lines", name="Anonymized",
                      line=dict(color="#22c55e")),
            row=2, col=1,
        )

        fig.update_layout(height=400, showlegend=False)
        fig.update_xaxes(title_text="Time (ms)", row=2, col=1)
        fig.update_yaxes(title_text="Amplitude (μV)")

        st.plotly_chart(fig, width="stretch")

        st.success(f"Anonymization complete. Filtered ERPs: {', '.join(erp_filter)}")


def _render_threat_classifier():
    """Render threat classifier with metric inputs."""
    st.subheader("Threat Classifier")
    st.markdown("*Real-time threat categorization based on signal metrics*")

    # Metric inputs
    col1, col2, col3 = st.columns(3)

    with col1:
        coherence = st.number_input("Coherence Score (Cₛ)", 0.0, 1.0, 0.85, 0.05)
        spike_rate = st.number_input("Spike Rate (Hz)", 0, 500, 50, 10)

    with col2:
        amplitude = st.number_input("Signal Amplitude (μV)", 0.0, 200.0, 50.0, 5.0)
        phase_deviation = st.number_input("Phase Deviation (°)", 0.0, 180.0, 15.0, 5.0)

    with col3:
        freq_shift = st.number_input("Frequency Shift (%)", -50, 50, 0, 5)
        latency = st.number_input("Latency (ms)", 0, 500, 20, 5)

    st.divider()

    if st.button("Classify Threat", type="primary"):
        # Classification logic
        threat_type = None
        confidence = 0.0

        if coherence < 0.3:
            threat_type = "ALTERATION"
            confidence = (0.3 - coherence) / 0.3
        elif spike_rate > 300:
            threat_type = "BLOCKING"
            confidence = min((spike_rate - 300) / 200, 1.0)
        elif phase_deviation > 90:
            threat_type = "EAVESDROPPING"
            confidence = phase_deviation / 180

        if threat_type:
            st.session_state.threat_classification = {
                "type": threat_type,
                "confidence": confidence,
                "metrics": {
                    "coherence": coherence,
                    "spike_rate": spike_rate,
                    "amplitude": amplitude,
                    "phase_deviation": phase_deviation,
                },
            }
        else:
            st.session_state.threat_classification = {
                "type": "NORMAL",
                "confidence": 0.95,
                "metrics": {},
            }

    # Display classification
    if st.session_state.threat_classification:
        result = st.session_state.threat_classification

        col1, col2 = st.columns(2)

        with col1:
            threat = result["type"]
            threat_colors = {
                "NORMAL": "#22c55e",
                "ALTERATION": "#ef4444",
                "BLOCKING": "#f59e0b",
                "EAVESDROPPING": "#3b82f6",
            }
            color = threat_colors.get(threat, "#888888")

            st.markdown(f"""
            <div style="background-color:{color}; padding:20px; border-radius:10px; text-align:center;">
                <h2 style="color:white; margin:0;">{threat}</h2>
                <p style="color:white; margin:5px 0;">Confidence: {result['confidence']:.0%}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("### Recommended Actions")
            if threat == "ALTERATION":
                st.markdown("- 🔴 Activate L8 Neural Firewall")
                st.markdown("- 🔴 Enable signal integrity verification")
                st.markdown("- 🔴 Alert security team")
            elif threat == "BLOCKING":
                st.markdown("- 🟠 Check for DoS attack patterns")
                st.markdown("- 🟠 Enable rate limiting at L8")
                st.markdown("- 🟠 Switch to backup channels")
            elif threat == "EAVESDROPPING":
                st.markdown("- 🔵 Activate BCI Anonymizer")
                st.markdown("- 🔵 Enable encryption at L9")
                st.markdown("- 🔵 Monitor for data exfiltration")
            else:
                st.markdown("- 🟢 Normal operation")
                st.markdown("- 🟢 Continue standard monitoring")


# ============================================================================
# REAL EEG DATA PAGE (MOABB Integration)
# ============================================================================

# Available MOABB datasets
MOABB_DATASETS = {
    "BNCI2014_001": {
        "name": "BNCI2014_001 (Motor Imagery)",
        "paradigm": "Motor Imagery",
        "subjects": 9,
        "description": "4-class motor imagery (left hand, right hand, feet, tongue)",
        "oni_relevance": "Motor cortex (L13) attack detection",
    },
    "BNCI2014_002": {
        "name": "BNCI2014_002 (Motor Imagery)",
        "paradigm": "Motor Imagery",
        "subjects": 14,
        "description": "3-class motor imagery (left hand, right hand, feet)",
        "oni_relevance": "Longitudinal firewall validation",
    },
    "EPFLP300": {
        "name": "EPFL P300 Dataset",
        "paradigm": "P300",
        "subjects": 8,
        "description": "P300 speller paradigm",
        "oni_relevance": "Privacy-sensitive ERP (Kohno threats)",
    },
    "SSVEP_Exo": {
        "name": "SSVEP Exoskeleton",
        "paradigm": "SSVEP",
        "subjects": 12,
        "description": "Steady-state visual evoked potentials",
        "oni_relevance": "Frequency injection attack vectors",
    },
    "Weibo2014": {
        "name": "Weibo 2014 (Motor Imagery)",
        "paradigm": "Motor Imagery",
        "subjects": 10,
        "description": "Multi-class motor imagery",
        "oni_relevance": "Cross-session attack resilience",
    },
}

# Attack types for injection
ATTACK_TYPES = {
    "spike": {"name": "Spike Attack", "description": "Sharp amplitude spikes (ransomware signature)"},
    "noise": {"name": "Gaussian Noise", "description": "Additive white noise (jamming)"},
    "frequency": {"name": "Frequency Shift", "description": "Alter frequency content (evasion)"},
    "phase": {"name": "Phase Manipulation", "description": "Phase scrambling (coherence attack)"},
    "dc_shift": {"name": "DC Shift", "description": "Baseline drift (gradual manipulation)"},
}


def render_real_eeg_page():
    """Render Real EEG Data page with MOABB integration."""
    st.title("Real EEG Data")
    st.markdown("*MOABB Dataset Integration for Security Testing*")

    # Check if MOABB is available
    try:
        from tara_mvp.data import MOABBAdapter, is_moabb_available
        moabb_available = is_moabb_available()
    except ImportError:
        moabb_available = False

    if not moabb_available:
        st.warning("MOABB not installed. Install with: `pip install oni-tara[moabb]`")
        st.info("MOABB provides real EEG datasets for testing attack detection algorithms.")

        # Show what would be available
        st.markdown("### Available Datasets (requires MOABB)")
        for ds_id, ds_info in MOABB_DATASETS.items():
            with st.expander(ds_info["name"]):
                st.markdown(f"**Paradigm:** {ds_info['paradigm']}")
                st.markdown(f"**Subjects:** {ds_info['subjects']}")
                st.markdown(f"**Description:** {ds_info['description']}")
                st.markdown(f"**ONI Relevance:** {ds_info['oni_relevance']}")
        return

    # MOABB is available
    st.success("MOABB is available. Real EEG data ready for security testing.")

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Load Dataset", "Attack Injection", "Coherence Benchmark"])

    with tab1:
        _render_dataset_loader()

    with tab2:
        _render_attack_injection()

    with tab3:
        _render_coherence_benchmark()


def _render_dataset_loader():
    """Render dataset loading interface."""
    st.subheader("Load MOABB Dataset")

    col1, col2 = st.columns(2)

    with col1:
        # Dataset selector
        dataset_id = st.selectbox(
            "Select Dataset",
            list(MOABB_DATASETS.keys()),
            format_func=lambda x: MOABB_DATASETS[x]["name"],
        )

        ds_info = MOABB_DATASETS[dataset_id]
        st.markdown(f"**Paradigm:** {ds_info['paradigm']}")
        st.markdown(f"**Description:** {ds_info['description']}")

    with col2:
        # Subject and epoch controls
        subject = st.number_input("Subject ID", 1, ds_info["subjects"], 1)
        max_epochs = st.slider("Max Epochs", 5, 100, 20)

    st.divider()

    if st.button("Load Dataset", type="primary"):
        with st.spinner("Loading dataset... (this may take a moment for first download)"):
            try:
                from tara_mvp.data import MOABBAdapter

                adapter = MOABBAdapter()
                dataset = adapter.load_dataset(dataset_id)
                signals = adapter.get_signals(dataset, subject=subject, max_epochs=max_epochs)

                st.session_state.moabb_signals = signals
                st.session_state.moabb_dataset = dataset_id

                st.success(f"Loaded {len(signals)} epochs from {dataset_id}, subject {subject}")

            except Exception as e:
                st.error(f"Error loading dataset: {e}")

    # Display loaded signals
    if st.session_state.moabb_signals:
        signals = st.session_state.moabb_signals
        st.markdown("### Loaded Signals")

        st.metric("Total Epochs", len(signals))

        # Show first signal preview
        if signals:
            signal = signals[0]
            st.markdown(f"**Shape:** {signal.data.shape}")
            st.markdown(f"**Sample Rate:** {signal.sample_rate} Hz")
            st.markdown(f"**Label:** {signal.label}")

            # Plot first epoch
            fig = go.Figure()
            for ch in range(min(4, signal.data.shape[0])):
                fig.add_trace(go.Scatter(
                    y=signal.data[ch, :500],
                    mode="lines",
                    name=f"Ch {ch}",
                    opacity=0.7,
                ))
            fig.update_layout(
                title="First Epoch Preview (4 channels, 500 samples)",
                xaxis_title="Sample",
                yaxis_title="Amplitude (μV)",
                height=300,
            )
            st.plotly_chart(fig, width="stretch")


def _render_attack_injection():
    """Render attack injection interface."""
    st.subheader("Attack Injection")

    if not st.session_state.moabb_signals:
        st.warning("Load a dataset first in the 'Load Dataset' tab.")
        return

    signals = st.session_state.moabb_signals

    col1, col2 = st.columns(2)

    with col1:
        # Attack type selector
        attack_type = st.selectbox(
            "Attack Type",
            list(ATTACK_TYPES.keys()),
            format_func=lambda x: ATTACK_TYPES[x]["name"],
        )
        st.caption(ATTACK_TYPES[attack_type]["description"])

        # Attack parameters
        intensity = st.slider("Attack Intensity", 0.1, 5.0, 2.0, 0.1)
        target_channels = st.multiselect(
            "Target Channels",
            list(range(min(8, signals[0].data.shape[0]))),
            default=[0, 1, 2],
        )

    with col2:
        # Epoch selector
        epoch_idx = st.slider("Target Epoch", 0, len(signals) - 1, 0)

        st.markdown("### Original Signal Stats")
        signal = signals[epoch_idx]
        st.metric("Max Amplitude", f"{signal.data.max():.2f} μV")
        st.metric("Mean", f"{signal.data.mean():.2f} μV")
        st.metric("Std", f"{signal.data.std():.2f} μV")

    st.divider()

    if st.button("Inject Attack", type="primary"):
        try:
            from tara_mvp.data import MOABBAdapter

            adapter = MOABBAdapter()
            attacked = adapter.inject_attack(
                signals[epoch_idx],
                attack_type=attack_type,
                intensity=intensity,
                channels=target_channels,
            )

            # Comparison plot
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                               subplot_titles=("Original Signal", f"After {ATTACK_TYPES[attack_type]['name']}"))

            ch = target_channels[0] if target_channels else 0

            fig.add_trace(
                go.Scatter(y=signals[epoch_idx].data[ch, :], mode="lines",
                          line=dict(color="#22c55e"), name="Original"),
                row=1, col=1,
            )

            fig.add_trace(
                go.Scatter(y=attacked.attacked[ch, :], mode="lines",
                          line=dict(color="#ef4444"), name="Attacked"),
                row=2, col=1,
            )

            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, width="stretch")

            # Stats comparison
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original:**")
                st.metric("Max", f"{signals[epoch_idx].data.max():.2f}")
            with col2:
                st.markdown("**Attacked:**")
                delta = attacked.attacked.max() - signals[epoch_idx].data.max()
                st.metric("Max", f"{attacked.attacked.max():.2f}", delta=f"+{delta:.2f}")

        except Exception as e:
            st.error(f"Error injecting attack: {e}")


def _render_coherence_benchmark():
    """Render coherence benchmark interface."""
    st.subheader("Coherence Benchmark")
    st.markdown("*Test coherence metric detection accuracy against real EEG*")

    if not st.session_state.moabb_signals:
        st.warning("Load a dataset first in the 'Load Dataset' tab.")
        return

    signals = st.session_state.moabb_signals

    col1, col2 = st.columns(2)

    with col1:
        attack_type = st.selectbox(
            "Attack Type for Benchmark",
            list(ATTACK_TYPES.keys()),
            format_func=lambda x: ATTACK_TYPES[x]["name"],
            key="bench_attack",
        )
        intensity = st.slider("Attack Intensity", 0.5, 3.0, 1.5, 0.1, key="bench_intensity")

    with col2:
        n_samples = st.slider("Number of Epochs to Test", 5, min(50, len(signals)), 10)

    st.divider()

    if st.button("Run Benchmark", type="primary"):
        with st.spinner("Running coherence benchmark..."):
            try:
                from tara_mvp.data import MOABBAdapter
                from tara_mvp import calculate_cs

                adapter = MOABBAdapter()

                # Prepare clean and attacked signals
                clean_scores = []
                attacked_scores = []

                for i in range(min(n_samples, len(signals))):
                    signal = signals[i]

                    # Calculate coherence on clean signal
                    clean_score = calculate_cs(signal.data)
                    clean_scores.append(clean_score)

                    # Inject attack and calculate
                    attacked = adapter.inject_attack(signal, attack_type, intensity)
                    attacked_score = calculate_cs(attacked.attacked)
                    attacked_scores.append(attacked_score)

                # Calculate detection metrics
                threshold = 0.5
                clean_correct = sum(1 for s in clean_scores if s >= threshold)
                attacked_correct = sum(1 for s in attacked_scores if s < threshold)
                total = len(clean_scores) + len(attacked_scores)

                accuracy = (clean_correct + attacked_correct) / total
                precision = attacked_correct / max(attacked_correct + (len(clean_scores) - clean_correct), 1)
                recall = attacked_correct / len(attacked_scores)
                f1 = 2 * precision * recall / max(precision + recall, 0.001)

                # Store results
                st.session_state.moabb_benchmark_results = {
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                    "clean_scores": clean_scores,
                    "attacked_scores": attacked_scores,
                }

                st.success("Benchmark complete!")

            except Exception as e:
                st.error(f"Error running benchmark: {e}")

    # Display results
    if st.session_state.moabb_benchmark_results:
        results = st.session_state.moabb_benchmark_results

        st.markdown("### Detection Metrics")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Accuracy", f"{results['accuracy']:.1%}")
        with col2:
            st.metric("Precision", f"{results['precision']:.1%}")
        with col3:
            st.metric("Recall", f"{results['recall']:.1%}")
        with col4:
            st.metric("F1 Score", f"{results['f1']:.2f}")

        # Distribution plot
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=results["clean_scores"],
            name="Clean Signals",
            marker_color="#22c55e",
            opacity=0.7,
        ))
        fig.add_trace(go.Histogram(
            x=results["attacked_scores"],
            name="Attacked Signals",
            marker_color="#ef4444",
            opacity=0.7,
        ))

        fig.add_vline(x=0.5, line_dash="dash", line_color="white",
                     annotation_text="Threshold (0.5)")

        fig.update_layout(
            title="Coherence Score Distribution",
            xaxis_title="Coherence Score (Cₛ)",
            yaxis_title="Count",
            barmode="overlay",
            height=300,
        )
        st.plotly_chart(fig, width="stretch")

        st.caption("Clean signals should cluster above threshold (0.5), attacked signals below.")


def _generate_sample_data():
    """Generate sample metric data."""
    n_points = 100
    base_time = datetime.now() - timedelta(minutes=n_points)

    timestamps = [base_time + timedelta(minutes=i) for i in range(n_points)]
    coherence = 0.85 + np.cumsum(np.random.normal(0, 0.02, n_points))
    coherence = np.clip(coherence, 0.3, 0.99)
    spike_rate = 50 + np.cumsum(np.random.normal(0, 5, n_points))
    spike_rate = np.clip(spike_rate, 10, 250)
    amplitude = 50 + np.random.normal(0, 10, n_points)

    st.session_state.metrics_history = {
        "timestamps": timestamps,
        "coherence": coherence.tolist(),
        "spike_rate": spike_rate.tolist(),
        "amplitude": amplitude.tolist(),
    }


def _generate_sample_alerts():
    """Generate sample alerts."""
    alerts = [
        {
            "level": "CRITICAL",
            "title": "Critical Coherence Drop",
            "description": "Signal coherence fell below 0.3 threshold on L8",
            "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "active": True,
        },
        {
            "level": "HIGH",
            "title": "DoS Attack Pattern Detected",
            "description": "High spike rate detected suggesting DoS attack",
            "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
            "active": True,
        },
        {
            "level": "MEDIUM",
            "title": "Phase Anomaly Detected",
            "description": "Unusual phase relationships in gamma band",
            "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "active": False,
        },
    ]
    st.session_state.alerts.extend(alerts)


def _generate_sample_events():
    """Generate sample events."""
    categories = ["COHERENCE", "SPIKE", "FIREWALL", "SYSTEM"]
    severities = ["INFO", "WARNING", "ERROR"]
    sources = ["L8", "L9", "Monitor", "Rules"]

    events = []
    base_time = datetime.now() - timedelta(hours=1)

    for i in range(30):
        events.append({
            "timestamp": (base_time + timedelta(minutes=i*2)).strftime("%H:%M:%S"),
            "category": np.random.choice(categories),
            "severity": np.random.choice(severities),
            "source": np.random.choice(sources),
            "message": f"Sample event {i+1} - monitoring neural activity",
        })

    st.session_state.events = events


# ============================================================================
# ONI VISUALIZATION PAGES (Interactive HTML Visualizations)
# ============================================================================

# Research alignment mapping for visualizations
VISUALIZATION_RESEARCH = {
    "coherence": {
        "title": "Coherence Metric Playground",
        "research": "Kohno (2009) — Signal integrity verification",
        "description": "Interactive coherence score calculation with real-time waveform comparison. "
                      "Demonstrates how Cₛ = e^(−(σ²φ + σ²τ + σ²γ)) detects attack signatures.",
        "oni_layer": "L8-L9",
    },
    "layers": {
        "title": "ONI Layer Explorer",
        "research": "ONI Framework — 14-layer bio-digital model",
        "description": "Navigate the complete ONI stack from L1 (Physical Carrier) to L14 (Identity & Ethics). "
                      "Shows attack surfaces and defense mechanisms at each layer.",
        "oni_layer": "L1-L14",
    },
    "killchain": {
        "title": "Neural Kill Chain Visualizer",
        "research": "Bonaci (2015) — BCI attack patterns",
        "description": "Animated attack propagation across ONI layers. Shows 5 attack types and how "
                      "the neural firewall intercepts them at L8.",
        "oni_layer": "L8",
    },
    "nsam": {
        "title": "NSAM Checkpoint Simulator",
        "research": "Neural Signal Assurance Monitoring pipeline",
        "description": "Gamified signal validation training. Learn to identify clean vs attacked "
                      "neural signals through 5 checkpoint stages.",
        "oni_layer": "L8-L10",
    },
    "scale_freq": {
        "title": "Scale-Frequency Navigator",
        "research": "f × S ≈ k invariant — Scale-frequency relationship",
        "description": "Explore temporal scales from femtoseconds (quantum) to hours (circadian). "
                      "Demonstrates the scale-frequency invariant principle.",
        "oni_layer": "L9-L14",
    },
}


def render_visualization_page(viz_key: str):
    """
    Render an ONI visualization page.

    Args:
        viz_key: Visualization key (coherence, layers, killchain, nsam, scale_freq)
    """
    if not VISUALIZATION_AVAILABLE:
        st.error("Visualization modules not available. Please check installation.")
        st.info(
            "The visualization modules require the full TARA installation. "
            "Clone the repository and install locally for full functionality."
        )
        return

    info = VISUALIZATION_RESEARCH.get(viz_key, {})

    # Page header
    st.title(f"🧠 {info.get('title', 'ONI Visualization')}")

    # Research context
    with st.expander("📚 Research Context", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**Academic Foundation:** {info.get('research', 'N/A')}")
            st.markdown(info.get('description', ''))
        with col2:
            st.metric("ONI Layers", info.get('oni_layer', 'N/A'))
            st.caption("See ACADEMIC_LANDSCAPE.md for full citations")

    st.divider()

    # Embed the visualization
    try:
        embed = ONIVisualizationEmbed()
        embed.render(
            viz_key,
            height=700,
            initial_data={
                "_visualization": viz_key,
                "oni_layer": info.get("oni_layer", ""),
            },
            scrolling=True,
        )
    except FileNotFoundError as e:
        st.error(f"Visualization file not found: {e}")
        st.info("Run the application from the tara-nsec-platform directory.")
    except Exception as e:
        st.error(f"Error loading visualization: {e}")


def main():
    """Main application entry point."""
    init_session_state()

    render_sidebar()
    page = st.session_state.get("current_page", "Dashboard")

    if page == "Dashboard":
        render_dashboard()
    elif page == "Brain Topology":
        render_brain_topology_page()
    elif page == "Neural Firewall":
        render_neural_firewall_page()
    elif page == "Neural Simulator":
        render_neural_simulator_page()
    elif page == "Attack Simulator":
        render_attack_simulator_page()
    elif page == "Signal Assurance":
        render_nsam_page()
    elif page == "Neurosecurity":
        render_neurosecurity_page()
    elif page == "Real EEG Data":
        render_real_eeg_page()
    elif page == "Settings":
        render_settings_page()
    # Interactive visualization pages (ONI Visualization Suite)
    elif page.startswith("viz_"):
        viz_key = page.replace("viz_", "")
        render_visualization_page(viz_key)

    # Auto-refresh when monitoring
    if st.session_state.monitor_running:
        # Add new data point
        if st.session_state.metrics_history["timestamps"]:
            last_time = st.session_state.metrics_history["timestamps"][-1]
            if isinstance(last_time, datetime):
                new_time = datetime.now()
                st.session_state.metrics_history["timestamps"].append(new_time)

                last_coherence = st.session_state.metrics_history["coherence"][-1]
                new_coherence = np.clip(last_coherence + np.random.normal(0, 0.02), 0.3, 0.99)
                st.session_state.metrics_history["coherence"].append(new_coherence)

                last_spike = st.session_state.metrics_history["spike_rate"][-1]
                new_spike = np.clip(last_spike + np.random.normal(0, 5), 10, 250)
                st.session_state.metrics_history["spike_rate"].append(new_spike)

                new_amp = 50 + np.random.normal(0, 10)
                st.session_state.metrics_history["amplitude"].append(new_amp)

                # Keep only last 200 points
                for key in st.session_state.metrics_history:
                    if len(st.session_state.metrics_history[key]) > 200:
                        st.session_state.metrics_history[key] = st.session_state.metrics_history[key][-200:]

        time.sleep(1)
        st.rerun()


def run_app():
    """Entry point for running the application."""
    main()


if __name__ == "__main__":
    main()
