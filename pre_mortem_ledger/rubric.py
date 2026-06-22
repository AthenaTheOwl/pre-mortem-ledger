"""Loader for the failure-mode rubric.

The rubric is the taxonomy of recurring failure categories. Every failure
mode in a pre-mortem is tagged with exactly one category that must exist
in `rubric/failure_modes.yaml`. Drift between the example pre-mortems and
the rubric is caught at validation time, not at render time.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml

DEFAULT_RUBRIC_PATH = Path("rubric/failure_modes.yaml")


@dataclass(frozen=True)
class RubricCategory:
    id: str
    name: str
    description: str


def load_rubric(path: str | Path = DEFAULT_RUBRIC_PATH) -> Dict[str, RubricCategory]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    categories = raw.get("categories", [])
    out: Dict[str, RubricCategory] = {}
    for row in categories:
        cat = RubricCategory(
            id=row["id"], name=row["name"], description=row["description"]
        )
        if cat.id in out:
            raise ValueError(f"duplicate rubric category id: {cat.id}")
        out[cat.id] = cat
    if len(out) < 8:
        raise ValueError(
            f"rubric must list at least 8 categories; got {len(out)}"
        )
    return out


def assert_categories_known(
    used_categories: List[str], rubric: Dict[str, RubricCategory]
) -> None:
    unknown = [c for c in used_categories if c not in rubric]
    if unknown:
        raise ValueError(
            f"unknown rubric categories referenced: {unknown}; "
            f"add them to rubric/failure_modes.yaml first"
        )
