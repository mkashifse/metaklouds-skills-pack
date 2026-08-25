#!/usr/bin/env python3
"""Permission-scoped Product Ledger updater."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from solo_founder_core import (
    CLASSIFICATIONS,
    ENGINEER_ROLES,
    HANDOFF_TYPES,
    ISSUE_KINDS,
    ISSUE_RESOLUTION_METHODS,
    LAYERS,
    MODES,
    ROLES,
    WORK_STATUSES,
    ArtifactError,
    atomic_write_yaml,
    file_lock,
    handoff_path_for,
    read_yaml,
    upgrade_ledger,
    validate_handoff_file,
    validate_ledger,
    validate_submitted_handoff,
)

ENGINEER_TRANSITIONS = {
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


def find_issue(ledger: dict, issue_id: str) -> dict:
    for item in ledger["issues"]:
        if item.get("id") == issue_id:
            return item
    raise ArtifactError(f"Unknown Issue ID: {issue_id}")


def string_list(value: object, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ArtifactError(f"{label} must be a list of non-empty strings")
    return list(dict.fromkeys(item.strip() for item in value))


def resolution_from_event(event: dict, method: str) -> dict:
    action = str(event.get("resolution_action") or "").strip()
    evidence = string_list(event.get("resolution_evidence"), "resolution_evidence")
    if not action or not evidence:
        raise ArtifactError("Issue resolution requires action and evidence")
    resolved_by = {
        "AUTO_WITHIN_AUTHORITY": "PM",
        "HUMAN_APPROVED": "HUMAN",
        "EXTERNAL_RESOLUTION": str(event.get("resolved_by") or "EXTERNAL"),
    }[method]
    return {
        "method": method,
        "action": action,
        "evidence": evidence,
        "resolved_by": resolved_by,
        "resolved_at": now(),
    }


def log_issue(ledger: dict, event: dict) -> None:
    issue_id = str(event.get("id") or "")
    if any(item.get("id") == issue_id for item in ledger["issues"]):
        raise ArtifactError(f"Duplicate Issue ID: {issue_id}")
    kind = str(event.get("kind") or "")
    if kind not in ISSUE_KINDS:
        raise ArtifactError(f"Invalid Issue kind: {kind}")
    summary = str(event.get("summary") or "").strip()
    if not summary:
        raise ArtifactError("Issue LOG requires summary")
    disposition = str(event.get("disposition") or "OPEN")
    if disposition not in {"OPEN", "AWAITING_HUMAN", "AUTO_RESOLVED"}:
        raise ArtifactError(f"Invalid Issue disposition: {disposition}")
    item = {
        "id": issue_id,
        "kind": kind,
        "summary": summary,
        "description": str(event.get("description") or "").strip() or None,
        "status": "RESOLVED" if disposition == "AUTO_RESOLVED" else disposition,
        "severity": str(event.get("severity") or "UNSET"),
        "human_approval_required": disposition == "AWAITING_HUMAN",
        "recommendation": str(event.get("recommendation") or "").strip() or None,
        "impact": str(event.get("impact") or "").strip() or None,
        "evidence": string_list(event.get("evidence"), "evidence"),
        "linked_work_ids": string_list(event.get("linked_work_ids"), "linked_work_ids"),
        "linked_truth_ids": string_list(
            event.get("linked_truth_ids"), "linked_truth_ids"
        ),
        "detected_at": str(event.get("detected_at") or now()),
        "resolution": None,
    }
    if disposition == "AWAITING_HUMAN" and not (
        item["recommendation"] and item["impact"]
    ):
        raise ArtifactError("AWAITING_HUMAN requires one recommendation and its impact")
    if disposition == "AUTO_RESOLVED":
        item["resolution"] = resolution_from_event(event, "AUTO_WITHIN_AUTHORITY")
    ledger["issues"].append(item)


def resolve_issue(ledger: dict, event: dict) -> None:
    item = find_issue(ledger, str(event.get("id") or ""))
    if item.get("status") == "RESOLVED":
        raise ArtifactError(f"Issue is already resolved: {item['id']}")
    method = str(event.get("resolution_method") or "")
    if method not in ISSUE_RESOLUTION_METHODS:
        raise ArtifactError(f"Invalid Issue resolution method: {method}")
    if item.get("status") == "AWAITING_HUMAN" and method != "HUMAN_APPROVED":
        raise ArtifactError("AWAITING_HUMAN requires HUMAN_APPROVED resolution")
    if item.get("status") == "OPEN" and method == "HUMAN_APPROVED":
        raise ArtifactError("OPEN Issue cannot claim HUMAN_APPROVED resolution")
    item["status"] = "RESOLVED"
    item["human_approval_required"] = False
    item["resolution"] = resolution_from_event(event, method)
    new_truth = string_list(event.get("linked_truth_ids"), "linked_truth_ids")
    item["linked_truth_ids"] = list(
        dict.fromkeys(list(item.get("linked_truth_ids") or []) + new_truth)
    )


def apply_issue_events(ledger: dict, payload: str) -> None:
    try:
        events = json.loads(payload)
    except json.JSONDecodeError as error:
        raise ArtifactError(f"Invalid Issue events JSON: {error.msg}") from error
    if not isinstance(events, list) or not events or len(events) > 100:
        raise ArtifactError("Issue exit sweep requires 1 to 100 events")
    for event in events:
        if not isinstance(event, dict):
            raise ArtifactError("Each Issue event must be an object")
        action = str(event.get("action") or "LOG")
        if action == "LOG":
            log_issue(ledger, event)
        elif action == "RESOLVE":
            resolve_issue(ledger, event)
        else:
            raise ArtifactError(f"Invalid Issue event action: {action}")


def create_work(ledger: dict, args: argparse.Namespace) -> dict:
    if args.actor != "PM":
        raise ArtifactError("Only the PM can create Work Packages")
    if any(item.get("id") == args.create_work for item in ledger["work"]):
        raise ArtifactError(f"Duplicate Work ID: {args.create_work}")
    if args.classification not in CLASSIFICATIONS:
        raise ArtifactError("--classification is required and must be valid")
    if not args.title:
        raise ArtifactError("--title is required when creating work")
    role = args.role or "PM"
    owner = args.owner or ("PM" if role == "PM" else None)
    if role not in ROLES:
        raise ArtifactError(
            "--role must be PM, PROTOTYPE_ENGINEER, or FULL_STACK_ENGINEER"
        )
    activity = args.activity or "PLANNING"
    workstream = args.workstream or (
        "PROTOTYPE"
        if role == "PROTOTYPE_ENGINEER"
        else "FULL_STACK"
        if role == "FULL_STACK_ENGINEER"
        else "PRODUCT"
    )
    if role == "PM" and owner != "PM":
        raise ArtifactError("PM work requires --owner PM")
    if role == "PM" and (args.delegation_reason or args.handoff_type):
        raise ArtifactError("Direct PM work cannot have delegation or handoff fields")
    if role == "PROTOTYPE_ENGINEER" and workstream != "PROTOTYPE":
        raise ArtifactError("Prototype Engineer work requires --workstream PROTOTYPE")
    if role == "FULL_STACK_ENGINEER" and workstream not in {
        "FRONTEND",
        "BACKEND",
        "FULL_STACK",
    }:
        raise ArtifactError(
            "Full-Stack Engineer work requires FRONTEND, BACKEND, or FULL_STACK focus"
        )
    if role in ENGINEER_ROLES:
        if not owner:
            raise ArtifactError("Delegated work requires --owner identity")
        if args.delegation_reason != "PARALLELISM":
            raise ArtifactError(
                "Engineer delegation requires --delegation-reason PARALLELISM"
            )
        if args.handoff_type not in HANDOFF_TYPES:
            raise ArtifactError("Engineer delegation requires a valid --handoff-type")
    handoff_path = (
        handoff_path_for(args.create_work, args.handoff_type)
        if role in ENGINEER_ROLES
        else None
    )
    item = {
        "id": args.create_work,
        "initiative_id": args.initiative_id,
        "title": args.title,
        "instruction": args.instruction or "",
        "expected_outcome": args.expected_outcome or "",
        "classification": args.classification,
        "workstream": workstream,
        "activity": activity,
        "execution": "DIRECT" if role == "PM" else "DELEGATED",
        "role": role,
        "owner": owner,
        "delegation_reason": args.delegation_reason if role in ENGINEER_ROLES else None,
        "handoff_type": args.handoff_type if role in ENGINEER_ROLES else None,
        "handoff_path": handoff_path,
        "handoff_submitted_at": None,
        "handoff_submitted_hash": None,
        "handoff_consumed_at": None,
        "status": args.status or "PENDING",
        "priority": args.priority or "P2",
        "depends_on": [],
        "linked_truth_ids": [],
        "linked_slice_ids": [],
        "owned_paths": args.owned_path or [],
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


def update_work(product_root: Path, item: dict, args: argparse.Namespace) -> None:
    previous_status = item.get("status")
    submitted_hash: str | None = None
    if args.actor == "ENGINEER":
        if item.get("role") not in ENGINEER_ROLES:
            raise ArtifactError("Engineers cannot update PM-owned work")
        if not args.identity or item.get("owner") != args.identity:
            raise ArtifactError("Engineers may update only their assigned work")
        if item.get("status") in {"VERIFYING", "DONE", "CANCELLED"}:
            raise ArtifactError("Engineer work is frozen pending PM action")
        if args.status:
            allowed = ENGINEER_TRANSITIONS.get(item["status"], set())
            if args.status not in allowed:
                raise ArtifactError(
                    f"Engineer transition {item['status']} → {args.status} is not allowed"
                )
    if args.status:
        if args.status not in WORK_STATUSES:
            raise ArtifactError(f"Invalid work status: {args.status}")
        if args.status == "VERIFYING" and item.get("execution") == "DELEGATED":
            if not (args.result or item.get("result")) or not (
                args.evidence or item.get("evidence")
            ):
                raise ArtifactError("VERIFYING requires result and evidence")
            submitted_hash = validate_handoff_file(product_root, item)
        item["status"] = args.status
        if args.status == "ACTIVE" and not item.get("started_at"):
            item["started_at"] = now()
        if args.status == "ACTIVE" and previous_status == "REWORK":
            item["handoff_submitted_at"] = None
            item["handoff_submitted_hash"] = None
            item["handoff_consumed_at"] = None
        if args.status == "VERIFYING" and item.get("execution") == "DELEGATED":
            item["handoff_submitted_at"] = now()
            item["handoff_submitted_hash"] = submitted_hash
            item["handoff_consumed_at"] = None
        if args.status in {"DONE", "REWORK"} and item.get("execution") == "DELEGATED":
            if previous_status != "VERIFYING":
                raise ArtifactError(
                    "PM can consume a delegated handoff only from VERIFYING"
                )
            validate_submitted_handoff(product_root, item)
            item["handoff_consumed_at"] = now()
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
    parser.add_argument(
        "--actor", choices=["PM", "ENGINEER", "SPECIALIST"], required=True
    )
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
    parser.add_argument("--role")
    parser.add_argument("--owner")
    parser.add_argument("--delegation-reason", choices=["PARALLELISM"])
    parser.add_argument("--handoff-type", choices=sorted(HANDOFF_TYPES))
    parser.add_argument("--owned-path", action="append")
    parser.add_argument("--priority")
    parser.add_argument("--acceptance", action="append")
    parser.add_argument("--status")
    parser.add_argument("--result")
    parser.add_argument("--evidence", action="append")
    parser.add_argument("--blocker")
    parser.add_argument("--issue-events-json")
    parser.add_argument("--mode")
    parser.add_argument("--layer")
    args = parser.parse_args()
    if args.actor == "SPECIALIST":
        args.actor = "ENGINEER"

    root = args.product_root.resolve()
    base = root / "docs" / "solo-founder"
    path = base / "product-ledger.yaml"
    try:
        with file_lock(base / ".product-ledger.lock"):
            ledger = read_yaml(path)
            validate_ledger(ledger)
            upgrade_ledger(ledger)
            if args.actor != "PM" and (
                args.mode or args.layer or args.create_work or args.issue_events_json
            ):
                raise ArtifactError(
                    "Engineers cannot change PM context, create work, or write Issues"
                )
            if args.issue_events_json and any(
                (args.mode, args.layer, args.create_work, args.work_id)
            ):
                raise ArtifactError(
                    "Issue exit sweep cannot be combined with another Ledger operation"
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
                update_work(root, item, args)
            elif args.issue_events_json:
                apply_issue_events(ledger, args.issue_events_json)
            elif not (args.mode or args.layer):
                raise ArtifactError(
                    "Provide --create-work, --work-id, --issue-events-json, --mode, or --layer"
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
