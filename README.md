# Grounded recommendations, and how to test that they are grounded

An LLM recommendation engine where **every recommendation must cite both the observation that triggered
it and the domain rule that justifies it**, the citations are enforced rather than requested, and there
is a harness that measures exactly which failure classes the enforcement catches and which it does not.

This repository contains the **schema contracts** and the **evaluation harness**. It is a curated extract
from a larger private engine, and what has been left out is described at the bottom.

```bash
python -m evaluation.run_integrity_eval
```

No API key, no network, no model calls. Runs in well under a second.

## The measured result

```
Referential failure classes caught : 11/11  (100%)
Semantic failure classes caught    :  0/5   (0%)   <- by design, not a defect
False positives on valid cases     :  0/3
```

**The zero is the most useful number here**, and it is why this repository exists.

## The problem

A recommendation someone has to defend in public is a different engineering problem from one they can
quietly ignore.

If a model suggests a blog post, nobody audits it. If a model suggests deferring a capital project or
changing a treatment plan, somebody eventually stands in a room and explains why. At that moment the
question is not whether the model was confident. It is: which observation triggered this, which rule
justifies it, can the chain be reproduced from the inputs as they were at the time, and **if the model
could not substantiate the recommendation, did the system say so or did it produce something plausible
anyway?**

The last one is the hard part, because language models are good at plausible. A system that cannot
distinguish grounded from plausible will eventually surface a confident recommendation with nothing
underneath it, and the failure stays invisible until somebody checks.

## The mechanism

Every recommendation carries three things:

- `evidence_finding_citations` — the client observations that triggered it, by `finding_id`
- `kb_citations` — the domain-methodology atoms that justify it, by `atom_id`
- `evidence_to_atom_trace` — one auditable sentence: *"Because the client shows [finding], and [atom]
  says …, do [action]."*

A single function, [`gate.py`](gate.py), decides whether a generated recommendation survives. It runs
after generation and before anything reaches the caller, and it checks:

1. Both citation lists are present and non-empty.
2. The trace exists and is not whitespace.
3. Every cited `atom_id` exists in the active knowledge-base snapshot.
4. Every cited `finding_id` exists in this request's evidence bundle.
5. **The trace textually references at least one cited `atom_id` and one cited `finding_id`.**

Be precise about check five, because it is weaker than it first sounds: it requires *any one* atom id and
*any one* finding id to appear in the trace. It does **not** require every identifier the recommendation
cites to be referenced, and it does not evaluate the reasoning. A recommendation citing three atoms passes
if the trace mentions one.

Failing any check **drops that recommendation**. Not a warning, not a lowered score. Survivors are then
ranked.

Check five exists because checks three and four only catch invented identifiers. They do not catch a
model citing perfectly valid identifiers and then writing a trace that has nothing to do with them,
which produces a recommendation that passes every referential test and is still unfounded, with a
citation list attached as decoration.

## What the harness found, including about itself

The corpus is 19 cases in three groups. The interesting group is the third.

**`control` (3 cases)** — well-formed recommendations that must be **accepted**. A rejection here is a
false positive, the most damaging kind of gate failure, because it silently discards good output.

**`referential` (11 cases)** — the failure classes the gate is built for. All must be **rejected**, and
most assert on the rejection *reason*, not merely that something was rejected. Covers absent citation
lists, empty lists, missing and whitespace traces, invented atom ids, invented finding ids, a valid
citation sitting beside an invented one, traces that omit the atom, traces that omit the finding, and
traces that name real ids which are not the ones actually cited.

**`semantic` (5 cases)** — reasoning failures the gate **cannot** catch. Each is marked
`expected="accept"`, because the gate lets it through. **They are in the corpus so the blind spot is
measured and visible rather than argued away:**

| Case | The failure |
|---|---|
| `sem-001-drive-by-citation` | Ids appended as a trailing parenthetical, no reasoning performed. **This is the decorative-citation case check five is described as preventing, and it survives** — a substring test is satisfied by an id list |
| `sem-002-reversed-relationship` | Both ids named, causal relationship stated backwards |
| `sem-003-misdescribed-records` | Valid ids, contents of both records misstated |
| `sem-004-non-sequitur-action` | Records described correctly, recommended action does not follow |
| `sem-005-contradictory-evidence-ignored` | Cites a supporting finding while ignoring a contradicting one in the same bundle. Invisible to a per-recommendation gate by construction |

