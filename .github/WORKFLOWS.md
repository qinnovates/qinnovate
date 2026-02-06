# GitHub Workflows Documentation

> Overview of all CI/CD workflows in the ONI repository.

**Last Updated:** 2026-01-26

---

## Quick Reference

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| [Tests](#tests) | Push/PR to main | Run unit tests for all packages |
| [Security Scan](#security-scan) | Push/PR, weekly | Bandit, CodeQL, dependency safety |
| [Security Audit](#security-audit) | Push/PR, weekly | Scan for secrets & PII |
| [QA Checks](#qa-checks) | Push/PR, weekly | Brand consistency, imports, links |
| [Publish to PyPI](#publish-to-pypi) | Release | Build and publish packages |
| [Accessibility](#accessibility-check) | After publish | WCAG 2.1 AA compliance |
| [Sync Brand](#sync-brand-to-docs) | brand.json change | Sync brand values to README |
| [Auto Index](#auto-generate-index) | MAIN/legacy-core/ changes | Generate GLOSSARY.md via AI |
| [Dependabot Auto-Merge](#dependabot-auto-merge) | Dependabot PRs | Auto-merge patch/minor updates |

---

## Workflow Details

### Tests
**File:** `tests.yml`

Runs unit tests for all Python packages across multiple Python versions and operating systems.

| Setting | Value |
|---------|-------|
| **Trigger** | Push/PR to `main` (when package files change) |
| **Python versions** | 3.9, 3.10, 3.11, 3.12 |
| **OS** | Ubuntu, macOS |
| **Packages tested** | oni-framework, tara-nsec-platform, oni-academy |
| **Coverage** | Uploaded to Codecov |

**Required status check:** `test (3.11, ubuntu-latest)`

---

### Security Scan
**File:** `security.yml`

Comprehensive security scanning for Python code and web assets.

| Setting | Value |
|---------|-------|
| **Trigger** | Push/PR to `main`, weekly (Monday 9am UTC) |
| **Tools** | Bandit, Safety, CodeQL |
| **Scans** | Python code, JavaScript/TypeScript, HTML |

**Jobs:**
1. **Bandit** - Python static analysis for security issues
2. **Safety** - Check dependencies for known vulnerabilities
3. **CodeQL (Python)** - GitHub's semantic code analysis
4. **CodeQL (JavaScript)** - TypeScript/JavaScript analysis
5. **Web Security** - Check for XSS patterns, CSP, SRI

**Required status check:** `Web Security Scan`

---

### Security Audit
**File:** `security-audit.yml`

Deep scan for secrets, API keys, and PII in code.

| Setting | Value |
|---------|-------|
| **Trigger** | Push/PR to `main`/`develop`, weekly (Sunday midnight UTC) |
| **Tools** | Custom audit script (TruffleHog disabled — requires third-party action permissions) |
| **Output** | SARIF report uploaded to GitHub Security tab |

**Features:**
- PR-only scans changed files (faster)
- Full repo scan on push/schedule
- Comments on PR with results
- TruffleHog deep scan on schedule/manual trigger

---

### QA Checks
**File:** `qa.yml`

Quality assurance checks for brand consistency, imports, and documentation.

| Setting | Value |
|---------|-------|
| **Trigger** | Push/PR to `main`, weekly (Sunday 6am UTC) |

**Jobs:**
1. **Brand Consistency** - Validates brand.json, checks all packages load brand correctly
2. **Import Validation** - Verifies all core imports work
3. **Formula Consistency** - Checks Coherence formula matches across docs
4. **Link Validation** - Finds broken internal links
5. **HTML Validation** - Checks CSP, SRI in docs/index.html

---

### Publish to PyPI
**File:** `publish.yml`

Builds and publishes Python packages to PyPI.

| Setting | Value |
|---------|-------|
| **Trigger** | GitHub Release published, manual dispatch |
| **Packages** | oni-framework, oni-tara, oni-academy |
| **Auth** | Trusted publisher (OIDC) |

**Features:**
- Can publish all packages or select individual
- Uses `twine check` to validate packages
- Uploads build artifacts

---

### Accessibility Check
**File:** `accessibility.yml`

WCAG 2.1 Level AA compliance verification.

| Setting | Value |
|---------|-------|
| **Trigger** | After successful PyPI publish, manual |
| **Standard** | WCAG 2.1 AA |

**Checks:**
- Color contrast ratios (4.5:1 minimum)
- Font size minimums (0.875rem)
- Focus indicator presence
- Reduced motion support
- Skip link implementation

---

### Sync Brand to Docs
**File:** `sync-brand.yml`

Syncs brand.json values to README.md.

| Setting | Value |
|---------|-------|
| **Trigger** | Push to `main` when `MAIN/legacy-core/resources/brand.json` changes |
| **Script** | `scripts/sync_brand.py` |

**Note:** This workflow pushes directly to main. May need PR-based approach if branch protection blocks it.

---

### Auto Generate Index
**File:** `auto-index.yml`

Generates `GLOSSARY.md` using AI based on repository structure.

| Setting | Value |
|---------|-------|
| **Trigger** | Push to `main` (MAIN/legacy-core/** or autodidactive/** changes), manual |
| **AI Model** | gpt-4o-mini via GitHub Models |
| **Output** | `GLOSSARY.md` |

**Process:**
1. Generates file tree of repository
2. Reads existing INDEX.md for style reference
3. Calls GitHub Models API to generate summary
4. Creates PR with generated index (doesn't push directly)

---

### Dependabot Auto-Merge
**File:** `dependabot-auto-merge.yml`

Automatically approves and merges Dependabot PRs for patch/minor updates.

| Setting | Value |
|---------|-------|
| **Trigger** | Dependabot PRs opened/updated |
| **Auto-merge** | Patch and minor version updates |
| **Manual review** | Major version updates (comments on PR) |

---

## Branch Protection Requirements

The `main` branch has protection rules requiring:

1. **Pull request required** - No direct pushes
2. **Required status checks:**
   - `test (3.11, ubuntu-latest)` - from tests.yml
   - `Web Security Scan` - from security.yml

---

## Workflow Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                    PR to main                                │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
      ┌─────────┐     ┌──────────┐    ┌───────────┐
      │  Tests  │     │ Security │    │ QA Checks │
      └────┬────┘     └────┬─────┘    └─────┬─────┘
           │               │                │
           └───────────────┼────────────────┘
                           ▼
                    ┌──────────────┐
                    │ Merge to main │
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
      ┌───────────┐  ┌───────────┐  ┌───────────┐
      │ Auto-Index│  │ Sync-Brand│  │(if release)│
      │   → PR    │  │ (blocked) │  │  Publish   │
      └───────────┘  └───────────┘  └─────┬─────┘
                                          │
                                          ▼
                                   ┌─────────────┐
                                   │Accessibility│
                                   └─────────────┘
```

---

## Manual Triggers

All workflows support `workflow_dispatch` for manual triggering via GitHub UI or CLI:

```bash
# Run tests manually
gh workflow run tests.yml

# Run security scan with specific severity
gh workflow run security.yml

# Generate index manually
gh workflow run auto-index.yml

# Publish specific package
gh workflow run publish.yml -f package=oni-framework
```

---

## Secrets Required

| Secret | Used By | Purpose |
|--------|---------|---------|
| `GITHUB_TOKEN` | All | Auto-provided by GitHub |
| `GIST_TOKEN` | accessibility.yml | Update accessibility badge |
| `A11Y_BADGE_GIST_ID` | accessibility.yml | Badge gist ID |

**Note:** PyPI publishing uses OIDC trusted publisher, no API token needed.

---

*Document Version: 1.0*
