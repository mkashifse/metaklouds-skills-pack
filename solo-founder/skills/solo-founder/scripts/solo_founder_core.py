#!/usr/bin/env python3
"""Dependency-free artifact parsing, validation, locking, and writes."""

from __future__ import annotations

import ast
import contextlib
import fcntl
import hashlib
import json
import os
import re
import tempfile
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any

LAYERS = (
    "BUSINESS_DIRECTION",
    "PRODUCT_DIRECTION",
    "PRODUCT_BEHAVIOR",
    "EXPERIENCE",
    "DOMAIN_DATA",
    "SYSTEM_DESIGN",
    "TECHNOLOGY",
    "QUALITY",
    "DELIVERY",
    "OPERATIONS",
)
MODES = {"DISCOVERY", "IMPLEMENTATION"}
TRUTH_STATUSES = {"PROPOSED", "APPROVED"}
WORK_STATUSES = {
    "PENDING",
    "READY",
    "ACTIVE",
    "VERIFYING",
    "BLOCKED",
    "PAUSED",
    "DONE",
    "REWORK",
    "CANCELLED",
}
CLASSIFICATIONS = {"TRIVIAL", "NON_TRIVIAL"}
ISSUE_KINDS = {"DRIFT", "BLOCKER", "RISK", "EXTERNAL_DEPENDENCY"}
ISSUE_STATUSES = {"OPEN", "AWAITING_HUMAN", "RESOLVED"}
ISSUE_RESOLUTION_METHODS = {
    "AUTO_WITHIN_AUTHORITY",
    "HUMAN_APPROVED",
    "EXTERNAL_RESOLUTION",
}
INITIATIVE_STATUSES = {"ACTIVE", "PAUSED", "DONE", "CANCELLED"}
ROLES = {"PM", "PROTOTYPE_ENGINEER", "FULL_STACK_ENGINEER"}
ENGINEER_ROLES = {"PROTOTYPE_ENGINEER", "FULL_STACK_ENGINEER"}
WORKSTREAMS = {"PRODUCT", "PROTOTYPE", "FRONTEND", "BACKEND", "FULL_STACK"}
LEGACY_WORKSTREAMS = {"DATA", "QA", "PLATFORM", "SECURITY"}
ACTIVITIES = {
    "RESEARCH",
    "DOCUMENTATION",
    "DESIGN",
    "PLANNING",
    "IMPLEMENTATION",
    "TESTING",
    "RELEASE",
    "OPERATIONS",
}
EXECUTIONS = {"DIRECT", "DELEGATED"}
DELEGATION_REASONS = {"PARALLELISM", "LEGACY_ASSIGNMENT"}
HANDOFF_TYPES = {
    "RESEARCH",
    "DOCUMENTATION",
    "PROTOTYPE",
    "IMPLEMENTATION",
    "VERIFICATION",
    "EXCEPTION",
}
HANDOFF_UNIVERSAL_SECTIONS = (
    "Outcome Summary",
    "Deliverables and Artifacts",
    "Evidence",
    "Risks and Limitations",
    "Open Decisions",
    "PM Consumption Target",
)
HANDOFF_PAYLOAD_SECTIONS = {
    "RESEARCH": (
        "Sources and Findings",
        "Conflicts and Confidence",
        "Preliminary Implications",
    ),
    "DOCUMENTATION": (
        "Target Documents",
        "Draft Contribution",
        "Traceability and Conflicts",
    ),
    "PROTOTYPE": (
        "Prototype Checkpoint",
        "Implemented Behavior and States",
        "Promotion Inputs",
        "Proposed Product Findings",
    ),
    "IMPLEMENTATION": (
        "Changed Paths and Commits",
        "Contracts and Migrations",
        "Tests and Rollback",
    ),
    "VERIFICATION": (
        "Acceptance Matrix",
        "Test Results",
        "Failures and Residual Risk",
    ),
    "EXCEPTION": (
        "Exception and Impact",
        "Blocked Work",
        "Options and Recommendation",
    ),
}


