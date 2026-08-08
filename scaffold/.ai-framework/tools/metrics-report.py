#!/usr/bin/env python3
"""Print the framework-effectiveness scorecard for a project.

Usage:
    python metrics-report.py [--root .] [--events metrics/events.ndjson] [--max-age 30]

Computes, from artifacts + git history + an optional event log (see
guides/evaluation.md for the schema):
  - work-item inventory and statuses
  - per task list: task count, validator status, amendment commits,
    human correction burden (diff between first committed and current version)
  - review verdicts (tasks/*-review.md)
  - doc health: validate-specs results + freshness-stamp age distribution
  - defect attribution: BUG-* work items linked back to FEAT-*
  - event-log metrics: per-step acceptance rate, mean step duration, token spend

Sections whose inputs are missing (no git repo, no event log, no tasks/) are
skipped with a note. Python 3.8+, standard library only.
"""

import argparse
import datetime
import difflib
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
TASK_HEADING_RE = re.compile(r"^#{2,4}\s+T-\d{1,4}\s*:", re.MULTILINE)
STAMP_RE = re.compile(r"^>\s*\*\*Last verified against code:\*\*\s*(.*)$", re.MULTILINE)
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
VERDICT_RE = re.compile(r"Verdict[^A-Za-z]*(approve|revise)", re.IGNORECASE)
SUMMARY_RE = re.compile(r"(\d+)\s+error\(s\),\s+(\d+)\s+warning\(s\)")
FEAT_RE = re.compile(r"\bFEAT-\d{1,4}\b")


