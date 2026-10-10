"""evals/run-evals.py - the deterministic assertion checker behind every eval case.

Generation is stochastic and billable, so CI never runs it; the checker is what makes a
baseline comparable across prompt edits. These tests exercise every check type against
a temp case built from the committed case-001 fixture and its golden reference.
"""

import json
import shutil
import unittest

from helpers import CASES_DIR, EVALS_DIR, FrameworkTestCase, PY, load_tool, run_tool

re_mod = load_tool("run-evals", EVALS_DIR)

CASE_001 = CASES_DIR / "feature-tasks" / "case-001-task-labels"
WORK_ITEM = "input/docs/work-items/FEAT-001-task-labels.md"
NO_JUDGE = {"enabled": False, "cmd": "", "timeout": 10, "samples": 1}


class CheckTypes(FrameworkTestCase):
    def setUp(self):
        super().setUp()
        self.case = self.tmp / "case"
        shutil.copytree(CASE_001 / "input", self.case / "input")
        self.reference = (CASE_001 / "reference" / "tasks.md").read_text(encoding="utf-8")
        self.out = self.case / "output" / "tasks.md"
        self.out.parent.mkdir()
        self.set_output(self.reference)

    def set_output(self, text):
        self.out.write_text(text, encoding="utf-8")
        self.text = text

    def check(self, **spec):
        return re_mod.run_check(spec, self.case, self.text, self.out, NO_JUDGE)

    def test_validator_check_passes_on_the_golden_reference_and_fails_on_a_broken_list(self):
        status, detail = self.check(type="validator", work_item=WORK_ITEM, root="input")
        self.assertEqual((status, detail), ("PASS", "validator clean"))
        self.set_output(self.reference.replace("**Type:** Database", "**Type:** Storage", 1))
        status, detail = self.check(type="validator", work_item=WORK_ITEM, root="input")
        self.assertEqual(status, "FAIL")
        self.assertIn("Type 'Storage'", detail)

    def test_task_count(self):
        self.assertEqual(self.check(type="task_count", min=6, max=16)[0], "PASS")
        status, detail = self.check(type="task_count", min=10, max=16)
        self.assertEqual(status, "FAIL")
        self.assertIn("7 tasks, expected 10-16", detail)

    def test_must_match_and_must_not_match(self):
        self.assertEqual(self.check(type="must_match",
                                    pattern="## Acceptance Criteria Coverage")[0], "PASS")
        status, detail = self.check(type="must_match", pattern="(?i)kubernetes", reason="why")
        self.assertEqual(status, "FAIL")
        self.assertIn("why (pattern:", detail)
        self.assertEqual(self.check(type="must_not_match", pattern="(?i)angular")[0], "PASS")
        self.assertEqual(self.check(type="must_not_match", pattern="T-001")[0], "FAIL")

    def test_paths_exist_catches_invented_files_and_placeholders(self):
        self.assertEqual(self.check(type="paths_exist", root="input")[0], "PASS")
        self.set_output(self.text.replace("**Files to Modify/Create:**\n",
                                          "**Files to Modify/Create:**\n- src/nope.ts\n"
                                          "- src/[module]/file.ts - todo\n", 1))
        status, detail = self.check(type="paths_exist", root="input")
        self.assertEqual(status, "FAIL")
        self.assertIn("src/nope.ts", detail)
        self.assertIn("src/[module]/file.ts (placeholder)", detail)

    def test_paths_exist_without_allow_new_rejects_new_files(self):
        status, detail = self.check(type="paths_exist", root="input", allow_new=False)
        self.assertEqual(status, "FAIL")

    def test_shard_refs_resolve_sanctioning_rules(self):
        self.assertEqual(self.check(type="shard_refs_resolve", root="input",
                                    sanctioned_by=[WORK_ITEM])[0], "PASS")
        self.set_output(self.text + "\nSee docs/api-spec/endpoints/ghost.md for details.\n")
        status, detail = self.check(type="shard_refs_resolve", root="input",
                                    sanctioned_by=[WORK_ITEM])
        self.assertEqual(status, "FAIL")
        self.assertIn("docs/api-spec/endpoints/ghost.md", detail)
        self.set_output(self.text.replace("ghost.md for details.", "ghost.md (new) for details."))
        self.assertEqual(self.check(type="shard_refs_resolve", root="input")[0], "PASS")

    def test_shard_refs_sanctioned_elsewhere_in_the_document(self):
        text = self.reference + "\nAlso docs/data-model/entities/sticker.md here.\n" \
                                "\n- docs/data-model/entities/sticker.md (new)\n"
        self.set_output(text)
        self.assertEqual(self.check(type="shard_refs_resolve", root="input",
                                    sanctioned_by=[WORK_ITEM])[0], "PASS")

    def test_line_count_and_files_exist(self):
        n = len(self.text.splitlines())
        self.assertEqual(self.check(type="line_count", min=n, max=n)[0], "PASS")
        status, detail = self.check(type="line_count", max=10)
        self.assertEqual(status, "FAIL")
        self.assertIn("output budgets", detail)
        self.assertEqual(self.check(type="files_exist", base="output",
                                    paths=["tasks.md"])[0], "PASS")
        status, detail = self.check(type="files_exist", base="output", paths=["plan.md"])
        self.assertEqual(status, "FAIL")
        self.assertIn("plan.md", detail)

    def test_spec_validator_on_a_tree_and_with_an_overlay(self):
        status, detail = self.check(type="spec_validator", root="input", strict=True)
        self.assertEqual((status, detail), ("PASS", "validate-specs clean"))
        # overlay: an output tree holding only a screen that references input endpoints
        screen = (self.case / "output" / "docs" / "ui-specification" / "screens" / "report.md")
        screen.parent.mkdir(parents=True)
        screen.write_text("---\nkind: screen\nscreen: report\nendpoints: [tasks]\n---\n\n"
                          "# Screen\n\n> **Last verified against code:** 2026-07-14\n",
                          encoding="utf-8")
        (self.case / "output" / "docs" / "ui-specification" / "index.md").write_text(
            "# UI\n\n> **Last verified against code:** 2026-07-14\n\n`screens/report.md` "
            "`screens/project-board.md` `screens/task-detail-panel.md`\n", encoding="utf-8")
        status, detail = self.check(type="spec_validator", root="output", overlay=["input"])
        self.assertEqual(status, "PASS", detail)
        self.assertIn("merged overlay root", detail)
        status, detail = self.check(type="spec_validator", root="output")
        self.assertEqual(status, "FAIL")  # without the overlay the endpoint ref dangles

    def test_judge_is_skipped_unless_enabled(self):
        status, detail = self.check(type="judge", rubric="rubric.md")
        self.assertEqual(status, "SKIP")
        self.assertIn("--judge", detail)

    def test_unknown_check_type_fails(self):
        status, detail = self.check(type="telepathy")
        self.assertEqual(status, "FAIL")
        self.assertIn("unknown check type", detail)


