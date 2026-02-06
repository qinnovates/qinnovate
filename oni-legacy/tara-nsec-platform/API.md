# TARA API Reference

> **TARA v0.8.0** - Telemetry Analysis & Response Automation
> Neural Security Platform for Brain-Computer Interfaces

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Module](#core-module)
- [Bidirectional BCI Security](#bidirectional-bci-security)
- [Attack Simulation](#attack-simulation)
- [Yale Threat Model & CVSS](#yale-threat-model--cvss)
- [NSAM (Neural Signal Assurance Monitoring)](#nsam-neural-signal-assurance-monitoring)
- [Neurosecurity](#neurosecurity)
- [Data Models](#data-models)
- [CLI Reference](#cli-reference)

---

## Installation

```bash
# Basic installation
pip install oni-tara

# With MOABB support (real EEG datasets)
pip install oni-tara[moabb]

# Full installation (all features)
pip install oni-tara[full]
```

---

## Quick Start

```python
from tara_mvp import (
    # Core
    CoherenceMetric, NeuralFirewall, ONIStack,
    # Attacks
    AttackSimulator, AttackPattern,
    # Yale/CVSS
    YaleThreatCategory, get_yale_patterns, get_cvss_summary,
    # NSAM
    NeuralMonitor, Alert, AlertLevel,
    # Neurosecurity
    NeurosecurityMonitor,
)

# Calculate coherence score
metric = CoherenceMetric()
score = metric.calculate(signal_data)

# Get Yale threat summary
summary = get_cvss_summary()
print(f"Critical vulnerabilities: {summary['by_severity']['Critical']}")
```

---

## Core Module

### CoherenceMetric

Calculates the Coherence Score (Cₛ) for neural signals.

```python
from tara_mvp import CoherenceMetric, calculate_cs

# Using class
metric = CoherenceMetric(
    weights=[0.4, 0.3, 0.3],  # Component weights
    threshold=0.7,            # Pass/fail threshold
)
score = metric.calculate(signal_data)

# Using function shortcut
score = calculate_cs(signal_data)
```

**Formula:** `Cₛ = e^(−(σ²φ + σ²τ + σ²γ))`

| Parameter | Type | Description |
|-----------|------|-------------|
| `signal_data` | np.ndarray | Neural signal array |
| `weights` | List[float] | Component weights (sum to 1.0) |
| `threshold` | float | Pass/fail threshold (0-1) |

**Returns:** `float` - Coherence score (0.0 to 1.0)

---

### NeuralFirewall

ONI Layer 8 firewall for signal validation. Supports both READ (recording) and WRITE (stimulation) operations for bidirectional BCIs.

```python
from tara_mvp import NeuralFirewall, Signal, StimulationCommand

# Create firewall for bidirectional BCI
firewall = NeuralFirewall(
    # READ (recording) settings
    threshold_high=0.6,
    threshold_low=0.3,
    amplitude_bounds=(0, 500),
    rate_limit=1000,
    # WRITE (stimulation) settings
    stim_amplitude_bounds=(0.0, 3000.0),  # 0-3 mA
    stim_frequency_bounds=(1.0, 200.0),   # 1-200 Hz
    stim_pulse_width_bounds=(100.0, 500.0),
    charge_density_limit=25.0,             # uC/cm^2/phase
    authorized_regions={"M1", "S1", "PMC"},
    stim_rate_limit=10,
)

# Validate a READ signal
signal = Signal(
    arrival_times=[0.0, 0.025, 0.050],
    amplitudes=[100.0, 98.0, 102.0],
    authenticated=True,
)
result = firewall.filter(signal)
print(f"Decision: {result.decision.name}")
print(f"Coherence: {result.coherence:.3f}")

# Validate a WRITE (stimulation) command
stim = StimulationCommand(
    target_region="M1",
    amplitude_uA=1000.0,
    frequency_Hz=100.0,
    pulse_width_us=200.0,
    authenticated=True,
)
stim_result = firewall.filter_stimulation(stim)
print(f"Decision: {stim_result.decision.name}")
print(f"All checks passed: {stim_result.all_checks_passed}")

# Get bidirectional statistics
stats = firewall.get_stats()
print(f"Flow direction: {stats['flow_direction']}")
print(f"Read stats: {stats['read']}")
print(f"Stimulation stats: {stats['stimulation']}")
```

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `filter(signal)` | Signal | FilterResult | Validate READ signal |
| `filter_batch(signals)` | List[Signal] | List[FilterResult] | Batch READ validation |
| `filter_stimulation(cmd)` | StimulationCommand | StimulationResult | Validate WRITE command |
| `filter_stimulation_batch(cmds)` | List[StimulationCommand] | List[StimulationResult] | Batch WRITE validation |
| `authorize_region(region)` | str | None | Add authorized stimulation region |
| `revoke_region(region)` | str | None | Remove authorized region |
| `get_stats()` | None | Dict | Get bidirectional statistics |
| `clear_log()` | None | None | Clear all logs |

---

### ONIStack

The complete 14-layer ONI model.

```python
from tara_mvp import ONIStack, Layer

stack = ONIStack()

# Get layer information
layer = stack.get_layer(8)  # Neural Gateway
print(f"Layer {layer.number}: {layer.name}")
print(f"Domain: {layer.domain}")
print(f"Function: {layer.function}")

# List all layers
for layer in stack.layers:
    print(f"L{layer.number}: {layer.name}")
```

**Layer Structure:**

| Range | Domain | Layers |
|-------|--------|--------|
| L1-L7 | Silicon (OSI) | Physical → Application |
| L8 | Bridge | Neural Gateway (Firewall) |
| L9-L14 | Biology | Signal Processing → Identity |

---

### ScaleFrequencyInvariant

Implements the f × S ≈ k relationship.

```python
from tara_mvp import ScaleFrequencyInvariant

invariant = ScaleFrequencyInvariant(k=1.0)

# Calculate expected frequency for a scale
freq = invariant.frequency_at_scale(scale=0.001)  # 1ms

# Calculate expected scale for a frequency
scale = invariant.scale_at_frequency(freq=40.0)  # 40 Hz

# Verify invariant holds
is_valid = invariant.verify(frequency=40.0, scale=0.025)
```

---

## Bidirectional BCI Security

Support for BCIs that both READ from and WRITE to the brain.

### FlowDirection

Enum indicating data flow direction through L8.

```python
from tara_mvp import FlowDirection

directions = [
    FlowDirection.READ,         # Brain → Computer (recording)
    FlowDirection.WRITE,        # Computer → Brain (stimulation)
    FlowDirection.BIDIRECTIONAL # Both directions (closed-loop)
]
```

---

### StimulationCommand

Represents a stimulation command for validation.

```python
from tara_mvp import StimulationCommand

cmd = StimulationCommand(
    target_region="M1",           # Brain region identifier
    amplitude_uA=1000.0,          # Amplitude in microamperes
    frequency_Hz=100.0,           # Frequency in Hertz
    pulse_width_us=200.0,         # Pulse width in microseconds
    duration_ms=1000.0,           # Total duration
    waveform="biphasic",          # "biphasic", "monophasic", "burst"
    authenticated=True,           # Authentication status
    source_id="clinical_001",     # Source identifier
    metadata={"trial": 1},        # Additional metadata
)

# Calculate charge per phase
print(f"Charge: {cmd.charge_per_phase_nC:.2f} nC")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_region` | str | required | Brain region (e.g., "M1", "PFC") |
| `amplitude_uA` | float | required | Stimulation amplitude (μA) |
| `frequency_Hz` | float | required | Stimulation frequency (Hz) |
| `pulse_width_us` | float | 200.0 | Pulse width (μs) |
| `duration_ms` | float | 1000.0 | Total duration (ms) |
| `waveform` | str | "biphasic" | Waveform type |
| `authenticated` | bool | False | Authentication status |

---

### StimulationResult

Result of stimulation command validation.

```python
from tara_mvp import StimulationResult, Decision, AlertLevel

# After firewall.filter_stimulation(cmd)
print(f"Decision: {result.decision.name}")      # ACCEPT or REJECT
print(f"Alert Level: {result.alert_level.name}")
print(f"Reason: {result.reason}")

# Check individual safety checks
for check, passed in result.safety_checks.items():
    status = "✓" if passed else "✗"
    print(f"  {status} {check}")

# Convenience properties
print(f"Accepted: {result.accepted}")
print(f"Rejected: {result.rejected}")
print(f"All checks passed: {result.all_checks_passed}")
```

**Safety Checks Performed:**

| Check | Description | Alert Level on Fail |
|-------|-------------|---------------------|
| `authenticated` | Command has valid authentication | ALERT |
| `region_authorized` | Target region in authorized set | CRITICAL |
| `amplitude_in_bounds` | Within configured amplitude limits | CRITICAL |
| `frequency_in_bounds` | Within configured frequency limits | CRITICAL |
| `pulse_width_in_bounds` | Within configured pulse width limits | ENHANCED |
| `charge_density_safe` | Below Shannon limit | CRITICAL |
| `rate_limit_ok` | Not exceeding commands/second | ALERT |

---

### Stimulation Safety Bounds

Default safety bounds based on literature (Shannon 1992, Merrill 2005):

| Parameter | Default Range | Rationale |
|-----------|---------------|-----------|
| Amplitude | 0-5000 μA | Prevent tissue damage |
| Frequency | 0.1-500 Hz | Physiological range |
| Pulse Width | 50-1000 μs | Balance efficacy/safety |
| Charge Density | <30 μC/cm²/phase | Shannon limit (k=1.5) |

```python
# Configure custom safety bounds
firewall = NeuralFirewall(
    stim_amplitude_bounds=(0.0, 2000.0),   # Max 2 mA
    stim_frequency_bounds=(1.0, 130.0),    # DBS range
    stim_pulse_width_bounds=(60.0, 450.0),
    charge_density_limit=25.0,
    authorized_regions={"STN", "GPi"},      # Deep brain targets
    stim_rate_limit=5,
)
```

---

### Region Authorization

Dynamic management of authorized stimulation targets.

```python
from tara_mvp import NeuralFirewall

firewall = NeuralFirewall(
    authorized_regions={"M1", "S1"}  # Initial regions
)

# Add new region
firewall.authorize_region("PMC")

# Revoke region
firewall.revoke_region("S1")

# Check current regions
stats = firewall.get_stats()
print(f"Authorized: {stats['stimulation']['authorized_regions']}")
```

**Security Note:** If no regions are authorized (empty set), ALL stimulation commands are rejected (fail-closed behavior).

---

## Attack Simulation

### AttackPattern

Defines individual attack patterns.

```python
from tara_mvp import AttackPattern
from tara_mvp.attacks.patterns import AttackType, ATTACK_PATTERNS

# Get predefined pattern
pattern = ATTACK_PATTERNS["malicious_firmware_update"]
print(f"Name: {pattern.name}")
print(f"Target Layer: L{pattern.target_layer}")
print(f"CVSS Score: {pattern.cvss_score}")
print(f"Severity: {pattern.cvss_severity}")

# Create custom pattern
custom = AttackPattern(
    name="Custom Attack",
    attack_type=AttackType.SIGNAL_INJECTION,
    target_layer=8,
    description="Custom attack description",
    intensity=0.7,
    duration=1000.0,
)
```

**Predefined Patterns:**

| Pattern | Type | Target Layer | CVSS |
|---------|------|--------------|------|
| `phase_jitter` | Phase Disruption | L8 | - |
| `amplitude_surge` | Amplitude Manipulation | L9 | - |
| `neural_ransomware` | Neural Ransomware | L6 | - |
| `dos_flood` | DoS Flooding | L8 | - |
| `malicious_firmware_update` | Malicious Update | L7 | 9.5 |
| `auth_bypass_wireless` | Auth Bypass | L8 | 9.1 |
| `ai_malicious_stimulation` | AI Manipulation | L13 | 7.7 |
| `wireless_network_exploit` | Wireless Exploit | L8 | 7.6 |
| `mass_neural_manipulation` | Network Hijacking | L14 | 7.5 |
| `unencrypted_neural_intercept` | Encryption Attack | L10 | 6.8 |

---

### AttackScenario

Multi-stage attack scenarios.

```python
from tara_mvp import AttackScenario
from tara_mvp.attacks.scenarios import (
    PREDEFINED_SCENARIOS,
    get_scenario,
    list_scenarios,
    get_yale_scenarios,
)

# List available scenarios
print(list_scenarios())
# ['ransomware', 'gateway_infiltration', 'dos', 'mitm', 'recon',
#  'supply_chain', 'wireless_exploit', 'ai_attack', 'mass_exploitation']

# Get scenario
scenario = get_scenario("supply_chain")
print(f"Name: {scenario.name}")
print(f"Severity: {scenario.severity.name}")
print(f"Stages: {scenario.n_stages}")
print(f"Duration: {scenario.total_duration}ms")

# Get Yale-based scenarios
yale = get_yale_scenarios()
for s in yale:
    print(f"{s.name}: {[c.value for c in s.yale_categories]}")
```

**Predefined Scenarios:**

| Scenario | Severity | Stages | Yale Categories |
|----------|----------|--------|-----------------|
| `ransomware` | Critical | 4 | - |
| `gateway_infiltration` | High | 3 | - |
| `dos` | High | 2 | - |
| `mitm` | Critical | 3 | - |
| `recon` | Medium | 1 | - |
| `supply_chain` | Critical | 4 | software_update, authentication |
| `wireless_exploit` | High | 3 | wireless, authentication, encryption |
| `ai_attack` | Critical | 3 | software_update |
| `mass_exploitation` | Critical | 3 | all four |

---

### AttackSimulator

Executes attack patterns and scenarios.

```python
from tara_mvp import AttackSimulator

simulator = AttackSimulator()

# Execute single pattern
result = simulator.execute_pattern(
    pattern=ATTACK_PATTERNS["phase_jitter"],
    target_signal=signal_data,
)
print(f"Attack success: {result.success}")
print(f"Detected: {result.detected}")

# Execute scenario
scenario_result = simulator.execute_scenario(
    scenario=get_scenario("ransomware"),
    target_network=network,
)
```

---

## Yale Threat Model & CVSS

### YaleThreatCategory

Enum for Yale Digital Ethics Center threat categories.

```python
from tara_mvp import YaleThreatCategory

# Four categories from Schroder et al. (2025)
categories = [
    YaleThreatCategory.SOFTWARE_UPDATE,   # Malicious firmware/software
    YaleThreatCategory.AUTHENTICATION,    # Weak/absent access controls
    YaleThreatCategory.WIRELESS,          # Network exposure
    YaleThreatCategory.ENCRYPTION,        # Unprotected data
]
```

**Reference:** Schroder, T., et al. (2025). Cyber Risks to Next-Gen BCIs. *Neuroethics*.

---

### CVSSScore

CVSS v4.0 vulnerability scoring.

```python
from tara_mvp import CVSSScore
from tara_mvp.attacks.patterns import CVSSMetric

# Create CVSS score
cvss = CVSSScore(
    attack_vector="N",           # Network
    attack_complexity="L",       # Low
    attack_requirements="N",     # None
    privileges_required="N",     # None
    user_interaction="N",        # None
    vuln_conf_impact="H",        # High
    vuln_integ_impact="H",       # High
    vuln_avail_impact="H",       # High
    subseq_conf_impact="L",      # Low
    subseq_integ_impact="L",     # Low
    subseq_avail_impact="N",     # None
)

print(f"Base Score: {cvss.base_score}")      # 0.0-10.0
print(f"Severity: {cvss.severity}")          # None/Low/Medium/High/Critical
print(f"Vector: {cvss.vector_string}")       # CVSS:4.0/AV:N/AC:L/...
```

**CVSS Metric Values:**

| Metric | Values | Description |
|--------|--------|-------------|
| Attack Vector | N, A, L, P | Network, Adjacent, Local, Physical |
| Attack Complexity | L, H | Low, High |
| Attack Requirements | N, P | None, Present |
| Privileges Required | N, L, H | None, Low, High |
| User Interaction | N, P, A | None, Passive, Active |
| Impact (C/I/A) | N, L, H | None, Low, High |

---

### Helper Functions

```python
from tara_mvp import (
    get_yale_patterns,
    get_cvss_summary,
    patterns_by_cvss_severity,
    get_yale_scenarios,
    scenarios_by_yale_category,
)

# Get all Yale patterns grouped by category
yale_patterns = get_yale_patterns()
# {'software_update': [...], 'authentication': [...], ...}

# Get CVSS summary statistics
summary = get_cvss_summary()
# {
#   'total_patterns': 6,
#   'by_severity': {'Critical': 2, 'High': 3, 'Medium': 1, ...},
#   'highest_score': {'score': 9.5, 'pattern': 'malicious_firmware_update'},
#   'mean_score': 8.0
# }

# Get patterns by severity
critical = patterns_by_cvss_severity("Critical")

# Get scenarios by Yale category
wireless = scenarios_by_yale_category(YaleThreatCategory.WIRELESS)
```

---

## NSAM (Neural Signal Assurance Monitoring)

### NeuralMonitor

Real-time neural signal monitoring.

```python
from tara_mvp import NeuralMonitor, Alert, AlertLevel

monitor = NeuralMonitor()

# Start monitoring
monitor.start()

# Process signals
for signal in signal_stream:
    alerts = monitor.process(signal)
    for alert in alerts:
        print(f"[{alert.level.name}] {alert.message}")

# Get current status
status = monitor.get_status()
print(f"Alerts: {status['alert_count']}")
print(f"Uptime: {status['uptime_seconds']}s")

# Stop monitoring
monitor.stop()
```

---

### DetectionRule

Custom detection rules for NSAM.

```python
from tara_mvp import DetectionRule

rule = DetectionRule(
    name="High Amplitude Spike",
    condition=lambda signal: signal.max() > 100,
    alert_level=AlertLevel.WARNING,
    description="Detects abnormally high amplitude spikes",
    tags=["amplitude", "spike"],
)

# Add to monitor
monitor.add_rule(rule)
```

---

### Alert & AlertLevel

```python
from tara_mvp import Alert, AlertLevel

# Alert levels
levels = [
    AlertLevel.INFO,      # Informational
    AlertLevel.WARNING,   # Potential issue
    AlertLevel.ERROR,     # Definite problem
    AlertLevel.CRITICAL,  # Immediate action required
]

# Create alert
alert = Alert(
    level=AlertLevel.WARNING,
    message="Coherence dropped below threshold",
    source="firewall",
    timestamp=datetime.now(),
    metadata={"coherence": 0.65, "threshold": 0.7},
)
```

---

## Neurosecurity

### NeurosecurityMonitor

Implements Kohno (2009) threat taxonomy.

```python
from tara_mvp import NeurosecurityMonitor

monitor = NeurosecurityMonitor()

# Load Kohno detection rules into NSAM
from tara_mvp.nsam import RuleEngine
engine = RuleEngine()
rules_loaded = monitor.load_kohno_rules(engine)

# Classify threat type
threat = monitor.classify_threat(metrics)
# Returns: 'Alteration', 'Blocking', or 'Eavesdropping'

# Calculate privacy score
score = monitor.calculate_privacy_score(
    signal_data=signal,
    detected_erps=["P300", "N170", "N400"],
)
print(f"Privacy Risk: {score['score']:.2f}")
print(f"Interpretation: {score['interpretation']}")
```

**Kohno Threat Categories:**

| Category | CIA Property | Description |
|----------|--------------|-------------|
| Alteration | Integrity | Unauthorized signal modification |
| Blocking | Availability | Signal disruption/denial |
| Eavesdropping | Confidentiality | Unauthorized data access |

---

### Additional Neurosecurity Classes

```python
from tara_mvp import (
    ThreatType,              # Enum: ALTERATION, BLOCKING, EAVESDROPPING
    KohnoThreatModel,        # Full threat model implementation
    BCIAnonymizer,           # Signal anonymization
    PrivacyScoreCalculator,  # Privacy risk assessment
    ERPType,                 # ERP types (P300, N170, etc.)
    PrivacySensitivity,      # Sensitivity levels
)

# BCI Anonymizer
anonymizer = BCIAnonymizer()
anonymized = anonymizer.anonymize(signal, preserve_utility=True)

# Privacy calculator
calculator = PrivacyScoreCalculator()
risk = calculator.calculate(signal, detected_erps=["P300"])
```

---

## Data Models

### Brain Regions

```python
from tara_mvp.data import BrainRegion, BRAIN_REGIONS

# Get region
m1 = BRAIN_REGIONS["M1"]
print(f"Name: {m1.name}")           # Primary Motor Cortex
print(f"ONI Layer: L{m1.oni_layer}") # L13
print(f"Center: {m1.center}")        # MNI coordinates
print(f"Function: {m1.function}")

# All regions
for abbrev, region in BRAIN_REGIONS.items():
    print(f"{abbrev}: {region.name} (L{region.oni_layer})")
```

**Available Regions:**

| Abbreviation | Name | ONI Layer |
|--------------|------|-----------|
| M1 | Primary Motor Cortex | L13 |
| S1 | Primary Somatosensory | L12 |
| PMC | Premotor Cortex | L13 |
| SMA | Supplementary Motor | L13 |
| PFC | Prefrontal Cortex | L14 |
| BROCA | Broca's Area | L14 |
| WERNICKE | Wernicke's Area | L14 |
| V1 | Primary Visual | L12 |
| A1 | Primary Auditory | L12 |
| HIPP | Hippocampus | L11 |

---

### MOABB Adapter

Integration with real EEG datasets.

```python
from tara_mvp.data import MOABBAdapter, is_moabb_available

if is_moabb_available():
    adapter = MOABBAdapter()

    # Load dataset
    dataset = adapter.load_dataset("BNCI2014_001")
    signals = adapter.get_signals(dataset, subject=1, max_epochs=10)

    # Inject attack
    attacked = adapter.inject_attack(
        signals[0],
        attack_type="spike",  # spike, noise, frequency, phase, dc_shift
        intensity=2.0,
    )

    # Benchmark coherence
    results = adapter.benchmark_coherence(signals)
    print(f"Mean Cₛ: {results['clean_signals']['mean_score']:.3f}")
```

**Requires:** `pip install oni-tara[moabb]`

---

## CLI Reference

```bash
# Launch web dashboard
tara ui [--port PORT]

# Run simulation
tara simulate --network oni --duration 1000

# Execute attack scenario
tara attack --scenario ransomware --target network.json

# Start real-time monitoring
tara monitor --input signals.json --realtime

# Show version
tara --version
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.8.0 | 2026-01-25 | Bidirectional BCI security, stimulation filtering, MOABB tests |
| 0.7.0 | 2026-01-25 | Yale threat model, CVSS v4.0 scoring |
| 0.6.0 | 2026-01-24 | Neurosecurity page, Real EEG, Neural ATT&CK matrix |
| 0.5.0 | 2026-01-23 | Consolidated package, ONI Visualization Suite |
| 0.4.0 | 2026-01-22 | Neurosecurity module (Kohno 2009) |
| 0.3.0 | 2026-01-21 | Neural Simulator with region security |
| 0.2.0 | 2026-01-20 | Visualization, brain topology, firewall pipeline |
| 0.1.0 | 2026-01-19 | Initial release |

---

## References

1. Schroder, T., et al. (2025). Cyber Risks to Next-Gen Brain-Computer Interfaces. *Neuroethics*.
2. Kohno, T., et al. (2009). Analysis of Wireless and Implantable Medical Devices. *J Neurosurg Focus*.
3. Bonaci, T., et al. (2015). App Stores for the Brain. *IEEE S&P Workshop*.
4. FIRST. (2023). Common Vulnerability Scoring System v4.0.
5. Shannon, R. V. (1992). A model of safe levels for electrical stimulation. *IEEE Trans Biomed Eng*.
6. Merrill, D. R., et al. (2005). Electrical stimulation of excitable tissue. *J Neurosci Methods*.

---

*Last Updated: 2026-01-25*
*TARA v0.8.0*
