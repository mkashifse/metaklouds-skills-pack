#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
            "docs/solo-founder/handoffs",
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

    def test_only_approved_engineer_roles_can_own_code(self) -> None:
        updater = self.skill / "scripts" / "update_ledger.py"
        base = [sys.executable, str(updater), str(self.root)]
        for work_id, role, owner in (
            ("WORK-BAD-ROLE", "FRONTEND_ENGINEER", "frontend-1"),
            ("WORK-PM-CODE", "PM", "PM"),
        ):
            failed = subprocess.run(
                base
                + [
                    "--actor",
                    "PM",
                    "--create-work",
                    work_id,
                    "--title",
                    "Invalid engineering assignment",
                    "--classification",
                    "TRIVIAL",
                    "--workstream",
                    "FULL_STACK",
                    "--activity",
                    "IMPLEMENTATION",
                    "--role",
                    role,
                    "--owner",
                    owner,
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, failed.returncode, role)

    def test_trivial_cross_stack_change_has_one_full_stack_owner(self) -> None:
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
                "Add one profile field end-to-end",
                "--classification",
                "TRIVIAL",
                "--workstream",
                "FULL_STACK",
                "--activity",
                "IMPLEMENTATION",
                "--role",
                "FULL_STACK_ENGINEER",
                "--owner",
                "full-stack-1",
                "--owned-path",
                "apps/frontend",
                "--owned-path",
                "apps/backend",
                "--owned-path",
                "packages/contracts",
                "--acceptance",
                "Backend data renders",
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
                "full-stack-1",
                "--work-id",
                "WORK-0002",
                "--status",
                "ACTIVE",
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
                "full-stack-1",
                "--work-id",
                "WORK-0002",
                "--status",
                "VERIFYING",
                "--result",
                "Connected adapter",
                "--evidence",
                "commit:abc123",
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
        self.assertEqual("TRIVIAL", item["classification"])
        self.assertEqual("DELEGATED", item["execution"])
        self.assertEqual("FULL_STACK_ENGINEER", item["role"])
        self.assertEqual("full-stack-1", item["owner"])
        self.assertNotIn("WORK-0002", ledger["current"]["active_work_ids"])

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
        self.assertEqual(2, ledger["schema_version"])
        self.assertEqual("FULL_STACK_ENGINEER", ledger["work"][0]["role"])

    def test_layer_order_is_stable(self) -> None:
        truth = read_yaml(self.base / "canonical-truth.yaml")
        self.assertEqual(LAYERS, tuple(truth["truth"].keys()))


if __name__ == "__main__":
    unittest.main()
