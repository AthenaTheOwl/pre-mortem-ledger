#!/usr/bin/env python3
"""Spec requirements traceability (R-PML-009).

Walks every spec directory under `specs/`, collects the `R-PML-NNN`
identifiers declared in `requirements.md`, and then confirms that every
`R-PML-NNN` referenced in `design.md`, `tasks.md`, and `acceptance.md`
exists in `requirements.md`. Missing identifiers fail the check; orphan
requirements (declared but never referenced) print a warning but do not
fail.

Exit code is 0 on clean, 1 on any missing reference, 2 on usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIREMENT_HEADING_RE = re.compile(r"^##\s+(R-PML-\d{3})\b", re.MULTILINE)
REQUIREMENT_REF_RE = re.compile(r"\bR-PML-\d{3}\b")


def collect_declared(spec_dir: Path) -> set[str]:
    req_file = spec_dir / "requirements.md"
    if not req_file.exists():
        return set()
    text = req_file.read_text(encoding="utf-8")
    return set(REQUIREMENT_HEADING_RE.findall(text))


def collect_referenced(spec_dir: Path) -> dict[str, set[str]]:
    refs: dict[str, set[str]] = {}
    for name in ("design.md", "tasks.md", "acceptance.md"):
        path = spec_dir / name
        if not path.exists():
            continue
        refs[name] = set(REQUIREMENT_REF_RE.findall(path.read_text(encoding="utf-8")))
    return refs


def check_spec(spec_dir: Path) -> tuple[int, int]:
    declared = collect_declared(spec_dir)
    refs = collect_referenced(spec_dir)
    referenced_anywhere: set[str] = set()
    missing = 0
    for fname, refs_in_file in refs.items():
        for req_id in sorted(refs_in_file):
            referenced_anywhere.add(req_id)
            if req_id not in declared:
                print(f"{spec_dir / fname}: references undeclared {req_id}")
                missing += 1
    orphans = declared - referenced_anywhere
    for orphan in sorted(orphans):
        print(f"warning: {spec_dir / 'requirements.md'}: {orphan} is declared but never referenced")
    return missing, len(orphans)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--specs-dir", default="specs")
    args = parser.parse_args(argv)
    specs_root = Path(args.specs_dir)
    if not specs_root.exists():
        print(f"no specs directory: {specs_root}", file=sys.stderr)
        return 2

    total_missing = 0
    for spec_dir in sorted(p for p in specs_root.iterdir() if p.is_dir()):
        missing, _ = check_spec(spec_dir)
        total_missing += missing
    if total_missing:
        print(f"\nspec_check: {total_missing} undeclared reference(s)", file=sys.stderr)
        return 1
    print("spec_check: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
