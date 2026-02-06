# Changelog

All notable changes to TARA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.1] - 2026-01-26

### Added
- **WCAG 2.1 AA Compliance** - Full accessibility compliance for TARA UI
- **Skip Links** - Keyboard navigation support for screen readers
- **Focus Indicators** - Visible focus states on all interactive elements
- **Reduced Motion Support** - Respects `prefers-reduced-motion` preference

### Changed
- Updated neon color palette for WCAG AA contrast ratios
- Fixed text colors for accessibility: `#94a3b8` → `#a8b5c7`, `#64748b` → `#8b9cb3`
- Minimum font size now 0.875rem (14px) for accessibility

### Documentation
- Added accessibility compliance to TARA documentation

## [0.8.0] - 2026-01-25

### Added
- **Bidirectional BCI Security** - Stimulation filtering for write-path BCIs
- **MOABB Integration Tests** - Real EEG data testing with attack injection
- **OpenBCI Adapter** - Live hardware integration via BrainFlow

### Changed
- Enhanced neurosecurity module with bidirectional threat detection
- Improved attack simulator with stimulation-based attacks

## [0.7.0] - 2026-01-25

### Added
- **Yale Threat Model** - Academic threat taxonomy with CVSS v4.0 scoring
- **API.md** - Comprehensive API documentation
- **Attack Scenarios** - Multi-stage attack simulation

## [0.6.0] - 2026-01-24

### Added
- **Neurosecurity Page** - Kohno threat rules, privacy calculator
- **Real EEG Data Page** - MOABB dataset integration
- **Neural ATT&CK Matrix** - Attack technique visualization
- **Pew-Pew Animation** - Attack visualization effects

## [0.5.0] - 2026-01-23

### Added
- **ONI Visualization Suite** - 5 interactive HTML visualizations
- **Consolidated Package** - All modules in single `tara_mvp/` directory

## [0.4.0] - 2026-01-22

### Added
- **Neurosecurity Module** - Kohno (2009) threat taxonomy integration
- **BCI Anonymizer** - Bonaci (2015) privacy filtering

## [0.3.0] - 2026-01-21

### Added
- **Neural Simulator** - Brain region security analysis
- **3D Brain Topology** - Interactive electrode visualization

## [0.2.0] - 2026-01-20

### Added
- **Visualization Module** - Real-time dashboards
- **Firewall Pipeline** - ONI L8-L14 validation visualization

## [0.1.0] - 2026-01-19

### Added
- Initial release with core, simulation, attacks, NSAM modules
- CLI tool (`tara`) with ui, simulate, attack, monitor commands
- Streamlit web interface

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 0.8.1 | 2026-01-26 | WCAG 2.1 AA compliance |
| 0.8.0 | 2026-01-25 | Bidirectional BCI, MOABB tests, OpenBCI |
| 0.7.0 | 2026-01-25 | Yale threat model, CVSS v4.0, API docs |
| 0.6.0 | 2026-01-24 | Neurosecurity page, Real EEG, ATT&CK matrix |
| 0.5.0 | 2026-01-23 | ONI Visualization Suite |
| 0.4.0 | 2026-01-22 | Neurosecurity module |
| 0.3.0 | 2026-01-21 | Neural Simulator, 3D brain |
| 0.2.0 | 2026-01-20 | Visualization, firewall pipeline |
| 0.1.0 | 2026-01-19 | Initial release |
