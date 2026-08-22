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

from check_dependencies import INTERNAL_SKILLS, SUPPORT_SKILLS, dependency_status
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
        self.assertEqual(12, len(projection["activity"]))
        self.assertEqual("Full-stack integration is blocked", projection["activity"][0]["title"])
        self.assertEqual("Prototype checkpoint 07 approved", projection["activity"][-1]["title"])
        packages = {item["id"]: item for item in projection["workPackages"]}
        self.assertEqual("BACKLOG", packages["WP-AUTH-07"]["status"])
        self.assertEqual("Product Manager", packages["WP-AUTH-03"]["assignedBy"])
        self.assertEqual("Development Lead", packages["WP-AUTH-03"]["leadBrief"]["issuedBy"])
        self.assertIn("complete authentication lifecycle API", packages["WP-AUTH-03"]["leadBrief"]["instruction"])
        self.assertTrue(packages["WP-AUTH-03"]["history"])
        self.assertEqual(20, len(projection["decisions"]))
        self.assertEqual(18, len({item["type"] for item in projection["decisions"]}))
        self.assertEqual(20, len({item["key"] for item in projection["decisions"]}))
        self.assertEqual(["GLOBAL", "PHASE-1", "PHASE-2", "PHASE-3"], projection["decisionMeta"]["phases"])
        self.assertEqual("DELIVERY", projection["decisionMeta"]["interactionMode"])
        self.assertEqual((16, 7, 4), (
            projection["decisionMeta"]["canonicalCount"],
            projection["decisionMeta"]["reviewCount"],
            projection["decisionMeta"]["contradictionCount"],
        ))
        self.assertEqual((24, 3, 1), (
            projection["decisionMeta"]["revisionCount"],
            projection["decisionMeta"]["historyCount"],
            projection["decisionMeta"]["candidateCount"],
        ))
        by_key = {item["key"]: item for item in projection["decisions"]}
        authentication = by_key["feature.authentication.email-password"]
        self.assertEqual(("DEC-005", 2, True), (authentication["id"], authentication["revision"], authentication["canonical"]))
        self.assertEqual([("DEC-005-R1", 1, "SUPERSEDED")], [
            (item["id"], item["revision"], item["status"]) for item in authentication["history"]
        ])
        self.assertEqual(("DEC-005-R3", 3, "TESTING"), (
            authentication["candidateRevision"]["id"],
            authentication["candidateRevision"]["revision"],
            authentication["candidateRevision"]["status"],
        ))
        self.assertEqual(["ux.navigation.topbar"], [item["key"] for item in by_key["ux.navigation.sidebar"]["contradictions"]])
        self.assertEqual(["ux.navigation.sidebar"], [item["key"] for item in by_key["ux.navigation.topbar"]["contradictions"]])
        self.assertTrue(by_key["storage.postgres.primary"]["canonical"])
        self.assertFalse(by_key["storage.document.primary"]["canonical"])
        self.assertEqual(5, len(projection["drifts"]))
        self.assertEqual((1, 3, 1, 0), (
            projection["driftMeta"]["openCount"],
            projection["driftMeta"]["autoResolvedCount"],
            projection["driftMeta"]["humanApprovalCount"],
            projection["driftMeta"]["criticalCount"],
        ))
        pending = next(item for item in projection["drifts"] if item["status"] == "HUMAN_APPROVAL_NEEDED")
        self.assertEqual(["WP-AUTH-03", "WP-AUTH-06", "WP-AUTH-07"], pending["blockedWorkPackages"])
        self.assertEqual(["WP-AUTH-04", "WP-AUTH-05"], pending["continuingWorkPackages"])
        self.assertIn("repository", projection)

    def test_drift_auto_resolution_requires_safe_high_confidence_evidence(self) -> None:
        path = self.base / "drift-log.yaml"
        path.write_text(path.read_text().replace("resolution_confidence: 96", "resolution_confidence: 60", 1))
        self.assertIn("drift.auto-resolution", {item["code"] for item in self.diagnostics()})

    def test_execution_v3_requires_immutable_lead_brief(self) -> None:
        path = self.base / "execution" / "SLICE-AUTH-001.yaml"
        content = path.read_text().replace("issued_by: Development Lead", 'issued_by: ""', 1)
        path.write_text(content)
        self.assertIn("package.lead-brief", {item["code"] for item in self.diagnostics()})

    def test_production_intent_frontend_package_requires_promotion_sources(self) -> None:
        path = self.base / "execution" / "SLICE-AUTH-001.yaml"
        content = path.read_text().replace(
            "    prototype_sources:\n      - source: prototypes/INIT-0042/auth/src/components/AuthFormShell.tsx",
            "    prototype_sources: []\n    ignored_prototype_sources:\n      - source: prototypes/INIT-0042/auth/src/components/AuthFormShell.tsx",
            1,
        )
        path.write_text(content)
        self.assertIn("prototype-promotion.sources", {item["code"] for item in self.diagnostics()})

    def test_prototype_promotion_rejects_invalid_classification(self) -> None:
        path = self.base / "execution" / "SLICE-AUTH-001.yaml"
        path.write_text(path.read_text().replace("classification: REUSE_AS_IS", "classification: REGENERATE", 1))
        self.assertIn("prototype-promotion.classification", {item["code"] for item in self.diagnostics()})

    def test_react_prototype_promotion_requires_vercel_guidance(self) -> None:
        path = self.base / "execution" / "SLICE-AUTH-001.yaml"
        path.write_text(path.read_text().replace(
            "applicable_skills: [frontend-design, vercel-react-best-practices, vercel-composition-patterns]",
            "applicable_skills: [frontend-design]",
            1,
        ))
        self.assertIn("prototype-promotion.skill", {item["code"] for item in self.diagnostics()})

    def test_human_approval_drift_requires_recommendation_and_pending_approval(self) -> None:
        path = self.base / "drift-log.yaml"
        content = path.read_text().replace(
            "recommendation: Keep the locked schema and restore role_ids in the event adapter.",
            'recommendation: ""',
            1,
        ).replace("status: PENDING", "status: NOT_REQUIRED", 1)
        path.write_text(content)
        codes = {item["code"] for item in self.diagnostics()}
        self.assertIn("drift.recommendation", codes)
        self.assertIn("drift.approval", codes)

    def test_drift_contract_rejects_unknown_truth_slice_and_work_package(self) -> None:
        path = self.base / "drift-log.yaml"
        content = path.read_text().replace("data.profile.schema-v1", "data.profile.unknown", 1)
        content = content.replace("affected_slices: [SLICE-AUTH-001]", "affected_slices: [SLICE-UNKNOWN]", 1)
        content = content.replace("affected_work_packages: [WP-AUTH-03, WP-AUTH-06]", "affected_work_packages: [WP-UNKNOWN]", 1)
        path.write_text(content)
        codes = {item["code"] for item in self.diagnostics()}
        self.assertTrue({"reference.decision", "reference.slice", "reference.package"}.issubset(codes))

    def test_drift_log_is_optional_until_first_detection(self) -> None:
        (self.base / "drift-log.yaml").unlink()
        projection = self.projection()
        self.assertEqual([], projection["drifts"])
        self.assertEqual([], self.diagnostics())

    def test_decision_contract_rejects_duplicate_revision_for_semantic_key(self) -> None:
        path = self.base / "decision-log.yaml"
        path.write_text(path.read_text().replace("key: product.user.busy-learners", "key: product.goal.guided-learning", 1))
        self.assertIn("id.duplicate-decision-revision", {item["code"] for item in self.diagnostics()})

    def test_decision_revision_chain_requires_previous_record_id(self) -> None:
        path = self.base / "decision-log.yaml"
        path.write_text(path.read_text().replace("supersedes: DEC-005-R1", "supersedes: DEC-UNKNOWN", 1))
        self.assertIn("reference.decision-revision", {item["code"] for item in self.diagnostics()})

    def test_decision_contract_rejects_unknown_contradiction_and_invalid_phase(self) -> None:
        path = self.base / "decision-log.yaml"
        content = path.read_text().replace("contradicts: [ux.navigation.sidebar]", "contradicts: [ux.navigation.unknown]", 1)
        content = content.replace("phases: [PHASE-3]", "phases: [PHASE-ZERO]", 1)
        path.write_text(content)
        codes = {item["code"] for item in self.diagnostics()}
        self.assertIn("reference.decision", codes)
        self.assertIn("decision.phase", codes)

    def test_two_locked_contradictory_decisions_are_invalid(self) -> None:
        path = self.base / "decision-log.yaml"
        content = path.read_text().replace(
            "key: ux.navigation.topbar\n    revision: 1\n    status: TESTING",
            "key: ux.navigation.topbar\n    revision: 1\n    status: LOCKED",
            1,
        )
        path.write_text(content)
        self.assertIn("decision.locked-contradiction", {item["code"] for item in self.diagnostics()})

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
        self.assertEqual(2, pack_manifest["schema_version"])
        self.assertEqual("meta-pds", pack_manifest["default_profile"]["entrypoint"])
        self.assertEqual(16, len(pack_manifest["default_profile"]["skills"]))
        bundled_skills = {item["name"]: item["path"] for item in pack_manifest["skills"] if item["kind"] == "bundled"}
        self.assertEqual("meta-pds/skills/meta-pds", bundled_skills["meta-pds"])
        for skill_name in ["rapid-prototyping", "slice-planning", "slice-development", "slice-qa"]:
            self.assertIn(skill_name, bundled_skills)
        self.assertEqual(5, len(bundled_skills))
        self.assertEqual(
            set(pack_manifest["default_profile"]["skills"]),
            {item["name"] for item in pack_manifest["skills"]},
        )

    def test_dependency_check_reports_complete_and_missing_profiles(self) -> None:
        with tempfile.TemporaryDirectory(prefix="meta-pds-skills-") as temporary_root:
            skills_root = Path(temporary_root)
            for skill_name in (*INTERNAL_SKILLS, *SUPPORT_SKILLS):
                skill_directory = skills_root / skill_name
                skill_directory.mkdir()
                (skill_directory / "SKILL.md").write_text(f"---\nname: {skill_name}\n---\n")
            ready = dependency_status(skills_root)
            self.assertEqual("ready", ready["status"])
            self.assertEqual({"internal": [], "support": []}, ready["missing"])

            (skills_root / "vitest" / "SKILL.md").unlink()
            incomplete = dependency_status(skills_root)
            self.assertEqual("incomplete", incomplete["status"])
            self.assertEqual(["vitest"], incomplete["missing"]["support"])

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
                self.assertEqual([], empty_projection["drifts"])
                self.assertNotIn("Learning Platform V1", json.dumps(empty_projection))
                self.assertGreater(empty_projection["dataHealth"]["errors"], 0)

                with urlopen(f"{live['url']}/api/dashboard?demo=1", timeout=5) as response:
                    demo_projection = json.loads(response.read())
                self.assertEqual("demo-fixture", demo_projection["projection"]["kind"])
                self.assertEqual("Learning Platform V1", demo_projection["initiative"]["name"])
                self.assertEqual(20, len(demo_projection["decisions"]))
                self.assertEqual(5, len(demo_projection["drifts"]))
                self.assertEqual(18, len({item["type"] for item in demo_projection["decisions"]}))

                with urlopen(f"{live['url']}/api/dashboard", timeout=5) as response:
                    live_after_demo = json.loads(response.read())
                self.assertEqual("live-project", live_after_demo["projection"]["kind"])
                self.assertEqual([], live_after_demo["decisions"])
                self.assertEqual([], live_after_demo["drifts"])
                self.assertNotIn("Learning Platform V1", json.dumps(live_after_demo))

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

    def test_execution_rejects_unsupported_applicable_skill(self) -> None:
        path = self.base / "execution" / "SLICE-AUTH-001.yaml"
        path.write_text(path.read_text().replace("applicable_skills: []", "applicable_skills: [obsolete-delivery-skill]", 1))
        self.assertIn("reference.skill", {item["code"] for item in self.diagnostics()})

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
