"""Contracts that several tools carry copies of must not drift apart.

The tools are shipped as standalone stdlib scripts, so the task-block grammar, file
bullet shape, freshness stamp and verdict regexes are duplicated by design. These tests
pin the copies to each other, check the scaffold mirrors the root sources (the Python
equivalent of scripts/sync-scaffold.sh --check, runnable on Windows), and gate the
release metadata the CI workflow also checks.
"""

import filecmp
import re
import unittest
from pathlib import Path

from helpers import CASES_DIR, EVALS_DIR, REPO_ROOT, SCAFFOLD_DIR, load_tool

ns = load_tool("next-step")
vt = load_tool("validate-tasks")
vs = load_tool("validate-specs")
mr = load_tool("metrics-report")
re_mod = load_tool("run-evals", EVALS_DIR)


class RegexCopies(unittest.TestCase):
    def test_task_block_grammar_is_shared(self):
        self.assertEqual(ns.TASK_HEADING_RE.pattern, vt.TASK_HEADING_RE.pattern)
        self.assertEqual(ns.FIELD_RE.pattern, vt.FIELD_RE.pattern)
        self.assertEqual(ns.DEP_ID_RE.pattern, vt.DEP_ID_RE.pattern)
        self.assertEqual(ns.FILE_BULLET_RE.pattern, vt.FILE_BULLET_RE.pattern)
        self.assertEqual(re_mod.FILE_BULLET_RE.pattern, vt.FILE_BULLET_RE.pattern)

    def test_freshness_stamp_is_shared(self):
        self.assertEqual(vs.STAMP_RE.pattern, mr.STAMP_RE.pattern)
        self.assertEqual(vs.STAMP_RE.flags, mr.STAMP_RE.flags)

    def test_verdict_section_grammar_is_shared(self):
        for name in ("VERDICT_HEADING_RE", "VERDICT_WORD_RE", "VERDICT_DECL_RE", "HEADING_RE"):
            with self.subTest(name):
                self.assertEqual(getattr(ns, name).pattern, getattr(mr, name).pattern)
                self.assertEqual(getattr(ns, name).flags, getattr(mr, name).flags)

    def test_published_verdict_regexes_match_the_same_strings(self):
        """metrics-report spells the contract with [^A-Za-z]; both are case-insensitive."""
        for text in ("Verdict: approve", "**Verdict:** revise", "verdict `revise`",
                     "VERDICT - APPROVE", "verdicts approve", "no verdict"):
            a = ns.VERDICT_RE.search(text)
            b = mr.VERDICT_RE.search(text)
            self.assertEqual(a is None, b is None, text)
            if a:
                self.assertEqual(a.group(1).lower(), b.group(1).lower(), text)

    def test_enum_contracts_match_the_schema_prompt(self):
        """prompts/base-template.md is the single canonical task schema."""
        base = (REPO_ROOT / "prompts" / "base-template.md").read_text(encoding="utf-8")
        for value in vt.TYPE_VALUES - {"Investigation", "Cleanup"}:
            self.assertIn(value, base, value)
        for value in vt.WORKFLOW_VALUES:
            self.assertIn(f"`{value}`", base, value)
        self.assertIn("Investigation", (REPO_ROOT / "prompts/bugfix-tasks.md").read_text(encoding="utf-8"))
        self.assertIn("Cleanup", (REPO_ROOT / "prompts/refactor-tasks.md").read_text(encoding="utf-8"))
        self.assertEqual(set(ns.NON_IMPL_COMMIT_PREFIXES),
                         {"plan", "review", "tasks", "docs", "close", "chore"})


