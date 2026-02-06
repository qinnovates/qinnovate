# Claude AI Instructions for TARA

> **TARA**: Telemetry Analysis & Response Automation
> Neural Security Stack for Brain-Computer Interfaces

This file provides instructions for Claude to follow when updating, maintaining, or extending TARA. Read this file at the start of any session involving TARA development.

---

## Quick Reference

| Resource | Location | Purpose |
|----------|----------|---------|
| **Main README** | `README.md` | Public documentation, installation |
| **API Reference** | `API.md` | **Complete API documentation (UPDATE AFTER CHANGES)** |
| **AGENTS.md** | `AGENTS.md` | Learnings from previous sessions |
| **pyproject.toml** | `pyproject.toml` | Package configuration and dependencies |
| **Main App** | `ui/app.py` | Streamlit dashboard entry point |
| **CLI** | `cli.py` | Command-line interface |
| **Core** | `core/` | ONI Framework security primitives |
| **This File** | `CLAUDE.md` | Claude-specific instructions |

---

## Module Architecture

> **Note:** All source code, tests, and visualizations are now consolidated in this folder.

```
tara-nsec-platform/   # Complete package
├── CLAUDE.md                    # Claude AI instructions (this file)
├── AGENTS.md                    # Learnings from previous sessions
├── README.md                    # Public documentation
├── API.md                       # API reference (UPDATE AFTER CODE CHANGES)
├── pyproject.toml               # Package configuration
├── LICENSE                      # Apache 2.0
│
├── tara_mvp/                        # Source code
│   ├── __init__.py              # Package entry point
│   ├── cli.py                   # Command-line interface
│   │
│   ├── core/                    # ONI Framework security primitives
│   │   ├── coherence.py         # Cₛ (Coherence Score) calculation
│   │   ├── layers.py            # 14-layer ONI model (L1-L14)
│   │   ├── firewall.py          # Neural firewall decision matrix
│   │   └── scale_freq.py        # Scale-frequency invariant (f × S ≈ k)
│   │
│   ├── simulation/              # Neural network simulation
│   │   ├── neurons/             # LIF, Izhikevich, Hodgkin-Huxley, Adaptive LIF
│   │   ├── synapses/            # Chemical, Electrical, STDP
│   │   ├── networks/            # Layered, Recurrent, Small-World
│   │   └── engine/              # Simulation execution engine
│   │
│   ├── attacks/                 # Attack simulation & testing
│   │   ├── patterns.py          # Attack pattern definitions
│   │   ├── generator.py         # Signal generation
│   │   ├── scenarios.py         # Multi-stage attack scenarios
│   │   └── simulator.py         # Attack execution engine
│   │
│   ├── nsam/                    # Neural Signal Assurance Monitoring (NSAM)
│   │   ├── events.py            # Event storage
│   │   ├── rules.py             # Detection rules engine
│   │   ├── detector.py          # Anomaly detection
│   │   ├── alerts.py            # Alert management
│   │   └── monitor.py           # Real-time monitoring service
│   │
│   ├── data/                    # Data models & external datasets
│   │   ├── brain_regions.py     # Brain region definitions (10 regions)
│   │   ├── bci_nodes.py         # BCI node network models
│   │   ├── moabb_adapter.py     # MOABB dataset integration (BSD 3-Clause)
│   │   └── export/              # Export functionality (placeholder)
│   │
│   ├── MAIN/           # Neurosecurity (Kohno 2009, Bonaci 2015)
│   │   ├── __init__.py          # ONI neurosecurity wrapper
│   │   └── integration.py       # Kohno rules, NeurosecurityMonitor
│   │
│   ├── visualization/           # Real-time visualization
│   │   ├── components/
│   │   │   ├── brain_topology.py      # 3D brain visualization
│   │   │   └── firewall_pipeline.py   # ONI L8-L14 pipeline visualization
│   │   ├── embeds/
│   │   │   └── html_bridge.py         # ONI-visualizations embedding
│   │   └── themes/
│   │       └── oni_theme.py           # ONI color scheme
│   │
│   ├── ui/                      # Streamlit web interface
│   │   ├── app.py               # Main dashboard (all pages)
│   │   ├── widgets/             # Reusable UI components
│   │   └── pages/               # Page components (if split)
│   │
│   └── persistence/             # Data storage (SQLite, placeholder)
│
├── tests/                       # Unit tests
│   ├── test_coherence.py
│   ├── test_firewall.py
│   ├── test_layers.py
│   ├── test_nsam.py
│   └── test_scale_freq.py
│
└── ../docs/visualizations/              # Interactive HTML visualizations (ONI Suite)
    ├── index.html               # Master launcher
    ├── README.md                # Visualization documentation
    ├── 01-coherence-metric-playground.html
    ├── 02-oni-layer-explorer.html
    ├── 03-neural-killchain-visualizer.html
    ├── 04-nsam-checkpoint-simulator.html
    └── 05-scale-frequency-navigator.html
```

