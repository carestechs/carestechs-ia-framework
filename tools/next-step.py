#!/usr/bin/env python3
"""Derive pipeline position from repo artifacts and print the next legal step(s).

This is the deterministic transition function for the state machine described in
guides/orchestrator-integration.md: artifacts are the only state (plus the optional
per-work-item progress overlay), and this tool is the only sequencing authority.
An orchestrator — human, model, or script — runs it, executes exactly the step it
prints, runs the printed gate, commits, and runs it again. Sequencing is never a
judgment call; that is the point.

Usage:
    python next-step.py [--root .] [--wi FEAT-001] [--json]
    python next-step.py --wi FEAT-001 --mark T-012=blocked --note "awaiting AWS account"
    python next-step.py --root . --log-event step=planning wi=FEAT-001 task=T-004 \
                        event=accepted tokens=5312 model=sonnet

--log-event appends one well-formed line to metrics/events.ndjson (the schema in
guides/evaluation.md) and exits — the uniform way for ANY driver (human,
/orchestrate session, external runner) to record what a step consumed. `tokens`
is approximate by design: record the best figure your driver exposes (headless
JSON `usage`, a runner's accounting, or an estimate) rather than nothing.
Key aliases: wi->work_item, tokens->session_tokens, cost->cost_usd,
outcome->event. Required: step, event, wi. `ts` is stamped automatically.

Per-task state is derived from these sources, highest precedence first:
  1. tasks/<WI>-progress.json overlay — the orchestrator-owned state of the guide's
     section 6, in repo form. The ONLY writer is --mark (or a human editing JSON).
  2. tasks/<WI>-T-XXX-implementation-review.md verdict: approve => done, revise => needs-fix
     (guide section 2 verdict contract). Task IDs restart per task list, so per-task
     artifacts carry the owning work item; an unqualified tasks/T-XXX-... name is still
     honoured while no other task list declares that ID, and refused with a warning once
     one does (this rung outranks commits - a stray approve would skip the work).
  3. git log commit evidence: a commit subject referencing T-XXX whose type prefix is
     not plan/review/tasks/docs/close/chore counts as implementation evidence => implemented
     (exception: docs: DOES count for Documentation-type tasks - their natural prefix).
     Task IDs restart at T-001 in every task list, so when two task lists declare the
     same ID the subject must ALSO name the owning work item (feat(FEAT-002/T-001): ...)
     or it is not credited, with a warning saying so - crediting the wrong work item
     skips real work, while a missed credit only costs a redundant pass.
  4. plans/plan-<WI>-T-XXX-*.md exists => planned (same qualification rule).
  5. Nothing => pending.

Work-item-level position: tasks file missing => task-generation; task-list review
missing or verdict revise (and overlay has no "task-review": "accepted") => the
step-3 review loop; otherwise the per-task frontier; all tasks done => docs-update
then closure.

The tool is read-only except for --mark. It never runs gates or validators — it
prints the exact command; the orchestrator runs it and never trusts a session's
claim of success (guide section 1, rule 3). Task-block parsing mirrors
validate-tasks.py (the validator remains the schema gate; this tool parses
leniently and assumes the list is validator-clean). Ad-hoc task lists
(tasks/adhoc-*.md) are out of scope. Output is ASCII-only by design.

Exit code 0 on success (including "nothing to do"); 1 on usage or parse failure.
Python 3.8+, standard library only.
"""

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

# --- parsing contracts (mirrors validate-tasks.py / orchestrator-integration.md) ---

