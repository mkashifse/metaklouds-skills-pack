#!/usr/bin/env python3
"""Regression tests for the Meta PDS artifact contract and dashboard projection."""

from __future__ import annotations

import unittest
import subprocess
import sys
from pathlib import Path

from serve_dashboard import (
    ArtifactError,
    build_dashboard_data,
    parse_table,
    parse_yaml,
    prepare_demo_root,
    validate_product_artifacts,
)


SKILL_ROOT = Path(__file__).resolve().parent.parent


class MetaPDSContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = prepare_demo_root(SKILL_ROOT)
        self.root = Path(self.runtime.name)
        self.base = self.root / "docs" / "meta-pds"

    def tearDown(self) -> None:
        self.runtime.cleanup()

    def diagnostics(self) -> list[dict]:
        return validate_product_artifacts(self.root)

    def projection(self) -> dict:
        return build_dashboard_data(self.root)

    def test_bundled_example_is_valid_and_complete(self) -> None:
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
