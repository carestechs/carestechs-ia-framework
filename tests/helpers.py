"""Shared fixtures for the framework's own regression suite.

Builds throwaway framework projects (docs/work-items + tasks/ + plans/ + reviews) in
temp directories, optionally as real git repos, and drives the shipped tools through
their command-line contracts - the same surface orchestrators and sessions use. Where a
test needs a function rather than a process, `load_tool` imports a hyphen-named script
as a module.

Run the suite from the repo root:

    python -m unittest discover -s tests -v

Stdlib only, Python 3.8+. Zero model calls, zero tokens.
"""

import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
TOOLS_DIR = REPO_ROOT / "tools"
EVALS_DIR = REPO_ROOT / "evals"
CASES_DIR = EVALS_DIR / "cases"
BASELINES_DIR = EVALS_DIR / "baselines"
SCAFFOLD_DIR = REPO_ROOT / "scaffold"

PY = sys.executable

# Every git call in the suite is isolated from the developer's identity, signing,
# and line-ending settings: fixtures must behave identically on Windows and Linux.
GIT_ISOLATION = [
    "-c", "user.email=tests@framework.local", "-c", "user.name=framework-tests",
    "-c", "core.autocrlf=false", "-c", "commit.gpgsign=false",
    "-c", "init.defaultBranch=main", "-c", "core.hooksPath=/dev/null",
]
_EMPTY_GITCONFIG = Path(tempfile.gettempdir()) / "fw-tests-empty-gitconfig"
_EMPTY_GITCONFIG.touch(exist_ok=True)


def git_env():
    env = dict(os.environ)
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = str(_EMPTY_GITCONFIG)
    return env


def run(cmd, cwd=None, env=None):
    return subprocess.run([str(c) for c in cmd], cwd=str(cwd) if cwd else None,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env)


def run_tool(name, *args, cwd=None, directory=None):
    """Run tools/<name>.py (or <directory>/<name>.py) and return the CompletedProcess."""
    directory = directory or TOOLS_DIR
    return run([PY, directory / f"{name}.py", *args], cwd=cwd)


def load_tool(name, directory=None):
    """Import a hyphen-named script (tools/next-step.py) as a module, cached per name."""
    directory = directory or TOOLS_DIR
    mod_name = "_fw_" + name.replace("-", "_")
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, directory / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


def rmtree_force(path):
    """rmtree that survives read-only .git objects on Windows."""
    def _retry(func, p, _exc):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except OSError:
            pass
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_retry)
    else:
        shutil.rmtree(path, onerror=_retry)


def task_block(id, title="Do the thing", type="Backend", workflow="standard",
               deps="None", complexity="M", files=None, ac=None,
               description="Do it.", rationale="Because."):
    """One validator-clean task block in the canonical schema (prompts/base-template.md)."""
    files = files or [f"src/t{id:03d}.py (new)"]
    ac = ac or ["It works"]
    lines = [f"### T-{id:03d}: {title}", "",
             f"**Type:** {type}", f"**Workflow:** {workflow}", "",
             "**Description:**", description, "",
             "**Rationale:**", rationale, "",
             "**Acceptance Criteria:**"]
    lines += [f"- [ ] {a}" for a in ac]
    lines += ["", f"**Dependencies:** {deps}", f"**Complexity:** {complexity}", "",
              "**Files to Modify/Create:**"]
    lines += [f"- {f}" for f in files]
    lines.append("")
    return "\n".join(lines)


WORK_ITEM_KIND = {"FEAT": "Feature Brief", "BUG": "Bug Report", "IMP": "Improvement Proposal"}


