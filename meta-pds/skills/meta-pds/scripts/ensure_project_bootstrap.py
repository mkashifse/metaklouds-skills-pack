#!/usr/bin/env python3
"""Install or verify the managed Meta PDS PM bootstrap in a product AGENTS.md."""

from __future__ import annotations

import argparse
from pathlib import Path


START_MARKER = "<!-- META_PDS_PM_BOOTSTRAP:START -->"
END_MARKER = "<!-- META_PDS_PM_BOOTSTRAP:END -->"
SKILL_ROOT = Path(__file__).resolve().parent.parent
BOOTSTRAP_TEMPLATE = SKILL_ROOT / "assets" / "project-pm-bootstrap.md"


def expected_block() -> str:
    return BOOTSTRAP_TEMPLATE.read_text(encoding="utf-8").strip()


def reconcile_agents_file(product_root: Path, *, check: bool = False) -> tuple[str, Path]:
    root = product_root.resolve()
    if not root.is_dir():
        raise ValueError(f"Product root is not a directory: {root}")

    agents_path = root / "AGENTS.md"
    current = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    has_start = START_MARKER in current
    has_end = END_MARKER in current
    if has_start != has_end:
        raise ValueError(
            f"Refusing to modify malformed Meta PDS bootstrap markers in {agents_path}"
        )

    block = expected_block()
    if has_start:
        start = current.index(START_MARKER)
        end = current.index(END_MARKER, start) + len(END_MARKER)
        updated = current[:start] + block + current[end:]
        status = "UNCHANGED" if updated == current else "OUTDATED"
    else:
        separator = "\n\n" if current.strip() else ""
        updated = current.rstrip() + separator + block + "\n"
        status = "MISSING"

    if check:
        return status, agents_path

    if updated == current:
        return "UNCHANGED", agents_path

    agents_path.write_text(updated, encoding="utf-8")
    return ("CREATED" if not current else "UPDATED"), agents_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ensure the project-local Meta PDS PM bootstrap"
    )
    parser.add_argument("product_root", type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report whether the managed block is current without writing",
    )
    args = parser.parse_args()

    try:
        status, path = reconcile_agents_file(args.product_root, check=args.check)
    except ValueError as exc:
        parser.error(str(exc))

    print(f"{status}: {path}")
    if args.check and status != "UNCHANGED":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
