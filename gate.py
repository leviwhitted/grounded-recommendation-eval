"""The citation-integrity gate, extracted verbatim from the production engine.

This function is a byte-for-byte copy of ``_integrity_reason`` in the private recommendation
engine (``implementation/recommend/recommend_engine.py``). It is reproduced here, rather than
reimplemented, so the evaluation harness in this repository measures the real gate instead of a
paraphrase that could quietly drift from it.

It has no dependencies beyond the standard library, which is why extracting it is possible without
shipping the surrounding engine.

The gate returns a rejection reason string, or ``None`` when the recommendation passes.
"""

from __future__ import annotations

from typing import Any


def _integrity_reason(
    rec: dict[str, Any], known_atom_ids: set[str], known_finding_ids: set[str]
) -> str | None:
    """Return a rejection reason if the recommendation violates citation integrity, else None."""
    kb_citations = rec.get("kb_citations") or []
    finding_citations = rec.get("evidence_finding_citations") or []
    trace = rec.get("evidence_to_atom_trace") or ""

    if not kb_citations:
        return "missing kb_citations (no MarketBrew atom cited)"
    if not finding_citations:
        return "missing evidence_finding_citations (no client finding cited)"
    if not trace.strip():
        return "missing evidence_to_atom_trace"

    cited_atom_ids = [c.get("atom_id", "") for c in kb_citations]
    unknown_atoms = sorted({a for a in cited_atom_ids if a not in known_atom_ids})
    if unknown_atoms:
        return f"unknown atom_id(s): {', '.join(unknown_atoms)}"

    cited_finding_ids = [c.get("finding_id", "") for c in finding_citations]
    unknown_findings = sorted({f for f in cited_finding_ids if f not in known_finding_ids})
    if unknown_findings:
        return f"unknown finding_id(s): {', '.join(unknown_findings)}"

    # Semantic trace guard: the trace must reference at least one cited id of each kind,
    # so a real-but-decorative citation cannot pass on id-existence alone.
    if not any(aid and aid in trace for aid in cited_atom_ids):
        return "evidence_to_atom_trace does not reference any cited atom_id"
    if not any(fid and fid in trace for fid in cited_finding_ids):
        return "evidence_to_atom_trace does not reference any cited finding_id"
    return None