---

## ONI Framework Alignment

### 14-Layer Model

TARA is fully aligned with the ONI 14-layer model:

```
OSI NETWORKING (L1-L7):
  L1:  Physical          - Transmission of raw bits over medium
  L2:  Data Link         - Framing, MAC addressing
  L3:  Network           - Logical addressing and routing
  L4:  Transport         - End-to-end delivery, flow control
  L5:  Session           - Connection lifecycle management
  L6:  Presentation      - Encoding, encryption, compression
  L7:  Application       - User-facing network services

BRIDGE (L8):
  L8:  Neural Gateway    - FIREWALL LOCATION (silicon-biology boundary)

NEURAL/COGNITIVE (L9-L14):
  L9:  Signal Processing - Filtering, amplification, digitization
  L10: Neural Protocol   - Neural data formatting, codecs
  L11: Cognitive Transport - Reliable neural data delivery
  L12: Cognitive Session - Context persistence, working memory
  L13: Semantic          - Meaning construction, intent decoding
  L14: Identity          - Self-model, ethics, continuity of self
```

**Key Principle:**
- **OSI (L1-L7)** answers: *How does data move?*
- **ONI (L8-L14)** answers: *Should it move, can it be trusted, and what does it mean?*

**Authoritative Reference:** See `MAIN/legacy-core/oni-framework/ONI_LAYERS.md` for complete definitions.

### Brain Regions → ONI Layer Mapping

| Region | Full Name | ONI Layer | Domain | MNI Coords | Brodmann |
|--------|-----------|-----------|--------|------------|----------|
| M1 | Primary Motor Cortex | L13 | Semantic | (-35,-20,55) | BA4 |
| S1 | Primary Somatosensory | L12 | Cognitive Session | (-35,-35,50) | BA1-3 |
| PMC | Premotor Cortex | L13 | Semantic | (-45,5,50) | BA6 |
| SMA | Supplementary Motor | L13 | Semantic | (0,-5,60) | BA6 |
| PFC | Prefrontal Cortex | L14 | Identity | (35,45,25) | BA8-12 |
| BROCA | Broca's Area | L14 | Identity | (-50,20,15) | BA44-45 |
| WERNICKE | Wernicke's Area | L14 | Identity | (-55,-55,20) | BA22 |
| V1 | Primary Visual | L12 | Cognitive Session | (0,-85,5) | BA17 |
| A1 | Primary Auditory | L12 | Cognitive Session | (-55,-20,10) | BA41-42 |
| HIPP | Hippocampus | L11 | Cognitive Transport | (-25,-20,-15) | — |

**Layer Mapping Rationale:**
- **L14 (Identity):** Regions central to self, language, executive function (PFC, BROCA, WERNICKE)
- **L13 (Semantic):** Regions translating intention to meaningful action (M1, PMC, SMA)
- **L12 (Cognitive Session):** Sensory processing regions (S1, V1, A1)
- **L11 (Cognitive Transport):** Memory transfer/consolidation (HIPP)

### Neurosecurity — Kohno Threat Taxonomy

| Category | CIA Property | Target Layers | Key Rules |
|----------|--------------|---------------|-----------|
| ALTERATION | Integrity | L13-L14 | signal_injection, command_modification, stimulation_tampering |
| BLOCKING | Availability | L8-L9 | neural_dos, signal_suppression, jamming, motor_lockout |
| EAVESDROPPING | Confidentiality | L11-L14 | cognitive_leakage, memory_extraction, face_recognition_probe |

### Attack Simulator — Neural ATT&CK Tactics

| Tactic | ONI Layers | Techniques Count |
|--------|------------|------------------|
| Reconnaissance | L7-L8 | 3 |
| Initial Access | L8-L9 | 3 |
| Execution | L9-L11 | 3 |
| Persistence | L10-L11 | 2 |
| Defense Evasion | L8-L9 | 2 |
| Collection | L12-L14 | 3 |
| Impact | L11-L14 | 3 |

