# Contracts

## Purpose
This directory defines repo-native contracts for structured project artifacts.

These contracts describe data shapes and evidence expectations. They are not runtime implementations, execution plans, or tooling choices.

## Truth-layer relationship
- Canonical code truth: committed repo state and history in Git/GitHub.
- `ai_context/`: stable orientation and workflow boundaries for this repo.
- `browser_context/`: curated browser-model handoff layer derived from committed repo truth.
- OpenBrain: later memory/context support, not canonical code truth.

## Current contract set
- `EVIDENCE_BUNDLE_SPEC.md`: human-readable v1 contract for Oracle evidence bundles.
- `evidence_bundle.schema.json`: machine-readable v1 schema.
- `examples/example_evidence_bundle.json`: synthetic, illustrative example.
- `RECOMMENDATION_SPEC.md`: human-readable v1 contract for evidence-grounded Oracle recommendations.
- `recommendation.schema.json`: machine-readable v1 schema.
- `examples/example_recommendation.json`: synthetic, illustrative example.
- `OUTCOME_RECORD_SPEC.md`: human-readable v1 contract for post-recommendation outcome records.
- `outcome_record.schema.json`: machine-readable v1 schema.
- `examples/example_outcome_record.json`: synthetic, illustrative example.
- `EVALUATION_RECORD_SPEC.md`: human-readable v1 contract for post-outcome recommendation evaluation records.
- `evaluation_record.schema.json`: machine-readable v1 schema.
- `examples/example_evaluation_record.json`: synthetic, illustrative example.
- `RECOMMENDATION_GENERATION_REQUEST_SPEC.md`: human-readable v1 app-facing request contract for recommendation generation.
- `recommendation_generation_request.schema.json`: machine-readable v1 schema.
- `examples/example_recommendation_generation_request.json`: synthetic, illustrative example.
- `RECOMMENDATION_GENERATION_RESPONSE_SPEC.md`: human-readable v1 app-facing response contract for recommendation generation.
- `recommendation_generation_response.schema.json`: machine-readable v1 schema.
- `examples/example_recommendation_generation_response.json`: synthetic, illustrative example.
- `RECOMMENDATION_DRAFT_SPEC.md`: human-readable v1 contract for generated recommendation drafts.
- `recommendation_draft.schema.json`: machine-readable v1 schema.
- `examples/example_recommendation_draft.json`: synthetic, illustrative example.
- `examples/scenarios/001_recommendation_generation_flow/`: synthetic end-to-end fixture chain across existing contract families.

## Scope boundary
- Contracts in this directory may evolve as committed repo reality evolves.
- Absence of producers/consumers in this repo is expected in the current sparse phase.
