"""Monthly runner.

Reads `config/positions.yaml`, picks the position to score this month, and
scaffolds a new pre-mortem Markdown file with three blank failure-mode
slots. The user fills in the narrative; the schema validator refuses the
file until each slot has at least one observability trigger.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import yaml

from pre_mortem_ledger.schema import FailureMode, PreMortem, dump_premortem_file

DEFAULT_POSITIONS_PATH = Path("config/positions.yaml")
DEFAULT_PREMORTEM_DIR = Path("premortem")

_TIER_RANK = {"concentrated": 0, "sized": 1, "probe": 2}


@dataclass(frozen=True)
class Position:
    ticker: str
    exposure_tier: str
    since: str


def load_positions(path: str | Path = DEFAULT_POSITIONS_PATH) -> List[Position]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    rows = raw.get("positions", [])
    return [
        Position(
            ticker=r["ticker"],
            exposure_tier=r["exposure_tier"],
            since=str(r["since"]),
        )
        for r in rows
    ]


def pick_target(positions: List[Position]) -> Position:
    """Pick the position for this month: the concentrated row with the
    longest exposure. Falls back to the first sized, then the first probe.
    Raises if no positions are registered."""
    if not positions:
        raise ValueError("no positions registered in config/positions.yaml")
    ranked = sorted(
        positions,
        key=lambda p: (_TIER_RANK.get(p.exposure_tier, 99), p.since, p.ticker),
    )
    return ranked[0]


def scaffold_premortem(
    month: str,
    position: str,
    *,
    out_dir: str | Path = DEFAULT_PREMORTEM_DIR,
    rubric_categories: Optional[List[str]] = None,
    exposure_tier: str = "concentrated",
) -> Path:
    """Write a fresh pre-mortem with three blank-but-valid failure-mode slots.

    Validation pass is intentional: the scaffold is a valid PreMortem on
    creation, so `premortem render` can read it back the same hour the
    user starts editing.
    """
    cats = rubric_categories or [
        "thesis-pillar-invalidation",
        "capital-allocation-regime",
        "operating-leverage-reversal",
    ]
    if len(cats) < 3:
        raise ValueError("scaffold needs at least 3 rubric categories")

    modes: List[FailureMode] = []
    for i, cat in enumerate(cats[:3], start=1):
        modes.append(
            FailureMode(
                id=f"fm-{i}",
                title=f"Placeholder failure mode {i}",
                narrative=(
                    "Replace this narrative with the concrete written-out "
                    "reason this position could be down 40 percent in 12 months."
                ),
                rank=i,
                rubric_category=cat,
                observability_triggers=[
                    "Replace this with a concrete observable signal."
                ],
                status_log=[],
            )
        )

    pm = PreMortem(
        position=position,
        month=month,
        exposure_tier=exposure_tier,
        failure_modes=modes,
    )
    out_path = Path(out_dir) / pm.expected_filename()
    body = (
        f"# Pre-Mortem: {position}, {month}\n\n"
        f"This file was scaffolded by `premortem new`. Fill in each failure "
        f"mode's narrative and observability triggers before the end of the "
        f"month, then run `premortem status --month <next-month>` to begin "
        f"tracking.\n"
    )
    return dump_premortem_file(pm, out_path, body=body)
