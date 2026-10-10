"""Regression suite for tools/next-step.py - the pipeline's sequencing authority.

Each test builds a real framework project in a temp git repo and reads the tool's
--json report, so what is tested is the published contract (orchestrator-integration.md
section 8), not internals. The historical cases are the trapped states each CHANGELOG
fix cites; their fixtures used to live in gitignored .fx*/ folders and were lost - they
are rebuilt here so the fixes stay fixed.
"""

import json
import unittest

from helpers import FrameworkTestCase, Project, first_step, states, steps


def three_tasks():
    """Database -> Backend -> Documentation(S) chain, disjoint file sets."""
    return [
        dict(id=1, title="Create label schema", type="Database", complexity="M",
             files=["src/db/label.py (new)"]),
        dict(id=2, title="Label endpoints", type="Backend", deps="T-001", complexity="M",
             files=["src/api/labels.py (new)"]),
        dict(id=3, title="Document label endpoints", type="Documentation", deps="T-002",
             complexity="S", files=["docs/api-spec/index.md"]),
    ]


class PipelineBase(FrameworkTestCase):
    WI = "FEAT-001"

    def open_frontier(self, tasks=None, wi_id=None):
        """Work item + committed task list + approved task-list review => steps 4-8."""
        wi_id = wi_id or self.WI
        self.p.work_item(wi_id)
        self.p.task_list(wi_id, tasks or three_tasks())
        if not (self.p.root / ".git").exists():
            self.p.init_git()
        self.p.commit(f"tasks({wi_id}): generate task list")
        self.p.review(f"tasks/{wi_id}-review.md", "approve")
        self.p.commit(f"review({wi_id}): approve task list")
        return self.p


class WorkItemLevelSteps(PipelineBase):
    def test_no_task_list_means_task_generation_with_validator_gate(self):
        self.p.work_item(self.WI)
        wi = self.p.wi()
        self.assertIn("step 2", wi["position"])
        step = first_step(wi)
        self.assertEqual(step["step"], "task-generation")
        self.assertIn("validate-tasks.py tasks/FEAT-001-tasks.md", step["gate"])
        self.assertIn("--work-item docs/work-items/FEAT-001-sample.md", step["gate"])

    def test_task_list_without_review_awaits_fresh_review(self):
        self.p.work_item(self.WI)
        self.p.task_list(self.WI, three_tasks())
        wi = self.p.wi()
        self.assertIn("awaiting fresh review", wi["position"])
        self.assertEqual(steps(wi), [("task-review", None, True)])
        self.assertIn("tasks/FEAT-001-review.md", first_step(wi)["gate"])

    def test_revise_verdict_emits_revision_step(self):
        self.p.work_item(self.WI)
        self.p.task_list(self.WI, three_tasks())
        self.p.init_git().commit("tasks(FEAT-001): generate task list")
        self.p.review("tasks/FEAT-001-review.md", "revise")
        self.p.commit("review(FEAT-001): revise")
        wi = self.p.wi()
        self.assertIn("verdict is 'revise'", wi["position"])
        step = first_step(wi)
        self.assertEqual(step["step"], "task-list-revision")
        self.assertIn("--work-item", step["gate"])
        self.assertIn("Coverage table", step["prompt"])  # v2.7.0 consistency rule

    def test_revision_commit_after_revise_triggers_fresh_rereview(self):
        """v2.7.1: a stale revise verdict must not keep emitting revisions once fixes land."""
        self.p.work_item(self.WI)
        self.p.task_list(self.WI, three_tasks())
        self.p.init_git().commit("tasks(FEAT-001): generate task list")
        self.p.review("tasks/FEAT-001-review.md", "revise")
        self.p.commit("review(FEAT-001): revise")
        self.p.task_list(self.WI, three_tasks(), title="Revised")
        self.p.commit("tasks(FEAT-001): apply review changes")
        wi = self.p.wi()
        self.assertIn("revision applied", wi["position"])
        self.assertEqual(steps(wi), [("task-review", None, True)])
        self.assertIn("OVERWRITE tasks/FEAT-001-review.md", first_step(wi)["prompt"])

    def test_uncommitted_revision_does_not_count(self):
        """Commits are the step boundary (guide rule 2)."""
        self.p.work_item(self.WI)
        self.p.task_list(self.WI, three_tasks())
        self.p.init_git().commit("tasks(FEAT-001): generate task list")
        self.p.review("tasks/FEAT-001-review.md", "revise")
        self.p.commit("review(FEAT-001): revise")
        self.p.task_list(self.WI, three_tasks(), title="Revised but not committed")
        wi = self.p.wi()
        self.assertEqual(first_step(wi)["step"], "task-list-revision")

    def test_task_review_accepted_overlay_bypasses_review_file(self):
        self.p.work_item(self.WI)
        self.p.task_list(self.WI, three_tasks())
        self.p.init_git().commit("tasks(FEAT-001): generate task list")
        self.p.mark(self.WI, "task-review=accepted")
        overlay = json.loads(self.p.read("tasks/FEAT-001-progress.json"))
        self.assertEqual(overlay["task-review"], "accepted")
        wi = self.p.wi()
        self.assertIn("steps 4-8", wi["position"])

    def test_approve_review_with_rereview_trap_sentence_opens_frontier(self):
        """v2.8.6: the verdict is read from the Verdict section, not the first match."""
        self.p.work_item(self.WI)
        self.p.task_list(self.WI, three_tasks())
        self.p.init_git().commit("tasks(FEAT-001): generate task list")
        self.p.review("tasks/FEAT-001-review.md", "approve",
                      preamble="This file overwrites the previous (verdict `revise`) review.")
        self.p.commit("review(FEAT-001): re-review approve")
        wi = self.p.wi()
        self.assertIn("steps 4-8", wi["position"])
        self.assertEqual(states(wi), {"T-001": "pending", "T-002": "pending", "T-003": "pending"})


