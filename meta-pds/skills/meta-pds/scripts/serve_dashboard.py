#!/usr/bin/env python3
"""Serve the Meta PDS dashboard directly from canonical product artifacts."""

from __future__ import annotations

import argparse
import ast
import hashlib
import http.client
import json
import os
import re
import signal
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


TERMINAL_PACKAGE_STATUSES = {"DONE"}
ACTIVE_PACKAGE_STATUSES = {"IN_PROGRESS", "VERIFYING", "REWORK_REQUIRED", "REVERIFY_REQUIRED"}
TERMINAL_SLICE_STATUSES = {"RELEASED", "OUTCOME_VALIDATED"}
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}
RUNTIME_SERVICE = "meta-pds-dashboard"
RUNTIME_VERSION = 5
SUPPORTED_IMPLEMENTATION_SKILLS = {
    "prototype",
    "vercel-react-best-practices",
    "frontend-design",
    "vercel-composition-patterns",
    "fastapi",
    "nodejs-backend-patterns",
    "python-testing-patterns",
    "vitest",
    "playwright-best-practices",
    "supabase",
    "supabase-postgres-best-practices",
}
DECISION_TYPES = {
    "GOAL": {"label": "Goal", "layer": "Product direction", "layerKey": "product-direction", "order": 10},
    "USER_PROBLEM": {"label": "User / Problem", "layer": "Product direction", "layerKey": "product-direction", "order": 20},
    "OUTCOME_METRIC": {"label": "Outcome / Metric", "layer": "Product direction", "layerKey": "product-direction", "order": 30},
    "SCOPE_PRIORITY": {"label": "Scope / Priority", "layer": "Product direction", "layerKey": "product-direction", "order": 40},
    "FEATURE_CAPABILITY": {"label": "Feature / Capability", "layer": "Product behavior", "layerKey": "product-behavior", "order": 50},
    "BUSINESS_RULE": {"label": "Business Rule", "layer": "Product behavior", "layerKey": "product-behavior", "order": 60},
    "UI_UX": {"label": "UI / UX", "layer": "Experience", "layerKey": "experience", "order": 70},
    "CONTENT_ACCESSIBILITY": {"label": "Content / Accessibility", "layer": "Experience", "layerKey": "experience", "order": 80},
    "DOMAIN_MODEL": {"label": "Domain Model", "layer": "Domain & data", "layerKey": "domain-data", "order": 90},
    "SCHEMA": {"label": "Schema", "layer": "Domain & data", "layerKey": "domain-data", "order": 100},
    "ARCHITECTURE": {"label": "Architecture", "layer": "System design", "layerKey": "system-design", "order": 110},
    "API_INTEGRATION": {"label": "API / Integration", "layer": "System design", "layerKey": "system-design", "order": 120},
    "SECURITY_PRIVACY": {"label": "Security / Privacy", "layer": "System design", "layerKey": "system-design", "order": 130},
    "STACK": {"label": "Stack", "layer": "Technology", "layerKey": "technology", "order": 140},
    "DATABASE_STORAGE": {"label": "Database / Storage", "layer": "Technology", "layerKey": "technology", "order": 150},
    "TESTING_QUALITY": {"label": "Testing / Quality", "layer": "Quality", "layerKey": "quality", "order": 160},
    "RELEASE_MIGRATION": {"label": "Release / Migration", "layer": "Delivery", "layerKey": "delivery", "order": 170},
    "OBSERVABILITY_OPERATIONS": {"label": "Observability / Operations", "layer": "Operations", "layerKey": "operations", "order": 180},
}
ALLOWED_INTERACTION_MODES = {"EXPLORE", "DECISION_REVIEW", "PROTOTYPE", "SLICE_SHAPING", "DELIVERY"}
DECISION_KEY_PATTERN = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
DECISION_PHASE_PATTERN = re.compile(r"^PHASE-[1-9][0-9]*$")


class ArtifactError(RuntimeError):
    pass


def normalize_block_scalars(text: str) -> str:
    """Convert ordinary YAML literal/folded scalars into quoted scalar lines.

    Meta PDS intentionally supports a conservative YAML surface, but multiline
    descriptions are common in agent output. Normalizing them here keeps the
    parser dependency-free while accepting the most useful standard YAML
    multiline syntax.
    """
    source = text.splitlines()
    normalized: list[str] = []
    index = 0
    marker_pattern = re.compile(r"^(\s*[A-Za-z_][A-Za-z0-9_-]*\s*:\s*)([|>])[-+]?\s*(?:#.*)?$")
    while index < len(source):
        line = source[index]
        match = marker_pattern.match(line)
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
            block.append(candidate[min(content_indent, len(candidate)):])
            index += 1
        if match.group(2) == ">":
            value = re.sub(r"(?<!\n)\n(?!\n)", " ", "\n".join(block)).strip()
        else:
            value = "\n".join(block).rstrip("\n")
        normalized.append(f"{match.group(1)}{json.dumps(value, ensure_ascii=False)}")
    return "\n".join(normalized)


def strip_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if character == "\\" and quote is not None:
            escaped = True
        elif character in {'"', "'"}:
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
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if character == "\\" and quote is not None:
            escaped = True
        elif character in {'"', "'"}:
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
    if value.startswith("&") or value.startswith("*") or value.startswith("!!"):
        raise ArtifactError("YAML anchors, aliases, and explicit tags are not supported")
    return value


def yaml_lines(text: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    for raw in normalize_block_scalars(text).splitlines():
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
            elif re.match(r"^[A-Za-z_][A-Za-z0-9_-]*\s*:(?:\s|$)", content):
                key, value = content.split(":", 1)
                item = {key.strip(): parse_scalar(value)}
                if index < len(lines) and lines[index][0] > indent:
                    continuation, index = parse_yaml_block(lines, index, indent + 2)
                    if isinstance(continuation, dict):
                        duplicate_keys = set(item) & set(continuation)
                        if duplicate_keys:
                            raise ArtifactError(f"Duplicate YAML key '{sorted(duplicate_keys)[0]}'")
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
    def cells(row: str) -> list[str]:
        values: list[str] = []
        current: list[str] = []
        escaped = False
        for character in row.strip("|"):
            if escaped:
                current.append(character)
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == "|":
                values.append("".join(current).strip())
                current = []
            else:
                current.append(character)
        values.append("".join(current).strip())
        return values
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


def parse_test_cases(body: str) -> list[dict[str, Any]]:
    section = markdown_section(body, "Test cases")
    matches = list(re.finditer(r"^###\s+(TC-[A-Za-z0-9-]+)\s+(?:—|-)\s+(.+?)\s*$", section, re.MULTILINE))
    tests: list[dict[str, Any]] = []
    field_pattern = re.compile(r"^\*\*([^*]+):\*\*\s*(.*?)(?=^\*\*[^*]+:\*\*|\Z)", re.MULTILINE | re.DOTALL)
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section)
        block = section[match.end():end]
        fields = {
            label.strip().lower(): re.sub(r"\s+", " ", value).strip()
            for label, value in field_pattern.findall(block)
        }
        supports = [value.strip(" `") for value in fields.get("supports stories", "").split(",") if value.strip(" `")]
        contracts = [value.strip(" `") for value in fields.get("validates contracts", "").split(",") if value.strip(" `")]
        tests.append({
            "id": match.group(1),
            "title": match.group(2).strip(),
            "level": fields.get("level", "").upper().replace(" ", "_"),
            "type": fields.get("type", ""),
            "owner": fields.get("owner", ""),
            "status": status(fields.get("status"), "UNKNOWN"),
            "supports": supports,
            "validatesContracts": contracts,
            "expected": fields.get("expected", ""),
        })
    return tests


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
            "description": row.get("Required behavior", ""),
        })
    return contracts


REQUIRED_INITIATIVE_HEADINGS = {
    "Problem and target users",
    "Goals, objectives, and expected outcomes",
    "Success measures",
    "Scope and non-goals",
    "Primary journeys and business rules",
    "Risks and assumptions",
    "Fat-slice roadmap overview",
}
REQUIRED_SLICE_HEADINGS = {
    "Capability outcome",
    "Scope and non-goals",
    "Lifecycle and journeys",
    "User stories and acceptance",
    "Test cases",
    "Security, accessibility, and operations",
    "Contracts and dependencies",
    "Observability, rollout, and rollback",
    "Planning validation",
}
REQUIRED_SLICE_METADATA = {
    "schema_version", "initiative_id", "initiative_revision", "slice_id", "title",
    "slice_revision", "status", "order", "priority", "dependencies",
}
REQUIRED_REPORT_HEADINGS = {
    "Released capability and scope",
    "Source revisions and commits",
    "Work-package completion",
    "Traceability and lifecycle verification",
    "CLI test evidence",
    "Security, accessibility, and migration evidence",
    "Deployment, feature flags, and rollback",
    "Observability and support readiness",
    "Defects, waivers, and remaining risks",
    "Independent QA recommendation",
    "Release evidence",
    "Outcome observation",
}
ALLOWED_SLICE_STATUSES = {
    "DRAFT", "PLANNING_REVIEW", "READY_FOR_DEVELOPMENT", "MOBILIZING", "EXECUTION_READY",
    "IN_PROGRESS", "READY_FOR_QA", "VERIFYING", "RELEASE_READY", "RELEASED",
    "OUTCOME_VALIDATED", "NEEDS_UPSTREAM_CLARIFICATION", "HUMAN_DECISION_REQUIRED",
    "REWORK_REQUIRED", "REVERIFY_REQUIRED", "REPLAN_REQUIRED", "BLOCKED", "PAUSED", "SUPERSEDED",
}
ALLOWED_PACKAGE_STATUSES = {
    "BLOCKED", "READY", "IN_PROGRESS", "VERIFYING", "DONE", "REWORK_REQUIRED",
    "REVERIFY_REQUIRED", "PAUSED",
}
ALLOWED_INITIATIVE_STATUSES = {
    "DRAFT", "DISCOVERING", "PROTOTYPING", "INITIATIVE_REVIEW", "INITIATIVE_READY",
    "EXECUTING", "PAUSED", "RELEASED", "OUTCOME_VALIDATED", "REPLAN_REQUIRED",
}


def markdown_headings(body: str, level: int | None = None) -> list[str]:
    pattern = r"^(#{1,6})\s+(.+?)\s*$"
    return [
        title.strip()
        for marks, title in re.findall(pattern, body, re.MULTILINE)
        if level is None or len(marks) == level
    ]


def add_diagnostic(
    diagnostics: list[dict[str, Any]],
    product_root: Path,
    path: Path,
    code: str,
    message: str,
    *,
    severity: str = "error",
    slice_id: str = "",
) -> None:
    diagnostics.append({
        "severity": severity,
        "code": code,
        "file": relative_path(path, product_root),
        "sliceId": slice_id,
        "message": message,
    })


def is_blank(value: Any) -> bool:
    return value is None or value == ""


