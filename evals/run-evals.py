#!/usr/bin/env python3
"""Run assertion checks against generated eval outputs.

Usage:
    python evals/run-evals.py [--case SUBSTRING] [--require-all] [--list]
                              [--judge] [--judge-cmd TEMPLATE]

Each case lives at evals/cases/<prompt>/<case>/ with:
    GENERATE.md       instructions an agent follows to produce the output
    input/            self-contained fixture project
    assertions.json   declarative checks (see below)
    rubric.md         judge rubric (only for cases with a judge check)
    reference/        known-good anchor output for the judge
    output/           where generated artifacts land (disposable)

This runner is deterministic by default: it only CHECKS outputs that already exist.
Producing an output is a separate step done by an agent following the case's
GENERATE.md (see evals/README.md). Cases with no output are reported as MISSING and
skipped, unless --require-all is passed (CI mode after a generation step).

`judge` checks call a model and are therefore SKIPPED unless --judge is passed.
The judge command is a template with a {prompt_file} placeholder; the default uses
the Claude Code CLI. The judge prompt embeds the rubric, the reference anchor, and
the candidate, and demands a final JSON verdict {"score": 1-10, "reasons": [...]}.

assertions.json:
    {"output": "output/tasks.md",
     "checks": [
       {"type": "validator", "work_item": "input/docs/work-items/X.md", "root": "input", "strict": false},
       {"type": "task_count", "min": 6, "max": 16},
       {"type": "must_match", "pattern": "## Acceptance Criteria Coverage", "reason": "..."},
       {"type": "must_not_match", "pattern": "(?i)angular", "reason": "..."},
       {"type": "paths_exist", "root": "input", "allow_new": true},
       {"type": "shard_refs_resolve", "root": "input", "allow_new": true,
        "sanctioned_by": ["input/docs/work-items/X.md"]},
       {"type": "judge", "rubric": "rubric.md", "reference": "reference/tasks.md", "min_score": 7}
     ]}

Exit code 0 when every executed check of every checked case passes (and, with
--require-all, every case had an output); 1 otherwise. SKIPs never fail a case.
Python 3.8+, standard library only.
"""

import argparse
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVALS_DIR.parent
VALIDATE_TASKS = REPO_ROOT / "tools" / "validate-tasks.py"

DEFAULT_JUDGE_CMD = ('claude -p "Read the file {prompt_file} and follow its '
                     'instructions exactly."')

TASK_HEADING_RE = re.compile(r"^#{2,4}\s+T-\d{1,4}\s*:", re.MULTILINE)
FILE_BULLET_RE = re.compile(
    r"^\s*[-*]\s*`?(?P<path>[^`\s]+)`?\s*(?P<new>\(new\))?\s*(?:[-–—]\s*(?P<desc>.*))?$"
)
SHARD_REF_RE = re.compile(r"docs/(?:data-model|api-spec|ui-specification)/[A-Za-z0-9/_.-]+?\.md")
JSON_VERDICT_RE = re.compile(r"\{[^{}]*\"score\"[^{}]*\}", re.DOTALL)

JUDGE_PROMPT_TEMPLATE = """# Eval Judge

You are an impartial judge grading a generated task list against a fixed rubric.
Read everything below. Do not use any other context. Your entire response must end
with a single JSON object on its own line — no prose after it.

## Rubric

{rubric}

## Project ground truth (spec and convention excerpts)

The following excerpts are the project's authoritative conventions and contracts.
Use them to judge spec fidelity: technical details in the candidate (routes, error
codes, envelopes, field names, constraints) must match these — contradictions and
invented conventions are penalized. Judge the output, not the process: the candidate
may not have been shown all of these excerpts.

{ground_truth}

## Reference output (known-good anchor)

The candidate does NOT need to match this verbatim — it anchors what "good" looks
like. Judge substance, not wording.

{reference}

## Candidate output (under evaluation)

{candidate}

## Verdict contract

Score the candidate 1-10 against the rubric (use the rubric's own scoring guide).
Final line, JSON only, exactly this shape:
{{"score": <integer 1-10>, "reasons": ["<short reason>", "..."]}}
"""