class TaskFrontier(PipelineBase):
    def test_frontier_plans_only_tasks_with_met_dependencies(self):
        self.open_frontier()
        wi = self.p.wi()
        self.assertIn("(0/3 done)", wi["position"])
        self.assertEqual(steps(wi), [("planning", "T-001", False)])
        self.assertIn("plans/plan-FEAT-001-T-001-<slug>.md", first_step(wi)["prompt"])
        self.assertIn("plan exists", first_step(wi)["gate"])

    def test_plan_file_makes_task_planned_and_names_it_in_the_implementation_prompt(self):
        self.open_frontier()
        self.p.write("plans/plan-FEAT-001-T-001-label-schema.md", "# Plan T-001\n")
        wi = self.p.wi()
        self.assertEqual(states(wi)["T-001"], "planned")
        step = first_step(wi)
        self.assertEqual((step["step"], step["task"]), ("implementation", "T-001"))
        self.assertIn("plans/plan-FEAT-001-T-001-label-schema.md", step["prompt"])

    def test_implementation_commit_makes_task_implemented_and_review_next(self):
        self.open_frontier()
        self.p.commit("feat(T-001): add label schema")
        wi = self.p.wi()
        self.assertEqual(states(wi)["T-001"], "implemented")
        step = first_step(wi)
        self.assertEqual((step["step"], step["task"], step["fresh"]),
                         ("implementation-review", "T-001", True))
        self.assertIn("tasks/FEAT-001-T-001-implementation-review.md", step["gate"])

    def test_approved_review_marks_done_and_unblocks_dependents(self):
        self.open_frontier()
        self.p.commit("feat(T-001): add label schema")
        self.p.review("tasks/FEAT-001-T-001-implementation-review.md", "approve")
        wi = self.p.wi()
        self.assertEqual(states(wi)["T-001"], "done")
        self.assertIn("(1/3 done)", wi["position"])
        self.assertEqual(steps(wi), [("planning", "T-002", False)])

    def test_revise_review_needs_fix_then_fix_commit_triggers_rereview(self):
        """v2.7.1 at task level; v2.8.5 made the lookup follow the qualified review name."""
        self.open_frontier()
        self.p.commit("feat(T-001): add label schema")
        self.p.review("tasks/FEAT-001-T-001-implementation-review.md", "revise")
        self.p.commit("review(FEAT-001/T-001): revise")
        wi = self.p.wi()
        self.assertEqual(states(wi)["T-001"], "needs-fix")
        self.assertEqual(first_step(wi)["step"], "implementation-fix")
        self.assertIn("fresh re-review of T-001", first_step(wi)["gate"])

        self.p.commit("chore(T-001): bookkeeping only")  # v2.8.1: never evidence
        self.assertEqual(first_step(self.p.wi())["step"], "implementation-fix")

        self.p.commit("fix(T-001): address review findings")
        step = first_step(self.p.wi())
        self.assertEqual((step["step"], step["task"], step["fresh"]),
                         ("implementation-review", "T-001", True))
        self.assertIn("Detected mechanically", step["note"])
        self.assertIn("OVERWRITE tasks/FEAT-001-T-001-implementation-review.md", step["prompt"])

    def test_s_task_implemented_gets_completion_step_instead_of_review(self):
        """Guide step 7 skip rule, plus v2.8.2: docs: counts for Documentation tasks."""
        self.open_frontier()
        self.p.mark(self.WI, "T-001=done", "T-002=done")
        self.p.commit("docs(T-003): document the label endpoints")
        wi = self.p.wi()
        self.assertEqual(states(wi)["T-003"], "implemented")
        step = first_step(wi)
        self.assertEqual((step["step"], step["task"]), ("task-completion", "T-003"))
        self.assertIn("--mark T-003=done", step["gate"])

    def test_docs_commit_is_not_evidence_for_non_documentation_tasks(self):
        """v2.8.2 keeps the docs exclusion for every other type."""
        self.open_frontier()
        self.p.commit("docs(T-001): describe the schema")
        self.assertEqual(states(self.p.wi())["T-001"], "pending")

    def test_bookkeeping_prefixes_are_never_evidence(self):
        """v2.8.1 (chore) and the original plan/review/tasks/close exclusions."""
        self.open_frontier()
        for subject in ("chore(T-001): drop stale overlay", "plan(T-001): write plan",
                        "review(T-001): review", "tasks(T-001): touch list",
                        "close(FEAT-001): T-001 closed"):
            self.p.commit(subject)
        self.assertEqual(states(self.p.wi())["T-001"], "pending")

    def test_mockup_first_requires_mockup_before_planning(self):
        tasks = [dict(id=1, title="Board filter", type="Frontend", workflow="mockup-first",
                      complexity="M", files=["src/ui/board.tsx (new)"])]
        self.open_frontier(tasks)
        step = first_step(self.p.wi())
        self.assertEqual((step["step"], step["task"]), ("mockup", "T-001"))
        self.assertIn("mockups/FEAT-001-T-001-<screen>.html", step["prompt"])
        self.p.write("mockups/FEAT-001-T-001-board.html", "<!doctype html>")
        self.assertEqual(first_step(self.p.wi())["step"], "planning")

    def test_investigation_first_planning_carries_workflow_note(self):
        tasks = [dict(id=1, title="Find root cause", type="Investigation",
                      workflow="investigation-first", complexity="S")]
        self.open_frontier(tasks)
        step = first_step(self.p.wi())
        self.assertEqual(step["step"], "planning")
        self.assertIn("investigation findings", step["note"])

    def test_parallel_frontier_file_conflict_warns(self):
        tasks = [dict(id=1, title="A", files=["src/shared.py", "src/a.py (new)"]),
                 dict(id=2, title="B", files=["src/shared.py", "src/b.py (new)"])]
        self.open_frontier(tasks)
        wi = self.p.wi()
        self.assertEqual(len(wi["next_steps"]), 2)
        self.assertTrue(any("share files (src/shared.py)" in w for w in wi["warnings"]),
                        wi["warnings"])

    def test_dependency_deadlock_is_reported_as_stalled(self):
        tasks = [dict(id=1, title="A", deps="T-002"), dict(id=2, title="B", deps="T-001")]
        self.open_frontier(tasks)
        wi = self.p.wi()
        self.assertIn("stalled", wi["position"])
        self.assertEqual(wi["next_steps"], [])
        self.assertTrue(any("validate-tasks" in w for w in wi["warnings"]))

    def test_docs_only_remaining_names_step_nine(self):
        self.open_frontier()
        self.p.mark(self.WI, "T-001=done", "T-002=done")
        wi = self.p.wi()
        self.assertIn("step 9 docs-update", wi["position"])
        self.assertEqual(first_step(wi)["task"], "T-003")


