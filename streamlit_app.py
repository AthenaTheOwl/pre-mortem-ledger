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
from pre_mortem_ledger.score import (
    brier_score,
    outcome_for_status,
    rank_to_prior,
)

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

st.divider()

# ---------------------------------------------------------------------------
# interactive: score the calibration yourself
#
# everything above reads the committed pre-mortem off disk. below, you drive
# the repo's real calibration engine -- pre_mortem_ledger.score -- on input
# you control. set each failure mode's rank (most-likely .. least-likely) and
# what actually happened (its status), and the live Brier score recomputes via
# the same rank_to_prior / outcome_for_status / brier_score functions the
# `premortem ledger score` path uses. nothing is hardcoded here; the numbers
# come straight out of the engine.
# ---------------------------------------------------------------------------

st.subheader("score the calibration yourself")
st.caption(
    "a pre-mortem ranks failure modes by how likely you think they are. months "
    "later you mark what actually happened. the Brier score grades that forecast: "
    "0.0 is perfect, higher is worse. set the ranks and the observed outcomes "
    "below and the real engine recomputes it live."
)

_STATUS_CHOICES = ["unchanged", "evidence-emerging", "observed", "retired"]
_STATUS_HELP = {
    "unchanged": "trigger never fired -- a non-event (outcome 0.0)",
    "evidence-emerging": "the named signal is starting to show up (outcome 0.5)",
    "observed": "the failure mode actually played out (outcome 1.0)",
    "retired": "no longer a live risk -- a non-event (outcome 0.0)",
}

with st.form("calibration"):
    n_modes = st.slider(
        "how many failure modes in this pre-mortem?",
        min_value=1,
        max_value=8,
        value=min(len(pm.failure_modes), 8),
        help="rank_to_prior maps rank 1 -> 0.6 and rank N -> 0.2 across this many modes.",
    )

    # seed defaults from the committed pre-mortem so the form starts on a real
    # example, then let the user edit freely.
    seeded = sorted(pm.failure_modes, key=lambda f: f.rank)
    rows = []
    for i in range(n_modes):
        seed_fm = seeded[i] if i < len(seeded) else None
        default_label = seed_fm.title if seed_fm else f"failure mode {i + 1}"
        seed_status = (
            seed_fm.status_log[-1].status
            if seed_fm and seed_fm.status_log
            else "unchanged"
        )
        cols = st.columns([1, 4, 3])
        with cols[0]:
            st.markdown(f"**rank {i + 1}**")
            st.caption(f"prior {rank_to_prior(i + 1, n_modes):.2f}")
        with cols[1]:
            label = st.text_input(
                "failure mode",
                value=default_label,
                key=f"label_{i}",
                label_visibility="collapsed",
            )
        with cols[2]:
            status = st.selectbox(
                "what actually happened?",
                _STATUS_CHOICES,
                index=_STATUS_CHOICES.index(seed_status),
                key=f"status_{i}",
                label_visibility="collapsed",
                help="\n".join(f"{k}: {v}" for k, v in _STATUS_HELP.items()),
            )
        rows.append((i + 1, label, status))

    submitted = st.form_submit_button("compute Brier score")

# build the (predicted, observed) pairs from user input and call the REAL
# engine. predicted comes from rank_to_prior, observed from outcome_for_status,
# and the grade from brier_score -- no reimplementation.
pairs = [
    (rank_to_prior(rank, n_modes), outcome_for_status(status))
    for rank, _label, status in rows
]
score = brier_score(pairs)

st.metric(
    "live Brier score (pre_mortem_ledger.score.brier_score)",
    f"{score:.4f}",
    help="mean squared error of your priors against what you marked as observed; 0.0 is a perfect forecast.",
)

if score <= 0.10:
    st.success(
        "well calibrated -- your ranks lined up with what played out. "
        "a low Brier is what a disciplined pre-mortem loop should converge toward."
    )
elif score <= 0.25:
    st.info("middling calibration -- the ranking captured some of the outcome but not all of it.")
else:
    st.warning(
        "poorly calibrated -- the things you ranked most likely are not the ones that "
        "happened (or vice versa). this is exactly the drift the monthly ledger exists to surface."
    )

st.markdown("**(predicted prior, observed outcome) pairs fed to the engine**")
pair_df = pd.DataFrame(
    [
        {
            "rank": rank,
            "failure mode": label,
            "predicted prior": f"{rank_to_prior(rank, n_modes):.2f}",
            "status": status,
            "observed outcome": f"{outcome_for_status(status):.1f}",
            "squared error": f"{(rank_to_prior(rank, n_modes) - outcome_for_status(status)) ** 2:.4f}",
        }
        for rank, label, status in rows
    ]
)
st.dataframe(pair_df, hide_index=True, use_container_width=True)
st.caption(
    "every number above is computed by importing and calling the package: "
    "`rank_to_prior`, `outcome_for_status`, and `brier_score` from "
    "`pre_mortem_ledger.score`. flip a status from `unchanged` to `observed` "
    "and watch the squared error and the Brier move."
)
