#!/usr/bin/env python3
"""Serve the Solo Founder cockpit from canonical repository artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from solo_founder_core import (
    LAYERS,
    ArtifactError,
    approve_truth,
    parse_yaml,
    read_yaml,
    sha256_file,
    validate_ledger,
    validate_truth,
)

DASHBOARD_ROOT = Path(__file__).resolve().parent.parent / "assets" / "dashboard"
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}
RUNTIME_VERSION = 2
TERMINAL_WORK_STATUSES = {"DONE", "CANCELLED"}


def runtime_path(product_root: Path) -> Path:
    digest = hashlib.sha256(str(product_root).encode()).hexdigest()[:16]
    directory = Path(tempfile.gettempdir()) / "solo-founder-dashboard"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{digest}.json"


def read_runtime(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def healthy(runtime: dict[str, Any] | None, product_root: Path) -> bool:
    if (
        not runtime
        or runtime.get("product_root") != str(product_root)
        or runtime.get("version") != RUNTIME_VERSION
    ):
        return False
    try:
        with urllib.request.urlopen(
            runtime["url"] + "/api/health", timeout=0.5
        ) as response:
            payload = json.loads(response.read())
            return (
                response.status == 200
                and payload.get("product_root") == str(product_root)
                and payload.get("version") == RUNTIME_VERSION
            )
    except (
        OSError,
        KeyError,
        ValueError,
        json.JSONDecodeError,
        urllib.error.URLError,
    ):
        return False


def markdown_section(body: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return ""
    value = re.sub(r"\s+", " ", match.group(1)).strip()
    return value.removeprefix("-").strip()


def read_slice(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", text, re.DOTALL)
    if not match:
        raise ArtifactError(f"Slice requires YAML frontmatter: {path}")
    header = parse_yaml(match.group(1))
    body = match.group(2)
    slice_id = str(header.get("slice_id") or path.stem)
    return {
        "id": slice_id,
        "initiative_id": header.get("initiative_id"),
        "title": str(header.get("title") or slice_id),
        "status": str(header.get("status") or "UNKNOWN"),
        "priority": str(header.get("priority") or "UNSET"),
        "order": header.get("order"),
        "dependencies": header.get("dependencies") or [],
        "capability_family": header.get("capability_family"),
        "prototype_checkpoint": header.get("prototype_checkpoint"),
        "promotion_map": header.get("promotion_map"),
        "approved_at": header.get("approved_at"),
        "approved_by": header.get("approved_by"),
        "outcome": markdown_section(body, "Capability outcome"),
        "story_count": len(re.findall(r"^### US-[A-Za-z0-9-]+ — ", body, re.MULTILINE)),
        "test_count": len(
            re.findall(r"^### TEST-[A-Za-z0-9-]+ — ", body, re.MULTILINE)
        ),
        "file": path.name,
    }


def slice_summaries(base: Path) -> tuple[list[dict[str, Any]], list[str]]:
    result: list[dict[str, Any]] = []
    diagnostics: list[str] = []
    paths = sorted((base / "slices").glob("*.md")) if (base / "slices").exists() else []
    for path in paths:
        try:
            result.append(read_slice(path))
        except (ArtifactError, OSError) as error:
            diagnostics.append(str(error))
    result.sort(
        key=lambda item: (item.get("order") is None, item.get("order") or 0, item["id"])
    )
    return result, diagnostics


def state(product_root: Path) -> dict[str, Any]:
    base = product_root / "docs" / "solo-founder"
    truth_path = base / "canonical-truth.yaml"
    truth = read_yaml(truth_path)
    ledger = read_yaml(base / "product-ledger.yaml")
    validate_truth(truth)
    validate_ledger(ledger)
    slices, diagnostics = slice_summaries(base)
    truth_items = [item for layer in LAYERS for item in truth["truth"][layer]]
    work = ledger["work"]
    issues = ledger["issues"]
    active_work = [
        item for item in work if item["status"] not in TERMINAL_WORK_STATUSES
    ]
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "layers": LAYERS,
        "truth": truth,
        "ledger": ledger,
        "slices": slices,
        "diagnostics": diagnostics,
        "file_hash": sha256_file(truth_path),
        "counts": {
            "approved": sum(item["status"] == "APPROVED" for item in truth_items),
            "proposed": sum(item["status"] == "PROPOSED" for item in truth_items),
            "slices": len(slices),
            "work": len(work),
            "active_work": len(active_work),
            "blocked_work": sum(item["status"] == "BLOCKED" for item in work),
            "direct_work": sum(
                item.get("execution") == "DIRECT" for item in active_work
            ),
            "delegated_work": sum(
                item.get("execution") == "DELEGATED" for item in active_work
            ),
            "issues": len(issues),
        },
    }


class Handler(BaseHTTPRequestHandler):
    product_root: Path

    def send_json(self, value: Any, status: int = 200) -> None:
        payload = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_static(self, name: str, content_type: str) -> None:
        path = DASHBOARD_ROOT / name
        payload = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        request_path = urlparse(self.path).path
        try:
            if request_path == "/api/health":
                self.send_json(
                    {
                        "ok": True,
                        "product_root": str(self.product_root),
                        "version": RUNTIME_VERSION,
                    }
                )
            elif request_path == "/api/state":
                self.send_json(state(self.product_root))
            elif request_path in STATIC_FILES:
                self.send_static(*STATIC_FILES[request_path])
            else:
                self.send_json({"error": "Not found"}, 404)
        except (ArtifactError, OSError) as error:
            self.send_json({"error": str(error)}, 422)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/truth/approve":
            self.send_json({"error": "Not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 65536:
                raise ValueError("Request body is too large")
            body = json.loads(self.rfile.read(length) or b"{}")
            item = approve_truth(
                self.product_root,
                str(body.get("id") or ""),
                str(body.get("file_hash") or ""),
            )
            self.send_json({"approved": item})
        except (ArtifactError, OSError, ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.CONFLICT)

    def log_message(self, _format: str, *_args: object) -> None:
        return


def serve(product_root: Path) -> int:
    handler = type("ProjectHandler", (Handler,), {"product_root": product_root})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    url = f"http://127.0.0.1:{server.server_port}"
    path = runtime_path(product_root)
    path.write_text(
        json.dumps(
            {
                "pid": os.getpid(),
                "url": url,
                "product_root": str(product_root),
                "version": RUNTIME_VERSION,
            }
        ),
        encoding="utf-8",
    )
    print(url, flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        if path.exists():
            path.unlink()
    return 0


def ensure(product_root: Path) -> int:
    path = runtime_path(product_root)
    existing = read_runtime(path)
    if healthy(existing, product_root):
        print(existing["url"])
        return 0
    if existing and existing.get("pid"):
        try:
            os.kill(int(existing["pid"]), 15)
        except (ProcessLookupError, ValueError):
            pass
    if path.exists():
        path.unlink()
    subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), str(product_root), "--serve"],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    deadline = time.time() + 5
    while time.time() < deadline:
        current = read_runtime(path)
        if healthy(current, product_root):
            print(current["url"])
            return 0
        time.sleep(0.05)
    print("ERROR: dashboard did not start", file=sys.stderr)
    return 1


def stop(product_root: Path) -> int:
    path = runtime_path(product_root)
    runtime = read_runtime(path)
    if runtime and runtime.get("pid"):
        try:
            os.kill(int(runtime["pid"]), 15)
        except (ProcessLookupError, ValueError):
            pass
    if path.exists():
        path.unlink()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product_root", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ensure", action="store_true")
    group.add_argument("--serve", action="store_true")
    group.add_argument("--stop", action="store_true")
    args = parser.parse_args()
    root = args.product_root.resolve()
    if args.serve:
        return serve(root)
    if args.stop:
        return stop(root)
    return ensure(root)


if __name__ == "__main__":
    sys.exit(main())
