# Judge Rubric — Project Board mockup for T-031 (mockup generation)

Score the candidate mockup 1-10 against these six dimensions. The reference output shows
one known-good mockup — use it as an anchor for what "good" looks like; the candidate
does not need to match it verbatim (markup structure, class names, sample content, and
exact CSS may all differ), judge substance.

1. **Layout fidelity.** The mockup reproduces the screen shard's Layout Sketch and
   Component Hierarchy: a BoardToolbar with project name, assignee filter, New task
   button, Members link, and Activity toggle; three status columns (To Do / In
   Progress / Done) of TaskCards; the Activity Feed drawer present and **collapsed by
   default**. TaskCards match the shard: title, assignee `UserBadge` (or the dashed
   "Unassigned" placeholder), and a due-date chip that is `warning`-colored when the
   date is past. Users are opaque-UUID badges — no names, emails, or avatars.
2. **Four states, side-by-side, each plausible.** Default, Loading, Empty, and Error
   all appear as distinct, labeled sections in one side-by-side grid — not just words
   somewhere on the page. Each follows the Design System state patterns: default with
   realistic sample cards; loading as skeleton placeholders matching the content
   layout; empty as an EmptyState (heading + description + CTA — never a blank
   region); error as an ErrorBanner with a human-readable message and a retry button
   — no raw error codes.
3. **Design-token fidelity.** Colors, typography, and spacing come from the Design
   System (index.md 2.1–2.3), declared as CSS custom properties with the published
   values (primary #2563EB, error #DC2626, warning #D97706, the neutral scale, 4px
   spacing base, the four type sizes) — not an invented palette. System font stack
   (the Design System declares no fonts). The `UserBadge`'s deterministic per-user
   swatch color is the one sanctioned exception to the token palette.
4. **Self-containment.** A single HTML file with all CSS embedded in `<style>`: no
   external URLs of any kind (CDN, web fonts, icon fonts, remote images), no
   `<link>`/`<script src>` tags, no JavaScript logic. It must render correctly
   offline from a double-click. Any external request is a serious deficiency, not a
   style nit.
5. **Semantic & accessible markup.** Real `<button>` elements for actions, landmark
   structure (header/main/section with headings), meaningful text alternatives where
   icons or swatches carry meaning (sr-only text, `title`, or aria labels), plausible
   text contrast on the chosen token colors, and the WCAG keyboard alternative to
   drag-and-drop — a visible "Move to…" affordance on cards — present.
6. **Scope.** The Project Board screen only, per its shard: no content from other
   screens (task detail panel body, member management), no invented features (search,
   labels, notifications, intra-column reordering), no functional behavior beyond a
   static prototype. Extra invention is penalized even when well-executed.

Scoring guide: 9-10 = accept as-is; 7-8 = minor revisions, structure sound;
5-6 = one dimension seriously deficient; below 5 = re-generate.
