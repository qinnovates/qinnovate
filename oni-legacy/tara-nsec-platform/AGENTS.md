# TARA Agent Learnings

> **Purpose:** Knowledge compounding through persistent learnings. Each session starts fresh but benefits from discoveries documented here.

---

## Session Protocol

```
1. Read CLAUDE.md — conventions and architecture
2. Read this file (AGENTS.md) — learnings from previous sessions
3. Execute tasks
4. Update this file with new learnings
5. Commit changes (memory persists via git)
```

---

## Critical Discoveries

| Date | Learning | Impact |
|------|----------|--------|
| 2026-01-22 | ONI layer direction was inverted in early code (L1-L7 Silicon, L8 Bridge, L9-L14 Biology) | Fixed across all documentation and code |
| 2026-01-22 | Neural Firewall should map to ONI L8-L14 (7 checkpoints), not arbitrary 6 layers | Rewrote `firewall_pipeline.py` to align with ONI |
| 2026-01-22 | BCI nodes operate at L8 (Neural Gateway) as firewall checkpoints | Key design decision for node architecture |
| 2026-01-22 | Brain regions map to specific ONI layers (M1→L13, S1→L12, PFC→L14, etc.) | Documented in CLAUDE.md and REGION_SECURITY_DATA |
| 2026-01-22 | Plotly deprecated `titlefont` property in colorbar | Use `title=dict(text=..., font=dict(...))` instead |

---

## Patterns Established

### UI Structure
- Sidebar: "TARA" title with "Neural Security Platform" caption
- Navigation sections: Monitoring, Testing, Configuration
- Dashboard consolidates System Status and BCI Node Network
- Real-time Signal Monitor at top of Dashboard with expandable details

### ONI Layer Colors
```python
layer_colors = {
    11: "#22c55e",  # Transport - Green
    12: "#3b82f6",  # Session - Blue
    13: "#f97316",  # Presentation - Orange
    14: "#8b5cf6",  # Application - Purple
}
```

### Status Emoji Convention
```python
status_emoji = {
    "ONLINE": "🟢",
    "DEGRADED": "🟡",
    "WARNING": "🟠",
    "OFFLINE": "🔴",
    "INITIALIZING": "⚪",
}
```

### Brain Region Data Pattern
Each region in `REGION_SECURITY_DATA` should include:
- `name`: Full name
- `function`: What it does
- `oni_layer`: Integer (11-14)
- `oni_name`: Layer name (Transport, Session, Presentation, Application)
- `neuron_types`: List of neuron types
- `connections`: List of connected regions
- `attack_vectors`: List of {name, severity, description}
- `defenses`: List of {name, layer, description}

### Visualization Patterns
- 3D Brain: Use Plotly Surface for mesh, Scatter3d for regions/electrodes
- Region spheres: 15pt markers with white border
- Connections: Rgba lines with 0.4 opacity
- Network topology: Circular layout with `np.linspace(0, 2*np.pi, n)`

---

## Gotchas Avoided

### Streamlit Session State
- Initialize all session state in `init_session_state()` function
- Check `if "key" not in st.session_state` before setting
- Use `st.rerun()` after state changes that need UI refresh

### Plotly in Streamlit
- Use `config={"displayModeBar": False}` for cleaner embeds
- Set `paper_bgcolor="rgba(0,0,0,0)"` for transparent backgrounds
- Use `width="stretch"` for responsive sizing (replaces deprecated `use_container_width=True`)

### Import Patterns
- Use try/except for optional visualization imports
- Set `VISUALIZATION_AVAILABLE = True/False` flag
- Fallback gracefully if modules not installed

### Navigation State
- Store `current_page` in session state
- Use button `type="primary"` for active page, `type="secondary"` for others
- Call `st.rerun()` after changing page

### Edit Tool String Matching
- Always re-read file before editing if unsure of current content
- String must match EXACTLY including whitespace
- Use `replace_all=True` for global replacements

---

## Architecture Decisions

### Why BCI Nodes at L8?
- L8 (Neural Gateway) is the bio-digital boundary
- BCI nodes physically exist at this interface
- All firewall operations happen at L8
- Nodes monitor signals crossing the boundary

### Why 10 Brain Regions?
- M1, S1: Primary motor/sensory (essential for BCI)
- PMC, SMA: Motor planning (movement BCIs)
- PFC: Executive function (cognitive BCIs)
- BROCA, WERNICKE: Language (speech BCIs)
- V1, A1: Visual/auditory (sensory BCIs)
- HIPP: Memory (research target)

### Why REGION_SECURITY_DATA in app.py?
- Keeps UI-specific data with UI code
- Easy to update without modifying data modules
- Contains presentation-layer concerns (attack descriptions, defense explanations)

---

## Performance Considerations

- Limit 3D neuron visualization to ~100 neurons (performance)
- Use `@st.cache_data` for expensive computations (not yet implemented)
- Keep metric history to last 200 points to prevent memory growth
- Use `st.empty()` for dynamic updates instead of full reruns

---

## Future Improvements Identified

1. **Add tests directory** - No unit tests yet
2. **Implement persistence module** - SQLite storage placeholder
3. **Add export functionality** - Report generation
4. **Cache expensive visualizations** - Use Streamlit caching
5. **Add real-time simulation mode** - Connect simulation to NSAM
6. **WebSocket for live updates** - Better than polling with `st.rerun()`

---

## Code Snippets Worth Remembering

### Circular Node Layout
```python
n_nodes = len(nodes)
angles = np.linspace(0, 2 * np.pi, n_nodes, endpoint=False)
radius = 1.0
node_x = [radius * np.cos(a) for a in angles]
node_y = [radius * np.sin(a) for a in angles]
```

### Brain Mesh Ellipsoid
```python
u = np.linspace(0, 2 * np.pi, 30)
v = np.linspace(0, np.pi, 20)
x_brain = 85 * np.outer(np.cos(u), np.sin(v))
y_brain = 70 * np.outer(np.sin(u), np.sin(v))
z_brain = 70 * np.outer(np.ones(np.size(u)), np.cos(v))
```

### Streamlit Page Routing
```python
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

if st.sidebar.button("Page Name", type="primary" if st.session_state.current_page == "Page Name" else "secondary"):
    st.session_state.current_page = "Page Name"
    st.rerun()
```

---

*Last Updated: 2026-01-22*
*Sessions: 1*
