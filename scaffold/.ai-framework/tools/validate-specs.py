#!/usr/bin/env python3
"""Validate sharded spec documents: frontmatter, cross-references, freshness stamps.

Usage:
    python validate-specs.py [--root .] [--max-age 30] [--strict]

Checks:
  - every shard's frontmatter parses (flat keys; scalar or inline [a, b, c] values),
    its `kind` matches its directory, and its name key matches the filename
  - cross-references resolve: entity.endpoints/screens -> shards exist,
    resource.entities -> entity shards exist, screen.endpoints -> resource shards exist
  - index.md files only reference shard files that exist (unless marked "(new)");
    existing shards are mentioned in their index
  - freshness stamps ("> **Last verified against code:** YYYY-MM-DD ...") present on
    every shard, index, and docs/ARCHITECTURE.md, and not older than --max-age days
  - work items (docs/work-items/, skipping TEMPLATE-*) reference only spec shard
    paths that exist or are marked "(new)" on the same line

TEMPLATE-*.md files are skipped. Missing frontmatter is a warning (filename-only
fallback). Errors exit 1; --strict promotes warnings to failures.
Python 3.8+, standard library only.
"""

import argparse
import datetime
import re
import sys
from pathlib import Path

HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
STAMP_RE = re.compile(r"^>\s*\*\*Last verified against code:\*\*\s*(.*)$", re.MULTILINE)
STAMP_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
SHARD_REF_RE = re.compile(r"(?:docs/)?(data-model/entities|api-spec/endpoints|ui-specification/screens)/([a-z0-9][a-z0-9-]*)\.md")
SHORT_REF_RE = re.compile(r"(?<![a-z0-9/-])(entities|endpoints|screens)/([a-z0-9][a-z0-9-]*)\.md")
WORKITEM_REF_RE = re.compile(r"docs/(data-model|api-spec|ui-specification)/[A-Za-z0-9/_.-]+?\.md")

SPEC_DIRS = {
    "data-model": ("entities", "entity"),
    "api-spec": ("endpoints", "resource"),
    "ui-specification": ("screens", "screen"),
}

NAME_KEY = {"entity": "name", "resource": "resource", "screen": "screen"}
REF_KEYS = {
    # kind -> {frontmatter key: (spec dir, shard subdir)}
    "entity": {"endpoints": ("api-spec", "endpoints"), "screens": ("ui-specification", "screens")},
    "resource": {"entities": ("data-model", "entities")},
    "screen": {"endpoints": ("api-spec", "endpoints")},
}


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, file, msg):
        self.errors.append(f"{file}: ERROR: {msg}")

    def warn(self, file, msg):
        self.warnings.append(f"{file}: WARN: {msg}")


def strip_comments(text):
    """Remove HTML comments before reference scanning, preserving line numbers.

    Templates and scaffold stubs carry example shard paths (screens/login.md,
    entities/task-label.md) as authoring guidance inside <!-- --> comments;
    commented-out content is not a reference and must never fail validation.
    """
    return HTML_COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def kebab(name):
    """PascalCase / camelCase / spaced name -> kebab-case."""
    name = name.strip().replace(" ", "-").replace("_", "-")
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", name)
    return name.lower()


