# CLAUDE.md — TaskFlow

TaskFlow is a small web-based task tracker (projects, tasks, membership, comments) built as a REST API + SPA.

## Stack

- **Language:** TypeScript (strict mode) across backend and frontend
- **Backend:** Node.js + Express 4, `pg` driver against PostgreSQL 16 (no ORM)
- **Frontend:** React 18 (function components + hooks), Vite, TanStack Query for server state
- **Testing:** Vitest everywhere; Supertest for API integration tests

## Planned Project Structure

The codebase is not started yet; this is the committed layout.

| Path | Contents |
|------|----------|
| `src/server.ts` | Express app entry — mounts the router from `src/api/index.ts` |
| `src/api/` | One Express router per resource; error middleware in `src/api/errors.ts` |
| `src/db/` | One repository module per entity, e.g. `src/db/task.ts`, `src/db/project.ts` |
| `src/ui/` | One React file per screen |
| `migrations/` | Plain SQL migrations, numbered `NNN-description.sql`, e.g. `migrations/001-init.sql` |
| `tests/` | Tests mirror `src/`, e.g. `tests/api/tasks.test.ts` |

## Conventions

1. **Naming:** kebab-case filenames; PascalCase React components and types; camelCase functions and variables; snake_case database tables and columns. JSON payloads use camelCase keys.
2. **Response envelope:** every success response is `{ "data": ... }`; list responses add `"meta": { "totalCount", "page", "pageSize" }`. Never return raw database rows.
3. **Error handling:** error responses are `{ "error": { "code", "message", "fields?" } }` with stable machine-readable codes. Routers throw `ApiError`; the middleware in `src/api/errors.ts` serializes it.
4. **Validation:** every router validates request bodies and query parameters with Zod schemas defined next to the route handlers.
5. **Data access:** SQL lives only in `src/db/` repository modules — routers never touch `pg` directly. One repository module per entity.
6. **Database:** snake_case tables, **plural** (`tasks`, `project_members`); snake_case columns; **UUID v4 primary keys in a column named `id`**; `created_at` + `updated_at` `timestamptz` (always UTC) on every table; explicit varchar limits (`varchar(200)`, never bare `varchar`); **hard deletes** (no `deleted_at` columns) in V1.
7. **User identity:** the external auth service issues **opaque user UUIDs**; the app database stores them in `*_id` columns and has **no local User entity** — never model users as a table.

## AI-Assisted Development Framework

This project uses the carestechs IA framework. The prompts live in the framework repo, not in this project.

- **Spec docs do not exist yet.** This project is at the strategy stage: `docs/` holds only `stakeholder-definition.md` and `ARCHITECTURE.md`. Spec generation (framework prompt `prompts/spec-generation.md`) will create the sharded spec sets, starting with `docs/data-model/` — `index.md` plus one `entities/<entity>.md` per entity (kebab-case, singular).
- Once generated, specs are sharded under `docs/`: read each spec's `index.md` plus only the shards named by a work item's impact tables. Do not read whole spec directories.
- Generated spec files are written to the location given by the harness instructions (`GENERATE.md` in the case directory), not to the project root.
