"""tools/validate-tasks.py - the task-list schema gate (step 2 of the pipeline).

Golden references under evals/cases/*/reference/ are the framework's own "known good"
task lists; the gate next-step.py prints must accept them. Synthetic lists probe each
rule in the docstring one at a time.
"""

import unittest

from helpers import CASES_DIR, FrameworkTestCase, run_tool, summary_counts, task_block

GOLDEN = {
    "FEAT": ("feature-tasks/case-001-task-labels", "FEAT-001-task-labels.md"),
    "BUG": ("bugfix-tasks/case-002-overdue-timezone", "BUG-001-overdue-filter-timezone.md"),
    "IMP": ("refactor-tasks/case-004-date-logic-extraction", "IMP-001-extract-date-logic.md"),
}


def validate(path, *args):
    return run_tool("validate-tasks", path, *args)


class GoldenReferences(unittest.TestCase):
    def golden(self, kind):
        case, wi = GOLDEN[kind]
        case_dir = CASES_DIR / case
        return (case_dir / "reference" / "tasks.md",
                case_dir / "input" / "docs" / "work-items" / wi,
                case_dir / "input")

    def test_feature_reference_is_clean_under_the_step_two_gate(self):
        tasks, wi, root = self.golden("FEAT")
        proc = validate(tasks, "--work-item", wi, "--root", root)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(summary_counts(proc.stdout), (0, 0))

    def test_bug_and_improvement_references_pass_the_step_two_gate(self):
        """The gate always passes --work-item; the coverage table is only recommended for
        BUG/IMP lists (bugfix-tasks.md, refactor-tasks.md), so its absence must be a
        warning here, not an error - otherwise the gate contradicts the prompts."""
        for kind in ("BUG", "IMP"):
            tasks, wi, root = self.golden(kind)
            with self.subTest(kind):
                proc = validate(tasks, "--work-item", wi, "--root", root)
                self.assertEqual(proc.returncode, 0, proc.stdout)
                errors, warnings = summary_counts(proc.stdout)
                self.assertEqual(errors, 0)
                self.assertIn("WARN", proc.stdout)
                self.assertIn("Acceptance Criteria Coverage", proc.stdout)
                strict = validate(tasks, "--work-item", wi, "--root", root, "--strict")
                self.assertEqual(strict.returncode, 1)
                plain = validate(tasks, "--root", root)
                self.assertEqual(plain.returncode, 0)

    def test_references_parse_to_the_expected_task_counts(self):
        for kind, expected in (("FEAT", 7), ("BUG", 5), ("IMP", 6)):
            tasks, _, root = self.golden(kind)
            proc = validate(tasks, "--root", root)
            self.assertIn(f"{expected} task(s)", proc.stdout, kind)


