#!/usr/bin/env python3
"""External exam for the Shortlist brief: black-box checks of the wire contract.

The agents that build Shortlist never see this file. It probes a RUNNING server and grades
it against the frozen brief (inputs/docs/work-items/FEAT-001-link-shortening-core.md):
acceptance criteria AC-1..AC-4, the edge cases of section 9, and the routing constraint of
section 10. AC-5 (the agents' own test suite) is deliberately not graded here - this exam
exists precisely because self-graded tests are not independent evidence.

Usage:
    python shortlist_exam.py --base-url http://127.0.0.1:5181 [--json exam.json]
                             [--concurrency 50] [--wait 30]

Exit code 0 when every check passes, 1 otherwise. Python 3.8+, standard library only.
The server is expected to start empty (the list check tolerates pre-existing links, the
count checks use codes this run created). Re-running against the same server is safe:
every custom code carries a per-run suffix.
"""

import argparse
import concurrent.futures
import json
import re
import sys
import time
import urllib.error
import urllib.request
import uuid

GENERATED_CODE_RE = re.compile(r"^[A-Za-z0-9]{6}$")
PROBLEM_TYPE = "application/problem+json"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def call(base, method, path, body=None, timeout=10):
    """Return (status, headers, text, json_or_None) without following redirects."""
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base + path, data=data, method=method, headers=headers)
    try:
        resp = OPENER.open(req, timeout=timeout)
        status, hdrs, raw = resp.status, resp.headers, resp.read()
    except urllib.error.HTTPError as exc:
        status, hdrs, raw = exc.code, exc.headers, exc.read()
    text = raw.decode("utf-8", errors="replace") if raw else ""
    parsed = None
    if text.strip():
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
    return status, hdrs, text, parsed


def get(d, key):
    """Case-insensitive key lookup (JSON casing is a project convention, not the contract)."""
    if not isinstance(d, dict):
        return None
    for k, v in d.items():
        if k.lower() == key.lower():
            return v
    return None


def is_problem(status, hdrs, parsed, expected):
    if status != expected:
        return False, f"expected {expected}, got {status}"
    ctype = (hdrs.get("Content-Type") or "").lower()
    if PROBLEM_TYPE not in ctype:
        return False, f"{status} but Content-Type is {ctype!r}, not Problem Details"
    if not isinstance(parsed, dict) or (get(parsed, "status") is None and get(parsed, "title") is None):
        return False, f"{status} Problem Details body lacks status/title"
    return True, f"{status} Problem Details"


def has_validation_error(parsed, field):
    errors = get(parsed, "errors")
    if not isinstance(errors, dict):
        return False, "no 'errors' dictionary in the 400 body"
    if not any(k.lower() == field.lower() for k in errors):
        return False, f"'errors' has keys {sorted(errors)} but no '{field}'"
    return True, f"errors['{field}'] present"


