#!/usr/bin/env python3
"""Serve the local Solo Founder dashboard and Human Truth approvals."""

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
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from solo_founder_core import (
    LAYERS,
    ArtifactError,
    approve_truth,
    read_yaml,
    sha256_file,
    validate_ledger,
    validate_truth,
)

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Solo Founder</title>
<style>
:root{color-scheme:light dark;--bg:#f6f5fb;--panel:#fff;--text:#242334;--muted:#6e6a7d;--line:#dedbe9;--brand:#5b5bd6;--ok:#16855b;--pending:#a75b00}*{box-sizing:border-box}body{margin:0;font:15px/1.5 ui-sans-serif,system-ui;background:var(--bg);color:var(--text)}header{padding:28px max(24px,calc((100% - 1120px)/2));background:linear-gradient(120deg,#36368c,#6e55c7);color:#fff}header h1{margin:0 0 4px;font-size:28px}header p{margin:0;opacity:.82}.shell{max-width:1120px;margin:0 auto;padding:24px}.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:24px}.metric,.panel,.card{background:var(--panel);border:1px solid var(--line);border-radius:14px}.metric{padding:16px}.metric b{display:block;font-size:20px}.metric span,.muted{color:var(--muted)}.panel{padding:20px;margin:16px 0}.panel h2{margin:0 0 14px}.layer{margin-top:22px}.layer h3{font-size:13px;letter-spacing:.06em;color:var(--muted);margin:0 0 8px}.cards{display:grid;gap:10px}.card{padding:14px}.row{display:flex;gap:12px;align-items:flex-start;justify-content:space-between}.badge{display:inline-block;padding:3px 8px;border-radius:999px;font-size:12px;font-weight:700}.approved{background:#dff4ea;color:var(--ok)}.proposed{background:#fff0d5;color:var(--pending)}button{border:0;border-radius:9px;background:var(--brand);color:#fff;padding:9px 12px;font-weight:700;cursor:pointer}button:disabled{opacity:.5}.evidence{font-size:12px;color:var(--muted);margin-top:8px}.empty{color:var(--muted);padding:8px 0}.error{background:#ffe7e7;color:#8d1d1d;padding:12px;border-radius:10px}.work{display:grid;grid-template-columns:110px 1fr 130px;gap:10px;padding:10px 0;border-top:1px solid var(--line)}@media(max-width:640px){.work{grid-template-columns:1fr}.row{display:block}.row button{margin-top:10px}}
@media(prefers-color-scheme:dark){:root{--bg:#171621;--panel:#222130;--text:#f2f0f8;--muted:#aaa5bb;--line:#3a374b}}
</style>
</head>
<body>
<header><h1>Solo Founder</h1><p>Canonical Truth and product delivery visibility</p></header>
<main class="shell"><div id="app">Loading…</div></main>
<script>
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path,options){const r=await fetch(path,options);const data=await r.json();if(!r.ok)throw new Error(data.error||'Request failed');return data}
function render(data){const t=data.truth, l=data.ledger, current=l.current||{}, work=l.work||[];window.truthItems={};let html=`<section class="summary"><div class="metric"><span>Mode</span><b>${esc(current.mode)}</b></div><div class="metric"><span>Current Layer</span><b>${esc(current.layer)}</b></div><div class="metric"><span>Approved Truth</span><b>${data.counts.approved}</b></div><div class="metric"><span>Proposed Truth</span><b>${data.counts.proposed}</b></div></section>`;html+=`<section class="panel"><h2>Canonical Truth</h2>`;for(const layer of data.layers){const items=t.truth[layer]||[];html+=`<div class="layer"><h3>${esc(layer.replaceAll('_',' '))}</h3><div class="cards">`;if(!items.length)html+=`<div class="empty">No Truth recorded.</div>`;for(const item of items){window.truthItems[item.id]={...item,layer};const proposed=item.status==='PROPOSED';html+=`<article class="card"><div class="row"><div><span class="badge ${proposed?'proposed':'approved'}">${esc(item.status)}</span><h4>${esc(item.title)}</h4><div>${esc(item.statement)}</div><div class="evidence">Affected: ${esc((item.affected_layers||[]).join(', ')||'none')} · Evidence: ${esc((item.evidence||[]).join(', ')||'none')}</div></div>${proposed?`<button onclick="approve('${item.id}')">Approve Truth</button>`:''}</div></article>`}html+=`</div></div>`}html+=`</section><section class="panel"><h2>Active work</h2>`;const active=work.filter(x=>!['DONE','CANCELLED'].includes(x.status));if(!active.length)html+=`<div class="empty">No active work.</div>`;for(const item of active){const handoff=item.execution==='DELEGATED'?`${item.handoff_type||'HANDOFF'} · ${item.handoff_consumed_at?'consumed':item.handoff_submitted_at?'awaiting PM':'awaiting submission'}`:'PM direct';html+=`<div class="work"><b>${esc(item.status)}</b><span>${esc(item.title)}<br><small class="muted">${esc(item.id)} · ${esc(item.classification)} · ${esc(item.workstream)} · ${esc(item.execution)}</small></span><span>${esc(item.role||'LEGACY')}<br><small class="muted">${esc(item.owner)} · ${esc(handoff)}</small></span></div>`}html+=`</section>`;document.querySelector('#app').innerHTML=html;window.fileHash=data.file_hash}
async function load(){try{render(await api('/api/state'))}catch(e){document.querySelector('#app').innerHTML=`<div class="error">${esc(e.message)}</div>`}}
async function approve(id){const item=window.truthItems[id];if(!item)return;const message=`Approve this as Canonical Truth?\n\nLayer: ${item.layer}\nTruth: ${item.statement}\nReplaces: ${item.replaces||'none'}\nAffected Layers: ${(item.affected_layers||[]).join(', ')||'none'}`;if(!confirm(message))return;try{await api('/api/truth/approve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,file_hash:window.fileHash})});await load()}catch(e){alert(e.message);await load()}}
load();
</script>
</body></html>"""


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
    if not runtime or runtime.get("product_root") != str(product_root):
        return False
    try:
        with urllib.request.urlopen(
            runtime["url"] + "/api/health", timeout=0.5
        ) as response:
            return response.status == 200
    except (OSError, KeyError, ValueError, urllib.error.URLError):
        return False


def slice_summaries(base: Path) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for path in (
        sorted((base / "slices").glob("*.md")) if (base / "slices").exists() else []
    ):
        text = path.read_text(encoding="utf-8")
        title = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", text, re.MULTILINE)
        status = re.search(r"^status:\s*([A-Z_]+)\s*$", text, re.MULTILINE)
        result.append(
            {
                "file": path.name,
                "title": title.group(1) if title else path.stem,
                "status": status.group(1) if status else "UNKNOWN",
            }
        )
    return result


def state(product_root: Path) -> dict[str, Any]:
    base = product_root / "docs" / "solo-founder"
    truth_path = base / "canonical-truth.yaml"
    truth = read_yaml(truth_path)
    ledger = read_yaml(base / "product-ledger.yaml")
    validate_truth(truth)
    validate_ledger(ledger)
    approved = sum(
        item["status"] == "APPROVED"
        for layer in LAYERS
        for item in truth["truth"][layer]
    )
    proposed = sum(
        item["status"] == "PROPOSED"
        for layer in LAYERS
        for item in truth["truth"][layer]
    )
    return {
        "layers": LAYERS,
        "truth": truth,
        "ledger": ledger,
        "slices": slice_summaries(base),
        "file_hash": sha256_file(truth_path),
        "counts": {"approved": approved, "proposed": proposed},
    }


class Handler(BaseHTTPRequestHandler):
    product_root: Path

    def send_json(self, value: Any, status: int = 200) -> None:
        payload = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        try:
            if self.path == "/api/health":
                self.send_json({"ok": True})
            elif self.path == "/api/state":
                self.send_json(state(self.product_root))
            elif self.path in {"/", "/index.html"}:
                payload = HTML.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            else:
                self.send_json({"error": "Not found"}, 404)
        except (ArtifactError, OSError) as error:
            self.send_json({"error": str(error)}, 422)

    def do_POST(self) -> None:
        if self.path != "/api/truth/approve":
            self.send_json({"error": "Not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
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
        json.dumps({"pid": os.getpid(), "url": url, "product_root": str(product_root)}),
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
        except ProcessLookupError:
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
