#!/usr/bin/env python3
"""Run assertion checks against generated eval outputs.

Usage:
    python evals/run-evals.py [--case SUBSTRING] [--require-all] [--list]

Each case lives at evals/cases/<prompt>/<case>/ with:
    GENERATE.md       instructions an agent follows to produce the output
    input/            self-contained fixture project
    assertions.json   declarative checks (see below)
    output/           where generated artifacts land (disposable)

This runner is deterministic: it only CHECKS outputs that already exist. Producing
an output is a separate step done by an agent following the case's GENERATE.md
(see evals/README.md). Cases with no output are reported as MISSING and skipped,
unless --require-all is passed (CI mode after a generation step).

assertions.json:
    {"output": "output/tasks.md",
     "checks": [
       {"type": "validator", "work_item": "input/docs/work-items/X.md", "root": "input", "strict": false},
       {"type": "task_count", "min": 6, "max": 16},
       {"type": "must_match", "pattern": "## Acceptance Criteria Coverage", "reason": "..."},
       {"type": "must_not_match", "pattern": "(?i)angular", "reason": "..."},
       {"type": "paths_exist", "root": "input", "allow_new": true},
       {"type": "shard_refs_resolve", "root": "input", "allow_new": true}
     ]}

Exit code 0 when every check of every checked case passes (and, with
--require-all, every case had an output); 1 otherwise.
Python 3.8+, standard library only.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVALS_DIR.parent
VALIDATE_TASKS = REPO_ROOT / "tools" / "validate-tasks.py"

TASK_HEADING_RE = re.compile(r"^#{2,4}\s+T-\d{1,4}\s*:", re.MULTILINE)
FILE_BULLET_RE = re.compile(
    r"^\s*[-*]\s*`?(?P<path>[^`\s]+)`?\s*(?P<new>\(new\))?\s*(?:[-–—]\s*(?P<desc>.*))?$"
)
FILES_FIELD_RE = re.compile(r"^\*\*Files to Modify/Create:\*\*", re.MULTILINE)
SHARD_REF_RE = re.compile(r"docs/(?:data-model|api-spec|ui-specification)/[A-Za-z0-9/_.-]+?\.md")


def extract_file_entries(text):
    """Return (path, is_new) for every bullet under a Files to Modify/Create field."""
    entries = []
    lines = text.splitlines()
    in_field = False
    for line in lines:
        if re.match(r"^\*\*Files to Modify/Create:\*\*", line.strip()):
            in_field = True
            continue
        if in_field:
            if re.match(r"^\*\*[A-Za-z /]+:\*\*", line.strip()) or line.startswith("#"):
                in_field = False
                continue
            m = FILE_BULLET_RE.match(line)
            if m and m.group("path") and not line.strip().startswith("- ["):
                entries.append((m.group("path"), bool(m.group("new"))))
    return entries


def run_check(check, case_dir, out_text, out_path):
    """Return (passed: bool, detail: str)."""
    ctype = check.get("type")

    if ctype == "validator":
        cmd = [sys.executable, str(VALIDATE_TASKS), str(out_path)]
        if check.get("work_item"):
            cmd += ["--work-item", str(case_dir / check["work_item"])]
        if check.get("root"):
            cmd += ["--root", str(case_dir / check["root"])]
        if check.get("strict"):
            cmd += ["--strict"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            return True, "validator clean"
        tail = "\n".join((proc.stdout or "").strip().splitlines()[-6:])
        return False, f"validator failed:\n      {tail.replace(chr(10), chr(10) + '      ')}"

    if ctype == "task_count":
        n = len(TASK_HEADING_RE.findall(out_text))
        lo, hi = check.get("min", 1), check.get("max", 10 ** 6)
        if lo <= n <= hi:
            return True, f"{n} tasks (allowed {lo}-{hi})"
        return False, f"{n} tasks, expected {lo}-{hi}"

    if ctype in ("must_match", "must_not_match"):
        found = re.search(check["pattern"], out_text)
        ok = bool(found) if ctype == "must_match" else not found
        reason = check.get("reason", check["pattern"])
        return ok, reason if ok else f"{reason} (pattern: {check['pattern']!r})"

    if ctype == "paths_exist":
        root = case_dir / check.get("root", "input")
        allow_new = check.get("allow_new", True)
        bad = []
        for path, is_new in extract_file_entries(out_text):
            if any(ch in path for ch in "[]<>{}"):
                bad.append(f"{path} (placeholder)")
            elif is_new and allow_new:
                continue
            elif not (root / path).exists():
                bad.append(path)
        if not bad:
            return True, "all referenced files exist or are (new)"
        return False, "unknown paths: " + ", ".join(bad[:8])

    if ctype == "shard_refs_resolve":
        root = case_dir / check.get("root", "input")
        allow_new = check.get("allow_new", True)
        bad = []
        for line in out_text.splitlines():
            for m in SHARD_REF_RE.finditer(line):
                ref = m.group(0)
                if (root / ref).exists():
                    continue
                if allow_new and "(new)" in line:
                    continue
                bad.append(ref)
        if not bad:
            return True, "all shard references resolve"
        return False, "unresolved shard refs: " + ", ".join(sorted(set(bad))[:8])

    return False, f"unknown check type: {ctype!r}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--case", default="", help="only run cases whose path contains this substring")
    ap.add_argument("--require-all", action="store_true",
                    help="fail if any case has no generated output (CI mode)")
    ap.add_argument("--list", action="store_true", help="list discovered cases and exit")
    args = ap.parse_args()

    cases = sorted(EVALS_DIR.glob("cases/*/*/assertions.json"))
    if args.case:
        cases = [c for c in cases if args.case in str(c.parent)]
    if not cases:
        print("no eval cases found", file=sys.stderr)
        return 1
    if args.list:
        for c in cases:
            print(c.parent.relative_to(EVALS_DIR))
        return 0

    failed = missing = 0
    for assertions_path in cases:
        case_dir = assertions_path.parent
        name = case_dir.relative_to(EVALS_DIR / "cases")
        spec = json.loads(assertions_path.read_text(encoding="utf-8"))
        out_path = case_dir / spec["output"]
        if not out_path.is_file():
            print(f"[MISSING] {name} — no {spec['output']} (generate it per GENERATE.md)")
            missing += 1
            continue
        out_text = out_path.read_text(encoding="utf-8", errors="replace")
        case_failed = False
        details = []
        for check in spec.get("checks", []):
            ok, detail = run_check(check, case_dir, out_text, out_path)
            details.append(f"    {'PASS' if ok else 'FAIL'}  {check['type']}: {detail}")
            if not ok:
                case_failed = True
        print(f"[{'FAIL' if case_failed else 'PASS'}] {name}")
        for d in details:
            print(d)
        if case_failed:
            failed += 1

    total = len(cases)
    print(f"\n{total} case(s): {total - failed - missing} passed, {failed} failed, {missing} missing")
    if failed or (args.require_all and missing):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
