# Brief: Shortlist (v1)

A self-hosted URL shortener for a small dev team: create a short code for a URL (generated
or custom), redirect with click counting, list, inspect, delete. API-only, in-memory, .NET 10
Minimal API with zero production NuGet dependencies, one API project and one test project.

| Field | Value |
|---|---|
| Brief version | v1 (frozen 2026-10-09) |
| Provenance | `Repos/proof/testsys-shortlist @ 052f580` (2026-08-03), the human inputs both autonomous arms and the `/orchestrate` fixture started from; `testsys-orch`'s first commit states "human inputs identical to testsys-shortlist @ 052f580". The work item carries the two `(new)` markers `testsys-orch @ dd07f41` restored at its preflight ("shards do not exist yet in this arm"): at 052f580 the bootstrap had already generated the shards, so the markers had been dropped, and a fresh seed fails `validate-specs.py` without them (found on the first 2.10.1 seed, 2026-10-10) |
| Framework the inputs were authored against | 2.6.0 scaffold (the run upgraded to 2.7.0 in flight) |
| Work items | FEAT-001 Link Shortening Core (the entire v1 scope) |
| Exam | `exam/shortlist_exam.py`, 16 checks, exam version 1 |
| Test command for the runner policy | `dotnet test` |
| Runner policies | default: `pipeline-runner/policies/testsys-shortlist.json`; control: `pipeline-runner/policies/testsys-shortlist-opus.json` |

## Frozen inputs

```
inputs/
  CLAUDE.md                                   conventions (replaces the scaffold's CLAUDE.md)
  docs/stakeholder-definition.md              vision, scope lock, success metrics, constraints
  docs/ARCHITECTURE.md                        two projects, in-memory store, Problem Details
  docs/personas/primary-user.md               the team developer
  docs/work-items/FEAT-001-link-shortening-core.md
  docs/ui-specification/index.md              "Shortlist has no UI" - the scope decision as a well-formed anchor
  docs/ui-specification/components.md         none, by scope lock
```

These seven files are the brief. Everything else in a run (data model, API spec, task list,
plans, reviews, code, tests) is produced by the pipeline and is what the run measures.

The two UI-specification files are human input, not generation: the product has no UI, so
nothing in the pipeline ever writes them, yet the scaffold ships UI stubs with unfilled
freshness stamps and the runner's bootstrap gate is `validate-specs.py --strict`. On
2026-08-03 the bootstrap failed on exactly that and a human wrote these two files by hand
("session output salvaged + validator fixes to human docs", commit `052f580`); the first
2.10.1 seed reproduced the failure before they were added to the freeze (2026-10-09).

**Stamps are set at seed time.** Every `Last verified against code` stamp in these inputs is
rewritten to the seed date when a run is seeded (the frozen copies keep their 2026-08-03
dates for provenance). The stamps describe intent at seed time, not verified code, and the
strict gate fails any stamp older than 30 days, so a frozen brief would otherwise expire a
month after it was cut.

## Seeding a run

```bash
mkdir shortlist-<version>-<arm> && cd shortlist-<version>-<arm> && git init
cp -r <framework-checkout>/scaffold/. .
cp -r <framework-checkout>/evals/proof-suite/briefs/shortlist/inputs/. .
# stamps describe intent at seed time; the strict bootstrap gate rejects old or unfilled ones
sed -i -E "s/(\*\*Last verified against code:\*\* *)[0-9]{4}-[0-9]{2}-[0-9]{2}/\1$(date +%F)/" \
    docs/ARCHITECTURE.md docs/ui-specification/index.md docs/ui-specification/components.md
git add -A && git commit -m "seed: shortlist@v1 on framework <version>"
```

The brief's `CLAUDE.md` deliberately overwrites the scaffold's: it carries the project's
conventions (naming, error handling as Problem Details, testing with
`WebApplicationFactory`) plus the framework routing table of the version it was authored
against. When the scaffold's routing table has moved on, keep the brief's conventions and
take the scaffold's routing section; note the merge in the record.

## Running the exam

The exam probes a running server and never touches the code.

```bash
# in the project checkout, after closure
dotnet run --project Shortlist.Api -c Release --urls http://127.0.0.1:5181 &
python <framework-checkout>/evals/proof-suite/briefs/shortlist/exam/shortlist_exam.py \
    --base-url http://127.0.0.1:5181 --json exam.json
```

| Check | Brief reference | What passes |
|---|---|---|
| E01, E02 | AC-1 | 201 with a generated 6-char base62 code, zero stats; redirect resolves |
| E03, E04 | AC-2 | free custom code 201; taken code 409 Problem Details |
| E05, E06 | AC-2 | invalid URL / malformed custom code 400 with an `errors` dictionary naming the field |
| E07, E08 | AC-3 | each redirect counts exactly once; 50 concurrent redirects lose nothing |
| E09 | AC-3, AC-4 | unknown code 404 Problem Details on both the redirect and detail routes |
| E10, E11, E12 | AC-4 | list carries stats; detail matches; delete 204 then 404 |
| E13..E16 | section 9 | reserved prefix `api` is 400; query string and fragment round-trip byte-identical; delete then re-create allowed; a custom code equal to a generated one is 409 |

Not graded by the exam: AC-5 (the agents' own test suite, a pipeline gate rather than
evidence), generated-code collision regeneration (not observable from outside), and
anything the stakeholder scope lock excludes.

The exam relies on the request fields being `url` and `customCode` and on ASP.NET's
Problem Details shape. The brief does not pin these; both 2026-08-03 arms converged on
them because `CLAUDE.md` pins the error-handling and JSON conventions. Brief v2, if ever
cut, states the wire contract in section 7 of the work item.

## History

| Date | Framework | Arm | Record |
|---|---|---|---|
| 2026-08-03 | 2.6.0 upgraded to 2.7.0 | default (Sonnet workers), control (all-Opus), `/orchestrate` fixture | `../../results/2.7.0/` (reconstructed from the event logs; exam run retroactively on the preserved builds) |
