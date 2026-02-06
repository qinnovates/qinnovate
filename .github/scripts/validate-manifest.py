#!/usr/bin/env python3
"""Validate docs/content-manifest.json.

Checks:
  - All `path` entries resolve to real files in the repo
  - No duplicate document IDs
  - No duplicate category IDs
  - Required fields present on every document
  - Valid badge and color values
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "docs" / "content-manifest.json"

VALID_BADGES = {"whitepaper", "techdoc", "blog", "guide", "reference", "live"}
VALID_COLORS = {"blue", "purple", "cyan", "pink", "amber", "emerald"}
REQUIRED_DOC_FIELDS = {"id", "title", "description", "badge"}


def main():
    errors = []

    if not MANIFEST_PATH.exists():
        print(f"FAIL: Manifest not found at {MANIFEST_PATH}")
        sys.exit(1)

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    # Check _meta
    meta = manifest.get("_meta", {})
    if not meta.get("base_url"):
        errors.append("_meta.base_url is missing")
    if not meta.get("repo"):
        errors.append("_meta.repo is missing")

    categories = manifest.get("categories", [])
    if not categories:
        errors.append("No categories found")

    seen_cat_ids = set()
    seen_doc_ids = set()
    total_docs = 0

    for cat in categories:
        cat_id = cat.get("id", "<missing>")

        # Category-level checks
        if cat_id in seen_cat_ids:
            errors.append(f"Duplicate category ID: {cat_id}")
        seen_cat_ids.add(cat_id)

        if not cat.get("title"):
            errors.append(f"Category {cat_id}: missing title")

        color = cat.get("color", "")
        if color not in VALID_COLORS:
            errors.append(f"Category {cat_id}: invalid color '{color}' (valid: {VALID_COLORS})")

        documents = cat.get("documents", [])
        if not documents:
            errors.append(f"Category {cat_id}: no documents")

        for doc in documents:
            total_docs += 1
            doc_id = doc.get("id", "<missing>")

            # Required fields
            for field in REQUIRED_DOC_FIELDS:
                if not doc.get(field):
                    errors.append(f"Doc {doc_id}: missing required field '{field}'")

            # Duplicate ID
            if doc_id in seen_doc_ids:
                errors.append(f"Duplicate document ID: {doc_id}")
            seen_doc_ids.add(doc_id)

            # Badge validation
            badge = doc.get("badge", "")
            if badge not in VALID_BADGES:
                errors.append(f"Doc {doc_id}: invalid badge '{badge}' (valid: {VALID_BADGES})")

            # Path or URL required
            path = doc.get("path")
            url = doc.get("url")

            if not path and not url:
                errors.append(f"Doc {doc_id}: must have either 'path' or 'url'")

            # Verify local path exists
            if path:
                full_path = REPO_ROOT / path
                if not full_path.exists():
                    errors.append(f"Doc {doc_id}: path not found: {path}")

    # Report
    if errors:
        print(f"FAIL: {len(errors)} error(s) in {total_docs} documents:\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"OK: {total_docs} documents across {len(categories)} categories — all paths valid.")
        sys.exit(0)


if __name__ == "__main__":
    main()