class JudgeHarness(FrameworkTestCase):
    """The judge command is a template; a scripted judge makes the harness testable."""

    def setUp(self):
        super().setUp()
        self.case = self.tmp / "case"
        self.case.mkdir()
        (self.case / "rubric.md").write_text("# Rubric\n\nScore 1-10.\n", encoding="utf-8")
        (self.case / "reference.md").write_text("# Reference\n", encoding="utf-8")
        (self.case / "ground.md").write_text("convention: snake_case\n", encoding="utf-8")
        if any(" " in str(p) for p in (PY, self.tmp)):
            self.skipTest("scripted judge needs whitespace-free paths for a shell template")

    def judge_cmd(self, body):
        script = self.tmp / "judge.py"
        script.write_text(body, encoding="utf-8")
        return f"{PY} {script} {{prompt_file}}"

    def run_judge(self, body, samples=1, **spec):
        opts = {"enabled": True, "cmd": self.judge_cmd(body), "timeout": 60, "samples": samples}
        check = dict(type="judge", rubric="rubric.md", reference="reference.md",
                     context=["ground.md"], min_score=7)
        check.update(spec)
        return re_mod.run_judge(check, self.case, "candidate text", opts)

    def test_scripted_judge_scores_are_parsed_and_the_prompt_embeds_everything(self):
        body = ("import sys, pathlib\n"
                "t = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')\n"
                "assert 'Score 1-10' in t and 'convention: snake_case' in t\n"
                "assert '# Reference' in t and 'candidate text' in t\n"
                "print('Looks good.')\n"
                "print('{\"score\": 8, \"reasons\": [\"solid\", \"grounded\"]}')\n")
        status, detail = self.run_judge(body)
        self.assertEqual(status, "PASS", detail)
        self.assertIn("score 8/10 (min 7)", detail)
        self.assertIn("solid", detail)
        self.assertTrue((self.case / "output" / "judge-prompt.md").is_file())
        status, detail = self.run_judge(body, min_score=9)
        self.assertEqual(status, "FAIL")

    def test_median_of_n_samples(self):
        body = ("import sys, pathlib\n"
                "c = pathlib.Path(sys.argv[1]).with_name('calls')\n"
                "n = int(c.read_text()) + 1 if c.exists() else 1\n"
                "c.write_text(str(n))\n"
                "print('{\"score\": %d, \"reasons\": []}' % [5, 9, 6][n - 1])\n")
        status, detail = self.run_judge(body, samples=3)
        self.assertEqual(status, "FAIL", detail)
        self.assertIn("score 6/10", detail)
        self.assertIn("[runs: 5, 9, 6]", detail)

    def test_judge_without_json_fails_after_retries(self):
        status, detail = self.run_judge("print('no verdict here')\n")
        self.assertEqual(status, "FAIL")
        self.assertIn("after 3 attempts", detail)

    def test_missing_rubric_or_reference_fails(self):
        (self.case / "rubric.md").unlink()
        status, detail = self.run_judge("print('{\"score\": 9}')\n")
        self.assertEqual(status, "FAIL")
        self.assertIn("rubric not found", detail)


