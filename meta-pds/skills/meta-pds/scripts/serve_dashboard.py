#!/usr/bin/env python3
"""Serve the Meta PDS dashboard directly from canonical product artifacts."""

from __future__ import annotations

import argparse
import ast
import json
import re
import tempfile
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


TERMINAL_PACKAGE_STATUSES = {"DONE"}
ACTIVE_PACKAGE_STATUSES = {"IN_PROGRESS", "VERIFYING", "REWORK_REQUIRED", "REVERIFY_REQUIRED"}
TERMINAL_SLICE_STATUSES = {"RELEASED", "OUTCOME_VALIDATED"}
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


class ArtifactError(RuntimeError):
    pass


def strip_comment(value: str) -> str:
    quote: str | None = None
    for index, character in enumerate(value):
        if character in {'"', "'"}:
            if quote == character:
                quote = None
            elif quote is None:
                quote = character
        elif character == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.rstrip()


def split_inline(value: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    for index, character in enumerate(value):
        if character in {'"', "'"}:
            if quote == character:
                quote = None
            elif quote is None:
                quote = character
        elif quote is None:
            if character in "[{":
                depth += 1
            elif character in "]}":
                depth -= 1
            elif character == "," and depth == 0:
                parts.append(value[start:index].strip())
                start = index + 1
    parts.append(value[start:].strip())
    return [part for part in parts if part]


def parse_scalar(value: str) -> Any:
    value = strip_comment(value).strip()
    if not value:
        return None
    lowered = value.lower()
    if lowered in {"null", "~"}:
        return None
    if lowered in {"true", "false"}:
        return lowered == "true"
    if value.startswith("[") and value.endswith("]"):
        return [parse_scalar(part) for part in split_inline(value[1:-1])]
    if value.startswith("{") and value.endswith("}"):
        result: dict[str, Any] = {}
        for part in split_inline(value[1:-1]):
            key, separator, item = part.partition(":")
            if not separator:
                raise ArtifactError(f"Invalid inline YAML mapping: {value}")
            result[str(parse_scalar(key.strip()))] = parse_scalar(item)
        return result
    if value[:1] in {'"', "'"} and value[-1:] == value[:1]:
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?(?:\d+\.\d*|\d*\.\d+)", value):
        return float(value)
    return value


def yaml_lines(text: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if "\t" in raw[:indent]:
            raise ArtifactError("Tabs are not supported in Meta PDS YAML")
        result.append((indent, strip_comment(raw.strip())))
    return result


def parse_yaml_block(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines) or lines[index][0] < indent:
        return None, index
    if lines[index][1].startswith("- ") or lines[index][1] == "-":
        items: list[Any] = []
        while index < len(lines) and lines[index][0] == indent and lines[index][1].startswith("-"):
            content = lines[index][1][1:].strip()
            index += 1
            if not content:
                item, index = parse_yaml_block(lines, index, indent + 2)
            elif re.match(r"^[A-Za-z_][A-Za-z0-9_-]*\s*:", content):
                key, value = content.split(":", 1)
                item = {key.strip(): parse_scalar(value)}
                if index < len(lines) and lines[index][0] > indent:
                    continuation, index = parse_yaml_block(lines, index, indent + 2)
                    if isinstance(continuation, dict):
                        item.update(continuation)
                    elif item[key.strip()] is None:
                        item[key.strip()] = continuation
            else:
                item = parse_scalar(content)
                if index < len(lines) and lines[index][0] > indent:
                    _, index = parse_yaml_block(lines, index, indent + 2)
            items.append(item)
        return items, index

    mapping: dict[str, Any] = {}
    while index < len(lines) and lines[index][0] == indent and not lines[index][1].startswith("-"):
        content = lines[index][1]
        key, separator, value = content.partition(":")
        if not separator:
            raise ArtifactError(f"Invalid YAML line: {content}")
        key = key.strip()
        index += 1
        parsed = parse_scalar(value)
        if parsed is None and index < len(lines) and lines[index][0] > indent:
            parsed, index = parse_yaml_block(lines, index, lines[index][0])
        mapping[key] = parsed
    return mapping, index


def parse_yaml(text: str) -> dict[str, Any]:
    lines = yaml_lines(text)
    if not lines:
        return {}
    value, index = parse_yaml_block(lines, 0, lines[0][0])
    if index != len(lines) or not isinstance(value, dict):
        raise ArtifactError("Meta PDS YAML must contain one top-level mapping")
    return value


def read_yaml(path: Path, required: bool = False) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise ArtifactError(f"Missing canonical artifact: {path}")
        return {}
    return parse_yaml(path.read_text(encoding="utf-8"))


def read_markdown(path: Path) -> tuple[dict[str, Any], str]:
    if not path.exists():
        raise ArtifactError(f"Missing canonical artifact: {path}")
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", text, re.DOTALL)
    if not match:
        raise ArtifactError(f"Markdown artifact requires YAML frontmatter: {path}")
    return parse_yaml(match.group(1)), match.group(2)


def first_heading(body: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled"


def markdown_section(body: str, heading: str, level: int = 2) -> str:
    prefix = "#" * level
    match = re.search(
        rf"^{prefix}\s+{re.escape(heading)}\s*$\n(.*?)(?=^{'#' * level}\s+|\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def normalized_paragraph(value: str) -> str:
    paragraph = value.split("\n\n", 1)[0]
    return re.sub(r"\s+", " ", paragraph).strip()


def parse_table(section: str) -> list[dict[str, str]]:
    rows = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(rows) < 2:
        return []
    cells = lambda row: [cell.strip() for cell in row.strip("|").split("|")]
    headers = cells(rows[0])
    output: list[dict[str, str]] = []
    for row in rows[2:]:
        values = cells(row)
        if len(values) == len(headers):
            output.append(dict(zip(headers, values)))
    return output


def parse_stories(body: str) -> list[dict[str, Any]]:
    section = markdown_section(body, "User stories and acceptance")
    matches = list(re.finditer(r"^###\s+(US-[A-Za-z0-9-]+)\s+(?:—|-)\s+(.+?)\s*$", section, re.MULTILINE))
    stories: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        block = section[match.end():end]
        story_match = re.search(r"\*\*Story:\*\*\s*(.*?)(?=\n\*\*Acceptance criteria:\*\*)", block, re.DOTALL)
        acceptance_match = re.search(r"\*\*Acceptance criteria:\*\*\s*(.*)", block, re.DOTALL)
        criteria = []
        if acceptance_match:
            criteria = [re.sub(r"\s+", " ", item).strip() for item in re.findall(r"^-\s+(.+?(?=\n-|\Z))", acceptance_match.group(1), re.MULTILINE | re.DOTALL)]
        stories.append({
            "id": match.group(1),
            "title": match.group(2).strip(),
            "description": normalized_paragraph(story_match.group(1)) if story_match else "",
            "acceptanceCriteria": criteria,
        })
    return stories


def parse_contract_table(body: str) -> list[dict[str, Any]]:
    section = markdown_section(body, "Contracts and dependencies")
    contract_section = markdown_section(section, "Contract expectations", level=3)
    contracts: list[dict[str, Any]] = []
    for index, row in enumerate(parse_table(contract_section), start=1):
        name = row.get("Contract", "").strip(" `")
        if not name:
            continue
        contracts.append({
            "id": f"CON-EXPECTED-{index:02d}",
            "name": name,
            "type": "Expectation",
            "version": row.get("Version", "Unspecified"),
            "status": "EXPECTED",
            "owner": row.get("Owner", "Unassigned"),
            "path": "",
        })
    return contracts


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else ([] if value is None or value == "" else [value])


def status(value: Any, default: str = "UNKNOWN") -> str:
    return str(value or default).strip().upper().replace(" ", "_")


def owner_initials(owner: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", owner)
    return "".join(word[0].upper() for word in words[:2]) or "—"


def package_progress(packages: list[dict[str, Any]]) -> float:
    weights = {
        "DONE": 1.0,
        "VERIFYING": 0.8,
        "REVERIFY_REQUIRED": 0.6,
        "IN_PROGRESS": 0.5,
        "REWORK_REQUIRED": 0.35,
        "READY": 0.0,
        "BLOCKED": 0.0,
        "PAUSED": 0.0,
    }
    if not packages:
        return 0.0
    return sum(weights.get(status(item.get("status")), 0.0) for item in packages) / len(packages)


def slice_progress(slice_status: str, packages: list[dict[str, Any]]) -> int:
    if slice_status in {"OUTCOME_VALIDATED", "RELEASED"}:
        return 100
    if slice_status == "RELEASE_READY":
        return 95
    if slice_status == "READY_FOR_QA":
        return 80
    if packages:
        return round(20 + 60 * package_progress(packages))
    return {
        "DRAFT": 5,
        "PLANNING_REVIEW": 15,
        "READY_FOR_DEVELOPMENT": 20,
        "EXECUTION_READY": 20,
    }.get(slice_status, 0)


def story_status(packages: list[dict[str, Any]], slice_status: str) -> str:
    if slice_status in TERMINAL_SLICE_STATUSES:
        return "DONE"
    if not packages:
        return "PLANNED"
    states = {status(item.get("status")) for item in packages}
    if states <= TERMINAL_PACKAGE_STATUSES:
        return "VERIFYING"
    if "BLOCKED" in states:
        return "BLOCKED"
    if states & ACTIVE_PACKAGE_STATUSES:
        return "IN_PROGRESS"
    return "READY"


def execution_records(base: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    execution_dir = base / "execution"
    if execution_dir.exists():
        for path in sorted(execution_dir.glob("*.yaml")):
            record = read_yaml(path)
            slice_id = str(record.get("slice_id") or path.stem)
            record["_path"] = path
            records[slice_id] = record
    return records


def report_records(base: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    report_dir = base / "reports"
    if not report_dir.exists():
        return records
    for path in sorted(report_dir.glob("*.md")):
        metadata, body = read_markdown(path)
        slice_id = str(metadata.get("slice_id") or path.stem)
        test_results: dict[str, dict[str, str]] = {}
        for row in parse_table(markdown_section(body, "CLI test evidence")):
            test_id = row.get("Test ID", "").strip(" `")
            if test_id:
                test_results[test_id] = row
        records[slice_id] = {"metadata": metadata, "test_results": test_results, "path": path}
    return records


def result_status(value: Any, default: str = "READY") -> str:
    normalized = status(value, default)
    return {"PASS": "PASSED", "SUCCESS": "PASSED", "FAIL": "FAILED", "FAILURE": "FAILED"}.get(normalized, normalized)


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def build_dashboard_data(
    product_root: Path,
    projection_kind: str = "live-canonical",
    projection_source: str = "Canonical Meta PDS artifacts",
) -> dict[str, Any]:
    product_root = product_root.resolve()
    base = product_root / "docs" / "meta-pds"
    initiative_meta, initiative_body = read_markdown(base / "initiative.md")
    delivery = read_yaml(base / "delivery-state.yaml", required=True)
    decisions_doc = read_yaml(base / "decision-log.yaml")
    executions = execution_records(base)
    reports = report_records(base)

    slice_state_by_id = {
        str(item.get("slice_id")): item
        for item in list_value(delivery.get("slice_states"))
        if isinstance(item, dict) and item.get("slice_id")
    }

    roadmap_rows = parse_table(markdown_section(initiative_body, "Fat-slice roadmap overview"))
    roadmap_by_id = {row.get("Slice ID", ""): row for row in roadmap_rows if row.get("Slice ID")}
    slice_paths = sorted((base / "slices").glob("*.md")) if (base / "slices").exists() else []
    slice_ids = set(roadmap_by_id) | {path.stem for path in slice_paths}
    path_by_id = {path.stem: path for path in slice_paths}

    slices: list[dict[str, Any]] = []
    stories: list[dict[str, Any]] = []
    work_packages: list[dict[str, Any]] = []
    contracts: list[dict[str, Any]] = []
    test_cases: list[dict[str, Any]] = []

    for fallback_order, slice_id in enumerate(sorted(slice_ids), start=1):
        path = path_by_id.get(slice_id)
        row = roadmap_by_id.get(slice_id, {})
        meta: dict[str, Any] = {}
        body = ""
        parsed_stories: list[dict[str, Any]] = []
        expected_contracts: list[dict[str, Any]] = []
        if path:
            meta, body = read_markdown(path)
            slice_id = str(meta.get("slice_id") or slice_id)
            parsed_stories = parse_stories(body)
            expected_contracts = parse_contract_table(body)

        execution = executions.get(slice_id, {})
        report_test_results = reports.get(slice_id, {}).get("test_results", {})
        raw_tests = []
        for item in list_value(execution.get("test_cases")):
            if not isinstance(item, dict):
                continue
            test = dict(item)
            report_result = report_test_results.get(str(test.get("id")), {})
            if report_result:
                test["status"] = result_status(report_result.get("Result"), test.get("status") or "READY")
                test["evidence"] = report_result.get("Report/evidence") or test.get("evidence") or ""
            raw_tests.append(test)
        tests_by_id = {str(item.get("id")): item for item in raw_tests if item.get("id")}
        parsed_packages: list[dict[str, Any]] = []
        for item in list_value(execution.get("work_packages")):
            if not isinstance(item, dict) or not item.get("id"):
                continue
            required_tests = [str(value) for value in list_value(item.get("required_tests"))]
            test_records = [tests_by_id[test_id] for test_id in required_tests if test_id in tests_by_id]
            owner = str(item.get("owner") or "Unassigned")
            parsed_packages.append({
                "id": str(item["id"]),
                "sliceId": slice_id,
                "title": str(item.get("title") or item["id"]),
                "description": str(item.get("description") or ""),
                "status": status(item.get("status"), "BLOCKED"),
                "area": str(item.get("area") or "unassigned"),
                "owner": owner,
                "ownerInitials": str(item.get("owner_initials") or owner_initials(owner)),
                "storyIds": [str(value) for value in list_value(item.get("supports"))],
                "dependsOn": [str(value) for value in list_value(item.get("depends_on"))],
                "tests": {
                    "passed": sum(status(test.get("status")) == "PASSED" for test in test_records),
                    "total": len(required_tests),
                },
                "critical": str(item["id"]) in {str(value) for value in list_value(execution.get("critical_path"))},
                "blocker": str(item.get("blocker") or ""),
            })
        work_packages.extend(parsed_packages)

        state_record = slice_state_by_id.get(slice_id, {})
        current_status = status(state_record.get("status") or execution.get("status") or meta.get("status") or row.get("Status"), "DRAFT")
        if current_status == "MOBILIZING":
            current_status = "EXECUTION_READY"

        for story in parsed_stories:
            linked = [item for item in parsed_packages if story["id"] in item["storyIds"]]
            evidence_verified = current_status in TERMINAL_SLICE_STATUSES
            stories.append({
                **story,
                "sliceId": slice_id,
                "status": story_status(linked, current_status),
                "acceptance": {
                    "passed": len(story["acceptanceCriteria"]) if evidence_verified else 0,
                    "total": len(story["acceptanceCriteria"]),
                    "evidenceStatus": "VERIFIED" if evidence_verified else "PENDING",
                },
                "workPackageIds": [item["id"] for item in linked],
            })

        raw_contracts = [item for item in list_value(execution.get("integration_contracts")) if isinstance(item, dict)]
        selected_contracts = raw_contracts or expected_contracts
        for contract in selected_contracts:
            contracts.append({
                "id": str(contract.get("id") or f"CON-{slice_id}-{len(contracts) + 1}"),
                "sliceId": slice_id,
                "name": str(contract.get("name") or "Unnamed contract"),
                "type": str(contract.get("type") or "Contract"),
                "version": str(contract.get("version") or "Unspecified"),
                "status": status(contract.get("status"), "EXPECTED"),
                "owner": str(contract.get("owner") or "Unassigned"),
                "path": str(contract.get("path") or ""),
            })

        for test in raw_tests:
            test_cases.append({
                "id": str(test.get("id") or f"TC-{slice_id}-{len(test_cases) + 1}"),
                "sliceId": slice_id,
                "title": str(test.get("title") or test.get("id") or "Unnamed test"),
                "type": str(test.get("type") or "CLI"),
                "status": status(test.get("status"), "READY"),
                "owner": str(test.get("owner") or "Unassigned"),
                "evidence": str(test.get("evidence") or "Pending"),
                "supports": [str(value) for value in list_value(test.get("supports"))],
            })

        title = str(meta.get("title") or row.get("Slice") or (first_heading(body) if body else slice_id))
        outcome = normalized_paragraph(markdown_section(body, "Capability outcome")) if body else str(row.get("Capability outcome") or "")
        dependencies = list_value(meta.get("dependencies")) or [value.strip() for value in str(row.get("Dependencies") or "").split(",") if value.strip() and value.strip().lower() != "none"]
        slices.append({
            "id": slice_id,
            "order": int(meta.get("order") or row.get("Order") or fallback_order),
            "title": title,
            "outcome": outcome,
            "status": current_status,
            "progress": slice_progress(current_status, parsed_packages),
            "revision": int(meta.get("slice_revision") or 0),
            "priority": str(meta.get("priority") or row.get("Priority") or "—"),
            "dependencies": [str(value) for value in dependencies],
            "stories": len(parsed_stories),
            "active": slice_id in {delivery.get("active_planning_slice"), delivery.get("active_execution_slice")},
            "artifactPath": relative_path(path, product_root) if path else "",
        })

    slices.sort(key=lambda item: (item["order"], item["id"]))

    decisions = []
    for item in list_value(decisions_doc.get("decisions")):
        if not isinstance(item, dict):
            continue
        decisions.append({
            "id": str(item.get("id") or "DEC-UNKNOWN"),
            "title": str(item.get("question") or item.get("decision") or "Decision"),
            "summary": str(item.get("decision") or item.get("rationale") or ""),
            "status": status(item.get("status"), "PROPOSED"),
            "revision": int(item.get("revision") or 1),
            "updatedAt": str(item.get("decided_at") or delivery.get("last_verified_at") or datetime.now(timezone.utc).isoformat()),
            "affects": [str(value) for value in list_value(item.get("affected_artifacts"))],
        })

    attention = []
    human_decision = delivery.get("human_decision_required")
    if human_decision:
        detail = human_decision if isinstance(human_decision, str) else human_decision.get("question") or human_decision.get("detail") or "Human decision required"
        attention.append({"id": "HUMAN-DECISION", "kind": "decision", "title": "Human decision required", "detail": str(detail), "age": "Current", "affects": []})
    for index, blocker in enumerate(list_value(delivery.get("blockers")), start=1):
        if isinstance(blocker, dict):
            title = blocker.get("title") or blocker.get("id") or f"Blocker {index}"
            detail = blocker.get("detail") or blocker.get("reason") or ""
            affects = list_value(blocker.get("affects") or blocker.get("blocks"))
        else:
            title, detail, affects = f"Blocker {index}", str(blocker), []
        attention.append({"id": f"BLOCKER-{index}", "kind": "blocker", "title": str(title), "detail": str(detail), "age": "Current", "affects": affects})

    events = []
    events_path = base / "delivery-events.jsonl"
    if events_path.exists():
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            events.append({
                "at": item.get("at") or item.get("timestamp") or datetime.now(timezone.utc).isoformat(),
                "title": item.get("title") or item.get("event") or "Delivery event",
                "detail": item.get("detail") or "",
                "kind": item.get("kind") or "updated",
            })

    initiative_title = str(initiative_meta.get("title") or first_heading(initiative_body))
    objective = normalized_paragraph(markdown_section(initiative_body, "Goals, objectives, and expected outcomes"))
    next_action = delivery.get("next_recommended_action")
    if isinstance(next_action, dict):
        next_action_record = {
            "title": str(next_action.get("title") or "Review delivery state"),
            "detail": str(next_action.get("detail") or ""),
            "owner": str(next_action.get("owner") or "Product Manager"),
            "impact": str(next_action.get("impact") or ""),
        }
    else:
        next_action_record = {"title": str(next_action or "Review delivery state"), "detail": "", "owner": "Product Manager", "impact": ""}

    prototype = delivery.get("prototype") if isinstance(delivery.get("prototype"), dict) else {}
    now = datetime.now(timezone.utc).isoformat()
    return {
        "schemaVersion": 2,
        "projection": {"kind": projection_kind, "generatedAt": now, "source": projection_source, "staleAfterMinutes": 0},
        "initiative": {
            "id": str(initiative_meta.get("initiative_id") or delivery.get("initiative_id") or "UNKNOWN"),
            "name": initiative_title,
            "shortName": initiative_title,
            "phase": status(delivery.get("initiative_status"), "UNKNOWN"),
            "health": status(delivery.get("health"), "UNKNOWN"),
            "progress": round(sum(item["progress"] for item in slices) / len(slices)) if slices else 0,
            "objective": objective,
            "humanOwner": str(initiative_meta.get("human_owner") or "Human Product Owner"),
            "currentRevision": int(delivery.get("initiative_revision") or initiative_meta.get("revision") or 1),
            "nextAction": next_action_record,
        },
        "attention": attention,
        "prototype": {
            "id": str(prototype.get("id") or "No active prototype"),
            "name": str(prototype.get("name") or "Prototype not active"),
            "description": str(prototype.get("description") or "No prototype checkpoint is recorded in delivery-state.yaml."),
            "status": status(prototype.get("status"), "NOT_ACTIVE"),
            "checkpoint": str(prototype.get("checkpoint") or "—"),
            "checkpointAt": str(prototype.get("checkpoint_at") or now),
            "route": str(prototype.get("route") or "—"),
            "persistence": str(prototype.get("persistence") or "—"),
            "seedProfiles": int(prototype.get("seed_profiles") or 0),
            "journeys": {"reviewed": int(prototype.get("journeys_reviewed") or 0), "total": int(prototype.get("journeys_total") or 0)},
            "assumptionsTested": int(prototype.get("assumptions_tested") or 0),
            "openQuestions": int(prototype.get("open_questions") or 0),
            "manualReview": str(prototype.get("manual_review") or "Not requested"),
        },
        "decisions": decisions,
        "slices": slices,
        "stories": stories,
        "workPackages": work_packages,
        "contracts": contracts,
        "testCases": test_cases,
        "activity": events,
    }


def handler_for(
    product_root: Path,
    asset_root: Path,
    projection_kind: str = "live-canonical",
    projection_source: str = "Canonical Meta PDS artifacts",
):
    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            path = urlparse(self.path).path
            if path == "/api/dashboard":
                try:
                    payload = json.dumps(
                        build_dashboard_data(product_root, projection_kind, projection_source),
                        ensure_ascii=False,
                    ).encode("utf-8")
                    self.send_response(200)
                except (ArtifactError, OSError, ValueError) as error:
                    payload = json.dumps({"error": str(error)}).encode("utf-8")
                    self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            if path not in STATIC_FILES:
                self.send_error(404)
                return
            filename, content_type = STATIC_FILES[path]
            payload = (asset_root / filename).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return DashboardHandler


def prepare_demo_root(skill_root: Path) -> tempfile.TemporaryDirectory[str]:
    runtime = tempfile.TemporaryDirectory(prefix="meta-pds-dashboard-demo-")
    base = Path(runtime.name) / "docs" / "meta-pds"
    (base / "slices").mkdir(parents=True)

    initiative = (skill_root / "assets" / "initiative-template.md").read_text(encoding="utf-8")
    initiative = initiative.replace("INIT-0001", "INIT-0042").replace('title: ""', 'title: "Learning Platform V1"')
    (base / "initiative.md").write_text(initiative, encoding="utf-8")

    delivery = (skill_root / "assets" / "delivery-state-template.yaml").read_text(encoding="utf-8")
    delivery = delivery.replace("INIT-0001", "INIT-0042").replace("initiative_status: DISCOVERING", "initiative_status: INITIATIVE_READY")
    delivery = delivery.replace("health: UNKNOWN", "health: ON_TRACK").replace("active_planning_slice: null", "active_planning_slice: SLICE-AUTH-001")
    delivery = delivery.replace(
        "slice_states: []",
        "slice_states:\n  - slice_id: SLICE-AUTH-001\n    status: READY_FOR_DEVELOPMENT\n    current_gate: READY_FOR_DEVELOPMENT\n    updated_at: \"2026-08-21T23:00:00+05:00\"",
    )
    delivery = delivery.replace('title: ""', 'title: "Review the Authentication slice"')
    delivery = delivery.replace('detail: ""', 'detail: "This preview is parsed from the bundled slice example."')
    delivery = delivery.replace('impact: ""', 'impact: "Verify the dashboard layout before initializing a product."')
    (base / "delivery-state.yaml").write_text(delivery, encoding="utf-8")

    decisions = (skill_root / "assets" / "decision-log-template.yaml").read_text(encoding="utf-8").replace("INIT-0001", "INIT-0042")
    (base / "decision-log.yaml").write_text(decisions, encoding="utf-8")

    slice_example = skill_root.parent / "slice-planning" / "assets" / "authentication-slice-example.md"
    (base / "slices" / "SLICE-AUTH-001.md").write_text(slice_example.read_text(encoding="utf-8"), encoding="utf-8")
    return runtime


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("product_root", type=Path, nargs="?")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--demo", action="store_true", help="Preview the bundled Authentication slice without writing product files")
    parser.add_argument("--print-json", action="store_true", help="Print one in-memory projection and exit")
    args = parser.parse_args()

    if args.demo and args.product_root:
        parser.error("product_root and --demo are mutually exclusive")
    if not args.demo and not args.product_root:
        parser.error("product_root is required unless --demo is used")

    skill_root = Path(__file__).resolve().parent.parent
    demo_runtime = prepare_demo_root(skill_root) if args.demo else None
    product_root = Path(demo_runtime.name).resolve() if demo_runtime else args.product_root.resolve()
    projection_kind = "bundled-example" if args.demo else "live-canonical"
    projection_source = "Bundled Authentication slice example" if args.demo else "Canonical Meta PDS artifacts"
    if not (product_root / "docs" / "meta-pds").is_dir():
        parser.error(f"not a Meta PDS product root: {product_root}")
    if args.print_json:
        print(json.dumps(build_dashboard_data(product_root, projection_kind, projection_source), indent=2, ensure_ascii=False))
        return 0

    asset_root = skill_root / "assets" / "dashboard"
    server = ThreadingHTTPServer(
        (args.host, args.port),
        handler_for(product_root, asset_root, projection_kind, projection_source),
    )
    print(f"Meta PDS dashboard: http://{args.host}:{server.server_port}")
    print("Reading the bundled Authentication example in memory." if args.demo else f"Reading canonical artifacts from: {product_root}")
    print("Refresh the page to reparse current files. Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