WI_ID_RE = re.compile(r"^(FEAT|BUG|IMP)-\d{1,4}")
TASK_HEADING_RE = re.compile(r"^#{2,4}\s+T-(\d{1,4})\s*:\s*(.+?)\s*$")
FIELD_RE = re.compile(r"^\*\*([A-Za-z /]+?):\*\*\s*(.*)$")
DEP_ID_RE = re.compile(r"T-\d{1,4}")
FILE_BULLET_RE = re.compile(
    r"^\s*[-*]\s*`?(?P<path>[^`\s]+)`?\s*(?P<new>\(new\))?\s*(?:[-–—]\s*(?P<desc>.*))?$"
)
# Verdict contract from guides/orchestrator-integration.md section 2, verbatim.
VERDICT_RE = re.compile(r"verdict[^a-z]*(approve|revise)", re.IGNORECASE)
# VERDICT_RE stays the published cross-tool contract (drivers match it), but it
# must be applied to the Verdict SECTION, never the whole file - see parse_verdict.
HEADING_RE = re.compile(r"^#{1,6}\s")
VERDICT_HEADING_RE = re.compile(r"^#{1,6}\s*\**\s*verdict\b\s*:?\s*\**", re.IGNORECASE)
VERDICT_WORD_RE = re.compile(r"\b(approve|revise)\b", re.IGNORECASE)
VERDICT_DECL_RE = re.compile(r"^[*_`\s]*verdict\b[^a-z]*(approve|revise)", re.IGNORECASE)
STATUS_TABLE_RE = re.compile(r"^\|\s*\*{0,2}Status\*{0,2}\s*\|\s*(.+?)\s*\|", re.IGNORECASE)
STATUS_LINE_RE = re.compile(r"^\*\*Status:?\*\*:?\s*(.+)$", re.IGNORECASE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

CLOSED_WI_STATUSES = {"completed", "resolved", "cancelled", "closed"}
# Guide section 6 per-task enum, plus "blocked" for external blockers.
OVERLAY_STATUSES = {
    "pending", "planned", "assigned", "in-progress", "implemented",
    "reviewed", "done", "blocked",
}
# Commit subjects whose type prefix is one of these are pipeline bookkeeping,
# not implementation evidence (guide section 4 commit conventions). "chore"
# added in 2.8.1: bookkeeping commits naming a task ID (park/mark/overlay
# edits) were counting as false implementation evidence - measured live, where
# a "chore(...): drop stale overlay ... T-001" commit re-triggered a re-review.
NON_IMPL_COMMIT_PREFIXES = ("plan", "review", "tasks", "docs", "close", "chore")

TODAY = datetime.date.today


def strip_code_fences(lines):
    fence = None
    for i, raw in enumerate(lines, 1):
        stripped = raw.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is None:
            yield i, raw


def read_text(path):
    return path.read_text(encoding="utf-8", errors="replace")


# --- discovery ---

def discover_work_items(root):
    items = []
    wi_dir = root / "docs" / "work-items"
    if not wi_dir.is_dir():
        return items
    for path in sorted(wi_dir.glob("*.md")):
        if path.name.startswith("TEMPLATE-"):
            continue
        m = WI_ID_RE.match(path.name)
        if not m:
            continue
        wi_id = m.group(0)
        text = read_text(path)
        status = "unknown"
        title = wi_id
        for _, raw in strip_code_fences(text.splitlines()):
            clean = HTML_COMMENT_RE.sub("", raw).strip()
            tm = STATUS_TABLE_RE.match(clean) or STATUS_LINE_RE.match(clean)
            if tm and status == "unknown":
                status = tm.group(1).strip().strip("*").strip()
            if raw.startswith("# ") and title == wi_id:
                title = raw.lstrip("# ").strip()
                title = re.sub(r"^(Feature Brief|Bug Report|Improvement Proposal)\s*:\s*",
                               "", title, flags=re.IGNORECASE)
                title = re.sub(rf"^{wi_id}\s*[—–-]+\s*", "", title)
        items.append({"id": wi_id, "path": path, "title": title, "status": status})
    return items


def parse_task_list(path):
    """Lenient task-block parse; validate-tasks.py is the real schema gate."""
    tasks = {}
    current = None
    current_field = None
    for _, raw in strip_code_fences(read_text(path).splitlines()):
        heading = TASK_HEADING_RE.match(raw)
        if heading:
            tid = int(heading.group(1))
            current = {
                "id": tid, "title": heading.group(2), "type": "", "workflow": "",
                "complexity": "", "deps": [], "files": [],
            }
            tasks[tid] = current
            current_field = None
            continue
        if raw.startswith("#"):
            current = None
            current_field = None
            continue
        if current is None:
            continue
        field = FIELD_RE.match(raw.strip())
        if field:
            name = field.group(1).strip()
            value = field.group(2).strip().strip("`").strip()
            current_field = name
            if name == "Type":
                current["type"] = value
            elif name == "Workflow":
                current["workflow"] = value
            elif name == "Complexity":
                current["complexity"] = HTML_COMMENT_RE.sub("", value).strip()
            elif name == "Dependencies":
                if value.lower() not in ("none", "none."):
                    current["deps"] = [int(d[2:]) for d in DEP_ID_RE.findall(value)]
            continue
        if current_field == "Files to Modify/Create" and raw.strip():
            m = FILE_BULLET_RE.match(raw)
            if m and m.group("path") and set(m.group("path")) - set("-*_"):
                current["files"].append(m.group("path"))
    return tasks


def glob_by_task_id(directory, pattern, id_re):
    """Map task id (int) -> [(owner_wi_or_None, path)] for task artifacts.

    Task IDs restart at T-001 in every task list, so a globally-named artifact
    like plans/plan-T-001-*.md or tasks/T-001-implementation-review.md does not
    say WHOSE T-001 it is. Artifacts may carry the owning work item in the name
    (tasks/FEAT-002-T-001-implementation-review.md, plans/plan-FEAT-002-T-001-*.md);
    `id_re` captures that optional prefix as group "wi". Resolution happens in
    pick_artifact() - this only collects candidates."""
    result = {}
    if not directory.is_dir():
        return result
    for path in sorted(directory.glob(pattern)):
        m = id_re.match(path.name)
        if not m:
            continue
        owner = m.group("wi")  # None when the name carries no work item
        result.setdefault(int(m.group("tid")), []).append((owner, path))
    return result


def pick_artifact(entries, wi_id, tid, others, warnings, kind):
    """Choose this work item's artifact from same-ID candidates.

    Same fail-safe as commit evidence (2.8.4): a work-item-qualified name always
    wins; an unqualified name is trusted only when no OTHER task list declares
    this ID. Crediting another work item's review file is worse than crediting
    its commit - the review rung outranks commits, so a stray approve marks a
    task done and skips implementation AND review."""
    if not entries:
        return None
    owned = [path for owner, path in entries if owner == wi_id]
    if owned:
        return owned[0]
    unqualified = [path for owner, path in entries if owner is None]
    if unqualified and not others:
        return unqualified[0]
    if unqualified and warnings is not None:
        warnings.append(
            f"T-{tid:03d}: {kind} '{unqualified[0].name}' is not work-item-qualified and "
            f"T-{tid:03d} is also declared by {', '.join(others)} - NOT used as evidence for "
            f"{wi_id} (crediting another work item's {kind} would skip real work). Rename it to "
            f"include the owning work item, or record the state with --mark.")
    return None


def parse_verdict(path):
    """Verdict of a review file, read from its '## Verdict' section only.

    The published contract (guide section 2) is a '## Verdict' heading whose
    section body is approve or revise. Applying VERDICT_RE to the WHOLE file
    takes the first match anywhere, and a re-review's natural opening sentence
    names the round it supersedes - "This file overwrites the previous (verdict
    `revise`) review" - where [^a-z]* happily spans the backtick. Measured live:
    a re-review that said approve was read as revise, and the orchestrator was
    pointed at finished work. Silent, and invisible to the validators, because
    nothing about the artifact is wrong.

    Resolution order: the Verdict section; then a line that itself DECLARES the
    verdict (**Verdict:** approve); then None. Quoted lines and fenced blocks
    are never authoritative - they are someone else's words."""
    lines = [raw for _, raw in strip_code_fences(read_text(path).splitlines())]

    # 1. The Verdict section: the heading's own tail, then its body up to the
    #    next heading of any level.
    for i, raw in enumerate(lines):
        if not VERDICT_HEADING_RE.match(raw):
            continue
        tail = VERDICT_HEADING_RE.sub("", raw, count=1)
        m = VERDICT_WORD_RE.search(tail)
        if m:
            return m.group(1).lower()
        for body in lines[i + 1:]:
            if HEADING_RE.match(body):
                break
            if body.lstrip().startswith(">"):
                continue
            m = VERDICT_WORD_RE.search(body)
            if m:
                return m.group(1).lower()

    # 2. No usable section: accept a line that declares the verdict itself.
    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith(">"):
            continue
        m = VERDICT_DECL_RE.match(stripped)
        if m:
            return m.group(1).lower()
    return None


def load_overlay(root, wi_id):
    path = root / "tasks" / f"{wi_id}-progress.json"
    if not path.is_file():
        return {}, path
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        print(f"{path}: ERROR: overlay is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)
    return data, path


def git_commit_subjects(root):
    """All commit subjects, or None when the root is not a usable git repo."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "log", "--format=%s"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.splitlines()


def last_commit_hash(root, rel_path):
    """Hash of the newest commit touching rel_path, or None."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "log", "-1", "--format=%H", "--", rel_path],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def commit_subjects_since(root, since_hash, rel_path=None):
    """Subjects of commits after since_hash (exclusive), optionally path-limited;
    None on git failure."""
    cmd = ["git", "-C", str(root), "log", "--format=%s", f"{since_hash}..HEAD"]
    if rel_path:
        cmd += ["--", rel_path]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.splitlines()


def impl_commit_match(subjects, tid, task_type="", wi_id=None, require_wi=False):
    """Commit evidence for one task. Returns (credited, unqualified_seen).

    Type-aware (2.8.2, org-review S-2026-08-05-11): for a Documentation-type
    task, `docs:` IS the natural implementation prefix - excluding it made doc
    tasks whose sessions self-commit invisible to the evidence ladder. Every
    other type keeps the full exclusion list.

    Work-item-aware (2.8.4): task IDs restart at T-001 in every task list, so
    `feat(T-001): ...` from one work item was credited to another work item's
    T-001 - a FALSE POSITIVE, which silently skips implementation instead of
    looping (reported from live use: a FEAT-002 commit marked all five BUG-001
    tasks implemented). When the same task ID exists in more than one task
    list, `require_wi` demands the subject also name the owning work item;
    otherwise the commit is not credited and `unqualified_seen` reports that a
    candidate was skipped, so the caller can say why."""
    excluded = NON_IMPL_COMMIT_PREFIXES
    if task_type == "Documentation":
        excluded = tuple(p for p in excluded if p != "docs")
    tag_re = re.compile(rf"\bT-{tid:03d}\b")
    wi_re = re.compile(rf"\b{re.escape(wi_id)}\b") if wi_id else None
    credited = False
    skipped = []
    for subject in subjects:
        if not tag_re.search(subject):
            continue
        prefix = subject.split(":", 1)[0].strip().lower()
        if any(prefix.startswith(p) for p in excluded):
            continue
        if require_wi and not (wi_re and wi_re.search(subject)):
            skipped.append(subject)
            continue
        credited = True
    return credited, skipped


def has_impl_commit(subjects, tid, task_type="", wi_id=None, require_wi=False):
    return impl_commit_match(subjects, tid, task_type, wi_id, require_wi)[0]


def task_id_owners(root):
    """tid -> sorted work-item IDs whose task list declares it.

    An ID owned by more than one work item has ambiguous commit evidence: task
    IDs restart at T-001 in every list. Every `tasks/*-tasks.md` counts, whether
    or not its work item is closed - a completed work item's commits stay in the
    log forever, which is exactly what made the reported collision possible."""
    owners = {}
    tasks_dir = root / "tasks"
    if not tasks_dir.is_dir():
        return owners
    for path in sorted(tasks_dir.glob("*-tasks.md")):
        m = WI_ID_RE.match(path.name)
        if not m:
            continue
        owner = m.group(0)
        for tid in parse_task_list(path):
            owners.setdefault(tid, set()).add(owner)
    return {tid: sorted(names) for tid, names in owners.items()}


def commit_ambiguity_warning(tag, wi_id, others, skipped):
    """Explain a skipped commit without handing over a dangerous remedy.

    When the skipped subject names one of the OTHER work items that declares
    this task ID, the commit is somebody else's work and the honest advice is
    "nothing to do here". Suggesting --mark in that case would talk the
    operator (or an orchestrator session) into re-creating by hand exactly the
    cross-work-item false positive this check exists to prevent."""
    also = ", ".join(others) if others else "another work item"
    claimed = sorted({o for o in others for s in skipped
                      if re.search(rf"\b{re.escape(o)}\b", s)})
    base = (f"{tag}: commit(s) mentioning {tag} were NOT credited to {wi_id} - "
            f"{tag} is also declared by {also}, so an unqualified subject is "
            f"ambiguous (crediting the wrong work item skips real work).")
    if claimed:
        return (base + f" The commit(s) name {', '.join(claimed)}, so this is that "
                f"work item's task, not {wi_id}'s - no action needed here.")
    return (base + f" If this IS {wi_id}'s work, qualify the subject "
            f"(e.g. 'feat({wi_id}/{tag}): ...'); only use "
            f"--mark {tag}=implemented if you have verified it by hand.")


# --- state derivation ---

def derive_task_state(task, overlay, reviews, subjects, plans,
                      wi_id=None, id_owners=None, warnings=None):
    """Returns (state, evidence). States: pending planned implemented needs-fix
    done blocked assigned in-progress."""
    tid = task["id"]
    tag = f"T-{tid:03d}"
    entry = overlay.get(tag)
    if isinstance(entry, dict) and entry.get("status") in OVERLAY_STATUSES:
        status = entry["status"]
        note = entry.get("note", "")
        evidence = f"overlay ({entry.get('updated', 'undated')})" + (f": {note}" if note else "")
        if status in ("done", "reviewed"):
            return "done", evidence
        if status == "blocked":
            return "blocked", evidence
        if status in ("assigned", "in-progress"):
            return status, evidence
        return {"pending": "pending", "planned": "planned",
                "implemented": "implemented"}[status], evidence
    owners = (id_owners or {}).get(tid) or []
    others = [o for o in owners if o != wi_id]
    review_path = pick_artifact(reviews.get(tid), wi_id, tid, others,
                                warnings, "implementation review")
    if review_path is not None:
        verdict = parse_verdict(review_path)
        if verdict == "approve":
            return "done", f"review approve ({review_path.name})"
        if verdict == "revise":
            return "needs-fix", f"review revise ({review_path.name})"
        if warnings is not None:
            warnings.append(
                f"{tag}: {review_path.name} exists but no verdict could be read from a "
                f"'## Verdict' section (quoted and fenced text is never authoritative) - "
                f"the review is not counted as evidence. Add the section per the verdict "
                f"contract, or record the state with --mark.")
    if subjects is not None:
        credited, skipped = impl_commit_match(
            subjects, tid, task.get("type", ""), wi_id, bool(others))
        if credited:
            return "implemented", "implementation commit(s) in git log"
        if skipped and warnings is not None:
            warnings.append(commit_ambiguity_warning(tag, wi_id, others, skipped))
    plan_path = pick_artifact(plans.get(tid), wi_id, tid, others, warnings, "plan")
    if plan_path is not None:
        return "planned", f"plan exists ({plan_path.name})"
    return "pending", "no artifacts"


COMPLETE_STATES = {"done"}


def step(name, prompt, gate, fresh=False, task=None, note=""):
    return {"step": name, "task": task, "fresh": fresh,
            "prompt": prompt, "gate": gate, "note": note}


def compute_work_item(root, wi, subjects, id_owners=None):
    wi_id = wi["id"]
    tasks_path = root / "tasks" / f"{wi_id}-tasks.md"
    review_path = root / "tasks" / f"{wi_id}-review.md"
    overlay, overlay_path = load_overlay(root, wi_id)
    result = {"id": wi_id, "title": wi["title"], "status": wi["status"],
              "position": "", "tasks": [], "next_steps": [], "warnings": []}

    status_words = wi["status"].lower().split()
    status_closed = bool(status_words) and status_words[0].rstrip(".,;") in CLOSED_WI_STATUSES
    if status_closed and not tasks_path.is_file():
        result["position"] = "closed"
        return result

    validate_cmd = (f"python .ai-framework/tools/validate-tasks.py tasks/{wi_id}-tasks.md "
                    f"--work-item docs/work-items/{wi['path'].name} --root .")

    # Step 2 — task generation
    if not tasks_path.is_file():
        result["position"] = "step 2: task list not yet generated"
        result["next_steps"].append(step(
            "task-generation",
            f"Read CLAUDE.md. Generate tasks for {wi_id} per the routing table row for its "
            f"work-item type. Write tasks/{wi_id}-tasks.md and run the validator "
            f"self-check before finishing.",
            validate_cmd))
        return result

    # Step 3 — task-list review loop
    review_accepted = overlay.get("task-review") == "accepted"
    verdict = parse_verdict(review_path) if review_path.is_file() else None
    if not review_accepted and verdict != "approve":
        mark_cmd = (f"python .ai-framework/tools/next-step.py --root . --wi {wi_id} "
                    f"--mark task-review=accepted")
        if verdict is None:
            result["position"] = "step 3: task list awaiting fresh review"
            result["next_steps"].append(step(
                "task-review",
                f"FRESH REVIEW - you did not generate this. Read CLAUDE.md. Review "
                f"tasks/{wi_id}-tasks.md per the routing row 'Task list review'. Run both "
                f"validators first and treat their output as ground truth. Write "
                f"tasks/{wi_id}-review.md.",
                f"parse '## Verdict' in tasks/{wi_id}-review.md (approve => accepted)",
                fresh=True,
                note="Skip rule: S-complexity adhoc lists only; if skipped, record it: " + mark_cmd))
            return result
        # Re-review detection (measured gap from the /orchestrate live test): once
        # a revision lands, the stale revise verdict must not keep emitting
        # revisions. Mechanical signal: commits touching the task list AFTER the
        # newest commit touching the review file. Commits are the step boundary
        # (guide rule 2) - uncommitted edits deliberately do not count.
        if subjects is not None:
            review_head = last_commit_hash(root, f"tasks/{wi_id}-review.md")
            if review_head:
                later = commit_subjects_since(root, review_head,
                                              f"tasks/{wi_id}-tasks.md")
                if later:
                    result["position"] = ("step 3: revision applied - task list "
                                          "awaiting fresh re-review")
                    result["next_steps"].append(step(
                        "task-review",
                        f"FRESH REVIEW - you did not generate or revise this. Read "
                        f"CLAUDE.md. Re-review tasks/{wi_id}-tasks.md per the routing "
                        f"row 'Task list review'; the previous review's required "
                        f"changes have been applied - verify them and review the "
                        f"whole list. Run both validators first and treat their "
                        f"output as ground truth. OVERWRITE tasks/{wi_id}-review.md "
                        f"with your review.",
                        f"parse '## Verdict' in tasks/{wi_id}-review.md "
                        f"(approve => accepted)",
                        fresh=True,
                        note="Detected mechanically: the task list was committed "
                             "after the current review file. Cap 2 revise loops, "
                             "then human. If already accepted, record it: " + mark_cmd))
                    return result
        result["position"] = "step 3: task-list review verdict is 'revise'"
        result["next_steps"].append(step(
            "task-list-revision",
            f"Apply every required change from tasks/{wi_id}-review.md to "
            f"tasks/{wi_id}-tasks.md, then update the Summary and the Acceptance "
            f"Criteria Coverage table so they stay consistent with what you changed. "
            f"Touch nothing else.",
            validate_cmd + "  (then re-review; cap 2 loops, then human)",
            note="If the changes were already applied and accepted, record it: " + mark_cmd))
        return result

    # Steps 4-8 — per-task frontier
    tasks = parse_task_list(tasks_path)
    if not tasks:
        result["position"] = "step 2: tasks file exists but contains no task blocks"
        result["warnings"].append(f"{tasks_path.name}: no task blocks parsed - run the validator")
        return result

    plans = glob_by_task_id(
        root / "plans", "plan-*.md",
        re.compile(r"plan-(?:(?P<wi>(?:FEAT|BUG|IMP)-\d{1,4})-)?T-(?P<tid>\d{1,4})-"))
    reviews = glob_by_task_id(
        root / "tasks", "*implementation-review.md",
        re.compile(r"(?:(?P<wi>(?:FEAT|BUG|IMP)-\d{1,4})-)?T-(?P<tid>\d{1,4})-implementation-review"))
    mockups = glob_by_task_id(
        root / "mockups", "*.html",
        re.compile(r"(?:(?P<wi>(?:FEAT|BUG|IMP)-\d{1,4})-)?T-(?P<tid>\d{1,4})[-.]"))

    states = {}
    for tid, task in sorted(tasks.items()):
        state, evidence = derive_task_state(
            task, overlay, reviews, subjects, plans,
            wi_id, id_owners, result["warnings"])
        states[tid] = state
        result["tasks"].append({
            "id": f"T-{tid:03d}", "title": task["title"], "type": task["type"],
            "complexity": task["complexity"], "state": state, "evidence": evidence,
            "deps": [f"T-{d:03d}" for d in task["deps"]],
        })
        # 2.8.1: a trusted overlay that contradicts review evidence gets a loud
        # warning (measured live: an overlay 'implemented' written before a
        # revise verdict silently masked the fix loop). Overlay still wins -
        # it is the orchestrator's state by design - but never silently.
        ov_review = pick_artifact(
            reviews.get(tid), wi_id, tid,
            [o for o in ((id_owners or {}).get(tid) or []) if o != wi_id],
            None, "implementation review")
        if evidence.startswith("overlay") and ov_review is not None \
                and state in ("done", "implemented"):
            verdict = parse_verdict(ov_review)
            if verdict == "revise":
                result["warnings"].append(
                    f"T-{tid:03d}: overlay says '{state}' but {ov_review.name} "
                    f"verdict is 'revise' - overlay wins by design; clear the entry "
                    f"if it is stale, or run a fresh re-review to refresh the "
                    f"verdict if the overlay is right")

    def deps_met(task):
        return all(states.get(d) in COMPLETE_STATES for d in task["deps"])

    # A closed Status is only trusted when the task evidence agrees. A docs task
    # that flips the Status early must not short-circuit the remaining tasks or
    # the formal closure step (learned from a live run: the docs task set
    # Status=Completed and the strict closure gate never ran).
    open_ids = [f"T-{tid:03d}" for tid, s in sorted(states.items())
                if s not in COMPLETE_STATES]
    if status_closed:
        if not open_ids:
            if subjects is not None and not any(f"close({wi_id})" in s for s in subjects):
                result["position"] = ("step 10: Status already flipped - formal closure "
                                      "incomplete (no close commit found)")
                result["next_steps"].append(step(
                    "closure",
                    f"Closure checklist for {wi_id}: the work item Status is already set - "
                    f"complete the rest: verify traceability, add a dated repo-level "
                    f"CHANGELOG.md entry for the shipped scope (create the file on first "
                    f"release), run the strict spec gate and the metrics report, final "
                    f"commit 'close({wi_id})'.",
                    "python .ai-framework/tools/validate-specs.py --root . --strict"))
                return result
            result["position"] = "closed"
            return result
        result["warnings"].append(
            f"work-item Status is '{wi['status']}' but {len(open_ids)} task(s) lack "
            f"completion evidence ({', '.join(open_ids[:5])}) - a docs task may have "
            f"flipped the Status early (the closure step owns that flip); continuing "
            f"the frontier")

    mark_hint = (f"python .ai-framework/tools/next-step.py --root . --wi {wi_id} "
                 f"--mark T-XXX=done")
    frontier_tids = []

    # Priority order: finish in-flight work before starting new work.
    for tid, task in sorted(tasks.items()):
        tag = f"T-{tid:03d}"
        slug = "<slug>"
        # Name the plan that actually exists (qualified or legacy); fall back to
        # the qualified placeholder so a session writing one gets the right name.
        _plan = pick_artifact(
            plans.get(tid), wi_id, tid,
            [o for o in ((id_owners or {}).get(tid) or []) if o != wi_id],
            None, "plan")
        plan_hint = (f"plans/{_plan.name}" if _plan
                     else f"plans/plan-{wi_id}-{tag}-{slug}.md")
        state = states[tid]
        if state == "needs-fix":
            # Same re-review detection as the task-list loop: fix commits that
            # landed after the revise verdict mean the next step is a fresh
            # re-review, not another fix.
            rereview_due = False
            if subjects is not None:
                rr_others = [o for o in ((id_owners or {}).get(tid) or [])
                             if o != wi_id]
                # Resolve the SAME file the state came from: a hardcoded
                # tasks/T-XXX-... pathspec finds nothing once the review is
                # work-item-qualified, and re-review would never trigger.
                rr_path = pick_artifact(reviews.get(tid), wi_id, tid, rr_others,
                                        None, "implementation review")
                review_head = last_commit_hash(
                    root, rr_path.relative_to(root).as_posix()) if rr_path else None
                if review_head:
                    later = commit_subjects_since(root, review_head)
                    rr_credited, rr_skipped = impl_commit_match(
                        later, tid, task.get("type", ""), wi_id, bool(rr_others))
                    rereview_due = bool(later) and rr_credited
                    if rr_skipped and not rr_credited:
                        # Silence here is worse than elsewhere: an applied fix
                        # that never triggers its re-review just keeps printing
                        # "implementation-fix" forever.
                        result["warnings"].append(commit_ambiguity_warning(
                            tag, wi_id, rr_others, rr_skipped)
                            + " Until then the re-review will not trigger.")
            if rereview_due:
                result["next_steps"].append(step(
                    "implementation-review",
                    f"FRESH REVIEW - you did not implement or fix this. Read CLAUDE.md. "
                    f"Re-review the implementation of {tag} per the routing row "
                    f"'Implementation review', focusing on whether the previous review's "
                    f"required changes were properly applied. Gather evidence first (run "
                    f"tests, linters, validate-specs) and treat it as ground truth. "
                    f"OVERWRITE tasks/{wi_id}-{tag}-implementation-review.md with your review.",
                    f"parse '## Verdict' in tasks/{wi_id}-{tag}-implementation-review.md",
                    fresh=True, task=tag,
                    note="Detected mechanically: fix commits referencing " + tag +
                         " landed after the current revise verdict. If already "
                         "accepted, record it: " + mark_hint.replace("T-XXX", tag)))
            else:
                result["next_steps"].append(step(
                    "implementation-fix",
                    f"Apply every required change from tasks/{wi_id}-{tag}-implementation-review.md "
                    f"for {tag}, then request re-review.",
                    f"tests green, then fresh re-review of {tag} (cap 2 loops, then human)",
                    task=tag,
                    note="If the fixes were already applied and accepted, record it: "
                         + mark_hint.replace("T-XXX", tag)))
        elif state == "implemented":
            if task["complexity"] == "S":
                result["next_steps"].append(step(
                    "task-completion",
                    f"{tag} is S-complexity: implementation review is optional (guide step 7 "
                    f"skip rule). Confirm tests are green and mark it done.",
                    mark_hint.replace("T-XXX", tag), task=tag))
            else:
                result["next_steps"].append(step(
                    "implementation-review",
                    f"FRESH REVIEW - you did not implement this. Read CLAUDE.md. Review the "
                    f"implementation of {tag} per the routing row 'Implementation review'. "
                    f"Gather evidence first (run tests, linters, validate-specs) and treat it "
                    f"as ground truth. Write tasks/{wi_id}-{tag}-implementation-review.md.",
                    f"parse '## Verdict' in tasks/{wi_id}-{tag}-implementation-review.md",
                    fresh=True, task=tag))
            frontier_tids.append(tid)
        elif state in ("assigned", "in-progress"):
            result["next_steps"].append(step(
                "implementation",
                f"Read CLAUDE.md. Implement {tag} from tasks/{wi_id}-tasks.md following "
                f"{plan_hint} exactly; document any deviation. Run the test "
                f"suite and validate-specs before finishing.",
                "tests green; validate-specs clean when shards were touched", task=tag))
            frontier_tids.append(tid)
        elif state == "planned" and deps_met(task):
            result["next_steps"].append(step(
                "implementation",
                f"Read CLAUDE.md. Implement {tag} from tasks/{wi_id}-tasks.md following "
                f"{plan_hint} exactly; document any deviation. Run the test "
                f"suite and validate-specs before finishing.",
                "tests green; validate-specs clean when shards were touched", task=tag))
            frontier_tids.append(tid)

    for tid, task in sorted(tasks.items()):
        tag = f"T-{tid:03d}"
        if states[tid] != "pending" or not deps_met(task):
            continue
        mockup_path = None
        if task["workflow"] == "mockup-first":
            mockup_others = [o for o in ((id_owners or {}).get(tid) or [])
                             if o != wi_id]
            mockup_path = pick_artifact(mockups.get(tid), wi_id, tid, mockup_others,
                                        result["warnings"], "mockup")
        if task["workflow"] == "mockup-first" and mockup_path is None:
            result["next_steps"].append(step(
                "mockup",
                f"Read CLAUDE.md. Generate the HTML mockup for {tag} per the routing row "
                f"'UI mockup'. Write mockups/{wi_id}-{tag}-<screen>.html.",
                "human approval of the mockup (workflow gate - required before planning)",
                task=tag))
        else:
            note = ("Workflow gate: verify investigation findings are recorded before planning"
                    if task["workflow"] == "investigation-first" else "")
            result["next_steps"].append(step(
                "planning",
                f"Read CLAUDE.md. Create the implementation plan for {tag} from "
                f"tasks/{wi_id}-tasks.md per the routing row 'Task implementation plan'. "
                f"Write plans/plan-{wi_id}-{tag}-<slug>.md within the plan budget.",
                f"plan exists, <= ~150 lines, references {tag}", task=tag, note=note))
        frontier_tids.append(tid)

    # Parallel-scheduling conflicts among frontier tasks (guide step 5).
    for i, a in enumerate(frontier_tids):
        for b in frontier_tids[i + 1:]:
            shared = set(tasks[a]["files"]) & set(tasks[b]["files"])
            if shared:
                result["warnings"].append(
                    f"T-{a:03d} and T-{b:03d} share files ({', '.join(sorted(shared)[:3])}"
                    f"{', ...' if len(shared) > 3 else ''}) - do not run them concurrently")

    blocked = [f"T-{tid:03d}" for tid, s in states.items() if s == "blocked"]
    open_states = {tid: s for tid, s in states.items() if s not in COMPLETE_STATES}

    if not open_states:
        result["position"] = "step 10: all tasks done - brief closure"
        result["next_steps"].append(step(
            "closure",
            f"Closure checklist for {wi_id}: set the work item Status to Completed/Resolved "
            f"(+ date), verify traceability, add a dated repo-level CHANGELOG.md entry for "
            f"the shipped scope (create the file on first release), run the strict spec gate "
            f"and the metrics report, final commit 'close({wi_id})'.",
            "python .ai-framework/tools/validate-specs.py --root . --strict"))
    elif not result["next_steps"]:
        if blocked and len(open_states) == len(blocked):
            result["position"] = "blocked: every remaining task is externally blocked"
        else:
            result["position"] = ("stalled: open tasks exist but none is actionable "
                                  "(unmet dependencies) - check for dependency deadlock")
            result["warnings"].append("no actionable task in the frontier; run validate-tasks "
                                      "to check the dependency DAG")
    else:
        done = len(states) - len(open_states)
        result["position"] = (f"steps 4-8: task frontier ({done}/{len(states)} done)")
        doc_open = [tid for tid, s in open_states.items()
                    if tasks[tid]["type"] == "Documentation"]
        if doc_open and len(open_states) == len(doc_open) + len(blocked):
            result["position"] += " - only Documentation (+blocked) remains: step 9 docs-update"
    if blocked:
        result["warnings"].append("blocked: " + ", ".join(sorted(blocked)))
    return result


# --- output ---

def render_human(report):
    lines = []
    for wi in report["work_items"]:
        lines.append(f"{wi['id']} - {wi['title']}")
        lines.append(f"  work-item status: {wi['status']}")
        lines.append(f"  position: {wi['position']}")
        if wi["tasks"]:
            done = sum(1 for t in wi["tasks"] if t["state"] == "done")
            lines.append(f"  tasks ({done}/{len(wi['tasks'])} done):")
            for t in wi["tasks"]:
                head = f"{t['id']} [{t['complexity'] or '?'}]"
                lines.append(f"    {head:<12} {t['state']:<12} {t['evidence']}")
        for w in wi["warnings"]:
            lines.append(f"  WARNING: {w}")
        if wi["next_steps"]:
            lines.append("  next steps (in priority order - execute the first):")
            for i, s in enumerate(wi["next_steps"], 1):
                head = f"    {i}. {s['step']}"
                if s["task"]:
                    head += f" ({s['task']})"
                if s["fresh"]:
                    head += "  [FRESH SESSION]"
                lines.append(head)
                lines.append(f"       prompt: {s['prompt']}")
                lines.append(f"       gate:   {s['gate']}")
                if s["note"]:
                    lines.append(f"       note:   {s['note']}")
        lines.append("")
    if report["closed"]:
        lines.append("closed work items: " + ", ".join(report["closed"]))
    if report["notes"]:
        for n in report["notes"]:
            lines.append(f"note: {n}")
    return "\n".join(lines)


# --- event logging ---

EVENT_VALUES = {"started", "artifact_committed", "accepted", "revised", "completed"}
EVENT_KEY_ALIASES = {"wi": "work_item", "tokens": "session_tokens",
                     "cost": "cost_usd", "outcome": "event"}


def do_log_event(root, pairs):
    entry = {}
    for pair in pairs:
        if "=" not in pair:
            print(f"ERROR: --log-event expects KEY=VALUE, got '{pair}'", file=sys.stderr)
            return 1
        key, _, value = pair.partition("=")
        key = EVENT_KEY_ALIASES.get(key.strip(), key.strip())
        entry[key] = value.strip()
    missing = [k for k in ("step", "event", "work_item") if not entry.get(k)]
    if missing:
        print(f"ERROR: --log-event requires {', '.join(missing)}", file=sys.stderr)
        return 1
    if entry["event"] not in EVENT_VALUES:
        print(f"ERROR: event '{entry['event']}' not in {sorted(EVENT_VALUES)}",
              file=sys.stderr)
        return 1
    for key, cast in (("session_tokens", int), ("cost_usd", float)):
        if key in entry:
            try:
                entry[key] = cast(entry[key])
            except ValueError:
                print(f"ERROR: {key} must be a number, got '{entry[key]}'", file=sys.stderr)
                return 1
    entry["ts"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path = root / "metrics" / "events.ndjson"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"{path}: logged {entry['step']}/{entry['event']} for {entry['work_item']}")
    return 0


# --- mark ---

def do_mark(root, wi_id, marks, note):
    overlay, path = load_overlay(root, wi_id)
    stamp = TODAY().isoformat()
    for target, value in marks:
        if target == "task-review":
            if value != "accepted":
                print(f"ERROR: task-review only accepts 'accepted', got '{value}'",
                      file=sys.stderr)
                return 1
            overlay["task-review"] = "accepted"
        else:
            if not re.fullmatch(r"T-\d{1,4}", target):
                print(f"ERROR: mark target must be T-XXX or task-review, got '{target}'",
                      file=sys.stderr)
                return 1
            if value not in OVERLAY_STATUSES:
                print(f"ERROR: status '{value}' not in {sorted(OVERLAY_STATUSES)}",
                      file=sys.stderr)
                return 1
            tid = int(target.split("-")[1])
            entry = {"status": value, "updated": stamp}
            if note:
                entry["note"] = note
            overlay[f"T-{tid:03d}"] = entry
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(overlay, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{path}: recorded " + ", ".join(f"{t}={v}" for t, v in marks))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path("."),
                    help="project root (where CLAUDE.md lives; default: cwd)")
    ap.add_argument("--wi", default=None,
                    help="limit to one work item ID (e.g. FEAT-001); required with --mark")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--mark", action="append", default=[], metavar="TARGET=STATUS",
                    help="record orchestrator-owned state in tasks/<WI>-progress.json: "
                         "T-XXX=<status> or task-review=accepted (repeatable)")
    ap.add_argument("--note", default="", help="free-text note stored with --mark entries")
    ap.add_argument("--log-event", nargs="+", metavar="KEY=VALUE", default=None,
                    help="append one event to metrics/events.ndjson (guides/evaluation.md "
                         "schema) and exit: step=... event=... wi=... [task=... tokens=... "
                         "model=... cost=... detail=...]")
    args = ap.parse_args()

    root = args.root.resolve()
    if not (root / "docs" / "work-items").is_dir():
        print(f"{root}: ERROR: docs/work-items/ not found - is this a framework project root?",
              file=sys.stderr)
        return 1

    if args.log_event:
        return do_log_event(root, args.log_event)

    if args.mark:
        if not args.wi:
            print("ERROR: --mark requires --wi", file=sys.stderr)
            return 1
        marks = []
        for m in args.mark:
            if "=" not in m:
                print(f"ERROR: --mark expects TARGET=STATUS, got '{m}'", file=sys.stderr)
                return 1
            target, value = m.split("=", 1)
            marks.append((target.strip(), value.strip().lower()))
        return do_mark(root, args.wi, marks, args.note)

    work_items = discover_work_items(root)
    if args.wi:
        work_items = [w for w in work_items if w["id"] == args.wi]
        if not work_items:
            print(f"ERROR: work item '{args.wi}' not found under docs/work-items/",
                  file=sys.stderr)
            return 1

    subjects = git_commit_subjects(root)
    # Task IDs restart per task list; ambiguous ones need work-item-qualified
    # commits before they count as evidence (2.8.4).
    id_owners = task_id_owners(root)
    report = {"root": str(root), "work_items": [], "closed": [], "notes": []}
    if subjects is None:
        report["notes"].append("not a git repo (or git unavailable) - commit evidence "
                               "disabled; task states rely on reviews, plans, and the overlay")

    for wi in work_items:
        computed = compute_work_item(root, wi, subjects, id_owners)
        if computed["position"] == "closed":
            report["closed"].append(wi["id"])
        else:
            report["work_items"].append(computed)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_human(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