def validate_product_artifacts(
    product_root: Path,
    selected_slice_ids: set[str] | None = None,
    require_execution_plan: bool = False,
) -> list[dict[str, Any]]:
    """Validate every canonical artifact and all cross-artifact references.

    When selected_slice_ids is None, discovery is repository-wide. This is the
    contract used by both the CLI validator and the dashboard projection.
    """
    product_root = product_root.resolve()
    base = product_root / "docs" / "meta-pds"
    diagnostics: list[dict[str, Any]] = []

    def error(path: Path, code: str, message: str, slice_id: str = "", severity: str = "error") -> None:
        add_diagnostic(diagnostics, product_root, path, code, message, severity=severity, slice_id=slice_id)

    def load_yaml(path: Path, required: bool = True) -> dict[str, Any] | None:
        if not path.exists():
            if required:
                error(path, "artifact.missing", "Required canonical artifact is missing")
            return None
        try:
            return read_yaml(path, required=True)
        except (ArtifactError, OSError) as exc:
            error(path, "artifact.parse", str(exc))
            return None

    def load_markdown(path: Path, required: bool = True) -> tuple[dict[str, Any], str] | None:
        if not path.exists():
            if required:
                error(path, "artifact.missing", "Required canonical artifact is missing")
            return None
        try:
            return read_markdown(path)
        except (ArtifactError, OSError) as exc:
            error(path, "artifact.parse", str(exc))
            return None

    initiative_path = base / "initiative.md"
    initiative_record = load_markdown(initiative_path)
    initiative_id = ""
    initiative_revision: int | None = None
    roadmap_ids: set[str] = set()
    if initiative_record:
        metadata, body = initiative_record
        initiative_id = str(metadata.get("initiative_id") or "")
        initiative_revision = metadata.get("revision") if isinstance(metadata.get("revision"), int) else None
        for field in ["schema_version", "initiative_id", "title", "revision", "status"]:
            if field not in metadata or is_blank(metadata.get(field)):
                error(initiative_path, "initiative.field", f"Frontmatter field '{field}' is required")
        if metadata.get("schema_version") != 2:
            error(initiative_path, "schema.version", "schema_version must be 2")
        if not isinstance(metadata.get("revision"), int):
            error(initiative_path, "initiative.type", "revision must be an integer")
        if initiative_id and not re.fullmatch(r"INIT-[A-Za-z0-9-]+", initiative_id):
            error(initiative_path, "initiative.id", "initiative_id must start with 'INIT-'")
        if status(metadata.get("status")) not in ALLOWED_INITIATIVE_STATUSES:
            error(initiative_path, "initiative.status", f"Unknown initiative status '{metadata.get('status')}'")
        headings = set(markdown_headings(body, 2))
        for heading in sorted(REQUIRED_INITIATIVE_HEADINGS - headings):
            error(initiative_path, "initiative.heading", f"Missing exact H2 heading '{heading}'")
        roadmap_section = markdown_section(body, "Fat-slice roadmap overview")
        roadmap_rows = parse_table(roadmap_section)
        table_lines = [line for line in roadmap_section.splitlines() if line.strip().startswith("|")]
        if table_lines:
            headers = [value.strip() for value in table_lines[0].strip("|").split("|")]
            expected = ["Order", "Slice ID", "Slice", "Capability outcome", "Priority", "Dependencies", "Status"]
            if headers != expected:
                error(initiative_path, "initiative.roadmap-columns", f"Roadmap columns must be: {', '.join(expected)}")
        for index, row in enumerate(roadmap_rows, start=1):
            slice_id = row.get("Slice ID", "").strip(" `")
            if not slice_id:
                error(initiative_path, "initiative.roadmap-id", f"Roadmap row {index} has no Slice ID")
            elif slice_id in roadmap_ids:
                error(initiative_path, "id.duplicate-slice", f"Duplicate roadmap Slice ID '{slice_id}'", slice_id)
            else:
                roadmap_ids.add(slice_id)

    decisions_path = base / "decision-log.yaml"
    decisions = load_yaml(decisions_path)
    decision_schema = 0
    decision_entries_by_key: dict[str, dict[str, Any]] = {}
    known_decision_keys: set[str] = set()
    if decisions is not None:
        for field in ["schema_version", "initiative_id", "decisions"]:
            if field not in decisions:
                error(decisions_path, "decision-log.field", f"Top-level field '{field}' is required")
        decision_schema = decisions.get("schema_version") if isinstance(decisions.get("schema_version"), int) else 0
        if decision_schema not in {2, 3}:
            error(decisions_path, "schema.version", "schema_version must be 2 or 3")
        elif decision_schema == 2:
            error(decisions_path, "schema.legacy", "decision-log schema v2 is supported for reading; migrate to v3 for canonical keys, types, phases, and contradictions", severity="warning")
        if initiative_id and decisions.get("initiative_id") != initiative_id:
            error(decisions_path, "initiative.mismatch", "initiative_id does not match initiative.md")
        entries = decisions.get("decisions")
        if not isinstance(entries, list):
            error(decisions_path, "decision-log.type", "decisions must be a list")
            entries = []
        seen_decisions: set[str] = set()
        seen_keys: set[str] = set()
        for index, entry in enumerate(entries):
            label = f"decisions[{index}]"
            if not isinstance(entry, dict):
                error(decisions_path, "decision.type", f"{label} must be a mapping")
                continue
            required_fields = ["id", "revision", "status", "question", "decision", "affected_artifacts", "authority"]
            if decision_schema == 3:
                required_fields.extend([
                    "key", "type", "secondary_types", "phases", "rationale", "evidence",
                    "depends_on", "contradicts", "approved_by", "decided_at", "supersedes",
                ])
            for field in required_fields:
                if field not in entry:
                    error(decisions_path, "decision.field", f"{label}.{field} is required")
            decision_id = entry.get("id")
            if not isinstance(decision_id, str) or not decision_id:
                error(decisions_path, "decision.id", f"{label}.id must be a non-empty string")
            elif decision_id in seen_decisions:
                error(decisions_path, "id.duplicate-decision", f"Duplicate decision ID '{decision_id}'")
            else:
                seen_decisions.add(decision_id)
            decision_key = entry.get("key") or (f"legacy.{str(decision_id).lower()}" if decision_id else "")
            if not isinstance(decision_key, str) or not DECISION_KEY_PATTERN.fullmatch(decision_key):
                error(decisions_path, "decision.key", f"{label}.key must be a lowercase dot- or hyphen-separated semantic key")
            elif decision_key in seen_keys:
                error(decisions_path, "id.duplicate-decision-key", f"Duplicate decision key '{decision_key}'")
            else:
                seen_keys.add(decision_key)
                known_decision_keys.add(decision_key)
                decision_entries_by_key[decision_key] = entry
            if status(entry.get("status")) not in {"PROPOSED", "TESTING", "LOCKED", "SUPERSEDED"}:
                error(decisions_path, "decision.status", f"{label}.status is invalid")
            if not isinstance(entry.get("revision"), int):
                error(decisions_path, "decision.type", f"{label}.revision must be an integer")
            if entry.get("authority") not in {"HUMAN", "PM"}:
                error(decisions_path, "decision.authority", f"{label}.authority must be HUMAN or PM")
            primary_type = str(entry.get("type") or "FEATURE_CAPABILITY")
            if primary_type not in DECISION_TYPES:
                error(decisions_path, "decision.category", f"{label}.type is not a supported decision type")
            for field in ["secondary_types", "phases", "evidence", "depends_on", "contradicts", "affected_artifacts"]:
                if not isinstance(entry.get(field, []), list):
                    error(decisions_path, "decision.type", f"{label}.{field} must be a list")
            secondary_types = entry.get("secondary_types", []) if isinstance(entry.get("secondary_types", []), list) else []
            if len(secondary_types) != len(set(str(value) for value in secondary_types)):
                error(decisions_path, "decision.category", f"{label}.secondary_types must not contain duplicates")
            for secondary_type in secondary_types:
                if not isinstance(secondary_type, str) or secondary_type not in DECISION_TYPES:
                    error(decisions_path, "decision.category", f"{label}.secondary_types references unsupported '{secondary_type}'")
                elif secondary_type == primary_type:
                    error(decisions_path, "decision.category", f"{label}.secondary_types must not repeat the primary type")
            phases = entry.get("phases", ["GLOBAL"]) if isinstance(entry.get("phases", ["GLOBAL"]), list) else []
            if not phases:
                error(decisions_path, "decision.phase", f"{label}.phases must contain GLOBAL or at least one PHASE-N value")
            for phase in phases:
                if not isinstance(phase, str) or (phase != "GLOBAL" and not DECISION_PHASE_PATTERN.fullmatch(phase)):
                    error(decisions_path, "decision.phase", f"{label}.phases contains invalid phase '{phase}'")
            if "GLOBAL" in phases and len(phases) > 1:
                error(decisions_path, "decision.phase", f"{label}.phases cannot combine GLOBAL with numbered phases")
            for field in ["question", "decision", "rationale", "approved_by", "decided_at", "supersedes"]:
                if field in entry and not isinstance(entry.get(field), str):
                    error(decisions_path, "decision.type", f"{label}.{field} must be text")

        dependency_graph: dict[str, list[str]] = {key: [] for key in known_decision_keys}
        checked_contradictions: set[tuple[str, str]] = set()
        for decision_key, entry in decision_entries_by_key.items():
            for field in ["depends_on", "contradicts"]:
                references = entry.get(field, []) if isinstance(entry.get(field, []), list) else []
                for referenced_key in references:
                    if not isinstance(referenced_key, str):
                        error(decisions_path, "reference.type", f"Decision '{decision_key}' {field} values must be decision keys")
                    elif referenced_key == decision_key:
                        error(decisions_path, "reference.decision", f"Decision '{decision_key}' cannot {field} itself")
                    elif referenced_key not in known_decision_keys:
                        error(decisions_path, "reference.decision", f"Decision '{decision_key}' {field} unknown key '{referenced_key}'")
                    elif field == "depends_on":
                        dependency_graph[decision_key].append(referenced_key)
                    else:
                        pair = tuple(sorted((decision_key, referenced_key)))
                        if pair in checked_contradictions:
                            continue
                        checked_contradictions.add(pair)
                        other = decision_entries_by_key[referenced_key]
                        if status(entry.get("status")) == "LOCKED" and status(other.get("status")) == "LOCKED":
                            error(decisions_path, "decision.locked-contradiction", f"Locked decisions '{decision_key}' and '{referenced_key}' contradict each other")
            supersedes = entry.get("supersedes")
            if supersedes == decision_key:
                error(decisions_path, "reference.decision", f"Decision '{decision_key}' cannot supersede itself")
            elif supersedes and supersedes not in known_decision_keys:
                error(decisions_path, "reference.decision", f"Decision '{decision_key}' supersedes unknown key '{supersedes}'")
        visiting_decisions: set[str] = set()
        visited_decisions: set[str] = set()

        def visit_decision(decision_key: str) -> None:
            if decision_key in visiting_decisions:
                error(decisions_path, "dependency.decision-cycle", f"Decision dependency cycle includes '{decision_key}'")
                return
            if decision_key in visited_decisions:
                return
            visiting_decisions.add(decision_key)
            for dependency_key in dependency_graph.get(decision_key, []):
                visit_decision(dependency_key)
            visiting_decisions.remove(decision_key)
            visited_decisions.add(decision_key)

        for decision_key in dependency_graph:
            visit_decision(decision_key)

    delivery_path = base / "delivery-state.yaml"
    delivery = load_yaml(delivery_path)
    state_slice_ids: set[str] = set()
    if delivery is not None:
        delivery_schema = delivery.get("schema_version") if isinstance(delivery.get("schema_version"), int) else 0
        required_fields = [
            "schema_version", "initiative_id", "initiative_status", "active_planning_slice",
            "active_execution_slice", "slice_states", "blockers", "next_recommended_action",
        ]
        if delivery_schema == 3:
            required_fields.extend(["interaction_mode", "decision_review"])
        for field in required_fields:
            if field not in delivery:
                error(delivery_path, "delivery-state.field", f"Top-level field '{field}' is required")
        if delivery_schema not in {2, 3}:
            error(delivery_path, "schema.version", "schema_version must be 2 or 3")
        elif delivery_schema == 2:
            error(delivery_path, "schema.legacy", "delivery-state schema v2 is supported for reading; migrate to v3 for interaction modes and decision review state", severity="warning")
        if initiative_id and delivery.get("initiative_id") != initiative_id:
            error(delivery_path, "initiative.mismatch", "initiative_id does not match initiative.md")
        if initiative_revision is not None and delivery.get("initiative_revision") != initiative_revision:
            error(delivery_path, "revision.mismatch", "initiative_revision does not match initiative.md")
        if not isinstance(delivery.get("initiative_revision"), int):
            error(delivery_path, "delivery-state.type", "initiative_revision must be an integer")
        if status(delivery.get("initiative_status")) not in ALLOWED_INITIATIVE_STATUSES:
            error(delivery_path, "initiative.status", f"Unknown initiative status '{delivery.get('initiative_status')}'")
        for field in ["active_planning_slice", "active_execution_slice"]:
            if delivery.get(field) is not None and not isinstance(delivery.get(field), str):
                error(delivery_path, "delivery-state.type", f"{field} must be null or a Slice ID")
        states = delivery.get("slice_states")
        if not isinstance(states, list):
            error(delivery_path, "delivery-state.type", "slice_states must be a list")
            states = []
        for index, entry in enumerate(states):
            label = f"slice_states[{index}]"
            if not isinstance(entry, dict):
                error(delivery_path, "slice-state.type", f"{label} must be a mapping")
                continue
            slice_id = entry.get("slice_id")
            if not isinstance(slice_id, str) or not slice_id:
                error(delivery_path, "slice-state.id", f"{label}.slice_id must be a non-empty string")
                continue
            if slice_id in state_slice_ids:
                error(delivery_path, "id.duplicate-slice-state", f"Duplicate slice state '{slice_id}'", slice_id)
            state_slice_ids.add(slice_id)
            if status(entry.get("status")) not in ALLOWED_SLICE_STATUSES:
                error(delivery_path, "slice-state.status", f"{label}.status is invalid", slice_id)
        for field in ["paused_slices", "completed_slices", "blockers", "risks", "evidence"]:
            if not isinstance(delivery.get(field, []), list):
                error(delivery_path, "delivery-state.type", f"{field} must be a list")
        if delivery.get("human_decision_required") is not None and not isinstance(delivery.get("human_decision_required"), (str, dict)):
            error(delivery_path, "delivery-state.type", "human_decision_required must be null, text, or a mapping")
        if not isinstance(delivery.get("next_recommended_action"), (str, dict)):
            error(delivery_path, "delivery-state.type", "next_recommended_action must be text or a mapping")
        if delivery.get("prototype") is not None and not isinstance(delivery.get("prototype"), dict):
            error(delivery_path, "delivery-state.type", "prototype must be null or a mapping")
        interaction_mode = status(delivery.get("interaction_mode"), "EXPLORE")
        if interaction_mode not in ALLOWED_INTERACTION_MODES:
            error(delivery_path, "delivery-state.mode", f"Unknown interaction_mode '{delivery.get('interaction_mode')}'")
        decision_review = delivery.get("decision_review", {"pending_keys": [], "last_checkpoint_at": ""})
        if not isinstance(decision_review, dict):
            error(delivery_path, "delivery-state.type", "decision_review must be a mapping")
        else:
            pending_keys = decision_review.get("pending_keys", [])
            if not isinstance(pending_keys, list):
                error(delivery_path, "delivery-state.type", "decision_review.pending_keys must be a list")
            else:
                for decision_key in pending_keys:
                    if not isinstance(decision_key, str):
                        error(delivery_path, "reference.type", "decision_review.pending_keys values must be decision keys")
                    elif decision_key not in known_decision_keys:
                        error(delivery_path, "reference.decision", f"decision_review.pending_keys references unknown key '{decision_key}'")
            if not isinstance(decision_review.get("last_checkpoint_at", ""), str):
                error(delivery_path, "delivery-state.type", "decision_review.last_checkpoint_at must be text")

    slices_dir = base / "slices"
    all_slice_paths = sorted(slices_dir.glob("*.md")) if slices_dir.exists() else []
    if selected_slice_ids is None:
        slice_paths = all_slice_paths
    else:
        slice_paths = [slices_dir / f"{slice_id}.md" for slice_id in sorted(selected_slice_ids)]

    slice_documents: dict[str, tuple[Path, dict[str, Any], str, set[str], set[str]]] = {}
    declared_slice_ids: dict[str, Path] = {}
    global_story_ids: dict[str, Path] = {}
    global_test_ids: dict[str, Path] = {}
    for path in slice_paths:
        record = load_markdown(path)
        if not record:
            continue
        metadata, body = record
        slice_id = str(metadata.get("slice_id") or path.stem)
        for field in sorted(REQUIRED_SLICE_METADATA):
            field_value = metadata.get(field)
            if field not in metadata or (field_value is None or field_value == "") and field != "dependencies":
                error(path, "slice.field", f"Frontmatter field '{field}' is required", slice_id)
        if metadata.get("schema_version") != 2:
            error(path, "schema.version", "schema_version must be 2", slice_id)
        if metadata.get("slice_id") != path.stem:
            error(path, "slice.filename", "slice_id must match the filename", slice_id)
        if not re.fullmatch(r"SLICE-[A-Za-z0-9-]+", slice_id):
            error(path, "slice.id", "slice_id must start with 'SLICE-'", slice_id)
        if slice_id in declared_slice_ids:
            error(path, "id.duplicate-slice", f"Slice ID '{slice_id}' is also declared by {relative_path(declared_slice_ids[slice_id], product_root)}", slice_id)
        else:
            declared_slice_ids[slice_id] = path
        if initiative_id and metadata.get("initiative_id") != initiative_id:
            error(path, "initiative.mismatch", "initiative_id does not match initiative.md", slice_id)
        if initiative_revision is not None and metadata.get("initiative_revision") != initiative_revision:
            error(path, "revision.mismatch", "initiative_revision does not match initiative.md", slice_id)
        for field in ["initiative_revision", "slice_revision", "order"]:
            if not isinstance(metadata.get(field), int):
                error(path, "slice.type", f"{field} must be an integer", slice_id)
        if not re.fullmatch(r"P[0-3]", str(metadata.get("priority") or "")):
            error(path, "slice.priority", "priority must be P0, P1, P2, or P3", slice_id)
        if not isinstance(metadata.get("dependencies"), list):
            error(path, "slice.type", "dependencies must be a list", slice_id)
        if status(metadata.get("status")) not in ALLOWED_SLICE_STATUSES:
            error(path, "slice.status", f"Unknown slice status '{metadata.get('status')}'", slice_id)
        headings = set(markdown_headings(body, 2))
        for heading in sorted(REQUIRED_SLICE_HEADINGS - headings):
            error(path, "slice.heading", f"Missing exact H2 heading '{heading}'", slice_id)
        if "Contract expectations" not in set(markdown_headings(markdown_section(body, "Contracts and dependencies"), 3)):
            error(path, "slice.contract-heading", "Missing exact H3 heading 'Contract expectations'", slice_id)
        contract_section = markdown_section(markdown_section(body, "Contracts and dependencies"), "Contract expectations", 3)
        contract_lines = [line for line in contract_section.splitlines() if line.strip().startswith("|")]
        if contract_lines:
            headers = [value.strip() for value in contract_lines[0].strip("|").split("|")]
            expected = ["Contract", "Version", "Owner", "Required behavior"]
            if headers != expected:
                error(path, "slice.contract-columns", f"Contract columns must be: {', '.join(expected)}", slice_id)

        story_section = markdown_section(body, "User stories and acceptance")
        story_headings = markdown_headings(story_section, 3)
        stories = parse_stories(body)
        if len(stories) != len(story_headings):
            error(path, "slice.story-grammar", "Every story H3 must use '### US-<id> — <title>'", slice_id)
        if not stories:
            error(path, "slice.stories", "At least one parseable user story is required", slice_id)
        story_ids: set[str] = set()
        for story in stories:
            story_id = story["id"]
            if story_id in story_ids:
                error(path, "id.duplicate-story", f"Duplicate story ID '{story_id}'", slice_id)
            story_ids.add(story_id)
            if story_id in global_story_ids:
                error(path, "id.duplicate-story-global", f"Story ID '{story_id}' is already used in {relative_path(global_story_ids[story_id], product_root)}", slice_id)
            else:
                global_story_ids[story_id] = path
            if not story.get("description"):
                error(path, "slice.story-description", f"Story '{story_id}' has no parseable Story text", slice_id)
            if not story.get("acceptanceCriteria"):
                error(path, "slice.story-acceptance", f"Story '{story_id}' has no parseable acceptance criteria", slice_id)

        test_section = markdown_section(body, "Test cases")
        test_headings = markdown_headings(test_section, 3)
        tests = parse_test_cases(body)
        if len(tests) != len(test_headings):
            error(path, "slice.test-grammar", "Every test H3 must use '### TC-<id> — <title>'", slice_id)
        if not tests:
            error(path, "slice.tests", "At least one parseable test case is required", slice_id)
        test_ids: set[str] = set()
        for test in tests:
            test_id = test["id"]
            if test_id in test_ids:
                error(path, "id.duplicate-test", f"Duplicate test ID '{test_id}'", slice_id)
            test_ids.add(test_id)
            if test_id in global_test_ids:
                error(path, "id.duplicate-test-global", f"Test ID '{test_id}' is already used in {relative_path(global_test_ids[test_id], product_root)}", slice_id)
            else:
                global_test_ids[test_id] = path
            if test.get("level") not in {"STORY", "CONTRACT", "CROSS_CUTTING", "SLICE"}:
                error(path, "slice.test-level", f"Test '{test_id}' has invalid Level", slice_id)
            if test.get("status") not in {"PLANNED", "READY", "BLOCKED", "PASSED", "FAILED"}:
                error(path, "slice.test-status", f"Test '{test_id}' has invalid Status", slice_id)
            for field in ["title", "type", "owner", "status", "expected"]:
                if not test.get(field):
                    error(path, "slice.test-field", f"Test '{test_id}' has no {field}", slice_id)
            if not test.get("supports"):
                error(path, "slice.test-support", f"Test '{test_id}' supports no stories", slice_id)
            for story_id in test.get("supports", []):
                if story_id not in story_ids:
                    error(path, "reference.story", f"Test '{test_id}' references unknown story '{story_id}'", slice_id)
        slice_documents[slice_id] = (path, metadata, body, story_ids, test_ids)

    known_slice_ids = roadmap_ids | set(declared_slice_ids)
    slice_dependency_graph: dict[str, list[str]] = {}
    for slice_id, (path, metadata, _, _, _) in slice_documents.items():
        slice_dependency_graph[slice_id] = []
        for dependency in metadata.get("dependencies", []) if isinstance(metadata.get("dependencies"), list) else []:
            if not isinstance(dependency, str):
                error(path, "reference.type", "Every slice dependency must be a Slice ID string", slice_id)
            elif dependency not in known_slice_ids:
                error(path, "reference.slice", f"Unknown slice dependency '{dependency}'", slice_id)
            elif dependency in slice_documents:
                slice_dependency_graph[slice_id].append(dependency)
    visiting_slices: set[str] = set()
    visited_slices: set[str] = set()
    def visit_slice(node: str) -> None:
        if node in visiting_slices:
            path = slice_documents[node][0]
            error(path, "dependency.slice-cycle", f"Slice dependency cycle includes '{node}'", node)
            return
        if node in visited_slices:
            return
        visiting_slices.add(node)
        for dependency in slice_dependency_graph.get(node, []):
            visit_slice(dependency)
        visiting_slices.remove(node)
        visited_slices.add(node)
    for slice_id in slice_dependency_graph:
        visit_slice(slice_id)
    for state_slice_id in state_slice_ids:
        if state_slice_id not in known_slice_ids:
            error(delivery_path, "reference.slice", f"slice_states references unknown slice '{state_slice_id}'", state_slice_id)

    execution_dir = base / "execution"
    all_execution_paths = sorted(execution_dir.glob("*.yaml")) if execution_dir.exists() else []
    if selected_slice_ids is None:
        execution_paths = all_execution_paths
    else:
        execution_paths = [execution_dir / f"{slice_id}.yaml" for slice_id in sorted(selected_slice_ids) if (execution_dir / f"{slice_id}.yaml").exists() or require_execution_plan]
    execution_slice_ids: dict[str, Path] = {}
    execution_documents: dict[str, dict[str, Any]] = {}
    global_package_ids: dict[str, Path] = {}
    global_contract_ids: dict[str, Path] = {}
    for path in execution_paths:
        document = load_yaml(path, required=require_execution_plan or path.exists())
        if document is None:
            continue
        slice_id = str(document.get("slice_id") or path.stem)
        for field in [
            "schema_version", "initiative_id", "slice_id", "slice_revision", "contract_version", "status",
            "repository", "code_areas", "integration_contracts", "critical_path", "execution_waves",
            "integration_sequence", "merge_sequence", "deployment_sequence", "feature_flags",
            "observability_checks", "rollback_sequence", "work_packages", "validation",
        ]:
            if field not in document:
                error(path, "execution.field", f"Top-level field '{field}' is required", slice_id)
        if document.get("schema_version") != 2:
            error(path, "schema.version", "schema_version must be 2", slice_id)
        if document.get("slice_id") != path.stem:
            error(path, "execution.filename", "slice_id must match the filename", slice_id)
        if slice_id in execution_slice_ids:
            error(path, "id.duplicate-execution", f"Execution plan for '{slice_id}' is already declared by {relative_path(execution_slice_ids[slice_id], product_root)}", slice_id)
        execution_slice_ids[slice_id] = path
        execution_documents[slice_id] = document
        slice_record = slice_documents.get(slice_id)
        if slice_id not in known_slice_ids:
            error(path, "reference.slice", f"Execution plan references unknown slice '{slice_id}'", slice_id)
        if initiative_id and document.get("initiative_id") != initiative_id:
            error(path, "initiative.mismatch", "initiative_id does not match initiative.md", slice_id)
        if slice_record and document.get("slice_revision") != slice_record[1].get("slice_revision"):
            error(path, "revision.mismatch", "slice_revision does not match the slice artifact", slice_id)
        if status(document.get("status")) not in {"MOBILIZING", "EXECUTION_READY", "EXECUTING", "IN_PROGRESS", "READY_FOR_QA", "BLOCKED", "PAUSED"}:
            error(path, "execution.status", f"Unknown execution status '{document.get('status')}'", slice_id)
        for field in ["repository", "code_areas", "validation"]:
            if not isinstance(document.get(field), dict):
                error(path, "execution.type", f"{field} must be a mapping", slice_id)
        for field in ["critical_path", "execution_waves", "integration_sequence", "merge_sequence", "deployment_sequence", "feature_flags", "observability_checks", "rollback_sequence"]:
            if not isinstance(document.get(field), list):
                error(path, "execution.type", f"{field} must be a list", slice_id)
        contracts = document.get("integration_contracts")
        if not isinstance(contracts, list):
            error(path, "execution.type", "integration_contracts must be a list", slice_id)
            contracts = []
        contract_ids: set[str] = set()
        for index, contract in enumerate(contracts):
            label = f"integration_contracts[{index}]"
            if not isinstance(contract, dict):
                error(path, "contract.type", f"{label} must be a mapping", slice_id)
                continue
            for field in ["id", "name", "type", "version", "status", "owner", "path"]:
                if field not in contract or is_blank(contract.get(field)):
                    error(path, "contract.field", f"{label}.{field} is required", slice_id)
            contract_id = contract.get("id")
            if isinstance(contract_id, str) and contract_id:
                if contract_id in contract_ids:
                    error(path, "id.duplicate-contract", f"Duplicate contract ID '{contract_id}'", slice_id)
                contract_ids.add(contract_id)
                if contract_id in global_contract_ids:
                    error(path, "id.duplicate-contract-global", f"Contract ID '{contract_id}' is already used in {relative_path(global_contract_ids[contract_id], product_root)}", slice_id)
                else:
                    global_contract_ids[contract_id] = path
        packages = document.get("work_packages")
        if not isinstance(packages, list):
            error(path, "execution.type", "work_packages must be a list", slice_id)
            packages = []
        if not packages:
            error(path, "execution.packages", "work_packages must contain at least one package", slice_id)
        package_by_id: dict[str, dict[str, Any]] = {}
        story_ids = slice_record[3] if slice_record else set()
        test_ids = slice_record[4] if slice_record else set()
        for index, package in enumerate(packages):
            label = f"work_packages[{index}]"
            if not isinstance(package, dict):
                error(path, "package.type", f"{label} must be a mapping", slice_id)
                continue
            for field in [
                "id", "title", "description", "area", "owner", "status", "blocker", "contract_version",
                "depends_on", "supports", "inputs", "produces", "owned_paths", "forbidden_paths",
                "entry_checks", "exit_checks", "required_tests", "applicable_skills", "integration_owner",
            ]:
                if field not in package:
                    error(path, "package.field", f"{label}.{field} is required", slice_id)
            package_id = package.get("id")
            if not isinstance(package_id, str) or not package_id:
                error(path, "package.id", f"{label}.id must be a non-empty string", slice_id)
                continue
            if package_id in package_by_id:
                error(path, "id.duplicate-package", f"Duplicate work-package ID '{package_id}'", slice_id)
            package_by_id[package_id] = package
            if package_id in global_package_ids:
                error(path, "id.duplicate-package-global", f"Work-package ID '{package_id}' is already used in {relative_path(global_package_ids[package_id], product_root)}", slice_id)
            else:
                global_package_ids[package_id] = path
            if status(package.get("status")) not in ALLOWED_PACKAGE_STATUSES:
                error(path, "package.status", f"{label}.status is invalid", slice_id)
            for field in ["title", "description", "area", "owner"]:
                if not isinstance(package.get(field), str) or not package.get(field):
                    error(path, "package.field", f"{label}.{field} must be non-empty text", slice_id)
            for field in ["depends_on", "supports", "required_tests", "applicable_skills", "inputs", "produces", "owned_paths", "forbidden_paths", "entry_checks", "exit_checks"]:
                if not isinstance(package.get(field, []), list):
                    error(path, "package.type", f"{label}.{field} must be a list", slice_id)
            for skill_name in package.get("applicable_skills", []) if isinstance(package.get("applicable_skills"), list) else []:
                if not isinstance(skill_name, str):
                    error(path, "reference.type", f"{label}.applicable_skills values must be skill-name strings", slice_id)
                elif skill_name not in SUPPORTED_IMPLEMENTATION_SKILLS:
                    error(path, "reference.skill", f"{label}.applicable_skills references unsupported '{skill_name}'", slice_id)
            for story_id in package.get("supports", []) if isinstance(package.get("supports"), list) else []:
                if not isinstance(story_id, str):
                    error(path, "reference.type", f"{label}.supports values must be Story ID strings", slice_id)
                elif story_id not in story_ids:
                    error(path, "reference.story", f"{label}.supports references unknown '{story_id}'", slice_id)
            if isinstance(package.get("supports"), list) and not package.get("supports"):
                error(path, "package.traceability", f"{label}.supports must cite at least one story", slice_id)
            for test_id in package.get("required_tests", []) if isinstance(package.get("required_tests"), list) else []:
                if not isinstance(test_id, str):
                    error(path, "reference.type", f"{label}.required_tests values must be Test ID strings", slice_id)
                elif test_id not in test_ids:
                    error(path, "reference.test", f"{label}.required_tests references unknown '{test_id}'", slice_id)
            if isinstance(package.get("required_tests"), list) and not package.get("required_tests"):
                error(path, "package.traceability", f"{label}.required_tests must cite at least one test", slice_id)
        graph: dict[str, list[str]] = {}
        for package_id, package in package_by_id.items():
            graph[package_id] = []
            for dependency in package.get("depends_on", []) if isinstance(package.get("depends_on"), list) else []:
                if not isinstance(dependency, str):
                    error(path, "reference.type", f"'{package_id}' dependency values must be Work-package ID strings", slice_id)
                elif dependency not in package_by_id:
                    error(path, "reference.package", f"'{package_id}' depends on unknown '{dependency}'", slice_id)
                else:
                    graph[package_id].append(dependency)
        visiting: set[str] = set()
        visited: set[str] = set()
        def visit(node: str) -> None:
            if node in visiting:
                error(path, "dependency.cycle", f"Dependency cycle includes '{node}'", slice_id)
                return
            if node in visited:
                return
            visiting.add(node)
            for dependency in graph.get(node, []):
                visit(dependency)
            visiting.remove(node)
            visited.add(node)
        for package_id in graph:
            visit(package_id)
        if status(document.get("status")) == "READY_FOR_QA":
            incomplete = [package_id for package_id, package in package_by_id.items() if status(package.get("status")) != "DONE"]
            if incomplete:
                error(path, "execution.gate", f"READY_FOR_QA requires every package DONE; incomplete: {', '.join(incomplete)}", slice_id)
        critical_path = document.get("critical_path", []) if isinstance(document.get("critical_path"), list) else []
        for package_id in critical_path:
            if not isinstance(package_id, str):
                error(path, "reference.type", "critical_path values must be Work-package ID strings", slice_id)
            elif package_id not in package_by_id:
                error(path, "reference.package", f"critical_path references unknown '{package_id}'", slice_id)
        seen_waves: set[str] = set()
        waves = document.get("execution_waves", []) if isinstance(document.get("execution_waves"), list) else []
        for index, wave in enumerate(waves):
            label = f"execution_waves[{index}]"
            if not isinstance(wave, dict):
                error(path, "wave.type", f"{label} must be a mapping", slice_id)
                continue
            for field in ["id", "purpose", "work_packages"]:
                if field not in wave:
                    error(path, "wave.field", f"{label}.{field} is required", slice_id)
            wave_id = wave.get("id")
            if not isinstance(wave_id, str) or not wave_id:
                error(path, "wave.id", f"{label}.id must be a non-empty string", slice_id)
            elif wave_id in seen_waves:
                error(path, "id.duplicate-wave", f"Duplicate execution wave ID '{wave_id}'", slice_id)
            else:
                seen_waves.add(wave_id)
            if not isinstance(wave.get("work_packages"), list):
                error(path, "wave.type", f"{label}.work_packages must be a list", slice_id)
            else:
                for package_id in wave["work_packages"]:
                    if not isinstance(package_id, str):
                        error(path, "reference.type", f"{label}.work_packages values must be Work-package ID strings", slice_id)
                    elif package_id not in package_by_id:
                        error(path, "reference.package", f"{label}.work_packages references unknown '{package_id}'", slice_id)

    reports_dir = base / "reports"
    all_report_paths = sorted(reports_dir.glob("*.md")) if reports_dir.exists() else []
    report_paths = all_report_paths if selected_slice_ids is None else [path for path in all_report_paths if path.stem in selected_slice_ids]
    report_slice_ids: dict[str, Path] = {}
    for path in report_paths:
        record = load_markdown(path)
        if not record:
            continue
        metadata, body = record
        slice_id = str(metadata.get("slice_id") or path.stem)
        for field in ["schema_version", "initiative_id", "slice_id", "slice_revision", "contract_version", "status"]:
            if field not in metadata or is_blank(metadata.get(field)):
                error(path, "report.field", f"Frontmatter field '{field}' is required", slice_id)
        if metadata.get("schema_version") != 2:
            error(path, "schema.version", "schema_version must be 2", slice_id)
        if metadata.get("slice_id") != path.stem:
            error(path, "report.filename", "slice_id must match the filename", slice_id)
        if slice_id in report_slice_ids:
            error(path, "id.duplicate-report", f"Report for '{slice_id}' is already declared by {relative_path(report_slice_ids[slice_id], product_root)}", slice_id)
        report_slice_ids[slice_id] = path
        slice_record = slice_documents.get(slice_id)
        if slice_id not in known_slice_ids:
            error(path, "reference.slice", f"Report references unknown slice '{slice_id}'", slice_id)
        if initiative_id and metadata.get("initiative_id") != initiative_id:
            error(path, "initiative.mismatch", "initiative_id does not match initiative.md", slice_id)
        if slice_record and metadata.get("slice_revision") != slice_record[1].get("slice_revision"):
            error(path, "revision.mismatch", "slice_revision does not match the slice artifact", slice_id)
        execution_record = execution_documents.get(slice_id)
        if execution_record and metadata.get("contract_version") != execution_record.get("contract_version"):
            error(path, "contract-version.mismatch", "contract_version does not match the execution plan", slice_id)
        if status(metadata.get("status")) not in {"VERIFYING", "RELEASE_READY", "RELEASED", "OUTCOME_VALIDATED", "REWORK_REQUIRED", "REPLAN_REQUIRED"}:
            error(path, "report.status", f"Unknown report status '{metadata.get('status')}'", slice_id)
        headings = set(markdown_headings(body, 2))
        for heading in sorted(REQUIRED_REPORT_HEADINGS - headings):
            error(path, "report.heading", f"Missing exact H2 heading '{heading}'", slice_id)
        allowed_tests = slice_record[4] if slice_record else set()
        evidence_section = markdown_section(body, "CLI test evidence")
        evidence_lines = [line for line in evidence_section.splitlines() if line.strip().startswith("|")]
        if evidence_lines:
            headers = [value.strip() for value in evidence_lines[0].strip("|").split("|")]
            expected = ["Test ID", "Command", "Revision/environment", "Result", "Report/evidence"]
            if headers != expected:
                error(path, "report.evidence-columns", f"CLI evidence columns must be: {', '.join(expected)}", slice_id)
        rows = parse_table(evidence_section)
        seen_tests: set[str] = set()
        for index, row in enumerate(rows, start=1):
            test_id = row.get("Test ID", "").strip(" `")
            if not test_id:
                error(path, "report.test-id", f"CLI evidence row {index} has no Test ID", slice_id)
            elif test_id in seen_tests:
                error(path, "id.duplicate-report-test", f"Duplicate Test ID '{test_id}'", slice_id)
            elif test_id not in allowed_tests:
                error(path, "reference.test", f"Unknown Test ID '{test_id}'", slice_id)
            seen_tests.add(test_id)
            if status(metadata.get("status")) in {"RELEASE_READY", "RELEASED", "OUTCOME_VALIDATED"}:
                if status(row.get("Result")) not in {"PASS", "PASSED", "SUCCESS"}:
                    error(path, "report.gate", f"Test '{test_id}' must pass before {metadata.get('status')}", slice_id)
                for field in ["Command", "Revision/environment", "Report/evidence"]:
                    if not row.get(field):
                        error(path, "report.evidence", f"Test '{test_id}' has no {field}", slice_id)
        if status(metadata.get("status")) in {"RELEASE_READY", "RELEASED", "OUTCOME_VALIDATED"}:
            missing_tests = sorted(allowed_tests - seen_tests)
            if missing_tests:
                error(path, "report.gate", f"Release evidence is missing tests: {', '.join(missing_tests)}", slice_id)

    events_path = base / "delivery-events.jsonl"
    if selected_slice_ids is None and events_path.exists():
        for line_number, line in enumerate(events_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                error(events_path, "event.parse", f"Line {line_number}: {exc.msg}")
                continue
            if not isinstance(event, dict):
                error(events_path, "event.type", f"Line {line_number} must contain one JSON object")
                continue
            if not (event.get("at") or event.get("timestamp")):
                error(events_path, "event.field", f"Line {line_number} requires 'at' or 'timestamp'")
            if not (event.get("title") or event.get("event")):
                error(events_path, "event.field", f"Line {line_number} requires 'title' or 'event'")

    return sorted(diagnostics, key=lambda item: (item["file"], item["code"], item["message"]))


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else ([] if value is None or value == "" else [value])


def status(value: Any, default: str = "UNKNOWN") -> str:
    return str(value or default).strip().upper().replace("-", "_").replace(" ", "_")


def safe_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


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
            try:
                record = read_yaml(path)
            except (ArtifactError, OSError):
                continue
            slice_id = str(record.get("slice_id") or path.stem)
            if record.get("schema_version") != 2 or slice_id != path.stem or slice_id in records:
                continue
            record["_path"] = path
            records[slice_id] = record
    return records


def report_records(base: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    report_dir = base / "reports"
    if not report_dir.exists():
        return records
    for path in sorted(report_dir.glob("*.md")):
        try:
            metadata, body = read_markdown(path)
        except (ArtifactError, OSError):
            continue
        slice_id = str(metadata.get("slice_id") or path.stem)
        if metadata.get("schema_version") != 2 or slice_id != path.stem or slice_id in records:
            continue
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


def contract_markdown(product_root: Path, contract_path: Any) -> str:
    value = str(contract_path or "").strip()
    if not value or Path(value).suffix.lower() not in {".md", ".markdown"}:
        return ""
    product_root = product_root.resolve()
    candidate = (product_root / value).resolve()
    try:
        candidate.relative_to(product_root)
    except ValueError:
        return ""
    if not candidate.is_file():
        return ""
    text = candidate.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n.*?\n---\s*\n?(.*)\Z", text, re.DOTALL)
    return (match.group(1) if match else text).strip()


def run_readonly_command(command: list[str], cwd: Path, timeout: float = 5.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def parse_tracking(value: str) -> tuple[int, int, bool]:
    ahead_match = re.search(r"ahead\s+(\d+)", value)
    behind_match = re.search(r"behind\s+(\d+)", value)
    return (
        int(ahead_match.group(1)) if ahead_match else 0,
        int(behind_match.group(1)) if behind_match else 0,
        "gone" in value.lower(),
    )


def pull_request_records(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    records: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict) or not isinstance(item.get("number"), int):
            continue
        state = status(item.get("state"), "UNKNOWN")
        display_status = "DRAFT" if item.get("isDraft") and state == "OPEN" else state
        records.append({
            "number": item["number"],
            "title": str(item.get("title") or f"Pull request {item['number']}"),
            "status": display_status,
            "state": state,
            "isDraft": bool(item.get("isDraft")),
            "headBranch": str(item.get("headRefName") or ""),
            "baseBranch": str(item.get("baseRefName") or ""),
            "url": str(item.get("url") or ""),
            "reviewDecision": status(item.get("reviewDecision"), "UNKNOWN"),
            "mergeState": status(item.get("mergeStateStatus"), "UNKNOWN"),
            "updatedAt": str(item.get("updatedAt") or ""),
        })
    state_order = {"OPEN": 0, "DRAFT": 0, "MERGED": 1, "CLOSED": 2}
    records.sort(key=lambda item: item["updatedAt"], reverse=True)
    records.sort(key=lambda item: state_order.get(item["status"], 3))
    return records


def build_repository_data(project_root: Path, gh_executable: str | None = None) -> dict[str, Any]:
    project_root = project_root.resolve()
    unavailable = {
        "available": False,
        "root": str(project_root),
        "currentBranch": "",
        "defaultBranch": "",
        "dirtyPaths": 0,
        "branches": [],
        "pullRequests": [],
        "pullRequestSource": {"available": False, "kind": "github-cli", "message": "Git repository unavailable."},
        "message": "Git repository unavailable.",
    }
    try:
        resolved = run_readonly_command(["git", "rev-parse", "--show-toplevel"], project_root, timeout=2.0)
    except (OSError, subprocess.TimeoutExpired):
        return unavailable
    if resolved.returncode != 0 or not resolved.stdout.strip():
        return unavailable

    repository_root = Path(resolved.stdout.strip()).resolve()
    current_result = run_readonly_command(["git", "symbolic-ref", "--quiet", "--short", "HEAD"], repository_root, timeout=2.0)
    current_branch = current_result.stdout.strip() if current_result.returncode == 0 else "DETACHED"
    dirty_result = run_readonly_command(["git", "status", "--porcelain", "--untracked-files=normal"], repository_root, timeout=2.0)
    dirty_paths = len([line for line in dirty_result.stdout.splitlines() if line.strip()]) if dirty_result.returncode == 0 else 0

    branch_result = run_readonly_command([
        "git", "for-each-ref", "--sort=-committerdate",
        "--format=%(refname:short)%00%(objectname:short)%00%(upstream:short)%00%(upstream:track)%00%(committerdate:iso-strict)%00%(subject)",
        "refs/heads",
    ], repository_root, timeout=3.0)
    branches: list[dict[str, Any]] = []
    if branch_result.returncode == 0:
        for line in branch_result.stdout.splitlines():
            fields = line.split("\0")
            if len(fields) != 6 or not fields[0]:
                continue
            name, head, upstream, tracking, updated_at, subject = fields
            ahead, behind, upstream_gone = parse_tracking(tracking)
            branches.append({
                "name": name,
                "head": head,
                "subject": subject,
                "updatedAt": updated_at,
                "upstream": upstream,
                "ahead": ahead,
                "behind": behind,
                "upstreamGone": upstream_gone,
                "isCurrent": name == current_branch,
                "isManaged": name.startswith("codex/"),
                "status": "UPSTREAM_GONE" if upstream_gone else ("AHEAD_BEHIND" if ahead and behind else ("AHEAD" if ahead else ("BEHIND" if behind else ("ACTIVE" if name == current_branch else ("SYNCED" if upstream else "LOCAL"))))),
                "pullRequestNumber": None,
            })

    default_branch = ""
    default_result = run_readonly_command(["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"], repository_root, timeout=2.0)
    if default_result.returncode == 0:
        default_branch = default_result.stdout.strip().removeprefix("origin/")
    if not default_branch:
        names = {branch["name"] for branch in branches}
        default_branch = "main" if "main" in names else ("master" if "master" in names else "")

    gh_path = shutil.which("gh") if gh_executable is None else gh_executable
    pull_requests: list[dict[str, Any]] = []
    if not gh_path:
        pull_request_source = {"available": False, "kind": "github-cli", "message": "GitHub CLI is not installed."}
    else:
        try:
            pr_result = run_readonly_command([
                gh_path, "pr", "list", "--state", "all", "--limit", "100", "--json",
                "number,title,state,isDraft,headRefName,baseRefName,url,reviewDecision,mergeStateStatus,updatedAt",
            ], repository_root, timeout=8.0)
        except (OSError, subprocess.TimeoutExpired) as error:
            pull_request_source = {"available": False, "kind": "github-cli", "message": f"Pull-request lookup failed: {error.__class__.__name__}."}
        else:
            if pr_result.returncode == 0:
                try:
                    pull_requests = pull_request_records(json.loads(pr_result.stdout))
                except json.JSONDecodeError:
                    pull_requests = []
                    pull_request_source = {"available": False, "kind": "github-cli", "message": "GitHub CLI returned invalid JSON."}
                else:
                    pull_request_source = {"available": True, "kind": "github-cli", "message": "Live GitHub pull-request evidence."}
            else:
                detail = next((line.strip() for line in pr_result.stderr.splitlines() if line.strip()), "GitHub CLI is unavailable for this repository.")
                pull_request_source = {"available": False, "kind": "github-cli", "message": detail[:240]}

    prs_by_branch: dict[str, list[dict[str, Any]]] = {}
    for pull_request in pull_requests:
        prs_by_branch.setdefault(pull_request["headBranch"], []).append(pull_request)
    for branch in branches:
        matches = prs_by_branch.get(branch["name"], [])
        if matches:
            pull_request = matches[0]
            branch["pullRequestNumber"] = pull_request["number"]
            branch["status"] = pull_request["status"]

    return {
        "available": True,
        "root": str(repository_root),
        "currentBranch": current_branch,
        "defaultBranch": default_branch,
        "dirtyPaths": dirty_paths,
        "branches": branches,
        "pullRequests": pull_requests,
        "pullRequestSource": pull_request_source,
        "message": "Live local Git branch evidence.",
    }


def build_uninitialized_dashboard_data(
    product_root: Path,
    diagnostics: list[dict[str, str]],
    projection_kind: str,
    projection_source: str,
    repository_root: Path,
) -> dict[str, Any]:
    """Return an honest empty delivery view backed only by this project."""
    now = datetime.now(timezone.utc).isoformat()
    error_count = sum(item["severity"] == "error" for item in diagnostics)
    warning_count = sum(item["severity"] == "warning" for item in diagnostics)
    return {
        "schemaVersion": 3,
        "projection": {"kind": projection_kind, "generatedAt": now, "source": projection_source, "staleAfterMinutes": 0},
        "dataHealth": {
            "status": "INVALID" if error_count else ("WARNING" if warning_count else "VALID"),
            "errors": error_count,
            "warnings": warning_count,
            "diagnostics": diagnostics,
        },
        "initiative": {
            "id": "UNKNOWN",
            "name": product_root.name,
            "shortName": product_root.name,
            "phase": "NOT_INITIALIZED",
            "health": "UNKNOWN",
            "progress": 0,
            "objective": "Canonical Meta PDS artifacts have not been initialized for this project.",
            "humanOwner": "Unassigned",
            "currentRevision": 0,
            "nextAction": {
                "title": "Initialize Meta PDS artifacts",
                "detail": "Create the canonical initiative, decision log, and delivery state when their lifecycle begins.",
                "owner": "Product Manager",
                "impact": "Enables delivery planning views without substituting sample data.",
            },
        },
        "decisionMeta": {
            "interactionMode": "EXPLORE",
            "types": [{"id": key, **value} for key, value in DECISION_TYPES.items()],
            "phases": [],
            "pendingKeys": [],
            "canonicalCount": 0,
            "reviewCount": 0,
            "contradictionCount": 0,
        },
        "attention": [],
        "prototype": {
            "id": "No active prototype",
            "name": "Prototype not active",
            "description": "No canonical prototype checkpoint is available for this project.",
            "status": "NOT_ACTIVE",
            "checkpoint": "—",
            "checkpointAt": now,
            "route": "—",
            "persistence": "—",
            "seedProfiles": 0,
            "journeys": {"reviewed": 0, "total": 0},
            "assumptionsTested": 0,
            "openQuestions": 0,
            "manualReview": "Not requested",
        },
        "decisions": [],
        "slices": [],
        "stories": [],
        "workPackages": [],
        "contracts": [],
        "testCases": [],
        "activity": [],
        "repository": build_repository_data(repository_root),
    }


def build_dashboard_data(
    product_root: Path,
    projection_kind: str = "live-project",
    projection_source: str = "Live project evidence",
    repository_root: Path | None = None,
) -> dict[str, Any]:
    product_root = product_root.resolve()
    base = product_root / "docs" / "meta-pds"
    diagnostics = validate_product_artifacts(product_root)
    resolved_repository_root = (repository_root or product_root).resolve()
    if not (base / "initiative.md").is_file() or not (base / "delivery-state.yaml").is_file():
        return build_uninitialized_dashboard_data(
            product_root,
            diagnostics,
            projection_kind,
            projection_source,
            resolved_repository_root,
        )
    initiative_meta, initiative_body = read_markdown(base / "initiative.md")
    delivery = read_yaml(base / "delivery-state.yaml", required=True)
    try:
        decisions_doc = read_yaml(base / "decision-log.yaml")
    except (ArtifactError, OSError):
        decisions_doc = {}
    if initiative_meta.get("schema_version") != 2:
        raise ArtifactError("initiative.md uses an unsupported schema_version")
    if delivery.get("schema_version") not in {2, 3}:
        raise ArtifactError("delivery-state.yaml uses an unsupported schema_version")
    decision_schema = decisions_doc.get("schema_version")
    if decision_schema is not None and decision_schema not in {2, 3}:
        decisions_doc = {}
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
        parsed_tests: list[dict[str, Any]] = []
        expected_contracts: list[dict[str, Any]] = []
        slice_artifact_valid = False
        if path:
            try:
                candidate_meta, candidate_body = read_markdown(path)
                if candidate_meta.get("schema_version") == 2 and str(candidate_meta.get("slice_id") or path.stem) == path.stem:
                    meta, body = candidate_meta, candidate_body
                    slice_artifact_valid = True
                    parsed_stories = parse_stories(body)
                    parsed_tests = parse_test_cases(body)
                    expected_contracts = parse_contract_table(body)
            except (ArtifactError, OSError):
                pass

        execution = executions.get(slice_id, {}) if slice_artifact_valid else {}
        report_test_results = reports.get(slice_id, {}).get("test_results", {}) if slice_artifact_valid else {}
        raw_tests = []
        for item in parsed_tests:
            if not isinstance(item, dict):
                continue
            test = dict(item)
            report_result = report_test_results.get(str(test.get("id")), {})
            if report_result:
                test["status"] = result_status(report_result.get("Result"), test.get("status") or "READY")
                test["evidence"] = report_result.get("Report/evidence") or test.get("evidence") or ""
                test["command"] = report_result.get("Command") or test.get("command") or ""
            raw_tests.append(test)
        tests_by_id = {str(item.get("id")): item for item in raw_tests if item.get("id")}
        wave_by_package: dict[str, str] = {}
        for wave in list_value(execution.get("execution_waves")):
            if not isinstance(wave, dict):
                continue
            for package_id in list_value(wave.get("work_packages")):
                wave_by_package[str(package_id)] = str(wave.get("id") or "")
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
                "wave": wave_by_package.get(str(item["id"]), ""),
                "contractVersion": str(item.get("contract_version") or execution.get("contract_version") or ""),
                "storyIds": [str(value) for value in list_value(item.get("supports"))],
                "dependsOn": [str(value) for value in list_value(item.get("depends_on"))],
                "inputs": [str(value) for value in list_value(item.get("inputs"))],
                "produces": [str(value) for value in list_value(item.get("produces"))],
                "ownedPaths": [str(value) for value in list_value(item.get("owned_paths"))],
                "forbiddenPaths": [str(value) for value in list_value(item.get("forbidden_paths"))],
                "entryChecks": [str(value) for value in list_value(item.get("entry_checks"))],
                "exitChecks": [str(value) for value in list_value(item.get("exit_checks"))],
                "requiredTestIds": required_tests,
                "applicableSkills": [str(value) for value in list_value(item.get("applicable_skills"))],
                "integrationOwner": str(item.get("integration_owner") or "Unassigned"),
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
                "testIds": [test["id"] for test in raw_tests if story["id"] in test.get("supports", [])],
            })

        raw_contracts = [item for item in list_value(execution.get("integration_contracts")) if isinstance(item, dict)]
        expected_by_name = {str(item.get("name", "")).strip().lower(): item for item in expected_contracts}
        selected_contracts = raw_contracts or expected_contracts
        for contract in selected_contracts:
            expected = expected_by_name.get(str(contract.get("name", "")).strip().lower(), {})
            path_value = str(contract.get("path") or "")
            contracts.append({
                "id": str(contract.get("id") or f"CON-{slice_id}-{len(contracts) + 1}"),
                "sliceId": slice_id,
                "name": str(contract.get("name") or "Unnamed contract"),
                "type": str(contract.get("type") or "Contract"),
                "version": str(contract.get("version") or "Unspecified"),
                "status": status(contract.get("status"), "EXPECTED"),
                "owner": str(contract.get("owner") or "Unassigned"),
                "path": path_value,
                "description": str(contract.get("description") or expected.get("description") or ""),
                "markdown": contract_markdown(product_root, path_value),
            })

        for test in raw_tests:
            test_cases.append({
                "id": str(test.get("id") or f"TC-{slice_id}-{len(test_cases) + 1}"),
                "sliceId": slice_id,
                "title": str(test.get("title") or test.get("id") or "Unnamed test"),
                "type": str(test.get("type") or "CLI"),
                "level": str(test.get("level") or "SLICE"),
                "status": status(test.get("status"), "READY"),
                "owner": str(test.get("owner") or "Unassigned"),
                "expected": str(test.get("expected") or ""),
                "command": str(test.get("command") or ""),
                "evidence": str(test.get("evidence") or ""),
                "supports": [str(value) for value in list_value(test.get("supports"))],
                "validatesContracts": [str(value) for value in list_value(test.get("validatesContracts"))],
            })

        title = str(meta.get("title") or row.get("Slice") or (first_heading(body) if body else slice_id))
        outcome = normalized_paragraph(markdown_section(body, "Capability outcome")) if body else str(row.get("Capability outcome") or "")
        dependencies = list_value(meta.get("dependencies")) or [value.strip() for value in str(row.get("Dependencies") or "").split(",") if value.strip() and value.strip().lower() != "none"]
        slices.append({
            "id": slice_id,
            "order": safe_int(meta.get("order") or row.get("Order"), fallback_order),
            "title": title,
            "outcome": outcome,
            "status": current_status,
            "progress": slice_progress(current_status, parsed_packages),
            "revision": safe_int(meta.get("slice_revision"), 0),
            "priority": str(meta.get("priority") or row.get("Priority") or "—"),
            "dependencies": [str(value) for value in dependencies],
            "stories": len(parsed_stories),
            "active": slice_id in {delivery.get("active_planning_slice"), delivery.get("active_execution_slice")},
            "artifactPath": relative_path(path, product_root) if path else "",
        })

    slices.sort(key=lambda item: (item["order"], item["id"]))

    raw_decisions = [item for item in list_value(decisions_doc.get("decisions")) if isinstance(item, dict)]
    decision_by_key: dict[str, dict[str, Any]] = {}
    explicit_contradictions: dict[str, set[str]] = {}
    superseded_keys: set[str] = set()
    for item in raw_decisions:
        decision_id = str(item.get("id") or "DEC-UNKNOWN")
        decision_key = str(item.get("key") or f"legacy.{decision_id.lower()}")
        decision_by_key[decision_key] = item
        explicit_contradictions[decision_key] = {
            str(value) for value in list_value(item.get("contradicts")) if isinstance(value, str)
        }
        if status(item.get("status")) == "LOCKED" and isinstance(item.get("supersedes"), str) and item.get("supersedes"):
            superseded_keys.add(str(item["supersedes"]))
    for decision_key, references in list(explicit_contradictions.items()):
        for referenced_key in references:
            if referenced_key in explicit_contradictions:
                explicit_contradictions[referenced_key].add(decision_key)

    decisions = []
    for item in raw_decisions:
        if not isinstance(item, dict):
            continue
        decision_id = str(item.get("id") or "DEC-UNKNOWN")
        decision_key = str(item.get("key") or f"legacy.{decision_id.lower()}")
        primary_type = str(item.get("type") or "FEATURE_CAPABILITY")
        type_meta = DECISION_TYPES.get(primary_type, DECISION_TYPES["FEATURE_CAPABILITY"])
        current_status = status(item.get("status"), "PROPOSED")
        contradictions = []
        locked_contradiction = False
        for referenced_key in sorted(explicit_contradictions.get(decision_key, set())):
            referenced = decision_by_key.get(referenced_key)
            if not referenced:
                continue
            referenced_type = str(referenced.get("type") or "FEATURE_CAPABILITY")
            referenced_status = status(referenced.get("status"), "PROPOSED")
            locked_contradiction = locked_contradiction or referenced_status == "LOCKED"
            contradictions.append({
                "key": referenced_key,
                "title": str(referenced.get("question") or referenced.get("decision") or referenced_key),
                "status": referenced_status,
                "typeLabel": DECISION_TYPES.get(referenced_type, DECISION_TYPES["FEATURE_CAPABILITY"])["label"],
            })
        canonical = current_status == "LOCKED" and decision_key not in superseded_keys and not locked_contradiction
        secondary_types = []
        for secondary_type in list_value(item.get("secondary_types")):
            if isinstance(secondary_type, str) and secondary_type in DECISION_TYPES:
                secondary_types.append({"id": secondary_type, "label": DECISION_TYPES[secondary_type]["label"]})
        decisions.append({
            "id": decision_id,
            "key": decision_key,
            "title": str(item.get("question") or item.get("decision") or "Decision"),
            "summary": str(item.get("decision") or item.get("rationale") or ""),
            "rationale": str(item.get("rationale") or ""),
            "status": current_status,
            "revision": safe_int(item.get("revision"), 1),
            "updatedAt": str(item.get("decided_at") or delivery.get("last_verified_at") or datetime.now(timezone.utc).isoformat()),
            "type": primary_type,
            "typeLabel": type_meta["label"],
            "layer": type_meta["layer"],
            "layerKey": type_meta["layerKey"],
            "typeOrder": type_meta["order"],
            "secondaryTypes": secondary_types,
            "phases": [str(value) for value in list_value(item.get("phases"))] or ["GLOBAL"],
            "dependsOn": [str(value) for value in list_value(item.get("depends_on"))],
            "contradictions": contradictions,
            "hasContradiction": bool(contradictions),
            "lockedContradiction": locked_contradiction,
            "canonical": canonical,
            "needsReview": current_status in {"PROPOSED", "TESTING"} or bool(contradictions),
            "affects": [str(value) for value in list_value(item.get("affected_artifacts"))],
            "authority": str(item.get("authority") or "PM"),
            "approvedBy": str(item.get("approved_by") or ""),
            "supersedes": str(item.get("supersedes") or ""),
        })
    decisions.sort(key=lambda item: (item["typeOrder"], item["key"]))

    phase_values = {phase for decision in decisions for phase in decision["phases"]}
    phases = sorted(
        phase_values,
        key=lambda phase: (0, 0) if phase == "GLOBAL" else (1, safe_int(str(phase).removeprefix("PHASE-"), 0)),
    )
    initiative_status = status(delivery.get("initiative_status"), "UNKNOWN")
    fallback_modes = {
        "DISCOVERING": "EXPLORE",
        "INITIATIVE_REVIEW": "DECISION_REVIEW",
        "PROTOTYPING": "PROTOTYPE",
        "INITIATIVE_READY": "SLICE_SHAPING",
    }
    interaction_mode = status(delivery.get("interaction_mode"), fallback_modes.get(initiative_status, "DELIVERY"))
    if interaction_mode not in ALLOWED_INTERACTION_MODES:
        interaction_mode = "EXPLORE"
    decision_review = delivery.get("decision_review") if isinstance(delivery.get("decision_review"), dict) else {}
    decision_meta = {
        "interactionMode": interaction_mode,
        "types": [{"id": key, **value} for key, value in DECISION_TYPES.items()],
        "phases": phases,
        "pendingKeys": [str(value) for value in list_value(decision_review.get("pending_keys"))],
        "canonicalCount": sum(decision["canonical"] for decision in decisions),
        "reviewCount": sum(decision["needsReview"] for decision in decisions),
        "contradictionCount": sum(decision["hasContradiction"] for decision in decisions),
    }

    attention = []
    human_decision = delivery.get("human_decision_required")
    if human_decision:
        if isinstance(human_decision, str):
            detail = human_decision
        elif isinstance(human_decision, dict):
            detail = human_decision.get("question") or human_decision.get("detail") or "Human decision required"
        else:
            detail = str(human_decision)
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
            if not isinstance(item, dict):
                continue
            events.append({
                "at": item.get("at") or item.get("timestamp") or datetime.now(timezone.utc).isoformat(),
                "title": item.get("title") or item.get("event") or "Delivery event",
                "detail": item.get("detail") or "",
                "kind": item.get("kind") or "updated",
            })
    events.sort(key=lambda item: str(item["at"]), reverse=True)

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
    error_count = sum(item["severity"] == "error" for item in diagnostics)
    warning_count = sum(item["severity"] == "warning" for item in diagnostics)
    return {
        "schemaVersion": 3,
        "projection": {"kind": projection_kind, "generatedAt": now, "source": projection_source, "staleAfterMinutes": 0},
        "dataHealth": {
            "status": "INVALID" if error_count else ("WARNING" if warning_count else "VALID"),
            "errors": error_count,
            "warnings": warning_count,
            "diagnostics": diagnostics,
        },
        "initiative": {
            "id": str(initiative_meta.get("initiative_id") or delivery.get("initiative_id") or "UNKNOWN"),
            "name": initiative_title,
            "shortName": initiative_title,
            "phase": initiative_status,
            "health": status(delivery.get("health"), "UNKNOWN"),
            "progress": round(sum(item["progress"] for item in slices) / len(slices)) if slices else 0,
            "objective": objective,
            "humanOwner": str(initiative_meta.get("human_owner") or "Human Product Owner"),
            "currentRevision": safe_int(delivery.get("initiative_revision") or initiative_meta.get("revision"), 1),
            "nextAction": next_action_record,
        },
        "decisionMeta": decision_meta,
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
            "seedProfiles": safe_int(prototype.get("seed_profiles"), 0),
            "journeys": {"reviewed": safe_int(prototype.get("journeys_reviewed"), 0), "total": safe_int(prototype.get("journeys_total"), 0)},
            "assumptionsTested": safe_int(prototype.get("assumptions_tested"), 0),
            "openQuestions": safe_int(prototype.get("open_questions"), 0),
            "manualReview": str(prototype.get("manual_review") or "Not requested"),
        },
        "decisions": decisions,
        "slices": slices,
        "stories": stories,
        "workPackages": work_packages,
        "contracts": contracts,
        "testCases": test_cases,
        "activity": events,
        "repository": build_repository_data(resolved_repository_root),
    }