### Key Formulas

**Coherence Score:** `Cₛ = e^(−(σ²φ + σ²τ + σ²γ))`

**Scale-Frequency Invariant:** `f × S ≈ k`

---

## UI Pages Reference

TARA's Streamlit UI has the following pages:

### Monitoring Pages

| Page | Purpose |
|------|---------|
| **Dashboard** | System status, alerts, BCI nodes, real-time metrics |
| **Brain Topology** | 3D brain visualization with electrode monitoring |
| **Neural Firewall** | ONI L8-L14 validation pipeline |
| **Signal Assurance** | Live metrics, alerts management, event logs |
| **Neurosecurity** | Kohno threat rules, privacy calculator, BCI Anonymizer |

### Data Pages

| Page | Purpose |
|------|---------|
| **Real EEG Data** | MOABB dataset integration, attack injection, coherence benchmarking |

### Simulations Pages

| Page | Purpose |
|------|---------|
| **Neural Simulator** | Brain region security analysis with attacks/defenses |
| **Attack Simulator** | Neural ATT&CK matrix, attack simulation, pew-pew visualization |

### Interactive Visualizations (ONI Suite)

| Page | Purpose | Research Alignment |
|------|---------|-------------------|
| **Coherence Playground** | Real-time Cₛ calculation, waveform comparison | Kohno (2009) signal integrity |
| **ONI Layer Explorer** | Interactive 14-layer model navigation | ONI Framework core model |
| **Kill Chain Visualizer** | Attack propagation across ONI layers | Bonaci (2015) attack patterns |
| **NSAM Checkpoint Sim** | Gamified signal validation training | NSAM validation pipeline |
| **Scale-Frequency Nav** | Temporal scale exploration (fs→hours) | Scale-frequency invariant (f × S ≈ k) |

### Configuration

| Page | Purpose |
|------|---------|
| **Settings** | Thresholds, rules, system parameters |

### Dashboard Structure

```
Dashboard
├── Real-time Signal Monitor (expandable)
│   └── Coherence and Spike Rate charts
├── System Status row
│   ├── Monitor status
│   ├── Active Alerts
│   ├── BCI Nodes (online/total)
│   ├── Network Health
│   └── Firewall Pass Rate
└── Two columns
    ├── Recent Alerts
    └── BCI Node Network (with expandable node details)
```

### Neural Simulator Structure

```
Neural Simulator
├── 3D Brain with region spheres (ONI layer colored)
├── Region selector dropdown
├── ONI Layer Legend
├── Region Details panel
│   ├── Function description
│   ├── ONI layer mapping
│   ├── Neuron types
│   └── Connections
├── Neural Network Visualization (3D neurons)
├── Security Analysis tabs
│   ├── Attack Vectors (per region)
│   └── Defenses (per region)
└── ONI Framework Layer Stack (L5-L14)
```

---

## Update Checklist

When making changes to TARA, ensure:

### Code Changes
- [ ] Update relevant `__init__.py` exports
- [ ] Add/update docstrings
- [ ] Maintain ONI layer alignment
- [ ] Update type hints

### UI Changes
- [ ] Update page routing in `ui/app.py` if adding pages
- [ ] Update sidebar navigation if changing page names
- [ ] Maintain consistent styling with ONI theme
- [ ] Test on localhost:8505

### Documentation Changes
- [ ] Update `README.md` with new features
- [ ] Update architecture diagram if structure changes
- [ ] Update CLI reference if adding commands

### API Documentation (REQUIRED for code changes)
> **CRITICAL:** Update `API.md` whenever public API changes are made.

- [ ] **New classes/functions**: Add to appropriate section in `API.md`
- [ ] **New attack patterns**: Add to Attack Simulation section
- [ ] **New scenarios**: Add to AttackScenario section
- [ ] **New CVSS/Yale items**: Add to Yale Threat Model section
- [ ] **New NSAM features**: Add to NSAM section
- [ ] **New CLI commands**: Add to CLI Reference section
- [ ] **Version changes**: Update Version History table at bottom
- [ ] **Update date**: Change "Last Updated" at bottom of `API.md`

### Data Model Changes
- [ ] Update `data/brain_regions.py` for new regions
- [ ] Update `data/bci_nodes.py` for node changes
- [ ] Update `REGION_SECURITY_DATA` in `ui/app.py` for Neural Simulator

