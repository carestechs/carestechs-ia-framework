# CLAUDE.md — TaskFlow

TaskFlow is a small web-based task tracker (projects, kanban boards, tasks) built as a REST API + SPA.

## Stack

- **Language:** TypeScript (strict mode) across backend and frontend
- **Backend:** Node.js + Express 4, `pg` driver against PostgreSQL 16 (no ORM)
- **Frontend:** React 18 (function components + hooks), Vite, TanStack Query for server state
- **Testing:** Vitest everywhere; Supertest for API integration tests

## Project Structure

| Path | Contents |
|------|----------|
| `src/server.ts` | Express app entry — mounts the router from `src/api/index.ts` |
| `src/api/` | One Express router per resource, e.g. `src/api/tasks.ts`; error middleware in `src/api/errors.ts` |
| `src/db/` | One repository module per entity, e.g. `src/db/task.ts`, `src/db/project.ts` |
| `src/ui/` | One React file per screen, e.g. `src/ui/project-board.tsx`, `src/ui/task-detail-panel.tsx` |
| `src/ui/components/` | Shared React components (inventory: `docs/ui-specification/components.md`) |
| `migrations/` | Plain SQL migrations, numbered `NNN-description.sql`, e.g. `migrations/001-init.sql` |
| `tests/` | Tests mirror `src/`, e.g. `tests/api/tasks.test.ts` |

## Conventions

1. **Naming:** kebab-case filenames (`task-detail-panel.tsx`); PascalCase React components and types; camelCase functions and variables; snake_case database tables and columns. JSON payloads use camelCase keys.
2. **Response envelope:** every success response is `{ "data": ... }`; list responses add `"meta": { "totalCount", "page", "pageSize" }`. Never return raw database rows.
3. **Error handling:** error responses are `{ "error": { "code", "message", "fields?" } }`, where `code` is a stable identifier from the Error Catalog in `docs/api-spec/index.md`. Routers throw `ApiError`; the middleware in `src/api/errors.ts` serializes it. Never invent an error code without adding a catalog row first.
4. **Validation:** every router validates request bodies and query parameters with Zod schemas defined next to the route handlers; validation failures map to the `validation-error` catalog entry.
5. **Data access:** SQL lives only in `src/db/` repository modules — routers never touch `pg` directly. One repository module per entity.
6. **Test location:** tests live under `tests/` mirroring the `src/` tree; every router gets a Supertest integration test and every repository gets a unit test against a test database.

## AI-Assisted Development Framework

This project uses the carestechs IA framework. The prompts live in the framework repo, not in this project.

- Specs are **sharded** under `docs/`: `docs/data-model/`, `docs/api-spec/`, `docs/ui-specification/` — read each spec's `index.md` plus **only** the shards named by the work item's impact tables (kebab-case naming rule). Do not read whole spec directories.
- Work items live in `docs/work-items/`.
- Task generation follows `../../../../../prompts/feature-tasks.md` (relative to this file) together with the canonical task schema in `../../../../../prompts/base-template.md`.
- Generated task lists are written to the location given by the harness instructions (`GENERATE.md` in the case directory), not to `tasks/`.
- This project has no `docs/stakeholder-definition.md` or persona documents — the work item's Feature Scope section is the scope authority.
