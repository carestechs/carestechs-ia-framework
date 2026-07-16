<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>T-031 Project Board Mockup — TaskFlow</title>

  <!-- All styles embedded — fully self-contained, no external requests, no JavaScript. -->
  <style>
    /* ==================================================================
       Design tokens — docs/ui-specification/index.md Section 2, verbatim.
       ================================================================== */
    :root {
      /* 2.1 Brand Colors */
      --color-primary: #2563EB;        /* Primary actions, active states, links */
      --color-primary-dark: #1D4ED8;   /* Hover/pressed states */
      --color-neutral-50: #F8FAFC;     /* App background */
      --color-neutral-100: #F1F5F9;    /* Card, column, and drawer backgrounds */
      --color-neutral-300: #CBD5E1;    /* Dividers, borders */
      --color-neutral-700: #334155;    /* Secondary text */
      --color-neutral-900: #0F172A;    /* Primary text */
      --color-success: #16A34A;        /* Success toasts */
      --color-warning: #D97706;        /* Overdue due-date chips */
      --color-error: #DC2626;          /* Error states, destructive actions */

      /* 2.2 Typography Scale — system font stack (the Design System declares no fonts) */
      --font-sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      --text-h1: 1.5rem;      --weight-h1: 600;   /* Screen titles */
      --text-h2: 1.125rem;    --weight-h2: 600;   /* Column headers, panel sections */
      --text-body: 0.875rem;  --weight-body: 400; /* Card titles, form fields, comments */
      --text-caption: 0.75rem; --weight-caption: 400; /* Timestamps, metadata, badges */

      /* 2.3 Spacing Scale — base unit 4px */
      --space-1: 4px;   /* Tight internal padding (badges, chips) */
      --space-2: 8px;   /* Standard internal padding */
      --space-3: 12px;  /* Gaps between cards and rows */
      --space-4: 16px;  /* Column, panel, and form padding */
      --space-6: 24px;  /* Page-level padding */
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--color-neutral-50);
      color: var(--color-neutral-900);
      font-family: var(--font-sans);
      font-size: var(--text-body);
      font-weight: var(--weight-body);
      line-height: 1.4;
    }

    button { font: inherit; cursor: default; } /* static mockup — buttons are affordances only */
    a { color: var(--color-primary); }

    .sr-only {
      position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
      overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0;
    }

    /* ---------- Reviewer header ---------- */
    .reviewer-header {
      padding: var(--space-4) var(--space-6);
      background: var(--color-neutral-100);
      border-bottom: 1px solid var(--color-neutral-300);
    }
    .reviewer-header h1 { margin: 0; font-size: var(--text-h1); font-weight: var(--weight-h1); }
    .reviewer-header h1 span { font-size: var(--text-body); font-weight: var(--weight-body); color: var(--color-neutral-700); }
    .reviewer-header p { margin: var(--space-1) 0 0; font-size: var(--text-caption); font-weight: var(--weight-caption); color: var(--color-neutral-700); }

    /* ---------- States grid: side-by-side, stacks on small screens ---------- */
    .states-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(620px, 100%), 1fr));
      gap: var(--space-6);
      padding: var(--space-6);
    }
    .state h2 { margin: 0; font-size: var(--text-h2); font-weight: var(--weight-h2); }
    .state-note { margin: var(--space-1) 0 var(--space-2); font-size: var(--text-caption); font-weight: var(--weight-caption); color: var(--color-neutral-700); }
    .frame {
      border: 1px solid var(--color-neutral-300);
      border-radius: var(--space-1);
      background: var(--color-neutral-50);
    }

    /* ---------- App shell (index.md Section 4.1 — 48px header, no sidebar) ---------- */
    .app-header {
      height: 48px;
      display: flex; align-items: center; gap: var(--space-2);
      padding: 0 var(--space-4);
      border-bottom: 1px solid var(--color-neutral-300);
    }
    .logo { width: var(--space-4); height: var(--space-4); color: var(--color-primary); flex: none; }
    .app-name { font-weight: var(--weight-h2); }
    .app-sep { color: var(--color-neutral-300); }
    .app-project { color: var(--color-neutral-700); }
    .app-spacer, .toolbar-spacer, .meta-spacer { flex: 1; }

    /* ---------- UserBadge (components.md) — deterministic color + shortened opaque UUID.
                 Hash-derived colors are represented here with Design System token colors. ---------- */
    .user-badge { display: inline-flex; align-items: center; gap: var(--space-1); font-size: var(--text-caption); font-weight: var(--weight-caption); color: var(--color-neutral-700); }
    .swatch { width: var(--space-4); height: var(--space-4); border-radius: 50%; flex: none; }
    .swatch-a { background: var(--color-primary); }
    .swatch-b { background: var(--color-success); }
    .swatch-c { background: var(--color-neutral-700); }
    .swatch-caller { background: var(--color-primary-dark); }
    .badge-unassigned {
      display: inline-flex; align-items: center;
      padding: 0 var(--space-1);
      border: 1px dashed var(--color-neutral-300); border-radius: var(--space-1);
      color: var(--color-neutral-700); font-size: var(--text-caption); font-weight: var(--weight-caption);
    }

    /* ---------- BoardToolbar ---------- */
    .toolbar {
      display: flex; align-items: center; flex-wrap: wrap; gap: var(--space-2);
      padding: var(--space-2) var(--space-4);
      border-bottom: 1px solid var(--color-neutral-300);
    }
    .toolbar-title { margin: 0; font-size: var(--text-h2); font-weight: var(--weight-h2); }
    .filter {
      display: inline-flex; align-items: center; gap: var(--space-1);
      padding: var(--space-1) var(--space-2);
      border: 1px solid var(--color-neutral-300); border-radius: var(--space-1);
      color: var(--color-neutral-700); font-size: var(--text-caption);
    }
    .btn-primary {
      padding: var(--space-1) var(--space-3);
      background: var(--color-primary); color: var(--color-neutral-50);
      border: 1px solid var(--color-primary-dark); border-radius: var(--space-1);
    }
    .toolbar-btn {
      padding: var(--space-1) var(--space-2);
      background: var(--color-neutral-50); color: var(--color-neutral-700);
      border: 1px solid var(--color-neutral-300); border-radius: var(--space-1);
    }
    .toolbar-link { font-size: var(--text-body); }

    /* ---------- Board: three status columns + collapsed activity drawer rail ---------- */
    .board { display: flex; gap: var(--space-3); padding: var(--space-4); }
    .columns {
      flex: 1; min-width: 0;
      display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: var(--space-3); align-items: start;
    }
    .column {
      background: var(--color-neutral-100);
      border-radius: var(--space-1);
      padding: var(--space-2);
      display: flex; flex-direction: column; gap: var(--space-3);
      min-height: 240px;
    }
    .column-title { margin: 0; padding: var(--space-1) var(--space-2) 0; font-size: var(--text-h2); font-weight: var(--weight-h2); }

    /* Activity Feed drawer — collapsed by default (screens/project-board.md) */
    .drawer-rail {
      flex: none;
      display: flex; flex-direction: column; align-items: center; gap: var(--space-2);
      background: var(--color-neutral-100);
      border: 1px solid var(--color-neutral-300); border-radius: var(--space-1);
      padding: var(--space-2) var(--space-1);
      color: var(--color-neutral-700);
    }
    .rail-glyph { font-size: var(--text-caption); }
    .rail-label { writing-mode: vertical-rl; font-size: var(--text-caption); }

    /* ---------- TaskCard ---------- */
    .card {
      position: relative;
      background: var(--color-neutral-100);
      border: 1px solid var(--color-neutral-300); border-radius: var(--space-1);
      padding: var(--space-2);
      display: flex; flex-direction: column; gap: var(--space-2);
    }
    .card-title { margin: 0; font-size: var(--text-body); }
    .card-meta { display: flex; align-items: center; gap: var(--space-2); }
    .chip {
      display: inline-flex; align-items: center;
      padding: 0 var(--space-1);
      border: 1px solid var(--color-neutral-300); border-radius: var(--space-1);
      font-size: var(--text-caption); font-weight: var(--weight-caption); color: var(--color-neutral-700);
      white-space: nowrap;
    }
    .chip-overdue { background: var(--color-warning); border-color: var(--color-warning); color: var(--color-neutral-900); }

    /* "Move to…" — visible keyboard-accessible alternative to drag-and-drop (WCAG 2.1 AA) */
    .move-btn {
      padding: 0 var(--space-1);
      background: var(--color-neutral-50); color: var(--color-neutral-700);
      border: 1px solid var(--color-neutral-300); border-radius: var(--space-1);
      font-size: var(--text-caption); white-space: nowrap;
    }
    .card-menu-open { z-index: 2; }
    .move-menu {
      position: absolute; right: var(--space-2); top: 100%; margin-top: calc(-1 * var(--space-1));
      min-width: 128px;
      background: var(--color-neutral-50);
      border: 1px solid var(--color-neutral-300); border-radius: var(--space-1);
      padding: var(--space-1);
      display: flex; flex-direction: column;
    }
    .move-menu-title { padding: var(--space-1) var(--space-2); font-size: var(--text-caption); color: var(--color-neutral-700); }
    .move-item {
      text-align: left;
      padding: var(--space-1) var(--space-2);
      background: var(--color-neutral-50); color: var(--color-neutral-900);
      border: 0; border-radius: var(--space-1);
      font-size: var(--text-body);
    }
    .move-item-focused { background: var(--color-neutral-100); }
    .move-item[disabled] { opacity: 0.5; cursor: not-allowed; } /* Disabled pattern — index.md Section 2.5 */

    /* ---------- Loading skeletons (index.md Section 2.5 — match content layout) ---------- */
    @keyframes skeleton-pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    .skeleton { background: var(--color-neutral-300); border-radius: var(--space-1); animation: skeleton-pulse 1.5s ease-in-out infinite; }
    .sk-line { height: var(--space-2); width: 100%; }
    .sk-line-short { width: 60%; }
    .sk-dot { width: var(--space-4); height: var(--space-4); border-radius: 50%; flex: none; }
    .sk-chip { width: 25%; height: var(--space-3); }
    .sk-title-bar { width: 25%; height: var(--space-3); }

    /* ---------- EmptyState (components.md — heading + description + CTA, never blank) ---------- */
    .empty-region {
      flex: 1; min-width: 0; min-height: 240px;
      display: flex; align-items: center; justify-content: center;
      background: var(--color-neutral-100); border-radius: var(--space-1);
      padding: var(--space-6);
    }
    .empty-state { text-align: center; padding: var(--space-6); }
    .empty-heading { margin: 0 0 var(--space-1); font-size: var(--text-h2); font-weight: var(--weight-h2); }
    .empty-desc { margin: 0 0 var(--space-4); color: var(--color-neutral-700); }

    /* ---------- ErrorBanner, region variant (components.md — accent border + retry) ---------- */
    .error-banner {
      display: flex; align-items: center; gap: var(--space-2);
      margin: var(--space-4) var(--space-4) 0;
      padding: var(--space-2) var(--space-3);
      background: var(--color-neutral-100);
      border: 1px solid var(--color-neutral-300);
      border-left: var(--space-1) solid var(--color-error);
      border-radius: var(--space-1);
    }
    .error-icon { width: var(--space-4); height: var(--space-4); color: var(--color-error); flex: none; }
    .error-message strong { font-weight: var(--weight-h2); }
    .btn-retry {
      margin-left: auto;
      padding: var(--space-1) var(--space-3);
      background: var(--color-primary); color: var(--color-neutral-50);
      border: 1px solid var(--color-primary-dark); border-radius: var(--space-1);
      white-space: nowrap;
    }

    /* ---------- Small screens: states and board columns stack (Section 2.6, mobile < 640px) ---------- */
    @media (max-width: 639px) {
      .states-grid { padding: var(--space-4); }
      .board { flex-direction: column; }
      .columns { grid-template-columns: 1fr; }
      .drawer-rail { flex-direction: row; justify-content: center; padding: var(--space-1) var(--space-2); }
      .rail-label { writing-mode: horizontal-tb; }
    }
  </style>
