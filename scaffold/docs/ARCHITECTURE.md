# Architecture

## System Summary

<!-- TODO: Describe the system in 2-3 sentences -->

### Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| <!-- e.g., Rendering strategy --> | <!-- e.g., SSR with Next.js --> | <!-- e.g., SEO requirements + fast initial load --> |
| <!-- e.g., Database --> | <!-- e.g., PostgreSQL --> | <!-- e.g., Relational data, strong consistency needs --> |
| <!-- e.g., Hosting --> | <!-- e.g., Vercel --> | <!-- e.g., Zero-config deploys, edge network --> |

## Technology Stack

<!-- TODO: List your chosen technologies -->

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | <!-- e.g., React, Next.js, Tailwind --> | <!-- e.g., UI rendering, styling --> |
| **Backend** | <!-- e.g., Node.js, Express --> | <!-- e.g., API layer, business logic --> |
| **Data** | <!-- e.g., PostgreSQL, Redis --> | <!-- e.g., Primary storage, caching --> |
| **Infrastructure** | <!-- e.g., Vercel, AWS S3 --> | <!-- e.g., Hosting, file storage --> |
| **Auth** | <!-- e.g., NextAuth, Clerk --> | <!-- e.g., User authentication --> |

## Component Architecture

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

### Component Descriptions

**[Component 1]**
- **Purpose:** <!-- What does it do? -->
- **Responsibilities:** <!-- What is it in charge of? -->
- **Key Dependencies:** <!-- What does it depend on? -->

**[Component 2]**
- **Purpose:** <!-- What does it do? -->
- **Responsibilities:** <!-- What is it in charge of? -->
- **Key Dependencies:** <!-- What does it depend on? -->

## Data Flow

<!-- TODO: Describe the primary data flow through your system -->

1. <!-- e.g., User submits form in browser -->
2. <!-- e.g., Frontend validates input and sends POST to /api/items -->
3. <!-- e.g., Backend validates, transforms, stores in database -->
4. <!-- e.g., Response returned to frontend, UI updates -->

## Integration Points

<!-- TODO: List any external services or APIs your system talks to -->

| Service | Purpose | Auth Method | Failure Strategy |
|---------|---------|-------------|------------------|
| <!-- e.g., Stripe --> | <!-- e.g., Payments --> | <!-- e.g., API key --> | <!-- e.g., Queue + retry --> |
| <!-- e.g., SendGrid --> | <!-- e.g., Email --> | <!-- e.g., API key --> | <!-- e.g., Queue + retry --> |

*If none yet, write "None planned for v1" and move on.*

## Security Architecture

<!-- TODO: Fill in what applies to your system -->

- **Authentication:** <!-- How do users prove who they are? -->
- **Authorization:** <!-- How do you control what users can do? -->
- **Data Protection:** <!-- How is sensitive data handled? Encryption at rest/transit? -->
- **API Security:** <!-- Rate limiting, input validation, CORS? -->

## AI Task Generation Notes

> These notes help AI assistants generate technically correct tasks.

- **Respect component boundaries.** Don't mix responsibilities across components.
- **Follow the defined data flow.** New features should fit the existing patterns.
- **Use only listed technologies** unless proposing a migration (which needs its own task).
- **Honor the security architecture.** Every new endpoint needs auth/authz consideration.