def parse_frontmatter(text, path, rep):
    """Parse a flat frontmatter block. Returns dict or None if absent."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fm = {}
    for i, raw in enumerate(lines[1:], 2):
        if raw.strip() == "---":
            return fm
        line = raw.split(" #", 1)[0].rstrip()
        if not line.strip():
            continue
        if ":" not in line:
            rep.error(path, f"frontmatter line {i} is not 'key: value': {raw.strip()!r}")
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("["):
            if not value.endswith("]"):
                rep.error(path, f"frontmatter key '{key}': inline arrays must close on the same line")
                fm[key] = []
                continue
            items = [v.strip() for v in value[1:-1].split(",") if v.strip()]
            fm[key] = items
        else:
            fm[key] = value
    rep.error(path, "frontmatter block never closed with '---'")
    return fm


def check_stamp(text, path, rep, max_age, today):
    if int(max_age) <= 0:  # 0 disables staleness checking (frozen eval fixtures)
        m = STAMP_RE.search(text)
        if not m:
            rep.warn(path, "missing freshness stamp ('> **Last verified against code:** ...')")
        return
    m = STAMP_RE.search(text)
    if not m:
        rep.warn(path, "missing freshness stamp ('> **Last verified against code:** ...')")
        return
    date_m = STAMP_DATE_RE.search(m.group(1))
    if not date_m:
        rep.warn(path, "freshness stamp present but not filled with a date")
        return
    try:
        stamped = datetime.date.fromisoformat(date_m.group(1))
    except ValueError:
        rep.warn(path, f"freshness stamp date is invalid: {date_m.group(1)}")
        return
    age = (today - stamped).days
    if age > max_age:
        rep.warn(path, f"stamp is {age} days old (max {max_age}) - verify this shard "
                       f"against the code before relying on it")


def is_placeholder(value):
    return not value or "[" in value or "<" in value or "TODO" in value


def check_shard(path, spec_key, kind, docs_root, rep, max_age, today):
    text = path.read_text(encoding="utf-8", errors="replace")
    check_stamp(text, path, rep, max_age, today)
    fm = parse_frontmatter(text, path, rep)
    if fm is None:
        rep.warn(path, "no frontmatter — cross-references cannot be validated mechanically")
        return
    got_kind = fm.get("kind", "")
    if got_kind != kind:
        rep.error(path, f"frontmatter kind is '{got_kind}', expected '{kind}' for this directory")
        return
    name_key = NAME_KEY[kind]
    name = fm.get(name_key, "")
    if is_placeholder(name):
        rep.warn(path, f"frontmatter '{name_key}' looks unfilled: {name!r}")
    elif kebab(name) != path.stem:
        rep.error(path, f"frontmatter {name_key} '{name}' does not match filename "
                        f"'{path.stem}' (expected '{kebab(name)}')")
    for key, (spec, sub) in REF_KEYS[kind].items():
        refs = fm.get(key, [])
        if isinstance(refs, str):
            rep.error(path, f"frontmatter '{key}' must be an inline array like [a, b]")
            continue
        for ref in refs:
            if is_placeholder(ref):
                rep.warn(path, f"frontmatter '{key}' has unfilled entry: {ref!r}")
                continue
            target = docs_root / spec / sub / f"{ref}.md"
            if not target.exists():
                rep.error(path, f"frontmatter {key} references '{ref}' but "
                                f"docs/{spec}/{sub}/{ref}.md does not exist")


def check_index(index_path, spec_key, docs_root, rep, max_age, today):
    text = index_path.read_text(encoding="utf-8", errors="replace")
    check_stamp(text, index_path, rep, max_age, today)
    sub, _ = SPEC_DIRS[spec_key]
    shard_dir = docs_root / spec_key / sub
    referenced = set()
    for line in strip_comments(text).splitlines():
        refs = [(m.group(1), m.group(2)) for m in SHARD_REF_RE.finditer(line)]
        refs += [(f"{spec_key}/{m.group(1)}", m.group(2))
                 for m in SHORT_REF_RE.finditer(line) if m.group(1) == sub]
        for ref_dir, ref_name in refs:
            if not ref_dir.startswith(spec_key):
                continue
            referenced.add(ref_name)
            if "(new)" in line:
                continue
            if not (shard_dir / f"{ref_name}.md").exists():
                rep.error(index_path, f"references {ref_dir}/{ref_name}.md, which does not "
                                      f"exist and is not marked (new)")
    if shard_dir.is_dir():
        for shard in sorted(shard_dir.glob("*.md")):
            if shard.name.startswith("TEMPLATE-"):
                continue
            if shard.stem not in referenced and f"{shard.stem}.md" not in text:
                rep.warn(index_path, f"existing shard {sub}/{shard.name} is not mentioned "
                                     f"in this index")


def check_work_items(docs_root, rep):
    wi_dir = docs_root / "work-items"
    if not wi_dir.is_dir():
        return
    for wi in sorted(wi_dir.glob("*.md")):
        if wi.name.startswith("TEMPLATE-"):
            continue
        text = strip_comments(wi.read_text(encoding="utf-8", errors="replace"))
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in WORKITEM_REF_RE.finditer(line):
                ref = m.group(0)
                target = docs_root.parent / ref
                if target.exists() or "(new)" in line:
                    continue
                rep.error(wi, f"line {lineno}: references {ref}, which does not exist "
                              f"and is not marked (new)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path("."),
                    help="project root containing docs/ (default: cwd)")
    ap.add_argument("--max-age", type=int, default=30,
                    help="max stamp age in days before a staleness warning "
                         "(default 30; 0 disables — frozen fixtures)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args()

    rep = Report()
    today = datetime.date.today()
    docs_root = args.root / "docs"
    if not docs_root.is_dir():
        print(f"{docs_root}: ERROR: no docs/ directory found under --root", file=sys.stderr)
        return 1

    found_any = False
    shard_count = 0
    for spec_key, (sub, kind) in SPEC_DIRS.items():
        spec_dir = docs_root / spec_key
        if not spec_dir.is_dir():
            continue
        found_any = True
        index = spec_dir / "index.md"
        if index.is_file():
            check_index(index, spec_key, docs_root, rep, args.max_age, today)
        else:
            rep.error(spec_dir, "missing index.md")
        shard_dir = spec_dir / sub
        if shard_dir.is_dir():
            for shard in sorted(shard_dir.glob("*.md")):
                if shard.name.startswith("TEMPLATE-"):
                    continue
                shard_count += 1
                check_shard(shard, spec_key, kind, docs_root, rep, args.max_age, today)
        components = spec_dir / "components.md"
        if spec_key == "ui-specification" and components.is_file():
            shard_count += 1
            text = components.read_text(encoding="utf-8", errors="replace")
            check_stamp(text, components, rep, args.max_age, today)
            fm = parse_frontmatter(text, components, rep)
            if fm is not None and fm.get("kind") != "component-inventory":
                rep.error(components, f"frontmatter kind is '{fm.get('kind')}', "
                                      f"expected 'component-inventory'")

    if not found_any:
        print(f"{docs_root}: ERROR: no sharded spec directories found "
              f"(expected docs/data-model/, docs/api-spec/, or docs/ui-specification/)",
              file=sys.stderr)
        return 1

    arch = docs_root / "ARCHITECTURE.md"
    if arch.is_file():
        check_stamp(arch.read_text(encoding="utf-8", errors="replace"), arch, rep,
                    args.max_age, today)

    check_work_items(docs_root, rep)

    for line in rep.errors + rep.warnings:
        print(line)
    print(f"\n{docs_root}: {shard_count} shard(s) checked, "
          f"{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    failed = bool(rep.errors) or (args.strict and bool(rep.warnings))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
