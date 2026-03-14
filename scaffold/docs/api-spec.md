# API Specification

## Overview

<!-- TODO: Describe the API surface — how many modules expose endpoints, the auth model, and the response format -->

### Key API Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| <!-- e.g., Base path --> | <!-- e.g., `/api/` --> | <!-- e.g., Standard convention --> |
| <!-- e.g., Auth mechanism --> | <!-- e.g., JWT Bearer tokens --> | <!-- e.g., Stateless, scalable --> |
| <!-- e.g., Response envelope --> | <!-- e.g., `{ data, meta }` --> | <!-- e.g., Consistent response shape --> |
| <!-- e.g., Error format --> | <!-- e.g., RFC 7807 --> | <!-- e.g., Standard problem details --> |
| <!-- e.g., Pagination style --> | <!-- e.g., Offset with `page` + `pageSize` --> | <!-- e.g., Simple, widely understood --> |

## Common Conventions

### Response Envelope

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

### Error Response

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

### Authentication

- **Mechanism**: <!-- e.g., JWT Bearer token in `Authorization` header -->
- **Token format**: `Authorization: Bearer <token>`

### Pagination

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number (1-based) |
| pageSize | int | 20 | Items per page (max 100) |

## Endpoints by Module

<!-- TODO: Define endpoints for each module. See .ai-framework/templates/api-spec.md for the full template. -->

### [Module Name]

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

<!-- TODO: Repeat endpoint blocks for each endpoint, module sections for each module -->

## Shared DTOs

<!-- TODO: Define DTOs used across modules -->

### [DTOName]

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| <!-- field --> | <!-- type --> | <!-- Yes/No --> | <!-- description --> |

## Endpoint Summary

| Method | Path | Module | Auth | Description |
|--------|------|--------|------|-------------|
| <!-- GET --> | <!-- /api/resources --> | <!-- Module --> | <!-- Required --> | <!-- List resources --> |
| <!-- POST --> | <!-- /api/resources --> | <!-- Module --> | <!-- Required --> | <!-- Create resource --> |

## AI Task Generation Notes

- **Controller structure**: Each module section maps to a controller
- **DTO generation**: Request and response shapes map to DTO classes
- **Status codes**: Every endpoint must handle all listed status codes
- **Auth requirements**: Respect the auth/roles column
- **Response envelope**: All responses must use the shared envelope format
- **Pagination**: List endpoints must support pagination parameters
