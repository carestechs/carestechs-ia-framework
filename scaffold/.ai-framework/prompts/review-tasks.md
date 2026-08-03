# Task List Review Prompt

---

## Purpose

Adversarially review a generated task list **in a fresh context**, before implementation begins. Use this prompt after a task list has been generated (`prompts/feature-tasks.md`, `bugfix-tasks.md`, or `refactor-tasks.md`) and validated, when the work warrants an independent quality gate — recommended for L/XL work items and any task list an orchestrator intends to hand to implementation agents.

**The fresh-context mandate is the point of this prompt.** Same-session self-review is unreliable: a model re-reading its own output with its generation reasoning still in context tends to re-derive the same conclusions and approve its own mistakes. What works is a **fresh context with no generation history, plus external tool feedback treated as ground truth**. The reviewer MUST NOT have the generator's conversation, chain of reasoning, or working notes in context — only the artifacts listed under Required Context.

The reviewer's job is to find problems, not to fix them: hallucinated references, uncovered acceptance criteria, scope creep, broken ordering, mis-sized tasks, wrong workflow classification. The output is a review file with a verdict and a findings table — the generator (or a new generation session) applies the required changes.

**Best-of-N (orchestrator-facing):** when the orchestrator samples multiple candidate task lists for the same work item, first run `validate-tasks.py` on every candidate and discard any with errors; then run this review — each in its own fresh session — on every validator-clean candidate. Pick the candidate with the strongest verdict, or synthesize a final list by adopting the best-reviewed tasks and applying every CONFIRMED required change before implementation.

---

## How to Use