class ArtifactError(RuntimeError):
    pass


def infer_handoff_type(item: dict[str, Any]) -> str:
    activity = item.get("activity")
    if activity == "RESEARCH":
        return "RESEARCH"
    if activity in {"DOCUMENTATION", "PLANNING"}:
        return "DOCUMENTATION"
    if (
        item.get("role") == "PROTOTYPE_ENGINEER"
        or item.get("workstream") == "PROTOTYPE"
    ):
        return "PROTOTYPE"
    if activity == "TESTING":
        return "VERIFICATION"
    return "IMPLEMENTATION"


def handoff_path_for(work_id: str, handoff_type: str) -> str:
    return f"docs/solo-founder/handoffs/{handoff_type.lower()}/{work_id}.md"


def upgrade_ledger(document: dict[str, Any]) -> bool:
    """Upgrade earlier Ledgers to PM-first execution and the Issue Sidecar."""
    schema_version = document.get("schema_version")
    if schema_version not in {1, 2, 3}:
        return False
    if schema_version in {1, 2}:
        for raw in document.get("work") or []:
            if not isinstance(raw, dict):
                continue
            owner = str(raw.get("owner") or "")
            workstream = str(raw.get("workstream") or "")
            if schema_version == 1 and not raw.get("role"):
                if owner == "PM":
                    raw["role"] = "PM"
                elif workstream == "PROTOTYPE" or "PROTOTYPE" in owner.upper():
                    raw["role"] = "PROTOTYPE_ENGINEER"
                else:
                    raw["role"] = "FULL_STACK_ENGINEER"
            if raw.get("role") == "PROTOTYPE_ENGINEER":
                raw["workstream"] = "PROTOTYPE"
            elif raw.get("role") == "FULL_STACK_ENGINEER" and workstream not in {
                "FRONTEND",
                "BACKEND",
                "FULL_STACK",
            }:
                raw["workstream"] = (
                    "BACKEND"
                    if workstream in {"DATA", "PLATFORM", "SECURITY"}
                    else "FULL_STACK"
                )
            raw["execution"] = "DIRECT" if raw.get("role") == "PM" else "DELEGATED"
            if raw.get("role") == "PM":
                raw["delegation_reason"] = None
                raw["handoff_type"] = None
                raw["handoff_path"] = None
                raw["handoff_submitted_at"] = None
                raw["handoff_submitted_hash"] = None
                raw["handoff_consumed_at"] = None
            else:
                handoff_type = raw.get("handoff_type") or infer_handoff_type(raw)
                raw["delegation_reason"] = (
                    raw.get("delegation_reason") or "LEGACY_ASSIGNMENT"
                )
                raw["handoff_type"] = handoff_type
                raw["handoff_path"] = raw.get("handoff_path") or handoff_path_for(
                    str(raw.get("id") or "WORK-LEGACY"), handoff_type
                )
                timestamp = (
                    raw.get("updated_at")
                    or raw.get("created_at")
                    or datetime.now().astimezone().isoformat(timespec="seconds")
                )
                raw["handoff_submitted_at"] = (
                    timestamp
                    if raw.get("status") in {"VERIFYING", "DONE", "REWORK"}
                    else None
                )
                raw["handoff_submitted_hash"] = None
                raw["handoff_consumed_at"] = (
                    raw.get("completed_at") or timestamp
                    if raw.get("status") in {"DONE", "REWORK"}
                    else None
                )
    migration_time = document.get(
        "updated_at"
    ) or datetime.now().astimezone().isoformat(timespec="seconds")
    for raw in document.get("issues") or []:
        if not isinstance(raw, dict):
            continue
        raw["summary"] = str(
            raw.get("summary")
            or raw.get("title")
            or raw.get("description")
            or f"Migrated {raw.get('kind', 'issue')} {raw.get('id', '')}"
        )
        raw["linked_work_ids"] = list(
            raw.get("linked_work_ids") or raw.get("work_ids") or []
        )
        raw["linked_truth_ids"] = list(
            raw.get("linked_truth_ids") or raw.get("truth_ids") or []
        )
        raw["detected_at"] = str(
            raw.get("detected_at") or raw.get("created_at") or migration_time
        )
        original_human = bool(raw.get("human_approval_required"))
        original_status = str(raw.get("status") or "").upper()
        resolved = bool(raw.get("resolved_at")) or original_status in {
            "DONE",
            "CLOSED",
            "RESOLVED",
            "CANCELLED",
        }
        if resolved:
            existing_resolution = raw.get("resolution")
            resolution = (
                dict(existing_resolution)
                if isinstance(existing_resolution, dict)
                else {}
            )
            resolution["method"] = resolution.get("method") or (
                "HUMAN_APPROVED" if original_human else "EXTERNAL_RESOLUTION"
            )
            resolution["action"] = str(
                resolution.get("action")
                or existing_resolution
                or raw.get("recommendation")
                or "Preserved the legacy resolution"
            )
            resolution["evidence"] = list(
                resolution.get("evidence")
                or raw.get("evidence")
                or ["Legacy Product Ledger record"]
            )
            resolution["resolved_by"] = str(
                resolution.get("resolved_by") or raw.get("resolved_by") or "PM"
            )
            resolution["resolved_at"] = str(
                resolution.get("resolved_at")
                or raw.get("resolved_at")
                or migration_time
            )
            raw["status"] = "RESOLVED"
            raw["human_approval_required"] = False
            raw["resolution"] = resolution
        elif original_human:
            raw["status"] = "AWAITING_HUMAN"
            raw["human_approval_required"] = True
            raw["recommendation"] = str(
                raw.get("recommendation") or "Human review is required"
            )
            raw["impact"] = str(
                raw.get("impact")
                or raw.get("description")
                or "Only the affected scope remains paused"
            )
            raw["resolution"] = None
        else:
            raw["status"] = "OPEN"
            raw["human_approval_required"] = False
            raw["resolution"] = None
    document["schema_version"] = 4
    return True


