"""Controlled discrepancy taxonomy (Paper A gap G2).

The taxonomy is defined in ``engiproof/contracts/contracts.json`` under
``contracts.discrepancy_taxonomy``. Labels describe the kind of a discrepancy
and the evidence through which it was established. They never change an
observation, value, discrepancy status, decision, promotion effect or
qualification, and they do not assert a cause.

Legacy free-text ``classification_hint`` values stay in the study manifests.
Mapping them to the taxonomy is proposed in
``engiproof/contracts/discrepancy_taxonomy_mapping.json`` and takes effect only
after a recorded human review (append-only).
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

MAPPING_SCHEMA = "engiproof.discrepancy_taxonomy_mapping/1.0"
AUDIT_SCHEMA = "engiproof.discrepancy_taxonomy_audit/1.0"
REVIEW_DECISIONS = {"APPROVED", "REJECTED"}


def _root(root: Path | None) -> Path:
    from .core import project_root
    return (root or project_root()).resolve()


def load_taxonomy(root: Path | None = None) -> dict[str, Any]:
    if root is None:
        from .core import load_contracts
        contracts = load_contracts()
    else:
        path = Path(root) / "engiproof" / "contracts" / "contracts.json"
        contracts = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    return dict(contracts.get("contracts", {}).get("discrepancy_taxonomy") or {})


def validate_classification_hint(hint: Any, taxonomy: dict[str, Any]) -> list[str]:
    """A hint must be a taxonomy category or a registered legacy hint."""
    if hint in (None, ""):
        return []
    allowed = set(taxonomy.get("categories", {})) | set(taxonomy.get("legacy_classification_hints", []))
    if not allowed:
        return []
    return [] if str(hint) in allowed else [f"classification_hint {hint!r} is neither a taxonomy category nor a registered legacy hint"]


def validate_taxonomy_label(category: Any, loci: Any, taxonomy: dict[str, Any]) -> list[str]:
    issues = []
    if category not in taxonomy.get("categories", {}):
        issues.append(f"unknown taxonomy category: {category!r}")
    if not isinstance(loci, list) or not loci:
        issues.append("taxonomy loci must be a non-empty list")
    else:
        issues += [f"unknown taxonomy locus: {x!r}" for x in loci if x not in taxonomy.get("loci", {})]
        if len(set(loci)) != len(loci):
            issues.append("taxonomy loci contain duplicates")
    return issues


def validate_manifest_discrepancies(manifest: dict[str, Any], taxonomy: dict[str, Any]) -> list[str]:
    issues = []
    for d in manifest.get("discrepancies", []) or []:
        did = d.get("id", "<unnamed>")
        issues += [f"{did}: {m}" for m in validate_classification_hint(d.get("classification_hint"), taxonomy)]
        label = d.get("taxonomy")
        if label is not None:
            if not isinstance(label, dict):
                issues.append(f"{did}: taxonomy must be an object with category and loci")
            else:
                issues += [f"{did}: {m}" for m in validate_taxonomy_label(label.get("category"), label.get("loci"), taxonomy)]
    return issues


def _mapping_path(root: Path) -> Path:
    return root / "engiproof" / "contracts" / "discrepancy_taxonomy_mapping.json"


def load_mapping(root: Path | None = None) -> dict[str, Any]:
    path = _mapping_path(_root(root))
    if not path.is_file():
        return {"schema_version": MAPPING_SCHEMA, "records": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _manifests(root: Path) -> dict[str, dict[str, Any]]:
    out = {}
    sroot = root / "engiproof" / "studies"
    if sroot.is_dir():
        for d in sorted(p for p in sroot.iterdir() if (p / "study.json").is_file()):
            out[d.name.upper()] = json.loads((d / "study.json").read_text(encoding="utf-8"))
    return out


def _effective_label(record: dict[str, Any]) -> dict[str, Any] | None:
    reviews = record.get("reviews") or []
    if not reviews or reviews[-1].get("decision") != "APPROVED":
        return None
    last = reviews[-1]
    return {"category": last.get("category", record.get("proposed_category")),
            "loci": last.get("loci", record.get("proposed_loci")),
            "review_id": last.get("review_id"), "reviewer": last.get("reviewer")}


def taxonomy_audit(paper_id: str | None = None, root: Path | None = None) -> dict[str, Any]:
    """Report legacy hints, proposed and approved taxonomy labels per discrepancy."""
    root = _root(root)
    taxonomy = load_taxonomy(root)
    mapping = load_mapping(root)
    manifests = _manifests(root)
    pid_filter = paper_id.upper() if paper_id else None
    by_id = {str(r.get("discrepancy_id", "")).upper(): r for r in mapping.get("records", [])}
    issues: list[str] = []
    records = []
    seen = set()
    for pid, manifest in manifests.items():
        if pid_filter and pid != pid_filter:
            continue
        issues += [f"{pid} {m}" for m in validate_manifest_discrepancies(manifest, taxonomy)]
        for d in manifest.get("discrepancies", []) or []:
            did = str(d.get("id", "")).upper()
            seen.add(did)
            m = by_id.get(did)
            item = {"paper_id": pid, "discrepancy_id": did, "status": d.get("status"),
                    "legacy_classification_hint": d.get("classification_hint"),
                    "review_status": "UNMAPPED", "proposed": None, "effective": None}
            if m:
                if str(m.get("paper_id", "")).upper() != pid:
                    issues.append(f"{did}: mapping paper_id {m.get('paper_id')} does not match manifest {pid}")
                issues += [f"{did}: {x}" for x in validate_taxonomy_label(m.get("proposed_category"), m.get("proposed_loci"), taxonomy)]
                for rv in m.get("reviews") or []:
                    if "category" in rv or "loci" in rv:
                        issues += [f"{did} {rv.get('review_id')}: {x}" for x in validate_taxonomy_label(rv.get("category", m.get("proposed_category")), rv.get("loci", m.get("proposed_loci")), taxonomy)]
                item.update(review_status=m.get("review_status", "PROPOSED"),
                            proposed={"category": m.get("proposed_category"), "loci": m.get("proposed_loci")},
                            effective=_effective_label(m))
            records.append(item)
    for did, m in by_id.items():
        mpid = str(m.get("paper_id", "")).upper()
        if did not in seen and (not pid_filter or mpid == pid_filter):
            issues.append(f"{did}: mapped but not present in any study manifest")
    counts: dict[str, int] = {}
    for r in records:
        counts[r["review_status"]] = counts.get(r["review_status"], 0) + 1
    by_category: dict[str, int] = {}
    for r in records:
        label = r["effective"] or r["proposed"]
        if label:
            by_category[label["category"]] = by_category.get(label["category"], 0) + 1
    return {"schema_version": AUDIT_SCHEMA, "paper_id": pid_filter, "status": "PASS" if not issues else "FAIL",
            "discrepancy_count": len(records), "review_status_counts": counts,
            "category_counts_proposed_or_approved": by_category,
            "records": records, "issues": issues,
            "rule": taxonomy.get("rule", "Taxonomy labels never change evidence or qualification.")}


def record_taxonomy_review(paper_id: str, discrepancy_id: str, decision: str, reviewer: str, note: str,
                           category: str | None = None, loci: list[str] | None = None,
                           root: Path | None = None, today: str | None = None) -> dict[str, Any]:
    """Append a human review of a proposed taxonomy label. Labels only; no evidence changes."""
    root = _root(root)
    decision = decision.upper().strip()
    if decision not in REVIEW_DECISIONS:
        raise ValueError(f"decision must be one of {sorted(REVIEW_DECISIONS)}")
    reviewer = str(reviewer or "").strip()
    note = str(note or "").strip()
    if not reviewer:
        raise ValueError("Reviewer name is required.")
    if len(note) < 12:
        raise ValueError("A substantive review note is required (at least 12 characters).")
    mapping = load_mapping(root)
    did = discrepancy_id.upper()
    rec = next((r for r in mapping.get("records", []) if str(r.get("discrepancy_id", "")).upper() == did), None)
    if rec is None or str(rec.get("paper_id", "")).upper() != paper_id.upper():
        raise KeyError(f"No proposed taxonomy mapping for {paper_id.upper()} {did}.")
    taxonomy = load_taxonomy(root)
    review = {"review_id": f"{did}-TAX-{len(rec.get('reviews') or []) + 1:03d}", "decision": decision,
              "reviewer": reviewer, "date": today or date.today().isoformat(), "note": note}
    if decision == "APPROVED" and (category or loci):
        final_cat = category or rec.get("proposed_category")
        final_loci = loci or rec.get("proposed_loci")
        problems = validate_taxonomy_label(final_cat, final_loci, taxonomy)
        if problems:
            raise ValueError("; ".join(problems))
        review["category"], review["loci"] = final_cat, list(final_loci)
    rec.setdefault("reviews", []).append(review)
    rec["review_status"] = decision
    _mapping_path(root).write_text(json.dumps(mapping, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"schema_version": MAPPING_SCHEMA, "paper_id": paper_id.upper(), "discrepancy_id": did,
            "review": review, "effective": _effective_label(rec),
            "rule": "Taxonomy review changes labels only; observations, values, status, decisions and qualification are unchanged."}