### Before Committing
- [ ] Update `AGENTS.md` with learnings
- [ ] **Update `API.md`** if any public API changed
- [ ] Run `tara ui` to verify UI works
- [ ] Check for import errors
- [ ] Update version in `__init__.py` and `pyproject.toml` if releasing

---

## Naming Conventions

### Files
- Python modules: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### UI Elements
- Page titles: Title Case ("Neural Simulator")
- Section headers: Title Case ("System Status")
- Button labels: Title Case ("Run Simulation")
- Metric labels: Title Case ("Active Alerts")

### ONI Alignment
- Always prefix layer references with "L" (L8, L13, etc.)
- Use full layer names in documentation (Neural Gateway, not just Gateway)
- Map brain regions to correct ONI layers per the table above

---

## Common Tasks

### Adding a New Brain Region

1. Add to `data/brain_regions.py`:
```python
"NEW": BrainRegion(
    abbreviation="NEW",
    name="New Region Name",
    center=(x, y, z),  # MNI coordinates
    radius=10,
    oni_layer=12,
    function="region function",
    category=RegionCategory.SENSORY,
    color="#hex",
)
```

2. Add to `REGION_SECURITY_DATA` in `ui/app.py`:
```python
"NEW": {
    "name": "New Region Name",
    "function": "Description of function",
    "oni_layer": 12,
    "oni_name": "Session",
    "neuron_types": [...],
    "connections": [...],
    "attack_vectors": [...],
    "defenses": [...],
}
```

3. Add to `region_positions` in `_create_brain_3d_with_regions()`

### Adding a New Attack Pattern

1. Add to `attacks/patterns.py`
2. Add to `REGION_SECURITY_DATA` attack_vectors in `ui/app.py`
3. Update `README.md` Attack Patterns table
4. **Update `API.md`** - Add pattern to "Predefined Patterns" table

### Adding a New UI Page

1. Create render function: `render_new_page()`
2. Add to `render_sidebar()` navigation
3. Add routing in `main()` function
4. **Update `API.md`** if page exposes new API functionality

### Updating API Documentation (REQUIRED)

**When to update `API.md`:**
- Adding new public classes, functions, or constants
- Adding new attack patterns or scenarios
- Adding new CVSS scores or Yale threat categories
- Adding new NSAM rules or alerts
- Adding new CLI commands
- Changing function signatures or parameters
- Changing return types or behaviors

**How to update `API.md`:**

1. **Find the appropriate section** (Core, Attacks, Yale/CVSS, NSAM, etc.)

2. **Add class/function documentation:**
```markdown
### NewClassName

Brief description.

\`\`\`python
from tara_mvp import NewClassName

instance = NewClassName(param1=value)
result = instance.method()
\`\`\`

| Parameter | Type | Description |
|-----------|------|-------------|
| `param1` | type | Description |
\`\`\`

3. **Update tables** (Predefined Patterns, Predefined Scenarios, etc.)

4. **Update Version History** at bottom of API.md

5. **Update "Last Updated" date** at bottom of API.md

### Using Neurosecurity Module

The neurosecurity module integrates Kohno (2009) threat taxonomy and Bonaci et al. (2015) BCI privacy research.

**Loading Kohno Rules:**
```python
from tara import NeurosecurityMonitor
from tara.nsam import RuleEngine

monitor = NeurosecurityMonitor()
engine = RuleEngine()
rules_loaded = monitor.load_kohno_rules(engine)
```

**Privacy Score Calculation:**
```python
score = monitor.calculate_privacy_score(
    signal_data=signal,
    detected_erps=["P300", "N170"]
)
# score['score']: 0-1 (higher = more risk)
# score['interpretation']: Human-readable risk level
```

**Threat Classification:**
```python
threat = monitor.classify_threat(metrics)
# Returns: Alteration (integrity), Blocking (availability), Eavesdropping (confidentiality)
```

**Adding New Kohno Rules:**
1. Add to `MAIN/integration.py` in `_build_kohno_rules()`
2. Include `kohno_category` and `cia_mapping` in metadata
3. Tag with "kohno" and the appropriate category
4. Update UI Pages Reference in this file

### Using MOABB Adapter (Real EEG Data)

TARA integrates with [MOABB](https://github.com/NeuroTechX/moabb) (BSD 3-Clause License) for testing against real EEG datasets.

**Installation:**
```bash
pip install oni-tara[moabb]
```

**Loading Real EEG Data:**
```python
from tara.data import MOABBAdapter, is_moabb_available

