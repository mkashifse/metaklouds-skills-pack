#!/usr/bin/env python3

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from serve_dashboard import DASHBOARD_ROOT, RUNTIME_VERSION, state
from solo_founder_core import (
    LAYERS,
    approve_truth,
    atomic_write_yaml,
    dump_yaml,
    parse_yaml,
    read_yaml,
    sha256_file,
    upgrade_ledger,
    validate_ledger,
    validate_truth,
)


class SoloFounderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = Path(__file__).resolve().parent.parent
        self.temporary = tempfile.TemporaryDirectory(prefix="solo-founder-tests-")
        self.root = Path(self.temporary.name)
        subprocess.run(
            [
                sys.executable,
                str(self.skill / "scripts" / "restore_context.py"),
                str(self.root),
                "--init",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.base = self.root / "docs" / "solo-founder"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_templates_validate_and_context_bootstrap_exists(self) -> None:
        validate_truth(read_yaml(self.base / "canonical-truth.yaml"))
        validate_ledger(read_yaml(self.base / "product-ledger.yaml"))
        self.assertIn("$solo-founder", (self.root / "AGENTS.md").read_text())

    def test_repository_structure_is_additive_and_git_visible(self) -> None:
        expected = (
            "docs/solo-founder/research",
            "docs/solo-founder/slices",
            "docs/solo-founder/reports",
            "docs/solo-founder/architecture",
            "docs/solo-founder/handoffs/research",
            "docs/solo-founder/handoffs/documentation",
            "docs/solo-founder/handoffs/prototype",
            "docs/solo-founder/handoffs/implementation",
            "docs/solo-founder/handoffs/verification",
            "docs/solo-founder/handoffs/exception",
            "prototypes/frontend",
            "prototypes/mobile",
            "apps/frontend",
            "apps/mobile",
            "apps/backend",
            "packages/contracts",
            "packages/domain",
            "packages/ui",
            "packages/shared",
            "packages/config",
            "infrastructure",
            "tests/e2e",
            "tests/integration",
        )
        for relative_path in expected:
            directory = self.root / relative_path
            self.assertTrue(directory.is_dir(), relative_path)
            self.assertTrue((directory / ".gitkeep").is_file(), relative_path)

        existing = self.root / "apps" / "frontend" / "existing.txt"
        existing.write_text("preserve me", encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                str(self.skill / "scripts" / "restore_context.py"),
                str(self.root),
                "--init",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual("preserve me", existing.read_text(encoding="utf-8"))

    def test_yaml_round_trip(self) -> None:
        value = {"name": "Gym plan", "items": [{"id": "ONE", "ok": True}], "empty": []}
        self.assertEqual(value, parse_yaml(dump_yaml(value)))

    def test_dashboard_truth_approval(self) -> None:
        path = self.base / "canonical-truth.yaml"
        document = read_yaml(path)
        document["truth"]["BUSINESS_DIRECTION"].append(
            {
                "id": "BUSINESS_DIRECTION-001",
                "status": "PROPOSED",
                "title": "Initial customer",
                "statement": "Independent gym members are the initial customer.",
                "evidence": ["Human direction"],
                "affected_layers": ["PRODUCT_DIRECTION"],
                "proposed_at": "2026-08-25T12:00:00+05:00",
                "approved_at": None,
                "approved_by": None,
                "approved_via": None,
            }
        )
        atomic_write_yaml(path, document)
        approved = approve_truth(self.root, "BUSINESS_DIRECTION-001", sha256_file(path))
        self.assertEqual("APPROVED", approved["status"])
        validate_truth(read_yaml(path))

    def test_dashboard_projects_current_solo_founder_data(self) -> None:
        for name in ("index.html", "styles.css", "app.js"):
            self.assertTrue((DASHBOARD_ROOT / name).is_file(), name)
        self.assertEqual(2, RUNTIME_VERSION)

        slice_path = self.base / "slices" / "SLICE-0001.md"
        template = (self.skill / "assets" / "fat-slice-template.md").read_text(
            encoding="utf-8"
        )
        slice_path.write_text(
            template.replace('title: ""', 'title: "Member workout plan"')
            .replace(
                "## Capability outcome\n",
                "## Capability outcome\n\nMember completes a guided workout.\n",
            )
            .replace(
                "## Test expectations\n",
                "## Test expectations\n\n### TEST-0002 — Workout completion\n",
            ),
            encoding="utf-8",
        )

        updater = self.skill / "scripts" / "update_ledger.py"
        subprocess.run(
            [
                sys.executable,
                str(updater),
                str(self.root),
                "--actor",
                "PM",
                "--create-work",
                "WORK-DASHBOARD",
                "--title",
                "Verify workout flow",
                "--classification",
                "TRIVIAL",
                "--activity",
                "TESTING",
                "--status",
                "ACTIVE",
                "--acceptance",
                "Workout evidence reviewed",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        projection = state(self.root)
        self.assertEqual(1, projection["counts"]["slices"])
        self.assertEqual(1, projection["counts"]["active_work"])
        self.assertEqual(1, projection["counts"]["direct_work"])
        self.assertEqual("SLICE-0001", projection["slices"][0]["id"])
        self.assertEqual("Member workout plan", projection["slices"][0]["title"])
        self.assertEqual(1, projection["slices"][0]["story_count"])
        self.assertEqual(2, projection["slices"][0]["test_count"])
        self.assertEqual([], projection["diagnostics"])

        (self.base / "slices" / "BROKEN.md").write_text(
            "# Missing frontmatter\n", encoding="utf-8"
        )
        degraded = state(self.root)
        self.assertEqual(1, degraded["counts"]["slices"])
        self.assertEqual(1, len(degraded["diagnostics"]))

    def test_engineer_cannot_mark_done(self) -> None:
        updater = self.skill / "scripts" / "update_ledger.py"
        subprocess.run(
            [
                sys.executable,
                str(updater),
                str(self.root),
                "--actor",
                "PM",
                "--create-work",
                "WORK-0001",
                "--title",
                "Build UI",
                "--classification",
                "NON_TRIVIAL",
                "--workstream",
                "FULL_STACK",
                "--activity",
                "IMPLEMENTATION",
                "--role",
                "FULL_STACK_ENGINEER",
                "--owner",
                "full-stack-1",
                "--delegation-reason",
                "PARALLELISM",
                "--handoff-type",
                "IMPLEMENTATION",
                "--acceptance",
                "Page renders",
                "--status",
                "READY",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        failed = subprocess.run(
            [
                sys.executable,
                str(updater),
                str(self.root),
                "--actor",
                "ENGINEER",
                "--identity",
                "full-stack-1",
                "--work-id",
                "WORK-0001",
                "--status",
                "DONE",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(0, failed.returncode)

    def test_pm_is_default_executor_for_code(self) -> None:
        updater = self.skill / "scripts" / "update_ledger.py"
        base = [sys.executable, str(updater), str(self.root)]
        subprocess.run(
            base
            + [
                "--actor",
                "PM",
                "--create-work",
                "WORK-PM-CODE",
                "--title",
                "Small end-to-end code change",
                "--classification",
                "TRIVIAL",
                "--workstream",
                "FULL_STACK",
                "--activity",
                "IMPLEMENTATION",
                "--status",
                "READY",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        ledger = read_yaml(self.base / "product-ledger.yaml")
        item = next(work for work in ledger["work"] if work["id"] == "WORK-PM-CODE")
        self.assertEqual("PM", item["role"])
        self.assertEqual("PM", item["owner"])
        self.assertEqual("DIRECT", item["execution"])
        self.assertIsNone(item["handoff_path"])

        subprocess.run(
            base
            + [
                "--actor",
                "PM",
                "--work-id",
                "WORK-PM-CODE",
                "--status",
                "DONE",
                "--result",
                "Small change completed",
                "--evidence",
                "tests:passed",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        completed = read_yaml(self.base / "product-ledger.yaml")
        validate_ledger(completed)
        item = next(work for work in completed["work"] if work["id"] == "WORK-PM-CODE")
        self.assertEqual("DONE", item["status"])
        self.assertIsNone(item["handoff_submitted_at"])
        self.assertIsNone(item["handoff_consumed_at"])

        failed = subprocess.run(
            base
            + [
                "--actor",
                "PM",
                "--create-work",
                "WORK-BAD-ROLE",
                "--title",
                "Invalid role",
                "--classification",
                "TRIVIAL",
                "--role",
                "FRONTEND_ENGINEER",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, failed.returncode)

        missing_contract = subprocess.run(
            base
            + [
                "--actor",
                "PM",
                "--create-work",
                "WORK-MISSING-HANDOFF",
                "--title",
                "Invalid delegated package",
                "--classification",
                "NON_TRIVIAL",
                "--role",
                "FULL_STACK_ENGINEER",
                "--owner",
                "full-stack-1",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, missing_contract.returncode)

    def test_delegated_research_handoff_is_required_and_consumed(self) -> None:
        updater = self.skill / "scripts" / "update_ledger.py"
        base = [sys.executable, str(updater), str(self.root)]
        subprocess.run(
            base
            + [
                "--actor",
                "PM",
                "--create-work",
                "WORK-0002",
                "--title",
                "Deep parallel technical research",
                "--classification",
                "NON_TRIVIAL",
                "--workstream",
                "FULL_STACK",
                "--activity",
                "RESEARCH",
                "--role",
                "FULL_STACK_ENGINEER",
                "--owner",
                "research-1",
                "--delegation-reason",
                "PARALLELISM",
                "--handoff-type",
                "RESEARCH",
                "--owned-path",
                "docs/solo-founder/handoffs/research",
                "--acceptance",
                "Reproducible evidence supports the PM decision",
                "--status",
                "READY",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            base
            + [
                "--actor",
                "ENGINEER",
                "--identity",
                "research-1",
                "--work-id",
                "WORK-0002",
                "--status",
                "ACTIVE",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        failed = subprocess.run(
            base
            + [
                "--actor",
                "ENGINEER",
                "--identity",
                "research-1",
                "--work-id",
                "WORK-0002",
                "--status",
                "VERIFYING",
                "--result",
                "Research complete",
                "--evidence",
                "source:https://example.com",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, failed.returncode)

        subprocess.run(
            [
                sys.executable,
                str(self.skill / "scripts" / "create_handoff.py"),
                str(self.root),
                "--work-id",
                "WORK-0002",
                "--identity",
                "research-1",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        handoff = self.base / "handoffs" / "research" / "WORK-0002.md"
        content = handoff.read_text(encoding="utf-8")
        content = re.sub(
            r"<!--.*?-->", "Completed with durable evidence.", content, flags=re.DOTALL
        )
        handoff.write_text(content, encoding="utf-8")

        subprocess.run(
            base
            + [
                "--actor",
                "ENGINEER",
                "--identity",
                "research-1",
                "--work-id",
                "WORK-0002",
                "--status",
                "VERIFYING",
                "--result",
                "Research complete",
                "--evidence",
                "source:https://example.com",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            base
            + [
                "--actor",
                "PM",
                "--work-id",
                "WORK-0002",
                "--status",
                "DONE",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        ledger = read_yaml(self.base / "product-ledger.yaml")
        validate_ledger(ledger)
        item = next(work for work in ledger["work"] if work["id"] == "WORK-0002")
        self.assertEqual("DONE", item["status"])
        self.assertEqual("NON_TRIVIAL", item["classification"])
        self.assertEqual("DELEGATED", item["execution"])
        self.assertEqual("FULL_STACK_ENGINEER", item["role"])
        self.assertEqual("research-1", item["owner"])
        self.assertEqual("PARALLELISM", item["delegation_reason"])
        self.assertEqual("RESEARCH", item["handoff_type"])
        self.assertTrue(item["handoff_submitted_at"])
        self.assertRegex(item["handoff_submitted_hash"], r"^[0-9a-f]{64}$")
        self.assertTrue(item["handoff_consumed_at"])
        self.assertNotIn("WORK-0002", ledger["current"]["active_work_ids"])

        validator = self.skill / "scripts" / "validate_artifacts.py"
        subprocess.run(
            [sys.executable, str(validator), str(self.root)],
            check=True,
            capture_output=True,
            text=True,
        )
        handoff.write_text(
            handoff.read_text(encoding="utf-8").replace(
                "Completed with durable evidence.",
                "Changed after PM consumption.",
                1,
            ),
            encoding="utf-8",
        )
        failed_audit = subprocess.run(
            [sys.executable, str(validator), str(self.root)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, failed_audit.returncode)

    def test_parallel_engineers_cannot_cross_assignment_boundaries(self) -> None:
        updater = self.skill / "scripts" / "update_ledger.py"
        base = [sys.executable, str(updater), str(self.root)]
        for work_id, focus, owner in (
            ("WORK-0101", "BACKEND", "full-stack-1"),
            ("WORK-0102", "FRONTEND", "full-stack-2"),
        ):
            subprocess.run(
                base
                + [
                    "--actor",
                    "PM",
                    "--create-work",
                    work_id,
                    "--title",
                    f"Parallel {focus.lower()} package",
                    "--classification",
                    "NON_TRIVIAL",
                    "--workstream",
                    focus,
                    "--activity",
                    "IMPLEMENTATION",
                    "--role",
                    "FULL_STACK_ENGINEER",
                    "--owner",
                    owner,
                    "--delegation-reason",
                    "PARALLELISM",
                    "--handoff-type",
                    "IMPLEMENTATION",
                    "--acceptance",
                    "Bounded result",
                    "--status",
                    "READY",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        failed = subprocess.run(
            base
            + [
                "--actor",
                "ENGINEER",
                "--identity",
                "full-stack-1",
                "--work-id",
                "WORK-0102",
                "--status",
                "ACTIVE",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, failed.returncode)

    def test_legacy_roles_upgrade_to_two_role_model(self) -> None:
        ledger = read_yaml(self.base / "product-ledger.yaml")
        ledger["schema_version"] = 1
        ledger["work"] = [
            {
                "id": "WORK-LEGACY",
                "classification": "NON_TRIVIAL",
                "workstream": "FRONTEND",
                "activity": "IMPLEMENTATION",
                "execution": "DELEGATED",
                "owner": "FRONTEND",
                "status": "READY",
                "acceptance_criteria": [],
                "evidence": [],
                "owned_paths": [],
            }
        ]
        self.assertTrue(upgrade_ledger(ledger))
        validate_ledger(ledger)
        self.assertEqual(3, ledger["schema_version"])
        self.assertEqual("FULL_STACK_ENGINEER", ledger["work"][0]["role"])
        self.assertEqual("LEGACY_ASSIGNMENT", ledger["work"][0]["delegation_reason"])
        self.assertEqual("IMPLEMENTATION", ledger["work"][0]["handoff_type"])

    def test_layer_order_is_stable(self) -> None:
        truth = read_yaml(self.base / "canonical-truth.yaml")
        self.assertEqual(LAYERS, tuple(truth["truth"].keys()))


if __name__ == "__main__":
    unittest.main()
