"""Measure the citation-integrity gate against a frozen adversarial corpus.

Runs every case in ``evaluation/cases.py`` through the PRODUCTION gate
(``implementation.recommend.recommend_engine._integrity_reason``) and reports what it
catches, what it misses, and what it wrongly rejects.

No network, no API key, no model calls. Deterministic, so it is usable as a regression gate.

Usage
-----
    python -m evaluation.run_integrity_eval                 # human-readable report
    python -m evaluation.run_integrity_eval --json          # machine-readable
    python -m evaluation.run_integrity_eval --write-baseline
    python -m evaluation.run_integrity_eval --check-baseline  # non-zero exit on drift

Exit codes
----------
    0  every case matched its expected verdict (and baseline matched, if checked)
    1  at least one case diverged from expectation, or baseline drift was detected

Note on scope: ``--check-baseline`` failing on a SEMANTIC case is not necessarily a
regression. If the gate starts catching a documented blind spot, that is an improvement and
the baseline plus the case's ``expected`` field should be updated deliberately.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# The gate under test, extracted verbatim from the production engine. See gate.py.
from gate import _integrity_reason

from evaluation.cases import CASES, KNOWN_ATOM_IDS, KNOWN_FINDING_IDS

BASELINE_PATH = Path(__file__).parent / "baseline.json"


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    reason = _integrity_reason(case["rec"], KNOWN_ATOM_IDS, KNOWN_FINDING_IDS)
    verdict = "reject" if reason else "accept"
    matched = verdict == case["expected"]

    reason_ok = True
    if verdict == "reject" and case.get("expected_reason_contains"):
        reason_ok = case["expected_reason_contains"] in (reason or "")

    return {
        "case_id": case["case_id"],
        "class": case["klass"],
        "failure_mode": case["failure_mode"],
        "expected": case["expected"],
        "actual": verdict,
        "reason": reason,
        "matched": matched,
        "reason_matched": reason_ok,
        "ok": matched and reason_ok,
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_class: dict[str, dict[str, int]] = {}
    for r in results:
        bucket = by_class.setdefault(r["class"], {"total": 0, "as_expected": 0})
        bucket["total"] += 1
        if r["ok"]:
            bucket["as_expected"] += 1

    referential = [r for r in results if r["class"] == "referential"]
    semantic = [r for r in results if r["class"] == "semantic"]
    controls = [r for r in results if r["class"] == "control"]

    caught_ref = sum(1 for r in referential if r["actual"] == "reject")
    caught_sem = sum(1 for r in semantic if r["actual"] == "reject")
    false_positives = sum(1 for r in controls if r["actual"] == "reject")

    return {
        "total_cases": len(results),
        "all_as_expected": all(r["ok"] for r in results),
        "by_class": by_class,
        "referential_failure_classes": len(referential),
        "referential_caught": caught_ref,
        "referential_catch_rate": (caught_ref / len(referential)) if referential else None,
        "semantic_failure_classes": len(semantic),
        "semantic_caught": caught_sem,
        "semantic_catch_rate": (caught_sem / len(semantic)) if semantic else None,
        "controls": len(controls),
        "false_positives": false_positives,
        "reason_mismatches": [r["case_id"] for r in results if not r["reason_matched"]],
        "divergences": [r["case_id"] for r in results if not r["ok"]],
    }


def render(results: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("Citation-integrity gate evaluation")
    lines.append("=" * 78)
    lines.append("")
    lines.append(f"{'case':<34} {'class':<12} {'expected':<9} {'actual':<9} ok")
    lines.append("-" * 78)
    for r in results:
        flag = "yes" if r["ok"] else "NO"
        lines.append(
            f"{r['case_id']:<34} {r['class']:<12} {r['expected']:<9} {r['actual']:<9} {flag}"
        )
    lines.append("")
    lines.append("Measured results")
    lines.append("-" * 78)

    rc = summary["referential_catch_rate"]
    sc = summary["semantic_catch_rate"]
    lines.append(
        f"  Referential failure classes caught : {summary['referential_caught']}"
        f"/{summary['referential_failure_classes']}"
        + (f"  ({rc:.0%})" if rc is not None else "")
    )
    lines.append(
        f"  Semantic failure classes caught    : {summary['semantic_caught']}"
        f"/{summary['semantic_failure_classes']}"
        + (f"  ({sc:.0%})" if sc is not None else "")
        + "   <- by design, not a defect"
    )
    lines.append(
        f"  False positives on valid cases      : {summary['false_positives']}/{summary['controls']}"
    )
    lines.append("")

    misses = [r for r in results if r["class"] == "semantic" and r["actual"] == "accept"]
    if misses:
        lines.append("Known blind spots (accepted by the gate, enumerated on purpose)")
        lines.append("-" * 78)
        for r in misses:
            lines.append(f"  {r['case_id']}: {r['failure_mode']}")
        lines.append("")

    if summary["divergences"]:
        lines.append("DIVERGENCES FROM EXPECTATION")
        lines.append("-" * 78)
        for r in results:
            if not r["ok"]:
                lines.append(
                    f"  {r['case_id']}: expected {r['expected']}, got {r['actual']}"
                    + (f" (reason: {r['reason']})" if r["reason"] else "")
                )
        lines.append("")

    lines.append(
        "Honest reading: the gate enforces referential validity. It does not verify that the "
        "reasoning is sound."
    )
    lines.append(
        "Claims of the form 'unsupported recommendations are impossible' are not supported by "
        "this data."
    )
    return "\n".join(lines)


def baseline_shape(results: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "cases": {r["case_id"]: {"expected": r["expected"], "actual": r["actual"]} for r in results},
        "summary": {
            k: summary[k]
            for k in (
                "total_cases",
                "referential_failure_classes",
                "referential_caught",
                "semantic_failure_classes",
                "semantic_caught",
                "controls",
                "false_positives",
            )
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a report")
    parser.add_argument("--write-baseline", action="store_true", help="overwrite baseline.json")
    parser.add_argument("--check-baseline", action="store_true", help="fail on drift from baseline")
    args = parser.parse_args()

    results = [run_case(c) for c in CASES]
    summary = summarize(results)
    current = baseline_shape(results, summary)

    if args.write_baseline:
        BASELINE_PATH.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
        print(f"baseline written: {BASELINE_PATH}")
        return 0

    drift: list[str] = []
    if args.check_baseline:
        if not BASELINE_PATH.exists():
            print("no baseline.json; run --write-baseline first", file=sys.stderr)
            return 1
        stored = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        for case_id, rec in current["cases"].items():
            was = stored["cases"].get(case_id)
            if was is None:
                drift.append(f"{case_id}: new case, absent from baseline")
            elif was["actual"] != rec["actual"]:
                drift.append(f"{case_id}: baseline {was['actual']} -> now {rec['actual']}")
        for case_id in stored["cases"]:
            if case_id not in current["cases"]:
                drift.append(f"{case_id}: present in baseline, missing from corpus")

    if args.json:
        print(json.dumps({"summary": summary, "results": results, "drift": drift}, indent=2))
    else:
        print(render(results, summary))
        if drift:
            print("\nBASELINE DRIFT")
            print("-" * 78)
            for d in drift:
                print(f"  {d}")

    return 0 if summary["all_as_expected"] and not drift else 1


if __name__ == "__main__":
    raise SystemExit(main())
