# Persona: Team Developer — "Rafa"

> **Template reference**: `.ai-framework/templates/persona.md`

## Profile

Backend developer on a 6-person product team. Lives in the terminal and team chat. Shares links to dashboards, PRs, and docs many times a day; long URLs get mangled in chat and are impossible to dictate or remember.

## Goals

- Turn a long URL into a short, speakable code in one command
- Choose a memorable custom code for links that get shared repeatedly (`/deploy-docs`)
- See whether a shared link actually got clicked

## Frustrations

- Public shorteners are blocked by company policy and leak internal URLs
- Standing up "a real service with a database" for something this small is overkill

## Behavior & Expectations

- Interacts via curl and scripts — cares about clean status codes and predictable JSON, not UI
- Expects mistakes (bad URL, taken code) to come back as clear 4xx errors, instantly
- Tolerates losing links on service restart in v1 — recreating them is cheap; simplicity wins
