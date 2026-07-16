<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>T-031 Project Board Mockup — TaskFlow</title>

  <!-- All styles embedded — fully self-contained, no external requests, works offline -->
  <style>
    /* ==========================================================
       Design tokens — verbatim from the UI Specification
       (docs/ui-specification/index.md, Section 2 Design System).
       No invented colors, sizes, or spacing.
       ========================================================== */
    :root {
      /* 2.1 Brand Colors */
      --color-primary: #2563EB;
      --color-primary-dark: #1D4ED8;
      --color-neutral-50: #F8FAFC;
      --color-neutral-100: #F1F5F9;
      --color-neutral-300: #CBD5E1;
      --color-neutral-700: #334155;
      --color-neutral-900: #0F172A;
      --color-success: #16A34A;
      --color-warning: #D97706;
      --color-error: #DC2626;

      /* 2.2 Typography Scale — the Design System declares no fonts:
         system font stack */
      --font-sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      --font-h1-size: 1.5rem;
      --font-h1-weight: 600;
      --font-h2-size: 1.125rem;
      --font-h2-weight: 600;
      --font-body-size: 0.875rem;
      --font-body-weight: 400;
      --font-caption-size: 0.75rem;
      --font-caption-weight: 400;

      /* 2.3 Spacing Scale — base unit 4px */
      --space-1: 4px;
      --space-2: 8px;
      --space-3: 12px;
      --space-4: 16px;
      --space-6: 24px;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      padding: var(--space-6);
      background: var(--color-neutral-50);
      color: var(--color-neutral-900);
      font-family: var(--font-sans);
      font-size: var(--font-body-size);
      font-weight: var(--font-body-weight);
      line-height: 1.5;
    }

    .sr-only {
      position: absolute; width: 1px; height: 1px;
      padding: 0; margin: -1px; overflow: hidden;
      clip: rect(0 0 0 0); white-space: nowrap; border: 0;
    }

    /* ---------- Reviewer header ---------- */
    .reviewer-header {
      border-bottom: 1px solid var(--color-neutral-300);
      padding-bottom: var(--space-4);
      margin-bottom: var(--space-6);
    }
    .reviewer-header h1 {
      margin: 0 0 var(--space-1);
      font-size: var(--font-h1-size);
      font-weight: var(--font-h1-weight);
    }
    .reviewer-header .sub {
      margin: 0;
      color: var(--color-neutral-700);
      font-size: var(--font-caption-size);
      font-weight: var(--font-caption-weight);
    }

    /* ---------- States grid: side-by-side, stacks on small screens ---------- */
    .states-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(540px, 100%), 1fr));
      gap: var(--space-6);
      align-items: start;
    }
    .state > h2 {
      margin: 0 0 var(--space-1);
      font-size: var(--font-h2-size);
      font-weight: var(--font-h2-weight);
    }
    .state > .state-note {
      margin: 0 0 var(--space-2);
      color: var(--color-neutral-700);
      font-size: var(--font-caption-size);
      font-weight: var(--font-caption-weight);
    }

    /* ---------- App shell frame (index.md Section 4.1) ---------- */
    .screen {
      border: 1px solid var(--color-neutral-300);
      border-radius: 8px;
      overflow: hidden;
      background: var(--color-neutral-50);
    }
    .shell-header {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      height: 48px; /* slim header per Section 4.1 */
      padding: 0 var(--space-4);
      background: var(--color-neutral-100);
      border-bottom: 1px solid var(--color-neutral-300);
    }
    .logo { font-weight: 600; }
    .shell-sep, .shell-project { color: var(--color-neutral-700); }
    .spacer { margin-left: auto; }

    /* ---------- UserBadge (shared component) ----------
       Runtime derives each swatch color deterministically from the
       UUID hash; this static mockup stands those in with Design
       System token colors. Compact (sm) variant on cards: swatch
       only, full id in the title attribute. */
    .badge {
      display: inline-flex;
      align-items: center;
      gap: var(--space-1);
      font-size: var(--font-caption-size);
      font-weight: var(--font-caption-weight);
      color: var(--color-neutral-700);
    }
    .swatch { display: inline-block; width: 16px; height: 16px; border-radius: 4px; }
    .swatch.sm { width: 14px; height: 14px; border-radius: 50%; }
    .swatch-a { background: var(--color-primary); }
    .swatch-b { background: var(--color-success); }
    .swatch-c { background: var(--color-neutral-700); }
    .swatch-d { background: var(--color-primary-dark); }
    .badge-unassigned {
      display: inline-flex;
      align-items: center;
      padding: var(--space-1) var(--space-2);
      border: 1px dashed var(--color-neutral-300);
      border-radius: 999px;
      color: var(--color-neutral-700);
      font-size: var(--font-caption-size);
      font-weight: var(--font-caption-weight);
    }

    /* ---------- BoardToolbar ---------- */
    .toolbar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: var(--space-3);
      padding: var(--space-3) var(--space-4);
      border-bottom: 1px solid var(--color-neutral-300);
    }
    .project-name {
      font-size: var(--font-h2-size);
      font-weight: var(--font-h2-weight);
    }
    .filter {
      display: inline-flex;
      align-items: center;
      gap: var(--space-1);
      padding: var(--space-1) var(--space-2);
      border: 1px solid var(--color-neutral-300);
      border-radius: 6px;
      background: var(--color-neutral-50);
      color: var(--color-neutral-700);
      font-size: var(--font-caption-size);
    }
    .btn {
      display: inline-flex;
      align-items: center;
      gap: var(--space-1);
      padding: var(--space-2) var(--space-3);
      border: 1px solid transparent;
      border-radius: 6px;
      font-family: var(--font-sans);
      font-size: var(--font-body-size);
      font-weight: var(--font-body-weight);
      cursor: pointer;
    }
    .btn-primary { background: var(--color-primary); color: var(--color-neutral-50); }
    .btn-primary:hover { background: var(--color-primary-dark); } /* primary-dark: hover/pressed */
    .btn-ghost {
      background: var(--color-neutral-50);
      border-color: var(--color-neutral-300);
      color: var(--color-neutral-700);
    }
    .link { color: var(--color-primary); text-decoration: underline; }

    /* ---------- Board: three status columns + drawer rail ---------- */
    .board { display: flex; align-items: stretch; }
    .board-main { flex: 1; min-width: 0; }
    .columns {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: var(--space-3); /* gaps between cards and rows */
      padding: var(--space-4);
    }
    .column {
      background: var(--color-neutral-100); /* column background token */
      border: 1px solid var(--color-neutral-300);
      border-radius: 8px;
      padding: var(--space-4); /* column padding token */
      min-width: 0;
    }
    .column-head {
      display: flex;
      align-items: baseline;
      gap: var(--space-2);
      margin-bottom: var(--space-3);
    }
    .column-head h3 {
      margin: 0;
      font-size: var(--font-h2-size); /* h2 type: column headers */
      font-weight: var(--font-h2-weight);
    }
    .count { color: var(--color-neutral-700); font-size: var(--font-caption-size); }
    .cards { display: flex; flex-direction: column; gap: var(--space-3); }
    .cards.is-empty { min-height: 72px; }

    /* ---------- TaskCard (screen-specific) ---------- */
    .card {
      background: var(--color-neutral-100); /* card background token */
      border: 1px solid var(--color-neutral-300);
      border-radius: 6px;
      padding: var(--space-2);
    }
    .card-head { display: flex; align-items: flex-start; gap: var(--space-2); }
    .card-title {
      margin: 0 0 var(--space-2);
      font-size: var(--font-body-size); /* body type: card titles */
      font-weight: var(--font-body-weight);
      color: var(--color-neutral-900);
    }
    .grip {
      margin-left: auto;
      color: var(--color-neutral-700);
      font-size: var(--font-caption-size);
      cursor: grab;
    }
    .card-meta {
      display: flex;
      align-items: center;
      gap: var(--space-2);
      flex-wrap: wrap;
    }
    .chip {
      display: inline-flex;
      align-items: center;
      padding: var(--space-1) var(--space-2); /* tight chip padding */
      border: 1px solid var(--color-neutral-300);
      border-radius: 999px;
      color: var(--color-neutral-700);
      font-size: var(--font-caption-size);
      font-weight: var(--font-caption-weight);
    }
    .chip-overdue { /* warning-colored when the calendar date is past */
      background: var(--color-warning);
      border-color: var(--color-warning);
      color: var(--color-neutral-900);
      font-weight: 600;
    }

    /* "Move to…" — the WCAG 2.1 AA keyboard alternative to drag-and-drop */
    .move-btn {
      margin-left: auto;
      padding: var(--space-1) var(--space-2);
      border: 1px solid var(--color-neutral-300);
      border-radius: 6px;
      background: var(--color-neutral-50);
      color: var(--color-neutral-700);
      font-family: var(--font-sans);
      font-size: var(--font-caption-size);
      font-weight: var(--font-caption-weight);
      cursor: pointer;
    }
    .menu {
      margin-top: var(--space-2);
      max-width: max-content;
      border: 1px solid var(--color-neutral-300);
      border-radius: 6px;
      background: var(--color-neutral-50);
      overflow: hidden;
    }
    .menu-label {
      padding: var(--space-1) var(--space-2);
      border-bottom: 1px solid var(--color-neutral-300);
      color: var(--color-neutral-700);
      font-size: var(--font-caption-size);
    }
    .menu-item {
      padding: var(--space-1) var(--space-2);
      font-size: var(--font-caption-size);
      color: var(--color-neutral-900);
    }
    .menu-item.is-current { color: var(--color-neutral-700); }
    .menu-item.is-focused { background: var(--color-primary); color: var(--color-neutral-50); }

    /* ---------- Activity Feed drawer — collapsed by default ---------- */
    .rail {
      width: 40px;
      background: var(--color-neutral-100); /* drawer background token */
      border-left: 1px solid var(--color-neutral-300);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: var(--space-2);
      padding: var(--space-2) 0;
    }
    .rail-glyph { color: var(--color-neutral-700); font-size: var(--font-caption-size); }
    .rail-text {
      writing-mode: vertical-rl;
      color: var(--color-neutral-700);
      font-size: var(--font-caption-size);
      font-weight: var(--font-caption-weight);
      letter-spacing: 0.05em;
    }

    /* ---------- Loading skeletons (Section 2.5: match content layout) ---------- */
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    .skeleton {
      background: var(--color-neutral-300);
      border-radius: 4px;
      animation: pulse 1.5s ease-in-out infinite;
    }
    .sk-title { height: 14px; width: 75%; margin-bottom: var(--space-2); }
    .sk-title.short { width: 55%; }
    .sk-swatch { width: 14px; height: 14px; border-radius: 50%; }
    .sk-chip { width: 72px; height: 18px; border-radius: 999px; }
    .sk-move { width: 56px; height: 18px; margin-left: auto; border-radius: 6px; }
    .sk-project { display: inline-block; width: 140px; height: 18px; }

    /* ---------- EmptyState (shared component, default variant) ---------- */
    .empty {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: var(--space-2);
      margin: var(--space-4);
      padding: var(--space-6); /* centered, space-6 padding */
    }
    .empty h3 {
      margin: 0;
      font-size: var(--font-h2-size);
      font-weight: var(--font-h2-weight);
    }
    .empty p { margin: 0; color: var(--color-neutral-700); }

    /* ---------- ErrorBanner (shared component, region variant) ---------- */
    .error-banner {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      margin: var(--space-4) var(--space-4) 0;
      padding: var(--space-3) var(--space-4);
      background: var(--color-neutral-100);
      border: 1px solid var(--color-neutral-300);
      border-left: 4px solid var(--color-error); /* error accent border */
      border-radius: 6px;
    }
    .error-banner .msg { flex: 1; margin: 0; }
    .error-glyph { color: var(--color-error); font-weight: 600; }

    /* ---------- Responsive (Section 2.6): mobile < 640px stacks ---------- */
    @media (max-width: 639px) {
      .states-grid { grid-template-columns: 1fr; }
      .columns { grid-template-columns: 1fr; } /* board columns stack on mobile */
      .board { flex-direction: column; }
      .rail {
        width: auto;
        flex-direction: row;
        justify-content: center;
        border-left: 0;
        border-top: 1px solid var(--color-neutral-300);
        padding: var(--space-2);
      }
      .rail-text { writing-mode: horizontal-tb; }
    }
  </style>
