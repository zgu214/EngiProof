"""Cross-environment verification records (Paper A gap G4).

``environment_record()`` runs the non-mutating verification of every study with a
manifest (live and frozen non-live) and reduces it to
a compact, text-free record: the verifying Python/NumPy/OS and, per study, the
verification status and comparator classification counts. The record is an
output of verification; it is never written into frozen evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .core import list_studies, project_root, verify_study
from .isolation import runtime_environment

SCHEMA = "engiproof.environment_record/1.0"
RULE = ("Recomputation equivalence across environments only. Environment fields are ENVIRONMENT_METADATA and never "
        "material; tolerances are not engineering acceptance criteria; verification is not qualification.")


def _all_study_ids() -> list[str]:
    sroot = project_root() / "engiproof" / "studies"
    return sorted(p.name for p in sroot.iterdir() if (p / "study.json").is_file())


def environment_record() -> dict[str, Any]:
    """Verify every study with a manifest (live registry and frozen non-live studies)."""
    live = {m["paper_id"] for m in list_studies()}
    items = [verify_study(pid) for pid in _all_study_ids()]
    good = {"PASS", "PASS_SOURCE_EXTERNAL"}
    result = {"status": "PASS" if all(x["status"] in good for x in items) else "FAIL", "studies": items}
    studies, totals = [], {}
    for item in result["studies"]:
        rep = item.get("reproduction") or {}
        counts = rep.get("classification_counts") or {}
        for k, v in counts.items():
            totals[k] = totals.get(k, 0) + v
        studies.append({
            "paper_id": item["paper_id"], "live": item["paper_id"] in live, "status": item["status"],
            "tests_passed": all(t.get("passed") for t in item.get("tests", [])),
            "classification_counts": counts, "material_artifacts": rep.get("material_artifacts"),
            "max_rel_diff": rep.get("max_rel_diff"), "max_abs_diff": rep.get("max_abs_diff"),
            "frozen_environment_declared": sorted({k for d in (rep.get("frozen_environment_declared") or {}).values() for k in d}),
        })
    return {"schema_version": SCHEMA, "status": result["status"], "environment": runtime_environment(),
            "study_count": len(studies), "classification_totals": totals, "studies": studies, "rule": RULE}


def compact_line(record: dict[str, Any]) -> str:
    """One-line JSON for CI annotations (environment, status, totals and non-identical studies)."""
    e = record["environment"]
    changed = {s["paper_id"]: {k: v for k, v in s["classification_counts"].items() if v and k != "IDENTICAL"}
               for s in record["studies"]}
    changed = {k: v for k, v in changed.items() if v}
    return json.dumps({"s": record["status"], "py": e["python_version"], "np": e["numpy_version"], "os": e["os"],
                       "m": e["machine"], "n": record["study_count"], "t": record["classification_totals"],
                       "nonidentical": changed}, separators=(",", ":"), sort_keys=True)


def write_record(record: dict[str, Any], out: str | Path) -> str:
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(path)
