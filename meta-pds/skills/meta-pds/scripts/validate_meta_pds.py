#!/usr/bin/env python3
"""Validate Meta PDS canonical artifacts through the dashboard's shared contract."""

from __future__ import annotations

import argparse
from pathlib import Path

from serve_dashboard import validate_product_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("product_root", type=Path)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--all", action="store_true", help="Validate every discovered artifact (the default)")
    selection.add_argument("--slice-id", action="append", dest="slice_ids", help="Validate one slice; repeat to validate several")
    parser.add_argument("--require-execution-plan", action="store_true")
    args = parser.parse_args()

    selected = set(args.slice_ids) if args.slice_ids else None
    diagnostics = validate_product_artifacts(
        args.product_root,
        selected_slice_ids=selected,
        require_execution_plan=args.require_execution_plan,
    )
    for item in diagnostics:
        print(f"{item['severity'].upper()}: {item['file']}: [{item['code']}] {item['message']}")
    errors = sum(item["severity"] == "error" for item in diagnostics)
    warnings = sum(item["severity"] == "warning" for item in diagnostics)
    if errors:
        print(f"Meta PDS validation failed: {errors} error(s), {warnings} warning(s).")
        return 1
    print(f"Meta PDS artifact validation passed: {warnings} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
