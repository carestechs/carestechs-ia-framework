# Orchestrator Integration Guide

How an external orchestrator drives the framework's pipeline: what each step expects,
what the orchestrator must provide, what comes back, and how to verify it — precisely
enough to implement against. Written for the manual/orchestrated operating model where
**every step runs as an independent session** that shares nothing with other steps
except committed artifacts.

Framework version: 2.5.0. Everything here is derived from the shipped conventions
(CLAUDE.md routing table, canonical task schema, validators) — when this guide and a
prompt template disagree, the prompt template wins.

---

## 1. Operating model

Five rules everything else follows from:

1. **Artifacts are the only state.** A session's entire input is files in the repo;
   its entire output is files it writes. No session depends on another session's
   conversation. If a human can't reconstruct pipeline position from the repo plus
   the orchestrator's own records, the orchestrator is holding state it shouldn't.
2. **Git commits are step boundaries.** Every step ends with the orchestrator
   committing the step's artifact. Handoffs are atomic; the audit trail is `git log`;
   correction burden is measurable as diffs between a step's first commit and its
   accepted state.
3. **Validators gate, sessions self-check.** Each generating session runs the
   validator on its own output before finishing (this is the single biggest measured
   compliance lever — omitting it collapsed schema compliance from 100% to 0% in
   testing). The orchestrator ALSO runs the same validator afterward and never trusts
   a session's claim of success.
4. **Review steps run in fresh sessions.** The task-list review and the
   implementation review must run in sessions that did not produce the artifact under
   review (measured: same-context self-review is unreliable; fresh context + tool
   evidence works).
5. **Context is loaded by retrieval keys, never wholesale.** Spec docs are sharded;
   sessions read each spec's `index.md` plus only the shards named by the work item's
   impact tables. The orchestrator never needs to assemble context manually — the
   project's CLAUDE.md routing table tells each session what to read — but it should
   verify referenced shards exist before spawning (see per-step preconditions).

### The pipeline

```
(0) bootstrap ─ once per project
(1) brief ──► (2) task-generation ──► (3) task-review ──► per task: ┐
                                                                    │
    ┌───────────────────────────────────────────────────────────────┘
    ▼
(4) planning ──► (5) assignment ──► (6) implementation ──► (7) implementation-review
    ▲                                                            │
    └───────────────── revise loop ◄─────────────────────────────┘
                                                                 ▼
                                             (8) task complete ──► all tasks done?
                                                                 ▼
                                (9) docs-update task ──► (10) brief closure
```

---

## 2. The session contract (common to every step)

How the orchestrator spawns any framework session:

| Aspect | Contract |
|---|---|
| Working directory | The project repo root (where CLAUDE.md lives). Sessions resolve every path relative to it. If your runner's cwd is elsewhere, pass `--add-dir <project root>` — sessions cannot read outside their allowed directories, and they will silently degrade rather than fail loudly (verified failure mode). |
| Headless invocation | `claude -p "<step prompt>" --permission-mode acceptEdits --allowedTools "Bash(python *)"` — acceptEdits lets the session write its artifact; the Bash allowance is for the validator self-check. Add `Bash(npm *)`/test runners for implementation and implementation-review sessions. |
| Bootstrap context | Every session reads the project's `CLAUDE.md` first (say so in the prompt). Its routing table maps the step to the prompt template, the files to read, and the output path — the orchestrator's step prompts stay 3–6 lines because the routing table carries the detail. |
| Output | The session writes the artifact file(s) named in the routing table's Output column and runs its self-check. The artifact is the deliverable; chat text is not. |
| Never provide | The transcript of any other session (especially not to reviews), or anything under `docs/rationale/`. |
| After the session | The orchestrator: (a) verifies the artifact exists, (b) runs the gate command(s) itself, (c) commits with the step's message convention, (d) appends event-log entries, (e) transitions its own state machine. |
| Timeouts | Generation sessions run 4–15 minutes on real fixtures (plans fastest ~4–6 min; UI specs slowest ~12–14 min). Budget 20 min; treat a timeout as `revised` with detail "timeout" and retry once before flagging a human. |
| Transient API failures | Retry with back-off (observed: 529s come in bursts; a 5–10 min wait clears them). A session that dies leaves no partial artifact contract — always re-verify the output file before treating a retry as a duplicate. |

### Event log

Append one JSON line per event to `metrics/events.ndjson` (schema in
`guides/evaluation.md`). Minimum per step: `started` when spawning,
`artifact_committed` after the commit (put the short SHA in `detail`),
`accepted`/`revised` when the gate or a human rules, `completed` for terminal steps.
Include `session_tokens` whenever your runner exposes it — it's the denominator for
cost-per-accepted-task.

### Verdict parsing (mechanical contracts)

