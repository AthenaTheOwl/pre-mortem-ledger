"""Streamlit view of the committed pre-mortem ledger.

Reads the same committed artifacts the `premortem show` CLI verb reads --
the worked example pre-mortem under examples/ and the run ledger under
data/ledger/ -- straight off disk, relative to this file. No network, no
secrets, no writes. Browse the ranked failure modes, read each one's
narrative and observability triggers, and see the run ledger.

run locally:
    python -m uv run --with streamlit streamlit run streamlit_app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from pre_mortem_ledger.ledger import read_ledger
from pre_mortem_ledger.schema import load_premortem_file

HERE = Path(__file__).resolve().parent
EXAMPLES_DIR = HERE / "examples"
LEDGER_PATH = HERE / "data" / "ledger" / "runs.jsonl"


def _latest_premortem_path() -> Path | None:
    candidates = sorted(EXAMPLES_DIR.glob("premortem-*.md"))
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: p.stem.rsplit("-", 1)[-1])[-1]


st.set_page_config(page_title="pre-mortem ledger", layout="wide")

st.title("pre-mortem ledger")
st.caption(
    "monthly forced pre-mortem on the largest active investing position: "
    "name the failure modes before they show up in price, attach an "
    "observability trigger to each, and track them month over month."
)

pm_path = _latest_premortem_path()
if pm_path is None or not pm_path.exists():
    st.warning(
        "no committed pre-mortem found under examples/. "
        "run `premortem new --month <YYYY-Mnn>` to scaffold one, then reload."
    )
    st.stop()

pm = load_premortem_file(pm_path)
ledger = read_ledger(LEDGER_PATH)

modes = sorted(pm.failure_modes, key=lambda fm: fm.rank)


def _latest_status(fm) -> str:
    return fm.status_log[-1].status if fm.status_log else "not yet re-scored"


rescored = sum(1 for fm in pm.failure_modes if fm.status_log)

c1, c2, c3 = st.columns(3)
c1.metric("position", f"{pm.position}", help=f"exposure tier: {pm.exposure_tier}")
c2.metric("failure modes", len(pm.failure_modes))
c3.metric("ledger runs", len(ledger))

st.divider()

left, right = st.columns([3, 2])

with left:
    st.subheader(f"ranked failure modes -- {pm.position}, {pm.month}")
    df = pd.DataFrame(
        [
            {
                "rank": fm.rank,
                "id": fm.id,
                "failure mode": fm.title,
                "rubric category": fm.rubric_category,
                "status": _latest_status(fm),
                "triggers": len(fm.observability_triggers),
            }
            for fm in modes
        ]
    ).sort_values("rank")
    st.dataframe(df, hide_index=True, use_container_width=True)

with right:
    st.subheader("inspect a failure mode")
    labels = {f"{fm.id} - {fm.title}": fm for fm in modes}
    pick = st.selectbox("pick a failure mode", list(labels.keys()))
    fm = labels[pick]
    st.markdown(f"**rank {fm.rank}** - `{fm.rubric_category}` - status: *{_latest_status(fm)}*")
    st.markdown(fm.narrative)
    st.markdown("**observability triggers**")
    for trig in fm.observability_triggers:
        st.markdown(f"- {trig}")
    if fm.status_log:
        st.markdown("**status log**")
        for entry in fm.status_log:
            note = f" - {entry.note}" if entry.note else ""
            st.markdown(f"- {entry.month}: {entry.status}{note}")

st.divider()

st.subheader("run ledger")
if not ledger:
    st.info("ledger is empty.")
else:
    ldf = pd.DataFrame(
        [
            {
                "month": r.month,
                "run type": r.run_type,
                "positions": ",".join(r.positions_scored) or "-",
                "modes": r.failure_modes_logged,
                "prior-run brier": "n/a" if r.prior_run_brier is None else f"{r.prior_run_brier:.3f}",
            }
            for r in ledger
        ]
    )
    st.dataframe(ldf, hide_index=True, use_container_width=True)

top = modes[0]
moved = [
    fm
    for fm in pm.failure_modes
    if fm.status_log and fm.status_log[-1].status in ("evidence-emerging", "observed")
]
if moved:
    hot = moved[0]
    st.info(
        f"headline: {hot.id} ({hot.title}) is now "
        f"'{hot.status_log[-1].status}' -- the pre-mortem is no longer hypothetical."
    )
else:
    st.info(
        f"headline: top failure mode for {pm.position} is {top.id}: {top.title}. "
        f"nothing re-scored yet across {len(ledger)} ledger run(s) -- "
        "all modes still imagined, not observed."
    )
