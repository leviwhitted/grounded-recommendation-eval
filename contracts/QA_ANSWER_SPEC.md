# Oracle QA Answer Spec (v1)

## What this is
A QA answer is a structured output artifact for MarketBrew question and answer mode.

It captures the input question, the grounded prose answer, atom-level citations, unresolved gaps, and coarse confidence.

## Problem this solves
- Enforces grounding from prose answers back to audited atom ids.
- Separates unresolved gaps from supported claims.
- Creates a stable contract that generation modules can validate against.
- Preserves auditability without assuming runtime architecture.

## Required fields (v1)
- `answer_id`: unique identifier for this answer.
- `project_id`: repo/project-scoped identifier.
- `created_at`: answer creation timestamp (UTC, ISO 8601 with `Z`).
- `question`: input question echoed verbatim.
- `answer`: grounded prose answer.
- `citations`: one or more cited atom records supporting the answer.
- `unknowns`: unresolved items that the KB does not sufficiently cover.
- `confidence`: coarse confidence label plus short rationale.

## Optional fields (v1)
- `freshness_note`: statement about snapshot freshness or staleness risk.
- `related_atom_ids`: broader context atoms not directly cited in core claims.
- `notes`: freeform operator notes.

## Grounding rules
- Every substantive claim in `answer` must trace to at least one cited `atom_id`.
- Missing or insufficient KB coverage must remain in `unknowns`.
- Unknowns must not be converted into inferred facts in `answer`.

## Citation representation
Each citation item includes:
- `atom_id`: stable atom identifier.
- `atom_title`: human-readable atom title.
- `relevance_note`: short note explaining why the atom supports the claim.

## Confidence representation
- Confidence level is coarse: `low`, `medium`, `high`.
- Confidence includes a short rationale.
- Confidence should consider cited atom tier mix (`gold`, `silver`, `bronze`) and coverage completeness.

## Missing coverage behavior
When KB coverage is partial or absent:
- capture the gap in `unknowns`,
- keep answer language bounded,
- and avoid unsupported certainty.

## Explicitly out of scope for v1
- Runtime orchestration or execution flow.
- Transport details, API envelopes, or invocation semantics.
- Retrieval ranking algorithm design.
- Vendor-specific adapter behavior.
