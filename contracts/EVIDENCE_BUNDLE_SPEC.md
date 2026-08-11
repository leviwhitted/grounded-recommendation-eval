# Oracle Evidence Bundle Spec (v1)

## What this is
An evidence bundle is a compact, structured record of:
- what source evidence was observed,
- what findings were derived directly from that evidence,
- what inferences were made beyond direct observation,
- and what remains unknown.

It is implementation-agnostic and intended to be useful even before runtime producers or consumers exist in the repo.

## Problem this solves
- Preserves traceability from claims back to source evidence.
- Separates observed facts from interpretation.
- Prevents overclaiming when evidence is incomplete or stale.
- Provides a stable contract for future tooling without assuming stack details now.

## Required fields (v1)
- `bundle_id`: unique identifier for this bundle.
- `project_id`: repo/project-scoped identifier.
- `created_at`: bundle creation timestamp (UTC, ISO 8601 with `Z`).
- `subject`: short description of what the bundle evaluates.
- `sources`: list of source evidence records.
- `findings`: list of derived findings grounded in cited sources.
- `unknowns`: list of unresolved items explicitly kept unknown.

## Optional fields (v1)
- `inferences`: interpretation or hypotheses that go beyond direct findings.
- `confidence`: coarse confidence label plus short rationale.
- `freshness_note`: short statement about evidence freshness/staleness risk.
- `related_files`: repo-relative file paths relevant to this bundle.
- `notes`: freeform operator notes.

## Source evidence rules
Source evidence should be traceable and reviewable. Acceptable examples:
- Committed repo files.
- Versioned repository metadata (for example, commit references).
- Clearly labeled external records with stable identifiers and retrieval timestamps.

Each source record should include:
- a source id,
- source kind,
- origin/location pointer,
- retrieval timestamp,
- and optional provenance details.

## Distinguishing records
- `source`: raw observed record with provenance.
- `finding`: evidence-grounded statement that cites one or more source ids.
- `inference`: non-direct conclusion derived from findings/sources, clearly marked as interpretive.
- `unknown`: unresolved question or fact kept explicitly unknown due to missing or insufficient evidence.

## Confidence representation
- Use coarse labels, not fake numeric precision: `low`, `medium`, `high`.
- Attach a short rationale for why that confidence level is assigned.
- Confidence applies to the bundle-level interpretation, not to rewriting source evidence.

## Freshness and staleness
- `created_at` records when the bundle was assembled.
- Each source has its own retrieval timestamp.
- `freshness_note` should call out staleness risk when evidence age may affect conclusions.

## Missing evidence behavior
When evidence is missing or contradictory:
- keep unresolved items in `unknowns`,
- avoid converting unknowns into inferred facts,
- and keep confidence conservative.

## Explicitly out of scope for v1
- Runtime execution behavior or orchestration.
- Tool, package manager, CI, deployment, or environment assumptions.
- Vendor-specific adapters or APIs.
- Scoring formulas that imply unsupported precision.
