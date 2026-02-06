# Security Audit Pipeline

Automated security scanning for secrets, credentials, PII, and sensitive data.

## Features

- **Pre-commit Hook**: Blocks commits containing secrets before they enter git history
- **GitHub Action**: Scans PRs and pushes, comments results on PRs, uploads to GitHub Security
- **Configurable Patterns**: JSON-based pattern definitions, easy to extend
- **Multiple Output Formats**: Text, JSON, SARIF (GitHub Advanced Security compatible)
- **Severity Levels**: Low, Medium, High, Critical with configurable thresholds
- **Allowlisting**: Exclude false positives by file or pattern

## What It Detects

| Category | Examples |
|----------|----------|
| **API Keys** | OpenAI, Anthropic, Google, Stripe, Slack, Discord, generic API keys |
| **AWS Credentials** | Access Key IDs, Secret Access Keys, Account IDs |
| **Private Keys** | RSA, OpenSSH, PGP, EC, DSA private keys |
| **Passwords** | Hardcoded passwords, database connection strings |
| **Tokens** | GitHub, GitLab, NPM, PyPI, JWT, Bearer tokens |
| **PII** | Email addresses, SSNs, phone numbers, credit cards |
| **Sensitive Files** | `.env`, `*.pem`, `*.key`, `credentials.json`, etc. |

## Quick Start

### 1. Install Pre-commit Hook

```bash
# From repository root
./.github/security-audit/install.sh
```

This installs a git pre-commit hook that automatically scans staged files before each commit.

### 2. GitHub Action (Automatic)

The GitHub Action runs automatically on:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`
- Weekly scheduled scan (Sundays at midnight UTC)

No additional setup required if the workflow file is present.

## Usage

### Command Line

```bash
# Scan staged files (default)
python .github/security-audit/scripts/audit.py --staged

# Scan all tracked files
python .github/security-audit/scripts/audit.py --all

# Scan specific files
python .github/security-audit/scripts/audit.py file1.py file2.js

# Set minimum severity
python .github/security-audit/scripts/audit.py --severity high

# Output as JSON
python .github/security-audit/scripts/audit.py --format json

# Output as SARIF (for GitHub Security)
python .github/security-audit/scripts/audit.py --format sarif

# Verbose output with match details
python .github/security-audit/scripts/audit.py --verbose

# Fail only on critical findings
python .github/security-audit/scripts/audit.py --fail-on critical
```

### Options

| Option | Description |
|--------|-------------|
| `--staged` | Scan only staged files (for pre-commit) |
| `--all` | Scan all tracked files in repository |
| `--config PATH` | Path to patterns config file |
| `--format FORMAT` | Output format: `text`, `json`, `sarif` |
| `--severity LEVEL` | Minimum severity to report: `low`, `medium`, `high`, `critical` |
| `--fail-on LEVEL` | Exit with error if findings >= severity level |
| `--verbose`, `-v` | Show detailed output including matched text |
| `--quiet`, `-q` | Minimal output, only show findings |

## Configuration

### Pattern Configuration

Patterns are defined in `patterns/secrets.json`. Structure:

```json
{
  "patterns": {
    "category_name": [
      {
        "name": "Pattern Display Name",
        "pattern": "regex_pattern",
        "severity": "critical|high|medium|low",
        "context_required": false
      }
    ]
  },
  "file_patterns": {
    "sensitive_files": [".env", "*.key", "*.pem"]
  },
  "allowlist": {
    "files": ["*.md", "test/**"],
    "patterns": ["example@example.com"]
  }
}
```

### Adding Custom Patterns

1. Edit `patterns/secrets.json`
2. Add your pattern to the appropriate category:

```json
{
  "name": "My Custom API Key",
  "pattern": "my-api-[a-zA-Z0-9]{32}",
  "severity": "high"
}
```

### Allowlisting False Positives

Add to the `allowlist` section:

```json
{
  "allowlist": {
    "files": [
      "docs/examples/**",
      "tests/fixtures/**"
    ],
    "patterns": [
      "test-api-key-12345",
      "example@example.com"
    ]
  }
}
```

## Directory Structure

```
.github/security-audit/
├── README.md                 # This file
├── install.sh                # Installation script
├── hooks/
│   └── pre-commit            # Git pre-commit hook
├── scripts/
│   └── audit.py              # Main audit script
└── patterns/
    └── secrets.json          # Pattern definitions
