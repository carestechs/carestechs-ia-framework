#!/usr/bin/env python3
"""Validate an AI-generated task list against the framework's canonical task schema.

Usage:
    python validate-tasks.py tasks/FEAT-001-tasks.md [--work-item docs/work-items/FEAT-001-title.md]
                                                     [--root .] [--strict]

Checks (schema reference: .ai-framework/prompts/base-template.md):
  - every task block has the required fields, with valid Type/Workflow/Complexity values
  - task IDs are unique (warns on gaps in the sequence)
  - Dependencies reference existing task IDs and form a DAG (no cycles)
  - every "Files to Modify/Create" entry exists under --root, or is marked (new)
  - every task has at least one acceptance criterion checkbox
  - with --work-item: the "Acceptance Criteria Coverage" table exists, its task IDs
    resolve, and its row count matches the work item's acceptance criteria

Exit code 0 when no errors (with --strict, warnings also fail); 1 otherwise.
Python 3.8+, standard library only.
"""

import argparse
import re
import sys
from pathlib import Path

TYPE_VALUES = {
    "Backend", "Frontend", "Database", "Testing", "DevOps", "Documentation",
    "Investigation",  # bugfix-tasks delta
    "Cleanup",        # refactor-tasks delta
}
WORKFLOW_VALUES = {"standard", "mockup-first", "investigation-first"}
COMPLEXITY_VALUES = {"S", "M", "L", "XL"}

# Canonical field order (Technical Notes is optional).
FIELD_ORDER = [
    "Type", "Workflow", "Description", "Rationale", "Acceptance Criteria",
    "Dependencies", "Complexity", "Files to Modify/Create",
]
REQUIRED_FIELDS = set(FIELD_ORDER)
KNOWN_FIELDS = REQUIRED_FIELDS | {"Technical Notes"}

TASK_HEADING_RE = re.compile(r"^#{2,4}\s+T-(\d{1,4})\s*:\s*(.+?)\s*$")
FIELD_RE = re.compile(r"^\*\*([A-Za-z /]+?):\*\*\s*(.*)$")
DEP_ID_RE = re.compile(r"T-\d{1,4}")
FILE_BULLET_RE = re.compile(
    r"^\s*[-*]\s*`?(?P<path>[^`\s]+)`?\s*(?P<new>\(new\))?\s*(?:[-–—]\s*(?P<desc>.*))?$"
)
CHECKBOX_RE = re.compile(r"^\s*[-*]\s*\[[ xX]\]\s+\S")
AC_BULLET_RE = re.compile(r"^\s*[-*]\s*\*\*AC-\d+\*\*\s*:")
COVERAGE_HEADING_RE = re.compile(r"^#{2,4}\s+Acceptance Criteria Coverage\s*$", re.IGNORECASE)


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, file, line, msg):
        self.errors.append(f"{file}:{line}: ERROR: {msg}")

    def warn(self, file, line, msg):
        self.warnings.append(f"{file}:{line}: WARN: {msg}")


class Task:
    def __init__(self, tid, title, line):
        self.id = tid            # int
        self.title = title
        self.line = line         # 1-based line of the heading
        self.fields = {}         # name -> (line, first-line value)
        self.body = {}           # name -> list[(line, text)] continuation lines
        self.order = []          # field names in appearance order


def strip_code_fences(lines):
    """Yield (lineno, text) for lines outside fenced code blocks."""
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


def parse_tasks(path, rep):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    tasks = []
    current = None
    current_field = None
    coverage_ids = []
    coverage_rows = 0
    coverage_line = None
    in_coverage = False

    for lineno, raw in strip_code_fences(lines):
        heading = TASK_HEADING_RE.match(raw)
        if heading:
            current = Task(int(heading.group(1)), heading.group(2), lineno)
            tasks.append(current)
            current_field = None
            in_coverage = False
            continue
        if COVERAGE_HEADING_RE.match(raw):
            in_coverage = True
            coverage_line = lineno
            current = None
            current_field = None
            continue
        if raw.startswith("#"):
            # any other heading ends the current task block / coverage section
            current = None
            current_field = None
            if not COVERAGE_HEADING_RE.match(raw):
                in_coverage = False
            continue
        if in_coverage:
            cells = [c.strip() for c in raw.strip().strip("|").split("|")]
            if raw.strip().startswith("|") and len(cells) >= 2 \
                    and not set(cells[0]) <= set("-: ") and cells[0].lower() != "work item ac":
                coverage_rows += 1
                coverage_ids.append((lineno, DEP_ID_RE.findall(cells[-1])))
            continue
        if current is None:
            continue
        field = FIELD_RE.match(raw.strip())
        if field and field.group(1).strip() in KNOWN_FIELDS:
            name = field.group(1).strip()
            if name in current.fields:
                rep.warn(path, lineno, f"T-{current.id:03d}: duplicate field '{name}'")
            current.fields[name] = (lineno, field.group(2).strip())
            current.order.append(name)
            current_field = name
            current.body.setdefault(name, [])
            continue
        if current_field is not None and raw.strip():
            current.body[current_field].append((lineno, raw))

    return tasks, {"rows": coverage_rows, "ids": coverage_ids, "line": coverage_line}


