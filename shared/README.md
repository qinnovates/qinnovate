# Classical↔Quantum Bridge

This folder contains shared data structures and validation tools that bridge the **Classical (ONI 14-Layer)** and **Quantum (QIF 7-Band Hourglass)** BCI security models.

## Architecture

```
shared/
├── threat-matrix.json            # Master taxonomy with category codes
├── validation/                   # Validation tools
│   ├── bridge.py                 # ONI↔QIF validator
│   ├── validate_metadata.py      # Metadata validation
│   └── generate_progress.py     # Progress tracking
└── README.md                     # This file
```

## Single Source of Truth

The `threat-matrix.json` file is the canonical source for all threat data. Each threat is mapped to **both** ONI layers (L1-L14) and QIF bands (N3/N2/N1/I0/S1/S2/S3).

### Category System

Threats are categorized using internal codes:

| Code | Name | Description |
|------|------|-------------|
| **Κ** | Common | Elements shared across both ONI and QIF models |
| **Δ** | Differences | Unique to one model only |
| **Σ** | Sum | Combined total across both models |

**Note:** These Greek letters are internal category codes used in the JSON. When building user interfaces, translate them to human-readable labels using the `_meta.categories` definitions.

## Usage

### Validate Consistency

```bash
python validation/bridge.py --validate    # Check consistency (0 errors = pass)
```

### Show Differences

```bash
python validation/bridge.py --diff        # Where models diverge
```

### Filter by Category

```bash
# In your code:
import json
with open('threat-matrix.json') as f:
    data = json.load(f)

# Get all common threats (Κ)
common = [t for t in data['tactics'] if t.get('category') == 'Κ']

# Get model-specific threats (Δ)
differences = [t for t in data['tactics'] if t.get('category') == 'Δ']

# Get sum/total threats (Σ)
total = [t for t in data['tactics'] if t.get('category') == 'Σ']
```

## Layer→Band Migration

The canonical translation between Classical layers (L1-L14) and Quantum bands is defined in `_meta.migration`:

```json
{
  "L1-L7": "S3",      // Silicon infrastructure
  "L8": "I0",         // Neural Gateway (physical interface)
  "L9": "I0/N1",      // Boundary-spanning
  "L10": "N1/N2",     // Boundary-spanning
  "L11": "N2",        // Neural semantics
  "L12-L14": "N3"     // Cognitive sovereignty
}
```

## Adding New Threats

When adding threats to `threat-matrix.json`:

1. Assign appropriate category code (**Κ**, **Δ**, or **Σ**)
2. Map to both ONI layers and QIF bands
3. Run validation: `python validation/bridge.py --validate`
4. Ensure consistency check passes

---

*Last updated: 2026-02-05*
