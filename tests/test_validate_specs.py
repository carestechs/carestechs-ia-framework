"""tools/validate-specs.py - the cross-shard consistency and freshness linter.

The eval fixtures double as integration cases (every frozen fixture must lint clean with
staleness disabled - evals/README.md). A synthetic three-spec project probes each rule.
"""

import datetime
import unittest

from helpers import CASES_DIR, FrameworkTestCase, SCAFFOLD_DIR, run_tool, summary_counts

TODAY = datetime.date.today().isoformat()


def validate(root, *args):
    return run_tool("validate-specs", "--root", root, *args)


def stamp(date=TODAY):
    return f"> **Last verified against code:** {date} (commit `abc1234`)\n"


class SpecProject:
    """Builds a minimal, internally consistent sharded docs/ tree."""

    def __init__(self, project, date=TODAY):
        self.p = project
        self.date = date
        self.p.write("docs/ARCHITECTURE.md", "# Architecture\n\n" + stamp(date))
        self.p.write("docs/data-model/index.md",
                     "# Data Model\n\n" + stamp(date) +
                     "\n## 2. Module Ownership\n\n| Module | Entities |\n|---|---|\n"
                     "| Projects | Task (`entities/task.md`) |\n")
        self.entity("task", "Task", endpoints="[tasks]", screens="[board]")
        self.p.write("docs/api-spec/index.md",
                     "# API\n\n" + stamp(date) +
                     "\n## Endpoint Summary\n\n| Resource | Shard |\n|---|---|\n"
                     "| tasks | `endpoints/tasks.md` |\n")
        self.resource("tasks", entities="[task]")
        self.p.write("docs/ui-specification/index.md",
                     "# UI\n\n" + stamp(date) +
                     "\n## Screens\n\n| Screen | Shard |\n|---|---|\n"
                     "| Board | `screens/board.md` |\n")
        self.screen("board", endpoints="[tasks]")
        self.p.write("docs/ui-specification/components.md",
                     "---\nkind: component-inventory\n---\n\n# Components\n\n" + stamp(date))

    def entity(self, file, name, endpoints="[]", screens="[]", kind="entity", extra=""):
        return self.p.write(
            f"docs/data-model/entities/{file}.md",
            f"---\nkind: {kind}\nname: {name}\nmodule: Projects\nendpoints: {endpoints}\n"
            f"screens: {screens}\n{extra}---\n\n# Entity: {name}\n\n" + stamp(self.date))

    def resource(self, file, entities="[]", kind="resource", name=None):
        return self.p.write(
            f"docs/api-spec/endpoints/{file}.md",
            f"---\nkind: {kind}\nresource: {name or file}\nentities: {entities}\n---\n\n"
            f"# Resource\n\n" + stamp(self.date))

    def screen(self, file, endpoints="[]", kind="screen", name=None):
        return self.p.write(
            f"docs/ui-specification/screens/{file}.md",
            f"---\nkind: {kind}\nscreen: {name or file}\nendpoints: {endpoints}\n---\n\n"
            f"# Screen\n\n" + stamp(self.date))


class Fixtures(unittest.TestCase):
    SHARDED = [
        "feature-tasks/case-001-task-labels",
        "bugfix-tasks/case-002-overdue-timezone",
        "review-tasks/case-003-review-flawed-tasks",
        "refactor-tasks/case-004-date-logic-extraction",
        "ui-spec-generation/case-007-ui-spec-from-specs",
    ]

    def test_every_frozen_fixture_lints_clean_with_staleness_off(self):
        for case in self.SHARDED:
            with self.subTest(case):
                proc = validate(CASES_DIR / case / "input", "--max-age", "0", "--strict")
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertEqual(summary_counts(proc.stdout), (0, 0))

    def test_fixtures_without_sharded_specs_are_reported_not_passed(self):
        for case in ("feature-tasks/case-901-task-labels-minimal-context",
                     "spec-generation/case-005-data-model-from-strategy"):
            with self.subTest(case):
                proc = validate(CASES_DIR / case / "input", "--max-age", "0")
                self.assertEqual(proc.returncode, 1)
                self.assertIn("no sharded spec directories found", proc.stderr)

    def test_scaffold_has_no_errors_and_only_unfilled_stamp_warnings(self):
        proc = validate(SCAFFOLD_DIR)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        errors, warnings = summary_counts(proc.stdout)
        self.assertEqual(errors, 0)
        for line in proc.stdout.splitlines():
            if "WARN" in line:
                self.assertIn("not filled with a date", line)
        self.assertEqual(validate(SCAFFOLD_DIR, "--strict").returncode, 1)


