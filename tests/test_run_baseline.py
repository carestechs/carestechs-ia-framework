"""evals/run-baseline.py - archiving samples and rescoring them without a model.

`--rescore LABEL` re-checks archived samples with today's checker and validators at zero
token cost, which makes the committed baselines a regression corpus for the tooling
itself. `--gate` turns that into a CI exit code. The end-to-end test builds a miniature
framework repo (tools + evals) so the real scripts run against each other.
"""

import json
import shutil
import unittest

from helpers import (BASELINES_DIR, CASES_DIR, EVALS_DIR, PY, TOOLS_DIR, FrameworkTestCase,
                     load_tool, run)

rb = load_tool("run-baseline", EVALS_DIR)


class OutputHelpers(FrameworkTestCase):
    def test_restore_into_an_existing_output_dir_with_gitkeep(self):
        """Directory outputs keep a tracked output/.gitkeep anchor, so restoring an archived
        sample used to raise FileExistsError and abort the whole rescore."""
        sample = self.tmp / "sample-1"
        (sample / "docs").mkdir(parents=True)
        (sample / "docs" / "index.md").write_text("# I\n", encoding="utf-8")
        out = self.tmp / "output"
        out.mkdir()
        (out / ".gitkeep").touch()
        rb.restore_output(sample, out)
        self.assertTrue((out / "docs" / "index.md").is_file())
        self.assertTrue((out / ".gitkeep").is_file())
        rb.remove_output(out)
        self.assertEqual([p.name for p in out.iterdir()], [".gitkeep"])

    def test_restore_a_file_sample_creates_missing_parents(self):
        sample = self.tmp / "sample-1.md"
        sample.write_text("x\n", encoding="utf-8")
        out = self.tmp / "case" / "output" / "tasks.md"
        rb.restore_output(sample, out)
        self.assertEqual(out.read_text(encoding="utf-8"), "x\n")
        rb.remove_output(out)
        self.assertFalse(out.exists())

    def test_output_present_ignores_runner_scratch(self):
        out = self.tmp / "output"
        out.mkdir()
        (out / ".gitkeep").touch()
        (out / "judge-prompt.md").write_text("scratch", encoding="utf-8")
        self.assertFalse(rb.output_present(out))
        (out / "docs.md").write_text("real", encoding="utf-8")
        self.assertTrue(rb.output_present(out))
        self.assertFalse(rb.output_present(self.tmp / "missing"))

    def test_archive_output_excludes_the_judge_prompt(self):
        out = self.tmp / "output"
        (out / "docs").mkdir(parents=True)
        (out / "docs" / "a.md").write_text("a", encoding="utf-8")
        (out / "judge-prompt.md").write_text("scratch", encoding="utf-8")
        rb.archive_output(out, self.tmp / "label" / "case" / "sample-1")
        archived = self.tmp / "label" / "case" / "sample-1"
        self.assertTrue((archived / "docs" / "a.md").is_file())
        self.assertFalse((archived / "judge-prompt.md").exists())
        single = self.tmp / "single.html"
        single.write_text("<html>", encoding="utf-8")
        rb.archive_output(single, self.tmp / "label" / "case2" / "sample-1")
        self.assertTrue((self.tmp / "label" / "case2" / "sample-1.html").is_file())


