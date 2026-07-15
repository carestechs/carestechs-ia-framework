<!-- Copy this file to docs/ui-specification/screens/<screen-kebab>.md (e.g., "Project Board" → project-board.md) — one screen per file. -->
<!-- Frontmatter: flat keys only — values are scalars or inline [a, b, c] arrays (no nesting, no multiline values); `screen` MUST equal the filename. -->

---
kind: screen
screen: [screen-name]               # kebab-case; MUST equal the filename
route: [/path]
endpoints: [resource-a, resource-b] # resource shard names this screen calls (may be [])
---

# Screen: [Screen Name]

> **Last verified against code:** <!-- YYYY-MM-DD (commit abc1234) — update whenever you confirm this file matches the code -->

**Route**: <!-- TODO: /path -->
**Auth**: <!-- Required / Public -->
**Layout**: <!-- App shell / Public — see index.md Section 4 -->

## Layout Sketch

```
<!-- TODO: ASCII diagram or description of the screen layout -->
```

## Component Hierarchy

```
[ScreenName]Page
├── [ComponentA]
│   └── [SubComponent]
└── [ComponentB]
```

## Component → API Mapping

<!-- Endpoints referenced here live in docs/api-spec/endpoints/<resource>.md -->

| Component | Data Needed | API Endpoint | Trigger |
|-----------|-------------|-------------|---------|
| <!-- Component --> | <!-- Data --> | <!-- GET /api/... --> | <!-- On page load --> |

## States

<!-- Use the standard patterns from index.md Section 2.5 — do not invent new loading/error UIs -->

| State | Condition | UI Behavior |
|-------|-----------|-------------|
| **Default** | Data loaded | Show content |
| **Loading** | API in flight | Show spinner/skeleton |
| **Empty** | No items | Show message + CTA |
| **Error** | API failed | Show error + retry |

## User Interactions

| Action | UI Element | Result | API Call |
|--------|-----------|--------|----------|
| <!-- Click create --> | <!-- Button --> | <!-- Open dialog --> | <!-- None until submit --> |
