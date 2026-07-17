# Implementation Diff Under Review — T-002 Label CRUD Endpoints

`git diff main..feat/FEAT-001-T-002-labels` — the complete change set the implementation session produced for T-002. The branch base already contains T-001's deliverables (migration `002-labels.sql`, `src/db/label.ts`, the label entity shards).

```diff
diff --git a/docs/api-spec/endpoints/labels.md b/docs/api-spec/endpoints/labels.md
new file mode 100644
index 0000000..48125b0
--- /dev/null
+++ b/docs/api-spec/endpoints/labels.md
@@ -0,0 +1,65 @@
+---
+kind: resource
+resource: labels
+routes: [/api/v1/projects/{projectId}/labels, /api/v1/labels/{id}, /api/v1/labels/export]
+entities: [label, project]
+---
+
+# Resource: Labels (`/api/v1/projects/{projectId}/labels`, `/api/v1/labels/{id}`)
+
+> **Last verified against code:** 2026-07-15 (commit `t002impl`)
+
+> *Module: Projects — project-scoped label management. Router: `src/api/labels.ts`; repository: `src/db/label.ts`. Conventions (envelope, errors, auth, pagination): see `docs/api-spec/index.md`.*
+
+## LabelDto
+
+| Field | Type | Nullable | Description |
+|-------|------|----------|-------------|
+| id | string (UUID) | No | Label id |
+| projectId | string (UUID) | No | Owning project |
+| name | string | No | 1–30 chars, whitespace-normalized |
+| color | string | No | One of the 12 palette tokens |
+
+## GET /api/v1/projects/{projectId}/labels
+
+> *List the project's labels, ordered by name. Supports `page`/`pageSize` per index Section 2.4.*
+
+**Response (200 OK):** `{ "data": [LabelDto], "meta": { "totalCount", "page", "pageSize" } }`
+
+**Status Codes:** 200 · 400 `validation-error` · 401 `unauthorized` · 404 `not-found` (project)
+
+## POST /api/v1/projects/{projectId}/labels
+
+> *Create a label.*
+
+**Request Body:** `{ "name": "1-30 chars", "color": "palette token" }`
+
+**Response (201 Created):** `{ "data": LabelDto }`
+
+**Status Codes:** 201 · 400 `validation-error` · 401 `unauthorized` · 404 `not-found` (project)
+
+## PUT /api/v1/labels/{id}
+
+> *Replace a label's name and color — both fields required.*
+
+**Request Body:** `{ "name": "1-30 chars", "color": "palette token" }`
+
+**Response (200 OK):** `{ "data": LabelDto }`
+
+**Status Codes:** 200 · 400 `validation-error` · 401 `unauthorized` · 404 `not-found`
+
+## DELETE /api/v1/labels/{id}
+
+> *Delete a label; task assignments are removed by the schema's cascade.*
+
+**Response (200 OK):** `{ "data": LabelDto }` — the deleted label
+
+**Status Codes:** 200 · 401 `unauthorized` · 404 `not-found`
+
+## GET /api/v1/labels/export
+
+> *CSV dump of a project's labels (`?projectId=<uuid>`): header `id,name,color`, one row per label.*
+
+**Response (200 OK):** `text/csv`
+
+**Status Codes:** 200 · 400 `validation-error` · 401 `unauthorized`
diff --git a/src/api/index.ts b/src/api/index.ts
index a2a27a9..06a5357 100644
--- a/src/api/index.ts
+++ b/src/api/index.ts
@@ -1 +1,9 @@
-// fixture placeholder — real implementation not needed for eval path checks
+import { Router } from "express";
+
+import { labelsRouter } from "./labels";
+import { tasksRouter } from "./tasks";
+
+export const apiRouter = Router();
+
+apiRouter.use(tasksRouter);
+apiRouter.use(labelsRouter);
diff --git a/src/api/labels.ts b/src/api/labels.ts
new file mode 100644
index 0000000..7d606c0
--- /dev/null
+++ b/src/api/labels.ts
@@ -0,0 +1,93 @@
+import { Router, type Request, type Response } from "express";
+import { z } from "zod";
+
+import { ApiError } from "./errors";
+import * as labelRepo from "../db/label";
+
+export const labelsRouter = Router();
+
+const PALETTE = ["red", "orange", "amber", "yellow", "lime", "green", "teal", "cyan",
+  "blue", "indigo", "purple", "pink"] as const;
+
+const labelCreateSchema = z.object({ name: z.string().min(1).max(30), color: z.enum(PALETTE) });
+const labelReplaceSchema = z.object({ name: z.string().min(1).max(30), color: z.enum(PALETTE) });
+
+// Labels are stored trimmed, with inner whitespace collapsed.
+function normalizeLabelName(raw: string): string {
+  return raw.trim().replace(/\s+/g, " ");
+}
+
+function parsePositiveInt(value: unknown, fallback: number, max?: number): number {
+  const n = Number(value ?? fallback);
+  if (!Number.isInteger(n) || n < 1) {
+    throw new ApiError(400, "validation-error", "page and pageSize must be positive integers");
+  }
+  return max !== undefined ? Math.min(n, max) : n;
+}
+
+function parseBody<T>(schema: z.ZodType<T>, body: unknown): T {
+  const parsed = schema.safeParse(body);
+  if (!parsed.success) {
+    throw new ApiError(400, "validation-error", "request body failed validation",
+      parsed.error.flatten().fieldErrors);
+  }
+  return parsed.data;
+}
+
+const wrap = (fn: (req: Request, res: Response) => Promise<void>) =>
+  (req: Request, res: Response, next: (err: unknown) => void) =>
+    fn(req, res).catch(next);
+
+// GET /api/v1/projects/{projectId}/labels — list the project's labels
+labelsRouter.get("/projects/:projectId/labels", wrap(async (req, res) => {
+  const page = parsePositiveInt(req.query.page, 1);
+  const pageSize = parsePositiveInt(req.query.pageSize, 50, 100);
+  if (!(await labelRepo.projectExists(req.params.projectId))) {
+    throw new ApiError(404, "not-found", "project does not exist");
+  }
+  const { rows, totalCount } = await labelRepo.listByProject(req.params.projectId, page, pageSize);
+  res.json({ data: rows, meta: { totalCount, page, pageSize } });
+}));
+
+// POST /api/v1/projects/{projectId}/labels — create a label
+labelsRouter.post("/projects/:projectId/labels", wrap(async (req, res) => {
+  const body = parseBody(labelCreateSchema, req.body);
+  if (!(await labelRepo.projectExists(req.params.projectId))) {
+    throw new ApiError(404, "not-found", "project does not exist");
+  }
+  const label = await labelRepo.create(
+    req.params.projectId, normalizeLabelName(body.name), body.color);
+  res.status(201).json({ data: label });
+}));
+
+// PUT /api/v1/labels/{id} — replace a label's name and color
+labelsRouter.put("/labels/:id", wrap(async (req, res) => {
+  const body = parseBody(labelReplaceSchema, req.body);
+  const label = await labelRepo.replace(
+    req.params.id, normalizeLabelName(body.name), body.color);
+  if (!label) {
+    throw new ApiError(404, "not-found", "label does not exist");
+  }
+  res.json({ data: label });
+}));
+
+// DELETE /api/v1/labels/{id} — delete a label (assignments cascade in the schema)
+labelsRouter.delete("/labels/:id", wrap(async (req, res) => {
+  const label = await labelRepo.remove(req.params.id);
+  if (!label) {
+    throw new ApiError(404, "not-found", "label does not exist");
+  }
+  res.json({ data: label });
+}));
+
+// GET /api/v1/labels/export — CSV dump of a project's labels for spreadsheets
+labelsRouter.get("/labels/export", wrap(async (req, res) => {
+  const projectId = String(req.query.projectId ?? "");
+  if (!projectId) {
+    throw new ApiError(400, "validation-error", "projectId query parameter is required");
+  }
+  const { rows } = await labelRepo.listByProject(projectId, 1, 1000);
+  const escape = (v: string) => (v.includes(",") ? `"${v.replace(/"/g, '""')}"` : v);
+  const csv = ["id,name,color", ...rows.map((l) => [l.id, escape(l.name), l.color].join(","))];
+  res.type("text/csv").send(csv.join("\n"));
+}));
diff --git a/tests/api/labels.test.ts b/tests/api/labels.test.ts
new file mode 100644
index 0000000..db8b840
--- /dev/null
+++ b/tests/api/labels.test.ts
@@ -0,0 +1,52 @@
+import { describe, expect, it } from "vitest";
+import request from "supertest";
+
+import { app } from "../helpers/app";
+import { seedLabel, seedProject } from "../helpers/seed";
+
+describe("labels API", () => {
+  it("lists a project's labels with the list envelope", async () => {
+    const project = await seedProject();
+    await seedLabel(project.id, { name: "bug", color: "red" });
+    const res = await request(app).get(`/api/v1/projects/${project.id}/labels`);
+    expect(res.status).toBe(200);
+    expect(res.body.meta).toMatchObject({ totalCount: 1, page: 1, pageSize: 50 });
+    expect(res.body.data[0]).toMatchObject({ name: "bug", color: "red" });
+  });
+
+  it("creates a label and returns 201 with the single-item envelope", async () => {
+    const project = await seedProject();
+    const res = await request(app)
+      .post(`/api/v1/projects/${project.id}/labels`)
+      .send({ name: "  client  request ", color: "blue" });
+    expect(res.status).toBe(201);
+    expect(res.body.data).toMatchObject({ name: "client request", color: "blue" });
+  });
+
+  it("replaces a label name and color via PUT", async () => {
+    const project = await seedProject();
+    const label = await seedLabel(project.id, { name: "bug", color: "red" });
+    const res = await request(app)
+      .put(`/api/v1/labels/${label.id}`)
+      .send({ name: "defect", color: "orange" });
+    expect(res.status).toBe(200);
+    expect(res.body.data).toMatchObject({ name: "defect", color: "orange" });
+  });
+
+  it("deletes a label and returns the deleted row", async () => {
+    const project = await seedProject();
+    const label = await seedLabel(project.id, { name: "bug", color: "red" });
+    const res = await request(app).delete(`/api/v1/labels/${label.id}`);
+    expect(res.status).toBe(200);
+    expect(res.body.data.id).toBe(label.id);
+  });
+
+  it("exports a project's labels as CSV", async () => {
+    const project = await seedProject();
+    await seedLabel(project.id, { name: "bug", color: "red" });
+    const res = await request(app).get(`/api/v1/labels/export?projectId=${project.id}`);
+    expect(res.status).toBe(200);
+    expect(res.headers["content-type"]).toContain("text/csv");
+    expect(res.text.split("\n")[0]).toBe("id,name,color");
+  });
+});
```