- **Review files** (`tasks/*-review.md`, `tasks/*-implementation-review.md`) contain a
  `## Verdict` heading whose section body is `approve` or `revise` (match
  `(?i)verdict[^a-z]*(approve|revise)` against the file). `revise` ⇒ loop back with
  the review file added to the regenerating/fixing session's context.
- **Task lists**: task blocks match `^#{2,4}\s+T-\d+\s*:`; fields are `**Field:** value`
  lines. `**Dependencies:**` is a comma-separated `T-XXX` list or `None` — build the
  scheduling DAG from it. `**Files to Modify/Create:**` bullets (suffix `(new)` for
  not-yet-existing files) are the conflict set for parallel scheduling: two tasks may
  run concurrently only if their file sets don't intersect.
- **Coverage**: feature task lists end with `## Acceptance Criteria Coverage`
  (`| AC | Covered By |` rows) — `validate-tasks.py --work-item` cross-checks it.

---

## 3. Step 0 — Project bootstrap (once per project)

Manual or orchestrated; listed for completeness.

1. Copy the scaffold: from the project root, `cp -r <framework>/scaffold/. .`
   (the `/.` carries `.ai-framework/` and `.claude/`). If the project already has a
   CLAUDE.md, merge by hand.
2. ADR compilation (if the org ADR repo applies): session per routing row
   **"ADR compilation"** with the chosen profile — pre-fills CLAUDE.md patterns,
   architecture decisions, and both spec index conventions. Provide: the ADR repo
   path (`--add-dir` it) and the profile name.
3. Fill strategy docs (human): `docs/stakeholder-definition.md`, persona, ARCHITECTURE.
4. Generate specs: sessions per routing rows **"Spec generation"** (writes
   `docs/data-model/` then `docs/api-spec/`, sharded, frontmattered, stamped) and
   **"UI spec generation"** (writes `docs/ui-specification/`). Gate each with
   `python .ai-framework/tools/validate-specs.py --root . --strict`.
5. Commit; the project is pipeline-ready.

---

## 4. Per-step specification

Conventions: `<WI>` = work-item ID (`FEAT-012`, `BUG-003`, `IMP-002`), `<T>` = task ID
(`T-004`), `<slug>` = kebab-case short title. All gate commands run from the project root.

### Step 1 — Brief creation (`step: brief`)

| | |
|---|---|
| Purpose | Produce the work item — the pipeline's densest, highest-leverage artifact (measured: its impact tables carry most of the grounding downstream steps need). |
| Trigger | Human intent: a feature/bug/improvement to do. |
| Orchestrator provides | The work-item TYPE and raw intent (a paragraph, a ticket link, bug evidence). Allocates the next free ID per type. Human-authored briefs are equally valid — this step may be a form, not a session. |
| Session prompt (if AI-assisted) | "Read CLAUDE.md. Copy docs/work-items/TEMPLATE-feature-brief.md to docs/work-items/<WI>-<slug>.md and fill it for: <intent>. Interview me for anything the template needs that the description doesn't cover. Impact tables must name entities/resources/screens precisely — they are retrieval keys; mark not-yet-existing shards `(new)`." |
| Output | `docs/work-items/<WI>-<slug>.md`, Status `Not Started`/`Reported`/`Proposed`. |
| Gate | Human review of the brief (scope lock and acceptance criteria especially). Mechanical: every existing shard the impact tables reference resolves — `python .ai-framework/tools/validate-specs.py --root .` covers this (work-item retrieval-key check). |
| Commit | `docs(<WI>): brief` |
| Events | `started`, `artifact_committed`, `accepted` |

### Step 2 — Task generation (`step: task-generation`)

| | |
|---|---|
| Precondition | Brief accepted; spec shards its impact tables reference exist (or are marked `(new)`). |
| Orchestrator provides | The `<WI>` only. |
| Session prompt | "Read CLAUDE.md. Generate tasks for <WI> per the routing table row '<New feature\|Bug fix\|Refactoring>'. Write tasks/<WI>-tasks.md and run the validator self-check before finishing." |
| Context the session reads (via routing table) | Work item + CLAUDE.md (+ ARCHITECTURE for refactors) + each spec's `index.md` + impact-table shards. |
| Output | `tasks/<WI>-tasks.md` — canonical schema blocks; feature lists end with the AC coverage table. |
| Gate (orchestrator re-runs) | `python .ai-framework/tools/validate-tasks.py tasks/<WI>-tasks.md --work-item docs/work-items/<WI>-<slug>.md --root .` → exit 0. Optionally `--strict` in CI. |
| On gate failure | One repair session ("fix every validator error, change nothing else"), then regenerate from scratch, then human. |
| Optional best-of-N | For L/XL briefs: run N=3 generation sessions, discard validator failures, feed survivors to step 3 review, pick/synthesize. |
| Commit | `tasks(<WI>): generate task list` |
| Events | `started`, `artifact_committed`; `accepted` comes from step 3 |