class OverlaySemantics(PipelineBase):
    def test_mark_writes_overlay_and_overlay_wins(self):
        self.open_frontier()
        out = self.p.mark(self.WI, "T-001=done", note="S task, review skipped")
        self.assertIn("recorded T-001=done", out)
        overlay = json.loads(self.p.read("tasks/FEAT-001-progress.json"))
        self.assertEqual(overlay["T-001"]["status"], "done")
        self.assertEqual(overlay["T-001"]["note"], "S task, review skipped")
        self.assertRegex(overlay["T-001"]["updated"], r"^\d{4}-\d{2}-\d{2}$")
        wi = self.p.wi()
        self.assertEqual(states(wi)["T-001"], "done")
        self.assertTrue(next(t for t in wi["tasks"] if t["id"] == "T-001")["evidence"]
                        .startswith("overlay"))

    def test_mark_rejects_bad_targets_and_statuses(self):
        self.open_frontier()
        for bad in ("T-001=finished", "task-review=maybe", "X-1=done", "T-001"):
            proc = self.p.next_step_raw("--wi", self.WI, "--mark", bad)
            self.assertEqual(proc.returncode, 1, bad)
        proc = self.p.next_step_raw("--mark", "T-001=done")  # --wi is required
        self.assertEqual(proc.returncode, 1)
        self.assertIn("--mark requires --wi", proc.stderr)

    def test_overlay_contradicting_revise_verdict_warns_loudly(self):
        """v2.8.1: the overlay still wins, but never silently."""
        self.open_frontier()
        self.p.commit("feat(T-001): add label schema")
        self.p.review("tasks/FEAT-001-T-001-implementation-review.md", "revise")
        self.p.mark(self.WI, "T-001=implemented")
        wi = self.p.wi()
        self.assertEqual(states(wi)["T-001"], "implemented")
        self.assertTrue(any("overlay says 'implemented'" in w and "revise" in w
                            for w in wi["warnings"]), wi["warnings"])

    def test_blocked_task_alone_reports_blocked_position(self):
        self.open_frontier([dict(id=1, title="Needs AWS account")])
        self.p.mark(self.WI, "T-001=blocked", note="awaiting AWS account")
        wi = self.p.wi()
        self.assertEqual(states(wi)["T-001"], "blocked")
        self.assertIn("externally blocked", wi["position"])
        self.assertTrue(any(w.startswith("blocked: T-001") for w in wi["warnings"]))

    def test_corrupt_overlay_exits_one(self):
        self.open_frontier()
        self.p.write("tasks/FEAT-001-progress.json", "{not json")
        rc, _, err = self.p.next_step()
        self.assertEqual(rc, 1)
        self.assertIn("overlay is not valid JSON", err)