def normalize_block_scalars(text: str) -> str:
    source = text.splitlines()
    normalized: list[str] = []
    index = 0
    pattern = re.compile(r"^(\s*[A-Za-z_][A-Za-z0-9_-]*\s*:\s*)([|>])[-+]?\s*(?:#.*)?$")
    while index < len(source):
        line = source[index]
        match = pattern.match(line)
        if not match:
            normalized.append(line)
            index += 1
            continue
        parent_indent = len(line) - len(line.lstrip(" "))
        index += 1
        block: list[str] = []
        content_indent: int | None = None
        while index < len(source):
            candidate = source[index]
            if not candidate.strip():
                block.append("")
                index += 1
                continue
            indent = len(candidate) - len(candidate.lstrip(" "))
            if indent <= parent_indent:
                break
            if content_indent is None:
                content_indent = indent
            block.append(candidate[min(content_indent, len(candidate)) :])
            index += 1
        value = "\n".join(block)
        if match.group(2) == ">":
            value = re.sub(r"(?<!\n)\n(?!\n)", " ", value).strip()
        else:
            value = value.rstrip("\n")
        normalized.append(f"{match.group(1)}{json.dumps(value, ensure_ascii=False)}")
    return "\n".join(normalized)


def strip_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
        elif character == "\\" and quote is not None:
            escaped = True
        elif character in {'"', "'"}:
            quote = (
                None if quote == character else character if quote is None else quote
            )
        elif (
            character == "#"
            and quote is None
            and (index == 0 or value[index - 1].isspace())
        ):
            return value[:index].rstrip()
    return value.rstrip()


