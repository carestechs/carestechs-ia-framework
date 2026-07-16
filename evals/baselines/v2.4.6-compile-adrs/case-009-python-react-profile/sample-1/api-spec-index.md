<!-- Step 0: 18 ADRs validated — no missing dependencies, no conflicts, all profile-Required ADRs selected -->

# API Specification — [Product Name] <!-- TODO: replace with the product name -->

> **Last verified against code:** <!-- TODO: YYYY-MM-DD (commit) — update whenever you confirm this file matches the code -->

---

## 1. Overview

### 1.1 API Summary

<!-- TODO: One paragraph describing the API surface, modules exposing endpoints, and general response format — project-specific content. -->

### 1.2 Key API Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Response envelope | Standard `{ data, meta }` envelope on all responses | A uniform envelope means the frontend always knows where to find the payload and metadata <!-- from: adrs/api/rest-envelope.md --> |
| Auth mechanism | JWT Bearer tokens — short-lived access tokens plus long-lived, rotated refresh tokens | Stateless tokens let the API validate requests without a session store <!-- from: adrs/api/jwt-bearer-auth.md --> |
| Pagination style | Offset-based with `page`/`pageSize` query parameters and `sortBy`/`sortDir` sorting | Simple to implement and understand; integrates naturally with SQL OFFSET/LIMIT <!-- from: adrs/api/offset-pagination.md --> |

<!-- TODO: Base path, versioning strategy, and error format decisions — project-specific content not covered by the compiled ADRs. -->

---

## 2. Common Conventions

### 2.1 Response Envelope

- Single item responses: `{ "data": { ... } }` <!-- from: adrs/api/rest-envelope.md -->
- List responses: `{ "data": [ ... ], "meta": { "totalCount": N, "page": N, "pageSize": N } }` <!-- from: adrs/api/rest-envelope.md --> <!-- from: adrs/api/offset-pagination.md -->
- Never return a raw array or raw object at the top level — controllers must always wrap return values in the envelope <!-- from: adrs/api/rest-envelope.md -->
- Generic response wrapper classes: `ApiResponse<T>` for single items, `ApiListResponse<T>` for lists <!-- from: adrs/api/rest-envelope.md -->

### 2.2 Error Response (RFC 7807)

- Error responses follow a separate error envelope, not the `{ data, meta }` success envelope <!-- from: adrs/api/rest-envelope.md -->

<!-- TODO: Define the error response format — project-specific content not covered by the compiled ADRs. -->

### 2.3 Authentication

- **Mechanism:** JWT Bearer tokens sent in the `Authorization: Bearer <token>` header on every authenticated request <!-- from: adrs/api/jwt-bearer-auth.md -->
- Access tokens contain claims: user ID (`sub`), role(s), issued-at, expiration; access token lifetime is 15-60 minutes (configurable) <!-- from: adrs/api/jwt-bearer-auth.md -->
- Refresh tokens are long-lived, stored securely (httpOnly cookie or secure storage), and rotated on every use <!-- from: adrs/api/jwt-bearer-auth.md -->
- Token validation must check signature, expiration, issuer, and audience <!-- from: adrs/api/jwt-bearer-auth.md -->
- Never store JWTs in localStorage — use httpOnly cookies or in-memory storage on the frontend <!-- from: adrs/api/jwt-bearer-auth.md -->
- Protect endpoints with the `[Authorize]` attribute; role-based access uses `[Authorize(Roles = "...")]` <!-- from: adrs/api/jwt-bearer-auth.md -->

<!-- TODO: List unauthenticated/public endpoints — project-specific content. -->

### 2.4 Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number, 1-based — the first page is `page=1` <!-- from: adrs/api/offset-pagination.md --> |
| `pageSize` | int | 20 | Items per page; maximum is 100 — requests exceeding it are rejected with a 400 error <!-- from: adrs/api/offset-pagination.md --> |
| `sortBy` | string | — | Column name to sort by; validated against an allowlist of sortable columns — raw user input is never passed to ORDER BY <!-- from: adrs/api/offset-pagination.md --> |
| `sortDir` | string | `asc` | Sort direction: `asc` or `desc` <!-- from: adrs/api/offset-pagination.md --> |

- Response `meta` must include `totalCount`, `page`, `pageSize` <!-- from: adrs/api/offset-pagination.md --> <!-- from: adrs/api/rest-envelope.md -->
- Query parameters bind via a shared `PaginationParams` class; queries use `.Skip((page - 1) * pageSize).Take(pageSize)` <!-- from: adrs/api/offset-pagination.md -->

### 2.5 Error Catalog

<!-- TODO: Stable error identifiers with HTTP statuses — project-specific content. -->

### 2.6 Authentication Endpoints

<!-- TODO: Auth endpoint blocks (login, refresh, logout) in their own resource shard — project-specific content. -->

---

## 3. Shared DTOs

<!-- TODO: DTOs referenced by multiple resources or modules — project-specific content. -->

---

## 4. Endpoint Summary

<!-- TODO: Quick-reference table of all endpoints across all shards — project-specific content. -->

---

## Usage Notes for AI Task Generation

<!-- TODO: Copy from the api-spec.md template — static framework content, not derived from ADRs. -->

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| <!-- TODO: YYYY-MM-DD --> | <!-- TODO: name --> | Initial version — API decisions and conventions compiled from api ADRs | — |
