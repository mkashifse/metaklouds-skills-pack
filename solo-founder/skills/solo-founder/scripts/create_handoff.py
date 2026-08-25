#!/usr/bin/env python3
"""Create the typed return envelope for one delegated Work Package."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from solo_founder_core import (
    ENGINEER_ROLES,
    HANDOFF_PAYLOAD_SECTIONS,
    ArtifactError,
    read_yaml,
    validate_ledger,
)


def find_work(ledger: dict, work_id: str) -> dict:
    for item in ledger["work"]:
        if item.get("id") == work_id:
            return item
    raise ArtifactError(f"Unknown Work ID: {work_id}")


def type_payload(handoff_type: str) -> str:
    blocks: list[str] = []
    for heading in HANDOFF_PAYLOAD_SECTIONS[handoff_type]:
        blocks.extend(
            [
                f"## {heading}",
                "",
                "<!-- Required typed payload. -->",
                "",
            ]
        )
    return "\n".join(blocks).rstrip()


def create(product_root: Path, work_id: str, identity: str) -> Path:
    ledger_path = product_root / "docs" / "solo-founder" / "product-ledger.yaml"
    ledger = read_yaml(ledger_path)
    validate_ledger(ledger)
    if ledger.get("schema_version") != 3:
        raise ArtifactError("Update the Product Ledger before creating a handoff")
    item = find_work(ledger, work_id)
    if item.get("role") not in ENGINEER_ROLES or item.get("execution") != "DELEGATED":
        raise ArtifactError("Only delegated engineer work has a handoff")
    if item.get("owner") != identity:
        raise ArtifactError("Only the assigned engineer may create this handoff")
    handoff_type = str(item["handoff_type"])
    relative_path = Path(str(item["handoff_path"]))
    target = product_root / relative_path
    if target.exists():
        raise ArtifactError(f"Handoff already exists: {relative_path}")
    template_path = (
        Path(__file__).resolve().parent.parent / "assets" / "handoff-template.md"
    )
    content = template_path.read_text(encoding="utf-8")
    replacements = {
        "{{WORK_ID}}": work_id,
        "{{HANDOFF_TYPE}}": handoff_type,
        "{{PRODUCER_ROLE}}": str(item["role"]),
        "{{PRODUCER_ID}}": identity,
        "{{CREATED_AT}}": datetime.now().astimezone().isoformat(timespec="seconds"),
        "{{TYPE_PAYLOAD}}": type_payload(handoff_type),
    }
    for marker, value in replacements.items():
        content = content.replace(marker, value)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")
    return relative_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product_root", type=Path)
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--identity", required=True)
    args = parser.parse_args()
    try:
        path = create(args.product_root.resolve(), args.work_id, args.identity)
    except (ArtifactError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