def git(root, *args):
    try:
        proc = subprocess.run(["git", "-C", str(root), *args],
                              capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def parse_ts(value):
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def section(title):
    print(f"\n== {title} " + "=" * max(1, 60 - len(title)))


def report_work_items(root):
    wi_dir = root / "docs" / "work-items"
    section("Work items")
    if not wi_dir.is_dir():
        print("  (no docs/work-items directory)")
        return
    counts = {}
    for wi in sorted(wi_dir.glob("*.md")):
        if wi.name.startswith("TEMPLATE-"):
            continue
        status = "?"
        for line in wi.read_text(encoding="utf-8", errors="replace").splitlines():
            if "Status" in line and "|" in line:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                cells = [c for c in cells if c and "Status" not in c]
                if cells:
                    status = re.sub(r"[*`]", "", cells[-1]).strip() or "?"
                break
        counts[status] = counts.get(status, 0) + 1
        print(f"  {wi.stem:45s} {status}")
    if counts:
        print("  --")
        for status, n in sorted(counts.items()):
            print(f"  {n} x {status}")


def run_validator(script, *args):
    try:
        proc = subprocess.run([sys.executable, str(TOOLS_DIR / script), *map(str, args)],
                              capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None, None
    m = SUMMARY_RE.search(proc.stdout or "")
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def report_task_lists(root, in_repo):
    tasks_dir = root / "tasks"
    section("Task lists")
    if not tasks_dir.is_dir():
        print("  (no tasks/ directory)")
        return
    files = [f for f in sorted(tasks_dir.glob("*.md")) if not f.stem.endswith("-review")]
    if not files:
        print("  (no task lists yet)")
        return
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        n_tasks = len(TASK_HEADING_RE.findall(text))
        errors, warnings = run_validator("validate-tasks.py", f, "--root", root)
        val = "validator n/a" if errors is None else f"{errors} err / {warnings} warn"
        line = f"  {f.name:40s} {n_tasks:3d} tasks   {val}"
        if in_repo:
            rel = f.relative_to(root).as_posix()
            log = git(root, "log", "--follow", "--reverse", "--format=%H %cI", "--", rel)
            shas = [l.split()[0] for l in (log or "").splitlines() if l.strip()]
            if shas:
                amendments = len(shas) - 1
                first = git(root, "show", f"{shas[0]}:{rel}")
                if first is not None:
                    ratio = difflib.SequenceMatcher(None, first, text).ratio()
                    burden = (1 - ratio) * 100
                    line += f"   burden {burden:5.1f}%   amendments {amendments}"
        print(line)
    print("  (burden = % of the first committed version rewritten before/after acceptance)")


VERDICT_HEADING_RE = re.compile(
    r"^#{1,6}\s*\**\s*verdict\b[\s:*]*(?:(approve|revise)\b.*)?$", re.IGNORECASE)
VERDICT_WORD_RE = re.compile(r"(?<!not )\b(approve|revise)\b", re.IGNORECASE)
VERDICT_DECL_RE = re.compile(r"^[*_`\s]*verdict\b[^a-z]*(approve|revise)", re.IGNORECASE)
HEADING_RE = re.compile(r"^#{1,6}\s")


def read_verdict(path):
    """Verdict from the '## Verdict' section only - mirrors next-step.py."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    fence = None
    body = []
    for raw in lines:  # drop fenced blocks: quoted examples are not verdicts
        st = raw.lstrip()
        if st.startswith("```") or st.startswith("~~~"):
            fence = None if fence == st[:3] else (fence or st[:3])
            continue
        if fence is None:
            body.append(raw)
    for i, raw in enumerate(body):
        hm = VERDICT_HEADING_RE.match(raw)
        if not hm:
            continue
        if hm.group(1):
            return hm.group(1).lower()
        for nxt in body[i + 1:]:
            if HEADING_RE.match(nxt):
                break
            if nxt.lstrip().startswith(">"):
                continue
            wm = VERDICT_WORD_RE.search(nxt)
            if wm:
                return wm.group(1).lower()
    for raw in body:
        st = raw.strip()
        if st.startswith(">"):
            continue
        dm = VERDICT_DECL_RE.match(st)
        if dm:
            return dm.group(1).lower()
    return None


def report_reviews(root):
    tasks_dir = root / "tasks"
    section("Reviews")
    if not tasks_dir.is_dir():
        print("  (no tasks/ directory)")
        return
    approve = revise = 0
    for f in sorted(tasks_dir.glob("*-review.md")):
        # Same section-scoped read as next-step.py (v2.8.6): a whole-file search
        # picks up a re-review's "overwrites the previous (verdict `revise`)"
        # opener, and two tools in one scaffold must never disagree about one file.
        verdict = read_verdict(f) or "?"
        if verdict == "approve":
            approve += 1
        elif verdict == "revise":
            revise += 1
        print(f"  {f.name:45s} {verdict}")
    total = approve + revise
    if total:
        print(f"  --\n  first-pass acceptance (current verdicts): "
              f"{approve}/{total} ({100 * approve / total:.0f}%)")
    else:
        print("  (no review files yet)")


def report_doc_health(root, max_age):
    section("Doc health")
    errors, warnings = run_validator("validate-specs.py", "--root", root,
                                     "--max-age", max_age)
    if errors is None:
        print("  validate-specs: n/a (no sharded specs found?)")
    else:
        print(f"  validate-specs: {errors} error(s), {warnings} warning(s)")
    docs = root / "docs"
    ages = []
    unfilled = 0
    today = datetime.date.today()
    if docs.is_dir():
        for f in docs.rglob("*.md"):
            if f.name.startswith("TEMPLATE-"):
                continue
            m = STAMP_RE.search(f.read_text(encoding="utf-8", errors="replace"))
            if not m:
                continue
            d = DATE_RE.search(m.group(1))
            if not d:
                unfilled += 1
                continue
            try:
                ages.append((today - datetime.date.fromisoformat(d.group(1))).days)
            except ValueError:
                unfilled += 1
    if ages:
        stale = sum(1 for a in ages if a > int(max_age))
        print(f"  stamps: {len(ages)} filled ({unfilled} unfilled), age "
              f"min/median/max = {min(ages)}/{int(statistics.median(ages))}/{max(ages)} days, "
              f"{stale} stale (>{max_age}d)")
    else:
        print(f"  stamps: none filled ({unfilled} unfilled)")


def report_defects(root):
    wi_dir = root / "docs" / "work-items"
    section("Defect attribution")
    if not wi_dir.is_dir():
        print("  (no docs/work-items directory)")
        return
    links = {}
    for bug in sorted(wi_dir.glob("BUG-*.md")):
        if bug.name.startswith("TEMPLATE-"):
            continue
        feats = sorted(set(FEAT_RE.findall(
            bug.read_text(encoding="utf-8", errors="replace"))))
        for feat in feats or ["(unattributed)"]:
            links.setdefault(feat, []).append(bug.stem)
    if not links:
        print("  (no BUG-* work items)")
        return
    for feat, bugs in sorted(links.items()):
        print(f"  {feat}: {len(bugs)} bug(s) — {', '.join(bugs)}")


def report_events(events_path):
    section("Event log")
    if not events_path.is_file():
        print(f"  (no event log at {events_path} — see guides/evaluation.md for the schema)")
        return
    events = []
    bad = 0
    for line in events_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            bad += 1
    if bad:
        print(f"  ({bad} malformed line(s) skipped)")
    if not events:
        print("  (event log is empty)")
        return

    steps = {}
    for e in events:
        s = steps.setdefault(e.get("step", "?"),
                             {"accepted": 0, "revised": 0, "tokens": 0, "durations": []})
        ev = e.get("event")
        if ev in ("accepted", "revised"):
            s[ev] += 1
        s["tokens"] += int(e.get("session_tokens") or 0)

    starts = {}
    for e in sorted(events, key=lambda x: x.get("ts", "")):
        key = (e.get("work_item"), e.get("task"), e.get("step"))
        ts = parse_ts(e.get("ts", ""))
        if ts is None:
            continue
        if e.get("event") == "started":
            starts.setdefault(key, ts)
        elif e.get("event") in ("accepted", "completed") and key in starts:
            delta = (ts - starts.pop(key)).total_seconds() / 60
            if delta >= 0:
                steps[e.get("step", "?")]["durations"].append(delta)

    print(f"  {len(events)} event(s)")
    print(f"  {'step':22s} {'accept':>6s} {'revise':>6s} {'rate':>6s} "
          f"{'avg min':>8s} {'tokens':>10s}")
    for step, s in sorted(steps.items()):
        total = s["accepted"] + s["revised"]
        rate = f"{100 * s['accepted'] / total:.0f}%" if total else "-"
        avg = f"{statistics.mean(s['durations']):.0f}" if s["durations"] else "-"
        print(f"  {step:22s} {s['accepted']:6d} {s['revised']:6d} {rate:>6s} "
              f"{avg:>8s} {s['tokens']:10d}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path("."),
                    help="project root (default: cwd)")
    ap.add_argument("--events", type=Path, default=None,
                    help="event log path (default: <root>/metrics/events.ndjson)")
    ap.add_argument("--max-age", type=int, default=30,
                    help="stamp staleness threshold in days (default 30)")
    args = ap.parse_args()

    root = args.root.resolve()
    events_path = args.events if args.events else root / "metrics" / "events.ndjson"
    in_repo = git(root, "rev-parse", "--is-inside-work-tree") is not None
    print(f"Framework effectiveness scorecard — {root}")
    if not in_repo:
        print("(not a git repository: correction-burden and amendment metrics skipped)")

    report_work_items(root)
    report_task_lists(root, in_repo)
    report_reviews(root)
    report_doc_health(root, args.max_age)
    report_defects(root)
    report_events(events_path)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