def handler_for(
    product_root: Path,
    asset_root: Path,
    projection_kind: str = "live-project",
    projection_source: str = "Live project evidence",
    runtime_project_root: Path | None = None,
):
    runtime_project_root = (runtime_project_root or product_root).resolve()

    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            request = urlparse(self.path)
            path = request.path
            demo_requested = parse_qs(request.query).get("demo") == ["1"]
            if path == "/api/runtime":
                payload = json.dumps({
                    "service": RUNTIME_SERVICE,
                    "runtimeVersion": RUNTIME_VERSION,
                    "projectRoot": str(runtime_project_root),
                    "projectionKind": projection_kind,
                    "pid": os.getpid(),
                }).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return

            if path == "/api/dashboard":
                try:
                    if demo_requested:
                        dashboard_data = build_demo_dashboard_data(asset_root.parent.parent, runtime_project_root)
                    else:
                        dashboard_data = build_dashboard_data(product_root, projection_kind, projection_source, runtime_project_root)
                    payload = json.dumps(
                        dashboard_data,
                        ensure_ascii=False,
                    ).encode("utf-8")
                    self.send_response(200)
                except Exception as error:  # keep local dashboard failures observable
                    try:
                        diagnostics = validate_product_artifacts(product_root)
                    except Exception:
                        diagnostics = []
                    payload = json.dumps({"error": str(error), "diagnostics": diagnostics}).encode("utf-8")
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


