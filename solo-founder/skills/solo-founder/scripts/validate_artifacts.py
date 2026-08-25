#!/usr/bin/env python3
"""Validate Solo Founder canonical artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from solo_founder_core import (
    ArtifactError,
    read_yaml,
    validate_ledger,
    validate_submitted_handoff,
    validate_truth,
)


def validate_slices(base: Path) -> list[str]:
    diagnostics: list[str] = []
    slices = base / "slices"
    if not slices.exists():
        return diagnostics
    for path in sorted(slices.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            diagnostics.append(f"{path}: missing YAML frontmatter")
            continue
        if "# Fat Slice" not in text:
            diagnostics.append(f"{path}: missing '# Fat Slice' heading")
        if not re.search(r"^### US-[A-Za-z0-9-]+ — .+$", text, re.MULTILINE):
            diagnostics.append(f"{path}: requires at least one User Story")
        if "**Acceptance criteria:**" not in text:
            diagnostics.append(f"{path}: missing acceptance criteria")
    return diagnostics


def run(product_root: Path) -> list[str]:
    base = product_root / "docs" / "solo-founder"
    diagnostics: list[str] = []
    try:
        validate_truth(read_yaml(base / "canonical-truth.yaml"))
    except (ArtifactError, OSError) as error:
        diagnostics.append(str(error))
    try:
        ledger = read_yaml(base / "product-ledger.yaml")
        validate_ledger(ledger)
        if ledger.get("schema_version") in {3, 4}:
            for item in ledger["work"]:
                if (
                    item.get("execution") == "DELEGATED"
                    and item.get("status")
                    in {
                        "VERIFYING",
                        "DONE",
                        "REWORK",
                    }
                    and item.get("delegation_reason") == "PARALLELISM"
                ):
                    validate_submitted_handoff(product_root, item)
    except (ArtifactError, OSError) as error:
        diagnostics.append(str(error))
    diagnostics.extend(validate_slices(base))
    return diagnostics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product_root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    diagnostics = run(args.product_root.resolve())
    if args.json:
        print(json.dumps({"valid": not diagnostics, "diagnostics": diagnostics}))
    elif diagnostics:
        for diagnostic in diagnostics:
            print(f"ERROR: {diagnostic}")
    else:
        print("Solo Founder artifacts are valid.")
    return 1 if diagnostics else 0


if __name__ == "__main__":
    sys.exit(main())