```

## GitHub Action Features

The GitHub Action (`/.github/workflows/security-audit.yml`) provides:

- **PR Scanning**: Scans only changed files in pull requests
- **Full Scans**: Scans all files on push to main branches
- **PR Comments**: Posts audit results as PR comments
- **SARIF Upload**: Uploads results to GitHub Advanced Security
- **Artifacts**: Stores detailed results for 30 days
- **TruffleHog Integration**: Disabled (requires third-party action permissions — see workflow for re-enable instructions)

### Manual Trigger

Run the workflow manually from GitHub Actions tab with custom severity level.

## Severity Levels

| Level | Description | Default Action |
|-------|-------------|----------------|
| `critical` | Confirmed secrets, private keys | Block commit/PR |
| `high` | Likely secrets, passwords | Block commit/PR |
| `medium` | Possible secrets, credentials | Warn |
| `low` | Informational (IPs, emails in context) | Log |

## Bypassing (Use Sparingly)

```bash
# Bypass pre-commit hook
git commit --no-verify

# Skip in GitHub Action
# Add [skip security] to commit message (requires workflow modification)
```

## Troubleshooting

### Pre-commit hook not running

```bash
# Check if hook is installed
ls -la .git/hooks/pre-commit

# Reinstall
./.github/security-audit/install.sh --force
```

### False positives

1. Check if the pattern matches test data or examples
2. Add to allowlist in `patterns/secrets.json`
3. For file-level exclusions, add to `allowlist.files`

#### Historical False Positives (Resolved)

**2026-01-24: Pattern definitions self-detection**

The scanner was flagging its own pattern definition file (`.github/security-audit/patterns/secrets.json`) as containing secrets because it includes pattern strings like `"-----BEGIN RSA PRIVATE KEY-----"`.

| Finding | File | Reason | Status |
|---------|------|--------|--------|
| RSA Private Key | `patterns/secrets.json:62` | Pattern definition string | **FALSE POSITIVE** |
| OpenSSH Private Key | `patterns/secrets.json:67` | Pattern definition string | **FALSE POSITIVE** |
| PGP Private Key | `patterns/secrets.json:72` | Pattern definition string | **FALSE POSITIVE** |
| EC Private Key | `patterns/secrets.json:77` | Pattern definition string | **FALSE POSITIVE** |
| DSA Private Key | `patterns/secrets.json:82` | Pattern definition string | **FALSE POSITIVE** |
| Bearer Token | `patterns/secrets.json:130` | Pattern definition string | **FALSE POSITIVE** |

**Resolution:** Added `'security-audit'` to `skip_dirs` in `scripts/audit.py` to prevent the scanner from scanning its own pattern definitions.

**Verification:** No actual secrets, API keys, or credentials exist in the repository. Manual audit confirmed:
- No `.env` files
- No `*.pem` or `*.key` files
- No hardcoded API keys (OpenAI, Anthropic, AWS, etc.)
- No credential files

### Python not found

```bash
# Ensure Python 3 is installed
python3 --version

# On macOS
brew install python3

# On Ubuntu/Debian
sudo apt install python3
```

## Integration with Other Tools

### Pre-commit Framework

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: security-audit
        name: Security Audit
        entry: python .github/security-audit/scripts/audit.py --staged --fail-on high
        language: python
        pass_filenames: false
```

### CI/CD Pipelines

```bash
# GitLab CI
python .github/security-audit/scripts/audit.py --all --format json > audit.json

# Jenkins
python .github/security-audit/scripts/audit.py --all --fail-on high
```

## Contributing

To add new detection patterns:

1. Research the secret format (check provider documentation)
2. Create a regex pattern (test at regex101.com)
3. Add to `patterns/secrets.json` with appropriate severity
4. Test with sample data
5. Submit PR

## License

Apache 2.0 - See repository LICENSE file.

---

*Security Audit Pipeline v1.0.0*
