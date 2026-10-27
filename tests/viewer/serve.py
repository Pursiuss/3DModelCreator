"""A local 3D model viewer for the skill's output: open http://localhost:8765 to turn, zoom and inspect any .glb.

usage: python tests/viewer/serve.py [--port 8765]
Serves the viewer page and every .glb under the kit folder and the test workspace (../penguin-skill-test), listed
newest first at /models.json. Nothing is written anywhere.
"""
import argparse, http.server, json, os, socketserver, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(os.path.dirname(HERE))
ROOTS = {"kit": KIT, "test": os.path.join(os.path.dirname(KIT), "penguin-skill-test")}
SKIP = {".venv", ".venv-skill", ".git", "__pycache__", "selfcheck"}


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


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.unquote(urllib.parse.urlparse(self.path).path)
        if path in ("/", "/index.html"): return self.send_file(os.path.join(HERE, "index.html"), "text/html")
        if path == "/models.json":
            body = json.dumps(models()).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body); return
        parts = path.strip("/").split("/", 1)
        if len(parts) == 2 and parts[0] in ROOTS and parts[1].endswith(".glb"):
            root = os.path.realpath(ROOTS[parts[0]]); p = os.path.realpath(os.path.join(root, parts[1]))
            if p.startswith(root + os.sep) and os.path.isfile(p): return self.send_file(p, "model/gltf-binary")
        self.send_error(404)

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
