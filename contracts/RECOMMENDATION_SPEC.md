# Oracle Recommendation Spec (v1)

## What this is
A recommendation is a derived, decision-oriented output produced from one or more evidence bundles.

It does not replace evidence. It points back to evidence bundles and states what action direction is advised, with explicit assumptions and unknowns.

## How this differs from related records
- `evidence`: raw observed records with provenance.
- `finding`: statement directly grounded in evidence.
- `inference`: interpretive conclusion that goes beyond direct observation.
- `recommendation`: suggested direction or action derived from findings/inferences and traceable to supporting evidence bundle(s).
- `unknown`: unresolved item that may affect recommendation confidence or urgency.

## Required fields (v1)
- `recommendation_id`: unique identifier for this recommendation.
- `project_id`: repo/project-scoped identifier.
- `created_at`: recommendation creation timestamp (UTC, ISO 8601 with `Z`).
- `subject`: short description of what this recommendation concerns.
- `title`: concise recommendation headline.
- `summary`: short decision-oriented summary.
- `recommendation_type`: coarse category of recommendation.
- `supporting_evidence_bundle_ids`: one or more evidence bundle ids that support this recommendation.
- `rationale`: brief explanation of why this recommendation follows from the supporting evidence.
- `confidence`: coarse confidence label plus short rationale.
- `priority`: coarse priority and urgency labels plus short rationale.
- `unknowns`: explicit list of unresolved items relevant to this recommendation (may be empty, but must be present).

## Optional fields (v1)
- `assumptions`: explicit assumptions this recommendation depends on.
- `suggested_next_steps`: short optional list of follow-up actions.
- `notes`: freeform operator notes.
- `kb_citations`: MarketBrew knowledge atoms (`atom_id`, `atom_title`, `relevance_note`) that justify the recommendation. Optional at the schema level; the recommendation engine requires at least one and rejects any unknown `atom_id`.
- `evidence_finding_citations`: client evidence findings (`finding_id`, `relevance_note`) that triggered the recommendation. Optional at the schema level; the engine requires at least one and rejects any unknown `finding_id`.
- `evidence_to_atom_trace`: one auditable sentence linking a cited client `finding_id` to a cited MarketBrew `atom_id` and the resulting action. The engine requires this and requires the trace to literally reference at least one cited id of each kind (a semantic guard against decorative citations).

> These three fields are how the engine enforces dual-citation integrity: every generated recommendation traces back to both the client signal that triggered it and the MarketBrew methodology atom that justifies it. They are optional in the base schema so earlier deterministic fixtures remain valid.

## Evidence traceability rules
- A recommendation must cite at least one `supporting_evidence_bundle_id`.
- Recommendation text must not present unsupported claims as facts.
- If supporting evidence is incomplete, recommendation confidence and priority should remain conservative.

## Rationale guidance
- Keep rationale short and evidence-linked.
- Explain the decision logic from evidence bundle(s) to recommendation.
- Separate what is known from what is assumed.

## Confidence representation
- Use coarse labels only: `low`, `medium`, `high`.
- Include a one-sentence rationale for the confidence level.

## Priority and urgency representation
- Use coarse priority levels only: `low`, `medium`, `high`.
- Use coarse urgency labels only: `immediate`, `soon`, `later`.
- Include a short rationale rather than numeric scoring.

## Unknowns and assumptions
- Keep unresolved risks or gaps in `unknowns`.
- Capture provisional premises in `assumptions`.
- Do not hide unknowns inside general notes.

## Explicitly out of scope for v1
- Execution orchestration, ownership assignment, or runtime workflow design.
- Tool, package manager, CI, deployment, or environment assumptions.
- Cost/ROI formulas or pseudo-precise numeric scoring.
- Vendor-specific adapters or product-specific implementation wiring.
