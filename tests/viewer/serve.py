"""A local 3D model viewer for the skill's output: open http://localhost:8765 to turn, zoom and inspect any .glb.

usage: python tests/viewer/serve.py [--port 8765]
Serves the viewer page; every .glb under the kit folder and the test projects folder (../TEST-KIT), listed newest
first; and any other .glb on this computer that is opened with the page's "Open file..." button (a Windows file
dialog, shown by this server). Files opened that way are remembered in recent.json next to this script (the
history; local to this computer, not in git), newest first, at most RECENT_MAX of them.

The server answers only on this computer (127.0.0.1). It serves .glb files and nothing else, and the requests that
open a dialog or read a file anywhere on the computer must carry the header the viewer page sends (X-Viewer), which
another web page cannot add without the server's permission. Nothing is written except recent.json.
"""
import argparse, http.server, json, os, socketserver, threading, time, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(os.path.dirname(HERE))
ROOTS = {"kit": KIT, "test": os.path.join(os.path.dirname(KIT), "TEST-KIT")}
SKIP = {".venv", ".venv-skill", ".git", "__pycache__", "selfcheck"}
RECENT = os.path.join(HERE, "recent.json")
RECENT_MAX = 30
LOCK = threading.Lock()                                    # one file dialog, one history write at a time


def models():
    out = []
    for name, root in ROOTS.items():
        for d, dirs, files in os.walk(root):
            dirs[:] = [x for x in dirs if x not in SKIP]
            for f in files:
                if f.endswith(".glb"):
                    p = os.path.join(d, f)
                    out.append({"url": f"/{name}/" + os.path.relpath(p, root).replace(os.sep, "/"),
                                "label": f"{name}: " + os.path.relpath(p, root).replace(os.sep, "/"),
                                "mtime": os.path.getmtime(p)})
    return sorted(out, key=lambda m: -m["mtime"])


def is_glb(p):
    return p.lower().endswith(".glb") and os.path.isfile(p)


def recent():
    """The history: [{"path", "opened" (time), "missing"}], newest first."""
    try: items = json.load(open(RECENT, encoding="utf-8"))
    except (OSError, ValueError): items = []
    return [dict(r, missing=not is_glb(r["path"])) for r in items if isinstance(r, dict) and "path" in r]


def save_recent(items):
    tmp = RECENT + ".tmp"
    json.dump([{"path": r["path"], "opened": r["opened"]} for r in items[:RECENT_MAX]], open(tmp, "w", encoding="utf-8"), indent=1)
    os.replace(tmp, RECENT)


def remember(path):
    with LOCK:
        key = os.path.normcase(path)
        save_recent([{"path": path, "opened": time.time()}] + [r for r in recent() if os.path.normcase(r["path"]) != key])


def forget(path=None):
    with LOCK:
        save_recent([] if path is None else [r for r in recent() if os.path.normcase(r["path"]) != os.path.normcase(path)])


def pick():
    """A Windows file dialog for a .glb, starting where the last opened file was; its path, or None."""
    import tkinter as tk
    from tkinter import filedialog
    start = next((os.path.dirname(r["path"]) for r in recent() if os.path.isdir(os.path.dirname(r["path"]))), KIT)
    with LOCK:
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        try:
            p = filedialog.askopenfilename(parent=root, title="Open a 3D model", initialdir=start,
                                           filetypes=[("glTF binary model", "*.glb"), ("All files", "*.*")])
        finally:
            root.destroy()
    return os.path.normpath(p) if p else None


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); path = urllib.parse.unquote(u.path)
        if path in ("/", "/index.html"): return self.send_file(os.path.join(HERE, "index.html"), "text/html")
        if path == "/models.json": return self.send_json(models())
        if path == "/recent.json": return self.send_json(recent())
        if path == "/file":                                    # any .glb on this computer, by its full path
            if not self.from_viewer(): return self.send_error(403)
            p = os.path.normpath(urllib.parse.parse_qs(u.query).get("path", [""])[0])
            if not os.path.isabs(p) or not is_glb(p): return self.send_error(404, "no such .glb file")
            remember(p); return self.send_file(p, "model/gltf-binary")
        parts = path.strip("/").split("/", 1)
        if len(parts) == 2 and parts[0] in ROOTS and parts[1].endswith(".glb"):
            root = os.path.realpath(ROOTS[parts[0]]); p = os.path.realpath(os.path.join(root, parts[1]))
            if p.startswith(root + os.sep) and os.path.isfile(p): return self.send_file(p, "model/gltf-binary")
        self.send_error(404)

    def do_POST(self):
        u = urllib.parse.urlparse(self.path); path = urllib.parse.unquote(u.path)
        if not self.from_viewer(): return self.send_error(403)
        if path == "/pick":                                    # show the file dialog
            p = pick()
            return self.send_json({"path": p if p and is_glb(p) else None, "chosen": bool(p)})
        if path == "/forget":                                  # ?path=... one entry; no path: the whole history
            p = urllib.parse.parse_qs(u.query).get("path", [None])[0]
            forget(p); return self.send_json(recent())
        self.send_error(404)

    def from_viewer(self):
        """Only the viewer page sends this header; a request from another web site cannot (it would need a CORS
        preflight that this server never answers), so it cannot open dialogs or read files here."""
        return self.headers.get("X-Viewer") == "1"

    def send_json(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body)

    def send_file(self, p, ctype):
        data = open(p, "rb").read()
        self.send_response(200); self.send_header("Content-Type", ctype); self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def log_message(self, *a): pass


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--port", type=int, default=8765); a = ap.parse_args()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", a.port), Handler) as s:
        print(f"model viewer at http://localhost:{a.port}", flush=True); s.serve_forever()


if __name__ == "__main__":
    main()
