#!/usr/bin/env python3
"""bright studio: browse, view, edit and rebuild every file in this repository.

Start it from the repository folder:

    python3 studio/bright_studio.py

It opens http://127.0.0.1:8765 in your browser. Only your own computer can reach
it. Press Ctrl+C in the terminal to stop it.

Needs only Python 3.8+. The "Rebuild" buttons also need Node.js with Playwright
(boxes, PDF) and pptxgenjs + sharp (PowerPoint); see README.md.
"""
import argparse
import json
import mimetypes
import secrets
import shutil
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
PAGE = Path(__file__).resolve().parent / "studio.html"
TOKEN = secrets.token_urlsafe(24)          # blocks other websites from calling this server
HIDDEN = {".git", "__pycache__", "node_modules", ".DS_Store"}
TEXT_EXT = {".md", ".txt", ".py", ".js", ".json", ".html", ".css", ".svg", ".csv", ".yml", ".yaml", ".gitignore", ""}
MAX_TEXT = 2_000_000

# Fixed list of rebuild tasks. Nothing else can be run from the page.
TASKS = {
    "boxes": {
        "label": "Rebuild box labels",
        "steps": [["python3", "packaging/build_cartons.py"], ["node", "packaging/render.js"]],
    },
    "costs": {
        "label": "Rebuild cost study",
        "steps": [["python3", "finance/cost_model.py"], ["python3", "finance/build_pdf.py"],
                  ["node", "finance/render_pdf.js"], ["node", "finance/build_pptx.js"]],
    },
}

mimetypes.add_type("text/markdown", ".md")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx")


def safe_path(rel, must_exist=True):
    """Resolve a repo-relative path, refusing anything outside the repo or inside .git."""
    if not rel or "\x00" in rel:
        raise ValueError("No file given.")
    p = (ROOT / rel).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise ValueError("That path is outside the project folder.")
    if ".git" in p.relative_to(ROOT).parts:
        raise ValueError("Files inside .git can't be opened here.")
    if must_exist and not p.exists():
        raise ValueError(f"{rel} doesn't exist.")
    return p


def tree():
    files = []
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT)
        if any(part in HIDDEN for part in rel.parts) or not p.is_file():
            continue
        files.append({"path": rel.as_posix(), "size": p.stat().st_size, "modified": p.stat().st_mtime,
                      "text": p.suffix.lower() in TEXT_EXT or p.name == ".gitignore"})
    return files