class ReferenceComparison(unittest.TestCase):
    def results(self, status, sample="sample-1.md", ctype="validator"):
        return {"case-x": [{"sample": sample, "generated": True,
                            "checks": [{"status": status, "type": ctype, "detail": "d"}]}]}

    def reference(self, status, sample=1, ctype="validator"):
        return {"case-x": {"samples": [{"sample": sample, "generated": True,
                                        "checks": [{"status": status, "type": ctype,
                                                    "detail": "d"}]}]}}

    def test_pass_to_fail_is_a_regression(self):
        regs = rb.compare_to_reference(self.results("FAIL"), self.reference("PASS"))
        self.assertEqual(len(regs), 1)
        self.assertIn("was PASS, now FAIL", regs[0][3])

    def test_recorded_failures_and_skips_do_not_regress(self):
        self.assertEqual(rb.compare_to_reference(self.results("FAIL"), self.reference("FAIL")), [])
        self.assertEqual(rb.compare_to_reference(self.results("SKIP"), self.reference("PASS")), [])
        self.assertEqual(rb.compare_to_reference(self.results("PASS"), self.reference("FAIL")), [])

    def test_sample_names_match_generation_time_indexes(self):
        """results.json stores sample 1; a rescore stores 'sample-1.md' or 'sample-1'."""
        for name in ("sample-1.md", "sample-1", "sample-1.html"):
            self.assertEqual(rb.compare_to_reference(self.results("FAIL", sample=name),
                                                     self.reference("FAIL", sample=1)), [])
        regs = rb.compare_to_reference(self.results("FAIL", sample="sample-2.md"),
                                       self.reference("FAIL", sample=1))
        self.assertEqual(len(regs), 1)
        self.assertIn("unrecorded", regs[0][3])

    def test_unrecorded_failing_checks_count(self):
        regs = rb.compare_to_reference(self.results("FAIL", ctype="task_count"),
                                       self.reference("FAIL", ctype="validator"))
        self.assertEqual(len(regs), 1)
        self.assertIn("unrecorded", regs[0][3])
        regs = rb.compare_to_reference(self.results("FAIL"), {})
        self.assertEqual(len(regs), 1)