- **AI agents (Claude Code, etc.):** Run in a **new session** — never the session that generated the task list. Read the context files listed in your project CLAUDE.md's routing table for "Task list review" (the task list, its work item, each spec's index plus the shards the work item's impact tables name, and CLAUDE.md), follow the sections below, and **write** the review to `tasks/<WORK-ITEM-ID>-review.md` (e.g., `tasks/FEAT-001-review.md`).
- **Chat workflows (manual copy-paste):** Use the XML skeleton in the [Chat Workflow Template (XML)](#chat-workflow-template-xml) appendix **in a fresh conversation**. Include this prompt's Guidance, Output Format, and Constraints sections alongside the skeleton.

---

## Required Context

The reviewer's context is deliberately minimal. Load **only**:

1. **The task list under review** — `tasks/FEAT-XXX-tasks.md` (or `BUG-XXX` / `IMP-XXX` / adhoc equivalent)
2. **The work item** — `docs/work-items/FEAT-XXX-short-title.md` (or `BUG-XXX` / `IMP-XXX`)
3. **Each spec's `index.md` plus only the shards named by the work item's impact tables** (Entities / API / UI), mapped via the kebab-case naming rule: entity `TaskLabel` → `docs/data-model/entities/task-label.md` (singular); resource `/api/task-labels` → `docs/api-spec/endpoints/task-labels.md` (matches the route segment); screen "Project Board" → `docs/ui-specification/screens/project-board.md`. Do not read whole spec directories.
4. **CLAUDE.md** — conventions, workflow rules, Development Pipeline

**Explicitly forbidden context:**

- **The generator's transcript** — the conversation, reasoning, or scratch notes that produced the task list. If you generated this task list, stop: this review must run in a different session.
- **Rationale files** (`docs/rationale/*.md`) — never loaded by default; the review judges the task list against the contract docs, not against narrative history.

---

## Guidance

### Step 1 — Run the external tools FIRST

Before reading a single task closely, run both validators and record their output:

```
python .ai-framework/tools/validate-tasks.py tasks/FEAT-XXX-tasks.md --work-item docs/work-items/FEAT-XXX-short-title.md
python .ai-framework/tools/validate-specs.py
```

**Treat tool output as ground truth.** Every validator error becomes a CONFIRMED finding — do not re-litigate, soften, or second-guess it. Tool warnings (e.g., stale freshness stamps from `validate-specs.py`) qualify the trustworthiness of the shards: if a shard the review depends on is flagged stale or drifted, say so in the affected findings rather than treating the shard as authoritative.

The tools check structure (schema, enums, DAG, file paths, AC coverage table, shard cross-refs). They cannot judge meaning — that is Step 2.

### Step 2 — Judge semantics against the fixed rubric

Evaluate the task list against all six points. Every point gets examined; a clean point produces no finding.

| # | Rubric Point | What to Verify |
|---|-------------|----------------|
| 1 | **AC completeness** | Every work-item acceptance criterion is covered by ≥1 task whose own acceptance criteria actually implement and verify it — not merely listed in the coverage table |
| 2 | **Scope fidelity** | No task implements anything outside the work item's scope (Included section) or violates the stakeholder Scope Lock; excluded items stay excluded |
| 3 | **Reference reality** | Every entity, endpoint, screen, and file a task mentions exists in the loaded shards, or is flagged `(new)` and matches what the work item's impact tables declare as new — nothing invented |
| 4 | **Dependency logic** | The order is buildable: schema before code that uses it, API before frontend integration, investigation before fix; no dependency that forces rework or an unbuildable intermediate state |
| 5 | **Sizing** | No task spans multiple `Type` values; no task is effectively larger than XL — such tasks must be split |
| 6 | **Workflow correctness** | `mockup-first` on new/significantly-changed user-facing screens (per the work item's UI impact), `investigation-first` where requirements depend on unknowns, `standard` otherwise — per the generating prompt's rules |

The rubric applies to all three task-list types; interpret it through the generating prompt's rules:

- **Feature (`FEAT-XXX`)** — the `## Acceptance Criteria Coverage` table is mandatory; its absence is a CONFIRMED high-severity finding (the validator also flags it when run with `--work-item`). Workflow checks (rubric point 6) key off the Feature Brief's UI impact table — new screens imply `mockup-first` on their frontend tasks.
- **Bug fix (`BUG-XXX`)** — verify the three-phase order (Investigation → Implementation → Verification & Prevention) is enforced through Dependencies; a list that jumps straight to a fix with no Phase 1 fails rubric point 4. For cross-system/contract bugs, the first investigation step must verify the contract against the producer (per `prompts/bugfix-tasks.md`). The coverage table is recommended, not mandatory — its absence alone is at most a low-severity finding.
- **Refactoring (`IMP-XXX`)** — verify Phase 0 (test-coverage safety net) precedes any restructuring, every phase leaves the system in a working state, and no task smuggles in a functionality change (rubric point 2 — refactoring is not enhancement). The coverage table is recommended, not mandatory.

### Step 3 — Classify every finding

Each finding gets a **classification** and a **severity**:

- **CONFIRMED** — verified against evidence: a validator error, or a direct check against a loaded shard, the work item, or CLAUDE.md (cite the evidence in the finding).
- **PLAUSIBLE** — a defensible judgment call the reviewer cannot mechanically verify (sizing instincts, suspected ordering risk, likely-missing edge case). Never present a PLAUSIBLE finding with CONFIRMED confidence.

Severity:

- **high** — implementing as-is produces wrong or unbuildable work (hallucinated reference, uncovered AC, out-of-scope task, broken ordering)
- **medium** — implementable but materially degraded (mis-sized task, wrong workflow classification, weak acceptance criteria on a risky task)
- **low** — polish (unclear rationale, minor naming drift, cosmetic inconsistency)

### Step 4 — Reach a verdict

Blocking is an **outcome test**, not a severity label:

- **revise** — any validator error, or any CONFIRMED finding meaning the list implemented AS WRITTEN would yield **wrong** software (a task contradicts a spec shard or the work item), an **unbuildable** state (dependency or ordering defects), or an **unverified** acceptance criterion (an AC clause no task's criteria assert).
- **approve** — everything else, including CONFIRMED findings whose cost is convention, budget, sizing, or consistency polish: record them under `## Advisories`. PLAUSIBLE findings never block on their own, whatever their severity.

Why the bar is outcome-anchored (measured): fresh reviewers are non-exhaustive — each new one surfaces a different legitimate slice — so "any CONFIRMED medium ⇒ revise" makes revise loops ratchet instead of converge (measured live: three consecutive revise rounds with disjoint finding sets, replicated across worker models). Reserve `revise` for findings that would ship a defect; everything else rides along as advisories.

Do not fix the task list yourself. The review file is the deliverable; regeneration or targeted edits happen in a separate step against the required-changes checklist.

---

## Output Format

**Output file:** `tasks/<WORK-ITEM-ID>-review.md` (e.g., `tasks/FEAT-001-review.md`; for ad-hoc task lists, `tasks/adhoc-short-title-review.md`). AI agents write this file — the review is not just chat output.

Structure:

**Header** — task list reviewed, work item, review date, and the outcome of both tool runs (errors/warnings counts).

**`## Verdict`** — `approve` or `revise`, followed by a 1–3 sentence justification naming the decisive findings. An `approve` may carry advisories — the verdict word stays exactly `approve` (the orchestrator contract's verdict regex is unchanged).

**`## Findings`** — one table, one row per finding:

```markdown
| ID | Severity | Class | Task(s) | Finding | Required Change |
|----|----------|-------|---------|---------|-----------------|
| R-1 | high | CONFIRMED | T-007 | [what is wrong + the evidence that confirms it] | [the specific change] |
| R-2 | medium | PLAUSIBLE | T-006 | [what looks wrong + why] | [the suggested change] |
```

- `ID`: `R-1`, `R-2`, … sequential.
- `Task(s)`: the task IDs the finding refers to (or `—` for list-level findings such as a missing coverage row).
- `Finding`: what is wrong and why — CONFIRMED findings cite their evidence (shard, work-item section, or tool output); PLAUSIBLE findings state the reasoning.
- `Required Change`: the concrete edit that resolves the finding.

**`## Required Changes Before Implementation`** — present when verdict = `revise`: a checklist distilled from the findings that block approval (every finding that met the Step 4 blocking bar, plus any validator errors), phrased as actionable edits:

```markdown
## Required Changes Before Implementation

- [ ] R-1: [actionable edit]
- [ ] R-2: [actionable edit]
```

**`## Advisories`** — present under either verdict when non-blocking findings exist: a short list distilled from the findings that did not meet the blocking bar. Disposition contract: advisories are never silently dropped — they stay recorded in this committed review; the acceptor may fold cheap ones in during acceptance; substantial ones become new work items. A PLAUSIBLE or low finding may be promoted into the blocking checklist only with an explicit reason stated in the finding.

---

## Constraints

- **Fresh context only** — never review a task list in the session that generated it; never load the generator's transcript or `docs/rationale/` files
- **Tools before judgment** — both validators run first; their errors are CONFIRMED findings verbatim, not re-argued
- **Evidence discipline** — every CONFIRMED finding cites its evidence; every PLAUSIBLE finding is labeled as such; no finding without at least one task reference or an explicit list-level scope
- **Review, don't rewrite** — the reviewer does not edit the task list; all changes flow through the required-changes checklist
- **No scope expansion** — do not demand tasks for work outside the work item; flagging a genuinely missing in-scope task is rubric point 1, inventing new scope is not
- **Complete rubric coverage** — all six rubric points are examined every time; absence of findings on a point means it passed, not that it was skipped

---

## Post-Generation Checklist

After writing the review, verify:

- [ ] Both tools were run (`validate-tasks.py` with `--work-item`, then `validate-specs.py`) and their results appear in the header; every tool error surfaced as a CONFIRMED finding
- [ ] All six rubric points were examined
- [ ] Every finding has ID, severity, CONFIRMED/PLAUSIBLE class, task reference(s), evidence or reasoning, and a required change
- [ ] The verdict follows the Step 4 rules (a finding meets the outcome-anchored blocking bar or a validator error ⇒ `revise`; otherwise `approve`)
- [ ] Verdict = `revise` ⇒ the Required Changes Before Implementation checklist is present and covers every blocking finding
- [ ] Non-blocking findings (whatever their severity) are recorded under `## Advisories`, not silently dropped and not smuggled into the blocking checklist
- [ ] No generator transcript or rationale file was loaded during the review
- [ ] Review saved to `tasks/<WORK-ITEM-ID>-review.md` (agents)

---

## Chat Workflow Template (XML)

Use in a **fresh conversation** — do not paste this into the conversation that generated the task list.

```xml
<task-review-request>

<context>

<task-list>
<!-- REQUIRED: The task list under review -->
[Paste full tasks/FEAT-XXX-tasks.md content]
</task-list>

<work-item>
<!-- REQUIRED: The work item the task list was generated from -->
[Paste full docs/work-items/FEAT-XXX-short-title.md content]
</work-item>

<spec-shards>
<!-- REQUIRED: Each spec's index.md + ONLY the shards named by the work item's
     impact tables (Entities / API / UI), mapped via the kebab-case naming rule.
     Do not paste whole spec directories. -->
[Paste docs/data-model/index.md + referenced entity shards]
[Paste docs/api-spec/index.md + referenced endpoint shards]
[Paste docs/ui-specification/index.md + referenced screen shards]
</spec-shards>

<code-conventions>
<!-- REQUIRED: CLAUDE.md for conventions and workflow rules -->
[Paste CLAUDE.md content]
</code-conventions>

<validator-output>
<!-- REQUIRED: Paste the raw output of both tool runs — chat reviewers cannot
     execute them, so the orchestrator/human runs them and pastes results:
     python .ai-framework/tools/validate-tasks.py <task-list> --work-item <work-item>
     python .ai-framework/tools/validate-specs.py -->
[Paste both tools' output]
</validator-output>

<!-- DO NOT include: the generating conversation, its reasoning, or docs/rationale/ files -->

</context>

<task-type>Task List Review</task-type>

<request>
Adversarially review this task list against the six-point rubric from
prompts/review-tasks.md. Treat the validator output as ground truth. Produce the
review in the Output Format (Verdict, Findings table, Required Changes checklist).
</request>

</task-review-request>
```

---

## Example

Excerpt of `tasks/FEAT-001-review.md` — reviewing the task list for TaskFlow's FEAT-001 (Task Labels) work item (`templates/examples/FEAT-001-task-labels.md`):

```markdown
# Task List Review: FEAT-001 Task Labels

**Task list:** tasks/FEAT-001-tasks.md · **Work item:** docs/work-items/FEAT-001-task-labels.md
**Reviewed:** 2026-03-02 · **validate-tasks:** 0 errors · **validate-specs:** 0 errors, 1 warning (stamp age)

## Verdict

**revise** — R-1 is a CONFIRMED high-severity hallucinated endpoint: T-007 integrates
against an API that neither the shards nor the work item define. R-2 is advisory.

## Findings

| ID | Severity | Class | Task(s) | Finding | Required Change |
|----|----------|-------|---------|---------|-----------------|
| R-1 | high | CONFIRMED | T-007 | T-007 wires the label picker to `PATCH /api/v1/tasks/{id}` with a `labelIds` body field. That endpoint shape does not exist: `docs/api-spec/endpoints/tasks.md` defines no label field on task update, and the work item's API impact table (§7) defines label assignment as `PUT /api/v1/tasks/{id}/labels` (new). The reference is invented, not flagged `(new)`. | Re-point T-007 to `PUT /api/v1/tasks/{id}/labels` per §7; update its Acceptance Criteria and Files to Modify/Create to match. |
| R-2 | medium | PLAUSIBLE | T-006 | T-006 ("Build Label Management Dialog") is sized M, but its acceptance criteria span four flows (create, rename, recolor, delete), the delete-confirmation dialog with affected-task count (AC-5), and inline duplicate-name validation (AC-6) — comparable dialogs in this list are L. Cannot be mechanically verified; judgment call. | Resize T-006 to L, or split the delete-confirmation flow (AC-5) into its own task depending on T-006. |

## Required Changes Before Implementation

- [ ] R-1: Re-point T-007 from `PATCH /api/v1/tasks/{id}` to `PUT /api/v1/tasks/{id}/labels`
      (work item §7); align its Acceptance Criteria and Files to Modify/Create.
```

Note the shape: the CONFIRMED finding cites its evidence (the shard and the work-item section that contradict the task); the PLAUSIBLE finding is labeled as a judgment call and stays out of the blocking checklist. With R-1 fixed and re-validated, a follow-up review would return `approve`.