def extract_file_entries(text):
    """Return (path, is_new) for every bullet under a Files to Modify/Create field."""
    entries = []
    in_field = False
    for line in text.splitlines():
        if re.match(r"^\*\*Files to Modify/Create:\*\*", line.strip()):
            in_field = True
            continue
        if in_field:
            if re.match(r"^\*\*[A-Za-z /]+:\*\*", line.strip()) or line.startswith("#"):
                in_field = False
                continue
            m = FILE_BULLET_RE.match(line)
            if m and m.group("path") and not line.strip().startswith("- [") \
                    and set(m.group("path")) - set("-*_"):
                entries.append((m.group("path"), bool(m.group("new"))))
    return entries


def run_judge(check, case_dir, out_text, judge_opts):
    if not judge_opts["enabled"]:
        return "SKIP", "judge check skipped (enable with --judge)"
    rubric_path = case_dir / check.get("rubric", "rubric.md")
    if not rubric_path.is_file():
        return "FAIL", f"rubric not found: {rubric_path}"
    rubric = rubric_path.read_text(encoding="utf-8", errors="replace")
    reference = "None provided."
    if check.get("reference"):
        ref_path = case_dir / check["reference"]
        if not ref_path.is_file():
            return "FAIL", f"reference not found: {ref_path}"
        reference = ref_path.read_text(encoding="utf-8", errors="replace")

    ground_parts = []
    for rel in check.get("context", []):
        p = case_dir / rel
        if not p.is_file():
            return "FAIL", f"judge context file not found: {p}"
        ground_parts.append(f"### {rel}\n\n{p.read_text(encoding='utf-8', errors='replace')}")
    ground_truth = "\n\n".join(ground_parts) if ground_parts else "None provided."

    prompt = JUDGE_PROMPT_TEMPLATE.format(rubric=rubric, reference=reference,
                                          ground_truth=ground_truth,
                                          candidate=out_text)
    prompt_file = case_dir / "output" / "judge-prompt.md"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text(prompt, encoding="utf-8")

    cmd = judge_opts["cmd"].replace("{prompt_file}", str(prompt_file))
    n_samples = max(1, int(check.get("judge_samples", judge_opts["samples"])))
    scores, all_reasons = [], []
    for _ in range(n_samples):
        verdict = None
        last_problem = ""
        for _attempt in range(3):  # judges occasionally omit the JSON line — retry
            try:
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                                      encoding="utf-8", errors="replace",
                                      timeout=judge_opts["timeout"])
            except subprocess.TimeoutExpired:
                return "FAIL", f"judge command timed out after {judge_opts['timeout']}s"
            except OSError as exc:
                return "FAIL", f"judge command failed to start: {exc}"
            verdicts = JSON_VERDICT_RE.findall(proc.stdout or "")
            if not verdicts:
                tail = (proc.stdout or proc.stderr or "").strip().splitlines()[-3:]
                last_problem = "no JSON verdict in judge output: " + " / ".join(tail)
                continue
            try:
                verdict = json.loads(verdicts[-1])
                scores.append(int(verdict["score"]))
                break
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                last_problem = f"unparseable judge verdict {verdicts[-1]!r}: {exc}"
                verdict = None
        if verdict is None:
            return "FAIL", f"{last_problem} (after 3 attempts)"
        all_reasons.append(verdict.get("reasons", []))

    # median of N runs; near-threshold single scores are noisy (see evals/experiments.md)
    score = int(statistics.median(scores))
    min_score = int(check.get("min_score", 7))
    reasons = "; ".join(str(r) for r in (all_reasons[scores.index(score)]
                                         if score in scores else all_reasons[0])[:3])
    runs = f" [runs: {', '.join(map(str, scores))}]" if n_samples > 1 else ""
    detail = f"score {score}/{10} (min {min_score}){runs}" + (f" — {reasons}" if reasons else "")
    return ("PASS" if score >= min_score else "FAIL"), detail