</head>

<body>

  <!-- Reviewer header -->
  <header class="reviewer-header">
    <h1>T-031 · Project Board Mockup — TaskFlow</h1>
    <p class="sub">Route /projects/:projectId/board · Four states shown side-by-side: Default, Loading, Empty, Error · Static mockup for stakeholder visual approval — no interactivity, fully offline</p>
  </header>

  <!-- States grid: one labeled section per state -->
  <main class="states-grid">

    <!-- ================= 1. DEFAULT ================= -->
    <section class="state" aria-labelledby="state-default">
      <h2 id="state-default">Default</h2>
      <p class="state-note">Tasks loaded — three columns of TaskCards grouped by status; Activity Feed drawer collapsed by default. One card shows the "Move to…" menu (keyboard alternative to drag) statically open.</p>
      <div class="screen">
        <div class="shell-header">
          <span class="logo">TaskFlow</span>
          <span class="shell-sep" aria-hidden="true">·</span>
          <span class="shell-project">Website Relaunch</span>
          <span class="spacer"></span>
          <span class="badge" title="9d4f7a2e-6c1b-4e5a-8d3f-2b7c9a4e6f1d"><span class="swatch swatch-d" aria-hidden="true"></span>9d4f7a2e</span>
        </div>
        <div class="toolbar">
          <span class="project-name">Website Relaunch</span>
          <span class="filter" title="AssigneeFilter — options render as UserBadges">Assignee: All <span aria-hidden="true">⌄</span></span>
          <button class="btn btn-primary" type="button">+ New task</button>
          <span class="spacer"></span>
          <a class="link" href="#members">Members</a>
          <button class="btn btn-ghost" type="button" aria-pressed="false">Activity <span aria-hidden="true">◂</span></button>
        </div>
        <div class="board">
          <div class="board-main">
            <div class="columns">
              <div class="column">
                <div class="column-head"><h3>To Do</h3><span class="count">2</span></div>
                <div class="cards">
                  <article class="card">
                    <div class="card-head">
                      <p class="card-title">Write launch announcement blog post</p>
                      <span class="grip" title="Drag to another column" aria-hidden="true">⠿</span>
                    </div>
                    <div class="card-meta">
                      <span class="swatch sm swatch-a" role="img" title="Assignee a3f8c2d1-4b6e-4c2a-9e7f-1d5b8a3c6e9f" aria-label="Assignee a3f8c2d1"></span>
                      <span class="chip">Due 2026-07-24</span>
                      <button class="move-btn" type="button" title="Keyboard alternative to drag-and-drop">Move to…</button>
                    </div>
                  </article>
                  <article class="card">
                    <div class="card-head">
                      <p class="card-title">Compress hero images for the landing page</p>
                      <span class="grip" title="Drag to another column" aria-hidden="true">⠿</span>
                    </div>
                    <div class="card-meta">
                      <span class="badge-unassigned">Unassigned</span>
                      <span class="chip chip-overdue" title="Past due — warning-colored per the Design System">Due 2026-07-12</span>
                      <button class="move-btn" type="button" title="Keyboard alternative to drag-and-drop">Move to…</button>
                    </div>
                  </article>
                </div>
              </div>
              <div class="column">
                <div class="column-head"><h3>In Progress</h3><span class="count">1</span></div>
                <div class="cards">
                  <article class="card">
                    <div class="card-head">
                      <p class="card-title">Migrate blog posts to the new CMS</p>
                      <span class="grip" title="Drag to another column" aria-hidden="true">⠿</span>
                    </div>
                    <div class="card-meta">
                      <span class="swatch sm swatch-b" role="img" title="Assignee 5e2d9b7f-8c1a-4f3e-b6d2-7a9c4e1f8b3d" aria-label="Assignee 5e2d9b7f"></span>
                      <span class="chip">Due 2026-07-18</span>
                      <button class="move-btn" type="button" aria-expanded="true" title="Keyboard alternative to drag-and-drop">Move to…</button>
                    </div>
                    <div class="menu" role="menu" aria-label="Move to">
                      <div class="menu-label">Move to…</div>
                      <div class="menu-item" role="menuitem">To Do</div>
                      <div class="menu-item is-current" role="menuitem" aria-disabled="true">In Progress ✓</div>
                      <div class="menu-item is-focused" role="menuitem">Done</div>
                    </div>
                  </article>
                </div>
              </div>
              <div class="column">
                <div class="column-head"><h3>Done</h3><span class="count">1</span></div>
                <div class="cards">
                  <article class="card">
                    <div class="card-head">
                      <p class="card-title">Set up staging environment</p>
                      <span class="grip" title="Drag to another column" aria-hidden="true">⠿</span>
                    </div>
                    <div class="card-meta">
                      <span class="swatch sm swatch-c" role="img" title="Assignee c1b7e4a9-3d5f-4a8b-8e2c-9f6d1a7b4c8e" aria-label="Assignee c1b7e4a9"></span>
                      <button class="move-btn" type="button" title="Keyboard alternative to drag-and-drop">Move to…</button>
                    </div>
                  </article>
                </div>
              </div>
            </div>
          </div>
          <aside class="rail" title="Activity Feed drawer — collapsed by default; the Activity toggle opens it">
            <span class="rail-glyph" aria-hidden="true">◂</span>
            <span class="rail-text">Activity</span>
          </aside>
        </div>
      </div>
    </section>

    <!-- ================= 2. LOADING ================= -->
    <section class="state" aria-labelledby="state-loading">
      <h2 id="state-loading">Loading</h2>
      <p class="state-note">Board queries in flight — skeleton placeholders match the card layout (Section 2.5); drawer stays collapsed.</p>
      <div class="screen">
        <div class="shell-header">
          <span class="logo">TaskFlow</span>
          <span class="shell-sep" aria-hidden="true">·</span>
          <span class="shell-project">Website Relaunch</span>
          <span class="spacer"></span>
          <span class="badge" title="9d4f7a2e-6c1b-4e5a-8d3f-2b7c9a4e6f1d"><span class="swatch swatch-d" aria-hidden="true"></span>9d4f7a2e</span>
        </div>
        <div class="toolbar">
          <span class="skeleton sk-project" aria-hidden="true"></span>
          <span class="filter" title="AssigneeFilter — options render as UserBadges">Assignee: All <span aria-hidden="true">⌄</span></span>
          <button class="btn btn-primary" type="button">+ New task</button>
          <span class="spacer"></span>
          <a class="link" href="#members">Members</a>
          <button class="btn btn-ghost" type="button" aria-pressed="false">Activity <span aria-hidden="true">◂</span></button>
        </div>
        <div class="board">
          <div class="board-main" role="status">
            <p class="sr-only">Loading the board…</p>
            <div class="columns" aria-hidden="true">
              <div class="column">
                <div class="column-head"><h3>To Do</h3></div>
                <div class="cards">
                  <article class="card">
                    <div class="skeleton sk-title"></div>
                    <div class="card-meta">
                      <span class="skeleton sk-swatch"></span>
                      <span class="skeleton sk-chip"></span>
                      <span class="skeleton sk-move"></span>
                    </div>
                  </article>
                  <article class="card">
                    <div class="skeleton sk-title short"></div>
                    <div class="card-meta">
                      <span class="skeleton sk-swatch"></span>
                      <span class="skeleton sk-chip"></span>
                      <span class="skeleton sk-move"></span>
                    </div>
                  </article>
                </div>
              </div>
              <div class="column">
                <div class="column-head"><h3>In Progress</h3></div>
                <div class="cards">
                  <article class="card">
                    <div class="skeleton sk-title"></div>
                    <div class="card-meta">
                      <span class="skeleton sk-swatch"></span>
                      <span class="skeleton sk-chip"></span>
                      <span class="skeleton sk-move"></span>
                    </div>
                  </article>
                </div>
              </div>
              <div class="column">
                <div class="column-head"><h3>Done</h3></div>
                <div class="cards">
                  <article class="card">
                    <div class="skeleton sk-title short"></div>
                    <div class="card-meta">
                      <span class="skeleton sk-swatch"></span>
                      <span class="skeleton sk-move"></span>
                    </div>
                  </article>
                </div>
              </div>
            </div>
          </div>
          <aside class="rail" title="Activity Feed drawer — collapsed by default">
            <span class="rail-glyph" aria-hidden="true">◂</span>
            <span class="rail-text">Activity</span>
          </aside>
        </div>
      </div>
    </section>

    <!-- ================= 3. EMPTY ================= -->
    <section class="state" aria-labelledby="state-empty">
      <h2 id="state-empty">Empty</h2>
      <p class="state-note">Project has no tasks — board-wide EmptyState (heading + description + CTA, never blank); drawer collapsed with no activity yet.</p>
      <div class="screen">
        <div class="shell-header">
          <span class="logo">TaskFlow</span>
          <span class="shell-sep" aria-hidden="true">·</span>
          <span class="shell-project">Website Relaunch</span>
          <span class="spacer"></span>
          <span class="badge" title="9d4f7a2e-6c1b-4e5a-8d3f-2b7c9a4e6f1d"><span class="swatch swatch-d" aria-hidden="true"></span>9d4f7a2e</span>
        </div>
        <div class="toolbar">
          <span class="project-name">Website Relaunch</span>
          <span class="filter" title="AssigneeFilter — options render as UserBadges">Assignee: All <span aria-hidden="true">⌄</span></span>
          <button class="btn btn-primary" type="button">+ New task</button>
          <span class="spacer"></span>
          <a class="link" href="#members">Members</a>
          <button class="btn btn-ghost" type="button" aria-pressed="false">Activity <span aria-hidden="true">◂</span></button>
        </div>
        <div class="board">
          <div class="board-main">
            <div class="empty">
              <h3>No tasks yet</h3>
              <p>Create the project's first task to get the board moving.</p>
              <button class="btn btn-primary" type="button">New task</button>
            </div>
          </div>
          <aside class="rail" title="Activity Feed drawer — collapsed; no activity yet">
            <span class="rail-glyph" aria-hidden="true">◂</span>
            <span class="rail-text">Activity</span>
          </aside>
        </div>
      </div>
    </section>

    <!-- ================= 4. ERROR ================= -->
    <section class="state" aria-labelledby="state-error">
      <h2 id="state-error">Error</h2>
      <p class="state-note">Board query failed — ErrorBanner with retry above the columns (human-readable message, no raw error codes); drawer stays collapsed.</p>
      <div class="screen">
        <div class="shell-header">
          <span class="logo">TaskFlow</span>
          <span class="shell-sep" aria-hidden="true">·</span>
          <span class="shell-project">Website Relaunch</span>
          <span class="spacer"></span>
          <span class="badge" title="9d4f7a2e-6c1b-4e5a-8d3f-2b7c9a4e6f1d"><span class="swatch swatch-d" aria-hidden="true"></span>9d4f7a2e</span>
        </div>
        <div class="toolbar">
          <span class="project-name">Website Relaunch</span>
          <span class="filter" title="AssigneeFilter — options render as UserBadges">Assignee: All <span aria-hidden="true">⌄</span></span>
          <button class="btn btn-primary" type="button">+ New task</button>
          <span class="spacer"></span>
          <a class="link" href="#members">Members</a>
          <button class="btn btn-ghost" type="button" aria-pressed="false">Activity <span aria-hidden="true">◂</span></button>
        </div>
        <div class="board">
          <div class="board-main">
            <div class="error-banner" role="alert">
              <span class="error-glyph" aria-hidden="true">⚠</span>
              <p class="msg">We couldn't load the board. Check your connection and try again.</p>
              <button class="btn btn-primary" type="button">Retry</button>
            </div>
            <div class="columns">
              <div class="column">
                <div class="column-head"><h3>To Do</h3></div>
                <div class="cards is-empty"></div>
              </div>
              <div class="column">
                <div class="column-head"><h3>In Progress</h3></div>
                <div class="cards is-empty"></div>
              </div>
              <div class="column">
                <div class="column-head"><h3>Done</h3></div>
                <div class="cards is-empty"></div>
              </div>
            </div>
          </div>
          <aside class="rail" title="Activity Feed drawer — collapsed by default">
            <span class="rail-glyph" aria-hidden="true">◂</span>
            <span class="rail-text">Activity</span>
          </aside>
        </div>
      </div>
    </section>

  </main>

</body>
</html>
