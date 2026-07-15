#!/usr/bin/env python3
"""Generate N samples per eval case and tabulate assertion pass rates.

Usage:
    python evals/run-baseline.py [--samples 3] [--case SUBSTRING] [--label NAME]
                                 [--gen-cmd TEMPLATE] [--timeout 900] [--judge]

For each case under evals/cases/, this script runs the generation command N times
(cwd = the case directory, so GENERATE.md's relative paths resolve), checks each
produced output with run-evals.py, archives the sample to
evals/baselines/<label>/<case>/sample-N.md, and writes a results table + JSON.

Generation is stochastic and billable: each sample is a real agent run. The default
command uses the Claude Code CLI headless mode with file edits allowed and Bash
restricted to python (so the agent can run the validators GENERATE.md asks for):

    claude -p "Read GENERATE.md in the current directory and follow it exactly."
        --permission-mode acceptEdits --allowedTools "Bash(python *)"

Cases run in parallel (one worker per case); samples within a case run sequentially
(they share the case's output path). Exit code is always 0 — a baseline is a
measurement, not a gate. Python 3.8+, standard library only.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
CHECK_LINE_RE = re.compile(r"^\s+(PASS|FAIL|SKIP)\s+([a-z_]+):", re.MULTILINE)
DEFAULT_GEN_CMD = ('claude -p "Read GENERATE.md in the current directory and follow it '
                   'exactly." --permission-mode acceptEdits --allowedTools "Bash(python *)"')


def generate_once(case_dir, cmd, timeout):
    spec = json.loads((case_dir / "assertions.json").read_text(encoding="utf-8"))
    out_path = case_dir / spec["output"]
    if out_path.exists():
        out_path.unlink()
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, shell=True, cwd=str(case_dir),
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"generation timed out ({timeout}s)", time.time() - t0
    if not out_path.is_file():
        tail = " / ".join((proc.stdout or proc.stderr or "").strip().splitlines()[-3:])
        return False, f"no output produced (exit {proc.returncode}): {tail}", time.time() - t0
    return True, "", time.time() - t0


def check_case(case_name, judge):
    cmd = [sys.executable, str(EVALS_DIR / "run-evals.py"), "--case", case_name]
    if judge:
        cmd.append("--judge")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    checks = [(m.group(1), m.group(2)) for m in CHECK_LINE_RE.finditer(proc.stdout or "")]
    passed = bool(checks) and all(s != "FAIL" for s, _ in checks)
    return passed, checks


def run_case(case_dir, args, label_dir):
    name = case_dir.name
    spec = json.loads((case_dir / "assertions.json").read_text(encoding="utf-8"))
    out_path = case_dir / spec["output"]
    results = []
    for i in range(1, args.samples + 1):
        ok, err, secs = generate_once(case_dir, args.gen_cmd, args.timeout)
        if not ok:
            print(f"[{name}] sample {i}: GENERATION FAILED — {err}", flush=True)
            results.append({"sample": i, "generated": False, "error": err,
                            "secs": round(secs)})
            continue
        passed, checks = check_case(name, args.judge)
        archive = label_dir / name / f"sample-{i}.md"
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out_path, archive)
        out_path.unlink()
        judge_prompt = case_dir / "output" / "judge-prompt.md"
        if judge_prompt.exists():
            judge_prompt.unlink()
        print(f"[{name}] sample {i}: {'PASS' if passed else 'FAIL'} "
              f"({round(secs)}s)", flush=True)
        results.append({"sample": i, "generated": True, "passed": passed,
                        "checks": [{"status": s, "type": t} for s, t in checks],
                        "secs": round(secs)})
    return name, results


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--samples", type=int, default=3, help="samples per case (default 3)")
    ap.add_argument("--case", default="", help="only cases whose path contains this substring")
    ap.add_argument("--label", default="baseline", help="results directory name under evals/baselines/")
    ap.add_argument("--gen-cmd", default=DEFAULT_GEN_CMD,
                    help="generation command run with cwd = case directory")
    ap.add_argument("--timeout", type=int, default=900,
                    help="per-generation timeout in seconds (default 900)")
    ap.add_argument("--judge", action="store_true", help="also run judge checks per sample")
    args = ap.parse_args()

    case_dirs = [c.parent for c in sorted(EVALS_DIR.glob("cases/*/*/assertions.json"))
                 if args.case in str(c.parent)]
    if not case_dirs:
        print("no eval cases found", file=sys.stderr)
        return 1
    label_dir = EVALS_DIR / "baselines" / args.label
    label_dir.mkdir(parents=True, exist_ok=True)

    print(f"Baseline '{args.label}': {len(case_dirs)} case(s) x {args.samples} sample(s)")
    with ThreadPoolExecutor(max_workers=len(case_dirs)) as pool:
        all_results = dict(pool.map(lambda d: run_case(d, args, label_dir), case_dirs))

    print(f"\n{'case':42s} {'gen ok':>6s} {'passed':>6s} {'rate':>6s}  top failing checks")
    summary = {}
    for name, results in sorted(all_results.items()):
        generated = [r for r in results if r.get("generated")]
        passed = [r for r in generated if r.get("passed")]
        fail_counts = {}
        for r in generated:
            for c in r.get("checks", []):
                if c["status"] == "FAIL":
                    fail_counts[c["type"]] = fail_counts.get(c["type"], 0) + 1
        rate = f"{100 * len(passed) / len(generated):.0f}%" if generated else "-"
        top = ", ".join(f"{t} x{n}" for t, n in
                        sorted(fail_counts.items(), key=lambda kv: -kv[1])[:3]) or "-"
        print(f"{name:42s} {len(generated):3d}/{len(results):<2d} {len(passed):6d} {rate:>6s}  {top}")
        summary[name] = {"samples": results, "pass_rate": rate, "failing_checks": fail_counts}

    results_path = label_dir / "results.json"
    results_path.write_text(json.dumps(
        {"label": args.label, "samples_per_case": args.samples,
         "gen_cmd": args.gen_cmd, "judge": args.judge, "cases": summary},
        indent=2), encoding="utf-8")
    print(f"\nresults written to {results_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