def check_schema(path, tasks, rep, root):
    seen = {}
    for t in tasks:
        tag = f"T-{t.id:03d}"
        if t.id in seen:
            rep.error(path, t.line, f"{tag}: duplicate task ID (first defined at line {seen[t.id]})")
        seen[t.id] = t.line

        for field in FIELD_ORDER:
            if field not in t.fields:
                rep.error(path, t.line, f"{tag}: missing required field '{field}'")

        # enum checks
        def enum_check(name, allowed):
            if name in t.fields:
                line, value = t.fields[name]
                clean = value.strip().strip("`").strip()
                if clean not in allowed:
                    rep.error(path, line, f"{tag}: {name} '{clean}' not in {sorted(allowed)}")

        enum_check("Type", TYPE_VALUES)
        enum_check("Workflow", WORKFLOW_VALUES)
        enum_check("Complexity", COMPLEXITY_VALUES)

        # field order (warning only)
        present_in_order = [f for f in t.order if f in FIELD_ORDER]
        expected = [f for f in FIELD_ORDER if f in t.fields]
        if present_in_order != expected:
            rep.warn(path, t.line, f"{tag}: fields out of canonical order "
                                   f"(found {present_in_order})")

        # acceptance criteria: at least one checkbox in the field body
        if "Acceptance Criteria" in t.fields:
            boxes = [ln for ln, text in t.body.get("Acceptance Criteria", [])
                     if CHECKBOX_RE.match(text)]
            if not boxes:
                rep.error(path, t.fields["Acceptance Criteria"][0],
                          f"{tag}: Acceptance Criteria has no '- [ ]' checklist items")

        # files: at least one bullet; existence check unless marked (new)
        if "Files to Modify/Create" in t.fields:
            bullets = t.body.get("Files to Modify/Create", [])
            parsed = []
            for ln, text in bullets:
                m = FILE_BULLET_RE.match(text)
                if m and m.group("path"):
                    parsed.append((ln, m.group("path"), bool(m.group("new"))))
            if not parsed:
                rep.error(path, t.fields["Files to Modify/Create"][0],
                          f"{tag}: Files to Modify/Create lists no files")
            for ln, fpath, is_new in parsed:
                if any(ch in fpath for ch in "[]<>{}"):
                    rep.warn(path, ln, f"{tag}: file entry '{fpath}' looks like an "
                                       f"unfilled placeholder")
                    continue
                if not is_new and not (root / fpath).exists():
                    rep.warn(path, ln, f"{tag}: file '{fpath}' does not exist under "
                                       f"'{root}' and is not marked (new)")

    # sequence gaps
    ids = sorted(seen)
    if ids:
        missing = sorted(set(range(ids[0], ids[-1] + 1)) - set(ids))
        if missing:
            gaps = ", ".join(f"T-{i:03d}" for i in missing)
            rep.warn(path, tasks[0].line, f"task ID sequence has gaps: {gaps}")


