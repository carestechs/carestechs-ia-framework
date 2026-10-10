# Stakeholder Definition — Shortlist

> **Template reference**: `.ai-framework/templates/stakeholder-definition.md`
> Deliberately compact: Shortlist is a small internal tool; this document is the scope authority.

---

## 1. Product Vision

A self-hosted URL shortener for small dev teams: paste a long URL, get a short code on the team's own domain, share it in chat/docs, and see how often it gets clicked. Runs as a single lightweight service with zero external dependencies.

## 2. Users

One persona: the **team developer** (see `docs/personas/primary-user.md`). No admin/visitor distinction in v1 — the service runs inside the team network and everyone with network access is trusted equally.

## 3. Scope

### 3.1 In Scope (v1)

- Create a short link from a valid absolute HTTP/HTTPS URL, with an optional caller-chosen custom code
- Redirect `GET /{code}` to the original URL, counting each click
- List all links; fetch one link's details and click stats; delete a link
- Automated test suite covering every endpoint's status-code contract

### 3.2 What We Intentionally Avoid in v1

- **Persistence** — links live in process memory and are lost on restart. Accepted: v1 validates the API shape; durability is a v2 decision (BUG/IMP work items will drive it)
- **Authentication/authorization** — trusted-network deployment; adding auth now would double the surface for no experimental value
- **UI** — API-only; consumers are curl, chat integrations, and scripts
- **Link expiry, QR codes, bulk import, analytics dashboards** — classic scope creep for shorteners; explicitly out

**Scope Lock (v1):** the four capability bullets in 3.1 are the complete v1 feature set. Anything else is a new work item, not an extension of FEAT-001.

## 4. Success Metrics

- A developer can create and use a working short link with two curl commands in under a minute
- `dotnet test` green proves every documented status-code contract
- Zero production NuGet dependencies (BCL + ASP.NET Core only)

## 5. Constraints

- .NET 10 Minimal API, single API project + single test project (see `docs/ARCHITECTURE.md`)
- No database, no external services, no configuration beyond the listen port
- Runs on Windows/Linux dev machines with only the .NET SDK installed

## 6. Release Model

Versioned: v1 is the scope-locked release above. Post-v1 work (persistence, auth) enters as new work items after a release transition.
