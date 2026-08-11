# Scenario 001: Recommendation Generation Flow (Synthetic)

## Purpose
This scenario is a fully synthetic, end-to-end fixture showing how existing Oracle contracts connect across one bounded flow.

## Synthetic-only notice
All values in this folder are illustrative placeholders. They are not client data and not MarketBrew production records.

## Intended flow
- Evidence bundle input is established.
- A recommendation generation request references that evidence bundle.
- A recommendation generation response returns recommendation draft output.
- A persisted recommendation record is represented as a separate artifact.
- An outcome record captures what was observed after acting on the persisted recommendation.
- An evaluation record judges the recommendation using outcome context.

## Lineage map
- `evidence_bundle_01.json`
  - `bundle_id`: `scenario-001-bundle-01`
- `recommendation_generation_request_01.json`
  - `request_id`: `scenario-001-recgen-req-01`
  - `evidence_bundle_ids`: `scenario-001-bundle-01`
- `recommendation_generation_response_01.json`
  - `response_id`: `scenario-001-recgen-res-01`
  - `request_id`: `scenario-001-recgen-req-01`
  - `generated_recommendations[0].draft_id`: `scenario-001-rec-draft-01`
- `recommendation_draft_01.json`
  - mirrors the draft object embedded in `recommendation_generation_response_01.json`
  - `draft_id`: `scenario-001-rec-draft-01`
- `recommendation_01.json`
  - persisted recommendation artifact
  - `recommendation_id`: `scenario-001-rec-01`
  - based on `scenario-001-rec-draft-01`
- `outcome_record_01.json`
  - `outcome_record_id`: `scenario-001-outcome-01`
  - `related_recommendation_ids`: `scenario-001-rec-01`
- `evaluation_record_01.json`
  - `evaluation_record_id`: `scenario-001-eval-01`
  - `related_recommendation_ids`: `scenario-001-rec-01`
  - `related_outcome_record_ids`: `scenario-001-outcome-01`

## Intentionally unknown
- The exact runtime mechanism that would promote draft to persisted recommendation.
- The specific producer/consumer components that would own each artifact in real operation.
