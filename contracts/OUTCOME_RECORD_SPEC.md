# Oracle Outcome Record Spec (v1)

## What this is
An outcome record captures what was observed after one or more recommendations were made.

It records outcome status and observed results. It does not replace source evidence and does not restate recommendation logic.

## How this differs from related records
- `evidence`: raw observed records with provenance.
- `finding`: statement directly grounded in evidence.
- `inference`: interpretive conclusion beyond direct observation.
- `recommendation`: suggested direction or action derived from evidence.
- `outcome`: post-recommendation record of observed status/results.
- `unknown`: unresolved item that limits outcome interpretation.

## Required fields (v1)
- `outcome_record_id`: unique identifier for this outcome record.
- `project_id`: repo/project-scoped identifier.
- `created_at`: record creation timestamp (UTC, ISO 8601 with `Z`).
- `subject`: short description of what this outcome concerns.
- `related_recommendation_ids`: one or more recommendation ids this outcome evaluates.
- `status`: coarse status of recommendation progress/state.
- `observed_result`: concise statement of what was observed.
- `confidence`: coarse confidence label plus short rationale.
- `unknowns`: explicit list of unresolved items relevant to the outcome (may be empty, but must be present).

## Optional fields (v1)
- `related_evidence_bundle_ids`: supporting evidence bundle ids when evidence linkage is needed for interpretation.
- `impact_summary`: short summary of observed impact.
- `notes`: freeform operator notes.

## Traceability rules
- An outcome record must reference at least one recommendation id.
- An outcome record may reference evidence bundle ids when result interpretation depends on specific evidence context.
- Outcome statements should be consistent with linked recommendations and any cited evidence bundles.

## Status and result representation
- Use coarse status labels only: `not_started`, `in_progress`, `completed`, `blocked`, `inconclusive`.
- Keep `observed_result` descriptive and factual; avoid unsupported causal certainty.

## Uncertainty and incomplete observation
- If observation is partial or ambiguous, keep confidence conservative.
- Keep unresolved gaps in `unknowns` rather than implying completion or impact that is not observed.

## Timestamps and freshness
- `created_at` records when the outcome record was assembled.
- Outcome records are point-in-time snapshots; they do not claim permanence.
- When observations may have aged, capture that limitation in `notes` or `unknowns`.

## Explicitly out of scope for v1
- Runtime execution behavior, orchestration, or status automation design.
- Tool, package manager, CI, deployment, or environment assumptions.
- Vendor-specific adapters or product-specific implementation wiring.
- Detailed KPI frameworks or pseudo-precise impact scoring formulas.