def split_inline(value: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
        elif character == "\\" and quote is not None:
            escaped = True
        elif character in {'"', "'"}:
            quote = (
                None if quote == character else character if quote is None else quote
            )
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
            parsed_key = str(parse_scalar(key.strip()))
            if parsed_key in result:
                raise ArtifactError(f"Duplicate YAML key '{parsed_key}'")
            result[parsed_key] = parse_scalar(item)
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
    if value.startswith(("&", "*", "!!")):
        raise ArtifactError(
            "YAML anchors, aliases, and explicit tags are not supported"
        )
    return value


def yaml_lines(text: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    for raw in normalize_block_scalars(text).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if "\t" in raw[:indent]:
            raise ArtifactError("Tabs are not supported in Solo Founder YAML")
        result.append((indent, strip_comment(raw.strip())))
    return result


def parse_yaml_block(
    lines: list[tuple[int, str]], index: int, indent: int
) -> tuple[Any, int]:
    if index >= len(lines) or lines[index][0] < indent:
        return None, index
    if lines[index][1].startswith("-"):
        items: list[Any] = []
        while (
            index < len(lines)
            and lines[index][0] == indent
            and lines[index][1].startswith("-")
        ):
            content = lines[index][1][1:].strip()
            index += 1
            if not content:
                item, index = parse_yaml_block(lines, index, indent + 2)
            elif re.match(r"^[A-Za-z_][A-Za-z0-9_-]*\s*:(?:\s|$)", content):
                key, value = content.split(":", 1)
                item = {key.strip(): parse_scalar(value)}
                if index < len(lines) and lines[index][0] > indent:
                    continuation, index = parse_yaml_block(lines, index, indent + 2)
                    if isinstance(continuation, dict):
                        duplicates = set(item) & set(continuation)
                        if duplicates:
                            raise ArtifactError(
                                f"Duplicate YAML key '{min(duplicates)}'"
                            )
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
    while (
        index < len(lines)
        and lines[index][0] == indent
        and not lines[index][1].startswith("-")
    ):
        content = lines[index][1]
        key, separator, value = content.partition(":")
        if not separator:
            raise ArtifactError(f"Invalid YAML line: {content}")
        key = key.strip()
        if key in mapping:
            raise ArtifactError(f"Duplicate YAML key '{key}'")
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
        raise ArtifactError("Solo Founder YAML must contain one top-level mapping")
    return value


def handoff_section_body(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        return ""
    return re.sub(r"<!--.*?-->", "", match.group(1), flags=re.DOTALL).strip()


def validate_handoff_file(product_root: Path, item: dict[str, Any]) -> str:
    relative_path = Path(str(item.get("handoff_path") or ""))
    path = product_root / relative_path
    if not path.is_file():
        raise ArtifactError(f"Handoff file is missing: {relative_path}")
    content = path.read_bytes()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ArtifactError(f"Handoff is not valid UTF-8: {relative_path}") from error
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ArtifactError(f"Invalid handoff frontmatter: {relative_path}")
    header = parse_yaml(parts[1])
    expected = {
        "schema_version": 1,
        "handoff_id": f"HANDOFF-{item['id']}",
        "work_id": item["id"],
        "type": item["handoff_type"],
        "producer_role": item["role"],
        "producer_id": item["owner"],
        "consumer": "PM",
    }
    for field, value in expected.items():
        if header.get(field) != value:
            raise ArtifactError(f"Handoff {field} must be {value}")
    if not str(header.get("created_at") or "").strip():
        raise ArtifactError("Handoff requires created_at")
    required_sections = (
        HANDOFF_UNIVERSAL_SECTIONS + HANDOFF_PAYLOAD_SECTIONS[item["handoff_type"]]
    )
    for heading in required_sections:
        if not handoff_section_body(parts[2], heading):
            raise ArtifactError(f"Handoff requires content in: {heading}")
    return hashlib.sha256(content).hexdigest()


def validate_submitted_handoff(product_root: Path, item: dict[str, Any]) -> None:
    current_hash = validate_handoff_file(product_root, item)
    expected_hash = item.get("handoff_submitted_hash")
    if item.get("delegation_reason") == "PARALLELISM":
        if not isinstance(expected_hash, str) or not re.fullmatch(
            r"[0-9a-f]{64}", expected_hash
        ):
            raise ArtifactError("Delegated handoff requires a submitted content hash")
        if current_hash != expected_hash:
            raise ArtifactError("Delegated handoff changed after submission")


def scalar_yaml(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def dump_yaml_node(value: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(value, dict):
        if not value:
            return [prefix + "{}"]
        lines: list[str] = []
        for key, item in value.items():
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", str(key)):
                raise ArtifactError(f"Unsupported YAML key: {key}")
            if isinstance(item, dict) and item or isinstance(item, list) and item:
                lines.append(f"{prefix}{key}:")
                lines.extend(dump_yaml_node(item, indent + 2))
            elif isinstance(item, dict):
                lines.append(f"{prefix}{key}: {{}}")
            elif isinstance(item, list):
                lines.append(f"{prefix}{key}: []")
            else:
                lines.append(f"{prefix}{key}: {scalar_yaml(item)}")
        return lines
    if isinstance(value, list):
        if not value:
            return [prefix + "[]"]
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(prefix + "-")
                lines.extend(dump_yaml_node(item, indent + 2))
            else:
                lines.append(prefix + "- " + scalar_yaml(item))
        return lines
    return [prefix + scalar_yaml(value)]


def dump_yaml(document: dict[str, Any]) -> str:
    return "\n".join(dump_yaml_node(document)) + "\n"


def read_yaml(path: Path, required: bool = True) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise ArtifactError(f"Missing canonical artifact: {path}")
        return {}
    return parse_yaml(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ArtifactError(f"{label} must be a list")
    return value


def require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ArtifactError(f"{label} must be a mapping")
    return value


def validate_truth(document: dict[str, Any]) -> None:
    if document.get("schema_version") != 1:
        raise ArtifactError("canonical-truth.yaml requires schema_version: 1")
    if not str(document.get("initiative_id") or "").strip():
        raise ArtifactError("canonical-truth.yaml requires initiative_id")
    truth = require_mapping(document.get("truth"), "truth")
    if tuple(truth.keys()) != LAYERS:
        raise ArtifactError("truth groups must exactly match the finalized Layer order")
    seen: set[str] = set()
    approved: set[str] = set()
    id_layers: dict[str, str] = {}
    all_items: list[tuple[str, dict[str, Any]]] = []
    for layer in LAYERS:
        for raw in require_list(truth[layer], f"truth.{layer}"):
            item = require_mapping(raw, f"truth.{layer} item")
            truth_id = str(item.get("id") or "")
            if not re.fullmatch(rf"{re.escape(layer)}-\d{{3,}}", truth_id):
                raise ArtifactError(f"Invalid Truth ID for {layer}: {truth_id}")
            if truth_id in seen:
                raise ArtifactError(f"Duplicate Truth ID: {truth_id}")
            seen.add(truth_id)
            id_layers[truth_id] = layer
            status = item.get("status")
            if status not in TRUTH_STATUSES:
                raise ArtifactError(f"Invalid Truth status for {truth_id}: {status}")
            for field in ("title", "statement", "proposed_at"):
                if not str(item.get(field) or "").strip():
                    raise ArtifactError(f"{truth_id} requires {field}")
            evidence = require_list(item.get("evidence"), f"{truth_id}.evidence")
            if not evidence or any(not str(value).strip() for value in evidence):
                raise ArtifactError(
                    f"{truth_id} requires at least one evidence reference"
                )
            affected = require_list(
                item.get("affected_layers"), f"{truth_id}.affected_layers"
            )
            unknown = [value for value in affected if value not in LAYERS]
            if unknown:
                raise ArtifactError(
                    f"{truth_id} has unknown affected Layer: {unknown[0]}"
                )
            if status == "APPROVED":
                approved.add(truth_id)
                if item.get("approved_by") != "HUMAN":
                    raise ArtifactError(f"{truth_id} requires approved_by: HUMAN")
                if item.get("approved_via") not in {"CHAT", "DASHBOARD"}:
                    raise ArtifactError(f"{truth_id} has invalid approved_via")
                if not item.get("approved_at"):
                    raise ArtifactError(f"{truth_id} requires approved_at")
            elif any(
                item.get(field) is not None
                for field in ("approved_at", "approved_by", "approved_via")
            ):
                raise ArtifactError(f"{truth_id} is PROPOSED but has approval metadata")
            all_items.append((layer, item))
    for _layer, item in all_items:
        replacement = item.get("replaces")
        if replacement is not None and replacement not in approved:
            raise ArtifactError(
                f"{item['id']} replaces unknown or non-approved Truth: {replacement}"
            )
        if (
            replacement is not None
            and id_layers.get(replacement) != id_layers[item["id"]]
        ):
            raise ArtifactError(f"{item['id']} must replace Truth in the same Layer")


def validate_ledger(document: dict[str, Any]) -> None:
    schema_version = document.get("schema_version")
    if schema_version not in {1, 2, 3, 4}:
        raise ArtifactError(
            "product-ledger.yaml requires schema_version: 1, 2, 3, or 4"
        )
    require_mapping(document.get("product"), "product")
    current = require_mapping(document.get("current"), "current")
    if current.get("mode") not in MODES:
        raise ArtifactError("current.mode must be DISCOVERY or IMPLEMENTATION")
    if current.get("layer") not in LAYERS:
        raise ArtifactError("current.layer must be a finalized Layer")
    affected = require_list(current.get("affected_layers"), "current.affected_layers")
    if any(layer not in LAYERS for layer in affected):
        raise ArtifactError("current.affected_layers contains an unknown Layer")
    require_mapping(document.get("authority"), "authority")
    initiatives = require_list(document.get("initiatives"), "initiatives")
    work = require_list(document.get("work"), "work")
    issues = require_list(document.get("issues"), "issues")
    initiative_ids: set[str] = set()
    for raw in initiatives:
        item = require_mapping(raw, "initiative item")
        initiative_id = str(item.get("id") or "")
        if not re.fullmatch(r"INIT-[A-Za-z0-9-]+", initiative_id):
            raise ArtifactError(f"Invalid Initiative ID: {initiative_id}")
        if initiative_id in initiative_ids:
            raise ArtifactError(f"Duplicate Initiative ID: {initiative_id}")
        initiative_ids.add(initiative_id)
        if item.get("status") not in INITIATIVE_STATUSES:
            raise ArtifactError(f"{initiative_id} has invalid status")
    work_ids: set[str] = set()
    for raw in work:
        item = require_mapping(raw, "work item")
        work_id = str(item.get("id") or "")
        if not re.fullmatch(r"WORK-[A-Za-z0-9-]+", work_id):
            raise ArtifactError(f"Invalid Work ID: {work_id}")
        if work_id in work_ids:
            raise ArtifactError(f"Duplicate Work ID: {work_id}")
        work_ids.add(work_id)
        if item.get("classification") not in CLASSIFICATIONS:
            raise ArtifactError(f"{work_id} has invalid classification")
        allowed_workstreams = (
            WORKSTREAMS | LEGACY_WORKSTREAMS if schema_version == 1 else WORKSTREAMS
        )
        if item.get("workstream") not in allowed_workstreams:
            raise ArtifactError(f"{work_id} has invalid workstream")
        if item.get("activity") not in ACTIVITIES:
            raise ArtifactError(f"{work_id} has invalid activity")
        if item.get("execution") not in EXECUTIONS:
            raise ArtifactError(f"{work_id} has invalid execution")
        if item.get("status") not in WORK_STATUSES:
            raise ArtifactError(f"{work_id} has invalid status")
        if not str(item.get("owner") or "").strip():
            raise ArtifactError(f"{work_id} requires owner")
        role = item.get("role")
        if schema_version in {2, 3, 4}:
            if role not in ROLES:
                raise ArtifactError(f"{work_id} has invalid role")
            expected_execution = "DIRECT" if role == "PM" else "DELEGATED"
            if item.get("execution") != expected_execution:
                raise ArtifactError(
                    f"{work_id} execution must be {expected_execution} for {role}"
                )
            if role == "PM" and item.get("owner") != "PM":
                raise ArtifactError(f"{work_id} PM work requires owner: PM")
            if role == "PROTOTYPE_ENGINEER" and item.get("workstream") != "PROTOTYPE":
                raise ArtifactError(
                    f"{work_id} Prototype Engineer requires PROTOTYPE workstream"
                )
            if role == "FULL_STACK_ENGINEER" and item.get("workstream") not in {
                "FRONTEND",
                "BACKEND",
                "FULL_STACK",
            }:
                raise ArtifactError(
                    f"{work_id} Full-Stack Engineer requires an engineering focus"
                )
        if schema_version in {3, 4}:
            if role == "PM":
                if any(
                    item.get(field) is not None
                    for field in (
                        "delegation_reason",
                        "handoff_type",
                        "handoff_path",
                        "handoff_submitted_at",
                        "handoff_submitted_hash",
                        "handoff_consumed_at",
                    )
                ):
                    raise ArtifactError(
                        f"{work_id} direct PM work cannot have a handoff"
                    )
            else:
                if item.get("delegation_reason") not in DELEGATION_REASONS:
                    raise ArtifactError(f"{work_id} has invalid delegation reason")
                handoff_type = item.get("handoff_type")
                if handoff_type not in HANDOFF_TYPES:
                    raise ArtifactError(f"{work_id} has invalid handoff type")
                expected_path = handoff_path_for(work_id, handoff_type)
                if item.get("handoff_path") != expected_path:
                    raise ArtifactError(
                        f"{work_id} handoff path must be {expected_path}"
                    )
                if (
                    item.get("status") in {"VERIFYING", "DONE", "REWORK"}
                    and not str(item.get("handoff_submitted_at") or "").strip()
                ):
                    raise ArtifactError(f"{work_id} requires submitted handoff time")
                if (
                    item.get("delegation_reason") == "PARALLELISM"
                    and item.get("status") in {"VERIFYING", "DONE", "REWORK"}
                    and not re.fullmatch(
                        r"[0-9a-f]{64}", str(item.get("handoff_submitted_hash") or "")
                    )
                ):
                    raise ArtifactError(f"{work_id} requires submitted handoff hash")
                if (
                    item.get("status") in {"DONE", "REWORK"}
                    and not str(item.get("handoff_consumed_at") or "").strip()
                ):
                    raise ArtifactError(f"{work_id} requires consumed handoff time")
        require_list(item.get("acceptance_criteria"), f"{work_id}.acceptance_criteria")
        require_list(item.get("evidence"), f"{work_id}.evidence")
        require_list(item.get("owned_paths"), f"{work_id}.owned_paths")
    issue_ids: set[str] = set()
    for raw in issues:
        item = require_mapping(raw, "issue item")
        issue_id = str(item.get("id") or "")
        if not re.fullmatch(r"ISSUE-[A-Za-z0-9-]+", issue_id):
            raise ArtifactError(f"Invalid Issue ID: {issue_id}")
        if issue_id in issue_ids:
            raise ArtifactError(f"Duplicate Issue ID: {issue_id}")
        issue_ids.add(issue_id)
        if item.get("kind") not in ISSUE_KINDS:
            raise ArtifactError(f"{issue_id} has invalid kind")
        if schema_version == 4:
            if not str(item.get("summary") or "").strip():
                raise ArtifactError(f"{issue_id} requires summary")
            status = item.get("status")
            if status not in ISSUE_STATUSES:
                raise ArtifactError(f"{issue_id} has invalid status")
            human_required = item.get("human_approval_required")
            if not isinstance(human_required, bool):
                raise ArtifactError(
                    f"{issue_id}.human_approval_required must be boolean"
                )
            linked_work = require_list(
                item.get("linked_work_ids"), f"{issue_id}.linked_work_ids"
            )
            require_list(item.get("linked_truth_ids"), f"{issue_id}.linked_truth_ids")
            unknown_issue_work = [
                work_id for work_id in linked_work if work_id not in work_ids
            ]
            if unknown_issue_work:
                raise ArtifactError(
                    f"{issue_id} links unknown work: {unknown_issue_work[0]}"
                )
            if not str(item.get("detected_at") or "").strip():
                raise ArtifactError(f"{issue_id} requires detected_at")
            resolution = item.get("resolution")
            if status == "OPEN":
                if human_required or resolution is not None:
                    raise ArtifactError(
                        f"{issue_id} OPEN cannot require Human approval or resolution"
                    )
            elif status == "AWAITING_HUMAN":
                if not human_required or resolution is not None:
                    raise ArtifactError(
                        f"{issue_id} AWAITING_HUMAN requires Human approval and no resolution"
                    )
                if (
                    not str(item.get("recommendation") or "").strip()
                    or not str(item.get("impact") or "").strip()
                ):
                    raise ArtifactError(
                        f"{issue_id} AWAITING_HUMAN requires recommendation and impact"
                    )
            else:
                if human_required:
                    raise ArtifactError(
                        f"{issue_id} RESOLVED cannot await Human approval"
                    )
                resolution_map = require_mapping(resolution, f"{issue_id}.resolution")
                if resolution_map.get("method") not in ISSUE_RESOLUTION_METHODS:
                    raise ArtifactError(f"{issue_id} has invalid resolution method")
                if not str(resolution_map.get("action") or "").strip():
                    raise ArtifactError(f"{issue_id} resolution requires action")
                evidence = require_list(
                    resolution_map.get("evidence"),
                    f"{issue_id}.resolution.evidence",
                )
                if not evidence:
                    raise ArtifactError(f"{issue_id} resolution requires evidence")
                if not str(resolution_map.get("resolved_by") or "").strip():
                    raise ArtifactError(f"{issue_id} resolution requires resolved_by")
                if not str(resolution_map.get("resolved_at") or "").strip():
                    raise ArtifactError(f"{issue_id} resolution requires resolved_at")
    unknown_active = [
        work_id
        for work_id in require_list(
            current.get("active_work_ids"), "current.active_work_ids"
        )
        if work_id not in work_ids
    ]
    if unknown_active:
        raise ArtifactError(
            f"current.active_work_ids contains unknown work: {unknown_active[0]}"
        )


@contextlib.contextmanager
def file_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def atomic_write_yaml(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(dump_yaml(document))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def approve_truth(
    product_root: Path,
    truth_id: str,
    expected_hash: str,
    via: str = "DASHBOARD",
) -> dict[str, Any]:
    base = product_root / "docs" / "solo-founder"
    path = base / "canonical-truth.yaml"
    with file_lock(base / ".canonical-truth.lock"):
        if sha256_file(path) != expected_hash:
            raise ArtifactError("Canonical Truth changed; refresh before approving")
        document = read_yaml(path)
        validate_truth(document)
        found_layer: str | None = None
        found: dict[str, Any] | None = None
        for layer in LAYERS:
            for item in document["truth"][layer]:
                if item.get("id") == truth_id:
                    found_layer = layer
                    found = item
                    break
        if found is None or found_layer is None:
            raise ArtifactError(f"Unknown Truth ID: {truth_id}")
        if found.get("status") != "PROPOSED":
            raise ArtifactError(f"{truth_id} is no longer PROPOSED")
        replacement = found.get("replaces")
        if replacement:
            document["truth"][found_layer] = [
                item
                for item in document["truth"][found_layer]
                if item.get("id") != replacement
            ]
            found = next(
                item
                for item in document["truth"][found_layer]
                if item.get("id") == truth_id
            )
        found["status"] = "APPROVED"
        found["approved_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        found["approved_by"] = "HUMAN"
        found["approved_via"] = via
        found.pop("replaces", None)
        validate_truth(document)
        atomic_write_yaml(path, document)
        return found
