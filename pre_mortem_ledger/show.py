"""`premortem show` — a no-arg, read-only snapshot of the committed state.

Reads the latest committed pre-mortem (the worked example by default) and
the run ledger, then prints a ranked, readable view: the failure modes in
rank order with their rubric category and a status read, plus a one-line
headline finding. Offline, side-effect free, exits 0.

The intent is that `python -m pre_mortem_ledger show` answers, at a glance,
"what does the most recent pre-mortem say is most likely to kill the
position, and has any of it started to show up yet?".
"""

from __future__ import annotations

from pathlib import Path

from pre_mortem_ledger.ledger import LedgerRow, read_ledger
from pre_mortem_ledger.schema import FailureMode, PreMortem, load_premortem_file

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = REPO_ROOT / "data" / "ledger" / "runs.jsonl"
EXAMPLES_DIR = REPO_ROOT / "examples"


def _latest_premortem_path(examples_dir: Path = EXAMPLES_DIR) -> Path | None:
    """Pick the pre-mortem to show: the highest month, then last by name."""
    candidates = sorted(examples_dir.glob("premortem-*.md"))
    if not candidates:
        return None
    # filenames are premortem-<position>-<YYYY-Mnn>.md; sorting by the month
    # token gives a stable "latest" without parsing every file.
    return sorted(candidates, key=lambda p: p.stem.rsplit("-", 1)[-1])[-1]


def _latest_status(fm: FailureMode) -> str:
    if not fm.status_log:
        return "not yet re-scored"
    return fm.status_log[-1].status


_STATUS_RANK = {
    "observed": 3,
    "evidence-emerging": 2,
    "unchanged": 1,
    "retired": 0,
}


def _headline(pm: PreMortem, ledger: list[LedgerRow]) -> str:
    top = min(pm.failure_modes, key=lambda fm: fm.rank)
    # has anything moved off "not yet re-scored"?
    moved = [
        fm
        for fm in pm.failure_modes
        if fm.status_log and fm.status_log[-1].status in ("evidence-emerging", "observed")
    ]
    runs = len(ledger)
    if moved:
        hottest = max(
            moved, key=lambda fm: _STATUS_RANK.get(fm.status_log[-1].status, 0)
        )
        return (
            f"{hottest.id} ({hottest.title}) is now "
            f"'{hottest.status_log[-1].status}' -- the pre-mortem is no longer hypothetical."
        )
    return (
        f"top failure mode for {pm.position} is {top.id}: {top.title}. "
        f"nothing re-scored yet across {runs} ledger run(s) -- all modes still imagined, not observed."
    )


def build_show_lines(
    *,
    premortem_path: str | Path | None = None,
    ledger_path: str | Path = DEFAULT_LEDGER,
) -> list[str]:
    """Return the lines for `premortem show`. Pure: no printing, no writes."""
    pm_path = Path(premortem_path) if premortem_path else _latest_premortem_path()
    if pm_path is None or not Path(pm_path).exists():
        return [
            "no committed pre-mortem found under examples/.",
            "run `premortem new --month <YYYY-Mnn>` to scaffold one.",
        ]

    pm = load_premortem_file(pm_path)
    ledger = read_ledger(ledger_path)

    lines: list[str] = []
    lines.append(f"pre-mortem -- {pm.position} ({pm.exposure_tier}), {pm.month}")
    lines.append(f"source: {Path(pm_path).name}")
    lines.append("")
    lines.append(f"{len(pm.failure_modes)} failure modes, ranked by current read of likelihood:")
    lines.append("")

    rank_w = 4
    title_w = 52
    cat_w = 26
    header = (
        f"{'rank':<{rank_w}}  {'failure mode':<{title_w}}  "
        f"{'rubric category':<{cat_w}}  status"
    )
    lines.append(header)
    lines.append("-" * len(header))
    for fm in sorted(pm.failure_modes, key=lambda f: f.rank):
        title = fm.title if len(fm.title) <= title_w else fm.title[: title_w - 3] + "..."
        cat = fm.rubric_category if len(fm.rubric_category) <= cat_w else fm.rubric_category[: cat_w - 3] + "..."
        lines.append(
            f"{fm.id:<{rank_w}}  {title:<{title_w}}  {cat:<{cat_w}}  {_latest_status(fm)}"
        )

    lines.append("")
    top = min(pm.failure_modes, key=lambda fm: fm.rank)
    lines.append(f"top trigger to watch ({top.id}):")
    for trig in top.observability_triggers[:2]:
        lines.append(f"  - {trig}")

    lines.append("")
    lines.append("ledger:")
    if not ledger:
        lines.append("  (empty)")
    else:
        for row in ledger:
            brier = "n/a" if row.prior_run_brier is None else f"{row.prior_run_brier:.3f}"
            lines.append(
                f"  {row.month}  {row.run_type:<14}  "
                f"positions={','.join(row.positions_scored) or '-'}  "
                f"modes={row.failure_modes_logged}  brier={brier}"
            )

    lines.append("")
    lines.append(f"headline: {_headline(pm, ledger)}")
    return lines


def cmd_show(
    *,
    premortem_path: str | Path | None = None,
    ledger_path: str | Path = DEFAULT_LEDGER,
) -> int:
    for line in build_show_lines(premortem_path=premortem_path, ledger_path=ledger_path):
        print(line)
    return 0
