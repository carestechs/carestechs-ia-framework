# System Architecture — TaskFlow

> **Last verified against code:** 2026-07-16 (commit `fixture5`)

> *Subset of the framework architecture template — strategy-stage fixture; sections not needed here are omitted.*

## 1. Overview

### 1.1 System Summary

TaskFlow is a **modular monolith**: one Express process serving a REST API, one React SPA consuming it, one PostgreSQL database behind it. V1 defines a **single module, `Core`** — it owns every entity, every route, and every screen. Module boundaries beyond Core are deferred until the domain demands them.

### 1.2 Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture style | Modular monolith with a single `Core` module | One team, one deployable; boundaries can split later |
| Backend | Node.js + Express 4 (TypeScript strict) | Team fluency; minimal framework surface |
| Frontend | React 18 SPA (Vite, TanStack Query) | Server state stays server-owned |
| Database | PostgreSQL 16 via `pg`, plain SQL (no ORM) | Explicit data contract; SQL is reviewable |
| Auth | External auth service issuing JWTs; app stores only opaque user UUIDs | No local credential or user-profile storage |

---

## 2. Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| API | Express 4 on Node.js | REST endpoints under `/api/v1` |
| SPA | React 18 + Vite + TanStack Query | Project, task, and feed views |
| Data | PostgreSQL 16 (`pg` driver, SQL migrations in `migrations/`) | System of record |
| Validation | Zod at the route boundary | Reject bad input before it reaches the service layer |
| Testing | Vitest + Supertest | Unit and API integration tests |

---

## 3. Module Architecture

| Module | Owns | Notes |
|--------|------|-------|
| Core | All V1 entities, all API routes, all screens | The **only** module in V1 — every entity's owning module is `Core` |

There are no cross-module references in V1: with a single module, every reference is same-module. Adding a second module requires an architecture change first.

---

## 4. API Contract (callout)

> **Contract:** every success response is `{ "data": ... }` (lists add `"meta"`); every error is `{ "error": { "code", "message", "fields?" } }` with a stable code; all routes live under `/api/v1` behind JWT bearer auth. Generated specs (data model, API spec) must not contradict this contract.

---

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| 2026-07-16 | TaskFlow team | Initial architecture (single Core module) | V1 baseline |