</head>

<body>

  <!-- Reviewer header -->
  <header class="reviewer-header">
    <h1>
      T-031 — Project Board Mockup
      <span>— Default, Loading, Empty, Error shown side-by-side</span>
    </h1>
    <p>TaskFlow · route /projects/:projectId/board · static visual prototype: plain embedded CSS, no JavaScript, no network requests. Users render as opaque-UUID UserBadges only — the app stores no names, emails, or avatars.</p>
  </header>

  <!-- States grid: one labeled section per state -->
  <main class="states-grid">

    <!-- ============================== DEFAULT ============================== -->
    <section class="state" aria-labelledby="state-default">
      <h2 id="state-default">Default</h2>
      <p class="state-note">Tasks loaded — cards grouped by status; activity drawer collapsed (right rail); the first To&nbsp;Do card shows the keyboard “Move to…” menu statically open.</p>
      <div class="frame">
        <div class="app-header">
          <svg class="logo" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><rect x="1" y="2" width="4" height="12" rx="1" fill="currentColor"/><rect x="6" y="2" width="4" height="8" rx="1" fill="currentColor"/><rect x="11" y="2" width="4" height="5" rx="1" fill="currentColor"/></svg>
          <span class="app-name">TaskFlow</span>
          <span class="app-sep">/</span>
          <span class="app-project">Marketing Site Refresh</span>
          <span class="app-spacer"></span>
          <span class="user-badge" title="Signed in as e2a8c4f6-1d3b-4a9e-8c5d-7f2b4e6a9c1d"><span class="swatch swatch-caller" aria-hidden="true"></span>e2a8c4f6</span>
        </div>
        <div class="toolbar">
          <p class="toolbar-title">Marketing Site Refresh</p>
          <span class="filter" title="Filter tasks by assignee — options render as UserBadges">Assignee: All ▾</span>
          <span class="toolbar-spacer"></span>
          <button class="btn-primary" type="button">+ New task</button>
          <a class="toolbar-link" href="#state-default">Members</a>
          <button class="toolbar-btn" type="button" title="Open the activity feed drawer">Activity ‹</button>
        </div>
        <div class="board">
          <div class="columns">
            <div class="column">
              <h3 class="column-title">To Do</h3>
              <article class="card card-menu-open">
                <p class="card-title">Wire the assignee filter to the members endpoint</p>
                <div class="card-meta">
                  <span class="swatch swatch-a" title="Assignee 7c9e6b1a-4f2d-4e8b-9a3c-5d8f2e7b1c4a"></span>
                  <span class="chip" title="Due 2026-07-24">Due Jul 24</span>
                  <span class="meta-spacer"></span>
                  <button class="move-btn" type="button" aria-expanded="true">Move to… ▾</button>
                </div>
                <div class="move-menu" role="menu" aria-label="Move to…">
                  <span class="move-menu-title">Move to…</span>
                  <button class="move-item" type="button" disabled>To Do ✓</button>
                  <button class="move-item move-item-focused" type="button">In Progress</button>
                  <button class="move-item" type="button">Done</button>
                </div>
              </article>
              <article class="card">
                <p class="card-title">Fix drag-and-drop rollback when a status update fails</p>
                <div class="card-meta">
                  <span class="swatch swatch-b" title="Assignee 3f8a2d5c-9b1e-4c7a-8d2f-6e4b9a1c3d7e"></span>
                  <span class="chip chip-overdue" title="Past due — 2026-07-10">Due Jul 10</span>
                  <span class="meta-spacer"></span>
                  <button class="move-btn" type="button">Move to… ▾</button>
                </div>
              </article>
              <article class="card">
                <p class="card-title">Add a keyboard shortcuts help dialog</p>
                <div class="card-meta">
                  <span class="badge-unassigned">Unassigned</span>
                  <span class="chip" title="Due 2026-07-30">Due Jul 30</span>
                  <span class="meta-spacer"></span>
                  <button class="move-btn" type="button">Move to… ▾</button>
                </div>
              </article>
            </div>
            <div class="column">
              <h3 class="column-title">In Progress</h3>
              <article class="card">
                <p class="card-title">Build the project activity feed endpoint</p>
                <div class="card-meta">
                  <span class="swatch swatch-c" title="Assignee b4d7f1e9-2a6c-4b8d-9e3f-1c5a7d2b8f4c"></span>
                  <span class="chip" title="Due 2026-07-18">Due Jul 18</span>
                  <span class="meta-spacer"></span>
                  <button class="move-btn" type="button">Move to… ▾</button>
                </div>
              </article>
              <article class="card">
                <p class="card-title">Render task comments with author badges</p>
                <div class="card-meta">
                  <span class="swatch swatch-a" title="Assignee 7c9e6b1a-4f2d-4e8b-9a3c-5d8f2e7b1c4a"></span>
                  <span class="chip" title="Due 2026-07-22">Due Jul 22</span>
                  <span class="meta-spacer"></span>
                  <button class="move-btn" type="button">Move to… ▾</button>
                </div>
              </article>
            </div>
            <div class="column">
              <h3 class="column-title">Done</h3>
              <article class="card">
                <p class="card-title">Set up TanStack Query for board data</p>
                <div class="card-meta">
                  <span class="swatch swatch-b" title="Assignee 3f8a2d5c-9b1e-4c7a-8d2f-6e4b9a1c3d7e"></span>
                  <span class="chip" title="Due 2026-07-16">Due Jul 16</span>
                  <span class="meta-spacer"></span>
                  <button class="move-btn" type="button">Move to… ▾</button>
                </div>
              </article>
              <article class="card">
                <p class="card-title">Scaffold the app shell header</p>
                <div class="card-meta">
                  <span class="swatch swatch-c" title="Assignee b4d7f1e9-2a6c-4b8d-9e3f-1c5a7d2b8f4c"></span>
                  <span class="chip" title="Due 2026-07-17">Due Jul 17</span>
                  <span class="meta-spacer"></span>
                  <button class="move-btn" type="button">Move to… ▾</button>
                </div>
              </article>
            </div>
          </div>
          <aside class="drawer-rail" title="Activity feed drawer — collapsed by default">
            <span class="rail-glyph" aria-hidden="true">‹</span>
            <span class="rail-label">Activity</span>
          </aside>
        </div>
      </div>
    </section>

    <!-- ============================== LOADING ============================== -->
    <section class="state" aria-labelledby="state-loading">
      <h2 id="state-loading">Loading</h2>
      <p class="state-note">Board queries in flight — skeleton placeholders match the card layout (CSS keyframe animation only; shown ≥200ms to avoid flicker).</p>
      <div class="frame">
        <div class="app-header">
          <svg class="logo" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><rect x="1" y="2" width="4" height="12" rx="1" fill="currentColor"/><rect x="6" y="2" width="4" height="8" rx="1" fill="currentColor"/><rect x="11" y="2" width="4" height="5" rx="1" fill="currentColor"/></svg>
          <span class="app-name">TaskFlow</span>
          <span class="app-spacer"></span>
          <span class="user-badge" title="Signed in as e2a8c4f6-1d3b-4a9e-8c5d-7f2b4e6a9c1d"><span class="swatch swatch-caller" aria-hidden="true"></span>e2a8c4f6</span>
        </div>
        <div class="toolbar" aria-hidden="true">
          <span class="skeleton sk-title-bar"></span>
          <span class="filter">Assignee: All ▾</span>
          <span class="toolbar-spacer"></span>
          <button class="btn-primary" type="button">+ New task</button>
          <a class="toolbar-link" href="#state-loading">Members</a>
          <button class="toolbar-btn" type="button">Activity ‹</button>
        </div>
        <div class="board" aria-busy="true">
          <span class="sr-only" role="status">Loading the project board…</span>
          <div class="columns" aria-hidden="true">
            <div class="column">
              <h3 class="column-title">To Do</h3>
              <div class="card"><div class="skeleton sk-line"></div><div class="skeleton sk-line sk-line-short"></div><div class="card-meta"><div class="skeleton sk-dot"></div><div class="skeleton sk-chip"></div></div></div>
              <div class="card"><div class="skeleton sk-line"></div><div class="card-meta"><div class="skeleton sk-dot"></div><div class="skeleton sk-chip"></div></div></div>
              <div class="card"><div class="skeleton sk-line"></div><div class="skeleton sk-line sk-line-short"></div><div class="card-meta"><div class="skeleton sk-dot"></div><div class="skeleton sk-chip"></div></div></div>
            </div>
            <div class="column">
              <h3 class="column-title">In Progress</h3>
              <div class="card"><div class="skeleton sk-line"></div><div class="skeleton sk-line sk-line-short"></div><div class="card-meta"><div class="skeleton sk-dot"></div><div class="skeleton sk-chip"></div></div></div>
              <div class="card"><div class="skeleton sk-line"></div><div class="card-meta"><div class="skeleton sk-dot"></div><div class="skeleton sk-chip"></div></div></div>
            </div>
            <div class="column">
              <h3 class="column-title">Done</h3>
              <div class="card"><div class="skeleton sk-line"></div><div class="card-meta"><div class="skeleton sk-dot"></div><div class="skeleton sk-chip"></div></div></div>
            </div>
          </div>
          <aside class="drawer-rail" title="Activity feed drawer — collapsed by default">
            <span class="rail-glyph" aria-hidden="true">‹</span>
            <span class="rail-label">Activity</span>
          </aside>
        </div>
      </div>
    </section>

    <!-- ============================== EMPTY ============================== -->
    <section class="state" aria-labelledby="state-empty">
      <h2 id="state-empty">Empty</h2>
      <p class="state-note">Project has no tasks — board-wide EmptyState (heading + description + CTA; never a blank region).</p>
      <div class="frame">
        <div class="app-header">
          <svg class="logo" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><rect x="1" y="2" width="4" height="12" rx="1" fill="currentColor"/><rect x="6" y="2" width="4" height="8" rx="1" fill="currentColor"/><rect x="11" y="2" width="4" height="5" rx="1" fill="currentColor"/></svg>
          <span class="app-name">TaskFlow</span>
          <span class="app-sep">/</span>
          <span class="app-project">Marketing Site Refresh</span>
          <span class="app-spacer"></span>
          <span class="user-badge" title="Signed in as e2a8c4f6-1d3b-4a9e-8c5d-7f2b4e6a9c1d"><span class="swatch swatch-caller" aria-hidden="true"></span>e2a8c4f6</span>
        </div>
        <div class="toolbar">
          <p class="toolbar-title">Marketing Site Refresh</p>
          <span class="filter" title="Filter tasks by assignee — options render as UserBadges">Assignee: All ▾</span>
          <span class="toolbar-spacer"></span>
          <button class="btn-primary" type="button">+ New task</button>
          <a class="toolbar-link" href="#state-empty">Members</a>
          <button class="toolbar-btn" type="button" title="Open the activity feed drawer">Activity ‹</button>
        </div>
        <div class="board">
          <div class="empty-region">
            <div class="empty-state">
              <p class="empty-heading">No tasks yet</p>
              <p class="empty-desc">Create the first task to get this board moving.</p>
              <button class="btn-primary" type="button">+ New task</button>
            </div>
          </div>
          <aside class="drawer-rail" title="Activity feed drawer — collapsed by default (shows “No activity yet” when opened)">
            <span class="rail-glyph" aria-hidden="true">‹</span>
            <span class="rail-label">Activity</span>
          </aside>
        </div>
      </div>
    </section>

    <!-- ============================== ERROR ============================== -->
    <section class="state" aria-labelledby="state-error">
      <h2 id="state-error">Error</h2>
      <p class="state-note">Board query failed — ErrorBanner (region variant) with a retry button above the columns; human-readable message, no raw error codes.</p>
      <div class="frame">
        <div class="app-header">
          <svg class="logo" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><rect x="1" y="2" width="4" height="12" rx="1" fill="currentColor"/><rect x="6" y="2" width="4" height="8" rx="1" fill="currentColor"/><rect x="11" y="2" width="4" height="5" rx="1" fill="currentColor"/></svg>
          <span class="app-name">TaskFlow</span>
          <span class="app-sep">/</span>
          <span class="app-project">Marketing Site Refresh</span>
          <span class="app-spacer"></span>
          <span class="user-badge" title="Signed in as e2a8c4f6-1d3b-4a9e-8c5d-7f2b4e6a9c1d"><span class="swatch swatch-caller" aria-hidden="true"></span>e2a8c4f6</span>
        </div>
        <div class="toolbar">
          <p class="toolbar-title">Marketing Site Refresh</p>
          <span class="filter" title="Filter tasks by assignee — options render as UserBadges">Assignee: All ▾</span>
          <span class="toolbar-spacer"></span>
          <button class="btn-primary" type="button">+ New task</button>
          <a class="toolbar-link" href="#state-error">Members</a>
          <button class="toolbar-btn" type="button" title="Open the activity feed drawer">Activity ‹</button>
        </div>
        <div class="error-banner" role="alert">
          <svg class="error-icon" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><circle cx="8" cy="8" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 4.5v4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="8" cy="11.5" r="0.9" fill="currentColor"/></svg>
          <span class="error-message"><strong>We couldn’t load the board.</strong> Check your connection and try again.</span>
          <button class="btn-retry" type="button">Retry</button>
        </div>
        <div class="board">
          <div class="columns">
            <div class="column"><h3 class="column-title">To Do</h3></div>
            <div class="column"><h3 class="column-title">In Progress</h3></div>
            <div class="column"><h3 class="column-title">Done</h3></div>
          </div>
          <aside class="drawer-rail" title="Activity feed drawer — collapsed by default">
            <span class="rail-glyph" aria-hidden="true">‹</span>
            <span class="rail-label">Activity</span>
          </aside>
        </div>
      </div>
    </section>

  </main>

</body>
</html>
