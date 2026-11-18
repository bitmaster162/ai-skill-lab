"""Measure the four candidate guide articles at mobile widths in an offline browser."""
import functools
import json
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from html import unescape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from build_conversion_r1 import NEW_GUIDES


class StaticHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        local = Path(super().translate_path(path))
        if not local.exists() and not local.suffix:
            return str(local.with_suffix(".html"))
        return str(local)

    def log_message(self, *_):
        pass


def run(site: Path):
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome and sys.platform == "win32":
        chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not chrome:
        raise RuntimeError("Headless Chrome is required for the mobile guide check")
    routes = [prefix + "/guides/" + slug for prefix in ("", "/en") for slug in NEW_GUIDES]
    probe = """<!doctype html><meta charset="utf-8"><title>Guide layout check</title><main></main><script>
    const results = [];
    const routes = ROUTES;
    const ready = [];
    for (const route of routes) for (const width of [320, 390]) {
      const frame = document.createElement('iframe');
      frame.style.cssText = 'display:block;border:0;height:844px;width:' + width + 'px';
      ready.push(new Promise(resolve => {
        frame.onload = async () => {
          const doc = frame.contentDocument;
          await doc.fonts.ready;
          const tables = [...doc.querySelectorAll('.guideTableWrap')];
          results.push({route, width, viewport: doc.documentElement.clientWidth,
            page: doc.documentElement.scrollWidth, tables: tables.length,
            contained: tables.every(wrap => wrap.clientWidth <= width &&
              wrap.scrollWidth > wrap.clientWidth &&
              frame.contentWindow.getComputedStyle(wrap).overflowX === 'auto')});
          resolve();
        };
      }));
      frame.src = route;
      document.querySelector('main').append(frame);
    }
    Promise.all(ready).then(() => {
      const out = document.createElement('output');
      out.id = 'measurements';
      out.textContent = JSON.stringify(results);
      document.body.append(out);
    });
    </script>""".replace("ROUTES", json.dumps(routes))
    # Serve the harness in memory; authored site bytes and release manifest stay intact.
    class Handler(StaticHandler):
        def do_GET(self):
            if self.path != "/_conversion_layout_probe":
                return super().do_GET()
            data = probe.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(site)))
    with server, tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            completed = subprocess.run([
                chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-first-run",
                "--disable-background-networking", "--disable-default-apps", "--hide-scrollbars",
                "--user-data-dir=" + profile, "--virtual-time-budget=15000", "--dump-dom",
                f"http://127.0.0.1:{server.server_port}/_conversion_layout_probe",
            ], capture_output=True, encoding="utf-8", errors="replace", check=True, timeout=50)
        finally:
            server.shutdown()
            thread.join()
    result = re.search(r'<output id="measurements">(.*?)</output>', completed.stdout)
    if not result:
        raise RuntimeError("Browser did not finish measuring guide pages")
    rows = json.loads(unescape(result[1]))
    if len({(r["route"], r["width"]) for r in rows}) != 8:
        raise ValueError(f"Incomplete mobile coverage: {rows}")
    for row in rows:
        if row["width"] != row["viewport"] or row["page"] != row["viewport"] or row["tables"] != 4 or not row["contained"]:
            raise ValueError(f"Guide mobile layout failed: {row}")
    print("GUIDE_LAYOUT_PASS " + json.dumps(sorted(rows, key=lambda r: (r["route"], r["width"]))))