class CrossWorkItemCollisions(FrameworkTestCase):
    """Task IDs restart at T-001 in every task list (v2.8.4 commits, v2.8.5 artifacts)."""

    def setUp(self):
        super().setUp()
        self.p.work_item("FEAT-001", slug="labels")
        self.p.work_item("BUG-001", slug="overdue")
        self.p.task_list("FEAT-001", [dict(id=1, title="Label schema", type="Database",
                                           files=["src/db/label.py (new)"])])
        self.p.task_list("BUG-001", [dict(id=1, title="Fix overdue predicate", type="Backend",
                                          files=["src/overdue.py"])])
        self.p.init_git().commit("tasks: both lists")
        self.p.mark("FEAT-001", "task-review=accepted")
        self.p.mark("BUG-001", "task-review=accepted")

    def test_unqualified_commit_credits_neither_and_warns(self):
        self.p.commit("feat(T-001): extract design tokens")
        feat, bug = self.p.wi("FEAT-001"), self.p.wi("BUG-001")
        self.assertEqual(states(feat)["T-001"], "pending")
        self.assertEqual(states(bug)["T-001"], "pending")
        for wi in (feat, bug):
            self.assertTrue(any("NOT credited" in w for w in wi["warnings"]), wi["warnings"])

    def test_qualified_commit_credits_only_its_owner(self):
        self.p.commit("feat(T-001): ambiguous")
        self.p.commit("fix(BUG-001/T-001): correct the overdue predicate")
        feat, bug = self.p.wi("FEAT-001"), self.p.wi("BUG-001")
        self.assertEqual(states(bug)["T-001"], "implemented")
        self.assertEqual(states(feat)["T-001"], "pending")
        # the FEAT warning explains the commit belongs to BUG-001 and offers no --mark remedy
        warn = next(w for w in feat["warnings"] if "NOT credited" in w)
        self.assertIn("no action needed", warn)
        self.assertNotIn("--mark T-001=implemented", warn)

    def test_unqualified_review_file_is_refused_when_id_collides(self):
        self.p.review("tasks/T-001-implementation-review.md", "approve")
        feat, bug = self.p.wi("FEAT-001"), self.p.wi("BUG-001")
        self.assertEqual(states(feat)["T-001"], "pending")
        self.assertEqual(states(bug)["T-001"], "pending")
        self.assertTrue(any("not work-item-qualified" in w for w in feat["warnings"]))

    def test_qualified_review_credits_only_its_owner(self):
        self.p.review("tasks/FEAT-001-T-001-implementation-review.md", "approve")
        self.assertEqual(states(self.p.wi("FEAT-001"))["T-001"], "done")
        self.assertEqual(states(self.p.wi("BUG-001"))["T-001"], "pending")

    def test_unqualified_plan_is_refused_when_id_collides(self):
        self.p.write("plans/plan-T-001-schema.md", "# Plan\n")
        feat = self.p.wi("FEAT-001")
        self.assertEqual(states(feat)["T-001"], "pending")
        self.assertTrue(any("plan 'plan-T-001-schema.md' is not work-item-qualified" in w
                            for w in feat["warnings"]), feat["warnings"])
        self.p.write("plans/plan-BUG-001-T-001-predicate.md", "# Plan\n")
        self.assertEqual(states(self.p.wi("BUG-001"))["T-001"], "planned")
        self.assertEqual(states(self.p.wi("FEAT-001"))["T-001"], "pending")

    def test_fix_after_revise_with_unqualified_commit_warns_rereview_will_not_trigger(self):
        self.p.commit("feat(FEAT-001/T-001): schema")
        self.p.review("tasks/FEAT-001-T-001-implementation-review.md", "revise")
        self.p.commit("review(FEAT-001/T-001): revise")
        self.p.commit("fix(T-001): unqualified fix")
        feat = self.p.wi("FEAT-001")
        self.assertEqual(first_step(feat)["step"], "implementation-fix")
        self.assertTrue(any("re-review will not trigger" in w for w in feat["warnings"]),
                        feat["warnings"])
        self.p.commit("fix(FEAT-001/T-001): qualified fix")
        self.assertEqual(first_step(self.p.wi("FEAT-001"))["step"], "implementation-review")


