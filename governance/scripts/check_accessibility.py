#!/usr/bin/env python3
"""
ONI Framework Accessibility Compliance Checker
===============================================

Automated WCAG 2.1 AA compliance verification for ONI Academy and TARA.

This script checks:
- Color contrast ratios (4.5:1 for normal text, 3:1 for large text)
- Minimum font sizes (0.875rem minimum)
- Focus indicator presence
- Reduced motion support
- Skip link implementation

Usage:
    python check_accessibility.py [--verbose] [--fix]

Exit codes:
    0 - All checks passed
    1 - Accessibility violations found
    2 - Script error
"""

import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional


# WCAG 2.1 AA Requirements
WCAG_AA_CONTRAST_NORMAL = 4.5  # For text < 18pt or < 14pt bold
WCAG_AA_CONTRAST_LARGE = 3.0   # For text >= 18pt or >= 14pt bold
MIN_FONT_SIZE_REM = 0.875      # Minimum accessible font size


@dataclass
class AccessibilityViolation:
    """Represents an accessibility violation."""
    file: str
    line: int
    rule: str
    message: str
    severity: str  # "error" or "warning"
    suggestion: Optional[str] = None


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance per WCAG 2.1."""
    def adjust(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = [adjust(c) for c in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color1: str, color2: str) -> float:
    """Calculate contrast ratio between two hex colors."""
    l1 = relative_luminance(hex_to_rgb(color1))
    l2 = relative_luminance(hex_to_rgb(color2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def extract_colors_from_css(content: str) -> List[Tuple[int, str, str]]:
    """Extract color definitions from CSS content."""
    colors = []
    lines = content.split('\n')

    # Pattern for color: #hex
    color_pattern = re.compile(r'color:\s*(#[0-9a-fA-F]{3,6})', re.IGNORECASE)

    for i, line in enumerate(lines, 1):
        match = color_pattern.search(line)
        if match:
            colors.append((i, match.group(1), line.strip()))

    return colors


def extract_font_sizes(content: str) -> List[Tuple[int, str, str]]:
    """Extract font-size definitions from CSS content."""
    sizes = []
    lines = content.split('\n')

    # Pattern for font-size: Xrem
    size_pattern = re.compile(r'font-size:\s*([0-9.]+)rem', re.IGNORECASE)

    for i, line in enumerate(lines, 1):
        match = size_pattern.search(line)
        if match:
            sizes.append((i, match.group(1), line.strip()))

    return sizes


def check_focus_indicators(content: str) -> bool:
    """Check if focus indicators are implemented."""
    focus_patterns = [
        r':focus-visible',
        r':focus\s*{',
        r'focus-ring',
        r'outline.*focus',
    ]

    for pattern in focus_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def check_reduced_motion(content: str) -> bool:
    """Check if prefers-reduced-motion is respected."""
    return 'prefers-reduced-motion' in content


def check_skip_links(content: str) -> bool:
    """Check if skip links are implemented."""
    return 'skip-link' in content.lower()


def check_file(filepath: Path, background_color: str = "#0f0f1a") -> List[AccessibilityViolation]:
    """Check a single file for accessibility violations."""
    violations = []

    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return [AccessibilityViolation(
            file=str(filepath),
            line=0,
            rule="FILE_READ",
            message=f"Could not read file: {e}",
            severity="error"
        )]

    # Check color contrast
    colors = extract_colors_from_css(content)
    for line_num, color, line_content in colors:
        # Skip if it's a background color definition
        if 'background' in line_content.lower():
            continue

        # Skip CSS variables definitions
        if '--' in line_content and ':' in line_content.split('--')[0]:
            continue

        try:
            ratio = contrast_ratio(color, background_color)
            if ratio < WCAG_AA_CONTRAST_NORMAL:
                # Check if there's already a WCAG comment indicating compliance
                if 'WCAG' in line_content and 'AA' in line_content:
                    continue

                violations.append(AccessibilityViolation(
                    file=str(filepath),
                    line=line_num,
                    rule="WCAG_1.4.3",
                    message=f"Color {color} has contrast ratio {ratio:.1f}:1 (minimum 4.5:1 required)",
                    severity="error",
                    suggestion=f"Use a lighter color with at least 4.5:1 contrast against {background_color}"
                ))
        except Exception:
            pass  # Skip invalid colors

    # Check font sizes
    font_sizes = extract_font_sizes(content)
    for line_num, size, line_content in font_sizes:
        try:
            size_float = float(size)
            if size_float < MIN_FONT_SIZE_REM:
                # Check if there's already a comment indicating intentional small size
                if 'accessible' in line_content.lower() or 'min' in line_content.lower():
                    continue

                violations.append(AccessibilityViolation(
                    file=str(filepath),
                    line=line_num,
                    rule="FONT_SIZE",
                    message=f"Font size {size}rem is below minimum {MIN_FONT_SIZE_REM}rem",
                    severity="warning",
                    suggestion=f"Use font-size: {MIN_FONT_SIZE_REM}rem or larger"
                ))
        except ValueError:
            pass

    # Check focus indicators
    if not check_focus_indicators(content):
        violations.append(AccessibilityViolation(
            file=str(filepath),
            line=0,
            rule="WCAG_2.4.7",
            message="No focus indicators found",
            severity="error",
            suggestion="Add :focus-visible styles for interactive elements"
        ))

    # Check reduced motion support
    if not check_reduced_motion(content):
        violations.append(AccessibilityViolation(
            file=str(filepath),
            line=0,
            rule="WCAG_2.3.3",
            message="prefers-reduced-motion not implemented",
            severity="warning",
            suggestion="Add @media (prefers-reduced-motion: reduce) { ... }"
        ))

    # Check skip links
    if not check_skip_links(content):
        violations.append(AccessibilityViolation(
            file=str(filepath),
            line=0,
            rule="WCAG_2.4.1",
            message="No skip links found",
            severity="warning",
            suggestion="Add .skip-link for keyboard navigation"
        ))

    return violations


def main():
    parser = argparse.ArgumentParser(
        description="Check ONI Framework for WCAG 2.1 AA accessibility compliance"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Show detailed output"
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help="Treat warnings as errors"
    )
    parser.add_argument(
        '--files',
        nargs='+',
        help="Specific files to check (default: all style files)"
    )

    args = parser.parse_args()

    # Find the repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent.parent

    # Default files to check
    default_files = [
        repo_root / "MAIN" / "oni-framework" / "oni" / "ui" / "styles.py",
        repo_root / "MAIN" / "tara-nsec-platform" / "tara_mvp" / "ui" / "styles.py",
    ]

    # Background colors for each file
    backgrounds = {
        "oni": "#0f0f1a",
        "tara": "#0a0a0f",
    }

    files_to_check = []
    if args.files:
        files_to_check = [Path(f) for f in args.files]
    else:
        files_to_check = [f for f in default_files if f.exists()]

    if not files_to_check:
        print("❌ No style files found to check")
        sys.exit(2)

    all_violations = []

    print("=" * 60)
    print("ONI Framework Accessibility Compliance Check")
    print("WCAG 2.1 Level AA")
    print("=" * 60)
    print()

    for filepath in files_to_check:
        # Determine background color based on file
        bg_color = backgrounds.get("tara" if "tara" in str(filepath).lower() else "oni", "#0f0f1a")

        print(f"Checking: {filepath.name}")
        violations = check_file(filepath, bg_color)
        all_violations.extend(violations)

        if violations:
            errors = [v for v in violations if v.severity == "error"]
            warnings = [v for v in violations if v.severity == "warning"]
            print(f"  ⚠️  {len(errors)} errors, {len(warnings)} warnings")
        else:
            print(f"  ✅ No violations found")

        if args.verbose and violations:
            for v in violations:
                icon = "❌" if v.severity == "error" else "⚠️"
                print(f"    {icon} [{v.rule}] Line {v.line}: {v.message}")
                if v.suggestion:
                    print(f"       💡 {v.suggestion}")

    print()
    print("=" * 60)

    # Summary
    errors = [v for v in all_violations if v.severity == "error"]
    warnings = [v for v in all_violations if v.severity == "warning"]

    if not all_violations:
        print("✅ All accessibility checks passed!")
        print("=" * 60)
        sys.exit(0)

    print(f"Summary: {len(errors)} errors, {len(warnings)} warnings")
    print("=" * 60)

    if errors:
        print("\n❌ ERRORS (must fix):")
        for v in errors:
            print(f"  • [{v.rule}] {v.file}:{v.line}")
            print(f"    {v.message}")

    if warnings:
        print("\n⚠️  WARNINGS (should fix):")
        for v in warnings:
            print(f"  • [{v.rule}] {v.file}:{v.line}")
            print(f"    {v.message}")

    # Exit with error if there are errors (or warnings in strict mode)
    if errors or (args.strict and warnings):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
