# Architecture

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

> **Context budget note:** This document is loaded into AI context — keep it contract-style (tables, schemas, rules); move narrative and history to `docs/rationale/` and link it (rationale files are never loaded by default).

## 1. Overview

### 1.1 System Summary

<!-- TODO: Describe the system in 2-3 sentences -->

### 1.2 Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| <!-- e.g., Rendering strategy --> | <!-- e.g., SSR with Next.js --> | <!-- e.g., SEO requirements + fast initial load --> |
| <!-- e.g., Database --> | <!-- e.g., PostgreSQL --> | <!-- e.g., Relational data, strong consistency needs --> |
| <!-- e.g., Hosting --> | <!-- e.g., Vercel --> | <!-- e.g., Zero-config deploys, edge network --> |

## 2. Technology Stack

<!-- TODO: List your chosen technologies -->

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | <!-- e.g., React, Next.js, Tailwind --> | <!-- e.g., UI rendering, styling --> |
| **Backend** | <!-- e.g., Node.js, Express --> | <!-- e.g., API layer, business logic --> |
| **Data** | <!-- e.g., PostgreSQL, Redis --> | <!-- e.g., Primary storage, caching --> |
| **Infrastructure** | <!-- e.g., Vercel, AWS S3 --> | <!-- e.g., Hosting, file storage --> |
| **Auth** | <!-- e.g., NextAuth, Clerk --> | <!-- e.g., User authentication --> |

## 3. Component Architecture

### 3.1 High-Level Component Diagram

<!-- TODO: Replace with your actual components -->

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│   Database   │
│              │     │   API        │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
                           │
                           ▼
                     ┌──────────────┐
                     │  External    │
                     │  Services    │
                     └──────────────┘
```

### 3.2 Component Descriptions

**[Component 1]**
- **Purpose:** <!-- What does it do? -->
- **Responsibilities:** <!-- What is it in charge of? -->
- **Key Dependencies:** <!-- What does it depend on? -->

**[Component 2]**
- **Purpose:** <!-- What does it do? -->
- **Responsibilities:** <!-- What is it in charge of? -->
- **Key Dependencies:** <!-- What does it depend on? -->

## 4. Data Flow

<!-- TODO: Describe the primary data flow through your system -->

1. <!-- e.g., User submits form in browser -->
2. <!-- e.g., Frontend validates input and sends POST to /api/items -->
3. <!-- e.g., Backend validates, transforms, stores in database -->
4. <!-- e.g., Response returned to frontend, UI updates -->

## 5. Integration Points

### 5.1 External Services

<!-- TODO: List any external services or APIs your system talks to -->

| Service | Purpose | Auth Method | Failure Strategy |
|---------|---------|-------------|------------------|
| <!-- e.g., Stripe --> | <!-- e.g., Payments --> | <!-- e.g., API key --> | <!-- e.g., Queue + retry --> |
| <!-- e.g., SendGrid --> | <!-- e.g., Email --> | <!-- e.g., API key --> | <!-- e.g., Queue + retry --> |

*If none yet, write "None planned for v1" and move on.*

### 5.2 Internal Communication

<!-- TODO: How do your own components talk to each other? For a single-process app, write "In-process calls only" and move on. -->

| From | To | Protocol | Pattern |
|------|-----|----------|---------|
| <!-- e.g., API --> | <!-- e.g., Worker --> | <!-- e.g., Queue --> | <!-- e.g., Async --> |

## 6. Security & Observability

### 6.1 Authentication

- <!-- How do users prove who they are? -->

### 6.2 Authorization

- <!-- How do you control what users can do? -->

### 6.3 Data Protection

- <!-- How is sensitive data handled? Encryption at rest/transit? -->
- **API Security:** <!-- Rate limiting, input validation, CORS? -->

### 6.4 Observability

<!-- TODO: How is the running system watched? One row per concern is enough. -->

| Concern | Tooling / Approach | Key Conventions |
|---------|-------------------|-----------------|
| Logging | <!-- e.g., Structured JSON logs --> | <!-- e.g., No PII in logs; include request ID --> |
| Metrics | <!-- e.g., Prometheus + Grafana --> | <!-- e.g., RED metrics per endpoint --> |
| Tracing | <!-- e.g., OpenTelemetry --> | <!-- e.g., Propagate trace ID --> |
| Alerting | <!-- e.g., PagerDuty on error-rate threshold --> | <!-- e.g., Alert on symptoms, not causes --> |

## 7. Scalability Considerations

<!-- TODO: Rough expected load and the scaling approach. For an early-stage product, honest small numbers beat aspirational ones. -->

- **Expected load:** <!-- e.g., ~50 concurrent users, <10 req/s, <1 GB data in year 1 -->
- **Scaling strategy:** <!-- e.g., Single instance until X; then horizontal on the API, read replica on the DB -->

## 8. Development & Deployment

### 8.1 Repository Structure

<!-- TODO: Top-level layout — where frontend, backend, shared code, and infrastructure live. -->

### 8.2 Environment Strategy

| Environment | Purpose | Data | Access |
|-------------|---------|------|--------|
| <!-- e.g., dev --> | <!-- Local development --> | <!-- Seeded/fake --> | <!-- All devs --> |
| <!-- e.g., production --> | <!-- Live traffic --> | <!-- Real --> | <!-- Restricted --> |

## Usage Notes for AI Task Generation

> These notes help AI assistants generate technically correct tasks.

- **Respect component boundaries.** Don't mix responsibilities across components.
- **Follow the defined data flow.** New features should fit the existing patterns.
- **Use only listed technologies** unless proposing a migration (which needs its own task).
- **Honor the security architecture.** Every new endpoint needs auth/authz consideration.
- **Follow the Failure Strategy** declared in Section 5.1 for every external service call.

## Changelog

| Date | Author | Change Description | Reason |
|------|--------|-------------------|--------|
| YYYY-MM-DD | [name] | Initial version | — |
