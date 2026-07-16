<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>T-031 Project Board Mockup — TaskFlow</title>

  <!-- Static mockup for stakeholder visual approval. All styles embedded; no external requests. -->
  <style>
    :root {
      /* ── Design tokens — docs/ui-specification/index.md Section 2 (exact values) ── */

      /* 2.1 Brand Colors */
      --primary: #2563EB;        /* Primary actions, active states, links */
      --primary-dark: #1D4ED8;   /* Hover/pressed states */
      --neutral-50: #F8FAFC;     /* App background */
      --neutral-100: #F1F5F9;    /* Card, column, and drawer backgrounds */
      --neutral-300: #CBD5E1;    /* Dividers, borders */
      --neutral-700: #334155;    /* Secondary text */
      --neutral-900: #0F172A;    /* Primary text */
      --success: #16A34A;        /* Success toasts */
      --warning: #D97706;        /* Overdue due-date chips */
      --error: #DC2626;          /* Error states, destructive actions */

      /* 2.2 Typography Scale (system font stack — the Design System declares no fonts) */
      --font-sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      --text-h1: 1.5rem;         /* 24px · 600 · screen titles */
      --text-h2: 1.125rem;       /* 18px · 600 · column headers, panel sections */
      --text-body: 0.875rem;     /* 14px · 400 · card titles, form fields, comments */
      --text-caption: 0.75rem;   /* 12px · 400 · timestamps, metadata, badges */
      --weight-heading: 600;
      --weight-body: 400;

      /* 2.3 Spacing Scale (base unit 4px) */
      --space-1: 4px;            /* tight internal padding (badges, chips) */
      --space-2: 8px;            /* standard internal padding */
      --space-3: 12px;           /* gaps between cards and rows */
      --space-4: 16px;           /* column, panel, and form padding */
      --space-6: 24px;           /* page-level padding */
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--neutral-50);
      color: var(--neutral-900);
      font-family: var(--font-sans);
      font-size: var(--text-body);
      font-weight: var(--weight-body);
      line-height: 1.5;
    }

    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0 0 0 0);
      white-space: nowrap;
      border: 0;
    }

    /* ── Reviewer header ── */
    .reviewer-header {
      background: var(--neutral-900);
      color: var(--neutral-50);
      padding: var(--space-4) var(--space-6);
    }
    .reviewer-header h1 {
      margin: 0;
      font-size: var(--text-h1);
      font-weight: var(--weight-heading);
    }
    .reviewer-header h1 span {
      font-size: var(--text-body);
      font-weight: var(--weight-body);
      color: var(--neutral-300);
    }
    .reviewer-header p {
      margin: var(--space-1) 0 0;
      font-size: var(--text-caption);
      color: var(--neutral-300);
    }

    /* ── States grid: one section per state, side-by-side; stacks below desktop ── */
    .states-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--space-6);
      padding: var(--space-6);
    }
    @media (min-width: 1024px) {
      /* Desktop breakpoint (Section 2.6) */
      .states-grid { grid-template-columns: 1fr 1fr; }
    }

    .state { min-width: 0; }
    .state__label {
      margin: 0 0 var(--space-1);
      font-size: var(--text-h2);
      font-weight: var(--weight-heading);
    }
    .state__note {
      margin: 0 0 var(--space-3);
      font-size: var(--text-caption);
      color: var(--neutral-700);
    }

    /* ── Screen frame: app shell (index.md Section 4.1) around the board ── */
    .frame {
      border: 1px solid var(--neutral-300);
      border-radius: var(--space-2);
      background: var(--neutral-50);
      overflow: hidden;
    }

    .app-header {
      height: 48px; /* slim header, always visible (Section 4.1) */
      display: flex;
      align-items: center;
      gap: var(--space-2);
      padding: 0 var(--space-4);
      border-bottom: 1px solid var(--neutral-300);
      background: var(--neutral-50);
    }
    .logo {
      display: inline-flex;
      align-items: center;
      gap: var(--space-1);
      font-weight: var(--weight-heading);
    }
    .logo-mark { fill: var(--primary); }
    .logo-check { fill: none; stroke: var(--neutral-50); }
    .app-header__sep { color: var(--neutral-300); }
    .app-header__project { color: var(--neutral-700); }
    .app-header .user-badge { margin-left: auto; }

    /* ── BoardToolbar ── */
    .board-toolbar {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: var(--space-3);
      padding: var(--space-3) var(--space-4);
      border-bottom: 1px solid var(--neutral-300);
      background: var(--neutral-50);
    }
    .board-toolbar__project {
      margin: 0;
      font-size: var(--text-h1); /* screen title */
      font-weight: var(--weight-heading);
    }
    .filter {
      display: inline-flex;
      align-items: center;
      gap: var(--space-1);
    }
    .filter__label {
      font-size: var(--text-caption);
      color: var(--neutral-700);
    }
    .filter__select {
      border: 1px solid var(--neutral-300);
      border-radius: var(--space-1);
      background: var(--neutral-50);
      padding: var(--space-1) var(--space-2);
      color: var(--neutral-900);
    }
    .btn {
      font-family: inherit;
      font-size: var(--text-body);
      border-radius: var(--space-1);
      padding: var(--space-1) var(--space-3);
      cursor: pointer;
      border: 1px solid transparent;
      background: none;
      color: inherit;
    }
    .btn--primary {
      background: var(--primary);
      border-color: var(--primary);
      color: var(--neutral-50);
    }
    .btn--primary:hover { background: var(--primary-dark); border-color: var(--primary-dark); }
    .btn--ghost {
      border-color: var(--neutral-300);
      color: var(--neutral-700);
    }
    .members-link { color: var(--primary); }
    .board-toolbar .btn--ghost { margin-left: auto; }

    /* ── Board area: three status columns + collapsed Activity Feed drawer ── */
    .board {
      display: flex;
      gap: var(--space-4);
      padding: var(--space-4);
      min-height: 320px;
    }
    .columns {
      flex: 1;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: var(--space-4);
      min-width: 0;
    }
    .columns--disabled {
      /* Disabled pattern (Section 2.5): opacity, not gray recoloring */
      opacity: 0.5;
      cursor: not-allowed;
    }
    .column {
      background: var(--neutral-100);
      border-radius: var(--space-2);
      padding: var(--space-3);
      min-width: 0;
    }
    .column__title {
      margin: 0 0 var(--space-3);
      font-size: var(--text-h2);
      font-weight: var(--weight-heading);
    }

    /* ── TaskCard (screen-specific, screens/project-board.md) ── */
    .task-card {
      background: var(--neutral-100);
      border: 1px solid var(--neutral-300);
      border-radius: var(--space-2);
      padding: var(--space-2);
    }
    .task-card + .task-card { margin-top: var(--space-3); }
    .task-card__title { margin: 0 0 var(--space-2); }
    .task-card__meta {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: var(--space-2);
    }

    /* Due-date chip — warning-colored when the calendar date is past */
    .chip {
      font-size: var(--text-caption);
      color: var(--neutral-700);
      background: var(--neutral-50);
      border: 1px solid var(--neutral-300);
      border-radius: var(--space-2);
      padding: 0 var(--space-2);
    }
    .chip--overdue {
      background: var(--warning);
      border-color: var(--warning);
      color: var(--neutral-50);
    }

    /* "Move to…" — visible keyboard-accessible alternative to drag-and-drop (WCAG 2.1 AA) */
    .move-btn {
      font-family: inherit;
      font-size: var(--text-caption);
      color: var(--primary);
      background: none;
      border: 0;
      padding: var(--space-1);
      margin-left: auto;
      cursor: pointer;
    }
    .move-menu {
      margin: var(--space-2) 0 0;
      padding: var(--space-1);
      list-style: none;
      background: var(--neutral-50);
      border: 1px solid var(--neutral-300);
      border-radius: var(--space-1);
    }
    .move-menu__label {
      display: block;
      padding: var(--space-1) var(--space-2);
      font-size: var(--text-caption);
      color: var(--neutral-700);
    }
    .move-menu li {
      padding: var(--space-1) var(--space-2);
      border-radius: var(--space-1);
    }
    .move-menu li.is-current { color: var(--neutral-700); }
    .move-menu li.is-option { color: var(--primary); }

    /* ── UserBadge (shared — components.md): the only way a user is ever rendered ── */
    .user-badge {
      display: inline-flex;
      align-items: center;
      gap: var(--space-1);
      font-size: var(--text-caption);
    }
    .user-badge__swatch {
      width: var(--space-4);
      height: var(--space-4);
      border-radius: 50%;
      flex: none;
    }
    .user-badge--unassigned {
      border: 1px dashed var(--neutral-300);
      border-radius: var(--space-2);
      padding: 0 var(--space-2);
      color: var(--neutral-700);
    }
    /* Swatch backgrounds are deterministic, derived from each opaque user UUID's hash
       (components.md — UserBadge); they are intentionally not Design System tokens. */
    .swatch-9d2f66c1 { background: hsl(16, 55%, 45%); }
    .swatch-7f3a9c2e { background: hsl(207, 61%, 42%); }
    .swatch-b41d8e07 { background: hsl(152, 45%, 36%); }
    .swatch-3c9f52aa { background: hsl(268, 44%, 50%); }

    /* ── Activity Feed drawer — collapsed by default ── */
    .drawer-collapsed {
      flex: none;
      width: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--neutral-100);
      border: 1px solid var(--neutral-300);
      border-radius: var(--space-2);
    }
    .drawer-collapsed span {
      writing-mode: vertical-rl;
      font-size: var(--text-caption);
      color: var(--neutral-700);
    }

    /* ── Loading skeletons (Section 2.5: match real content dimensions) ── */
    .skel {
      background: linear-gradient(90deg, var(--neutral-300), var(--neutral-100), var(--neutral-300));
      background-size: 200% 100%;
      animation: shimmer 1.4s linear infinite;
      border-radius: var(--space-1);
    }
    @keyframes shimmer {
      from { background-position: 200% 0; }
      to   { background-position: -200% 0; }
    }
    .skel--title { height: 0.875rem; width: 75%; margin-bottom: var(--space-2); }
    .skel--dot   { width: var(--space-4); height: var(--space-4); border-radius: 50%; flex: none; }
    .skel--chip  { width: 72px; height: 1.125rem; border-radius: var(--space-2); }

    /* ── EmptyState (shared — heading + description + CTA, never blank) ── */
    .empty-state {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: var(--space-6);
    }
    .empty-state__heading {
      margin: 0 0 var(--space-1);
      font-size: var(--text-h2);
      font-weight: var(--weight-heading);
    }
    .empty-state__description {
      margin: 0 0 var(--space-4);
      color: var(--neutral-700);
    }

    /* ── ErrorBanner (shared — region variant: error accent border + retry) ── */
    .error-banner {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: var(--space-3);
      margin: var(--space-4) var(--space-4) 0;
      padding: var(--space-3) var(--space-4);
      background: var(--neutral-50);
      border: 1px solid var(--neutral-300);
      border-left: 4px solid var(--error);
      border-radius: var(--space-1);
    }
    .error-banner strong { color: var(--error); }
    .error-banner__retry {
      margin-left: auto;
      font-family: inherit;
      font-size: var(--text-body);
      color: var(--error);
      background: none;
      border: 1px solid var(--error);
      border-radius: var(--space-1);
      padding: var(--space-1) var(--space-3);
      cursor: pointer;
    }

    /* ── Mobile (Section 2.6): board columns stack vertically ── */
    @media (max-width: 639px) {
      .board { flex-direction: column; }
      .columns { grid-template-columns: 1fr; }
      .drawer-collapsed { width: auto; height: 40px; }
      .drawer-collapsed span { writing-mode: horizontal-tb; }
    }
  </style>
