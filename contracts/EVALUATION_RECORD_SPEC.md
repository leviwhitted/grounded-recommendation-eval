# Oracle Evaluation Record Spec (v1)

## What this is
An evaluation record is a judgment layer created after outcome information exists for one or more recommendations.

It captures how a recommendation is assessed based on linked outcome records. It does not replace source evidence, recommendations, or outcomes.

## How this differs from related records
- `evidence`: raw observed records with provenance.
- `finding`: statement directly grounded in evidence.
- `inference`: interpretive conclusion beyond direct observation.
- `recommendation`: suggested direction or action derived from evidence.
- `outcome`: post-recommendation observation of status/results.
- `evaluation`: assessment of recommendation quality/effectiveness using outcome information.
- `unknown`: unresolved item that limits evaluation confidence or completeness.

## Required fields (v1)
- `evaluation_record_id`: unique identifier for this evaluation record.
- `project_id`: repo/project-scoped identifier.
- `created_at`: evaluation creation timestamp (UTC, ISO 8601 with `Z`).
- `subject`: short description of what this evaluation concerns.
- `related_recommendation_ids`: one or more recommendation ids being evaluated.
- `related_outcome_record_ids`: one or more outcome record ids used for the evaluation.
- `evaluation_result`: coarse evaluation judgment.
- `evaluation_summary`: concise explanation of the judgment.
- `confidence`: coarse confidence label plus short rationale.
- `unknowns`: explicit unresolved items relevant to this evaluation (may be empty, but must be present).

## Optional fields (v1)
- `related_evidence_bundle_ids`: supporting evidence bundle ids when direct evidence context is needed.
- `notes`: freeform operator notes.

## Traceability rules
- An evaluation record must reference at least one recommendation id and at least one outcome record id.
- Evidence bundle ids are optional, but should be included when evaluation claims depend on specific evidence context.
- Evaluation statements should remain consistent with linked recommendations and outcomes.

## Evaluation result representation
- Use coarse labels only: `successful`, `partially_successful`, `unsuccessful`, `inconclusive`.
- Avoid pseudo-precise scoring or unsupported causal certainty.

## Partial or inconclusive evaluation handling
- Use `partially_successful` when results are mixed or only partly observed.
- Use `inconclusive` when available outcome data is insufficient to support a clear judgment.
- Keep unresolved limitations in `unknowns`.

## Uncertainty and missing data
- Keep confidence conservative when linked outcomes are sparse, stale, or incomplete.
- Do not convert missing data into assumed success/failure.

## Explicitly out of scope for v1
- Runtime workflow orchestration, ownership routing, or automation policies.
- Tool, package manager, CI, deployment, or environment assumptions.
- Vendor-specific adapters or product-specific implementation wiring.
- Detailed KPI frameworks or formula-based evaluation scoring systems.