class LegacySingleWorkItemNames(PipelineBase):
    """A repo with one task list keeps accepting unqualified names (v2.8.5 compatibility)."""

    def test_unqualified_review_and_plan_resolve_when_id_is_unique(self):
        self.open_frontier()
        self.p.write("plans/plan-T-002-endpoints.md", "# Plan\n")
        self.p.review("tasks/T-001-implementation-review.md", "approve")
        wi = self.p.wi()
        self.assertEqual(states(wi)["T-001"], "done")
        self.assertEqual(states(wi)["T-002"], "planned")
        self.assertIn("plans/plan-T-002-endpoints.md", first_step(wi)["prompt"])
        self.assertEqual(wi["warnings"], [])


class VerdictReading(PipelineBase):
    def test_review_without_readable_verdict_is_not_evidence_and_warns(self):
        """v2.8.6: fenced text is never authoritative; the safe failure is a redundant pass."""
        self.open_frontier()
        self.p.commit("feat(T-001): add label schema")
        self.p.write("tasks/FEAT-001-T-001-implementation-review.md",
                     "# Review\n\n```\n## Verdict\n\napprove\n```\n")
        wi = self.p.wi()
        self.assertEqual(states(wi)["T-001"], "implemented")  # falls through to commits
        self.assertTrue(any("no verdict could be read" in w for w in wi["warnings"]),
                        wi["warnings"])

    def test_quoted_prior_verdict_does_not_count(self):
        self.open_frontier()
        self.p.write("tasks/FEAT-001-T-001-implementation-review.md",
                     "# Re-review\n\n> previous verdict: revise\n\n## Verdict\n\napprove\n")
        self.assertEqual(states(self.p.wi())["T-001"], "done")


