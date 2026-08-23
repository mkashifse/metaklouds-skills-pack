#!/usr/bin/env python3
"""Emit the compact, repository-backed Product Manager heartbeat."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from serve_dashboard import build_dashboard_data


ACTIVE_TASK_STATUSES = {
    "BACKLOG", "READY", "IN_PROGRESS", "VERIFYING", "BLOCKED",
    "BLOCKED_BY_DRIFT", "PAUSED", "REWORK_REQUIRED", "REVERIFY_REQUIRED",
    "HUMAN_DECISION_REQUIRED",
}
PM_ALLOWED_ACTIONS = {"communicate", "prioritize", "recommend", "authorize", "instruct"}
HEARTBEAT_SIGNAL_STATUSES = {"LIVE", "RECOVERED", "ATTENTION"}


def role_action_guard(action: str) -> dict[str, str | bool]:
    normalized = action.strip().lower().replace("_", "-")
    allowed = normalized in PM_ALLOWED_ACTIONS
    return {
        "action": normalized,
        "allowed": allowed,
        "route": "Product Manager" if allowed else "PM Assistant",
        "reason": (
            "Product Manager communication/instruction boundary permits this action."
            if allowed
            else "Product Manager cannot execute this action; delegate it to the PM Assistant."
        ),
    }


def build_heartbeat(product_root: Path, dashboard_url: str = "") -> dict[str, Any]:
    data = build_dashboard_data(product_root.resolve())
    initiative = data.get("initiative", {})
    decision_meta = data.get("decisionMeta", {})
    active_tasks = [
        {
            "id": task.get("id"),
            "phase": task.get("phase", "DEVELOPMENT"),
            "assignee": task.get("owner", "Unassigned"),
            "status": task.get("status", "UNKNOWN"),
        }
        for task in data.get("tasks", [])
        if task.get("status") in ACTIVE_TASK_STATUSES
    ][:12]
    active_slices = [
        {"id": item.get("id"), "status": item.get("status")}
        for item in data.get("slices", [])
        if item.get("active") or item.get("status") in {"IN_PROGRESS", "VERIFYING", "BLOCKED", "PAUSED"}
    ][:6]
    human_decisions = [
        {"id": item.get("id"), "title": item.get("title")}
        for item in data.get("attention", [])
        if item.get("kind") in {"decision", "drift"}
    ][:6]
    open_drifts = [
        {
            "id": item.get("id"),
            "status": item.get("status"),
            "paused": item.get("blockedWorkPackages", []),
        }
        for item in data.get("drifts", [])
        if item.get("status") not in {"AUTO_RESOLVED", "CLOSED"}
    ][:6]
    heartbeat = {
        "role": "Meta PDS Product Manager",
        "role_boundary": "Communicate, prioritize, recommend, authorize, and instruct only",
        "forbidden_for_pm": ["research", "canonical writing", "coding", "testing", "artifact edits", "raw worker output"],
        "initiative": {"id": initiative.get("id", "UNKNOWN"), "title": initiative.get("name", "Unknown initiative")},
        "mode": decision_meta.get("interactionMode", "EXPLORE"),
        "phase": initiative.get("phase", "NOT_INITIALIZED"),
        "active_tasks": active_tasks,
        "active_slices": active_slices,
        "pending_human_decisions": human_decisions,
        "open_drift": open_drifts,
        "next_valid_action": initiative.get("nextAction", {}),
        "dashboard": dashboard_url or "Use serve_dashboard.py --ensure for the current project URL",
        "data_health": data.get("dataHealth", {}),
    }
    heartbeat["human_signal"] = human_signal(heartbeat)
    return heartbeat


def human_signal(heartbeat: dict[str, Any], status: str = "LIVE") -> str:
    normalized = status.strip().upper()
    if normalized not in HEARTBEAT_SIGNAL_STATUSES:
        raise ValueError(f"Unsupported heartbeat signal status: {status}")
    mode = str(heartbeat.get("mode") or "EXPLORE").upper()
    return (
        f"🟠 MetaPDS · Mode: {mode} · Heartbeat: {normalized} — "
        "If this line is missing, invoke $meta-pds."
    )


def text_heartbeat(heartbeat: dict[str, Any]) -> str:
    initiative = heartbeat["initiative"]
    lines = [
        f"HUMAN SIGNAL: {heartbeat['human_signal']}",
        f"ROLE: {heartbeat['role']} — {heartbeat['role_boundary']}",
        f"INITIATIVE: {initiative['id']} — {initiative['title']}",
        f"MODE / PHASE: {heartbeat['mode']} / {heartbeat['phase']}",
        "ACTIVE TASKS: " + (", ".join(
            f"{item['id']} {item['assignee']} [{item['status']}]" for item in heartbeat["active_tasks"]
        ) or "None"),
        "ACTIVE SLICES: " + (", ".join(
            f"{item['id']} [{item['status']}]" for item in heartbeat["active_slices"]
        ) or "None"),
        "PENDING HUMAN DECISIONS: " + (", ".join(
            str(item["id"]) for item in heartbeat["pending_human_decisions"]
        ) or "None"),
        "OPEN DRIFT: " + (", ".join(
            f"{item['id']} [{item['status']}]" for item in heartbeat["open_drift"]
        ) or "None"),
        "NEXT VALID ACTION: " + str(heartbeat.get("next_valid_action", {}).get("title") or "Review current delivery state"),
        f"DASHBOARD: {heartbeat['dashboard']}",
        "FORBIDDEN FOR PM: " + ", ".join(heartbeat["forbidden_for_pm"]),
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit the Meta PDS Product Manager heartbeat")
    parser.add_argument("product_root", type=Path)
    parser.add_argument("--dashboard-url", default="")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--signal-only", action="store_true")
    parser.add_argument(
        "--signal-status",
        choices=sorted(HEARTBEAT_SIGNAL_STATUSES),
        default="LIVE",
    )
    parser.add_argument("--assert-action", default="", help="Fail when the requested action crosses the Product Manager boundary")
    args = parser.parse_args()
    heartbeat = build_heartbeat(args.product_root, args.dashboard_url)
    heartbeat["human_signal"] = human_signal(heartbeat, args.signal_status)
    exit_code = 0
    if args.assert_action:
        heartbeat["action_guard"] = role_action_guard(args.assert_action)
        exit_code = 0 if heartbeat["action_guard"]["allowed"] else 2
    if args.signal_only:
        print(heartbeat["human_signal"])
    else:
        print(json.dumps(heartbeat, indent=2, ensure_ascii=False) if args.json else text_heartbeat(heartbeat))
    if args.assert_action and not args.json:
        guard = heartbeat["action_guard"]
        print(f"ACTION GUARD: {guard['action']} — {'ALLOWED' if guard['allowed'] else 'BLOCKED'}; route: {guard['route']}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
