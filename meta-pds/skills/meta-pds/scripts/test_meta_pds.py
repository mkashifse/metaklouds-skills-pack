#!/usr/bin/env python3
"""Regression tests for the Meta PDS artifact contract and dashboard projection."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.request import urlopen

from serve_dashboard import (
    ArtifactError,
    build_dashboard_data,
    build_repository_data,
    ensure_dashboard,
    parse_table,
    parse_yaml,
    prepare_projection_fixture,
    pull_request_records,
    validate_product_artifacts,
)


SKILL_ROOT = Path(__file__).resolve().parent.parent


class MetaPDSContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = prepare_projection_fixture(SKILL_ROOT)
        self.root = Path(self.runtime.name)
        self.base = self.root / "docs" / "meta-pds"

    def tearDown(self) -> None:
        self.runtime.cleanup()

    def diagnostics(self) -> list[dict]:
        return validate_product_artifacts(self.root)

    def projection(self) -> dict:
        return build_dashboard_data(self.root)

    def test_projection_fixture_is_valid_and_complete(self) -> None:
        projection = self.projection()
        self.assertEqual([], self.diagnostics())
        self.assertEqual("VALID", projection["dataHealth"]["status"])
        self.assertEqual((1, 6, 7, 12, 4), (
            len(projection["slices"]),
            len(projection["stories"]),
            len(projection["workPackages"]),
            len(projection["testCases"]),
            len(projection["contracts"]),
        ))
        self.assertEqual(9, len(projection["activity"]))
        self.assertEqual("Full-stack integration is blocked", projection["activity"][0]["title"])
        self.assertEqual("Prototype checkpoint 07 approved", projection["activity"][-1]["title"])
        self.assertEqual(["DEC-003", "DEC-006", "DEC-009", "DEC-012"], [item["id"] for item in projection["decisions"]])
        self.assertEqual("TESTING", projection["decisions"][-1]["status"])
        self.assertIn("repository", projection)

    def test_repository_projection_reads_local_branch_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="meta-pds-git-projection-") as temporary_root:
            repository = Path(temporary_root)
            commands = [
                ["git", "init", "-q", "-b", "main"],
                ["git", "config", "user.name", "Meta PDS Test"],
                ["git", "config", "user.email", "meta-pds@example.invalid"],
            ]
            for command in commands:
                completed = subprocess.run(command, cwd=repository, capture_output=True, text=True, check=False)
                self.assertEqual(0, completed.returncode, completed.stderr)
            (repository / "checkpoint.txt").write_text("first\n", encoding="utf-8")
            subprocess.run(["git", "add", "checkpoint.txt"], cwd=repository, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "Initial checkpoint"], cwd=repository, check=True)
            subprocess.run(["git", "switch", "-q", "-c", "codex/INIT-0001-discovery"], cwd=repository, check=True)
            (repository / "checkpoint.txt").write_text("first\nsecond\n", encoding="utf-8")

            projection = build_repository_data(repository, gh_executable="")
            self.assertTrue(projection["available"])
            self.assertEqual("codex/INIT-0001-discovery", projection["currentBranch"])
            self.assertEqual("main", projection["defaultBranch"])
            self.assertEqual(1, projection["dirtyPaths"])
            current = next(branch for branch in projection["branches"] if branch["isCurrent"])
            self.assertTrue(current["isManaged"])
            self.assertEqual("ACTIVE", current["status"])
            self.assertFalse(projection["pullRequestSource"]["available"])

    def test_pull_request_projection_preserves_evidence_states(self) -> None:
        records = pull_request_records([
            {
                "number": 7,
                "title": "Delivery checkpoint",
                "state": "OPEN",
                "isDraft": True,
                "headRefName": "codex/SLICE-001-delivery",
                "baseRefName": "main",
                "url": "https://example.invalid/pull/7",
                "reviewDecision": "REVIEW_REQUIRED",
                "mergeStateStatus": "BLOCKED",
                "updatedAt": "2026-08-22T05:00:00Z",
            },
            {"number": 6, "title": "Merged work", "state": "MERGED", "headRefName": "old", "baseRefName": "main"},
        ])
        self.assertEqual([7, 6], [record["number"] for record in records])
        self.assertEqual("DRAFT", records[0]["status"])
        self.assertEqual("REVIEW_REQUIRED", records[0]["reviewDecision"])
        self.assertEqual("MERGED", records[1]["status"])

    def test_manifest_declares_installed_dashboard_bundle(self) -> None:
        suite_root = SKILL_ROOT.parent.parent
        manifest = json.loads((suite_root / "manifest.json").read_text(encoding="utf-8"))
        dashboard = manifest["dashboard"]
        self.assertEqual("ensure-one-runtime-per-project", dashboard["lifecycle"])
        declared = [dashboard["entrypoint"], *dashboard["assets"]]
        self.assertEqual(4, len(declared))
        for relative_path in declared:
            self.assertTrue((suite_root / relative_path).is_file(), relative_path)

        pack_manifest = json.loads((suite_root.parent / "manifest.json").read_text(encoding="utf-8"))
        bundled_skills = {item["name"]: item["path"] for item in pack_manifest["skills"] if item["kind"] == "bundled"}
        self.assertEqual("meta-pds/skills/meta-pds", bundled_skills["meta-pds"])
        for skill_name in ["rapid-prototyping", "slice-planning", "slice-development", "slice-qa"]:
            self.assertIn(skill_name, bundled_skills)

    def test_ensure_dashboard_reuses_one_runtime_for_project(self) -> None:
        first = ensure_dashboard(self.root, SKILL_ROOT, port=0, startup_timeout=5)
        process = first["process"]
        try:
            second = ensure_dashboard(self.root, SKILL_ROOT, port=0, startup_timeout=5)
            self.assertEqual("started", first["status"])
            self.assertEqual("reused", second["status"])
            self.assertEqual(first["url"], second["url"])
            self.assertEqual(first["pid"], second["pid"])
            self.assertEqual(str(self.root.resolve()), second["runtime"]["projectRoot"])
        finally:
            process.terminate()
            process.wait(timeout=5)

    def test_ensure_dashboard_never_substitutes_sample_project_data(self) -> None:
        with tempfile.TemporaryDirectory(prefix="meta-pds-runtime-transition-") as temporary_root:
            project_root = Path(temporary_root)
            live = ensure_dashboard(project_root, SKILL_ROOT, port=0, startup_timeout=5)
            try:
                self.assertEqual("live-project", live["projectionKind"])
                with urlopen(f"{live['url']}/api/dashboard", timeout=5) as response:
                    empty_projection = json.loads(response.read())
                self.assertEqual("live-project", empty_projection["projection"]["kind"])
                self.assertEqual([], empty_projection["slices"])
                self.assertEqual([], empty_projection["decisions"])
                self.assertNotIn("Learning Platform V1", json.dumps(empty_projection))
                self.assertGreater(empty_projection["dataHealth"]["errors"], 0)

                shutil.copytree(self.base, project_root / "docs" / "meta-pds")
                refreshed = ensure_dashboard(project_root, SKILL_ROOT, port=0, startup_timeout=5)
                self.assertEqual("reused", refreshed["status"])
                self.assertEqual(live["pid"], refreshed["pid"])
                with urlopen(f"{live['url']}/api/dashboard", timeout=5) as response:
                    canonical_projection = json.loads(response.read())
                self.assertEqual(1, len(canonical_projection["slices"]))
                self.assertEqual("INIT-0042", canonical_projection["initiative"]["id"])
            finally:
                live["process"].terminate()
                live["process"].wait(timeout=5)

    def test_cli_defaults_to_repository_wide_validation(self) -> None:
        validator = Path(__file__).with_name("validate_meta_pds.py")
        passed = subprocess.run([sys.executable, str(validator), str(self.root)], capture_output=True, text=True, check=False)
        self.assertEqual(0, passed.returncode, passed.stdout + passed.stderr)
        (self.base / "execution" / "BROKEN.yaml").write_text("not valid yaml\n")
        failed = subprocess.run([sys.executable, str(validator), str(self.root), "--all"], capture_output=True, text=True, check=False)
        self.assertEqual(1, failed.returncode)
        self.assertIn("docs/meta-pds/execution/BROKEN.yaml", failed.stdout)

    def test_malformed_story_is_reported_instead_of_silent(self) -> None:
        path = self.base / "slices" / "SLICE-AUTH-001.md"
        path.write_text(path.read_text().replace("### US-AUTH-01 —", "### Story US-AUTH-01 —", 1))
        projection = self.projection()
        self.assertEqual(5, len(projection["stories"]))
        self.assertEqual("INVALID", projection["dataHealth"]["status"])
        self.assertIn("slice.story-grammar", {item["code"] for item in projection["dataHealth"]["diagnostics"]})

    def test_renamed_contract_heading_is_reported(self) -> None:
        (self.base / "execution" / "SLICE-AUTH-001.yaml").unlink()
        path = self.base / "slices" / "SLICE-AUTH-001.md"
        path.write_text(path.read_text().replace("### Contract expectations", "### Integration contract expectations", 1))
        projection = self.projection()
        self.assertEqual(0, len(projection["contracts"]))
        self.assertIn("slice.contract-heading", {item["code"] for item in projection["dataHealth"]["diagnostics"]})

    def test_duplicate_yaml_keys_are_rejected(self) -> None:
        with self.assertRaisesRegex(ArtifactError, "Duplicate YAML key 'health'"):
            parse_yaml("health: ON_TRACK\nhealth: OFF_TRACK\n")

    def test_wrong_delivery_type_is_visible_without_crashing(self) -> None:
        path = self.base / "delivery-state.yaml"
        path.write_text(path.read_text().replace("slice_states:\n  - slice_id:", "slice_states: {}\nignored_states:\n  - slice_id:", 1))
        projection = self.projection()
        self.assertEqual(1, len(projection["slices"]))
        self.assertIn("delivery-state.type", {item["code"] for item in projection["dataHealth"]["diagnostics"]})

    def test_unrelated_broken_execution_is_quarantined(self) -> None:
        (self.base / "execution" / "BROKEN.yaml").write_text("not valid yaml\n")
        projection = self.projection()
        self.assertEqual(7, len(projection["workPackages"]))
        self.assertIn("docs/meta-pds/execution/BROKEN.yaml", {item["file"] for item in projection["dataHealth"]["diagnostics"]})

    def test_unrelated_broken_report_is_quarantined(self) -> None:
        reports = self.base / "reports"
        reports.mkdir()
        (reports / "BROKEN.md").write_text("# Missing frontmatter\n")
        projection = self.projection()
        self.assertEqual(1, len(projection["slices"]))
        self.assertIn("docs/meta-pds/reports/BROKEN.md", {item["file"] for item in projection["dataHealth"]["diagnostics"]})

    def test_broken_decision_log_does_not_hide_delivery_data(self) -> None:
        (self.base / "decision-log.yaml").write_text("not valid yaml\n")
        projection = self.projection()
        self.assertEqual(1, len(projection["slices"]))
        self.assertEqual([], projection["decisions"])
        self.assertIn("docs/meta-pds/decision-log.yaml", {item["file"] for item in projection["dataHealth"]["diagnostics"]})

    def test_invalid_activity_line_is_reported(self) -> None:
        (self.base / "delivery-events.jsonl").write_text("{invalid json}\n")
        projection = self.projection()
        self.assertEqual([], projection["activity"])
        self.assertIn("event.parse", {item["code"] for item in projection["dataHealth"]["diagnostics"]})

    def test_invalid_human_decision_type_does_not_crash_projection(self) -> None:
        path = self.base / "delivery-state.yaml"
        path.write_text(path.read_text().replace("human_decision_required: null", "human_decision_required: 42"))
        projection = self.projection()
        self.assertEqual("42", projection["attention"][0]["detail"])
        self.assertIn("delivery-state.type", {item["code"] for item in projection["dataHealth"]["diagnostics"]})

    def test_literal_and_folded_yaml_scalars_are_supported(self) -> None:
        parsed = parse_yaml("description: |\n  first line\n  second line\nsummary: >\n  folded\n  value\n")
        self.assertEqual("first line\nsecond line", parsed["description"])
        self.assertEqual("folded value", parsed["summary"])

    def test_duplicate_declared_slice_id_is_reported_and_not_joined_twice(self) -> None:
        original = self.base / "slices" / "SLICE-AUTH-001.md"
        (self.base / "slices" / "SLICE-DUP.md").write_text(original.read_text())
        projection = self.projection()
        self.assertIn("id.duplicate-slice", {item["code"] for item in projection["dataHealth"]["diagnostics"]})
        ids = [item["id"] for item in projection["slices"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_unsupported_slice_schema_quarantines_dependent_execution(self) -> None:
        path = self.base / "slices" / "SLICE-AUTH-001.md"
        path.write_text(path.read_text().replace("schema_version: 2", "schema_version: 99", 1))
        projection = self.projection()
        self.assertEqual([], projection["stories"])
        self.assertEqual([], projection["workPackages"])
        self.assertIn("schema.version", {item["code"] for item in projection["dataHealth"]["diagnostics"]})

    def test_escaped_markdown_table_pipe_remains_in_cell(self) -> None:
        rows = parse_table("| A | B |\n| --- | --- |\n| one \\| two | value |")
        self.assertEqual([{"A": "one | two", "B": "value"}], rows)


if __name__ == "__main__":
    unittest.main()