def run(cmd, timeout=600):
    exe = shutil.which(cmd[0])
    if not exe:
        return 127, f"'{cmd[0]}' isn't installed or isn't on your PATH.\n"
    try:
        r = subprocess.run([exe] + cmd[1:], cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, f"Stopped after {timeout} seconds.\n"


def git_status():
    if not (ROOT / ".git").exists():
        return {"available": False}
    code, branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    _, out = run(["git", "status", "--porcelain=v1", "-uall"])
    _, ahead = run(["git", "rev-list", "--count", "@{u}..HEAD"])
    changes = []
    for line in out.splitlines():
        if len(line) > 3:
            changes.append({"state": line[:2].strip() or "?", "path": line[3:].strip().strip('"')})
    return {"available": code == 0, "branch": branch.strip(), "changes": changes,
            "unpushed": int(ahead.strip()) if ahead.strip().isdigit() else None}


class Handler(BaseHTTPRequestHandler):
    server_version = "brightstudio/1"

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet

    def send(self, code, body, ctype="application/json", extra=None):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def authorized(self):
        q = parse_qs(urlparse(self.path).query)
        return self.headers.get("X-Studio-Token") == TOKEN or q.get("t", [""])[0] == TOKEN

    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        try:
            if url.path == "/":
                html = PAGE.read_text(encoding="utf-8").replace("__STUDIO_TOKEN__", TOKEN)
                return self.send(200, html.encode(), "text/html; charset=utf-8")
            if not self.authorized():
                return self.send(403, {"error": "Reload the page to reconnect."})
            if url.path == "/api/tree":
                return self.send(200, {"root": ROOT.name, "files": tree(),
                                       "tasks": {k: v["label"] for k, v in TASKS.items()}})
            if url.path == "/api/text":
                p = safe_path(q.get("path", [""])[0])
                if p.stat().st_size > MAX_TEXT:
                    raise ValueError("This file is too large to edit here.")
                return self.send(200, {"content": p.read_text(encoding="utf-8", errors="replace")})
            if url.path == "/api/raw":
                p = safe_path(q.get("path", [""])[0])
                ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
                extra = {"Content-Security-Policy": "sandbox"} if ctype == "text/html" else {}
                if q.get("download"):
                    extra["Content-Disposition"] = f'attachment; filename="{p.name}"'
                return self.send(200, p.read_bytes(), ctype, extra)
            if url.path == "/api/git":
                return self.send(200, git_status())
            return self.send(404, {"error": "Not found."})
        except ValueError as e:
            return self.send(400, {"error": str(e)})

    def do_POST(self):
        if not self.authorized():
            return self.send(403, {"error": "Reload the page to reconnect."})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0) or b"{}")
        except json.JSONDecodeError:
            return self.send(400, {"error": "Bad request."})
        path = urlparse(self.path).path
        try:
            if path == "/api/save":
                p = safe_path(body.get("path"))
                p.write_text(body.get("content", ""), encoding="utf-8")
                return self.send(200, {"ok": True})
            if path == "/api/new":
                p = safe_path(body.get("path"), must_exist=False)
                if p.exists():
                    raise ValueError("A file with that name already exists.")
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(body.get("content", ""), encoding="utf-8")
                return self.send(200, {"ok": True})
            if path == "/api/rename":
                src = safe_path(body.get("path"))
                dst = safe_path(body.get("to"), must_exist=False)
                if dst.exists():
                    raise ValueError("A file with that name already exists.")
                dst.parent.mkdir(parents=True, exist_ok=True)
                src.rename(dst)
                return self.send(200, {"ok": True})
            if path == "/api/delete":
                p = safe_path(body.get("path"))
                if not p.is_file():
                    raise ValueError("Only single files can be deleted here.")
                p.unlink()
                return self.send(200, {"ok": True})
            if path == "/api/run":
                task = TASKS.get(body.get("task"))
                if not task:
                    raise ValueError("Unknown task.")
                log, ok = [], True
                for step in task["steps"]:
                    code, out = run(step)
                    log.append(f"$ {' '.join(step)}\n{out}")
                    if code != 0:
                        ok = False
                        log.append(f"Stopped: this step failed (exit code {code}).")
                        break
                return self.send(200, {"ok": ok, "log": "\n".join(log)})
            if path == "/api/commit":
                msg = (body.get("message") or "").strip()
                if not msg:
                    raise ValueError("Write a short note describing your changes.")
                files = body.get("files") or []
                for f in files:
                    safe_path(f, must_exist=False)
                code, out = run(["git", "add", "-A", "--"] + (files or ["."]))
                if code == 0:
                    code, out2 = run(["git", "commit", "-m", msg])
                    out += out2
                return self.send(200, {"ok": code == 0, "log": out})
            if path == "/api/push":
                branch = git_status().get("branch", "")
                code, out = run(["git", "push", "-u", "origin", branch], timeout=120)
                return self.send(200, {"ok": code == 0, "log": out})
            return self.send(404, {"error": "Not found."})
        except ValueError as e:
            return self.send(400, {"error": str(e)})
        except OSError as e:
            return self.send(500, {"error": f"Couldn't complete that: {e.strerror or e}"})


def main():
    ap = argparse.ArgumentParser(description="Browse, view, edit and rebuild the bright gum files.")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true", help="don't open a browser window")
    a = ap.parse_args()
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    except OSError:
        sys.exit(f"Port {a.port} is busy. Try: python3 studio/bright_studio.py --port 8766")
    url = f"http://127.0.0.1:{a.port}/"
    print(f"bright studio is running at {url}\nProject folder: {ROOT}\nPress Ctrl+C to stop.")
    if not a.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
