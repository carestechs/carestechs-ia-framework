# Feature Brief: FEAT-001 — Link Shortening Core

> **Purpose**: Describe a feature at a high level before breaking it down into implementation tasks.
> **Template reference**: `.ai-framework/templates/feature-brief.md`

> **Context budget note:** This document is loaded into AI context — keep it contract-style (tables, schemas, rules); move narrative and history to `docs/rationale/` and link it (rationale files are never loaded by default).

---

## 1. Identity

| Field | Value |
|-------|-------|
| **ID** | FEAT-001 |
| **Name** | Link Shortening Core |
| **Target Version** | v1 |
| **Status** | Not Started |
| **Priority** | Critical |
| **Requested By** | Carlos (product owner) — the entire v1 scope |
| **Date Created** | 2026-08-03 |

---

## 2. User Story

**As a** team developer (Rafa), **I want to** turn long URLs into short codes I can create, share, inspect, and delete over a simple HTTP API, **so that** internal links are speakable, chat-safe, and I can see whether they get clicked.

---

## 3. Goal

A running Shortlist service where every endpoint of the v1 scope lock works exactly as specified and every status-code contract is proven by the automated suite.

---

## 4. Feature Scope

### 4.1 Included

- Solution skeleton: `Shortlist.Api` + `Tests/Shortlist.Api.Tests` (net10.0, nullable, warnings-as-errors)
- `POST /api/links` — create with generated 6-char base62 code, or optional custom code (4–32 chars `[A-Za-z0-9_-]`)
- `GET /{code}` — 302 redirect to the original URL with an atomic click count increment
- `GET /api/links` (list), `GET /api/links/{code}` (detail + stats), `DELETE /api/links/{code}`
- Problem Details for all 400/404/409 responses
- Integration + unit test suite per CLAUDE.md testing conventions

### 4.2 Excluded

- Persistence, auth, UI, expiry, bulk operations — all excluded by the stakeholder scope lock (v2+ candidates)

---

## 5. Acceptance Criteria

- **AC-1**: `POST /api/links` with a valid absolute HTTP/HTTPS URL returns `201` with a `LinkResponse` carrying a generated 6-char base62 code, and `GET /{code}` immediately resolves to it.
- **AC-2**: `POST /api/links` with a free custom code creates it (`201`); with a taken code returns `409` Problem Details; with an invalid URL or malformed custom code returns `400` Problem Details carrying an `errors` dictionary.
- **AC-3**: `GET /{code}` returns `302` with `Location` = the original URL and increments `clickCount` exactly once per request (safe under concurrent requests, proven by a parallel test); unknown code returns `404` Problem Details.
- **AC-4**: `GET /api/links` lists all links with `clickCount` and `lastClickedAt`; `GET /api/links/{code}` returns one; `DELETE /api/links/{code}` returns `204` and subsequent redirects for that code return `404`.
- **AC-5**: `dotnet test` passes with every documented status-code contract covered by a `WebApplicationFactory` integration test.

---

## 6. Key Entities and Business Rules

| Entity | Role in Feature | Key Business Rules |
|--------|----------------|--------------------|
| Link | The only entity: code → URL mapping with click stats | Code unique; generated codes 6-char base62; custom codes 4–32 chars `[A-Za-z0-9_-]`; URL must be absolute http/https; `clickCount` increments atomically; `lastClickedAt` null until first click |

**New entities required:** Link → `docs/data-model/entities/link.md` (new)

---

## 7. API Impact

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/api/links` | POST | New | Create; 201 / 400 / 409 |
| `/api/links` | GET | New | List all |
| `/api/links/{code}` | GET | New | Detail + stats; 404 |
| `/api/links/{code}` | DELETE | New | 204 / 404 |
| `/{code}` | GET | New | Redirect 302; 404; documented in the links resource shard |

**New endpoints required:** links resource (including the redirect route) → `docs/api-spec/endpoints/links.md` (new)

---

## 8. UI Impact

| Screen / Component | Status | Description |
|--------------------|--------|-------------|
| — | — | No UI: API-only product (stakeholder scope decision) |

**New screens required:** None

---

## 9. Edge Cases

- Concurrent redirects to the same code must each count exactly once (no lost increments)
- Custom code equal to an already generated code → 409 (single namespace)
- Custom code colliding with reserved route prefixes (`api`) → 400 (reserved)
- URL with query string and fragment must round-trip byte-identical in the redirect `Location`
- Generated-code collision on insert → regenerate transparently (never surfaces to the caller)
- Delete then re-create the same custom code → allowed (namespace freed)

---

## 10. Constraints

- Zero production NuGet dependencies; in-memory store only (scope lock)
- Redirect route must not shadow `/api/*` routes
- All error responses Problem Details per CLAUDE.md Error Handling

**Non-Functional Requirements (optional):** none beyond global standards.

---

## 11. Motivation and Priority Justification

**Motivation:** FEAT-001 IS the v1 product — the experiment needs a complete, testable vertical slice.

**Impact if delayed:** no product; nothing else exists to build.

**Dependencies on this feature:** all future work items (persistence, auth) build on this API surface.

---

## 12. Traceability

| Reference | Link |
|-----------|------|
| **Persona** | `docs/personas/primary-user.md` |
| **Stakeholder Scope Item** | Scope Lock v1 — all four capability bullets (3.1) |
| **Success Metric** | "two curl commands in under a minute"; "`dotnet test` green proves every contract" |
| **Related Work Items** | None yet |