class Rules(FrameworkTestCase):
    def setUp(self):
        super().setUp()
        self.spec = SpecProject(self.p)

    def lint(self, *args):
        return validate(self.p.root, *args)

    def test_consistent_project_is_clean(self):
        proc = self.lint()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(summary_counts(proc.stdout), (0, 0))
        self.assertIn("4 shard(s) checked", proc.stdout)

    def test_kind_must_match_directory(self):
        self.spec.entity("task", "Task", kind="resource")
        proc = self.lint()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("kind is 'resource', expected 'entity'", proc.stdout)

    def test_name_key_must_match_filename_in_kebab_case(self):
        self.spec.entity("task", "TaskItem")
        proc = self.lint()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("does not match filename 'task' (expected 'task-item')", proc.stdout)
        self.spec.entity("task", "Task")
        self.spec.entity("task-label", "TaskLabel")
        self.p.write("docs/data-model/index.md", "# DM\n\n" + stamp() +
                     "`entities/task.md` and `entities/task-label.md`\n")
        self.assertEqual(self.lint().returncode, 0)

    def test_cross_references_must_resolve(self):
        self.spec.entity("task", "Task", endpoints="[tasks, labels]")
        proc = self.lint()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("references 'labels' but docs/api-spec/endpoints/labels.md does not exist",
                      proc.stdout)

    def test_reference_keys_must_be_inline_arrays(self):
        self.spec.entity("task", "Task", endpoints="tasks")
        proc = self.lint()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("must be an inline array", proc.stdout)

    def test_unfilled_placeholders_warn(self):
        self.spec.entity("task", "Task", endpoints="[tasks, [endpoint-name]]")
        proc = self.lint()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("unfilled entry", proc.stdout)
        self.spec.entity("task", "[EntityName]")
        self.assertIn("looks unfilled", self.lint().stdout)

    def test_frontmatter_parse_errors(self):
        self.p.write("docs/data-model/entities/task.md",
                     "---\nkind: entity\nname: Task\nendpoints: [tasks\n---\n" + stamp())
        self.assertIn("inline arrays must close on the same line", self.lint().stdout)
        self.p.write("docs/data-model/entities/task.md",
                     "---\nkind: entity\nname: Task\njust words\n---\n" + stamp())
        self.assertIn("is not 'key: value'", self.lint().stdout)
        self.p.write("docs/data-model/entities/task.md", "---\nkind: entity\nname: Task\n" + stamp())
        self.assertIn("never closed", self.lint().stdout)

    def test_missing_frontmatter_is_a_warning_not_an_error(self):
        self.p.write("docs/data-model/entities/task.md", "# Entity: Task\n\n" + stamp())
        proc = self.lint()
        self.assertEqual(proc.returncode, 0)
        self.assertIn("no frontmatter", proc.stdout)

    def test_index_references_must_exist_unless_marked_new(self):
        self.p.write("docs/data-model/index.md", "# DM\n\n" + stamp() +
                     "`entities/task.md`, `entities/label.md`\n")
        proc = self.lint()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("references data-model/entities/label.md, which does not exist", proc.stdout)
        self.p.write("docs/data-model/index.md", "# DM\n\n" + stamp() +
                     "`entities/task.md`\n`entities/label.md` (new)\n")
        self.assertEqual(self.lint().returncode, 0)

    def test_html_comments_are_not_references(self):
        """v2.7.0: template guidance inside <!-- --> must never fail validation."""
        self.p.write("docs/data-model/index.md", "# DM\n\n" + stamp() +
                     "`entities/task.md`\n<!-- e.g. `entities/login.md`,\n"
                     "`entities/ghost.md` -->\n")
        proc = self.lint()
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_shard_absent_from_its_index_warns(self):
        self.spec.entity("project", "Project")
        proc = self.lint()
        self.assertEqual(proc.returncode, 0)
        self.assertIn("existing shard entities/project.md is not mentioned", proc.stdout)

    def test_missing_index_is_an_error(self):
        (self.p.root / "docs/api-spec/index.md").unlink()
        proc = self.lint()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("missing index.md", proc.stdout)

    def test_component_inventory_kind(self):
        self.p.write("docs/ui-specification/components.md",
                     "---\nkind: screen\n---\n\n# C\n\n" + stamp())
        proc = self.lint()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("expected 'component-inventory'", proc.stdout)

    def test_work_item_shard_references(self):
        self.p.write("docs/work-items/FEAT-001-x.md",
                     "# Brief\n\n- docs/api-spec/endpoints/tasks.md\n"
                     "- docs/api-spec/endpoints/labels.md\n")
        proc = self.lint()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("references docs/api-spec/endpoints/labels.md, which does not exist",
                      proc.stdout)
        self.p.write("docs/work-items/FEAT-001-x.md",
                     "# Brief\n\n- docs/api-spec/endpoints/labels.md (new)\n"
                     "<!-- docs/api-spec/endpoints/example.md -->\n")
        self.assertEqual(self.lint().returncode, 0)
        self.p.write("docs/work-items/TEMPLATE-feature-brief.md",
                     "- docs/api-spec/endpoints/anything.md\n")
        self.assertEqual(self.lint().returncode, 0)

    def test_no_docs_directory_exits_one(self):
        proc = validate(self.tmp / "empty")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("no docs/ directory", proc.stderr)


class Freshness(FrameworkTestCase):
    def test_stale_stamp_warns_and_max_age_zero_disables(self):
        old = (datetime.date.today() - datetime.timedelta(days=100)).isoformat()
        SpecProject(self.p, date=old)
        proc = validate(self.p.root)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("100 days old (max 30)", proc.stdout)
        self.assertEqual(validate(self.p.root, "--strict").returncode, 1)
        proc = validate(self.p.root, "--max-age", "0", "--strict")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        proc = validate(self.p.root, "--max-age", "365")
        self.assertEqual(summary_counts(proc.stdout), (0, 0))

    def test_missing_unfilled_and_invalid_stamps_warn(self):
        SpecProject(self.p)
        self.p.write("docs/ARCHITECTURE.md", "# Architecture without a stamp\n")
        self.assertIn("missing freshness stamp", validate(self.p.root).stdout)
        self.p.write("docs/ARCHITECTURE.md", "> **Last verified against code:** YYYY-MM-DD\n")
        self.assertIn("not filled with a date", validate(self.p.root).stdout)
        self.p.write("docs/ARCHITECTURE.md", "> **Last verified against code:** 2026-13-45\n")
        self.assertIn("date is invalid", validate(self.p.root).stdout)


if __name__ == "__main__":
    unittest.main()
