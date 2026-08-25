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

    def test_specialist_cannot_mark_done(self) -> None:
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
                "--owner",
                "FRONTEND",
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
                "SPECIALIST",
                "--identity",
                "FRONTEND",
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

    def test_specialist_handoff_and_pm_completion(self) -> None:
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
                "Connect frontend",
                "--classification",
                "NON_TRIVIAL",
                "--workstream",
                "FRONTEND",
                "--activity",
                "IMPLEMENTATION",
                "--owner",
                "FRONTEND",
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
                "SPECIALIST",
                "--identity",
                "FRONTEND",
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
                "SPECIALIST",
                "--identity",
                "FRONTEND",
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
        self.assertNotIn("WORK-0002", ledger["current"]["active_work_ids"])

    def test_layer_order_is_stable(self) -> None:
        truth = read_yaml(self.base / "canonical-truth.yaml")
        self.assertEqual(LAYERS, tuple(truth["truth"].keys()))


if __name__ == "__main__":
    unittest.main()