def check_dependencies(path, tasks, rep):
    ids = {t.id for t in tasks}
    graph = {t.id: [] for t in tasks}
    for t in tasks:
        tag = f"T-{t.id:03d}"
        if "Dependencies" not in t.fields:
            continue
        line, value = t.fields["Dependencies"]
        clean = value.strip().strip("`")
        if clean.lower() in ("none", "none."):
            continue
        deps = [int(d[2:]) for d in DEP_ID_RE.findall(clean)]
        if not deps:
            rep.error(path, line, f"{tag}: Dependencies must be task IDs "
                                  f"(T-XXX, comma-separated) or 'None'; got '{clean}'")
            continue
        leftover = DEP_ID_RE.sub("", clean).replace(",", "").strip()
        if leftover:
            rep.warn(path, line, f"{tag}: Dependencies contains extra text '{leftover}' - "
                                 f"use plain ID lists")
        for d in deps:
            if d not in ids:
                rep.error(path, line, f"{tag}: depends on T-{d:03d}, which is not in this file")
            elif d == t.id:
                rep.error(path, line, f"{tag}: depends on itself")
            else:
                graph[t.id].append(d)

    # cycle detection (iterative DFS, 3-color)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {tid: WHITE for tid in graph}
    for start in graph:
        if color[start] != WHITE:
            continue
        stack = [(start, iter(graph[start]))]
        color[start] = GRAY
        path_ids = [start]
        while stack:
            node, it = stack[-1]
            advanced = False
            for nxt in it:
                if color.get(nxt, BLACK) == GRAY:
                    cyc = " -> ".join(f"T-{i:03d}" for i in path_ids + [nxt])
                    t = next(t for t in tasks if t.id == node)
                    rep.error(path, t.line, f"dependency cycle detected: {cyc}")
                elif color.get(nxt) == WHITE:
                    color[nxt] = GRAY
                    stack.append((nxt, iter(graph[nxt])))
                    path_ids.append(nxt)
                    advanced = True
                    break
            if not advanced:
                color[node] = BLACK
                stack.pop()
                path_ids.pop()


def check_coverage(path, tasks, coverage, work_item, rep):
    ids = {t.id for t in tasks}
    if coverage["line"] is None:
        rep.error(path, 1, "work item given but no '## Acceptance Criteria Coverage' "
                           "section found in the task list")
        return
    if coverage["rows"] == 0:
        rep.error(path, coverage["line"], "Acceptance Criteria Coverage table has no rows")
    for lineno, dep_ids in coverage["ids"]:
        if not dep_ids:
            rep.error(path, lineno, "coverage row has no task IDs in 'Covered By'")
        for d in dep_ids:
            if int(d[2:]) not in ids:
                rep.error(path, lineno, f"coverage row references {d}, which is not in this file")

    wi_lines = work_item.read_text(encoding="utf-8", errors="replace").splitlines()
    in_ac = False
    ac_count = 0
    for _, raw in strip_code_fences(wi_lines):
        if re.match(r"^#{2,4}\s+.*Acceptance Criteria", raw, re.IGNORECASE):
            in_ac = True
            continue
        if raw.startswith("#"):
            in_ac = False
            continue
        if in_ac and (CHECKBOX_RE.match(raw) or AC_BULLET_RE.match(raw)):
            ac_count += 1
    if ac_count and coverage["rows"] != ac_count:
        rep.warn(path, coverage["line"],
                 f"coverage table has {coverage['rows']} rows but the work item defines "
                 f"{ac_count} acceptance criteria")
    if ac_count == 0:
        rep.warn(path, coverage["line"],
                 f"no acceptance criteria checkboxes found in {work_item} - "
                 f"cannot cross-check coverage")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("task_list", type=Path, help="task list markdown file (tasks/*.md)")
    ap.add_argument("--work-item", type=Path, default=None,
                    help="work item doc to cross-check acceptance-criteria coverage against")
    ap.add_argument("--root", type=Path, default=Path("."),
                    help="project root for file-existence checks (default: cwd)")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as failures")
    args = ap.parse_args()

    rep = Report()
    if not args.task_list.is_file():
        print(f"{args.task_list}: ERROR: file not found", file=sys.stderr)
        return 1

    tasks, coverage = parse_tasks(args.task_list, rep)
    if not tasks:
        rep.error(args.task_list, 1, "no task blocks found (expected headings like '### T-001: ...')")
    else:
        check_schema(args.task_list, tasks, rep, args.root)
        check_dependencies(args.task_list, tasks, rep)

    if args.work_item is not None:
        if not args.work_item.is_file():
            rep.error(args.task_list, 1, f"--work-item file not found: {args.work_item}")
        elif tasks:
            check_coverage(args.task_list, tasks, coverage, args.work_item, rep)

    for line in rep.errors + rep.warnings:
        print(line)
    n_tasks = len(tasks)
    print(f"\n{args.task_list}: {n_tasks} task(s), "
          f"{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    failed = bool(rep.errors) or (args.strict and bool(rep.warnings))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
