# AGENTS.md — pre-mortem-ledger

Operating contract for AI agents working in this repo. Conventions match
the rest of the portfolio so an agent already trained on
trace-to-eval-harness or thesis-pillar-tracker recognizes the shape.

## What this repo is

A typed ledger for monthly pre-mortems on the user's largest active
investing position. Each pre-mortem is a Markdown file with a fixed
schema: ranked failure modes, observability triggers per mode, and a
rolling status block updated the following month. Resolved positions
sharpen the failure-mode rubric.

This is not an investing-research tool, an alerting system, or a market
data feed. It is a discipline scaffold for the forced monthly exercise.

## Voice constraints

- No marketing words. The banlist mirrors the portfolio voice spec and
  will be enforced by `scripts/voice_lint.py` in spec 0002.
- No antithetical reversals as a structural device. The "X isn't Y; Z is
  the W" shape is the AI tell. One per surface, when the contrast does
  real work.
- Plain assertions. The rubric and the dated evidence are the spine; the
  voice is scaffolding around them.
- Pre-mortem entries are written in the second person to the user.
  Failure modes are stated as concrete events, not abstractions.

## Roles in tasks

| Role | What they do |
|---|---|
| `position-curator` | Maintains `config/positions.yaml`; tags exposure tier |
| `rubric-keeper` | Owns `rubric/failure_modes.yaml`; reviews after each resolution |
| `monthly-runner` | Renders the new pre-mortem; updates open statuses |
| `eval-curator` | Back-scores resolved pre-mortems vs realized outcomes |

Not all roles exist as code in v0. They are named here so spec 0001 has
a vocabulary to reference.

## Gates (will land in spec 0002)

```bash
uv run pytest
python scripts/voice_lint.py
python scripts/spec_check.py
python scripts/validate_premortem_schema.py
```

A PR that fails any gate is not merged.

## Out of scope

- Live market data. Inputs are the user's own position list and notes.
- Order routing. The ledger names what would trigger an action, not the
  action itself.
- Multi-user portfolios. Single-user discipline tool by design.
- Quantitative factor models. The failure modes are written-out
  hypotheses, not regression coefficients.
