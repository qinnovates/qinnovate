# TARA - Neural Security Platform

**Telemetry Analysis & Response Automation**

[![PyPI version](https://badge.fury.io/py/oni-tara.svg)](https://badge.fury.io/py/oni-tara)
[![Tests](https://github.com/qinnovates/mindloft/actions/workflows/tests.yml/badge.svg)](https://github.com/qinnovates/mindloft/actions/workflows/tests.yml)
[![Security](https://github.com/qinnovates/mindloft/actions/workflows/security.yml/badge.svg)](https://github.com/qinnovates/mindloft/actions/workflows/security.yml)

TARA is a comprehensive neural security platform for brain-computer interfaces (BCIs). It combines neural network simulation, attack modeling, real-time security monitoring, and interactive visualization in a unified framework aligned with the ONI 14-layer model.

Named after Tara, the Buddhist goddess of protection who guides travelers safely through darkness — with 8 forms protecting against 8 fears, just as TARA protects neural interfaces across all ONI layers.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Reference](#cli-reference)
- [Architecture](#architecture)
- [Dashboard Features](#dashboard-features)
- [Attack Patterns](#attack-patterns)
- [Detection Rules](#detection-rules)
- [Neurosecurity Module](#neurosecurity-module)

---

## Overview

TARA provides:

- **Neural Simulation**: Biologically plausible neural network simulation with LIF, Izhikevich, and Hodgkin-Huxley neuron models
- **Attack Simulation**: Comprehensive attack pattern library for security testing (ransomware, DoS, gateway bypass, etc.)
- **Neural Signal Assurance Monitoring (NSAM)**: Real-time anomaly detection and signal integrity validation
- **Brain Topology Visualization**: 3D brain visualization with electrode monitoring and region analysis
- **Neural Firewall**: ONI-aligned 7-layer (L8-L14) signal validation pipeline with **bidirectional BCI support**
- **Bidirectional BCI Security**: Stimulation command validation with safety bounds, region authorization, and charge density limits
- **Neural Simulator**: Interactive brain region security analysis with attack vectors and defenses
- **BCI Node Network**: Monitoring and connectivity visualization for distributed firewall nodes
- **Unified Dashboard**: Streamlit-based web interface for monitoring, testing, and analysis
- **Neurosecurity Module**: Kohno threat taxonomy (2009) and BCI privacy filtering (Bonaci et al. 2015)

---

## Installation

```bash
# Basic installation
pip install oni-tara

# With web UI support
pip install oni-tara[ui]

# With simulation features
pip install oni-tara[simulation]

# With MOABB datasets (real EEG for security testing)
pip install oni-tara[moabb]

# Full installation (includes MOABB)
pip install oni-tara[full]

# Development installation (from source)
cd MAIN/legacy-core/tara-nsec-platform
pip install -e ".[full,dev]"
```

---

## Quick Start

### Launch the Dashboard

```bash
tara ui
```

The dashboard opens at `http://localhost:8501` with these pages:

| Page | Section | Description |
|------|---------|-------------|
| **Dashboard** | Monitoring | System status, alerts, BCI nodes, real-time metrics |
| **Brain Topology** | Monitoring | 3D brain visualization with electrode monitoring |
| **Neural Firewall** | Monitoring | ONI L8-L14 validation pipeline |
| **Signal Assurance** | Monitoring | Live metrics, alerts management, event logs |
| **Neurosecurity** | Monitoring | Kohno threat rules, privacy calculator, BCI Anonymizer |
| **Real EEG Data** | Data | MOABB dataset integration, attack injection, coherence benchmarking |
| **Neural Simulator** | Simulations | Brain region security analysis |
| **Attack Simulator** | Simulations | Neural ATT&CK matrix, attack simulation, pew-pew visualization |
| **Settings** | Configuration | Thresholds, rules, system parameters |

### Test with Real EEG Data (MOABB)

TARA integrates with [MOABB](https://github.com/NeuroTechX/moabb) (BSD 3-Clause) for testing against real BCI data:

```python
from tara.data import MOABBAdapter, is_moabb_available
from tara import NeuralFirewall, CoherenceMetric

# Check if MOABB is installed
if not is_moabb_available():
    print("Install with: pip install oni-tara[moabb]")
else:
    # Load real EEG dataset
    adapter = MOABBAdapter()
    dataset = adapter.load_dataset("BNCI2014_001")  # Motor imagery
    signals = adapter.get_signals(dataset, subject=1, max_epochs=10)

    # Test coherence metric on real signals
    coherence = CoherenceMetric()
    firewall = NeuralFirewall()

    for signal in signals:
        cs_score = coherence.calculate(signal.data)
        result = firewall.process_signal(signal.to_tara_format())
        print(f"Signal: {signal.label}, Cₛ={cs_score:.3f}, Passed={result}")

    # Inject attack and test detection
    attacked = adapter.inject_attack(signals[0], "spike", intensity=2.0)
    attack_cs = coherence.calculate(attacked.attacked)
    print(f"Attack injected: Cₛ dropped from {cs_score:.3f} to {attack_cs:.3f}")
```

**Available Datasets:**
| Dataset | Paradigm | Subjects | ONI Relevance |
|---------|----------|----------|---------------|
| BNCI2014_001 | Motor Imagery | 9 | Motor cortex (L13) attack detection |
| BNCI2014_002 | Motor Imagery | 14 | Longitudinal firewall validation |
| EPFLP300 | P300 | 8 | Privacy-sensitive ERP (Kohno threats) |
| SSVEP_Exo | SSVEP | 12 | Frequency injection attack vectors |

**Citation:** When publishing results using MOABB data, cite:
> Jayaram, V., & Barachant, A. (2018). MOABB: Trustworthy algorithm benchmarking for BCIs. *J Neural Eng*, 15(6), 066011.

---

### Python API

```python
from tara import NeuralNSAM, AttackSimulator, NeuralFirewall, NeurosecurityMonitor
from tara.simulation import LayeredNetwork

# Create ONI-aligned neural network
network = LayeredNetwork.create_oni_model()

# Initialize Neural Signal Assurance Monitoring
nsam = NeuralNSAM()
session = nsam.start()

# Process incoming metrics
metrics = {"coherence": 0.75, "spike_rate": 50.0}
result = nsam.process(metrics)

if result and result.detected:
    print(f"Anomaly detected: {result.anomaly_type}")

# Stop monitoring
session = nsam.stop()
print(f"Processed {session.samples_processed} samples")
```

### Run Attack Simulations

```python
from tara.attacks import AttackSimulator
from tara.attacks.scenarios import get_scenario

simulator = AttackSimulator()
scenario = get_scenario("ransomware")

result = simulator.run_scenario(scenario)
print(f"Detection rate: {result.detection_rate:.1%}")
print(f"Block rate: {result.block_rate:.1%}")
```

### Bidirectional BCI Security

TARA supports bidirectional BCIs that both READ from and WRITE (stimulate) the brain:

```python
from tara import NeuralFirewall, StimulationCommand, FlowDirection

# Create firewall with stimulation safety bounds
firewall = NeuralFirewall(
    # READ settings
    threshold_high=0.6,
    threshold_low=0.3,
    # WRITE (stimulation) settings
    stim_amplitude_bounds=(0.0, 3000.0),   # 0-3 mA
    stim_frequency_bounds=(1.0, 200.0),    # 1-200 Hz
    charge_density_limit=25.0,              # uC/cm^2 (Shannon limit)
    authorized_regions={"M1", "S1", "PMC"}, # Only authorized regions
    stim_rate_limit=10,                     # Max 10 commands/second
)

# Validate a stimulation command
stim_cmd = StimulationCommand(
    target_region="M1",
    amplitude_uA=1000.0,    # 1 mA
    frequency_Hz=100.0,
    pulse_width_us=200.0,
    authenticated=True,
)

result = firewall.filter_stimulation(stim_cmd)
if result.accepted:
    print("Stimulation approved")
else:
    print(f"Rejected: {result.reason}")
    for check, passed in result.safety_checks.items():
        print(f"  {'✓' if passed else '✗'} {check}")

# Check bidirectional flow stats
stats = firewall.get_stats()
print(f"Flow direction: {stats['flow_direction']}")
```

**Safety Bounds (based on Shannon 1992, Merrill 2005):**

| Parameter | Default Range | Purpose |
|-----------|---------------|---------|
| Amplitude | 0-5 mA | Prevent tissue damage |
| Frequency | 0.1-500 Hz | Physiological range |
| Pulse Width | 50-1000 μs | Balance efficacy/safety |
| Charge Density | <30 μC/cm²/phase | Shannon limit (k=1.5) |

---

## CLI Reference

```bash
# Launch web dashboard
tara ui --port 8501

# Run neural simulation
tara simulate --network oni --neurons 200 --duration 1000

# Execute attack scenario
tara attack --scenario ransomware --intensity 0.7

# Start monitoring
tara monitor --realtime

# List available resources
tara list patterns
tara list scenarios
tara list rules
```

---

## Architecture

TARA follows the ONI (Organic Neurocomputing Interface) 14-layer model:

```
BIOLOGICAL DOMAIN (L1-L7):
  L1-L7: Molecular → Behavioral (brain-side processing)

BRIDGE (L8):
  L8: Neural Gateway (primary security boundary - FIREWALL LOCATION)

SILICON DOMAIN (L9-L14):
  L9:  Signal Processing  - ADC, filtering, amplification
  L10: Protocol           - Data formatting, transmission rules
  L11: Transport          - Encryption, reliable delivery
  L12: Session            - Connection management, state tracking
  L13: Presentation       - Data interpretation, motor intention
  L14: Application        - End-user interfaces, identity & ethics
```

### Brain Regions → ONI Layer Mapping (Neural Simulator)

The Neural Simulator includes **10 brain regions** strategically selected for their relevance to BCI security. Each region represents a critical attack surface in modern brain-computer interfaces.

#### Quick Reference

| Region | Name | ONI Layer | Domain | BCI Application |
|--------|------|-----------|--------|-----------------|
| M1 | Primary Motor Cortex | L13 | Semantic | Motor BCIs (Neuralink, BrainGate) |
| S1 | Primary Somatosensory | L12 | Cognitive Session | Sensory feedback, closed-loop control |
| PMC | Premotor Cortex | L13 | Semantic | Movement prediction |
| SMA | Supplementary Motor Area | L13 | Semantic | Complex movement sequences |
| PFC | Prefrontal Cortex | L14 | Identity | Cognitive state, attention, intent |
| BROCA | Broca's Area | L14 | Identity | Speech BCIs (Edward Chang lab) |
| WERNICKE | Wernicke's Area | L14 | Identity | Language comprehension BCIs |
| V1 | Primary Visual Cortex | L12 | Cognitive Session | Visual prosthetics (Second Sight Orion) |
| A1 | Primary Auditory Cortex | L12 | Cognitive Session | Cochlear implant integration |
| HIPP | Hippocampus | L11 | Cognitive Transport | Memory prosthetics (DARPA RAM) |

#### ONI Layer Hierarchy Visualization

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ONI BIOLOGICAL DOMAIN                            │
├─────────────────────────────────────────────────────────────────────────┤
│  L14 │ Identity & Ethics  │ PFC, BROCA, WERNICKE                       │
│      │                    │ Executive function, language, self-model    │
├──────┼────────────────────┼─────────────────────────────────────────────┤
│  L13 │ Semantic           │ M1, PMC, SMA                                │
│      │                    │ Motor intention → meaningful action         │
├──────┼────────────────────┼─────────────────────────────────────────────┤
│  L12 │ Cognitive Session  │ S1, V1, A1                                  │
│      │                    │ Sensory processing, perceptual context      │
├──────┼────────────────────┼─────────────────────────────────────────────┤
│  L11 │ Cognitive Transport│ HIPP                                        │
│      │                    │ Memory encoding/consolidation               │
├──────┴────────────────────┴─────────────────────────────────────────────┤
│  L8  │ Neural Gateway     │ ═══ FIREWALL BOUNDARY ═══                   │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Region Details

| Region | MNI Coordinates | Brodmann Area | Key Security Threats |
|--------|-----------------|---------------|----------------------|
| **M1** | (-35, -20, 55) | BA4 | Motor hijacking, motor lockout |
| **S1** | (-35, -35, 50) | BA1-3 | Sensory flooding, sensory deprivation |
| **PMC** | (-45, 5, 50) | BA6 | Movement planning disruption |
| **SMA** | (0, -5, 60) | BA6 | Sequence coordination attacks |
| **PFC** | (35, 45, 25) | BA8-12, 44-47 | Decision manipulation, identity erosion |
| **BROCA** | (-50, 20, 15) | BA44-45 | Speech hijacking, expressive aphasia |
| **WERNICKE** | (-55, -55, 20) | BA22 | Comprehension disruption |
| **V1** | (0, -85, 5) | BA17 | Visual injection, phosphene attacks |
| **A1** | (-55, -20, 10) | BA41-42 | Auditory hallucination injection |
| **HIPP** | (-25, -20, -15) | — (subcortical) | False memory implant, memory erasure |

**Sources:** MNI coordinates verified against neuroimaging meta-analyses ([PMC2034289](https://pmc.ncbi.nlm.nih.gov/articles/PMC2034289/)). Functional mappings based on established neuroanatomy.

---

### Neurosecurity Module — Kohno Threat Taxonomy

TARA implements the foundational **Denning, Matsuoka & Kohno (2009)** neurosecurity threat taxonomy, the first academic framework for BCI security.

> "Neurosecurity is protection of the confidentiality, integrity, and availability of neural devices from malicious parties with the goal of preserving the safety of a person's neural mechanisms, neural computation, and free will."
> — Denning et al. (2009)

#### Threat Categories → CIA Triad Mapping

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    KOHNO THREAT TAXONOMY (2009)                          │
├────────────────┬─────────────────┬───────────────────────────────────────┤
│   CATEGORY     │   CIA PROPERTY  │   DESCRIPTION                         │
├────────────────┼─────────────────┼───────────────────────────────────────┤
│  ALTERATION    │   Integrity     │ Unauthorized modification of neural   │
│                │                 │ signals, commands, or stimulation     │
│                │                 │ Target: L13-L14 (Semantic/Identity)   │
├────────────────┼─────────────────┼───────────────────────────────────────┤
│  BLOCKING      │   Availability  │ Suppression or denial of neural       │
│                │                 │ signals, causing loss of function     │
│                │                 │ Target: L8-L9 (Gateway/Signal)        │
├────────────────┼─────────────────┼───────────────────────────────────────┤
│  EAVESDROPPING │ Confidentiality │ Unauthorized extraction of cognitive  │
│                │                 │ states, memories, or identity info    │
│                │                 │ Target: L11-L14 (Cognitive/Identity)  │
└────────────────┴─────────────────┴───────────────────────────────────────┘
```

#### Kohno Detection Rules (11 Rules)

| Rule ID | Category | Severity | Detection Method | Target |
|---------|----------|----------|------------------|--------|
| `kohno_signal_injection` | ALTERATION | CRITICAL | Coherence mismatch + external origin | L8-L9 |
| `kohno_command_modification` | ALTERATION | CRITICAL | Motor command checksum mismatch | L13-L14 |
| `kohno_stimulation_tampering` | ALTERATION | CRITICAL | Stimulation >10mA threshold | L9 |
| `kohno_neural_dos` | BLOCKING | CRITICAL | spike_rate >500 AND coherence <0.3 | L8 |
| `kohno_signal_suppression` | BLOCKING | HIGH | amplitude <0.01 | L9 |
| `kohno_jamming` | BLOCKING | CRITICAL | noise_floor >0.8 AND SNR <1.0 | L8 |
| `kohno_motor_lockout` | BLOCKING | CRITICAL | Motor output blocked | L13 |
| `kohno_cognitive_leakage` | EAVESDROPPING | CRITICAL | P300 ERP + external query pattern | L12-L14 |
| `kohno_memory_extraction` | EAVESDROPPING | CRITICAL | N400 ERP + hippocampus activation | L11 |
| `kohno_face_recognition_probe` | EAVESDROPPING | HIGH | N170 ERP + visual stimulus | L12 |
| `kohno_emotional_inference` | EAVESDROPPING | HIGH | Amygdala activation pattern | L14 |

#### BCI Privacy — Bonaci et al. (2015)

TARA includes privacy protections based on research showing that **BCI applications can extract private information without user awareness**.

> "Most applications have unrestricted access to users' brainwave signals and can easily extract private information about their users without them even noticing."
> — Bonaci et al. (2015)

##### ERP Privacy Risk Matrix

| ERP Component | Latency | Privacy Risk | Information Leaked |
|---------------|---------|--------------|-------------------|
| **P300** | ~300ms | 🔴 CRITICAL | Recognition, secrets, PIN codes |
| **N170** | ~170ms | 🔴 CRITICAL | Face recognition, known persons |
| **N400** | ~400ms | 🟠 HIGH | Semantic knowledge, memory content |
| **ERN** | ~100ms | 🟡 MEDIUM | Error awareness, decision confidence |
| **LRP** | ~200ms | 🟢 LOW | Motor preparation (allowed for BCIs) |
| **CNV** | ~1000ms | 🟢 LOW | Anticipation (allowed for BCIs) |

##### BCI Anonymizer Function

```
Raw EEG Signal → [Privacy Filter] → Anonymized Signal
                       │
                       ├─ BLOCK: P300, N170, N400 (privacy-sensitive)
                       └─ ALLOW: LRP, CNV (motor commands only)
```

**Patent Status:** The BCI Anonymizer patent (US20140228701A1) was **abandoned** — concepts freely available for implementation.

**Sources:** [Kohno (2009)](https://pubmed.ncbi.nlm.nih.gov/19569895/), [Bonaci (2015)](https://www.semanticscholar.org/paper/App-Stores-for-the-Brain-:-Privacy-and-Security-in-Bonaci-Calo/9ce645240e6e965cc160dfb290504c7fc7d7ebe5), [UW BioRobotics BCI Security](https://wp.ece.uw.edu/brl/neural-engineering/bci-security/)

---

### Attack Simulator — Neural ATT&CK Matrix

The Attack Simulator implements a **MITRE ATT&CK-inspired framework** adapted for neural interfaces, mapping adversary tactics and techniques to the ONI layer model.

> MITRE ATT&CK organizes adversary behavior into tactics (objectives) and techniques (methods). TARA's Neural ATT&CK applies this methodology to brain-computer interfaces.

#### Neural ATT&CK Matrix (10 Tactics × 46 Techniques)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              NEURAL ATT&CK MATRIX                                       │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬──────────────────┤
│RECONNAISSANCE│INITIAL ACCESS│ EXECUTION  │ PERSISTENCE │DEF. EVASION │ COLLECTION       │
│   (L7-L8)   │   (L8-L9)   │  (L9-L11)  │  (L10-L11)  │   (L8-L9)   │   (L12-L14)      │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┼──────────────────┤
│Signal       │Electrode    │Signal       │Pattern      │Coherence    │ERP               │
│Profiling    │Compromise   │Injection    │Lock         │Mimicry      │Harvesting        │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┼──────────────────┤
│Side-Channel │RF           │Protocol     │Memory       │Gradual      │Cognitive         │
│Analysis     │Exploitation │Manipulation │Implant      │Drift        │Capture           │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┼──────────────────┤
│Network      │Firmware     │Command      │             │             │Memory            │
│Mapping      │Backdoor     │Hijacking    │             │             │Extraction        │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴──────────────────┘
                                                                              │
                                    ┌─────────────────────────────────────────┘
                                    │
                              ┌─────┴─────┐
                              │  IMPACT   │
                              │ (L11-L14) │
                              ├───────────┤
                              │Neural DoS │
                              ├───────────┤
                              │Motor      │
                              │Hijacking  │
                              ├───────────┤
                              │Identity   │
                              │Erosion    │
                              └───────────┘
```

#### Tactic Definitions (Aligned with MITRE ATT&CK)

| Tactic | Objective | ONI Layers | Example Techniques |
|--------|-----------|------------|-------------------|
| **Reconnaissance** | Gather information for attack planning | L7-L8 | Signal profiling, side-channel analysis |
| **Initial Access** | Gain entry to the BCI system | L8-L9 | Electrode compromise, RF exploitation |
| **Execution** | Run malicious neural signals | L9-L11 | Signal injection, command hijacking |
| **Persistence** | Maintain long-term access | L10-L11 | Pattern lock, memory implant |
| **Defense Evasion** | Avoid detection by NSAM | L8-L9 | Coherence mimicry, gradual drift |
| **Collection** | Extract neural data | L12-L14 | ERP harvesting, cognitive capture |
| **Impact** | Cause harm to the user | L11-L14 | Neural DoS, motor hijacking, identity erosion |

#### Attack Patterns (8 Predefined)

| Pattern | Type | Target Layer | Intensity | Signature |
|---------|------|--------------|-----------|-----------|
| `phase_jitter` | Phase Disruption | L8 | 0.7 | Timing jitter in gamma band |
| `amplitude_surge` | Amplitude Manipulation | L9 | 0.8 | 10x amplitude spikes |
| `desync_wave` | Desynchronization | L3 | 0.6 | Multi-frequency phase chaos |
| `neural_ransomware` | Ransomware | L6 | 0.9 | Pattern suppression + override |
| `dos_flood` | DoS Flooding | L8 | 1.0 | High-rate spike flood |
| `gateway_bypass` | Layer 8 Gateway | L8 | 0.6 | Coherence mimicry → drift |
| `replay_attack` | Signal Replay | L8 | 0.5 | Captured signal repetition |
| `side_channel_leak` | Side Channel | L9 | 0.3 | Timing/power analysis |

#### Attack Scenarios (5 Predefined)

| Scenario | Severity | Stages | Duration | Target Layers |
|----------|----------|--------|----------|---------------|
| **Neural Ransomware Campaign** | 🔴 CRITICAL | 4 | 6.8s | L6, L8, L9 |
| **Gateway Infiltration** | 🟠 HIGH | 3 | 4.7s | L8, L9, L10 |
| **Denial of Service** | 🟠 HIGH | 2 | 5.6s | L8, L9 |
| **Man-in-the-Middle** | 🔴 CRITICAL | 3 | 5.2s | L8, L10, L11 |
| **Stealth Reconnaissance** | 🟡 MEDIUM | 1 | 5.0s | L8, L9 |

#### Attack → ONI Layer Coverage Map

```
Layer   │ Recon │ Access │ Execute │ Persist │ Evade │ Collect │ Impact │
────────┼───────┼────────┼─────────┼─────────┼───────┼─────────┼────────┤
L14     │       │        │         │         │       │    ●    │   ●    │ Identity
L13     │       │        │    ●    │         │       │    ●    │   ●    │ Semantic
L12     │       │        │         │         │       │    ●    │   ●    │ Session
L11     │       │        │    ●    │    ●    │       │    ●    │   ●    │ Transport
L10     │       │        │    ●    │    ●    │       │         │        │ Protocol
L9      │   ●   │   ●    │    ●    │         │   ●   │         │        │ Signal
L8      │   ●   │   ●    │    ●    │         │   ●   │         │        │ Gateway
L7      │   ●   │        │         │         │       │         │        │ Application
────────┴───────┴────────┴─────────┴─────────┴───────┴─────────┴────────┘
```

**Sources:** [MITRE ATT&CK](https://attack.mitre.org/), [BCI Security Research 2024](https://arxiv.org/abs/2508.12571), [Yale BCI Security Study](https://news.yale.edu/2025/07/23/study-offers-measures-safeguarding-brain-implants)

---

### Components

```
tara_mvp/
├── core/                  # ONI Framework security primitives
│   ├── coherence.py       # Coherence metric (Cₛ) calculation
│   ├── layers.py          # 14-layer model implementation
│   ├── firewall.py        # Neural firewall with decision matrix
│   └── scale_freq.py      # Scale-frequency invariant (f × S ≈ k)
│
├── simulation/            # Neural network simulation
│   ├── neurons/           # LIF, Izhikevich, Hodgkin-Huxley, Adaptive LIF
│   ├── synapses/          # Chemical, Electrical, STDP
│   ├── networks/          # Layered, Recurrent, Small-World
│   └── engine/            # Simulation execution engine
│
├── attacks/               # Attack simulation
│   ├── patterns.py        # Attack pattern definitions
│   ├── generator.py       # Attack signal generation
│   ├── scenarios.py       # Multi-stage attack scenarios
│   └── simulator.py       # Attack execution engine
│
├── nsam/                  # Neural Signal Assurance Monitoring (NSAM)
│   ├── events.py          # Event storage and management
│   ├── rules.py           # Detection rules engine
│   ├── detector.py        # Anomaly detection algorithms
│   ├── alerts.py          # Alert management
│   └── monitor.py         # Real-time monitoring
│
├── data/                  # Data models
│   ├── brain_regions.py   # Brain region definitions (10 regions)
│   └── bci_nodes.py       # BCI node network models
│
├── MAIN/         # Neurosecurity integration
│   ├── __init__.py        # ONI neurosecurity wrapper
│   └── integration.py     # Kohno rules, NeurosecurityMonitor
│
├── visualization/         # Real-time visualization
│   ├── components/
│   │   ├── brain_topology.py      # 3D brain visualization
│   │   └── firewall_pipeline.py   # ONI L8-L14 pipeline
│   ├── embeds/
│   │   └── html_bridge.py         # ONI-visualizations embedding
│   └── themes/
│       └── oni_theme.py           # ONI color scheme
│
├── ui/                    # Web interface
│   └── app.py             # Streamlit dashboard
│
└── cli.py                 # Command-line interface
```

---

## Dashboard Features

### Dashboard Page
- **Real-time Signal Monitor**: Coherence and spike rate charts (expandable)
- **System Status**: Monitor status, alerts, BCI nodes, network health, firewall pass rate
- **Recent Alerts**: Color-coded alert feed with severity levels
- **BCI Node Network**: Interactive topology visualization with node details

### Brain Topology Page
- **3D Brain Visualization**: Transparent brain mesh with electrode markers
- **Region Highlighting**: Click to focus on specific brain regions
- **Electrode Metrics**: Color-coded by spike rate, impedance, SNR, or status
- **Thread Visualization**: Electrode thread paths through cortex

### Neural Firewall Page
- **ONI L8-L14 Pipeline**: 7-checkpoint validation pipeline
- **Signal Processing**: Process signals through each checkpoint
- **Pass/Block Statistics**: Per-checkpoint pass rates and block counts
- **Checkpoint Details**: Threshold values and validation rules

### Neural Simulator Page
- **3D Brain with Regions**: Color-coded by ONI layer (L11-L14)
- **Region Security Analysis**: Function, attack vectors, defenses per region
- **Neuron Network Visualization**: 3D neuron connections within regions
- **ONI Layer Stack**: Visual representation of full layer model

### Attack Simulator Page
- **Neural ATT&CK Matrix**: MITRE-style grid with 10 tactics and 46 techniques mapped to ONI layers
- **Attack Simulation**: Configure and launch attacks with intensity/duration controls
- **Pew-Pew Visualization**: Real-time attack packet animation across ONI layers with L8 shield effects
- **Attack Timeline**: Stage-by-stage visualization with detection/block status
- **Detection Metrics**: Detection rate, block rate, response time, impact score
- **Report Export**: Download attack simulation reports

### Neurosecurity Page
- **Kohno Threat Rules**: 11 threat rules across ALTERATION, BLOCKING, EAVESDROPPING categories
- **Privacy Calculator**: Calculate privacy risk based on detected ERPs (P300, N170, N400, etc.)
- **BCI Anonymizer Demo**: Before/after visualization of privacy-preserving signal transformation
- **Threat Classifier**: Real-time threat categorization based on signal metrics

### Real EEG Data Page
- **MOABB Integration**: Load real EEG datasets (BNCI2014_001, EPFLP300, etc.)
- **Attack Injection**: Inject spike, noise, frequency, phase, dc_shift attacks into real signals
- **Coherence Benchmark**: Test detection accuracy with precision, recall, F1 metrics

---

## Attack Patterns

TARA includes these predefined attack patterns:

| Pattern | Type | Target | Description |
|---------|------|--------|-------------|
| `phase_jitter` | Phase Disruption | L8 | Timing jitter to disrupt coherence |
| `amplitude_surge` | Amplitude Manipulation | L9 | Sudden amplitude spikes |
| `desync_wave` | Desynchronization | L3 | Disrupt neural synchrony |
| `neural_ransomware` | Ransomware | L6 | Lock neural patterns |
| `dos_flood` | DoS Flooding | L8 | Overwhelm signal processing |
| `gateway_bypass` | Layer 8 Gateway | L8 | Bypass firewall validation |
| `replay_attack` | Signal Replay | L8 | Replay captured signals |
| `side_channel_leak` | Side Channel | L9 | Information leakage via timing |

### Region-Specific Attack Vectors

| Region | Attack | Severity | Description |
|--------|--------|----------|-------------|
| M1 | Motor Hijacking | CRITICAL | Unauthorized motor commands |
| M1 | Motor Lockout | CRITICAL | Signal suppression causing paralysis |
| PFC | Decision Manipulation | CRITICAL | Influencing decision-making |
| PFC | Identity Erosion | CRITICAL | Long-term personality alteration |
| BROCA | Speech Hijacking | CRITICAL | Forcing unintended speech |
| HIPP | False Memory Implant | CRITICAL | Creating fabricated memories |
| HIPP | Memory Erasure | CRITICAL | Disrupting memory consolidation |

---

## Detection Rules

Predefined NSAM detection rules:

| Rule | Type | Action |
|------|------|--------|
| `coherence_low` | Threshold | Alert when Cₛ < 0.5 |
| `coherence_critical` | Threshold | Block when Cₛ < 0.3 |
| `spike_surge` | Threshold | Alert on spike rate > 200 Hz |
| `dos_signature` | Signature | Detect DoS attack pattern |
| `ransomware_signature` | Signature | Detect ransomware pattern |
| `gateway_bypass` | Signature | Detect bypass attempts |

---

## Neurosecurity Module

TARA includes a neurosecurity module implementing foundational BCI security research:

### Kohno Threat Taxonomy (2009)

Based on Denning, Matsuoka, & Kohno's seminal neurosecurity research, TARA detects three fundamental threat categories:

| Category | CIA Property | Description | Example Attacks |
|----------|--------------|-------------|-----------------|
| **Alteration** | Integrity | Unauthorized signal modification | Signal injection, command tampering, stimulation manipulation |
| **Blocking** | Availability | Denial or suppression of signals | DoS flooding, signal suppression, jamming, motor lockout |
| **Eavesdropping** | Confidentiality | Unauthorized information extraction | Cognitive leakage, memory extraction, face recognition probes |

### Kohno Detection Rules

| Rule | Category | Severity | Description |
|------|----------|----------|-------------|
| `kohno_signal_injection` | Alteration | Critical | Detects unauthorized signal injection |
| `kohno_command_modification` | Alteration | Critical | Detects tampering with motor commands |
| `kohno_stimulation_tampering` | Alteration | Critical | Detects unsafe stimulation parameters |
| `kohno_neural_dos` | Blocking | Critical | Detects signal flooding attacks |
| `kohno_signal_suppression` | Blocking | High | Detects malicious signal blocking |
| `kohno_jamming` | Blocking | Critical | Detects RF/EM jamming |
| `kohno_motor_lockout` | Blocking | Critical | Detects motor signal suppression |
| `kohno_cognitive_leakage` | Eavesdropping | Critical | Detects cognitive state extraction |
| `kohno_memory_extraction` | Eavesdropping | Critical | Detects memory content extraction |
| `kohno_face_recognition_probe` | Eavesdropping | High | Detects N170-based face probes |
| `kohno_emotional_inference` | Eavesdropping | High | Detects emotional state extraction |
| `kohno_side_channel` | Eavesdropping | High | Detects timing/power side channels |

### BCI Privacy Filtering

Inspired by Bonaci et al. (2015) research on BCI privacy, TARA includes:

- **Privacy Score Calculator**: Quantifies information leakage risk (0-1 scale)
- **BCI Anonymizer**: Filters privacy-sensitive ERP components while preserving motor commands
- **ERP Classification**: P300, N170, N400, ERN, LRP, CNV component identification

### Usage Example

```python
from tara import NeurosecurityMonitor, create_kohno_rules
from tara.nsam import RuleEngine

# Initialize neurosecurity monitor
monitor = NeurosecurityMonitor()

# Load Kohno rules into NSAM
engine = RuleEngine()
rules_loaded = monitor.load_kohno_rules(engine)
print(f"Loaded {rules_loaded} Kohno rules")

# Calculate privacy score
score = monitor.calculate_privacy_score(
    signal_data=[0.1, 0.2, 0.3, ...],
    detected_erps=["P300", "N170"]
)
if score:
    print(f"Privacy Risk: {score['score']:.2f}")
    print(f"Interpretation: {score['interpretation']}")

# Classify threat based on metrics
threat = monitor.classify_threat({
    "spike_rate": 600,
    "coherence": 0.2,
    "signal_entropy": 0.95,
})
if threat and threat['threats_detected']:
    for t in threat['threats']:
        print(f"Detected: {t['type']} ({t['category']})")
```

### References

- Denning, T., Matsuoka, Y., & Kohno, T. (2009). Neurosecurity: Security and privacy for neural devices. *Neurosurgical Focus*, 27(1), E7.
- Bonaci, T., Calo, R., & Chizeck, H. J. (2015). App stores for the brain: Privacy and security in brain-computer interfaces. *IEEE Technology and Society Magazine*, 34(2), 32-39.

**Note on BCI Anonymizer Patent:** The related patent application (US20140228701A1) was **abandoned** and never granted. The concepts from the academic research are freely available for implementation.

---

## API Reference

### Core Classes

```python
# Coherence calculation
from tara import calculate_cs
cs = calculate_cs(phase_data, amplitude_data, frequency_data)

# Neural firewall
from tara import NeuralFirewall
firewall = NeuralFirewall(threshold=0.5)
decision = firewall.evaluate(signal)

# Attack simulation
from tara import AttackSimulator, AttackPattern
simulator = AttackSimulator(dt=0.1, seed=42)

# Neural Signal Assurance Monitoring
from tara import NeuralNSAM, AlertLevel
nsam = NeuralNSAM()
nsam.on_alert(lambda a: print(f"Alert: {a.title}"))

# Neurosecurity (Kohno + Privacy)
from tara import NeurosecurityMonitor, create_kohno_rules
monitor = NeurosecurityMonitor()
privacy = monitor.calculate_privacy_score(signal_data, detected_erps=["P300"])
```

### Simulation Classes

```python
from tara.simulation import (
    LIFNeuron,
    IzhikevichNeuron,
    LayeredNetwork,
    RecurrentNetwork,
    Simulator,
)
```

### Data Models

```python
from tara.data import (
    BrainRegion,
    BRAIN_REGIONS,
    Electrode,
    ElectrodeThread,
    ElectrodeArray,
    BCINode,
    BCINodeNetwork,
    create_demo_network,
)
```

### Visualization

```python
from tara.visualization.components import (
    BrainTopologyVisualization,
    FirewallPipelineVisualization,
    NeuralFirewall,
)
from tara.visualization.themes import ONI_COLORS, apply_oni_theme
```

---

## Requirements

- Python 3.9+
- NumPy >= 1.21.0
- SciPy >= 1.7.0

Optional:
- Streamlit >= 1.28.0 (for UI)
- Plotly >= 5.17.0 (for visualizations)
- Matplotlib >= 3.5.0 (for simulation plots)
- Pandas >= 1.4.0 (for data manipulation)
- scikit-learn >= 1.0.0 (for anomaly detection)

---

## Development

### Project Structure

```
tara_mvp/
├── CLAUDE.md        # Claude AI instructions for updates
├── AGENTS.md        # Learnings from development sessions
├── README.md        # This file
├── pyproject.toml   # Package configuration
└── tests/           # Unit tests
```

### Running Locally

```bash
# Install in development mode
pip install -e ".[full,dev]"

# Run UI
python -m streamlit run tara_mvp/ui/app.py --server.port 8505

# Run tests
pytest tests/ -v
```

### Contributing

See `CLAUDE.md` for development conventions and update procedures.

---

## Documentation & Resources

**Full documentation on GitHub:**

| Resource | Description |
|----------|-------------|
| [ONI Framework Wiki](https://github.com/qinnovates/mindloft/blob/main/MAIN/legacy-core/INDEX.md) | Central hub — navigation, dependencies, roadmap |
| [TARA Developer Guide](https://github.com/qinnovates/mindloft/blob/main/MAIN/legacy-core/tara-nsec-platform/CLAUDE.md) | Development conventions, architecture details |
| [14-Layer Model Reference](https://github.com/qinnovates/mindloft/blob/main/MAIN/legacy-core/oni-framework/ONI_LAYERS.md) | Complete ONI layer specification |
| [Academic Landscape](https://github.com/qinnovates/mindloft/blob/main/MAIN/legacy-core/ACADEMIC_LANDSCAPE.md) | Research foundation, key papers |
| [Interactive Demos](https://qinnovates.github.io/ONI/visualizations/) | Browser-based learning tools |

**Related packages:**

| Package | Purpose | Install |
|---------|---------|---------|
| [oni-framework](https://pypi.org/project/oni-framework/) | Core API library (coherence, firewall, layers) | `pip install oni-framework` |
| [oni-academy](https://pypi.org/project/oni-academy/) | Educational platform, tutorials | `pip install oni-academy` |

---

## License

Apache 2.0 License

---

## Citation

If you use TARA in your research, please cite:

```bibtex
@software{tara2026,
  title={TARA: Telemetry Analysis & Response Automation},
  author={Qi, Kevin L.},
  year={2026},
  url={https://github.com/qinnovates/mindloft}
}
```

---

## Changelog

### v0.8.0 (2026-01-25)
- **Bidirectional BCI Security**:
  - Added `FlowDirection` enum (READ/WRITE/BIDIRECTIONAL)
  - Added `StimulationCommand` and `StimulationResult` dataclasses
  - Added `filter_stimulation()` method to NeuralFirewall with 7 safety checks
  - Safety bounds based on Shannon (1992) and Merrill (2005): charge density, amplitude, frequency limits
  - Region authorization and rate limiting for stimulation commands
- **MOABB Integration Tests**:
  - Added 42 tests for MOABB dataset adapter
  - Tests cover all 5 datasets (BNCI2014_001, BNCI2014_002, EPFLP300, SSVEP_Exo, Weibo2014)
  - Tests cover all 5 attack types (spike, noise, frequency, phase, dc_shift)
  - Coherence benchmarking with detection metrics
  - Uses mock data for CI/CD without requiring actual downloads
- **Stimulation Security Tests**:
  - Added 32 tests for stimulation command validation
  - Tests for safety bounds, region authorization, rate limiting
  - Comprehensive edge case coverage
- **CI/CD Pipeline**:
  - Updated tests.yml with Python 3.9-3.12 matrix and macOS support
  - Added security.yml with Bandit, Safety, and CodeQL scanning
  - Weekly scheduled security scans

### v0.6.1 (2026-01-25)
- **Documentation Overhaul**:
  - Added comprehensive Neural Simulator brain region documentation with MNI coordinates and Brodmann areas
  - Added detailed Neurosecurity module documentation with Kohno (2009) threat taxonomy
  - Added Neural ATT&CK Matrix documentation with 10 tactics and 46 techniques
  - Added visual ASCII diagrams for ONI layer hierarchy and attack coverage maps
  - Added ERP privacy risk matrix with component-level analysis
  - Cross-referenced all mappings with peer-reviewed neuroscience literature
  - Verified MNI coordinates against neuroimaging meta-analyses

### v0.6.0 (2026-01-24)
- **Major UI Enhancements**:
  - Renamed "Testing" section to "Simulations" in navigation
  - Renamed "Attack Testing" to "Attack Simulator"
  - Added new "Data" section in navigation
- **New Neurosecurity Page** (under Monitoring):
  - Kohno threat rules grid (11 rules: ALTERATION/BLOCKING/EAVESDROPPING)
  - Privacy score calculator with ERP checkboxes (P300, N170, N400, ERN, LPP, MMN, CNV, SSVEP)
  - BCI Anonymizer demo with before/after visualization
  - Threat classifier with metric inputs
- **New Real EEG Data Page** (under Data):
  - MOABB dataset selector (5 datasets: BNCI2014_001, BNCI2014_002, EPFLP300, SSVEP_Exo, Weibo2014)
  - Subject and epoch controls
  - Attack injection (5 types: spike, noise, frequency, phase, dc_shift)
  - Coherence benchmark with detection metrics (accuracy, precision, recall, F1)
- **Attack Simulator Enhancements**:
  - Neural ATT&CK Matrix with 10 tactics and 46 techniques mapped to ONI layers
  - Pew-pew attack animation with L8 shield effect
  - Attack report export capability
- Updated documentation (README.md, CLAUDE.md)

### v0.5.1 (2026-01-24)
- Fixed Layer Explorer interactivity
- Added comprehensive educational content for all 14 ONI layers

### v0.5.0 (2026-01-24)
- Consolidated package structure
- Integrated ONI Visualization Suite

### v0.4.0 (2026-01-23)
- Added neurosecurity module with Kohno threat taxonomy (2009)
- Added 12 Kohno-based detection rules for NSAM
- Added BCI privacy filtering (Bonaci et al. 2015)
- Added NeurosecurityMonitor for real-time threat classification
- Added Privacy Score Calculator for information leakage risk assessment
- Integrated ONI Framework neurosecurity components

### v0.3.0 (2026-01-22)
- Added Neural Simulator with brain region security analysis
- Added region-specific attack vectors and defenses
- Added ONI layer stack visualization
- Renamed Simulation to Neural Simulator
- Updated documentation with comprehensive CLAUDE.md and AGENTS.md

### v0.2.0 (2026-01-22)
- Added visualization module with brain topology and firewall pipeline
- Added BCI node network monitoring
- Added ONI L8-L14 aligned firewall (7 checkpoints)
- Reorganized UI navigation into Monitoring/Testing/Configuration sections
- Consolidated BCI nodes to Dashboard

### v0.1.0 (2026-01)
- Initial release
- Core modules: coherence, layers, firewall, scale_freq
- Simulation: LIF, Izhikevich, Hodgkin-Huxley neurons
- Attacks: 8 predefined patterns, scenarios
- NSAM: Real-time monitoring with detection rules
- CLI: Basic commands for ui, simulate, attack, monitor

---

*Documents: README.md, CLAUDE.md, AGENTS.md*
*Modules: 9 | Sub-modules: 16 | Lines of Code: ~19,000*
*Last Updated: 2026-01-25*
