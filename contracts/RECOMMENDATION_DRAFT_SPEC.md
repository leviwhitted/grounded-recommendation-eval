# Oracle Recommendation Draft Spec (v1)

## What this is
A recommendation draft is generated recommendation output that is not yet a persisted recommendation record.

It is intended for app-facing generation results and review. This contract does not define how or whether a draft is promoted.

## How this differs from related records
- `evidence`: raw observed records with provenance.
- `finding`/`inference`: evidence-grounded and interpretive reasoning layers.
- persisted `recommendation`: stable recommendation artifact defined by `recommendation.schema.json`.
- response wrapper: app-facing envelope that may carry one or more recommendation drafts.
- `recommendation draft`: recommendation-shaped generated content intended for possible future materialization.

## Required fields (v1)
- `draft_id`: unique identifier for this draft output.
- `subject`: short description of what this draft concerns.
- `title`: concise recommendation headline.
- `summary`: short decision-oriented summary.
- `recommendation_type`: coarse recommendation category.
- `supporting_evidence_bundle_ids`: one or more evidence bundle ids grounding this draft.
- `rationale`: brief explanation of why this draft follows from the cited evidence.
- `confidence`: coarse confidence label plus short rationale.
- `priority`: coarse priority and urgency labels plus short rationale.
- `unknowns`: explicit unresolved items relevant to this draft (may be empty, but must be present).

## Optional fields (v1)
- `assumptions`: explicit assumptions this draft depends on.
- `suggested_next_steps`: optional follow-up actions.
- `notes`: freeform notes.

## Evidence linkage rules
- Each draft must cite at least one `supporting_evidence_bundle_id`.
- Draft statements should not present unsupported claims as settled facts.

## Confidence and priority representation
- Confidence levels are coarse: `low`, `medium`, `high`.
- Priority levels are coarse: `low`, `medium`, `high`.
- Urgency labels are coarse: `immediate`, `soon`, `later`.
- Avoid pseudo-precise scoring.

## Unknowns and assumptions
- Keep unresolved gaps in `unknowns`.
- Keep provisional premises in `assumptions`.
- Do not hide uncertainty in general notes.

## Explicitly out of scope for v1
- Promotion/materialization workflow mechanics.
- Runtime orchestration, producer/consumer wiring, or automation semantics.
- Tool, package manager, CI, deployment, or environment assumptions.
- Vendor-specific adapters or API integration details.
