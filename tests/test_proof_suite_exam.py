"""Calibration of the Shortlist exam (evals/proof-suite/briefs/shortlist/exam/).

The exam is a measurement instrument: before it grades a pipeline's product it must score a
contract-perfect server with full marks (19/19 in exam v2) and fail a broken server on exactly
the checks that cover the breakage. A small stdlib HTTP server implementing the brief's wire
contract plays both roles.
"""

import json
import re
import subprocess
import sys
import threading
import unittest
import urllib.parse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from helpers import EVALS_DIR, PY, FrameworkTestCase

EXAM = EVALS_DIR / "proof-suite" / "briefs" / "shortlist" / "exam" / "shortlist_exam.py"
CODE_RE = re.compile(r"^[A-Za-z0-9_-]{4,32}$")
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


class FakeShortlist(ThreadingHTTPServer):
    """In-memory Shortlist honouring the frozen brief; `broken` selects contract violations."""

    def __init__(self, broken=()):
        super().__init__(("127.0.0.1", 0), Handler)
        self.links = {}
        self.lock = threading.RLock()  # do_POST holds it while new_code() takes it again
        self.broken = set(broken)
        self.counter = 0

    def new_code(self):
        with self.lock:
            self.counter += 1
            n = self.counter * 7919 + 100000
        out = ""
        for _ in range(6):
            out = ALPHABET[n % 62] + out
            n //= 62
        return out


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_):
        pass

    # --- helpers ---
    def send_json(self, status, payload, ctype="application/json", extra=None):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def problem(self, status, title, errors=None):
        payload = {"type": "about:blank", "title": title, "status": status}
        if errors is not None:
            payload["errors"] = errors
        self.send_json(status, payload, ctype="application/problem+json")

    def view(self, link):
        return {"code": link["code"], "url": link["url"], "clickCount": link["clicks"],
                "lastClickedAt": link["last"]}

    def read_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b""
        try:
            return json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError:
            return None

    # --- routes ---
    def do_POST(self):
        if self.path != "/api/links":
            return self.problem(404, "Not Found")
        body = self.read_body()
        if body is None:
            return self.problem(400, "Bad Request", errors={"body": ["malformed JSON"]})
        errors = {}
        url = body.get("url")
        parts = urllib.parse.urlsplit(url) if isinstance(url, str) else None
        if not parts or parts.scheme not in ("http", "https") or not parts.netloc:
            errors["url"] = ["must be an absolute http(s) URL"]
        custom = body.get("customCode")
        if custom is not None:
            if custom.lower() == "api":
                errors["customCode"] = ["reserved"]
            elif not CODE_RE.match(custom):
                errors["customCode"] = ["4-32 chars of [A-Za-z0-9_-]"]
        if errors:
            return self.problem(400, "One or more validation errors occurred.", errors=errors)
        srv = self.server
        with srv.lock:
            code = custom or srv.new_code()
            if code in srv.links and "no_conflict" not in srv.broken:
                return self.problem(409, "Conflict")
            srv.links[code] = {"code": code, "url": url, "clicks": 0, "last": None}
            link = dict(srv.links[code])
        self.send_json(201, self.view(link), extra={"Location": f"/{code}"})

    def do_GET(self):
        srv = self.server
        if self.path == "/api/links":
            with srv.lock:
                items = [self.view(l) for l in srv.links.values()]
            return self.send_json(200, items)
        if self.path.startswith("/api/links/"):
            code = self.path[len("/api/links/"):]
            with srv.lock:
                link = srv.links.get(code)
            if not link:
                return self.problem(404, "Not Found")
            return self.send_json(200, self.view(link))
        code = self.path.lstrip("/")
        with srv.lock:
            link = srv.links.get(code)
            if link:
                if "lost_clicks" in srv.broken:
                    link["clicks"] = 1
                else:
                    link["clicks"] += 1
                link["last"] = datetime.now(timezone.utc).isoformat()
                url = link["url"]
        if not link:
            return self.problem(404, "Not Found")
        self.send_response(302)
        self.send_header("Location", url)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_DELETE(self):
        if not self.path.startswith("/api/links/"):
            return self.problem(404, "Not Found")
        code = self.path[len("/api/links/"):]
        with self.server.lock:
            existed = self.server.links.pop(code, None) is not None
        if not existed:
            return self.problem(404, "Not Found")
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()


class ExamCalibration(FrameworkTestCase):
    def serve(self, broken=()):
        srv = FakeShortlist(broken)
        thread = threading.Thread(target=srv.serve_forever, daemon=True)
        thread.start()
        # cleanups run last-in first-out: stop serving, then close the socket
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        return f"http://127.0.0.1:{srv.server_address[1]}"

    def run_exam(self, base):
        out = self.tmp / "exam.json"
        proc = subprocess.run([PY, str(EXAM), "--base-url", base, "--json", str(out),
                               "--wait", "10", "--concurrency", "30"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
        verdict = json.loads(out.read_text(encoding="utf-8"))
        return proc, verdict

    def test_contract_perfect_server_scores_full_marks(self):
        proc, verdict = self.run_exam(self.serve())
        failed = [c for c in verdict["checks"] if c["status"] != "PASS"]
        self.assertEqual(failed, [], proc.stdout)
        self.assertEqual((verdict["passed"], verdict["total"]), (19, 19))
        self.assertEqual(verdict["exam_version"], 2)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("exam: 19/19 passed", proc.stdout)

    def test_lost_increments_fail_exactly_the_click_checks(self):
        proc, verdict = self.run_exam(self.serve(broken={"lost_clicks"}))
        failed = sorted(c["id"] for c in verdict["checks"] if c["status"] == "FAIL")
        self.assertEqual(failed, ["E07", "E08"], proc.stdout)
        self.assertEqual(proc.returncode, 1)

    def test_missing_conflict_fails_exactly_the_namespace_checks(self):
        proc, verdict = self.run_exam(self.serve(broken={"no_conflict"}))
        failed = sorted(c["id"] for c in verdict["checks"] if c["status"] == "FAIL")
        self.assertEqual(failed, ["E04", "E16"], proc.stdout)

    def test_unreachable_server_exits_two(self):
        proc = subprocess.run([PY, str(EXAM), "--base-url", "http://127.0.0.1:9", "--wait", "1"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("did not answer", proc.stderr)

    def test_exam_is_stdlib_only(self):
        """The exam runs on any machine with Python; it must not grow dependencies."""
        stdlib = getattr(sys, "stdlib_module_names", None)
        if stdlib is None:
            self.skipTest("sys.stdlib_module_names needs Python 3.10+")
        src = EXAM.read_text(encoding="utf-8")
        imports = re.findall(r"^(?:import|from)\s+([A-Za-z_][\w.]*)", src, re.M)
        self.assertTrue(imports)
        for mod in imports:
            top = mod.split(".")[0]
            self.assertIn(top, stdlib, f"non-stdlib import: {mod}")


if __name__ == "__main__":
    unittest.main()