class Exam:
    def __init__(self, base, concurrency):
        self.base = base.rstrip("/")
        self.concurrency = concurrency
        self.run_id = uuid.uuid4().hex[:6]
        self.results = []
        self.created = {}  # label -> (code, url)

    def code(self, label):
        return f"exam-{label}-{self.run_id}"

    def create(self, url, custom=None):
        body = {"url": url}
        if custom is not None:
            body["customCode"] = custom
        return call(self.base, "POST", "/api/links", body)

    def record(self, cid, ac, name, ok, detail):
        self.results.append({"id": cid, "ac": ac, "name": name,
                             "status": "PASS" if ok else "FAIL", "detail": detail})

    def check(self, cid, ac, name, fn):
        try:
            ok, detail = fn()
        except Exception as exc:  # a crash is a failed check, never a crashed exam
            ok, detail = False, f"exception: {exc!r}"
        self.record(cid, ac, name, ok, detail)

    # --- checks ------------------------------------------------------------
    def e01_create_generated(self):
        url = "https://example.com/dashboard"
        status, hdrs, text, body = self.create(url)
        if status != 201:
            return False, f"expected 201, got {status}: {text[:120]}"
        code = get(body, "code")
        if not isinstance(code, str) or not GENERATED_CODE_RE.match(code):
            return False, f"code {code!r} is not a 6-char base62 code"
        if get(body, "url") != url:
            return False, f"url echoed as {get(body, 'url')!r}"
        if get(body, "clickCount") != 0:
            return False, f"clickCount {get(body, 'clickCount')!r} on a fresh link"
        if get(body, "lastClickedAt") is not None:
            return False, f"lastClickedAt {get(body, 'lastClickedAt')!r} before any click"
        self.created["generated"] = (code, url)
        return True, f"201, code={code}"

    def e02_redirect_generated(self):
        code, url = self.created["generated"]
        status, hdrs, _, _ = call(self.base, "GET", f"/{code}")
        if status != 302:
            return False, f"expected 302, got {status}"
        loc = hdrs.get("Location")
        return (loc == url), f"302 Location={loc!r}"

    def e03_create_custom(self):
        custom = self.code("free")
        url = "https://example.com/custom"
        status, _, text, body = self.create(url, custom)
        if status != 201:
            return False, f"expected 201, got {status}: {text[:120]}"
        if get(body, "code") != custom:
            return False, f"code echoed as {get(body, 'code')!r}, wanted {custom!r}"
        self.created["custom"] = (custom, url)
        return True, f"201, code={custom}"

    def e04_taken_custom_is_409(self):
        custom, _ = self.created["custom"]
        status, hdrs, _, body = self.create("https://example.com/other", custom)
        return is_problem(status, hdrs, body, 409)

    def e05_invalid_url_is_400(self):
        details = []
        for bad in ("ftp://example.com/x", "not a url", "/relative/path", ""):
            status, hdrs, _, body = self.create(bad)
            ok, d = is_problem(status, hdrs, body, 400)
            if not ok:
                return False, f"url={bad!r}: {d}"
            ok, d = has_validation_error(body, "url")
            if not ok:
                return False, f"url={bad!r}: {d}"
            details.append(repr(bad))
        return True, "400 + errors['url'] for " + ", ".join(details)

    def e06_malformed_custom_is_400(self):
        for bad in ("abc", "bad code!", "x" * 33, "ünïcode"):
            status, hdrs, _, body = self.create("https://example.com/x", bad)
            ok, d = is_problem(status, hdrs, body, 400)
            if not ok:
                return False, f"customCode={bad!r}: {d}"
            ok, d = has_validation_error(body, "customCode")
            if not ok:
                return False, f"customCode={bad!r}: {d}"
        return True, "400 + errors['customCode'] for too short, bad chars, too long, non-ASCII"

    def e07_click_count_increments_once(self):
        custom = self.code("count")
        url = "https://example.com/count"
        status, _, _, _ = self.create(url, custom)
        if status != 201:
            return False, f"setup create returned {status}"
        for _ in range(3):
            status, _, _, _ = call(self.base, "GET", f"/{custom}")
            if status != 302:
                return False, f"redirect returned {status}"
        status, _, _, body = call(self.base, "GET", f"/api/links/{custom}")
        count = get(body, "clickCount")
        last = get(body, "lastClickedAt")
        if count != 3:
            return False, f"clickCount after 3 redirects is {count!r}"
        if not last:
            return False, "lastClickedAt still null after clicks"
        return True, f"clickCount=3, lastClickedAt={last}"

    def e08_concurrent_redirects_lose_nothing(self):
        custom = self.code("race")
        status, _, _, _ = self.create("https://example.com/race", custom)
        if status != 201:
            return False, f"setup create returned {status}"
        n = self.concurrency
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(n, 32)) as pool:
            statuses = list(pool.map(lambda _: call(self.base, "GET", f"/{custom}")[0], range(n)))
        if any(s != 302 for s in statuses):
            return False, f"non-302 among concurrent redirects: {sorted(set(statuses))}"
        _, _, _, body = call(self.base, "GET", f"/api/links/{custom}")
        count = get(body, "clickCount")
        return (count == n), f"{n} concurrent redirects -> clickCount={count}"

    def e09_unknown_code_is_404(self):
        unknown = self.code("nope")
        status, hdrs, _, body = call(self.base, "GET", f"/{unknown}")
        ok, d = is_problem(status, hdrs, body, 404)
        if not ok:
            return False, f"redirect route: {d}"
        status, hdrs, _, body = call(self.base, "GET", f"/api/links/{unknown}")
        ok, d2 = is_problem(status, hdrs, body, 404)
        return ok, f"redirect route: {d}; detail route: {d2}"

    def e10_list_has_stats(self):
        status, hdrs, _, body = call(self.base, "GET", "/api/links")
        if status != 200:
            return False, f"expected 200, got {status} (is /api/links shadowed by the redirect route?)"
        if not isinstance(body, list):
            return False, "list body is not a JSON array"
        codes = {get(item, "code") for item in body}
        want = {c for c, _ in self.created.values()}
        missing = want - codes
        if missing:
            return False, f"created codes missing from list: {sorted(missing)}"
        for item in body:
            if get(item, "clickCount") is None or "lastclickedat" not in {k.lower() for k in item}:
                return False, f"list item lacks clickCount/lastClickedAt: {item}"
        return True, f"200, {len(body)} link(s), all created codes present with stats"

    def e11_detail_matches(self):
        code, url = self.created["generated"]
        status, _, _, body = call(self.base, "GET", f"/api/links/{code}")
        if status != 200:
            return False, f"expected 200, got {status}"
        ok = get(body, "code") == code and get(body, "url") == url
        return ok, f"200, code={get(body, 'code')!r}, url={get(body, 'url')!r}"

    def e12_delete_then_404(self):
        custom = self.code("del")
        self.create("https://example.com/del", custom)
        status, _, _, _ = call(self.base, "DELETE", f"/api/links/{custom}")
        if status != 204:
            return False, f"DELETE expected 204, got {status}"
        status, hdrs, _, body = call(self.base, "GET", f"/{custom}")
        ok, d = is_problem(status, hdrs, body, 404)
        if not ok:
            return False, f"redirect after delete: {d}"
        status, hdrs, _, body = call(self.base, "DELETE", f"/api/links/{custom}")
        ok, d2 = is_problem(status, hdrs, body, 404)
        return ok, f"204, then redirect {d}, second delete {d2}"

    def e13_reserved_prefix_is_400(self):
        status, hdrs, _, body = self.create("https://example.com/x", "api")
        ok, d = is_problem(status, hdrs, body, 400)
        if not ok:
            return False, d
        return has_validation_error(body, "customCode")

    def e14_query_and_fragment_round_trip(self):
        custom = self.code("qf")
        url = "https://example.com/path/a%20b?tab=1&x=y%26z#section-2"
        status, _, _, body = self.create(url, custom)
        if status != 201:
            return False, f"create returned {status}"
        if get(body, "url") != url:
            return False, f"stored url altered: {get(body, 'url')!r}"
        status, hdrs, _, _ = call(self.base, "GET", f"/{custom}")
        loc = hdrs.get("Location")
        return (status == 302 and loc == url), f"{status} Location={loc!r}"

    def e15_recreate_after_delete(self):
        custom = self.code("again")
        self.create("https://example.com/first", custom)
        call(self.base, "DELETE", f"/api/links/{custom}")
        status, _, text, body = self.create("https://example.com/second", custom)
        return (status == 201 and get(body, "url") == "https://example.com/second"), \
            f"re-create returned {status}: {text[:80]}"

    def e16_generated_code_is_single_namespace(self):
        code, _ = self.created["generated"]
        status, hdrs, _, body = self.create("https://example.com/clash", code)
        return is_problem(status, hdrs, body, 409)

    def run(self):
        checks = [
            ("E01", "AC-1", "POST valid URL -> 201 with generated 6-char base62 code, zero stats", self.e01_create_generated),
            ("E02", "AC-1", "GET /{generated} -> 302 to the original URL", self.e02_redirect_generated),
            ("E03", "AC-2", "POST with free custom code -> 201 echoing it", self.e03_create_custom),
            ("E04", "AC-2", "POST with taken custom code -> 409 Problem Details", self.e04_taken_custom_is_409),
            ("E05", "AC-2", "POST invalid URL -> 400 Problem Details with errors['url']", self.e05_invalid_url_is_400),
            ("E06", "AC-2", "POST malformed custom code -> 400 with errors['customCode']", self.e06_malformed_custom_is_400),
            ("E07", "AC-3", "each redirect increments clickCount exactly once; lastClickedAt set", self.e07_click_count_increments_once),
            ("E08", "AC-3", "concurrent redirects lose no increments", self.e08_concurrent_redirects_lose_nothing),
            ("E09", "AC-3/4", "unknown code -> 404 Problem Details on redirect and detail routes", self.e09_unknown_code_is_404),
            ("E10", "AC-4", "GET /api/links lists created links with clickCount and lastClickedAt", self.e10_list_has_stats),
            ("E11", "AC-4", "GET /api/links/{code} returns the link", self.e11_detail_matches),
            ("E12", "AC-4", "DELETE -> 204; redirect and second delete -> 404", self.e12_delete_then_404),
            ("E13", "S9", "custom code 'api' (reserved prefix) -> 400", self.e13_reserved_prefix_is_400),
            ("E14", "S9", "query string and fragment round-trip byte-identical", self.e14_query_and_fragment_round_trip),
            ("E15", "S9", "delete then re-create the same custom code -> 201", self.e15_recreate_after_delete),
            ("E16", "S9", "custom code equal to a generated code -> 409 (single namespace)", self.e16_generated_code_is_single_namespace),
        ]
        for cid, ac, name, fn in checks:
            self.check(cid, ac, name, fn)
        return self.results