</head>

<body>

  <!-- Reviewer header -->
  <header class="reviewer-header">
    <h1>
      T-031 · Project Board Mockup
      <span>— Default, Loading, Empty, Error shown side-by-side</span>
    </h1>
    <p>TaskFlow · Route /projects/:projectId/board · Static HTML prototype for stakeholder visual approval — no JavaScript, no external requests</p>
  </header>

  <main class="states-grid">

    <!-- ═════════ State 1: Default ═════════ -->
    <section class="state" aria-labelledby="label-default">
      <h2 class="state__label" id="label-default">1 · Default</h2>
      <p class="state__note">Tasks loaded — three status columns of TaskCards; Activity Feed drawer collapsed by default. Every card carries the keyboard "Move to…" alternative to drag-and-drop; the menu is shown statically open on one card.</p>
      <div class="frame">
        <div class="app-header">
          <span class="logo">
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">
              <rect class="logo-mark" x="3" y="3" width="18" height="18" rx="4" />
              <path class="logo-check" d="M8 12.5l3 3 5-6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            TaskFlow
          </span>
          <span class="app-header__sep">·</span>
          <span class="app-header__project">Website Relaunch</span>
          <span class="user-badge" title="9d2f66c1-4b0e-4c1a-9f3e-8a51c0d7b2aa">
            <span class="user-badge__swatch swatch-9d2f66c1"></span>9d2f66c1
          </span>
        </div>

        <div class="board-toolbar">
          <p class="board-toolbar__project">Website Relaunch</p>
          <span class="filter">
            <span class="filter__label">Assignee</span>
            <span class="filter__select">All ▾</span>
          </span>
          <button class="btn btn--primary" type="button">+ New task</button>
          <a class="members-link" href="#members">Members</a>
          <button class="btn btn--ghost" type="button">Activity</button>
        </div>

        <div class="board">
          <div class="columns">
            <div class="column">
              <h3 class="column__title">To Do</h3>
              <article class="task-card">
                <p class="task-card__title">Design empty-state illustrations</p>
                <div class="task-card__meta">
                  <span class="user-badge" title="b41d8e07-9c2a-4f6e-8d13-57a0ce92bf64">
                    <span class="user-badge__swatch swatch-b41d8e07"></span>
                    <span class="sr-only">Assignee b41d8e07</span>
                  </span>
                  <span class="chip">Due 2026-07-21</span>
                  <button class="move-btn" type="button">Move to…</button>
                </div>
              </article>
              <article class="task-card">
                <p class="task-card__title">Write keyboard-navigation test plan</p>
                <div class="task-card__meta">
                  <span class="user-badge user-badge--unassigned">Unassigned</span>
                  <span class="chip">Due 2026-07-24</span>
                  <button class="move-btn" type="button">Move to…</button>
                </div>
              </article>
            </div>
            <div class="column">
              <h3 class="column__title">In Progress</h3>
              <article class="task-card">
                <p class="task-card__title">Implement JWT refresh flow</p>
                <div class="task-card__meta">
                  <span class="user-badge" title="7f3a9c2e-51d4-4b8a-b0c6-2e9d14f7a3c5">
                    <span class="user-badge__swatch swatch-7f3a9c2e"></span>
                    <span class="sr-only">Assignee 7f3a9c2e</span>
                  </span>
                  <span class="chip chip--overdue" title="Overdue — the due date is past">Due 2026-07-14</span>
                  <button class="move-btn" type="button" aria-haspopup="menu" aria-expanded="true">Move to…</button>
                </div>
                <ul class="move-menu">
                  <li class="move-menu__label" role="presentation">Move to…</li>
                  <li class="is-option">To Do</li>
                  <li class="is-current">✓ In Progress (current)</li>
                  <li class="is-option">Done</li>
                </ul>
              </article>
            </div>
            <div class="column">
              <h3 class="column__title">Done</h3>
              <article class="task-card">
                <p class="task-card__title">Set up CI pipeline</p>
                <div class="task-card__meta">
                  <span class="user-badge" title="3c9f52aa-e81b-4d07-a2f4-6b1d90c8e735">
                    <span class="user-badge__swatch swatch-3c9f52aa"></span>
                    <span class="sr-only">Assignee 3c9f52aa</span>
                  </span>
                  <span class="chip">Due 2026-07-18</span>
                  <button class="move-btn" type="button">Move to…</button>
                </div>
              </article>
            </div>
          </div>
          <aside class="drawer-collapsed" title="Activity Feed drawer — collapsed by default; opens with the Activity toggle">
            <span>Activity ›</span>
          </aside>
        </div>
      </div>
    </section>

    <!-- ═════════ State 2: Loading ═════════ -->
    <section class="state" aria-labelledby="label-loading">
      <h2 class="state__label" id="label-loading">2 · Loading</h2>
      <p class="state__note">Board queries in flight — skeleton card placeholders match the real content layout (title line, assignee badge, due-date chip).</p>
      <div class="frame">
        <div class="app-header">
          <span class="logo">
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">
              <rect class="logo-mark" x="3" y="3" width="18" height="18" rx="4" />
              <path class="logo-check" d="M8 12.5l3 3 5-6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            TaskFlow
          </span>
          <span class="app-header__sep">·</span>
          <span class="app-header__project">Website Relaunch</span>
          <span class="user-badge" title="9d2f66c1-4b0e-4c1a-9f3e-8a51c0d7b2aa">
            <span class="user-badge__swatch swatch-9d2f66c1"></span>9d2f66c1
          </span>
        </div>

        <div class="board-toolbar">
          <p class="board-toolbar__project">Website Relaunch</p>
          <span class="filter">
            <span class="filter__label">Assignee</span>
            <span class="filter__select">All ▾</span>
          </span>
          <button class="btn btn--primary" type="button">+ New task</button>
          <a class="members-link" href="#members">Members</a>
          <button class="btn btn--ghost" type="button">Activity</button>
        </div>

        <div class="board">
          <span class="sr-only">Loading the board…</span>
          <div class="columns" aria-hidden="true">
            <div class="column">
              <h3 class="column__title">To Do</h3>
              <article class="task-card">
                <div class="skel skel--title"></div>
                <div class="task-card__meta">
                  <div class="skel skel--dot"></div>
                  <div class="skel skel--chip"></div>
                </div>
              </article>
              <article class="task-card">
                <div class="skel skel--title"></div>
                <div class="task-card__meta">
                  <div class="skel skel--dot"></div>
                  <div class="skel skel--chip"></div>
                </div>
              </article>
            </div>
            <div class="column">
              <h3 class="column__title">In Progress</h3>
              <article class="task-card">
                <div class="skel skel--title"></div>
                <div class="task-card__meta">
                  <div class="skel skel--dot"></div>
                  <div class="skel skel--chip"></div>
                </div>
              </article>
            </div>
            <div class="column">
              <h3 class="column__title">Done</h3>
              <article class="task-card">
                <div class="skel skel--title"></div>
                <div class="task-card__meta">
                  <div class="skel skel--dot"></div>
                  <div class="skel skel--chip"></div>
                </div>
              </article>
            </div>
          </div>
          <aside class="drawer-collapsed" title="Activity Feed drawer — collapsed by default">
            <span>Activity ›</span>
          </aside>
        </div>
      </div>
    </section>

    <!-- ═════════ State 3: Empty ═════════ -->
    <section class="state" aria-labelledby="label-empty">
      <h2 class="state__label" id="label-empty">3 · Empty</h2>
      <p class="state__note">Project has no tasks — board-wide EmptyState with heading, description, and CTA; never a blank region.</p>
      <div class="frame">
        <div class="app-header">
          <span class="logo">
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">
              <rect class="logo-mark" x="3" y="3" width="18" height="18" rx="4" />
              <path class="logo-check" d="M8 12.5l3 3 5-6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            TaskFlow
          </span>
          <span class="app-header__sep">·</span>
          <span class="app-header__project">Website Relaunch</span>
          <span class="user-badge" title="9d2f66c1-4b0e-4c1a-9f3e-8a51c0d7b2aa">
            <span class="user-badge__swatch swatch-9d2f66c1"></span>9d2f66c1
          </span>
        </div>

        <div class="board-toolbar">
          <p class="board-toolbar__project">Website Relaunch</p>
          <span class="filter">
            <span class="filter__label">Assignee</span>
            <span class="filter__select">All ▾</span>
          </span>
          <button class="btn btn--primary" type="button">+ New task</button>
          <a class="members-link" href="#members">Members</a>
          <button class="btn btn--ghost" type="button">Activity</button>
        </div>

        <div class="board">
          <div class="empty-state">
            <h3 class="empty-state__heading">No tasks yet</h3>
            <p class="empty-state__description">Create the first task to get this project moving.</p>
            <button class="btn btn--primary" type="button">+ New task</button>
          </div>
          <aside class="drawer-collapsed" title="Activity Feed drawer — collapsed by default; no activity yet">
            <span>Activity ›</span>
          </aside>
        </div>
      </div>
    </section>

    <!-- ═════════ State 4: Error ═════════ -->
    <section class="state" aria-labelledby="label-error">
      <h2 class="state__label" id="label-error">4 · Error</h2>
      <p class="state__note">Board query failed — ErrorBanner with a retry button above the columns; human-readable message, no raw error codes.</p>
      <div class="frame">
        <div class="app-header">
          <span class="logo">
            <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">
              <rect class="logo-mark" x="3" y="3" width="18" height="18" rx="4" />
              <path class="logo-check" d="M8 12.5l3 3 5-6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            TaskFlow
          </span>
          <span class="app-header__sep">·</span>
          <span class="app-header__project">Website Relaunch</span>
          <span class="user-badge" title="9d2f66c1-4b0e-4c1a-9f3e-8a51c0d7b2aa">
            <span class="user-badge__swatch swatch-9d2f66c1"></span>9d2f66c1
          </span>
        </div>

        <div class="board-toolbar">
          <p class="board-toolbar__project">Website Relaunch</p>
          <span class="filter">
            <span class="filter__label">Assignee</span>
            <span class="filter__select">All ▾</span>
          </span>
          <button class="btn btn--primary" type="button">+ New task</button>
          <a class="members-link" href="#members">Members</a>
          <button class="btn btn--ghost" type="button">Activity</button>
        </div>

        <div class="error-banner" role="alert">
          <span><strong>We couldn't load the board.</strong> Check your connection and try again.</span>
          <button class="error-banner__retry" type="button">Retry</button>
        </div>

        <div class="board">
          <div class="columns columns--disabled" aria-hidden="true">
            <div class="column">
              <h3 class="column__title">To Do</h3>
            </div>
            <div class="column">
              <h3 class="column__title">In Progress</h3>
            </div>
            <div class="column">
              <h3 class="column__title">Done</h3>
            </div>
          </div>
          <aside class="drawer-collapsed" title="Activity Feed drawer — collapsed by default">
            <span>Activity ›</span>
          </aside>
        </div>
      </div>
    </section>

  </main>

</body>
</html>
