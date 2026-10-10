# Architecture — Shortlist

> **Template reference**: `.ai-framework/templates/architecture.md`
> Small by design: one service, one store, no external dependencies.

---

## 1. System Overview

A single ASP.NET Core Minimal API process. All state lives in one thread-safe in-memory store behind an interface. No database, queue, or external service.

```
curl / scripts ──HTTP──> Shortlist.Api (Kestrel)
                          ├── Endpoints/   (link management + redirect)
                          └── Store/       (ILinkStore -> InMemoryLinkStore singleton)
```

## 2. Components

| Component | Responsibility |
|-----------|----------------|
| `Shortlist.Api` | The whole service: endpoint mapping, request validation, DTO mapping, DI wiring |
| `Shortlist.Api/Store` | `ILinkStore` contract + `InMemoryLinkStore` (ConcurrentDictionary keyed by code); owns code generation and click counting |
| `Shortlist.Api/Models` | `Link` record + request/response DTOs |
| `Tests/Shortlist.Api.Tests` | xUnit: WebApplicationFactory integration tests + store/codegen unit tests |

## 3. Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage | In-memory singleton store | v1 scope lock — validates API shape with zero infra |
| State access | Everything behind `ILinkStore` | Single seam for the v2 persistence swap; testable |
| Short codes | 6-char base62, generated server-side; custom codes 4–32 chars `[A-Za-z0-9_-]` | Collision-safe at team scale; predictable validation |
| Concurrency | `ConcurrentDictionary` + atomic click increments | Correct under parallel redirects without locks in endpoints |
| Errors | Problem Details for every non-2xx | One error shape; matches ASP.NET Core defaults |
| Responses | Plain JSON DTOs, no envelope | Small API; envelope adds nothing at this scale |
| Auth | None in v1 | Trusted network (stakeholder scope decision) |

## 4. Request Flows

- **Create:** `POST /api/links` → validate URL + optional custom code → store assigns/validates code → 201 + `LinkResponse` (409 if custom code taken)
- **Redirect:** `GET /{code}` → store lookup → 302 `Location` + atomic click increment, or 404 problem
- **Manage:** `GET /api/links` (list), `GET /api/links/{code}` (detail + stats), `DELETE /api/links/{code}` (204)

## 5. Solution Structure

```
Shortlist.slnx
├── Shortlist.Api/            # net10.0, nullable, warnings-as-errors
└── Tests/Shortlist.Api.Tests/
```

Route note: the redirect route `/{code}` is constrained so it never shadows `/api/*` paths.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-08-03 | Initial architecture for v1 scope. |

> **Last verified against code:** 2026-08-03 (pre-implementation — describes the intended skeleton)
