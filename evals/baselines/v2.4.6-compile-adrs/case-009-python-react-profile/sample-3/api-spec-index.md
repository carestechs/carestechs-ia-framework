<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->

# API Specification — <!-- TODO: [Product Name] -->

> **Last verified against code:** <!-- TODO: YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

---

## 1. Overview

### 1.1 API Summary

<!-- TODO: One paragraph describing the API surface — modules exposing endpoints, auth model, response format. -->

### 1.2 Key API Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Response envelope | Standard `{ data, meta }` envelope for all responses | Uniform envelope — the frontend always knows where to find the payload and metadata <!-- from: adrs/api/rest-envelope.md --> |
| Auth mechanism | JWT Bearer tokens via the Authorization header; short-lived access tokens, rotated refresh tokens | Stateless — the API validates requests without a session store <!-- from: adrs/api/jwt-bearer-auth.md --> |
| Pagination style | Offset-based with `page` and `pageSize`; sorting via `sortBy` and `sortDir` | Simple to implement and understand; integrates naturally with SQL OFFSET/LIMIT <!-- from: adrs/api/offset-pagination.md --> |

---

## 2. Common Conventions

### 2.1 Response Envelope

- Single item responses: `{ "data": { ... } }` <!-- from: adrs/api/rest-envelope.md -->
- List responses: `{ "data": [ ... ], "meta": { "totalCount": N, "page": N, "pageSize": N } }` <!-- from: adrs/api/rest-envelope.md --> <!-- from: adrs/api/offset-pagination.md -->
- Never return a raw array or raw object at the top level <!-- from: adrs/api/rest-envelope.md -->
- Generic response wrapper classes: `ApiResponse<T>` for single items, `ApiListResponse<T>` for lists; controllers must always wrap return values in the envelope <!-- from: adrs/api/rest-envelope.md -->

### 2.2 Error Response

- Error responses follow a separate error envelope, not covered by the compiled ADRs <!-- from: adrs/api/rest-envelope.md -->

<!-- TODO: Project-specific — define the error response format (e.g., RFC 7807 Problem Details). -->

### 2.3 Authentication

- **Mechanism**: JWT Bearer tokens sent in `Authorization: Bearer <token>` header on every authenticated request <!-- from: adrs/api/jwt-bearer-auth.md -->
- Access tokens contain claims: user ID (`sub`), role(s), issued-at, expiration <!-- from: adrs/api/jwt-bearer-auth.md -->
- Access token lifetime: 15–60 minutes (configurable) <!-- from: adrs/api/jwt-bearer-auth.md -->
- Refresh tokens are long-lived, stored securely (httpOnly cookie or secure storage), and rotated on every use <!-- from: adrs/api/jwt-bearer-auth.md -->
- Token validation must check signature, expiration, issuer, and audience <!-- from: adrs/api/jwt-bearer-auth.md -->
- Never store JWTs in localStorage — use httpOnly cookies or in-memory storage on the frontend <!-- from: adrs/api/jwt-bearer-auth.md -->
- Protect endpoints with the `[Authorize]` attribute; role-based access with `[Authorize(Roles = "...")]` <!-- from: adrs/api/jwt-bearer-auth.md -->
- **Unauthenticated endpoints**: <!-- TODO: Project-specific — list any public endpoints. -->

### 2.4 Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | — | 1-based page number (first page is `page=1`) <!-- from: adrs/api/offset-pagination.md --> |
| `pageSize` | int | 20 | Items per page; maximum 100 — requests exceeding it are rejected with a 400 error <!-- from: adrs/api/offset-pagination.md --> |
| `sortBy` | string | — | Column name to sort by; validated against an allowlist of sortable columns — never passed raw to ORDER BY <!-- from: adrs/api/offset-pagination.md --> |
| `sortDir` | string | `asc` | Sort direction: `asc` or `desc` <!-- from: adrs/api/offset-pagination.md --> |

- Response `meta` must include: `totalCount`, `page`, `pageSize` <!-- from: adrs/api/rest-envelope.md --> <!-- from: adrs/api/offset-pagination.md -->
- A shared `PaginationParams` class binds the query parameters <!-- from: adrs/api/offset-pagination.md -->
- Queries use `.Skip((page - 1) * pageSize).Take(pageSize)` <!-- from: adrs/api/offset-pagination.md -->

### 2.5 Error Catalog

<!-- TODO: Project-specific — enumerate stable, machine-readable error identifiers clients can rely on. -->

### 2.6 Authentication Endpoints

<!-- TODO: Project-specific — model login, token refresh, logout, and password reset as full endpoint blocks in docs/api-spec/endpoints/auth.md. -->

---

## 3. Shared DTOs

<!-- TODO: Project-specific — define DTOs referenced by multiple resources or modules. -->

---

## 4. Endpoint Summary

<!-- TODO: Project-specific — quick-reference table of all endpoints across all shards. -->

---

## Usage Notes for AI Task Generation

<!-- TODO: Framework boilerplate from the api-spec.md template — copy when assembling the project docs/api-spec/index.md. -->

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| <!-- TODO: YYYY-MM-DD --> | <!-- TODO: name --> | Initial version compiled from ADRs | — |