if is_moabb_available():
    adapter = MOABBAdapter()

    # Load motor imagery dataset
    dataset = adapter.load_dataset("BNCI2014_001")
    signals = adapter.get_signals(dataset, subject=1, max_epochs=10)

    # Each signal is an EEGSignal object
    for signal in signals:
        print(f"Label: {signal.label}, Shape: {signal.data.shape}")
```

**Injecting Attacks for Security Testing:**
```python
# Inject spike attack (ransomware signature)
attacked = adapter.inject_attack(
    signals[0],
    attack_type="spike",     # spike, noise, frequency, phase, dc_shift
    intensity=2.0,
    channels=[0, 1, 2],      # Target specific channels
)

# Compare original vs attacked
print(f"Original max: {signals[0].data.max():.2f}")
print(f"Attacked max: {attacked.attacked.max():.2f}")
```

**Benchmarking Coherence Metric:**
```python
# Benchmark coherence against real signals
results = adapter.benchmark_coherence(signals)
print(f"Clean signal Cₛ: {results['clean_signals']['mean_score']:.3f}")

# With attack detection metrics
attacked_signals = [adapter.inject_attack(s, "spike") for s in signals]
results = adapter.benchmark_coherence(signals, attacked_signals)
print(f"Detection accuracy: {results['detection_metrics']['accuracy']:.2%}")
```

**Available Datasets:**

| Dataset | Paradigm | ONI Relevance |
|---------|----------|---------------|
| BNCI2014_001 | Motor Imagery | Motor cortex (L13) attack detection |
| BNCI2014_002 | Motor Imagery | Longitudinal firewall validation |
| EPFLP300 | P300 | Privacy-sensitive ERP (Kohno threats) |
| SSVEP_Exo | SSVEP | Frequency injection attack vectors |

**Citation Requirement:**
When publishing results using MOABB data, cite:
> Jayaram, V., & Barachant, A. (2018). MOABB: Trustworthy algorithm benchmarking for BCIs. *J Neural Eng*, 15(6), 066011.

---

## Testing

### Manual Testing
```bash
# Launch UI
tara ui --port 8505

# Check each page loads
# Test button interactions
# Verify visualizations render
```

### Unit Tests (when implemented)
```bash
pytest tests/ -v
```

---

## Dependencies

### Core (always installed)
- numpy >= 1.21.0
- scipy >= 1.7.0

### UI (optional)
- streamlit >= 1.28.0
- plotly >= 5.17.0

### Simulation (optional)
- matplotlib >= 3.5.0
- pandas >= 1.4.0

### Full (all features)
- scikit-learn >= 1.0.0

---

## Troubleshooting

### "Module not found" errors
- Check `__init__.py` exports
- Verify PYTHONPATH includes tara parent directory

### UI not loading
- Check Streamlit is installed: `pip install streamlit`
- Kill existing processes: `pkill -f streamlit`
- Restart: `tara ui` or `python -m streamlit run tara_mvp/ui/app.py`

### Visualization not rendering
- Check Plotly is installed: `pip install plotly`
- Check browser console for JavaScript errors

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01 | Initial release with core, simulation, attacks, NSAM |
| 0.2.0 | 2026-01 | Added visualization, brain topology, firewall pipeline |
| 0.3.0 | 2026-01 | Added Neural Simulator with region security analysis |
| 0.4.0 | 2026-01 | Added neurosecurity module (Kohno 2009, Bonaci 2015) |
| 0.5.0 | 2026-01 | Consolidated package structure, integrated ONI Visualization Suite |
| 0.5.1 | 2026-01 | Fixed Layer Explorer interactivity, comprehensive educational content for all 14 layers |
| 0.6.0 | 2026-01 | Major UI enhancements: Neurosecurity page, Real EEG Data page, Neural ATT&CK matrix, pew-pew attack animation |
| 0.8.0 | 2026-01-25 | Bidirectional BCI security, stimulation filtering, MOABB integration tests |
| 0.7.0 | 2026-01-25 | Yale threat model with CVSS v4.0, API.md documentation |

---

*Version: 1.8*
*Last Updated: 2026-01-25*
*For: Claude AI Assistant*
