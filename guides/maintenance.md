# Documentation Maintenance Guide

> **Purpose**: This guide explains when and how to update the 12 documentation artifacts (10 templates + HTML mockups + Component Examples) to keep them synchronized with the codebase. Outdated documentation leads to incorrect AI task generation and wasted effort.

---

## Core Principle: Documentation as Code

Treat documentation with the same rigor as code:
- Review docs in PRs that change related code
- Include doc updates in definition of done
- Automate sync verification where possible

---

## Freshness Stamps

Every spec shard (`docs/data-model/entities/*.md`, `docs/api-spec/endpoints/*.md`, `docs/ui-specification/screens/*.md`, `docs/ui-specification/components.md`), every spec `index.md`, and `ARCHITECTURE.md` carries a stamp directly under its H1, in exactly this format:

```markdown
> **Last verified against code:** YYYY-MM-DD (commit `abc1234`)
```

**Rules:**

- **Update the stamp whenever a shard is edited** — set the date and the current commit.
- **Update the stamp whenever a shard is verified against code**, even if no edit was needed. A fresh stamp means "this file matched the code on this date", not "this file was last written on this date".
- **Verify untouched shards per release.** Re-verifying shards that no code change touched is part of the Sprint/Release Verification below — otherwise accurate shards accumulate stale stamps and force needless re-verification.
- **Agents must verify before trusting.** Before relying on a shard whose stamp is missing or older than 30 days, verify its claims against the source (grep/read the relevant code). If it drifted: fix the shard, add a changelog entry to the spec's `index.md`, and update the stamp. This mirrors the "Trust code over docs" item in the CLAUDE.md Pre-Work Checklist.

**Shard frontmatter:** every spec shard begins (before its H1) with a machine-readable frontmatter block — kind, name, and cross-references (e.g., an entity's `endpoints`/`screens`, a screen's `endpoints`) — used by `validate-specs.py` and by orchestrators for deterministic shard retrieval. Update the frontmatter whenever a shard's relationships change, not just its body — e.g., when a new screen starts calling a resource, add that resource to the screen shard's `endpoints` list. `python .ai-framework/tools/validate-specs.py` checks that these cross-references resolve and that stamps are fresh.

---

## Document Lifecycle Matrix

| Document | Created | Updated | Reviewed | Retired |
|----------|---------|---------|----------|---------|
| Persona | Product discovery | Major pivot | Quarterly | Segment deprecated |
| Stakeholder Definition | Project start | Feature shipped or strategy change | Per feature ship | Project end |
| Architecture | System design | Structural changes | Quarterly | System retired |
| CLAUDE.md | Project start | Convention changes | Quarterly | - |
| Data Model | Project start | Entity/field changes | Per release | Major version rewrite |
| API Specification | Project start | Endpoint/DTO changes | Per release | Major version rewrite |
| UI Specification | Project start | Screen/component changes | Per release | Major version rewrite |
| HTML Mockups | Pre-implementation | Design/layout changes | Per release | Screen implemented |
| Component Examples | DDR compilation | Design token changes, component DDR updates | Per release | Project design system stabilized |
| Feature Brief | Before feature task generation | Scope/AC changes during implementation | When tasks are generated | Feature completed or cancelled |
| Bug Report | When bug is discovered | Investigation reveals new info | When fix is verified | Bug resolved or closed |
| Improvement Proposal | Before refactoring task generation | Risk/scope changes during implementation | When improvement is complete | Improvement completed or deferred |

---

## Update Triggers by Document Type

