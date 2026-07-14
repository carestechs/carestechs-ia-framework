<!-- Copy this file to docs/api-spec/endpoints/<resource>.md — kebab-case, plural, matching the route segment (e.g., /api/task-labels → task-labels.md); one resource group per file, containing ALL endpoint blocks for that resource. -->

# Resource: [Resource Name] (`/api/[resource]`)

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

> *Module: [Owning Module] — <!-- TODO: One-sentence description of this resource group -->. Conventions (envelope, errors, auth, pagination): see `docs/api-spec/index.md`.*

## [METHOD] [/api/path]

> *<!-- TODO: One-sentence description of what this endpoint does -->*

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
| 400 | Validation error — see Error Catalog (`index.md` Section 2.5) |
| 401 | Unauthorized |
| 404 | Not found |

---

<!-- TODO: Repeat one ## endpoint block per endpoint in this resource group. Add each endpoint to the Endpoint Summary in index.md. -->