### Step 3 — Task-list review (`step: task-review`) — FRESH SESSION

| | |
|---|---|
| Precondition | Task list committed, validator-clean. **The reviewing session must not be the generating session.** |
| Orchestrator provides | The `<WI>`. Nothing from step 2's session. |
| Session prompt | "FRESH REVIEW — you did not generate this. Read CLAUDE.md. Review tasks/<WI>-tasks.md per the routing row 'Task list review'. Run both validators first and treat their output as ground truth. Write tasks/<WI>-review.md." |
| Output | `tasks/<WI>-review.md` — `## Verdict` approve/revise + findings table + required changes. |
| Gate | Parse the verdict. `approve` ⇒ mark task list accepted (`accepted` event). `revise` ⇒ spawn a revision session with the review file in context ("apply every required change to tasks/<WI>-tasks.md"), re-run the step-2 gate, then re-review. Cap at 2 loops before human escalation. |
| Commit | `review(<WI>): task list <verdict>` |
| Skip rule | May be skipped for S-complexity adhoc lists; never skip for L/XL or multi-task briefs. |

### Step 4 — Planning (`step: planning`, per task)

| | |
|---|---|
| Precondition | Task list accepted; the task's Dependencies are complete; **Workflow honored**: `mockup-first` ⇒ run the UI mockup row first (`mockups/<T>-<screen>.html`, human approval) — `investigation-first` ⇒ the investigation task(s) completed and findings recorded before fix tasks are planned. |
| Orchestrator provides | `<WI>` and `<T>`. |
| Session prompt | "Read CLAUDE.md. Create the implementation plan for <T> from tasks/<WI>-tasks.md per the routing row 'Task implementation plan'. Write plans/plan-<T>-<slug>.md within the plan budget." |
| Context (via routing) | The task block, CLAUDE.md, the files its Files to Modify/Create names (existing ones), conditional spec shards. |
| Output | `plans/plan-<T>-<slug>.md` — ≤ ~150 lines, ≤ 10 steps, Acceptance Verification section. |
| Gate | Mechanical: file exists, ≤ ~150 lines (`line_count` logic), mentions `<T>`. Semantic: human skim or accept on the strength of the baseline (plans measured 9.0 with zero variance — the safest step to auto-accept). |
| Commit | `plan(<T>): implementation plan` |
| Events | `started`, `artifact_committed`, `accepted` |

### Step 5 — Assignment (`step: assignment`) — orchestrator-internal

No framework session. The orchestrator schedules accepted-plan tasks respecting:
(a) the Dependencies DAG; (b) file-set non-overlap (two tasks whose Files to
Modify/Create intersect never run concurrently); (c) Workflow prerequisites already
enforced in step 4. Emit `started`(assignment)/`completed` with the assignee in `detail`.
The framework's task blocks carry no Status/Assignee fields — the orchestrator is the
authority for per-task state (deliberate; see §6).

### Step 6 — Implementation (`step: implementation`, per task)

| | |
|---|---|
| Precondition | Plan accepted; task assigned. |
| Orchestrator provides | `<WI>`, `<T>`, and a working branch (recommended: `task/<T>-<slug>`). |
| Session prompt | "Read CLAUDE.md. Implement <T> from tasks/<WI>-tasks.md following plans/plan-<T>-<slug>.md exactly; document any deviation in the commit message. Update the spec shards your changes affect (+ stamps + index changelog) per the maintenance table. Run the test suite and `python .ai-framework/tools/validate-specs.py --root .` before finishing." |
| Session tooling | Needs wider Bash allowances (test runner, linters) than other steps. |
| Output | Code changes + spec-shard updates on the branch. **Implementation record**: the orchestrator stores the branch/commit range against `<T>` (the framework does not — orchestrator-owned state). |
| Gate | Tests pass; `validate-specs.py` clean when shards were touched. The real gate is step 7. |
| Commit | The session's own commits on the branch; conventional style per CLAUDE.md. |
| Events | `started`, `artifact_committed` (head SHA in detail), `completed` after step 7 approves |

### Step 7 — Implementation review (`step: implementation-review`) — FRESH SESSION