> **Stack note:** The checklists in this guide use a .NET + Angular + Tailwind example stack (EF Core entities, C# DTOs, Angular components, Tailwind tokens) — substitute the equivalents from the stack declared in your CLAUDE.md.

### 1. Persona Documents

**Update When:**
- User research reveals new insights
- Customer feedback contradicts assumptions
- Market conditions change
- New customer segment identified
- Usage data shows different behavior than expected

**Update Process:**
1. Document the trigger (what changed)
2. Review current persona with stakeholders
3. Update affected sections
4. Propagate changes to dependent docs (stakeholder definition)

**Review Checklist:**
- [ ] Pain points still accurate?
- [ ] Behavior patterns match reality?
- [ ] Technology relationship current?
- [ ] Strategic fit still valid?

---

### 2. Stakeholder Definition

> **Note:** Triggers referencing Current Work / Release History / Under Consideration / Not Planned assume the continuous development model. If using the versioned model, these sections don't exist yet — see `guides/release-lifecycle.md`.

**Update When:**
- Feature shipped (move from Current Work → Release History)
- Development model changed (versioned → continuous) — see `guides/release-lifecycle.md`
- Product strategy shifts
- Success metrics need adjustment
- Current Work, Under Consideration, or Not Planned items change
- New guiding principles adopted

**Update Process:**
1. Identify which section changed (Release History, Current Work, Under Consideration, Not Planned)
2. Move items between sections as appropriate
3. Review current metrics against actuals
4. Communicate changes to team

**Review Checklist:**
- [ ] Success metrics still measurable and relevant?
- [ ] Current Work reflects what's actually being built?
- [ ] Release History is up to date with shipped features?
- [ ] Guiding principles still apply?
- [ ] Philosophy aligned with execution?

---

### 3. Architecture Document

**Update When:**
- New component added
- Component removed or deprecated
- Integration point added/removed
- Technology stack changes
- Scaling approach changes
- Security model changes

**Update Process:**
1. Update diagrams first
2. Update component descriptions
3. Update data flow documentation
4. Review integration points
5. Verify consistency with code

**Review Checklist:**
- [ ] Diagrams match deployed system?
- [ ] All components documented?
- [ ] Integration points current?
- [ ] Security section accurate?
- [ ] Technology stack list complete?

---

### 4. CLAUDE.md (Code Conventions)

**Update When:**
- New pattern adopted
- Pattern deprecated
- File structure changes
- New tool/library adopted
- Naming conventions change
- Common gotchas discovered

**Update Process:**
1. Propose change in team discussion
2. Update CLAUDE.md
3. Add examples of new pattern
4. Communicate to team
5. Update related tooling (linters, etc.)

**Review Checklist:**
- [ ] Patterns match actual code?
- [ ] Examples are current?
- [ ] No outdated conventions?
- [ ] Common gotchas documented?
- [ ] Security checklist current?

---

### 5. Data Model (`docs/data-model/`)

**Update When → Where:**

| Trigger | Update |
|---------|--------|
| New entity added to a module | New shard `docs/data-model/entities/<entity>.md` (kebab-case, singular) + `index.md` if module ownership, conventions, or the relationships overview change |
| Field added, removed, or type-changed | Affected `entities/<entity>.md` shard |
| Index added, removed, or modified | Affected `entities/<entity>.md` shard |
| Enum value added or renamed | Entity shard (entity-specific enums) or `index.md` (shared enums/value types) |
| Relationship or cascade behavior changed | Affected entity shard(s) + `index.md` relationships overview (ER diagram) |
| Database convention or business rule added/corrected | `index.md` (cross-cutting) or the affected entity shard (entity-specific) |

**Update Process:**
1. Edit the affected shard(s) first — `entities/<entity>.md` for entity-level changes, `index.md` for conventions, ownership, and relationships
2. Implement the change in code (EF Core entity, migration, service logic)
3. Include both the doc update and code change in the same PR
4. Update the freshness stamp on every file you edited; add a changelog entry to `index.md`
5. Verify the relationships overview (ER diagram) in `index.md` still reflects the change (update if needed)

**Review Checklist:**
- [ ] Every persisted entity has a shard, and each shard matches its EF Core entity class?
- [ ] Field types and constraints match migration code?
- [ ] Indexes listed match actual migration indexes?
- [ ] Enum values match C# enum definitions?
- [ ] Cross-module references are ID-only (no navigation properties)?
- [ ] Relationships overview (ER diagram) in `index.md` reflects current entity structure?
- [ ] Business rules are accurate and complete?

---

### 6. API Specification (`docs/api-spec/`)

**Update When → Where:**

| Trigger | Update |
|---------|--------|
| New or changed endpoint (route, method, auth) | `docs/api-spec/endpoints/<resource>.md` (shard named after the route segment, plural) |
| Request or response DTO shape changed (field added, renamed, type changed) | Affected `endpoints/<resource>.md` shard |
| New query parameter or filter added to a list endpoint | Affected `endpoints/<resource>.md` shard |
| Status code or error condition added/corrected | Affected endpoint shard; `index.md` Error Catalog if a new error type/code is introduced |
| Response envelope, pagination, or auth convention changed | `index.md` |
| Shared DTO (e.g., `UserSummaryDto`, `PaginationMeta`) modified | `index.md` (+ endpoint shards that reference it, if shapes shown there change) |

**Update Process:**
1. Edit the affected shard first — `endpoints/<resource>.md` for endpoint/DTO changes, `index.md` for envelope, error catalog, auth, and pagination conventions
2. Implement the change in code (controller, service, DTO class)
3. Include both the doc update and code change in the same PR
4. Update the freshness stamp on every file you edited; add a changelog entry to `index.md`

**Review Checklist:**
- [ ] All endpoints match controller actions, and each resource shard contains all endpoint blocks for that resource?
- [ ] Request/response JSON shapes match DTO classes?
- [ ] Status codes match actual controller responses and map to the Error Catalog in `index.md`?
- [ ] Auth requirements match `[Authorize]` attributes?
- [ ] Pagination parameters match list endpoint implementations?
- [ ] Shared DTOs in `index.md` match actual C# DTO classes?

---

### 7. UI Specification (`docs/ui-specification/`)

**Update When → Where:**

| Trigger | Update |
|---------|--------|
| New screen or page added | New shard `docs/ui-specification/screens/<screen>.md` (kebab-case — "Project Board" → `project-board.md`) |
| Screen layout or component hierarchy changed | Affected `screens/<screen>.md` shard |
| Design token changed (color, typography, spacing) | `docs/ui-specification/index.md` (Design System) + affected HTML mockups |
| New shared component added or existing one modified | `components.md` (+ screen shards whose hierarchies change) |
| Interaction pattern added or changed (new user action, new drag-drop behavior) | Affected `screens/<screen>.md` shard |
| Component → API mapping changed (component now calls a different endpoint) | Affected `screens/<screen>.md` shard |
| Screen state handling changed (new loading skeleton, different empty state) | Affected `screens/<screen>.md` shard (or `index.md` if a cross-screen state pattern changed) |

**Update Process:**
1. Edit the affected shard first — `screens/<screen>.md` for screen changes, `components.md` for shared components, `index.md` for design tokens and cross-screen patterns
2. Implement the change in code (Angular component, template, styles)
3. Include both the doc update and code change in the same PR
4. Update the freshness stamp on every file you edited; add a changelog entry to `index.md`

**Review Checklist:**
- [ ] Every implemented screen has a shard in `screens/`, and no shard describes a removed screen?
- [ ] Component hierarchies match actual Angular component trees?
- [ ] Component → API mappings match actual service calls in components?
- [ ] All 4 states (default, loading, empty, error) are defined for every screen?
- [ ] `components.md` matches actual reusable components?
- [ ] Design tokens in `index.md` match actual Tailwind config / Angular Material theme?
- [ ] User interactions match actual event bindings in templates?
- [ ] Routes match actual Angular router configuration?

---

### 8. HTML Mockups

**Update When:**
- Design tokens change (Design System in `docs/ui-specification/index.md`)
- Screen layout changes (component hierarchy or ASCII sketch modified in the screen's shard)
- Stakeholder feedback requires visual revisions
- Angular Material theme reconfigured

**Update Process:**
1. Identify which mockups are affected by the change (check `mockups/` directory)
2. Regenerate affected mockups using the [`mockup-generation.md`](../prompts/mockup-generation.md) prompt with updated context
3. Open regenerated files in a browser and verify visual accuracy
4. Include updated mockup files in the same PR as the code/doc change

**Review Checklist:**
- [ ] Colors match current design tokens from UI Specification?
- [ ] Layout matches current ASCII sketch and component hierarchy?
- [ ] All states are accurate and correctly labeled?
- [ ] File naming follows the `mockups/T-XXX-screen-name.html` convention?

---

### 9. Component Examples (`docs/component-examples.md`, from DDR Compilation)

**Update When:**
- Design tokens change in `docs/ui-specification/index.md` (colors, typography, spacing)
- A component DDR is updated in the shared DDR repo (new variant, changed constraint)
- A state pattern DDR is updated (new loading, empty, or error pattern)
- The project switches profiles or adds/removes DDRs from the compiled set

**Update Process:**
1. Re-run DDR compilation using `compile-ddrs.md` with the updated DDR files or profile
2. Replace `docs/component-examples.md` with the newly compiled Component Examples Appendix
3. Update any CLAUDE.md Design Patterns that changed due to updated DDR constraints
4. Regenerate affected HTML mockups using the updated component examples as context

**Review Checklist:**
- [ ] Component examples match current design token values (colors, fonts, spacing)?
- [ ] Button, card, form, and state examples use the correct Tailwind classes?
- [ ] Examples are consistent with the Design System in `docs/ui-specification/index.md`?
- [ ] Any new component DDRs have been compiled and their examples added?
- [ ] CLAUDE.md Design Patterns/Anti-Patterns are in sync with DDR constraints?

---

### 10. Work Items (`docs/work-items/`)

**Update When:**
- Investigation reveals new information about a bug (update Bug Report)
- Feature scope changes during implementation (update Feature Brief)
- Risk assessment changes during refactoring (update Improvement Proposal)
- Tasks are generated, in progress, or completed (update Status field)

**Update Process:**
1. Update the Status field in Section 1 to reflect current state
2. If scope/details changed, update the relevant sections and note the change
3. When completed, update Status to final state (Completed, Resolved, etc.)

**Status Lifecycle:**

| Work Item Type | Status Progression |
|---------------|-------------------|
| Feature Brief | Not Started → In Progress → Tasks Generated → Completed · Cancelled |
| Bug Report | Reported → Investigating → Fix In Progress → Resolved · Won't Fix |
| Improvement Proposal | Proposed → Approved → In Progress → Completed · Deferred · Rejected |

**Review Checklist:**
- [ ] Status field reflects actual state of work?
- [ ] Acceptance criteria still accurate (not changed during implementation)?
- [ ] Traceability links are correct?
- [ ] Completed work items marked as such?

---

## Sync Verification Checklist

Use this checklist periodically to verify documentation is in sync with code.

### Weekly Verification

> **Team-size tiering:** A weekly cadence suits multi-developer teams. Solo developers should run this checklist monthly or per-release instead — weekly is overkill when one person makes every change.

- [ ] CLAUDE.md patterns match recent PRs
- [ ] Architecture reflects any new services or endpoints
- [ ] Data Model reflects any entity/field changes in recent PRs
- [ ] API Specification reflects any endpoint/DTO changes in recent PRs
- [ ] UI Specification reflects any screen/component changes in recent PRs
- [ ] HTML Mockups reflect current design tokens and layout specs
- [ ] Work item statuses reflect actual state of work

### Sprint/Release Verification

- [ ] Architecture diagram reflects deployments
- [ ] Stakeholder definition reflects current state (Release History, Current Work, Not Planned)
- [ ] CLAUDE.md conventions match team practices
- [ ] Data model entity shards match EF Core entity classes and migrations
- [ ] API spec endpoint shards match controller actions
- [ ] UI spec screen shards match Angular routes and components
- [ ] Untouched spec shards re-verified against code, and freshness stamps refreshed on every shard verified this release (see Freshness Stamps)

### Quarterly Verification

- [ ] Full documentation audit across all 12 documentation artifacts
- [ ] Archive completed/resolved work items (move to `docs/work-items/archive/` or mark clearly)
- [ ] Stakeholder definition alignment with product direction
- [ ] Architecture review against deployed system
- [ ] Persona assumptions validated against user data

---

## Documentation Review in PRs

### When to Require Doc Updates

Add doc updates to PR when:

| Code Change | Document to Update |
|-------------|-------------------|
| New service/component | Architecture |
| New pattern introduced | CLAUDE.md |
| Changed file structure | CLAUDE.md |
| Added external integration | Architecture |
| Changed environment vars | CLAUDE.md |
| Updated dependencies | CLAUDE.md (if affects patterns) |
| Shipped major feature | Stakeholder (update scope) |
| User feedback received | Persona (if contradicts assumptions) |
| Added/changed entity or field | `docs/data-model/entities/<entity>.md` (+ `index.md` if conventions or relationships change) |
| Added/changed index or constraint | `docs/data-model/entities/<entity>.md` |
| Added/changed endpoint | `docs/api-spec/endpoints/<resource>.md` |
| Changed DTO shape | `docs/api-spec/endpoints/<resource>.md` (shared DTOs: `index.md`) |
| Added/changed screen or page | `docs/ui-specification/screens/<screen>.md` |
| Changed component hierarchy | Affected `docs/ui-specification/screens/<screen>.md` |
| Changed design tokens | `docs/ui-specification/index.md` + HTML Mockups (affected screens) |
| Added/changed shared component | `docs/ui-specification/components.md` |
| Changed screen layout | HTML Mockups (affected screens) |

### PR Checklist for Reviewers

```markdown
## Documentation Review

- [ ] Architecture updated if components changed
- [ ] CLAUDE.md updated if new patterns introduced
- [ ] Stakeholder definition reflects current state
- [ ] UI Specification updated if screens or components changed
- [ ] Freshness stamp updated on every spec shard edited in this PR
- [ ] Changelog entry added to each updated spec's `index.md` (and `ARCHITECTURE.md` if it changed)
- [ ] Task lists added/changed in this PR pass `python .ai-framework/tools/validate-tasks.py`
- [ ] Spec shards pass `python .ai-framework/tools/validate-specs.py` (shards internally consistent — frontmatter cross-references resolve, freshness stamps present and fresh)
```

---

## Changelog Entries

Every update to a living spec document must include a changelog entry — and changelogs live in each spec's `index.md`, not in the shards.

**Where changelogs live:** `docs/data-model/index.md`, `docs/api-spec/index.md`, `docs/ui-specification/index.md`, and `ARCHITECTURE.md`. Individual shards do NOT carry changelogs — a shard's history is its freshness stamp plus git history. This is deliberate: per-shard changelog tables would bloat every shard loaded into AI context. When a shard changes, add the entry to its spec's `index.md` and name the shard in the description.

**Format:**

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| YYYY-MM-DD | [name] | Brief description of what changed | PR link, feature name, or trigger |

**Rules:**
- One row per logical change (group related field additions into one entry, don't list each field separately)
- Date is the date the change is made, not the date it ships
- Reason should help someone understand *why* this changed — link a PR, name the feature, or describe the trigger
- Changelog entries are append-only — never edit or remove previous entries
- When multiple specs are updated in the same PR, each spec's `index.md` gets its own changelog entry
- Shard-level changes are recorded in the owning spec's `index.md` changelog (e.g., "Added `dueDate` field to `entities/task.md`") — never add changelog tables to shards

---

## Handling Documentation Debt

### Identifying Doc Debt

Signs of documentation debt:
- AI generates tasks that don't match codebase
- New team members confused by docs
- Docs reference removed features/code
- Multiple "accurate" versions of truth
- Tribal knowledge not written down

### Paying Down Doc Debt

1. **Triage**: List all known inaccuracies
2. **Prioritize**: Focus on CLAUDE.md and Architecture first (most impact on AI task generation)
3. **Schedule**: Allocate time each sprint for doc maintenance
4. **Culture**: Make doc updates part of definition of done

### Doc Debt Sprint Template

```markdown
## Documentation Debt Sprint

### High Priority (AI Task Generation Impact)
- [ ] Update CLAUDE.md with current patterns
- [ ] Verify architecture matches deployed system
- [ ] Verify data model shards match EF Core entities and migrations
- [ ] Verify API spec shards match controller actions and DTOs
- [ ] Verify UI spec shards match Angular routes, components, and design tokens
- [ ] Refresh freshness stamps on every shard verified

### Medium Priority (Team Productivity)
- [ ] Update stakeholder definition (Current Work, Release History)
- [ ] Archive completed features to Release History

### Low Priority (Long-term Health)
- [ ] Quarterly persona review
- [ ] Stakeholder definition alignment
```

---

## Quick Reference: "When Do I Update X?"

```
Code Change                    → Update These Docs
─────────────────────────────────────────────────────────────
Added new service/component    → Architecture
Changed component structure    → Architecture
Added external integration     → Architecture
Introduced new code pattern    → CLAUDE.md
Changed file structure         → CLAUDE.md
Changed environment vars       → CLAUDE.md
Updated dependencies           → CLAUDE.md (if affects patterns)
Product strategy shifted       → Stakeholder Definition
Feature lifecycle state changed → Stakeholder Definition
User feedback contradicts docs → Persona
New user research insights     → Persona
Added/changed entity or field  → docs/data-model/entities/<entity>.md
                                 (+ index.md if conventions or
                                 relationships change)
Added/changed index/constraint → docs/data-model/entities/<entity>.md
Added/changed API endpoint     → docs/api-spec/endpoints/<resource>.md
Changed DTO shape or status    → docs/api-spec/endpoints/<resource>.md
                                 (shared DTOs / error catalog:
                                 api-spec index.md)
Added/changed screen or page   → docs/ui-specification/screens/<screen>.md
Changed component hierarchy    → affected screens/<screen>.md shard
Changed design tokens          → docs/ui-specification/index.md
                                 + HTML Mockups (affected screens)
Added/changed shared component → docs/ui-specification/components.md
Changed screen layout          → HTML Mockups (affected screens)
Edited or verified a shard     → update its freshness stamp
                                 (+ changelog entry in the spec's
                                 index.md if content changed)
Updated DDR in shared repo     → Re-run DDR compilation, update
                                 Component Examples, CLAUDE.md
                                 Design Patterns, UI Spec Design System
Feature tasks generated        → Feature Brief (Status → Tasks Generated)
Bug fix verified               → Bug Report (Status → Resolved)
Improvement completed          → Improvement Proposal (Status → Completed)
```