class Closure(PipelineBase):
    def test_all_done_emits_closure_with_strict_spec_gate(self):
        self.open_frontier()
        self.p.mark(self.WI, "T-001=done", "T-002=done", "T-003=done")
        wi = self.p.wi()
        self.assertIn("step 10: all tasks done", wi["position"])
        step = first_step(wi)
        self.assertEqual(step["step"], "closure")
        self.assertIn("validate-specs.py --root . --strict", step["gate"])
        self.assertIn("close(FEAT-001)", step["prompt"])
        self.assertIn("CHANGELOG.md", step["prompt"])  # v2.8.3

    def test_early_status_flip_without_evidence_does_not_close(self):
        """v2.7.0: a docs task flipping Status must not short-circuit the frontier."""
        self.open_frontier()
        self.p.work_item(self.WI, status="Completed")
        self.p.commit("docs: flip status early")
        wi = self.p.wi()
        self.assertIn("steps 4-8", wi["position"])
        self.assertTrue(any("flipped the Status early" in w for w in wi["warnings"]),
                        wi["warnings"])

    def test_closed_status_with_evidence_but_no_close_commit_still_needs_closure(self):
        self.open_frontier()
        self.p.mark(self.WI, "T-001=done", "T-002=done", "T-003=done")
        self.p.work_item(self.WI, status="Completed")
        self.p.commit("docs(FEAT-001): status completed")
        wi = self.p.wi()
        self.assertIn("formal closure incomplete", wi["position"])
        self.assertEqual(first_step(wi)["step"], "closure")

    def test_close_commit_moves_work_item_to_closed(self):
        self.open_frontier()
        self.p.mark(self.WI, "T-001=done", "T-002=done", "T-003=done")
        self.p.work_item(self.WI, status="Completed")
        self.p.commit("close(FEAT-001): task labels shipped")
        report = self.p.report()
        self.assertEqual(report["closed"], ["FEAT-001"])
        self.assertEqual(report["work_items"], [])

    def test_closed_status_without_task_list_is_closed_immediately(self):
        self.p.work_item(self.WI, status="Cancelled")
        report = self.p.report()
        self.assertEqual(report["closed"], ["FEAT-001"])