| | |
|---|---|
| Precondition | Implementation pushed to its branch. **Fresh session — not the implementer.** |
| Orchestrator provides | `<WI>`, `<T>`, and the diff handle: either a git range (`git diff main..task/<T>-<slug>`) or the branch name. This is the one step where the orchestrator supplies material beyond IDs — the diff is not derivable from the routing table. |
| Session prompt | "FRESH REVIEW — you did not implement this. Read CLAUDE.md. Review the implementation of <T> per the routing row 'Implementation review'. The diff: `git diff <range>`. Gather evidence first (run tests, linters, validate-specs) and treat it as ground truth. Write tasks/<T>-implementation-review.md." |
| Output | `tasks/<T>-implementation-review.md` — verdict, findings (AC satisfaction, plan adherence, scope, conventions, spec sync, test adequacy), required changes. ≤ ~120 lines. |
| Gate | Parse verdict. `revise` ⇒ fix session on the same branch with the review in context, then re-review (cap 2 loops → human). `approve` ⇒ merge the task branch, mark `<T>` complete, emit `accepted` + `completed`. |
| Commit | `review(<T>): implementation <verdict>` (the review file goes to the main branch or the task branch per your merge flow — pick one and stay consistent). |
| Skip rule | Recommended for M+ complexity; S tasks may go straight to merge on green tests. Measured: these reviews catch unplanned real defects, not just planted ones — skip sparingly. |

### Step 8 — Task completion

Orchestrator-internal state flip once step 7 approves and the branch is merged.
Emit `completed`. When ALL non-documentation tasks of the brief are complete, proceed
to step 9.

### Step 9 — Docs-update task (`step: docs-update`)

| | |
|---|---|
| Purpose | The batch documentation pass the operating model uses instead of per-change doc edits. |
| Precondition | All other tasks complete. **If the task list contains no Documentation-type closing task, the orchestrator creates the work**: its Files to Modify/Create are mechanically derivable — the work item's impact-table shards + stamps + index changelogs. |
| Session prompt | "Read CLAUDE.md. Execute the documentation task for <WI>: bring every shard named by the work item's impact tables in line with the merged implementation; refresh 'Last verified against code' stamps; add index changelog rows. Acceptance: `python .ai-framework/tools/validate-specs.py --root . --strict` passes." |
| Gate | That exact command, run by the orchestrator. This converts "remember what changed" into "make the linter pass". |
| Commit | `docs(<WI>): sync specs post-implementation` |

### Step 10 — Brief closure (`step: closure`)

Orchestrator-internal checklist (no session needed; a session may do the mechanical bits):

1. Every task `completed`; docs task gate green.
2. `validate-specs.py --strict` clean at the repo root.
3. Work item Status → `Completed`/`Resolved` (+ date); for bugs, Root Cause & Resolution filled.
4. Traceability updated (bug→feature links etc.).
5. `python .ai-framework/tools/metrics-report.py` run and archived — the per-brief scorecard.
6. Final commit `close(<WI>)`; emit `completed`(closure). Merge per your branch strategy.

---

## 5. Gates summary

| After step | Command | Pass criterion |
|---|---|---|
| 2 (and any task-list change) | `python .ai-framework/tools/validate-tasks.py tasks/<WI>-tasks.md --work-item <brief> --root .` | exit 0 |
| 3, 7 | parse `## Verdict` in the review file | `approve` |
| 4 | plan exists, ≤ ~150 lines, references `<T>` | mechanical |
| 6 (shards touched) | `python .ai-framework/tools/validate-specs.py --root .` | exit 0 |
| 9, 10 | `python .ai-framework/tools/validate-specs.py --root . --strict` | exit 0 |
| any time | `python .ai-framework/tools/metrics-report.py --root .` | informational |

---

## 6. What the orchestrator owns (deliberately outside the framework)

- **Per-task state machine** (`pending → planned → assigned → in-progress → implemented → reviewed → done`) and assignees. Artifacts stay immutable after acceptance; the orchestrator is the single writer of state. (A `Status:` field in task blocks was considered and deferred — see BACKLOG.)
- **Implementation records** — task → branch/commits/PR mapping.
- **ID allocation** — next free `FEAT/BUG/IMP` numbers (or adopt tracker keys).
- **Revise-loop budgets and human escalation.**
- **Token/cost capture** per session into the event log.
- **Best-of-N orchestration** where used (generate N, validator-filter, fresh-review, pick).

## 7. Practical calibration (from the measured baselines)

- Auto-accept confidence, highest first: plans (9.0, zero variance) > feature/UI-spec
  outputs (9.0) > ADR compilation (8.7) > data-model (8.3) > bugfix/mockups (8.0).
  Reviews still gate everything M+; the numbers say where a lenient policy is safe.
- Session durations for scheduling: plans 4–6 min, task lists/reviews 3–8 min,
  data models 5–7 min, mockups 7–9 min, UI specs 12–14 min.
- Reviews find real issues beyond what they're pointed at — budget for acting on
  legitimate findings outside the current task (park them as new work items rather
  than expanding scope mid-task).
- Never strip the self-check instruction from a generation prompt to save time —
  it is the measured difference between 100% and 0% schema compliance.