class Helpers(FrameworkTestCase):
    def test_read_output_concatenates_directories_with_file_headers(self):
        out = self.tmp / "out"
        (out / "docs").mkdir(parents=True)
        (out / "docs" / "b.md").write_text("B\n", encoding="utf-8")
        (out / "a.md").write_text("A\n", encoding="utf-8")
        (out / "judge-prompt.md").write_text("ignored\n", encoding="utf-8")
        text = re_mod.read_output(out)
        self.assertIn("<!-- FILE: a.md -->\nA", text)
        self.assertIn("<!-- FILE: docs/b.md -->\nB", text)
        self.assertNotIn("ignored", text)
        self.assertIsNone(re_mod.read_output(self.tmp / "missing"))
        empty = self.tmp / "empty"
        empty.mkdir()
        (empty / ".gitkeep").touch()
        self.assertIsNone(re_mod.read_output(empty))  # a dir with no .md files

    def test_extract_file_entries_stops_at_the_next_field(self):
        text = ("**Files to Modify/Create:**\n- src/a.py (new) - thing\n- `src/b.py`\n"
                "- [ ] not a file\n**Technical Notes:** x\n- src/c.py\n")
        self.assertEqual(re_mod.extract_file_entries(text),
                         [("src/a.py", True), ("src/b.py", False)])


class CommandLine(unittest.TestCase):
    def test_list_discovers_the_shipped_cases(self):
        proc = run_tool("run-evals", "--list", directory=EVALS_DIR)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        names = proc.stdout.split()
        self.assertGreaterEqual(len(names), 10)
        self.assertTrue(any(n.endswith("case-001-task-labels") for n in names))

    def test_unknown_case_filter_exits_one(self):
        proc = run_tool("run-evals", "--case", "no-such-case-xyz", directory=EVALS_DIR)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("no eval cases found", proc.stderr)

    def test_every_assertions_file_is_well_formed(self):
        for path in sorted(CASES_DIR.glob("*/*/assertions.json")):
            with self.subTest(path.parent.name):
                spec = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("output", spec)
                for check in spec["checks"]:
                    self.assertIn(check["type"], {
                        "validator", "spec_validator", "files_exist", "task_count",
                        "line_count", "must_match", "must_not_match", "paths_exist",
                        "shard_refs_resolve", "judge"})
                    if check["type"] == "judge":
                        self.assertTrue((path.parent / check.get("rubric", "rubric.md")).is_file())
                        for rel in check.get("context", []):
                            self.assertTrue((path.parent / rel).is_file(), rel)


if __name__ == "__main__":
    unittest.main()
