# shortlist / attended (`/orchestrate` fixture) on framework 2.7.0

The in-repo mode driven one step per invocation from a Claude Code session, all-Opus, with
the human running the printed gates. Seeded from the same inputs as the two autonomous arms
(`testsys-orch`'s first commit: "human inputs identical to testsys-shortlist @ 052f580").
No product was built, so there is no exam; the record exists because this fixture is the
evidence behind two framework changes.

| Field | Value |
|---|---|
| Framework version | 2.7.0 (`7eb1aff`) |
| Brief | shortlist v1 |
| Arm | attended: `/orchestrate` scaffold command, one step per invocation |
| Models (as reported) | `claude-opus-5` / `opus` on 4 of 5 events |
| Started / finished | 2026-08-03T11:54:10-03:00 to 2026-08-03T15:37:01-03:00 |
| Project checkout | `Repos/proof/testsys-orch @ 5ebbc5d` (7 commits) |

## Outcome

| Metric | Value |
|---|---|
| Exam | not run (no implementation) |
| Steps completed | preflight fix (restored `(new)` markers the validator demanded), spec bootstrap, task generation (15 tasks: S 7, M 7, L 1), fresh task-list review (revise), revision, fresh re-review (revise, loop 2), **stopped at the cap** |
| First-pass acceptance (event log) | task-list review 0/2 |
| Tokens / notional cost | 277,962 logged / not logged |

## Findings

1. **The ratchet in attended mode.** Two revise rounds with new findings each time before the
   human stopped it, matching both autonomous arms. The CHANGELOG for v2.8.0 counts this as
   "two in the /orchestrate fixture".
2. **Re-review had to be requested by the human.** After the revision landed, the one-step
   driver kept emitting the revision step because it only read the stale verdict file; the
   orchestrating session escalated purely to ask "re-review now?". Became v2.7.1 (mechanical
   re-review detection from commit order), the first fix this fixture paid for.

Raw: `events.ndjson` (5 events).
