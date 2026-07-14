# API Specification

## 1. Overview

### 1.1 API Summary

<!-- TODO: Describe the API surface — how many modules expose endpoints, the auth model, and the response format -->

### 1.2 Key API Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| <!-- e.g., Base path --> | <!-- e.g., `/api/` --> | <!-- e.g., Standard convention --> |
| <!-- e.g., Versioning strategy --> | <!-- e.g., URL prefix `/api/v1/` --> | <!-- e.g., Explicit, cache-friendly --> |
| <!-- e.g., Auth mechanism --> | <!-- e.g., JWT Bearer tokens --> | <!-- e.g., Stateless, scalable --> |
| <!-- e.g., Response envelope --> | <!-- e.g., `{ data, meta }` --> | <!-- e.g., Consistent response shape --> |
| <!-- e.g., Error format --> | <!-- e.g., RFC 7807 --> | <!-- e.g., Standard problem details --> |
| <!-- e.g., Pagination style --> | <!-- e.g., Offset with `page` + `pageSize` --> | <!-- e.g., Simple, widely understood --> |

## 2. Common Conventions

### 2.1 Response Envelope

```json
{
  "data": { },
  "meta": {
    "totalCount": 0,
    "page": 1,
    "pageSize": 20
  }
}
```

<!-- TODO: Adjust to match your project's response format -->

### 2.2 Error Response (RFC 7807)

```json
{
  "type": "https://tools.ietf.org/html/rfc7807",
  "title": "[Error Title]",
  "status": 400,
  "detail": "[Human-readable explanation]",
  "errors": {
    "[field]": ["[Validation message]"]
  }
}
```

### 2.3 Authentication

- **Mechanism**: <!-- e.g., JWT Bearer token in `Authorization` header -->
- **Token format**: `Authorization: Bearer <token>`

### 2.4 Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number (1-based) |
| pageSize | int | 20 | Items per page (max 100) |

### 2.5 Error Catalog

<!-- TODO: Enumerate the stable error identifiers clients can rely on — the RFC 7807 `type` values or error codes. Endpoints reference these instead of inventing ad-hoc errors. -->

| Error Code / `type` | HTTP Status | When Used | Notes |
|---------------------|-------------|-----------|-------|
| <!-- e.g., validation-error --> | <!-- e.g., 400 --> | <!-- e.g., Request fails validation --> | <!-- e.g., `errors` lists per-field messages --> |
| <!-- e.g., not-found --> | <!-- e.g., 404 --> | <!-- e.g., Resource does not exist --> | <!-- --> |

### 2.6 Authentication Endpoints

<!-- TODO: Model auth endpoints (login, refresh, logout) as full endpoint blocks in Section 3 — don't leave auth as prose-only. Mark which are public vs authenticated in the Auth attribute, and reference Error Catalog entries for failed auth. -->

## 3. Endpoints by Module

<!-- TODO: Define endpoints for each module. See .ai-framework/templates/api-spec.md for the full template. -->

### 3.1 [Module Name]

#### [Resource Name]

##### [METHOD] [/api/path]

> *[One-sentence description]*

| Attribute | Value |
|-----------|-------|
| **Auth** | <!-- Required / Public --> |
| **Roles** | <!-- Any / Admin / Owner --> |

**Request Body:**

```json
{
  "[field]": "[type — description]"
}
```

**Response (200 OK):**

```json
{
  "data": {
    "[field]": "[type]"
  }
}
```

**Status Codes:**

| Code | Condition |
|------|-----------|
| 200 | Success |
| 400 | Validation error |
| 401 | Unauthorized |
| 404 | Not found |

---

<!-- TODO: Repeat endpoint blocks for each endpoint, module sections (3.2, 3.3, ...) for each module -->

## 4. Shared DTOs

<!-- TODO: Define DTOs used across modules -->

### 4.1 [DTOName]

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| <!-- field --> | <!-- type --> | <!-- Yes/No --> | <!-- description --> |

## 5. Endpoint Summary

| Method | Path | Module | Auth | Description |
|--------|------|--------|------|-------------|
| <!-- GET --> | <!-- /api/resources --> | <!-- Module --> | <!-- Required --> | <!-- List resources --> |
| <!-- POST --> | <!-- /api/resources --> | <!-- Module --> | <!-- Required --> | <!-- Create resource --> |

## Usage Notes for AI Task Generation

- **Controller structure**: Each module section maps to a controller
- **DTO generation**: Request and response shapes map to DTO classes
- **Status codes**: Every endpoint must handle all listed status codes
- **Auth requirements**: Respect the auth/roles column
- **Response envelope**: All responses must use the shared envelope format
- **Pagination**: List endpoints must support pagination parameters
- **Error catalog discipline**: Error responses must use identifiers from the Error Catalog (Section 2.5) — add a catalog row before introducing a new error condition

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| YYYY-MM-DD | [name] | Initial version | — |
