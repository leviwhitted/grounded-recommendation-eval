# Oracle Recommendation Generation Request Spec (v1)

## What this is
This contract defines a minimal app-facing request that asks Oracle to generate recommendation output from known evidence bundle ids.

It is a boundary wrapper for recommendation generation. It is not raw evidence and not runtime orchestration logic.

## Required fields (v1)
- `request_id`: unique identifier for this request.
- `project_id`: repo/project-scoped identifier.
- `created_at`: request creation timestamp (UTC, ISO 8601 with `Z`).
- `subject`: short description of what recommendation generation should address.
- `evidence_bundle_ids`: one or more evidence bundle ids to use as generation input.

## Optional fields (v1)
- `request_scope`: short scope statement to bound recommendation generation.
- `constraints`: short list of constraints or preferences to respect.
- `known_unknowns`: unresolved items the caller already knows about.
- `notes`: freeform caller notes.

## Evidence input rules
- Inputs are evidence bundle ids, not raw source records.
- Evidence ids should refer to existing bundle artifacts in the same project context.
- If evidence is incomplete, callers should pass known gaps in `known_unknowns`.

## Subject and scope guidance
- `subject` should be concise and decision-oriented.
- `request_scope` should bound what to include/exclude without prescribing implementation details.

## Constraints, preferences, and unknowns
- Keep `constraints` short and coarse.
- Use `known_unknowns` for unresolved facts or ambiguity that may affect recommendation quality.
- Do not encode stack/tooling policy in this contract.

## Explicitly out of scope for v1
- Runtime execution plans, orchestration, or producer/consumer wiring.
- Tool, package manager, CI, deployment, or environment assumptions.
- Vendor-specific adapters or API integration details.
- Rich policy/ranking engines for recommendation generation behavior.
