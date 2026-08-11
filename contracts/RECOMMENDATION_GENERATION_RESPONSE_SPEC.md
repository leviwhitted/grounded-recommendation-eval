# Oracle Recommendation Generation Response Spec (v1)

## What this is
This contract defines a minimal app-facing response for recommendation generation.

It returns generated recommendation output grounded in evidence-bundle input, plus unresolved unknowns and warnings when applicable.

## Required fields (v1)
- `response_id`: unique identifier for this response.
- `request_id`: id of the request this response answers.
- `project_id`: repo/project-scoped identifier.
- `created_at`: response creation timestamp (UTC, ISO 8601 with `Z`).
- `subject`: short description of the generation subject.
- `generated_recommendations`: list of generated recommendation drafts (`recommendation_draft.schema.json`).
- `unresolved_unknowns`: unresolved items that remain after generation (may be empty, but must be present).

## Optional fields (v1)
- `warnings`: coarse limitations or caveats about this generation result.
- `notes`: freeform operator/system notes.

## Generated recommendation representation
- `generated_recommendations` contains `recommendation_draft` objects, not persisted recommendations.
- Draft structure is defined by `recommendation_draft.schema.json`.
- This response wrapper returns draft outputs only; promotion/materialization behavior is intentionally out of scope.

## Unknowns, warnings, and limitations
- Keep unresolved uncertainty in `unresolved_unknowns`.
- Use `warnings` for caveats such as sparse evidence coverage or conflicting inputs.
- Do not present unresolved unknowns as settled conclusions.

## Wrapper boundary
- This response is an app-facing wrapper, not a runtime orchestration contract.
- It does not require a specific storage, transport, execution, or deployment mechanism.

## Explicitly out of scope for v1
- Runtime producer/consumer design and orchestration semantics.
- Tool, package manager, CI, deployment, or environment assumptions.
- Vendor-specific adapters or API integration wiring.
- Advanced paging, streaming, ranking, or policy engine behavior.