class Project:
    """A throwaway framework project root (what `next-step.py --root` points at)."""

    def __init__(self, root):
        self.root = Path(root)
        (self.root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)

    # --- files -------------------------------------------------------------
    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        return p

    def read(self, rel):
        return (self.root / rel).read_text(encoding="utf-8")

    def exists(self, rel):
        return (self.root / rel).exists()

    def work_item(self, wi_id, title="Sample work item", status="In Progress",
                  slug="sample", acs=2):
        kind = WORK_ITEM_KIND[wi_id.split("-")[0]]
        lines = [f"# {kind}: {title}", "", "## 1. Identity", "",
                 "| Field | Value |", "|-------|-------|",
                 f"| **ID** | {wi_id} |", f"| **Status** | {status} |", "",
                 "## 7. Acceptance Criteria", ""]
        lines += [f"- [ ] **AC-{i}**: criterion {i}" for i in range(1, acs + 1)]
        lines.append("")
        return self.write(f"docs/work-items/{wi_id}-{slug}.md", "\n".join(lines))

    def task_list(self, wi_id, tasks, coverage=None, title="Sample"):
        """tasks: list of dicts accepted by task_block(). coverage: [(ac_text, covered_by)]."""
        out = [f"# Task List: {wi_id} {title}", "", "## Tasks", ""]
        out += [task_block(**t) for t in tasks]
        if coverage is not None:
            out += ["## Acceptance Criteria Coverage", "",
                    "| Work Item AC | Covered By |", "|--------------|------------|"]
            out += [f"| {ac} | {by} |" for ac, by in coverage]
            out.append("")
        return self.write(f"tasks/{wi_id}-tasks.md", "\n".join(out))

    def review(self, rel, verdict, preamble=""):
        body = "# Review\n\n"
        if preamble:
            body += preamble.rstrip() + "\n\n"
        body += f"## Verdict\n\n{verdict}\n"
        return self.write(rel, body)

    # --- git ---------------------------------------------------------------
    def git(self, *args):
        proc = run(["git", "-C", self.root, *GIT_ISOLATION, *args], env=git_env())
        if proc.returncode != 0:
            raise AssertionError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
        return proc.stdout

    def init_git(self):
        self.git("init", "-q")
        return self

    def commit(self, message):
        """Stage everything and commit (empty commits allowed: subjects are evidence)."""
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self

    # --- tools -------------------------------------------------------------
    def next_step_raw(self, *args):
        return run_tool("next-step", "--root", self.root, *args)

    def next_step(self, *args):
        """Run next-step.py --json. Returns (returncode, report-or-None, stderr)."""
        proc = run_tool("next-step", "--root", self.root, "--json", *args)
        report = None
        if proc.returncode == 0 and proc.stdout.strip():
            report = json.loads(proc.stdout)
        return proc.returncode, report, proc.stderr

    def report(self, *args):
        rc, report, err = self.next_step(*args)
        if rc != 0:
            raise AssertionError(f"next-step exited {rc}: {err.strip()}")
        return report

    def wi(self, wi_id="FEAT-001"):
        report = self.report()
        for w in report["work_items"]:
            if w["id"] == wi_id:
                return w
        raise AssertionError(f"{wi_id} not in open work items (closed={report['closed']})")

    def mark(self, wi_id, *marks, note=None):
        args = ["--wi", wi_id]
        for m in marks:
            args += ["--mark", m]
        if note:
            args += ["--note", note]
        proc = self.next_step_raw(*args)
        if proc.returncode != 0:
            raise AssertionError(f"--mark failed: {proc.stderr.strip()}")
        return proc.stdout


def states(wi):
    return {t["id"]: t["state"] for t in wi["tasks"]}


def steps(wi):
    return [(s["step"], s["task"], s["fresh"]) for s in wi["next_steps"]]


def first_step(wi):
    if not wi["next_steps"]:
        raise AssertionError(f"no next steps; position={wi['position']!r} "
                             f"warnings={wi['warnings']}")
    return wi["next_steps"][0]


class FrameworkTestCase(unittest.TestCase):
    """Gives every test a fresh temp dir (`self.tmp`) and project (`self.p`)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fw-test-"))
        self.addCleanup(rmtree_force, self.tmp)
        self.p = Project(self.tmp / "project")

    def fixture_input(self, case_rel, dest=None):
        """Copy an eval case's input/ fixture into the temp dir; returns its path."""
        src = CASES_DIR / case_rel / "input"
        dest = dest or (self.tmp / "fixture")
        shutil.copytree(src, dest)
        return dest


def summary_counts(stdout):
    """(errors, warnings) from a validator's trailing summary line."""
    m = re.search(r"(\d+) error\(s\), (\d+) warning\(s\)", stdout)
    if not m:
        raise AssertionError(f"no summary line in output:\n{stdout}")
    return int(m.group(1)), int(m.group(2))
