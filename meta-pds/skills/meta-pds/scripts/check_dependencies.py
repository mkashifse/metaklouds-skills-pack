#!/usr/bin/env python3
"""Check that the complete Meta PDS profile is installed beside this skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


INTERNAL_SKILLS = (
    "rapid-prototyping",
    "slice-planning",
    "slice-development",
    "slice-qa",
)
SUPPORT_SKILLS = (
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
)


def dependency_status(skills_root: Path) -> dict[str, object]:
    groups = {"internal": INTERNAL_SKILLS, "support": SUPPORT_SKILLS}
    missing = {
        group: [name for name in names if not (skills_root / name / "SKILL.md").is_file()]
        for group, names in groups.items()
    }
    return {
        "status": "ready" if not any(missing.values()) else "incomplete",
        "skillsRoot": str(skills_root.resolve()),
        "required": {group: list(names) for group, names in groups.items()},
        "missing": missing,
        "repair": "Run the Metaklouds pack installer with --force; selecting --only meta-pds installs the complete dependency profile.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Skills directory containing meta-pds and its sibling skills.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable status.")
    args = parser.parse_args()

    result = dependency_status(args.skills_root)
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["status"] == "ready":
        print("Meta PDS dependency profile: ready")
    else:
        missing = result["missing"]
        for group in ("internal", "support"):
            if missing[group]:
                print(f"Missing {group} skills: {', '.join(missing[group])}")
        print(result["repair"])
    return 0 if result["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
