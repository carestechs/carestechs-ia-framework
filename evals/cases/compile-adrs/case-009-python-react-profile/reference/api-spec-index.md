<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->
<!-- Compiled docs/api-spec/index.md sections — api-category ADRs of the python-react-modular-monolith-docker-compose
     profile, via prompts/compile-adrs.md (Rule 6). Paste into docs/api-spec/index.md and fill the TODO scaffolds. -->

## 1. Overview

### 1.1 API Summary

<!-- TODO: One paragraph describing the API surface — project-specific. -->

### 1.2 Key API Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Response envelope | Standard `{ data, meta }` envelope on all responses | Uniform envelope — the frontend always knows where to find the payload and metadata <!-- from: adrs/api/rest-envelope.md --> |
| Auth mechanism | JWT Bearer tokens via the `Authorization` header; short-lived access + rotated refresh tokens | Stateless token validation — no session store required per request <!-- from: adrs/api/jwt-bearer-auth.md --> |
| Pagination style | Offset-based with `page`/`pageSize` query parameters and `sortBy`/`sortDir` sorting | Simple to implement and understand; integrates naturally with SQL OFFSET/LIMIT <!-- from: adrs/api/offset-pagination.md --> |

---

## 2. Common Conventions

- Single-item responses: `{ "data": { ... } }` <!-- from: adrs/api/rest-envelope.md -->
- List responses: `{ "data": [ ... ], "meta": { "totalCount": N, "page": N, "pageSize": N } }` <!-- from: adrs/api/rest-envelope.md -->
- Responses are never a raw array or raw object at the top level — controllers always wrap return values in the envelope, via generic wrappers `ApiResponse<T>` (single item) and `ApiListResponse<T>` (list) <!-- from: adrs/api/rest-envelope.md -->
- Error responses follow a separate error envelope (not covered by the envelope ADR) <!-- from: adrs/api/rest-envelope.md -->
- Authentication: `Authorization: Bearer <token>` header on every authenticated request <!-- from: adrs/api/jwt-bearer-auth.md -->
- Access tokens carry `sub` (user ID), role(s), issued-at, and expiration claims; lifetime 15-60 minutes (configurable) <!-- from: adrs/api/jwt-bearer-auth.md -->
- Refresh tokens are long-lived, stored securely (httpOnly cookie or secure storage), and rotated on every use; JWTs are never stored in localStorage <!-- from: adrs/api/jwt-bearer-auth.md -->
- Token validation checks signature, expiration, issuer, and audience; endpoints protected with `[Authorize]` / `[Authorize(Roles = "...")]` <!-- from: adrs/api/jwt-bearer-auth.md -->
- Pagination: `page` is 1-based; `pageSize` defaults to 20, maximum 100 (requests above are rejected with a 400 error) <!-- from: adrs/api/offset-pagination.md -->
- List response `meta` includes `totalCount`, `page`, and `pageSize` <!-- from: adrs/api/offset-pagination.md --> <!-- from: adrs/api/rest-envelope.md -->
- Sorting: `sortBy` (column name) and `sortDir` (`asc` or `desc`, default `asc`); `sortBy` is validated against an allowlist — raw user input never reaches ORDER BY <!-- from: adrs/api/offset-pagination.md -->
- A shared `PaginationParams` class binds pagination query parameters; EF Core queries use `.Skip((page - 1) * pageSize).Take(pageSize)` <!-- from: adrs/api/offset-pagination.md -->

---

## 3. Shared DTOs

<!-- TODO: DTOs shared across resources/modules — project-specific. -->

---

## 4. Endpoint Summary

<!-- TODO: one row per endpoint across all resource shards — project-specific. -->

---

## Usage Notes for AI Task Generation

<!-- TODO: retain the template's usage notes when pasting into the real index — not filled by ADR compilation. -->

---

## Changelog

<!-- TODO: changelog table — maintained by the project. -->