`sem-001` is the finding I would not have reached by reading the code. The guard is real and it is
weaker than its description.

## What the numbers support, and what they do not

**Supported:** the gate rejects every enumerated referential failure, distinguishes them by reason, and
does not reject valid recommendations.

**Not supported:** any claim about groundedness, factual correctness, calibration, decision quality or
safety. Structural conformance is not correctness. **An 11/11 referential catch rate says nothing about
whether the surviving recommendations are right.** Closing the semantic gap needs entailment checking
between trace and cited record text, bundle-level review for selective citation, and a judge with
measured agreement against human labels. None of that is claimed here.

## Design decisions worth arguing about

**Two surfaces fail differently, deliberately.** The recommendation path drops the individual offending
item and returns the survivors. The question-answering path invalidates the **entire answer** on one
unmatched identifier. A recommendation list is severable, so removing one bad item leaves the rest
trustworthy. A prose answer is not: if one claim cites something that does not exist, you have learned
something about the whole answer, and salvaging the paragraphs you happen to like is how a bad answer
survives review.

**Gaps are declared, not filled.** `unresolved_unknowns` is a first-class response field, and `unknowns`
is a **required** field on an evaluation record that may be empty but must be present. Pedantic, and it
is the difference between a system that has considered its own limits and one where nobody had to.

**Confidence is tied to source tier, not model self-report.** A recommendation resting on a gold-tier
atom and one resting on bronze do not get equal confidence because the model wrote both fluently.

**Coarse evaluation labels only** — `successful`, `partially_successful`, `unsuccessful`,
`inconclusive`. [`EVALUATION_RECORD_SPEC.md`](contracts/EVALUATION_RECORD_SPEC.md) forbids pseudo-precise
scoring, and states: **"Do not convert missing data into assumed success/failure."** Most evaluation
systems degrade quietly, where sparse data becomes a middling score, the score becomes a trend line, and
the trend line reaches someone making a decision. Refusing that conversion at the schema level is
cheaper than catching it later.

## The record taxonomy

Seven types with defined boundaries: `evidence`, `finding`, `inference`, `recommendation`, `outcome`,
`evaluation`, `unknown`. Collapsing `finding` into `inference` is how an interpretation becomes a fact
downstream. Collapsing `outcome` into `evaluation` is how "we did the thing" becomes "the thing worked."
Keeping them separate in the schema makes the collapse deliberate rather than accidental.

## Layout

```
gate.py                     the integrity gate, extracted verbatim from the engine
evaluation/
  cases.py                  the 19-case frozen adversarial corpus
  run_integrity_eval.py     runner, reporting, baseline comparison
  baseline.json             committed baseline for regression detection
  README.md                 what is measured and what is not
contracts/
  *_SPEC.md                 nine specifications
  *.schema.json             eight JSON schemas
  examples/                 worked examples, including an end-to-end scenario
```

`--check-baseline` exits non-zero when any case changes verdict. **Verified non-vacuous:** replacing the
gate with a permissive stub produces 11 drift entries and fails the run.

A semantic case flipping to `reject` is an **improvement**, not a regression. Update that case's
`expected` field and re-baseline deliberately.

## What is not in this repository, and why

This is a curated extract, not the whole system.

- **`gate.py` is a verbatim copy**, not the live import. The harness in the private repo imports the
  function directly from the engine; here it is reproduced byte for byte so the harness is runnable
  standalone. It has no dependencies beyond the standard library, which is what makes that possible.
- **The engine itself is not here** — corpus loading, prompt construction, the Anthropic API layer,
  structured-output handling, ranking, CLI. Roughly 3,900 lines of Python across 41 modules, plus 59
  contract tests, in a private repository.
- **No knowledge-base content and no client data.** The domain corpus is third-party methodology and is
  not mine to publish. The examples here are synthetic.
- **Generation-time evaluation is not here** because it needs live model calls: real drop rates, failure
  distribution in production, gap-declaration behaviour against a deliberately pruned corpus, and
  prompt-or-model regression comparisons.

**Honest status:** the engine was demonstrated end to end against a synthetic client fixture. It has not
run as a paid production deployment. The harness in this repository is real, runs on every commit if you
wire it up, and its numbers are reproducible in under a second.

---

Levi Whitted · [sonomasolutions.io](https://sonomasolutions.io) · levi@sonomasolutions.io
