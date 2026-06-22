"""Ledger of monthly scoring / calibration runs.

The pre-mortem files are the artifacts; the ledger is the meta-record of
*when* the monthly exercise ran, *what* it covered, and (for runs after
the first) *how well* the prior month's predictions held up. Persisted as
append-only JSONL so two runs of the same month would conflict loudly.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

DEFAULT_LEDGER_PATH = Path("data/ledger/runs.jsonl")


@dataclass(frozen=True)
class LedgerRow:
    run_id: str
    month: str
    run_type: str  # "initialization" | "monthly" | "calibration"
    positions_scored: List[str]
    failure_modes_logged: int
    prior_run_brier: Optional[float] = None
    notes: str = ""
    schema_version: int = 1
    extras: dict = field(default_factory=dict)


def read_ledger(path: str | Path = DEFAULT_LEDGER_PATH) -> List[LedgerRow]:
    p = Path(path)
    if not p.exists():
        return []
    rows: List[LedgerRow] = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        data = json.loads(raw)
        rows.append(
            LedgerRow(
                run_id=data["run_id"],
                month=data["month"],
                run_type=data["run_type"],
                positions_scored=list(data.get("positions_scored", [])),
                failure_modes_logged=int(data.get("failure_modes_logged", 0)),
                prior_run_brier=data.get("prior_run_brier"),
                notes=data.get("notes", ""),
                schema_version=int(data.get("schema_version", 1)),
                extras=dict(data.get("extras", {})),
            )
        )
    return rows


def append_ledger(
    row: LedgerRow, path: str | Path = DEFAULT_LEDGER_PATH
) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    for existing in read_ledger(p):
        if existing.run_id == row.run_id:
            raise ValueError(f"ledger already contains run_id {row.run_id!r}")
        if existing.month == row.month and existing.run_type == row.run_type:
            raise ValueError(
                f"ledger already has a {row.run_type} run for {row.month}"
            )
    line = json.dumps(asdict(row), sort_keys=True)
    with p.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")
    return p