class SchemaRules(FrameworkTestCase):
    def write_list(self, wi_id, tasks, coverage=None):
        return self.p.task_list(wi_id, tasks, coverage=coverage)

    def run_list(self, wi_id, tasks, coverage=None, *extra):
        path = self.write_list(wi_id, tasks, coverage)
        return validate(path, "--root", self.p.root, *extra)

    def test_minimal_clean_list(self):
        proc = self.run_list("FEAT-001", [dict(id=1), dict(id=2, deps="T-001")])
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(summary_counts(proc.stdout), (0, 0))

    def test_missing_required_field_is_an_error(self):
        block = task_block(1).replace("**Rationale:**\nBecause.\n\n", "")
        path = self.p.write("tasks/FEAT-001-tasks.md", "# T\n\n" + block)
        proc = validate(path, "--root", self.p.root)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("missing required field 'Rationale'", proc.stdout)

    def test_enum_values_are_checked(self):
        for field, value, expect in (("type", "Frontendish", "Type 'Frontendish'"),
                                     ("workflow", "fast", "Workflow 'fast'"),
                                     ("complexity", "XXL", "Complexity 'XXL'")):
            with self.subTest(field):
                proc = self.run_list("FEAT-001", [dict(id=1, **{field: value})])
                self.assertEqual(proc.returncode, 1)
                self.assertIn(expect, proc.stdout)

    def test_prompt_specific_type_deltas_are_accepted(self):
        proc = self.run_list("BUG-001", [dict(id=1, type="Investigation",
                                              workflow="investigation-first"),
                                         dict(id=2, type="Cleanup", deps="T-001")])
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_duplicate_ids_error_and_gaps_warn(self):
        proc = self.run_list("FEAT-001", [dict(id=1), dict(id=1, title="again")])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("duplicate task ID", proc.stdout)
        proc = self.run_list("FEAT-001", [dict(id=1), dict(id=3)])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("sequence has gaps: T-002", proc.stdout)

    def test_dependency_rules(self):
        cases = [
            ([dict(id=1, deps="T-009")], 1, "depends on T-009, which is not in this file"),
            ([dict(id=1, deps="T-001")], 1, "depends on itself"),
            ([dict(id=1, deps="T-002"), dict(id=2, deps="T-001")], 1, "dependency cycle detected"),
            ([dict(id=1, deps="nothing really")], 1, "must be task IDs"),
            ([dict(id=1), dict(id=2, deps="after T-001 lands")], 0, "contains extra text"),
            ([dict(id=1), dict(id=2, deps="`T-001`")], 0, "0 error(s), 0 warning(s)"),
        ]
        for tasks, rc, expect in cases:
            with self.subTest(expect):
                proc = self.run_list("FEAT-001", tasks)
                self.assertEqual(proc.returncode, rc, proc.stdout)
                self.assertIn(expect, proc.stdout)

    def test_three_node_cycle_is_reported_once_per_entry(self):
        tasks = [dict(id=1, deps="T-003"), dict(id=2, deps="T-001"), dict(id=3, deps="T-002")]
        proc = self.run_list("FEAT-001", tasks)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("T-001 -> T-003 -> T-002 -> T-001", proc.stdout)

    def test_acceptance_criteria_need_checkboxes(self):
        block = task_block(1).replace("- [ ] It works", "It works")
        path = self.p.write("tasks/FEAT-001-tasks.md", "# T\n\n" + block)
        proc = validate(path, "--root", self.p.root)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("has no '- [ ]' checklist items", proc.stdout)

    def test_file_entries(self):
        self.p.write("src/existing.py", "x = 1\n")
        proc = self.run_list("FEAT-001", [dict(id=1, files=["src/existing.py",
                                                            "src/brand-new.py (new)"])])
        self.assertEqual(summary_counts(proc.stdout), (0, 0))
        proc = self.run_list("FEAT-001", [dict(id=1, files=["src/missing.py"])])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("does not exist under", proc.stdout)
        proc = self.run_list("FEAT-001", [dict(id=1, files=["[path/to/file]"])])
        self.assertIn("unfilled placeholder", proc.stdout)
        block = task_block(1).replace("- src/t001.py (new)\n", "")
        path = self.p.write("tasks/FEAT-001-tasks.md", "# T\n\n" + block)
        proc = validate(path, "--root", self.p.root)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("lists no files", proc.stdout)

    def test_fenced_code_is_ignored(self):
        text = "# T\n\n" + task_block(1) + "\n```markdown\n" + task_block(99) + "```\n"
        path = self.p.write("tasks/FEAT-001-tasks.md", text)
        proc = validate(path, "--root", self.p.root)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("1 task(s)", proc.stdout)

    def test_field_order_is_a_warning(self):
        block = task_block(1).replace("**Type:** Backend\n**Workflow:** standard",
                                      "**Workflow:** standard\n**Type:** Backend")
        path = self.p.write("tasks/FEAT-001-tasks.md", "# T\n\n" + block)
        proc = validate(path, "--root", self.p.root)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("out of canonical order", proc.stdout)
        self.assertEqual(validate(path, "--root", self.p.root, "--strict").returncode, 1)

    def test_no_task_blocks_is_an_error(self):
        path = self.p.write("tasks/FEAT-001-tasks.md", "# Nothing here\n\nTASK-1: wrong shape\n")
        proc = validate(path)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("no task blocks found", proc.stdout)

    def test_missing_files_exit_one(self):
        proc = validate(self.p.root / "tasks" / "nope.md")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("file not found", proc.stderr)
        path = self.write_list("FEAT-001", [dict(id=1)])
        proc = validate(path, "--work-item", self.p.root / "docs/work-items/nope.md")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("--work-item file not found", proc.stdout)