def dashboard_url(host: str, port: int) -> str:
    rendered_host = f"[{host}]" if ":" in host and not host.startswith("[") else host
    return f"http://{rendered_host}:{port}"


def dashboard_runtime_paths(project_root: Path) -> tuple[Path, Path, Path]:
    runtime_root = Path(tempfile.gettempdir()) / "meta-pds-dashboard"
    runtime_root.mkdir(parents=True, mode=0o700, exist_ok=True)
    try:
        runtime_root.chmod(0o700)
    except OSError:
        pass
    project_key = hashlib.sha256(str(project_root.resolve()).encode("utf-8")).hexdigest()[:20]
    return (
        runtime_root / f"{project_key}.json",
        runtime_root / ".launch.lock",
        runtime_root / f"{project_key}.log",
    )


@contextmanager
def dashboard_launch_lock(lock_path: Path):
    """Serialize dashboard discovery and launch across concurrent invocations."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+b")
    if handle.tell() == 0:
        handle.write(b"0")
        handle.flush()
    handle.seek(0)
    try:
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def read_runtime_registry(registry_path: Path) -> dict[str, Any]:
    try:
        value = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def write_runtime_registry(registry_path: Path, record: dict[str, Any]) -> None:
    temporary_path = registry_path.with_name(f".{registry_path.name}.{os.getpid()}.tmp")
    temporary_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    try:
        temporary_path.chmod(0o600)
    except OSError:
        pass
    temporary_path.replace(registry_path)


def probe_dashboard_runtime(url: str, timeout: float = 0.5) -> dict[str, Any]:
    parsed = urlparse(url)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
        or not parsed.port
    ):
        return {}
    connection = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=timeout)
    try:
        connection.request("GET", "/api/runtime")
        response = connection.getresponse()
        if response.status != 200:
            return {}
        value = json.loads(response.read().decode("utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError, http.client.HTTPException):
        return {}
    finally:
        connection.close()


def runtime_identity_matches(runtime: dict[str, Any], project_root: Path) -> bool:
    return (
        runtime.get("service") == RUNTIME_SERVICE
        and runtime.get("projectRoot") == str(project_root.resolve())
    )


def runtime_matches(runtime: dict[str, Any], project_root: Path, projection_kind: str) -> bool:
    return (
        runtime_identity_matches(runtime, project_root)
        and runtime.get("runtimeVersion") == RUNTIME_VERSION
        and runtime.get("projectionKind") == projection_kind
    )


def stop_dashboard_runtime(url: str, runtime: dict[str, Any], timeout: float = 5.0) -> None:
    """Stop an exact, locally identified project runtime before replacing it."""
    pid = runtime.get("pid")
    if not isinstance(pid, int) or pid == os.getpid():
        raise RuntimeError(f"cannot replace dashboard runtime without a valid child PID: {url}")
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not probe_dashboard_runtime(url):
            return
        time.sleep(0.05)
    raise RuntimeError(f"existing dashboard runtime did not stop: {url}")


def port_is_available(host: str, port: int) -> bool:
    if port == 0:
        return True
    family = socket.AF_INET6 if ":" in host else socket.AF_INET
    try:
        with socket.socket(family, socket.SOCK_STREAM) as candidate:
            candidate.bind((host, port))
    except OSError:
        return False
    return True


def ensure_dashboard(
    project_root: Path,
    skill_root: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    startup_timeout: float = 10.0,
) -> dict[str, Any]:
    """Start one dashboard for a project or reuse its healthy existing runtime."""
    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise RuntimeError(f"project root does not exist: {project_root}")
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("managed dashboards must bind to a loopback host")
    registry_path, lock_path, log_path = dashboard_runtime_paths(project_root)
    expected_projection_kind = "live-project"

    with dashboard_launch_lock(lock_path):
        registry = read_runtime_registry(registry_path)
        registered_url = str(registry.get("url") or "")
        registered_runtime = probe_dashboard_runtime(registered_url) if registered_url else {}
        if runtime_matches(registered_runtime, project_root, expected_projection_kind):
            return {**registry, "status": "reused", "runtime": registered_runtime}
        if runtime_identity_matches(registered_runtime, project_root):
            stop_dashboard_runtime(registered_url, registered_runtime)

        if registry_path.exists():
            registry_path.unlink()

        requested_url = dashboard_url(host, port) if port else ""
        requested_runtime = probe_dashboard_runtime(requested_url) if requested_url else {}
        if runtime_matches(requested_runtime, project_root, expected_projection_kind):
            record = {
                "service": RUNTIME_SERVICE,
                "runtimeVersion": RUNTIME_VERSION,
                "projectRoot": str(project_root),
                "url": requested_url,
                "pid": requested_runtime.get("pid"),
                "projectionKind": requested_runtime.get("projectionKind"),
            }
            write_runtime_registry(registry_path, record)
            return {**record, "status": "reused", "runtime": requested_runtime}
        if runtime_identity_matches(requested_runtime, project_root):
            stop_dashboard_runtime(requested_url, requested_runtime)

        selected_port = port if port_is_available(host, port) else 0
        command = [sys.executable, str(Path(__file__).resolve()), str(project_root)]
        command.extend([
            "--host", host,
            "--port", str(selected_port),
            "--registry-path", str(registry_path),
        ])

        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("ab") as log_handle:
            process_options: dict[str, Any] = {
                "stdin": subprocess.DEVNULL,
                "stdout": log_handle,
                "stderr": subprocess.STDOUT,
                "cwd": str(project_root),
            }
            if os.name == "nt":
                process_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            else:
                process_options["start_new_session"] = True
            process = subprocess.Popen(command, **process_options)

        deadline = time.monotonic() + startup_timeout
        while time.monotonic() < deadline:
            if process.poll() is not None:
                detail = log_path.read_text(encoding="utf-8", errors="replace")[-2000:] if log_path.exists() else ""
                raise RuntimeError(f"dashboard failed to start (exit {process.returncode}): {detail.strip()}")
            registry = read_runtime_registry(registry_path)
            runtime_url = str(registry.get("url") or "")
            runtime = probe_dashboard_runtime(runtime_url) if runtime_url else {}
            if runtime_matches(runtime, project_root, expected_projection_kind):
                return {**registry, "status": "started", "runtime": runtime, "process": process}
            time.sleep(0.05)

        process.terminate()
        raise RuntimeError(f"dashboard did not become ready within {startup_timeout:g} seconds; log: {log_path}")


def prepare_projection_fixture(skill_root: Path) -> tempfile.TemporaryDirectory[str]:
    """Build complete canonical artifacts for parser regression tests only."""
    runtime = tempfile.TemporaryDirectory(prefix="meta-pds-projection-fixture-")
    base = Path(runtime.name) / "docs" / "meta-pds"
    (base / "slices").mkdir(parents=True)
    (base / "execution").mkdir(parents=True)

    initiative = (skill_root / "assets" / "initiative-template.md").read_text(encoding="utf-8")
    initiative = initiative.replace("INIT-0001", "INIT-0042").replace('title: ""', 'title: "Learning Platform V1"')
    initiative = initiative.replace("revision: 1", "revision: 3", 1)
    (base / "initiative.md").write_text(initiative, encoding="utf-8")

    delivery = (skill_root / "assets" / "delivery-state-template.yaml").read_text(encoding="utf-8")
    delivery = delivery.replace("INIT-0001", "INIT-0042").replace("initiative_status: DISCOVERING", "initiative_status: EXECUTING")
    delivery = delivery.replace("initiative_revision: 1", "initiative_revision: 3")
    delivery = delivery.replace("interaction_mode: EXPLORE", "interaction_mode: DELIVERY")
    delivery = delivery.replace(
        "decision_review:\n  pending_keys: []\n  last_checkpoint_at: \"\"",
        "decision_review:\n  pending_keys: [release.auth.feature-flag, operations.auth-events, ux.navigation.topbar, storage.document.primary]\n  last_checkpoint_at: \"2026-08-22T00:20:00+05:00\"",
    )
    delivery = delivery.replace("health: UNKNOWN", "health: ON_TRACK").replace("active_execution_slice: null", "active_execution_slice: SLICE-AUTH-001")
    delivery = delivery.replace(
        "slice_states: []",
        "slice_states:\n  - slice_id: SLICE-AUTH-001\n    status: IN_PROGRESS\n    current_gate: EXECUTION_READY\n    updated_at: \"2026-08-22T00:30:00+05:00\"",
    )
    delivery = delivery.replace('title: ""', 'title: "Complete active Authentication work packages"')
    delivery = delivery.replace('detail: ""', 'detail: "Backend and frontend packages are active; integration remains dependency-blocked."')
    delivery = delivery.replace('impact: ""', 'impact: "Unblocks complete lifecycle integration and Playwright CLI verification."')
    (base / "delivery-state.yaml").write_text(delivery, encoding="utf-8")

    decisions = (skill_root / "assets" / "decision-log-example.yaml").read_text(encoding="utf-8")
    (base / "decision-log.yaml").write_text(decisions, encoding="utf-8")

    demo_events = [
        {
            "at": "2026-08-22T00:42:00+05:00",
            "kind": "blocked",
            "title": "Full-stack integration is blocked",
            "detail": "WP-AUTH-06 is waiting for persistence, backend, frontend, and email-adapter exit checks.",
        },
        {
            "at": "2026-08-22T00:36:00+05:00",
            "kind": "verifying",
            "title": "Transactional email adapter entered verification",
            "detail": "Integration Engineer submitted WP-AUTH-05 evidence against CON-AUTH-EMAIL v1.",
        },
        {
            "at": "2026-08-22T00:30:00+05:00",
            "kind": "started",
            "title": "Frontend authentication journeys started",
            "detail": "Frontend Engineer started WP-AUTH-04 using the locked API contract and approved prototype checkpoint 07.",
        },
        {
            "at": "2026-08-22T00:24:00+05:00",
            "kind": "started",
            "title": "Authentication lifecycle API started",
            "detail": "Backend Engineer started WP-AUTH-03 after the persistence interfaces became available for integration.",
        },
        {
            "at": "2026-08-22T00:18:00+05:00",
            "kind": "verifying",
            "title": "Authentication persistence entered verification",
            "detail": "Database Engineer submitted WP-AUTH-02 migration, rollback, repository, and concurrency evidence.",
        },
        {
            "at": "2026-08-22T00:05:00+05:00",
            "kind": "completed",
            "title": "Authentication contracts and threat boundaries locked",
            "detail": "WP-AUTH-01 completed; API, session, data, and email-adapter boundaries are versioned as auth-v1.",
        },
        {
            "at": "2026-08-21T23:52:00+05:00",
            "kind": "assigned",
            "title": "Authentication work packages assigned",
            "detail": "Seven bounded packages were assigned across development lead, database, backend, frontend, and integration owners.",
        },
        {
            "at": "2026-08-21T23:40:00+05:00",
            "kind": "approved",
            "title": "Authentication slice approved for development",
            "detail": "Human Product Owner approved SLICE-AUTH-001 revision 1 after planning readiness and dependency validation passed.",
        },
        {
            "at": "2026-08-21T23:15:00+05:00",
            "kind": "approved",
            "title": "Prototype checkpoint 07 approved",
            "detail": "Human manual review accepted registration, sign-in, recovery, session restoration, and sign-out behavior.",
        },
    ]
    (base / "delivery-events.jsonl").write_text(
        "\n".join(json.dumps(event, separators=(",", ":")) for event in demo_events) + "\n",
        encoding="utf-8",
    )

    slice_example = skill_root.parent / "slice-planning" / "assets" / "authentication-slice-example.md"
    (base / "slices" / "SLICE-AUTH-001.md").write_text(slice_example.read_text(encoding="utf-8"), encoding="utf-8")
    execution_example = skill_root.parent / "slice-development" / "assets" / "authentication-execution-example.yaml"
    (base / "execution" / "SLICE-AUTH-001.yaml").write_text(execution_example.read_text(encoding="utf-8"), encoding="utf-8")
    return runtime


def build_demo_dashboard_data(skill_root: Path, repository_root: Path) -> dict[str, Any]:
    """Project the bundled fixture explicitly without touching product artifacts."""
    fixture = prepare_projection_fixture(skill_root)
    try:
        return build_dashboard_data(
            Path(fixture.name),
            projection_kind="demo-fixture",
            projection_source="Bundled demo delivery data · repository evidence remains live",
            repository_root=repository_root,
        )
    finally:
        fixture.cleanup()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("product_root", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--ensure", action="store_true", help="Start or reuse one background dashboard for this project, then exit")
    parser.add_argument("--print-json", action="store_true", help="Print one in-memory projection and exit")
    parser.add_argument("--registry-path", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.ensure and args.print_json:
        parser.error("--ensure and --print-json are mutually exclusive")

    skill_root = Path(__file__).resolve().parent.parent
    if args.ensure:
        result = ensure_dashboard(args.product_root, skill_root, args.host, args.port)
        print(f"Meta PDS dashboard: {result['url']}")
        print(f"Meta PDS demo: {result['url']}/?demo=1#decisions")
        print(f"Dashboard runtime: {result['status']} for {result['projectRoot']}")
        base = args.product_root.resolve() / "docs" / "meta-pds"
        if not (base / "initiative.md").is_file() or not (base / "delivery-state.yaml").is_file():
            print("Canonical Meta PDS artifacts are not initialized; showing only live project evidence and missing-artifact diagnostics.")
        return 0

    product_root = args.product_root.resolve()
    runtime_project_root = product_root
    projection_kind = "live-project"
    projection_source = "Live project evidence"
    if args.print_json:
        print(json.dumps(build_dashboard_data(product_root, projection_kind, projection_source), indent=2, ensure_ascii=False))
        return 0

    asset_root = skill_root / "assets" / "dashboard"
    server = ThreadingHTTPServer(
        (args.host, args.port),
        handler_for(product_root, asset_root, projection_kind, projection_source, runtime_project_root),
    )
    url = dashboard_url(args.host, server.server_port)
    registry_record = {
        "service": RUNTIME_SERVICE,
        "runtimeVersion": RUNTIME_VERSION,
        "projectRoot": str(runtime_project_root),
        "url": url,
        "pid": os.getpid(),
        "projectionKind": projection_kind,
        "startedAt": datetime.now(timezone.utc).isoformat(),
    }
    if args.registry_path:
        write_runtime_registry(args.registry_path, registry_record)

    def stop_server(_signum, _frame):
        raise KeyboardInterrupt

    previous_sigterm = signal.signal(signal.SIGTERM, stop_server)
    print(f"Meta PDS dashboard: {url}", flush=True)
    print(f"Reading live project evidence from: {product_root}", flush=True)
    print("Refresh the page to reparse current files. Press Ctrl-C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        signal.signal(signal.SIGTERM, previous_sigterm)
        if args.registry_path:
            current_registry = read_runtime_registry(args.registry_path)
            if current_registry.get("pid") == os.getpid():
                args.registry_path.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
