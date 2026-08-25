#!/usr/bin/env python3
"""Permission-scoped Product Ledger updater."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from solo_founder_core import (
    CLASSIFICATIONS,
    LAYERS,
    MODES,
    WORK_STATUSES,
    ArtifactError,
    atomic_write_yaml,
    file_lock,
    read_yaml,
    validate_ledger,
)

SPECIALIST_TRANSITIONS = {
    "READY": {"ACTIVE", "BLOCKED"},
    "ACTIVE": {"VERIFYING", "BLOCKED"},
    "BLOCKED": {"ACTIVE"},
    "REWORK": {"ACTIVE", "BLOCKED"},
}


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def find_work(ledger: dict, work_id: str) -> dict:
    for item in ledger["work"]:
        if item.get("id") == work_id:
            return item
    raise ArtifactError(f"Unknown Work ID: {work_id}")


def create_work(ledger: dict, args: argparse.Namespace) -> dict:
    if args.actor != "PM":
        raise ArtifactError("Only the PM can create Work Packages")
    if any(item.get("id") == args.create_work for item in ledger["work"]):
        raise ArtifactError(f"Duplicate Work ID: {args.create_work}")
    if args.classification not in CLASSIFICATIONS:
        raise ArtifactError("--classification is required and must be valid")
    if not args.title or not args.owner:
        raise ArtifactError("--title and --owner are required when creating work")
    item = {
        "id": args.create_work,
        "initiative_id": args.initiative_id,
        "title": args.title,
        "instruction": args.instruction or "",
        "expected_outcome": args.expected_outcome or "",
        "classification": args.classification,
        "workstream": args.workstream or "PRODUCT",
        "activity": args.activity or "PLANNING",
        "execution": "DIRECT" if args.classification == "TRIVIAL" else "DELEGATED",
        "owner": args.owner,
        "status": args.status or "PENDING",
        "priority": args.priority or "P2",
        "depends_on": [],
        "linked_truth_ids": [],
        "linked_slice_ids": [],
        "owned_paths": [],
        "acceptance_criteria": args.acceptance or [],
        "created_at": now(),
        "started_at": None,
        "updated_at": now(),
        "completed_at": None,
        "result": None,
        "evidence": [],
        "blocker": None,
    }
    ledger["work"].append(item)
    return item


def update_work(item: dict, args: argparse.Namespace) -> None:
    if args.actor == "SPECIALIST":
        if not args.identity or item.get("owner") != args.identity:
            raise ArtifactError(
                "Specialists may update only work assigned to their identity"
            )
        if item.get("status") in {"DONE", "CANCELLED"}:
            raise ArtifactError("Specialists cannot update terminal work")
        if args.status:
            allowed = SPECIALIST_TRANSITIONS.get(item["status"], set())
            if args.status not in allowed:
                raise ArtifactError(
                    f"Specialist transition {item['status']} → {args.status} is not allowed"
                )
            if args.status == "VERIFYING" and not (
                args.result and (args.evidence or item.get("evidence"))
            ):
                raise ArtifactError("VERIFYING requires result and evidence")
    if args.status:
        if args.status not in WORK_STATUSES:
            raise ArtifactError(f"Invalid work status: {args.status}")
        item["status"] = args.status
        if args.status == "ACTIVE" and not item.get("started_at"):
            item["started_at"] = now()
        if args.status == "DONE":
            if args.actor != "PM":
                raise ArtifactError("Only the PM may mark work DONE")
            if not (args.result or item.get("result")) or not (
                args.evidence or item.get("evidence")
            ):
                raise ArtifactError("DONE requires a verified result and evidence")
            item["completed_at"] = now()
        if args.status == "BLOCKED" and not (args.blocker or item.get("blocker")):
            raise ArtifactError("BLOCKED requires a blocker")
    if args.result is not None:
        item["result"] = args.result
    if args.evidence:
        existing = list(item.get("evidence") or [])
        item["evidence"] = existing + [
            value for value in args.evidence if value not in existing
        ]
    if args.blocker is not None:
        item["blocker"] = args.blocker or None
    item["updated_at"] = now()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product_root", type=Path)
    parser.add_argument("--actor", choices=["PM", "SPECIALIST"], required=True)
    parser.add_argument("--identity")
    parser.add_argument("--create-work")
    parser.add_argument("--work-id")
    parser.add_argument("--initiative-id", default="INIT-0001")
    parser.add_argument("--title")
    parser.add_argument("--instruction")
    parser.add_argument("--expected-outcome")
    parser.add_argument("--classification")
    parser.add_argument("--workstream")
    parser.add_argument("--activity")
    parser.add_argument("--owner")
    parser.add_argument("--priority")
    parser.add_argument("--acceptance", action="append")
    parser.add_argument("--status")
    parser.add_argument("--result")
    parser.add_argument("--evidence", action="append")
    parser.add_argument("--blocker")
    parser.add_argument("--mode")
    parser.add_argument("--layer")
    args = parser.parse_args()

    root = args.product_root.resolve()
    base = root / "docs" / "solo-founder"
    path = base / "product-ledger.yaml"
    try:
        with file_lock(base / ".product-ledger.lock"):
            ledger = read_yaml(path)
            validate_ledger(ledger)
            if args.actor != "PM" and (args.mode or args.layer or args.create_work):
                raise ArtifactError(
                    "Specialists cannot change PM context or create work"
                )
            if args.mode:
                if args.mode not in MODES:
                    raise ArtifactError(f"Invalid Mode: {args.mode}")
                ledger["current"]["mode"] = args.mode
            if args.layer:
                if args.layer not in LAYERS:
                    raise ArtifactError(f"Invalid Layer: {args.layer}")
                ledger["current"]["layer"] = args.layer
            if args.create_work:
                item = create_work(ledger, args)
            elif args.work_id:
                item = find_work(ledger, args.work_id)
                update_work(item, args)
            elif not (args.mode or args.layer):
                raise ArtifactError(
                    "Provide --create-work, --work-id, --mode, or --layer"
                )
            ledger["updated_at"] = now()
            ledger["updated_by"] = args.identity or args.actor
            ledger["current"]["active_work_ids"] = [
                work["id"]
                for work in ledger["work"]
                if work["status"] not in {"DONE", "CANCELLED"}
            ]
            validate_ledger(ledger)
            atomic_write_yaml(path, ledger)
    except (ArtifactError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Product Ledger updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