class MiniRepo(FrameworkTestCase):
    """A copy of the two eval scripts plus the validators, with one file-output case and
    one directory-output case, each with an archived sample and recorded results."""

    def setUp(self):
        super().setUp()
        self.repo = self.tmp / "repo"
        tools = self.repo / "tools"
        tools.mkdir(parents=True)
        for name in ("validate-tasks.py", "validate-specs.py"):
            shutil.copy(TOOLS_DIR / name, tools / name)
        evals = self.repo / "evals"
        evals.mkdir()
        for name in ("run-evals.py", "run-baseline.py"):
            shutil.copy(EVALS_DIR / name, evals / name)

        # file-output case: case-001's fixture + its golden reference as the archived sample
        src = CASES_DIR / "feature-tasks" / "case-001-task-labels"
        case = evals / "cases" / "feature-tasks" / "case-f"
        shutil.copytree(src / "input", case / "input")
        (case / "output").mkdir()
        (case / "output" / ".gitkeep").touch()
        (case / "assertions.json").write_text(json.dumps({
            "output": "output/tasks.md",
            "checks": [
                {"type": "validator", "root": "input",
                 "work_item": "input/docs/work-items/FEAT-001-task-labels.md"},
                {"type": "task_count", "min": 5, "max": 10},
                {"type": "must_match", "pattern": "## Acceptance Criteria Coverage"},
                {"type": "judge", "rubric": "rubric.md", "min_score": 7},
            ]}), encoding="utf-8")
        (case / "rubric.md").write_text("rubric\n", encoding="utf-8")
        shutil.copy(src / "reference" / "tasks.md",
                    self.archive("lbl", "case-f", "sample-1.md"))

        # directory-output case: assertions like case-005, sample from the v2.4.6 archive
        dcase = evals / "cases" / "spec-generation" / "case-d"
        (dcase / "input").mkdir(parents=True)
        (dcase / "output").mkdir()
        (dcase / "output" / ".gitkeep").touch()
        (dcase / "assertions.json").write_text(json.dumps({
            "output": "output",
            "checks": [
                {"type": "spec_validator", "root": "output", "strict": True},
                {"type": "files_exist", "base": "output",
                 "paths": ["docs/data-model/index.md", "docs/data-model/entities/task.md"]},
            ]}), encoding="utf-8")
        archived = BASELINES_DIR / "v2.4.6-spec-gen" / "case-005-data-model-from-strategy" / "sample-1"
        shutil.copytree(archived, self.archive("lbl", "case-d", "sample-1"))

        self.results_path = evals / "baselines" / "lbl" / "results.json"
        self.results_path.write_text(json.dumps({"label": "lbl", "cases": {
            "case-f": {"samples": [{"sample": 1, "generated": True, "checks": [
                {"status": "PASS", "type": "validator", "detail": ""},
                {"status": "PASS", "type": "task_count", "detail": ""},
                {"status": "PASS", "type": "must_match", "detail": ""},
                {"status": "PASS", "type": "judge", "detail": "score 9/10"}]}]},
            "case-d": {"samples": [{"sample": 1, "generated": True, "checks": [
                {"status": "PASS", "type": "spec_validator", "detail": ""},
                {"status": "PASS", "type": "files_exist", "detail": ""}]}]},
        }}), encoding="utf-8")

    def archive(self, label, case, name):
        p = self.repo / "evals" / "baselines" / label / case / name
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def baseline(self, *args):
        return run([PY, self.repo / "evals" / "run-baseline.py", *args], cwd=self.repo)

    def test_rescore_handles_file_and_directory_outputs_and_restores_the_tree(self):
        proc = self.baseline("--rescore", "lbl")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("[case-f] sample-1.md: PASS", proc.stdout)
        self.assertIn("[case-d] sample-1: PASS", proc.stdout)
        rescored = json.loads((self.repo / "evals/baselines/lbl/results-rescored.json")
                              .read_text(encoding="utf-8"))
        self.assertEqual(rescored["cases"]["case-d"]["pass_rate"], "100%")
        for case in ("feature-tasks/case-f", "spec-generation/case-d"):
            out = self.repo / "evals" / "cases" / case / "output"
            self.assertEqual([p.name for p in out.iterdir()], [".gitkeep"], case)

    def test_gate_passes_when_nothing_regressed_and_writes_nothing(self):
        proc = self.baseline("--rescore", "lbl", "--gate")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("no regressions", proc.stdout)
        self.assertFalse((self.repo / "evals/baselines/lbl/results-rescored.json").exists())

    def test_gate_fails_on_a_regression_and_names_it(self):
        sample = self.repo / "evals/baselines/lbl/case-f/sample-1.md"
        text = sample.read_text(encoding="utf-8").replace("## Acceptance Criteria Coverage",
                                                           "## Coverage")
        sample.write_text(text, encoding="utf-8")
        proc = self.baseline("--rescore", "lbl", "--gate")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("REGRESSION", proc.stdout)
        self.assertIn("case-f", proc.stdout)
        self.assertIn("must_match", proc.stdout)
        self.assertIn("validator", proc.stdout)  # FEAT list lost its table: gate error too

    def test_gate_prefers_rescored_results_as_reference(self):
        ref = json.loads(self.results_path.read_text(encoding="utf-8"))
        ref["cases"]["case-f"]["samples"][0]["checks"][2]["status"] = "FAIL"
        (self.results_path.with_name("results-rescored.json")).write_text(json.dumps(ref),
                                                                           encoding="utf-8")
        sample = self.repo / "evals/baselines/lbl/case-f/sample-1.md"
        sample.write_text(sample.read_text(encoding="utf-8").replace(
            "## Acceptance Criteria Coverage", "## Coverage"), encoding="utf-8")
        proc = self.baseline("--rescore", "lbl", "--gate")
        # must_match was already failing in the rescored reference; only the validator regressed
        self.assertEqual(proc.returncode, 1)
        named = [line for line in proc.stdout.splitlines()
                 if line.strip().startswith("REGRESSION ")]
        self.assertEqual(len(named), 1, proc.stdout)
        self.assertIn("validator", named[0])
        self.assertIn("results-rescored.json", proc.stdout)

    def test_unknown_label_exits_one(self):
        proc = self.baseline("--rescore", "nope")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("no baseline named", proc.stderr)
        proc = self.baseline("--gate")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("--gate requires --rescore", proc.stderr)


if __name__ == "__main__":
    unittest.main()
