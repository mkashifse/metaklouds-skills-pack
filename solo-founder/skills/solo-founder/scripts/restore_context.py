#!/usr/bin/env python3
"""Initialize a governed product or print a compact local context snapshot."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from solo_founder_core import (
    LAYERS,
    ArtifactError,
    read_yaml,
    validate_ledger,
    validate_truth,
)

START = "<!-- SOLO-FOUNDER:START -->"
END = "<!-- SOLO-FOUNDER:END -->"
BOOTSTRAP = f"""{START}
## Solo Founder

This product is governed by `$solo-founder`. For product discovery, planning,
prototype, implementation, QA, release, or operations work, load that skill and
restore context from `docs/solo-founder/canonical-truth.yaml` and
`docs/solo-founder/product-ledger.yaml` before acting. The Solo Founder Product
Manager is the Human's single contact, handles research, documentation,
planning, and trivial non-code work directly, and
assigns prototype code to a Prototype Engineer and production code end-to-end
to one Full-Stack Engineer by default. Additional Full-Stack Engineers are used
only when parallel execution is clearly faster.
{END}
"""

REPOSITORY_DIRECTORIES = (
    "docs/solo-founder/research",
    "docs/solo-founder/slices",
    "docs/solo-founder/reports",
    "docs/solo-founder/architecture",
    "docs/solo-founder/handoffs",
    "prototypes/frontend",
    "prototypes/mobile",
    "apps/frontend",
    "apps/mobile",
    "apps/backend",
    "packages/contracts",
    "packages/domain",
    "packages/ui",
    "packages/shared",
    "packages/config",
    "infrastructure",
    "tests/e2e",
    "tests/integration",
)


def install_bootstrap(product_root: Path) -> None:
    path = product_root / "AGENTS.md"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if START in current and END in current:
        prefix, rest = current.split(START, 1)
        _old, suffix = rest.split(END, 1)
        updated = prefix.rstrip() + "\n\n" + BOOTSTRAP + suffix.lstrip("\n")
    else:
        updated = current.rstrip() + ("\n\n" if current.strip() else "") + BOOTSTRAP
    path.write_text(updated.rstrip() + "\n", encoding="utf-8")


def initialize(product_root: Path, skill_root: Path) -> None:
    base = product_root / "docs" / "solo-founder"
    for relative_path in REPOSITORY_DIRECTORIES:
        directory = product_root / relative_path
        directory.mkdir(parents=True, exist_ok=True)
        marker = directory / ".gitkeep"
        if not any(directory.iterdir()):
            marker.touch()
    assets = skill_root / "assets"
    targets = {
        assets / "canonical-truth-template.yaml": base / "canonical-truth.yaml",
        assets / "product-ledger-template.yaml": base / "product-ledger.yaml",
    }
    for source, target in targets.items():
        if not target.exists():
            shutil.copyfile(source, target)
    install_bootstrap(product_root)


def summarize(product_root: Path) -> dict[str, object]:
    base = product_root / "docs" / "solo-founder"
    truth = read_yaml(base / "canonical-truth.yaml")
    ledger = read_yaml(base / "product-ledger.yaml")
    validate_truth(truth)
    validate_ledger(ledger)
    proposed: list[str] = []
    approved_count = 0
    for layer in LAYERS:
        for item in truth["truth"][layer]:
            if item["status"] == "PROPOSED":
                proposed.append(item["id"])
            else:
                approved_count += 1
    active = [
        item["id"]
        for item in ledger["work"]
        if item["status"] not in {"DONE", "CANCELLED"}
    ]
    blockers = [item["id"] for item in ledger["work"] if item["status"] == "BLOCKED"]
    current = ledger["current"]
    return {
        "role": "Solo Founder Product Manager",
        "initiative": truth["initiative_id"],
        "mode": current["mode"],
        "layer": current["layer"],
        "affected_layers": current["affected_layers"],
        "approved_truth_count": approved_count,
        "proposed_truth": proposed,
        "active_work": active,
        "blockers": blockers,
        "next_action": current.get("next_recommended_action"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product_root", type=Path)
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    product_root = args.product_root.resolve()
    skill_root = Path(__file__).resolve().parent.parent
    try:
        if args.init:
            initialize(product_root, skill_root)
        snapshot = summarize(product_root)
    except (ArtifactError, OSError) as error:
        print(f"ATTENTION: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(snapshot, ensure_ascii=False))
    else:
        print(f"ROLE: {snapshot['role']}")
        print(f"INITIATIVE: {snapshot['initiative']}")
        print(f"MODE / LAYER: {snapshot['mode']} / {snapshot['layer']}")
        print(f"PROPOSED TRUTH: {', '.join(snapshot['proposed_truth']) or 'none'}")
        print(f"ACTIVE WORK: {', '.join(snapshot['active_work']) or 'none'}")
        print(f"BLOCKERS: {', '.join(snapshot['blockers']) or 'none'}")
        next_action = snapshot["next_action"] or {}
        print(f"NEXT ACTION: {next_action.get('title') or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
