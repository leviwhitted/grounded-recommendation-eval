"""Frozen adversarial corpus for the citation-integrity gate.

Every case is a recommendation object shaped as the model is required to emit one, paired
with the verdict the gate SHOULD return. Cases are grouped into three classes:

- ``control``     : well-formed recommendations that must be ACCEPTED. Any rejection here is a
                    false positive, which is the most damaging failure a gate can have.
- ``referential`` : structural or identifier violations the gate is designed to catch. These
                    must ALL be rejected.
- ``semantic``    : reasoning failures the gate is NOT designed to catch, documented here on
                    purpose. Each carries ``expected="accept"`` because the gate lets them
                    through. They exist so the system's blind spot is measured and visible
                    rather than asserted away.

The semantic block is the honest answer to "does this make unsupported recommendations
impossible?" It does not. It makes a specific, enumerated set of referential failures
impossible, and this corpus is where the boundary is written down.

Do not edit a case to make a run pass. Add a case, or fix the gate.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict


# --- Fixture world -------------------------------------------------------------------
# A deliberately tiny known universe. The gate takes id sets, so a small fixture exercises
# it exactly as a full snapshot would.

KNOWN_ATOM_IDS: set[str] = {"A-CANON-001", "A-SPEED-014", "A-SCHEMA-022"}
KNOWN_FINDING_IDS: set[str] = {"F-DUP-001", "F-LCP-002", "F-NOSCHEMA-003"}


class Case(TypedDict):
    case_id: str
    klass: Literal["control", "referential", "semantic"]
    failure_mode: str
    expected: Literal["accept", "reject"]
    expected_reason_contains: str | None
    note: str
    rec: dict[str, Any]


def _rec(
    atoms: list[str],
    findings: list[str],
    trace: str,
    *,
    drop_kb: bool = False,
    drop_findings: bool = False,
) -> dict[str, Any]:
    """Build a recommendation payload in the shape recommend_engine expects."""
    payload: dict[str, Any] = {
        "recommendation_title": "Fixture recommendation",
        "action": "Do the thing described in the trace.",
        "evidence_to_atom_trace": trace,
        "priority": {"impact": 3, "effort": 2},
    }
    if not drop_kb:
        payload["kb_citations"] = [
            {"atom_id": a, "atom_title": f"Atom {a}", "relevance_note": "fixture"} for a in atoms
        ]
    if not drop_findings:
        payload["evidence_finding_citations"] = [
            {"finding_id": f, "finding_summary": f"Finding {f}"} for f in findings
        ]
    return payload


# A trace that genuinely reasons, and names both ids inline.
GOOD_TRACE = (
    "Because the client shows F-DUP-001 (duplicate title tags across 40 templated pages), "
    "and MarketBrew A-CANON-001 says duplicate titles dilute canonical signals and suppress "
    "the preferred URL, consolidate the templates onto one canonical title pattern."
)


CASES: list[Case] = [
    # ---------------- controls: must be accepted ----------------
    {
        "case_id": "ctl-001-well-formed",
        "klass": "control",
        "failure_mode": "none",
        "expected": "accept",
        "expected_reason_contains": None,
        "note": "The baseline good case. A rejection here is a false positive.",
        "rec": _rec(["A-CANON-001"], ["F-DUP-001"], GOOD_TRACE),
    },
    {
        "case_id": "ctl-002-multi-citation",
        "klass": "control",
        "failure_mode": "none",
        "expected": "accept",
        "expected_reason_contains": None,
        "note": "Several atoms and findings cited; trace names one of each. Gate requires ANY, not ALL.",
        "rec": _rec(
            ["A-CANON-001", "A-SCHEMA-022"],
            ["F-DUP-001", "F-NOSCHEMA-003"],
            GOOD_TRACE,
        ),
    },
    {
        "case_id": "ctl-003-ids-mid-sentence",
        "klass": "control",
        "failure_mode": "none",
        "expected": "accept",
        "expected_reason_contains": None,
        "note": "Ids appear mid-sentence with punctuation adjacency. Guards against a brittle substring match.",
        "rec": _rec(
            ["A-SPEED-014"],
            ["F-LCP-002"],
            "Because F-LCP-002, an LCP of 4.8s on mobile templates, and A-SPEED-014, which ties "
            "LCP to crawl budget, defer the hero carousel.",
        ),
    },

    # ---------------- referential: must be rejected ----------------
    {
        "case_id": "ref-001-no-kb-citations",
        "klass": "referential",
        "failure_mode": "kb_citations absent entirely",
        "expected": "reject",
        "expected_reason_contains": "missing kb_citations",
        "note": "Model produced advice with no methodology basis at all.",
        "rec": _rec([], ["F-DUP-001"], GOOD_TRACE, drop_kb=True),
    },
    {
        "case_id": "ref-002-empty-kb-citations",
        "klass": "referential",
        "failure_mode": "kb_citations present but empty list",
        "expected": "reject",
        "expected_reason_contains": "missing kb_citations",
        "note": "Empty list must be treated as absent, not as satisfied.",
        "rec": _rec([], ["F-DUP-001"], GOOD_TRACE),
    },
    {
        "case_id": "ref-003-no-finding-citations",
        "klass": "referential",
        "failure_mode": "evidence_finding_citations absent",
        "expected": "reject",
        "expected_reason_contains": "missing evidence_finding_citations",
        "note": "Generic best-practice advice untethered from this client's data.",
        "rec": _rec(["A-CANON-001"], [], GOOD_TRACE, drop_findings=True),
    },
    {
        "case_id": "ref-004-missing-trace",
        "klass": "referential",
        "failure_mode": "evidence_to_atom_trace absent",
        "expected": "reject",
        "expected_reason_contains": "missing evidence_to_atom_trace",
        "note": "Citations without the auditable sentence a human actually reads.",
        "rec": _rec(["A-CANON-001"], ["F-DUP-001"], ""),
    },
    {
        "case_id": "ref-005-whitespace-trace",
        "klass": "referential",
        "failure_mode": "trace is whitespace only",
        "expected": "reject",
        "expected_reason_contains": "missing evidence_to_atom_trace",
        "note": "Whitespace must not satisfy a presence check.",
        "rec": _rec(["A-CANON-001"], ["F-DUP-001"], "   \n\t  "),
    },
    {
        "case_id": "ref-006-fabricated-atom",
        "klass": "referential",
        "failure_mode": "atom_id not in the knowledge base",
        "expected": "reject",
        "expected_reason_contains": "unknown atom_id",
        "note": "The canonical hallucination: an invented but plausible methodology id.",
        "rec": _rec(
            ["A-CANON-999"],
            ["F-DUP-001"],
            "Because the client shows F-DUP-001, and MarketBrew A-CANON-999 says so, act.",
        ),
    },
    {
        "case_id": "ref-007-fabricated-finding",
        "klass": "referential",
        "failure_mode": "finding_id not in the client evidence bundle",
        "expected": "reject",
        "expected_reason_contains": "unknown finding_id",
        "note": "Invented client evidence. Arguably worse than an invented atom.",
        "rec": _rec(
            ["A-CANON-001"],
            ["F-GHOST-404"],
            "Because the client shows F-GHOST-404, and MarketBrew A-CANON-001 applies, act.",
        ),
    },
    {
        "case_id": "ref-008-one-valid-one-fabricated-atom",
        "klass": "referential",
        "failure_mode": "mixed valid and invented atom ids",
        "expected": "reject",
        "expected_reason_contains": "unknown atom_id",
        "note": "A valid citation must not launder an invalid one sitting beside it.",
        "rec": _rec(
            ["A-CANON-001", "A-FAKE-777"],
            ["F-DUP-001"],
            GOOD_TRACE,
        ),
    },
    {
        "case_id": "ref-009-trace-omits-atom",
        "klass": "referential",
        "failure_mode": "valid ids cited, trace references no atom_id",
        "expected": "reject",
        "expected_reason_contains": "does not reference any cited atom_id",
        "note": "The decorative-citation guard. Citations valid, trace does not use the atom.",
        "rec": _rec(
            ["A-CANON-001"],
            ["F-DUP-001"],
            "Because the client shows F-DUP-001, consolidate the duplicate titles.",
        ),
    },
    {
        "case_id": "ref-010-trace-omits-finding",
        "klass": "referential",
        "failure_mode": "valid ids cited, trace references no finding_id",
        "expected": "reject",
        "expected_reason_contains": "does not reference any cited finding_id",
        "note": "Methodology asserted without naming the client observation that triggered it.",
        "rec": _rec(
            ["A-CANON-001"],
            ["F-DUP-001"],
            "MarketBrew A-CANON-001 says duplicate titles dilute canonical signals, so consolidate.",
        ),
    },
    {
        "case_id": "ref-011-trace-names-uncited-ids",
        "klass": "referential",
        "failure_mode": "trace names real ids that are not the ones cited",
        "expected": "reject",
        "expected_reason_contains": "does not reference any cited",
        "note": (
            "Subtle: every id mentioned exists in the known universe, and every cited id is "
            "valid, but the trace reasons from different records than it cites."
        ),
        "rec": _rec(
            ["A-CANON-001"],
            ["F-DUP-001"],
            "Because the client shows F-LCP-002, and MarketBrew A-SPEED-014 says so, act.",
        ),
    },

    # ---------------- semantic: documented blind spots, gate accepts ----------------
    {
        "case_id": "sem-001-drive-by-citation",
        "klass": "semantic",
        "failure_mode": "ids appended as a parenthetical, no reasoning performed",
        "expected": "accept",
        "expected_reason_contains": None,
        "note": (
            "PASSES. The substring check is satisfied by a trailing id list. This is the exact "
            "decorative-citation case the guard is described as preventing, and it survives."
        ),
        "rec": _rec(
            ["A-CANON-001"],
            ["F-DUP-001"],
            "Consolidate the duplicate titles. (F-DUP-001, A-CANON-001)",
        ),
    },
    {
        "case_id": "sem-002-reversed-relationship",
        "klass": "semantic",
        "failure_mode": "both ids named, causal relationship stated backwards",
        "expected": "accept",
        "expected_reason_contains": None,
        "note": "PASSES. The gate cannot evaluate whether the stated relationship is true.",
        "rec": _rec(
            ["A-CANON-001"],
            ["F-DUP-001"],
            "Because MarketBrew A-CANON-001 shows duplicate titles, and the client F-DUP-001 "
            "says canonical dilution causes them, deduplicate the methodology.",
        ),
    },
    {
        "case_id": "sem-003-misdescribed-records",
        "klass": "semantic",
        "failure_mode": "valid ids, contents of both records misstated",
        "expected": "accept",
        "expected_reason_contains": None,
        "note": "PASSES. No comparison is made between the trace and what the records actually say.",
        "rec": _rec(
            ["A-SPEED-014"],
            ["F-LCP-002"],
            "Because the client shows F-LCP-002 (excellent Core Web Vitals), and MarketBrew "
            "A-SPEED-014 says speed is not a ranking factor, take no action on performance.",
        ),
    },
    {
        "case_id": "sem-004-non-sequitur-action",
        "klass": "semantic",
        "failure_mode": "records described correctly, recommended action does not follow",
        "expected": "accept",
        "expected_reason_contains": None,
        "note": "PASSES. The gate never inspects whether the action follows from the premises.",
        "rec": _rec(
            ["A-CANON-001"],
            ["F-DUP-001"],
            "Because the client shows F-DUP-001, duplicate title tags, and MarketBrew "
            "A-CANON-001 says duplicates dilute canonical signals, migrate the site to a new CMS.",
        ),
    },
    {
        "case_id": "sem-005-contradictory-evidence-ignored",
        "klass": "semantic",
        "failure_mode": "cites supporting finding, ignores a contradicting one in the same bundle",
        "expected": "accept",
        "expected_reason_contains": None,
        "note": (
            "PASSES. Selective citation is invisible to a per-recommendation gate. Detecting it "
            "requires reasoning over the whole evidence bundle, which this layer does not do."
        ),
        "rec": _rec(
            ["A-SCHEMA-022"],
            ["F-NOSCHEMA-003"],
            "Because the client shows F-NOSCHEMA-003, no structured data present, and MarketBrew "
            "A-SCHEMA-022 says schema aids entity resolution, add FAQPage markup sitewide.",
        ),
    },
]


def counts_by_class() -> dict[str, int]:
    out: dict[str, int] = {}
    for case in CASES:
        out[case["klass"]] = out.get(case["klass"], 0) + 1
    return out