def run_check(check, case_dir, out_text, out_path, judge_opts):
    """Return (status: PASS|FAIL|SKIP, detail: str)."""
    ctype = check.get("type")

    if ctype == "judge":
        return run_judge(check, case_dir, out_text, judge_opts)

    if ctype == "validator":
        cmd = [sys.executable, str(VALIDATE_TASKS), str(out_path)]
        if check.get("work_item"):
            cmd += ["--work-item", str(case_dir / check["work_item"])]
        if check.get("root"):
            cmd += ["--root", str(case_dir / check["root"])]
        if check.get("strict"):
            cmd += ["--strict"]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc.returncode == 0:
            return "PASS", "validator clean"
        tail = "\n".join((proc.stdout or "").strip().splitlines()[-6:])
        return "FAIL", f"validator failed:\n      {tail.replace(chr(10), chr(10) + '      ')}"

    if ctype == "task_count":
        n = len(TASK_HEADING_RE.findall(out_text))
        lo, hi = check.get("min", 1), check.get("max", 10 ** 6)
        if lo <= n <= hi:
            return "PASS", f"{n} tasks (allowed {lo}-{hi})"
        return "FAIL", f"{n} tasks, expected {lo}-{hi}"

    if ctype in ("must_match", "must_not_match"):
        found = re.search(check["pattern"], out_text)
        ok = bool(found) if ctype == "must_match" else not found
        reason = check.get("reason", check["pattern"])
        return ("PASS" if ok else "FAIL"), (
            reason if ok else f"{reason} (pattern: {check['pattern']!r})")

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
            return "PASS", "all referenced files exist or are (new)"
        return "FAIL", "unknown paths: " + ", ".join(bad[:8])

    if ctype == "shard_refs_resolve":
        root = case_dir / check.get("root", "input")
        allow_new = check.get("allow_new", True)
        # A not-yet-existing shard reference is sanctioned when marked (new) on the
        # same line, on any line of the document itself, or in a sanctioning doc
        # (typically the work item whose impact tables declare the (new) shards).
        sanctioned = set()
        if allow_new:
            texts = [out_text]
            for rel in check.get("sanctioned_by", []):
                p = case_dir / rel
                if p.is_file():
                    texts.append(p.read_text(encoding="utf-8", errors="replace"))
            for text in texts:
                for line in text.splitlines():
                    if "(new)" in line:
                        for m in SHARD_REF_RE.finditer(line):
                            sanctioned.add(m.group(0))
        bad = []
        for line in out_text.splitlines():
            for m in SHARD_REF_RE.finditer(line):
                ref = m.group(0)
                if (root / ref).exists():
                    continue
                if allow_new and ("(new)" in line or ref in sanctioned):
                    continue
                bad.append(ref)
        if not bad:
            return "PASS", "all shard references resolve or are sanctioned (new)"
        return "FAIL", "unresolved shard refs: " + ", ".join(sorted(set(bad))[:8])

    return "FAIL", f"unknown check type: {ctype!r}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--case", default="", help="only run cases whose path contains this substring")
    ap.add_argument("--require-all", action="store_true",
                    help="fail if any case has no generated output (CI mode)")
    ap.add_argument("--list", action="store_true", help="list discovered cases and exit")
    ap.add_argument("--judge", action="store_true",
                    help="execute judge checks (calls a model; skipped otherwise)")
    ap.add_argument("--judge-cmd", default=DEFAULT_JUDGE_CMD,
                    help="judge command template with a {prompt_file} placeholder "
                         f"(default: {DEFAULT_JUDGE_CMD!r})")
    ap.add_argument("--judge-timeout", type=int, default=600,
                    help="judge command timeout in seconds (default 600)")
    ap.add_argument("--judge-samples", type=int, default=1,
                    help="judge runs per check, median taken (default 1; "
                         "per-check 'judge_samples' key overrides)")
    args = ap.parse_args()
    judge_opts = {"enabled": args.judge, "cmd": args.judge_cmd,
                  "timeout": args.judge_timeout, "samples": args.judge_samples}

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
            status, detail = run_check(check, case_dir, out_text, out_path, judge_opts)
            details.append(f"    {status:4s}  {check['type']}: {detail}")
            if status == "FAIL":
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