class ParsersAgree(unittest.TestCase):
    TASK_LISTS = [
        "feature-tasks/case-001-task-labels/reference/tasks.md",
        "bugfix-tasks/case-002-overdue-timezone/reference/tasks.md",
        "refactor-tasks/case-004-date-logic-extraction/reference/tasks.md",
        "review-tasks/case-003-review-flawed-tasks/input/tasks/FEAT-001-tasks.md",
        "plan-generation/case-006-plan-label-endpoints/input/tasks/FEAT-001-tasks.md",
    ]

    def test_next_step_and_validator_parse_the_same_tasks_and_dependencies(self):
        for rel in self.TASK_LISTS:
            path = CASES_DIR / rel
            with self.subTest(rel):
                lenient = ns.parse_task_list(path)
                strict, _ = vt.parse_tasks(path, vt.Report())
                self.assertEqual(sorted(lenient), sorted(t.id for t in strict))
                for t in strict:
                    deps_text = t.fields["Dependencies"][1]
                    deps = [] if deps_text.strip("`").lower() in ("none", "none.") else \
                        [int(d[2:]) for d in vt.DEP_ID_RE.findall(deps_text)]
                    self.assertEqual(lenient[t.id]["deps"], deps, f"T-{t.id:03d}")
                    self.assertEqual(lenient[t.id]["type"], t.fields["Type"][1].strip("`"))
                text = path.read_text(encoding="utf-8")
                self.assertEqual(len(re_mod.TASK_HEADING_RE.findall(text)), len(strict))


class ScaffoldMirror(unittest.TestCase):
    SYNCED = ("templates", "prompts", "guides", "tools")

    def diff(self, a, b):
        cmp = filecmp.dircmp(a, b, ignore=["__pycache__"])
        problems = [f"only in {a}: {n}" for n in cmp.left_only]
        problems += [f"only in {b}: {n}" for n in cmp.right_only]
        problems += [f"differs: {b / n}" for n in cmp.diff_files]
        for sub in cmp.common_dirs:
            problems += self.diff(a / sub, b / sub)
        return problems

    def test_scaffold_copy_matches_root_sources(self):
        """scripts/sync-scaffold.sh --check, for environments without bash."""
        problems = []
        for d in self.SYNCED:
            problems += self.diff(REPO_ROOT / d, SCAFFOLD_DIR / ".ai-framework" / d)
        self.assertEqual(problems, [], "run scripts/sync-scaffold.sh")

    def test_bundled_version_matches_changelog_head(self):
        version = (SCAFFOLD_DIR / ".ai-framework" / "VERSION").read_text(encoding="utf-8").strip()
        head = re.search(r"^## \[(\d+\.\d+\.\d+)\]", (REPO_ROOT / "CHANGELOG.md")
                         .read_text(encoding="utf-8"), re.MULTILINE)
        self.assertIsNotNone(head)
        self.assertEqual(version, head.group(1))

    def test_slash_command_self_checks_run_the_gate_command(self):
        """The step-2 gate passes --work-item for every work-item type; the shipped
        wrappers' self-check must run the same command (BACKLOG: nothing else gates them)."""
        for name in ("feature-tasks", "bugfix-tasks", "refactor-tasks"):
            cmd = (SCAFFOLD_DIR / ".claude" / "commands" / f"{name}.md").read_text(encoding="utf-8")
            with self.subTest(name):
                m = re.search(r"validate-tasks\.py tasks/\S+ (--work-item \S+)", cmd)
                self.assertIsNotNone(m, "validator self-check without --work-item")

    def test_prompt_self_checks_run_the_gate_command(self):
        for name in ("feature-tasks", "bugfix-tasks", "refactor-tasks"):
            text = (REPO_ROOT / "prompts" / f"{name}.md").read_text(encoding="utf-8")
            with self.subTest(name):
                calls = re.findall(r"validate-tasks\.py tasks/\S+[^\n`]*", text)
                self.assertTrue(calls)
                for call in calls:
                    self.assertIn("--work-item", call)

    def test_shell_scripts_are_committed_with_lf_endings(self):
        for path in REPO_ROOT.glob("scripts/*.sh"):
            with self.subTest(path.name):
                self.assertNotIn(b"\r\n", path.read_bytes(),
                                 "CRLF breaks bash ('set: pipefail: invalid option name'); "
                                 ".gitattributes pins *.sh to LF")


if __name__ == "__main__":
    unittest.main()
