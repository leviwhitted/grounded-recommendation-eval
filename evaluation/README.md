# Evaluation: the citation-integrity gate

A frozen adversarial corpus and a deterministic runner that measure what the recommendation
engine's integrity gate actually catches.

```bash
python -m evaluation.run_integrity_eval                  # report
python -m evaluation.run_integrity_eval --json           # machine-readable
python -m evaluation.run_integrity_eval --check-baseline # exit 1 on drift
python -m evaluation.run_integrity_eval --write-baseline # re-baseline deliberately
```

No network, no API key, no model calls. Runs in well under a second, so it is usable as a
pre-commit or CI gate.

## Measured result, 2026-08-11

| | |
|---|---:|
| Referential failure classes caught | **11 / 11 (100%)** |
| Semantic failure classes caught | **0 / 5 (0%)** |
| False positives on valid recommendations | **0 / 3** |

**The zero is the point of this harness, not a defect in it.**

## Why this exists

The engine's integrity gate was described as making unsupported recommendations "impossible."
That claim was wrong, and it was wrong in a way that only measurement exposes.

The gate enforces **referential validity**: cited identifiers must exist, and the reasoning
trace must textually reference the identifiers it claims to reason from. It does **not** verify
that the reasoning is sound, that the records say what the trace claims, or that the
recommended action follows from the premises.

So this corpus is split three ways:

- **`control`** (3 cases) — well-formed recommendations that must be **accepted**. A rejection
  here is a false positive, the most damaging kind of gate failure, since it silently discards
  good output.
- **`referential`** (11 cases) — the failure classes the gate is designed to catch. All must be
  **rejected**, and most assert on the rejection *reason*, not merely that something was rejected.
- **`semantic`** (5 cases) — reasoning failures the gate cannot catch. Each is marked
  `expected="accept"` because the gate lets it through. **They are in the corpus so the blind
  spot is measured and visible rather than argued away.**

## The blind spots, enumerated

These pass the gate today. Each is a real way a recommendation can be unfounded while fully
compliant:

| Case | Failure |
|---|---|
| `sem-001-drive-by-citation` | Ids appended as a trailing parenthetical, no reasoning performed. **This is the decorative-citation case the trace guard is described as preventing, and it survives** — a substring check is satisfied by an id list |
| `sem-002-reversed-relationship` | Both ids named, causal relationship stated backwards |
| `sem-003-misdescribed-records` | Valid ids, contents of both records misstated |
| `sem-004-non-sequitur-action` | Records described correctly, recommended action does not follow |
| `sem-005-contradictory-evidence-ignored` | Cites a supporting finding while ignoring a contradicting one in the same bundle. Invisible to a per-recommendation gate by construction |

Closing these needs a different mechanism: entailment checking between the trace and the cited
record text, bundle-level review for selective citation, and a judge with measured agreement
against human labels. That is the next layer, and **none of it is claimed here.**

## What the numbers do and do not support

**Supported:** the gate rejects every enumerated referential failure, distinguishes them by
reason, and does not reject valid recommendations.

**Not supported:** any claim about groundedness, factual correctness, calibration, decision
quality, or safety. Structural conformance is not correctness. An 11/11 catch rate on
referential failures says nothing about whether surviving recommendations are *right*.

## Regression use

`baseline.json` records the verdict per case. `--check-baseline` exits non-zero when any case
changes verdict or the corpus gains or loses a case.

**Verified 2026-08-11:** replacing the gate with a permissive stub produces 11 drift entries and
fails the run, so the detector is not vacuous.

A semantic case flipping to `reject` is an **improvement**, not a regression. Update the case's
`expected` field and re-baseline deliberately when that happens.

## Relationship to `validator/tests`

`validator/tests` (59 tests) covers schema and contract conformance: are artifacts shaped
correctly, do parsers reject malformed input. **This directory covers something different** —
whether the gate that decides which generated recommendations survive actually behaves as
described, and where it stops working.

## Not covered here

Generation-time behaviour is untested by this harness because it needs live model calls: drop
rate on real generations, failure distribution by reason in production, gap-declaration
behaviour against a deliberately pruned corpus, and prompt or model regression comparisons.
Those require an API key and a spend decision. **The corpus and runner are structured so those
suites can be added alongside rather than replacing this one.**
