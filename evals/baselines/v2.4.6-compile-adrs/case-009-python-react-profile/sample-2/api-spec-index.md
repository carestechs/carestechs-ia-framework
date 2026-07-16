<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->

# API Specification — <!-- TODO: [Product Name] -->

> **Last verified against code:** <!-- TODO: YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

---

## 1. Overview

### 1.1 API Summary

<!-- TODO: One paragraph describing the API surface — how many modules expose endpoints, the authentication model, and the general response format. -->

### 1.2 Key API Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Response envelope | Standard `{ data, meta }` envelope for all API responses | A uniform envelope means the frontend always knows where to find the payload and metadata <!-- from: adrs/api/rest-envelope.md --> |
| Auth mechanism | JWT Bearer tokens via the Authorization header; short-lived access tokens + long-lived rotated refresh tokens | JWT Bearer tokens are stateless and allow the API to validate requests without a session store <!-- from: adrs/api/jwt-bearer-auth.md --> |
| Pagination style | Offset-based with `page` and `pageSize` query parameters; sorting via `sortBy` and `sortDir` | Simple to implement and understand; integrates naturally with SQL OFFSET/LIMIT <!-- from: adrs/api/offset-pagination.md --> |

<!-- TODO: add project-specific decisions as rows (base path, versioning strategy, error format) — not defined by the selected ADRs. -->

---

## 2. Common Conventions

### 2.1 Response Envelope

- Single item responses: `{ "data": { ... } }` <!-- from: adrs/api/rest-envelope.md -->
- List responses: `{ "data": [ ... ], "meta": { "totalCount": N, "page": N, "pageSize": N } }` <!-- from: adrs/api/rest-envelope.md --> <!-- from: adrs/api/offset-pagination.md -->
- Never return a raw array or raw object at the top level <!-- from: adrs/api/rest-envelope.md -->
- Create generic response wrapper classes: `ApiResponse<T>` for single items, `ApiListResponse<T>` for lists <!-- from: adrs/api/rest-envelope.md -->
- Controllers must always wrap return values in the envelope <!-- from: adrs/api/rest-envelope.md -->

### 2.2 Error Response

- Error responses follow a separate error envelope, not covered by the envelope ADR <!-- from: adrs/api/rest-envelope.md -->

<!-- TODO: document the error response format — no selected ADR defines it. -->

### 2.3 Authentication

- Mechanism: JWT Bearer tokens sent in the `Authorization: Bearer <token>` header on every authenticated request <!-- from: adrs/api/jwt-bearer-auth.md -->
- Access tokens contain claims: user ID (`sub`), role(s), issued-at, expiration <!-- from: adrs/api/jwt-bearer-auth.md -->
- Access token lifetime: 15-60 minutes (configurable) <!-- from: adrs/api/jwt-bearer-auth.md -->
- Refresh tokens are long-lived, stored securely (httpOnly cookie or secure storage), and rotated on every use <!-- from: adrs/api/jwt-bearer-auth.md -->
- Token validation must check signature, expiration, issuer, and audience <!-- from: adrs/api/jwt-bearer-auth.md -->
- Never store JWTs in localStorage — use httpOnly cookies or in-memory storage on the frontend <!-- from: adrs/api/jwt-bearer-auth.md -->
- Protect endpoints with `[Authorize]`; role-based access with `[Authorize(Roles = "...")]` <!-- from: adrs/api/jwt-bearer-auth.md -->

<!-- TODO: list any unauthenticated/public endpoints. -->

### 2.4 Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | — | 1-based page number (first page is `page=1`) <!-- from: adrs/api/offset-pagination.md --> |
| `pageSize` | int | 20 | Items per page; maximum is 100 — requests exceeding it are rejected with a 400 error <!-- from: adrs/api/offset-pagination.md --> |
| `sortBy` | string | — | Column to sort by; validated against an allowlist of sortable columns — never passed raw to ORDER BY <!-- from: adrs/api/offset-pagination.md --> |
| `sortDir` | string | `asc` | Sort direction: `asc` or `desc` <!-- from: adrs/api/offset-pagination.md --> |

- Response `meta` must include: `totalCount`, `page`, `pageSize` <!-- from: adrs/api/offset-pagination.md --> <!-- from: adrs/api/rest-envelope.md -->
- A shared `PaginationParams` class binds the query parameters <!-- from: adrs/api/offset-pagination.md -->
- Use `.Skip((page - 1) * pageSize).Take(pageSize)` for EF Core queries <!-- from: adrs/api/offset-pagination.md -->

### 2.5 Error Catalog

<!-- TODO: stable, machine-readable error identifiers — no selected ADR defines them. -->

### 2.6 Authentication Endpoints

<!-- TODO: auth endpoint blocks (login, refresh, logout) belong in their own resource shard (docs/api-spec/endpoints/auth.md) — project-specific. -->

---

## 3. Shared DTOs

<!-- TODO: DTOs referenced by multiple resources or modules. -->

---

## 4. Endpoint Summary

<!-- TODO: quick-reference table of ALL endpoints across all shards — project-specific. -->

---

## Usage Notes for AI Task Generation

<!-- TODO: static template content — copy verbatim from the api-spec.md template. -->

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| <!-- TODO: YYYY-MM-DD --> | <!-- TODO: name --> | Initial version (compiled from ADRs) | — |
