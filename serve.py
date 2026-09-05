#!/usr/bin/env python3
"""Static server for the portfolio page, plus the tuning panel's save endpoint.

`python3 -m http.server` is enough to view the page, but the panel's SAVE TO
CODE button needs somewhere to POST to. This is that, and nothing else: it
serves the directory exactly as http.server does, and adds one route.

  POST /__tune/save   body: the TUNE object as JSON
                      effect: rewrites the `const TUNE = { ... };` block in
                              index.html in place, preserving key order and
                              the comment above it.

Run it from the portfolio directory:

    python3 serve.py            # http://127.0.0.1:5180
    python3 serve.py 5199       # a different port

Without this server the panel still works — Save falls back to copying the
values to the clipboard.
"""

import http.server
import json
import math
import os
import re
import socketserver
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"

# the opening line, everything up to the closing brace, and the semicolon
TUNE_RE = re.compile(r"(const TUNE = \{)(.*?)(\n\};)", re.S)


def format_value(value, template):
    """Write the value the way the file already writes that key.

    JSON has no float/int distinction to speak of — a slider sitting on 1.00
    arrives here as the integer 1, and formatting off the incoming type alone
    rewrites `envIntensity: 1.00` as `envIntensity: 1`. So the existing text
    for the key decides: if it had a decimal point, keep that many places.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if "." in template:
        return f"{float(value):.{len(template.split('.')[1])}f}"
    return str(int(round(float(value))))


def write_tune(values):
    if not isinstance(values, dict):
        raise ValueError("expected a JSON object of tuning values")
    src = INDEX.read_text(encoding="utf-8")
    match = TUNE_RE.search(src)
    if not match:
        raise ValueError("could not find the `const TUNE = { ... };` block in index.html")

    # Replace supplied numeric literals without losing omitted settings,
    # comments or settings added since the browser tab loaded.
    value_re = re.compile(r"^(\s*(\w+)\s*:\s*)(-?(?:\d+(?:\.\d*)?|\.\d+))", re.M)
    known = {m.group(2) for m in value_re.finditer(match.group(2))}
    updates = known.intersection(values)
    if not updates:
        raise ValueError("no recognized tuning values supplied")
    for key in updates:
        value = values[key]
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"{key} must be a finite number")

    def replace_value(m):
        key = m.group(2)
        if key not in updates:
            return m.group(0)
        return m.group(1) + format_value(values[key], m.group(3))

    body = value_re.sub(replace_value, match.group(2))
    updated = src[:match.start(2)] + body + src[match.end(2):]

    # Stage alongside the original so replacement is atomic. Failed writes
    # leave the source intact, and the original file permissions survive.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=INDEX.parent, prefix=".tune-",
                                         delete=False) as staged:
            temporary = Path(staged.name)
            os.fchmod(staged.fileno(), INDEX.stat().st_mode & 0o777)
            staged.write(updated)
        os.replace(temporary, INDEX)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return len(updates)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HERE), **kwargs)

    def do_POST(self):  # noqa: N802 — http.server's naming
        if self.path != "/__tune/save":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("content-length", 0))
            values = json.loads(self.rfile.read(length) or b"{}")
            count = write_tune(values)
        except Exception as err:  # report it to the panel rather than 500-ing silently
            body = str(err).encode()
            self.send_response(400 if isinstance(err, ValueError) else 500)
            self.send_header("content-type", "text/plain")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            print(f"[tune] save failed: {err}", file=sys.stderr)
            return
        body = f"wrote {count} values".encode()
        self.send_response(200)
        self.send_header("content-type", "text/plain")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        print(f"[tune] wrote {count} values into index.html")

    def end_headers(self):
        # the page is edited constantly while tuning; never serve it from cache
        self.send_header("cache-control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # the save line above is the only output worth having


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5180
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        print(f"portfolio  → http://127.0.0.1:{port}/")
        print(f"tuning     → http://127.0.0.1:{port}/?tune=1")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
