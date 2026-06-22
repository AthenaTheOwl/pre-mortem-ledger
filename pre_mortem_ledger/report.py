"""Rendered Markdown views of the ledger and a month's pre-mortems.

Two outputs ship in v0.1:

- `render_month_index(...)` writes `premortem/INDEX.md` for one month.
  The CLI verb `premortem render` is a thin wrapper around it.
- `render_ledger_report(...)` walks `data/ledger/runs.jsonl` and prints
  a human-readable summary table. Used by `premortem ledger list` and
  by future audit jobs that want a static snapshot.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from pre_mortem_ledger.ledger import DEFAULT_LEDGER_PATH, LedgerRow, read_ledger
from pre_mortem_ledger.schema import load_premortem_file


def render_month_index(
    month: str,
    *,
    in_dir: str | Path,
    out_path: Optional[str | Path] = None,
) -> Path:
    """Write a Markdown index for every pre-mortem matching `month`.

    Returns the path written. If `out_path` is None, writes to
    `<in_dir>/INDEX.md`. The index is regenerated on each call; rows are
    sorted by filename so the output is deterministic.
    """
    in_dir_path = Path(in_dir)
    if not in_dir_path.exists():
        raise FileNotFoundError(f"no premortem directory: {in_dir_path}")
    rows: List[str] = []
    for path in sorted(in_dir_path.glob(f"premortem-*-{month}.md")):
        pm = load_premortem_file(path)
        rows.append(
            f"- **{pm.position}** ({pm.exposure_tier}): "
            f"{len(pm.failure_modes)} failure modes — `{path.name}`"
        )
    if not rows:
        rows.append(f"_no pre-mortems for {month}_")
    out = Path(out_path) if out_path else in_dir_path / "INDEX.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    body = "# Pre-Mortem Index — {m}\n\n{rows}\n".format(
        m=month, rows="\n".join(rows)
    )
    out.write_text(body, encoding="utf-8")
    return out


def _format_row(row: LedgerRow) -> str:
    brier = "—" if row.prior_run_brier is None else f"{row.prior_run_brier:.3f}"
    return (
        f"{row.month}  {row.run_type:<14}  brier={brier}  "
        f"positions={','.join(row.positions_scored) or '-'}  "
        f"modes={row.failure_modes_logged}  {row.run_id}"
    )


def format_ledger_rows(rows: Iterable[LedgerRow]) -> List[str]:
    """One formatted line per ledger row. Empty list maps to empty list."""
    return [_format_row(r) for r in rows]


def render_ledger_report(
    *,
    path: str | Path = DEFAULT_LEDGER_PATH,
    out_path: Optional[str | Path] = None,
) -> Path:
    """Render the ledger as a Markdown report at `out_path`.

    If `out_path` is None, writes `<path>.md` alongside the JSONL file.
    Empty ledgers still produce a file so downstream callers can rely on
    the path existing.
    """
    rows = read_ledger(path)
    src = Path(path)
    out = Path(out_path) if out_path else src.with_suffix(src.suffix + ".md")
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Ledger report", ""]
    if not rows:
        lines.append("_ledger is empty_")
    else:
        lines.append("| month | run_type | brier | positions | modes | run_id |")
        lines.append("|---|---|---|---|---|---|")
        for r in rows:
            brier = "—" if r.prior_run_brier is None else f"{r.prior_run_brier:.3f}"
            positions = ",".join(r.positions_scored) or "-"
            lines.append(
                f"| {r.month} | {r.run_type} | {brier} | {positions} | "
                f"{r.failure_modes_logged} | `{r.run_id}` |"
            )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
