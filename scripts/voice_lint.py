#!/usr/bin/env python3
"""Voice lint stub (R-PML-008).

v0.1 enforces only the banlist. The structural anti-pattern checks (the
"X isn't Y; Z is the W" reversal, marketing scaffolds, em-dash overuse)
ship in spec 0002.

Usage:
    python scripts/voice_lint.py [path ...]

Exit code is 0 on clean, 1 on any banlist hit, 2 on usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

# Banlist mirrors the portfolio voice spec. Each pattern is matched
# case-insensitively as a whole word. Keep narrow on purpose; the
# structural checks are where this script earns its keep in spec 0003.
#
# Note: "leverage" is intentionally omitted in v0.1. The verb form ("we
# leverage X") is what the portfolio guide bans, but "operating
# leverage" is a legitimate financial-accounting noun that appears in
# the rubric. The verb-only check returns as a structural rule in 0003.
BANLIST = (
    "delve",
    "synergy",
    "seamless",
    "robust",
    "cutting-edge",
    "best-in-class",
    "game-changer",
    "revolutionize",
    "unlock value",
    "value-add",
    "stakeholder",
    "actionable insights",
    "tapestry",
)

WORD_RE = {term: re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE) for term in BANLIST}


def iter_paths(args_paths: Iterable[str]) -> Iterable[Path]:
    for p in args_paths:
        path = Path(p)
        if path.is_dir():
            yield from sorted(path.rglob("*.md"))
        elif path.is_file():
            yield path


def lint_file(path: Path) -> list[tuple[int, str, str]]:
    hits: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        for term, pattern in WORD_RE.items():
            if pattern.search(line):
                hits.append((lineno, term, line.strip()))
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "paths",
        nargs="*",
        default=["premortem", "examples", "docs", "README.md", "STATUS.md"],
    )
    args = parser.parse_args(argv)

    total_hits = 0
    for path in iter_paths(args.paths):
        for lineno, term, line in lint_file(path):
            print(f"{path}:{lineno}: banned term '{term}': {line}")
            total_hits += 1
    if total_hits:
        print(f"\nvoice_lint: {total_hits} hit(s)", file=sys.stderr)
        return 1
    print("voice_lint: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
