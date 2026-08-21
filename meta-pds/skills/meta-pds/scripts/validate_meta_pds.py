#!/usr/bin/env python3
"""Validate Meta PDS artifact structure and execution-plan dependencies."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


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
    "Security, accessibility, and operations",
    "Contracts and dependencies",
    "Observability, rollout, and rollback",
    "Planning validation",
}

ALLOWED_PACKAGE_STATUSES = {
    "BLOCKED",
    "READY",
    "IN_PROGRESS",
    "VERIFYING",
    "DONE",
    "REWORK_REQUIRED",
    "REVERIFY_REQUIRED",
    "PAUSED",
}


def clean_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def top_level_keys(text: str) -> set[str]:
    return {
        match.group(1)
        for match in re.finditer(r"^([a-zA-Z_][a-zA-Z0-9_-]*):(?:\s|$)", text, re.MULTILINE)
    }


def parse_list_value(block: str, field: str) -> list[str] | None:
    match = re.search(
        rf"^    {re.escape(field)}:\s*(.*?)\s*$", block, re.MULTILINE
    )
    if not match:
        return None
    inline = match.group(1).strip()
    if inline.startswith("[") and inline.endswith("]"):
        body = inline[1:-1].strip()
        if not body:
            return []
        return [clean_scalar(item) for item in body.split(",") if item.strip()]
    if inline:
        return None

    remainder = block[match.end() :]
    items: list[str] = []
    for line in remainder.splitlines():
        if re.match(r"^    [a-zA-Z_]", line):
            break
        item = re.match(r"^      -\s+(.+?)\s*$", line)
        if item:
            items.append(clean_scalar(item.group(1)))
    return items


def parse_work_packages(text: str) -> list[dict[str, object]]:
    start = re.search(r"^work_packages:\s*$", text, re.MULTILINE)
    if not start:
        return []
    section = text[start.end() :]
    end = re.search(r"^[a-zA-Z_][a-zA-Z0-9_-]*:\s*$", section, re.MULTILINE)
    if end:
        section = section[: end.start()]

    starts = list(re.finditer(r"^  - id:\s*(.+?)\s*$", section, re.MULTILINE))
    packages: list[dict[str, object]] = []
    for index, match in enumerate(starts):
        block_end = starts[index + 1].start() if index + 1 < len(starts) else len(section)
        block = section[match.start() : block_end]
        package: dict[str, object] = {"id": clean_scalar(match.group(1))}
        for field in ["owner", "status"]:
            field_match = re.search(
                rf"^    {field}:\s*(.+?)\s*$", block, re.MULTILINE
            )
            if field_match:
                package[field] = clean_scalar(field_match.group(1))
        for field in ["depends_on", "supports", "required_tests"]:
            value = parse_list_value(block, field)
            if value is not None:
                package[field] = value
        packages.append(package)
    return packages


def markdown_headings(text: str) -> set[str]:
    return {
        match.group(1).strip()
        for match in re.finditer(r"^#{1,6}\s+(.+?)\s*$", text, re.MULTILINE)
    }


def check_markdown(path: Path, required: set[str], errors: list[str]):
    if not path.exists():
        errors.append(f"missing artifact: {path}")
        return
    text = path.read_text()
    if "TODO" in text or "[TODO" in text:
        errors.append(f"{path}: contains unfinished TODO text")
    missing = sorted(required - markdown_headings(text))
    if missing:
        errors.append(f"{path}: missing headings: {', '.join(missing)}")


def check_required(keys: set[str], fields: list[str], path: Path, errors: list[str]):
    for field in fields:
        if field not in keys:
            errors.append(f"{path}: missing field '{field}'")


def check_execution_plan(path: Path, errors: list[str]):
    if not path.exists():
        errors.append(f"missing execution plan: {path}")
        return
    text = path.read_text()
    check_required(
        top_level_keys(text),
        ["slice_id", "slice_revision", "contract_version", "status", "work_packages"],
        path,
        errors,
    )
    packages = parse_work_packages(text)
    if not packages:
        errors.append(f"{path}: work_packages must be a non-empty list")
        return

    by_id: dict[str, dict] = {}
    for index, package in enumerate(packages):
        label = f"{path}: work_packages[{index}]"
        for field in ["id", "owner", "status", "depends_on", "supports", "required_tests"]:
            if field not in package:
                errors.append(f"{label} missing '{field}'")
        package_id = package.get("id")
        if not isinstance(package_id, str) or not package_id:
            errors.append(f"{label} has invalid id")
            continue
        if package_id in by_id:
            errors.append(f"{path}: duplicate work-package id '{package_id}'")
        by_id[package_id] = package
        if package.get("status") not in ALLOWED_PACKAGE_STATUSES:
            errors.append(f"{label} has invalid status '{package.get('status')}'")
        for field in ["depends_on", "supports", "required_tests"]:
            if not isinstance(package.get(field), list):
                errors.append(f"{label}.{field} must be a list")

    graph: dict[str, list[str]] = {}
    for package_id, package in by_id.items():
        dependencies = package.get("depends_on", [])
        graph[package_id] = []
        if not isinstance(dependencies, list):
            continue
        for dependency in dependencies:
            if dependency not in by_id:
                errors.append(f"{path}: '{package_id}' depends on unknown '{dependency}'")
            else:
                graph[package_id].append(dependency)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str):
        if node in visiting:
            errors.append(f"{path}: dependency cycle includes '{node}'")
            return
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph.get(node, []):
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product_root", type=Path)
    parser.add_argument("--slice-id")
    parser.add_argument("--require-execution-plan", action="store_true")
    args = parser.parse_args()

    root = args.product_root.resolve()
    base = root / "docs" / "meta-pds"
    errors: list[str] = []

    check_markdown(base / "initiative.md", REQUIRED_INITIATIVE_HEADINGS, errors)

    decisions_path = base / "decision-log.yaml"
    state_path = base / "delivery-state.yaml"
    for path, fields in [
        (decisions_path, ["initiative_id", "schema_version", "decisions"]),
        (
            state_path,
            [
                "schema_version",
                "initiative_id",
                "initiative_status",
                "active_planning_slice",
                "active_execution_slice",
                "blockers",
                "next_recommended_action",
            ],
        ),
    ]:
        if not path.exists():
            errors.append(f"missing artifact: {path}")
            continue
        check_required(top_level_keys(path.read_text()), fields, path, errors)

    if args.slice_id:
        slice_path = base / "slices" / f"{args.slice_id}.md"
        check_markdown(slice_path, REQUIRED_SLICE_HEADINGS, errors)
        execution_path = base / "execution" / f"{args.slice_id}.yaml"
        if args.require_execution_plan or execution_path.exists():
            check_execution_plan(execution_path, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Meta PDS artifact validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