def wait_for_server(base, seconds):
    deadline = time.time() + seconds
    last = None
    while time.time() < deadline:
        try:
            call(base, "GET", "/api/links", timeout=3)
            return True
        except Exception as exc:  # connection refused while starting
            last = exc
            time.sleep(0.5)
    print(f"server at {base} did not answer within {seconds}s: {last}", file=sys.stderr)
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", required=True, help="e.g. http://127.0.0.1:5181")
    ap.add_argument("--json", default=None, help="write the verdict as JSON to this path")
    ap.add_argument("--concurrency", type=int, default=50,
                    help="parallel redirects for the lost-increment check (default 50)")
    ap.add_argument("--wait", type=int, default=30,
                    help="seconds to wait for the server to answer (default 30)")
    args = ap.parse_args()

    if not wait_for_server(args.base_url, args.wait):
        return 2
    exam = Exam(args.base_url, args.concurrency)
    results = exam.run()
    passed = sum(1 for r in results if r["status"] == "PASS")
    for r in results:
        print(f"{r['status']:4s} {r['id']} [{r['ac']:<6}] {r['name']}")
        print(f"       {r['detail']}")
    print(f"\nexam: {passed}/{len(results)} passed  (run {exam.run_id}, {args.base_url})")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"brief": "shortlist", "exam_version": 1, "base_url": args.base_url,
                       "run_id": exam.run_id, "passed": passed, "total": len(results),
                       "checks": results}, f, indent=2)
        print(f"written {args.json}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
