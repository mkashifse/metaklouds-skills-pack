#!/usr/bin/env python3
"""Validate Meta PDS artifact structure and execution-plan dependencies."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from serve_dashboard import ArtifactError, markdown_section, parse_stories, parse_table, parse_test_cases, read_markdown, read_yaml


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

REQUIRED_SLICE_METADATA = {
    "schema_version",
    "initiative_id",
    "initiative_revision",
    "slice_id",
    "title",
    "slice_revision",
    "status",
    "order",
    "priority",
    "dependencies",
}


def top_level_keys(text: str) -> set[str]:
    return {
        match.group(1)
        for match in re.finditer(r"^([a-zA-Z_][a-zA-Z0-9_-]*):(?:\s|$)", text, re.MULTILINE)
    }

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


def check_execution_plan(
    path: Path,
    errors: list[str],
    story_ids: set[str] | None = None,
    test_ids: set[str] | None = None,
):
    if not path.exists():
        errors.append(f"missing execution plan: {path}")
        return
    text = path.read_text()
    check_required(
        top_level_keys(text),
        ["schema_version", "slice_id", "slice_revision", "contract_version", "status", "integration_contracts", "work_packages"],
        path,
        errors,
    )
    try:
        document = read_yaml(path)
    except (ArtifactError, OSError) as error:
        errors.append(f"{path}: {error}")
        return
    if document.get("schema_version") != 2:
        errors.append(f"{path}: schema_version must be 2")
    packages = document.get("work_packages")
    if not isinstance(packages, list):
        packages = []
    if not packages:
        errors.append(f"{path}: work_packages must be a non-empty list")
        return

    test_ids = test_ids or set()

    contracts = document.get("integration_contracts")
    if not isinstance(contracts, list):
        errors.append(f"{path}: integration_contracts must be a list")
        contracts = []
    contract_ids: set[str] = set()
    for index, contract in enumerate(contracts):
        label = f"{path}: integration_contracts[{index}]"
        if not isinstance(contract, dict):
            errors.append(f"{label} must be a mapping")
            continue
        for field in ["id", "name", "type", "version", "status", "owner", "path"]:
            if field not in contract:
                errors.append(f"{label} missing '{field}'")
            elif contract.get(field) in {None, ""}:
                errors.append(f"{label}.{field} must not be empty")
        contract_id = contract.get("id")
        if not isinstance(contract_id, str) or not contract_id:
            errors.append(f"{label} has invalid id")
        elif contract_id in contract_ids:
            errors.append(f"{path}: duplicate contract id '{contract_id}'")
        else:
            contract_ids.add(contract_id)

    by_id: dict[str, dict] = {}
    for index, package in enumerate(packages):
        label = f"{path}: work_packages[{index}]"
        if not isinstance(package, dict):
            errors.append(f"{label} must be a mapping")
            continue
        for field in ["id", "title", "description", "area", "owner", "status", "depends_on", "supports", "required_tests"]:
            if field not in package:
                errors.append(f"{label} missing '{field}'")
        for field in ["id", "title", "description", "area", "owner", "status"]:
            if package.get(field) in {None, ""}:
                errors.append(f"{label}.{field} must not be empty")
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
        if story_ids is not None and isinstance(package.get("supports"), list):
            for story_id in package["supports"]:
                if story_id not in story_ids:
                    errors.append(f"{label}.supports references unknown '{story_id}'")
        for test_id in package.get("required_tests", []) if isinstance(package.get("required_tests"), list) else []:
            if test_id not in test_ids:
                errors.append(f"{label}.required_tests references unknown '{test_id}'")

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


def check_parseable_initiative(path: Path, errors: list[str]):
    try:
        metadata, _ = read_markdown(path)
    except (ArtifactError, OSError) as error:
        errors.append(f"{path}: {error}")
        return
    for field in ["schema_version", "initiative_id", "title", "revision", "status"]:
        if field not in metadata:
            errors.append(f"{path}: frontmatter missing '{field}'")
        elif metadata.get(field) in {None, ""}:
            errors.append(f"{path}: frontmatter '{field}' must not be empty")
    if metadata.get("schema_version") != 2:
        errors.append(f"{path}: schema_version must be 2")


def check_parseable_slice(path: Path, errors: list[str]) -> tuple[set[str], set[str]]:
    try:
        metadata, body = read_markdown(path)
    except (ArtifactError, OSError) as error:
        errors.append(f"{path}: {error}")
        return set(), set()
    for field in sorted(REQUIRED_SLICE_METADATA):
        if field not in metadata:
            errors.append(f"{path}: frontmatter missing '{field}'")
    for field in ["initiative_id", "slice_id", "title", "status", "priority"]:
        if metadata.get(field) in {None, ""}:
            errors.append(f"{path}: frontmatter '{field}' must not be empty")
    if metadata.get("schema_version") != 2:
        errors.append(f"{path}: schema_version must be 2")
    if metadata.get("slice_id") != path.stem:
        errors.append(f"{path}: slice_id must match filename")
    if not isinstance(metadata.get("dependencies"), list):
        errors.append(f"{path}: dependencies must be a list")
    stories = parse_stories(body)
    if not stories:
        errors.append(f"{path}: no parseable 'US-* — title' stories")
        return set(), set()
    story_ids: set[str] = set()
    for story in stories:
        if story["id"] in story_ids:
            errors.append(f"{path}: duplicate story id '{story['id']}'")
        story_ids.add(story["id"])
        if not story["acceptanceCriteria"]:
            errors.append(f"{path}: story '{story['id']}' has no parseable acceptance criteria")
    tests = parse_test_cases(body)
    if not tests:
        errors.append(f"{path}: no parseable 'TC-* — title' test cases")
        return story_ids, set()
    test_ids: set[str] = set()
    allowed_levels = {"STORY", "CONTRACT", "CROSS_CUTTING", "SLICE"}
    allowed_statuses = {"PLANNED", "READY", "BLOCKED", "PASSED", "FAILED"}
    for test in tests:
        test_id = test["id"]
        if test_id in test_ids:
            errors.append(f"{path}: duplicate test-case id '{test_id}'")
        test_ids.add(test_id)
        if test["level"] not in allowed_levels:
            errors.append(f"{path}: test '{test_id}' has invalid level '{test['level']}'")
        if test["status"] not in allowed_statuses:
            errors.append(f"{path}: test '{test_id}' has invalid status '{test['status']}'")
        for field in ["title", "type", "owner", "status", "expected"]:
            if not test.get(field):
                errors.append(f"{path}: test '{test_id}' has no {field}")
        if not test["supports"]:
            errors.append(f"{path}: test '{test_id}' supports no stories")
        for story_id in test["supports"]:
            if story_id not in story_ids:
                errors.append(f"{path}: test '{test_id}' references unknown story '{story_id}'")
    return story_ids, test_ids


def check_report(path: Path, test_ids: set[str], errors: list[str]):
    try:
        _, body = read_markdown(path)
    except (ArtifactError, OSError) as error:
        errors.append(f"{path}: {error}")
        return
    seen: set[str] = set()
    for index, row in enumerate(parse_table(markdown_section(body, "CLI test evidence"))):
        test_id = row.get("Test ID", "").strip(" `")
        if not test_id:
            errors.append(f"{path}: CLI evidence row {index + 1} has no Test ID")
        elif test_id in seen:
            errors.append(f"{path}: duplicate Test ID '{test_id}'")
        elif test_id not in test_ids:
            errors.append(f"{path}: unknown Test ID '{test_id}'")
        seen.add(test_id)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product_root", type=Path)
    parser.add_argument("--slice-id")
    parser.add_argument("--require-execution-plan", action="store_true")
    args = parser.parse_args()

    root = args.product_root.resolve()
    base = root / "docs" / "meta-pds"
    errors: list[str] = []

    initiative_path = base / "initiative.md"
    check_markdown(initiative_path, REQUIRED_INITIATIVE_HEADINGS, errors)
    if initiative_path.exists():
        check_parseable_initiative(initiative_path, errors)

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
                "slice_states",
                "blockers",
                "next_recommended_action",
            ],
        ),
    ]:
        if not path.exists():
            errors.append(f"missing artifact: {path}")
            continue
        check_required(top_level_keys(path.read_text()), fields, path, errors)
        try:
            document = read_yaml(path)
            if document.get("schema_version") != 2:
                errors.append(f"{path}: schema_version must be 2")
        except (ArtifactError, OSError) as error:
            errors.append(f"{path}: {error}")

    if args.slice_id:
        slice_path = base / "slices" / f"{args.slice_id}.md"
        check_markdown(slice_path, REQUIRED_SLICE_HEADINGS, errors)
        story_ids: set[str] = set()
        test_ids: set[str] = set()
        if slice_path.exists():
            story_ids, test_ids = check_parseable_slice(slice_path, errors)
        execution_path = base / "execution" / f"{args.slice_id}.yaml"
        if args.require_execution_plan or execution_path.exists():
            check_execution_plan(execution_path, errors, story_ids, test_ids)
        report_path = base / "reports" / f"{args.slice_id}.md"
        if report_path.exists():
            check_report(report_path, test_ids, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Meta PDS artifact validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