class CommandLineContract(PipelineBase):
    def test_json_shape_is_stable(self):
        self.open_frontier()
        report = self.p.report()
        self.assertEqual(sorted(report), ["closed", "notes", "root", "work_items"])
        wi = report["work_items"][0]
        self.assertEqual(sorted(wi), ["id", "next_steps", "position", "status", "tasks",
                                      "title", "warnings"])
        self.assertEqual(sorted(wi["tasks"][0]),
                         ["complexity", "deps", "evidence", "id", "state", "title", "type"])
        self.assertEqual(sorted(wi["next_steps"][0]),
                         ["fresh", "gate", "note", "prompt", "step", "task"])
        self.assertEqual(wi["tasks"][1]["deps"], ["T-001"])
        self.assertEqual(wi["title"], "Sample work item")
        self.assertEqual(wi["status"], "In Progress")

    def test_human_output_is_ascii_and_lists_steps(self):
        self.open_frontier()
        proc = self.p.next_step_raw()
        self.assertEqual(proc.returncode, 0)
        proc.stdout.encode("ascii")  # raises UnicodeEncodeError if not ASCII-only
        self.assertIn("next steps (in priority order", proc.stdout)
        self.assertIn("1. planning (T-001)", proc.stdout)

    def test_not_a_git_repo_disables_commit_evidence_with_a_note(self):
        self.p.work_item(self.WI)
        self.p.task_list(self.WI, three_tasks())
        self.p.review("tasks/FEAT-001-review.md", "approve")
        report = self.p.report()
        self.assertTrue(any("not a git repo" in n for n in report["notes"]), report["notes"])
        self.assertIn("steps 4-8", report["work_items"][0]["position"])

    def test_missing_work_items_dir_exits_one(self):
        bare = Project.__new__(Project)
        bare.root = self.tmp / "bare"
        bare.root.mkdir()
        rc, _, err = bare.next_step()
        self.assertEqual(rc, 1)
        self.assertIn("docs/work-items/ not found", err)

    def test_unknown_work_item_filter_exits_one(self):
        self.open_frontier()
        rc, _, err = self.p.next_step("--wi", "FEAT-999")
        self.assertEqual(rc, 1)
        self.assertIn("FEAT-999", err)

    def test_wi_filter_limits_report(self):
        self.p.work_item("FEAT-001", slug="a")
        self.p.work_item("BUG-001", slug="b")
        report = self.p.report("--wi", "BUG-001")
        self.assertEqual([w["id"] for w in report["work_items"]], ["BUG-001"])

    def test_template_work_items_are_ignored(self):
        self.p.write("docs/work-items/TEMPLATE-feature-brief.md", "# Template\n")
        self.p.work_item("FEAT-001")
        report = self.p.report()
        self.assertEqual([w["id"] for w in report["work_items"]], ["FEAT-001"])


class EventLogging(PipelineBase):
    def test_log_event_appends_well_formed_ndjson(self):
        self.p.work_item(self.WI)
        proc = self.p.next_step_raw("--log-event", "step=planning", "wi=FEAT-001",
                                    "task=T-001", "event=accepted", "tokens=5312",
                                    "model=sonnet", "cost=0.42")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = self.p.read("metrics/events.ndjson").splitlines()
        self.assertEqual(len(lines), 1)
        event = json.loads(lines[0])
        self.assertEqual(event["work_item"], "FEAT-001")
        self.assertEqual(event["session_tokens"], 5312)
        self.assertEqual(event["cost_usd"], 0.42)
        self.assertEqual(event["step"], "planning")
        self.assertEqual(event["event"], "accepted")
        self.assertRegex(event["ts"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.p.next_step_raw("--log-event", "step=closure", "wi=FEAT-001", "event=completed")
        self.assertEqual(len(self.p.read("metrics/events.ndjson").splitlines()), 2)

    def test_log_event_rejects_malformed_input(self):
        self.p.work_item(self.WI)
        cases = [
            ("step=planning", "event=accepted"),            # missing wi
            ("step=planning", "wi=FEAT-001", "event=done"),  # bad event value
            ("step=planning", "wi=FEAT-001", "event=accepted", "tokens=lots"),
            ("step=planning", "wi=FEAT-001", "event=accepted", "garbage"),
        ]
        for args in cases:
            proc = self.p.next_step_raw("--log-event", *args)
            self.assertEqual(proc.returncode, 1, args)
        self.assertFalse(self.p.exists("metrics/events.ndjson"))


if __name__ == "__main__":
    unittest.main()
