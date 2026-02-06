#!/bin/bash
#
# Security Audit Pipeline - Installation Script
#
# This script installs the pre-commit hook and verifies the setup.
#
# Usage:
#   ./security-audit-pipeline/install.sh [OPTIONS]
#
# Options:
#   --uninstall    Remove the pre-commit hook
#   --check        Verify installation without making changes
#   --force        Overwrite existing pre-commit hook
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Find repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Paths
HOOKS_DIR="$REPO_ROOT/.git/hooks"
PRECOMMIT_SRC="$SCRIPT_DIR/hooks/pre-commit"
PRECOMMIT_DST="$HOOKS_DIR/pre-commit"
AUDIT_SCRIPT="$SCRIPT_DIR/scripts/audit.py"

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Security Audit Pipeline Installer${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

check_prerequisites() {
    local errors=0

    echo -e "${BLUE}Checking prerequisites...${NC}"

    # Check if in git repo
    if [ ! -d "$REPO_ROOT/.git" ]; then
        echo -e "  ${RED}✗${NC} Not a git repository"
        errors=$((errors + 1))
    else
        echo -e "  ${GREEN}✓${NC} Git repository found"
    fi

    # Check Python 3
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        echo -e "  ${GREEN}✓${NC} Python 3 found ($PYTHON_VERSION)"
    else
        echo -e "  ${RED}✗${NC} Python 3 not found"
        errors=$((errors + 1))
    fi

    # Check audit script
    if [ -f "$AUDIT_SCRIPT" ]; then
        echo -e "  ${GREEN}✓${NC} Audit script found"
    else
        echo -e "  ${RED}✗${NC} Audit script not found at $AUDIT_SCRIPT"
        errors=$((errors + 1))
    fi

    # Check pre-commit hook source
    if [ -f "$PRECOMMIT_SRC" ]; then
        echo -e "  ${GREEN}✓${NC} Pre-commit hook source found"
    else
        echo -e "  ${RED}✗${NC} Pre-commit hook source not found"
        errors=$((errors + 1))
    fi

    echo ""
    return $errors
}

install_hook() {
    local force=$1

    echo -e "${BLUE}Installing pre-commit hook...${NC}"

    # Create hooks directory if needed
    if [ ! -d "$HOOKS_DIR" ]; then
        mkdir -p "$HOOKS_DIR"
        echo -e "  ${GREEN}✓${NC} Created hooks directory"
    fi

    # Check for existing hook
    if [ -f "$PRECOMMIT_DST" ]; then
        if [ "$force" = "true" ]; then
            echo -e "  ${YELLOW}!${NC} Backing up existing pre-commit hook"
            mv "$PRECOMMIT_DST" "$PRECOMMIT_DST.backup.$(date +%Y%m%d%H%M%S)"
        else
            # Check if it's our hook
            if grep -q "Security Audit Pipeline" "$PRECOMMIT_DST" 2>/dev/null; then
                echo -e "  ${GREEN}✓${NC} Security audit hook already installed"
                return 0
            else
                echo -e "  ${YELLOW}!${NC} Existing pre-commit hook found"
                echo -e "  ${YELLOW}!${NC} Use --force to overwrite or manually integrate"
                return 1
            fi
        fi
    fi

    # Copy hook
    cp "$PRECOMMIT_SRC" "$PRECOMMIT_DST"
    chmod +x "$PRECOMMIT_DST"

    echo -e "  ${GREEN}✓${NC} Pre-commit hook installed"
    return 0
}

uninstall_hook() {
    echo -e "${BLUE}Uninstalling pre-commit hook...${NC}"

    if [ -f "$PRECOMMIT_DST" ]; then
        if grep -q "Security Audit Pipeline" "$PRECOMMIT_DST" 2>/dev/null; then
            rm "$PRECOMMIT_DST"
            echo -e "  ${GREEN}✓${NC} Pre-commit hook removed"

            # Restore backup if exists
            BACKUP=$(ls -t "$PRECOMMIT_DST.backup."* 2>/dev/null | head -1)
            if [ -n "$BACKUP" ]; then
                mv "$BACKUP" "$PRECOMMIT_DST"
                echo -e "  ${GREEN}✓${NC} Previous hook restored from backup"
            fi
        else
            echo -e "  ${YELLOW}!${NC} Existing hook is not from Security Audit Pipeline"
            echo -e "  ${YELLOW}!${NC} Not removing to preserve your custom hook"
        fi
    else
        echo -e "  ${YELLOW}!${NC} No pre-commit hook found"
    fi
}

verify_installation() {
    echo -e "${BLUE}Verifying installation...${NC}"

    local status=0

    # Check hook exists and is executable
    if [ -x "$PRECOMMIT_DST" ]; then
        echo -e "  ${GREEN}✓${NC} Pre-commit hook is executable"
    else
        echo -e "  ${RED}✗${NC} Pre-commit hook not executable"
        status=1
    fi

    # Check it's our hook
    if grep -q "Security Audit Pipeline" "$PRECOMMIT_DST" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Security audit hook identified"
    else
        echo -e "  ${YELLOW}!${NC} Hook exists but may not be security audit"
        status=1
    fi

    # Test audit script
    echo ""
    echo -e "${BLUE}Testing audit script...${NC}"
    if python3 "$AUDIT_SCRIPT" --help > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Audit script runs successfully"
    else
        echo -e "  ${RED}✗${NC} Audit script failed to run"
        status=1
    fi

    return $status
}

run_test_scan() {
    echo ""
    echo -e "${BLUE}Running test scan on repository...${NC}"
    echo ""

    python3 "$AUDIT_SCRIPT" --all --severity medium --verbose || true

    echo ""
}

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --uninstall    Remove the pre-commit hook"
    echo "  --check        Verify installation without making changes"
    echo "  --force        Overwrite existing pre-commit hook"
    echo "  --test         Run a test scan after installation"
    echo "  --help         Show this help message"
    echo ""
}

# Main
main() {
    local action="install"
    local force="false"
    local test_scan="false"

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --uninstall)
                action="uninstall"
                shift
                ;;
            --check)
                action="check"
                shift
                ;;
            --force)
                force="true"
                shift
                ;;
            --test)
                test_scan="true"
                shift
                ;;
            --help|-h)
                print_usage
                exit 0
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                print_usage
                exit 1
                ;;
        esac
    done

    print_header

    case $action in
        install)
            if ! check_prerequisites; then
                echo -e "${RED}Prerequisites check failed. Please fix the issues above.${NC}"
                exit 1
            fi

            if install_hook "$force"; then
                verify_installation
                if [ "$test_scan" = "true" ]; then
                    run_test_scan
                fi
                echo ""
                echo -e "${GREEN}Installation complete!${NC}"
                echo ""
                echo "The security audit will now run automatically before each commit."
                echo "To bypass (not recommended): git commit --no-verify"
                echo ""
            else
                exit 1
            fi
            ;;
        uninstall)
            uninstall_hook
            echo ""
            echo -e "${GREEN}Uninstallation complete.${NC}"
            ;;
        check)
            if ! check_prerequisites; then
                exit 1
            fi
            verify_installation
            ;;
    esac
}

main "$@"