class CoverageCrossCheck(FrameworkTestCase):
    def setUp(self):
        super().setUp()
        self.wi = self.p.work_item("FEAT-001", acs=2)
        self.bug = self.p.work_item("BUG-001", acs=2, slug="bug")

    def run_with_wi(self, wi_id, tasks, coverage=None, wi_path=None, *extra):
        path = self.p.task_list(wi_id, tasks, coverage=coverage)
        return validate(path, "--root", self.p.root, "--work-item",
                        wi_path or (self.wi if wi_id.startswith("FEAT") else self.bug), *extra)

    def test_feature_without_coverage_table_fails_the_gate(self):
        proc = self.run_with_wi("FEAT-001", [dict(id=1)])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("no '## Acceptance Criteria Coverage' section", proc.stdout)

    def test_bug_without_coverage_table_warns_only(self):
        proc = self.run_with_wi("BUG-001", [dict(id=1, type="Investigation",
                                                 workflow="investigation-first")])
        self.assertEqual(proc.returncode, 0, proc.stdout)
        errors, warnings = summary_counts(proc.stdout)
        self.assertEqual((errors, warnings), (0, 1))
        self.assertIn("recommended for BUG", proc.stdout)

    def test_bug_with_coverage_table_is_fully_cross_checked(self):
        proc = self.run_with_wi("BUG-001", [dict(id=1)],
                                coverage=[("AC-1: a", "T-001"), ("AC-2: b", "T-009")])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("coverage row references T-009", proc.stdout)

    def test_complete_coverage_is_clean(self):
        proc = self.run_with_wi("FEAT-001", [dict(id=1), dict(id=2, deps="T-001")],
                                coverage=[("AC-1: a", "T-001"), ("AC-2: b", "T-001, T-002")])
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(summary_counts(proc.stdout), (0, 0))

    def test_row_count_mismatch_warns_and_empty_rows_error(self):
        proc = self.run_with_wi("FEAT-001", [dict(id=1)], coverage=[("AC-1: a", "T-001")])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("coverage table has 1 rows but the work item defines 2", proc.stdout)
        proc = self.run_with_wi("FEAT-001", [dict(id=1)],
                                coverage=[("AC-1: a", "T-001"), ("AC-2: b", "later")])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("coverage row has no task IDs", proc.stdout)

    def test_empty_coverage_table_is_an_error(self):
        proc = self.run_with_wi("FEAT-001", [dict(id=1)], coverage=[])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Coverage table has no rows", proc.stdout)

    def coverage_list(self, wi_id, header, rows):
        columns = header.count("|") - 1
        text = (f"# Task List: {wi_id}\n\n" + task_block(1) + task_block(2, deps="T-001")
                + "## Acceptance Criteria Coverage\n\n" + header + "\n"
                + "|" + "---|" * columns + "\n" + "\n".join(rows) + "\n")
        return self.p.write(f"tasks/{wi_id}-tasks.md", text)

    def test_annotated_header_row_is_not_a_coverage_row(self):
        """Caught by the baseline gate on its first run: the archived smoke sample's header
        reads '| Work Item AC (Section 9 success criteria) | Covered By |' and was counted
        as a data row with no task IDs."""
        path = self.coverage_list("FEAT-001",
                                  "| Work Item AC (Section 9 success criteria) | Covered By |",
                                  ["| AC-1: a | T-001 |", "| AC-2: b | T-002 |"])
        proc = validate(path, "--root", self.p.root, "--work-item", self.wi)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(summary_counts(proc.stdout), (0, 0))

    def test_covered_by_column_is_located_by_header_not_position(self):
        """Two archived samples add a 'How' column after 'Covered By'."""
        path = self.coverage_list("FEAT-001", "| Work Item AC | Covered By | How |",
                                  ["| AC-1: a | T-001 | migration plus repository |",
                                   "| AC-2: b | T-002 | endpoint handler |"])
        proc = validate(path, "--root", self.p.root, "--work-item", self.wi)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(summary_counts(proc.stdout), (0, 0))
        path = self.coverage_list("FEAT-001", "| Work Item AC | Description | Covered By |",
                                  ["| AC-1 | a | T-001 |", "| AC-2 | b | T-009 |"])
        proc = validate(path, "--root", self.p.root, "--work-item", self.wi)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("coverage row references T-009", proc.stdout)

    def test_work_item_without_acceptance_criteria_cannot_be_cross_checked(self):
        bare = self.p.write("docs/work-items/FEAT-002-bare.md",
                            "# Feature Brief: Bare\n\n| **ID** | FEAT-002 |\n")
        proc = self.run_with_wi("FEAT-002", [dict(id=1)], coverage=[("AC-1", "T-001")],
                                wi_path=bare)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("cannot cross-check coverage", proc.stdout)


if __name__ == "__main__":
    unittest.main()
