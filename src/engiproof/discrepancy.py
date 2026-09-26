from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .core import load_manifest, project_root

ASSESSMENT_SCHEMA = "engiproof.discrepancy_assessment/1.0"
GATE_SCHEMA = "engiproof.discrepancy_gate/1.0"
CLOSED_STATES = {"CLOSED", "RESOLVED"}
BOUNDED_STATES = {"BOUNDED"}
OPEN_STATES = {"OPEN", "UNRESOLVED", "CONDITIONAL"}
DECISION_SCHEMA = "engiproof.discrepancy_decisions/1.0"
DECISION_STATES = {"RESOLVED", "BOUNDED", "ACCEPTED_WITH_RATIONALE", "DEFERRED"}
UNBLOCKING_DECISIONS = {"RESOLVED", "BOUNDED", "ACCEPTED_WITH_RATIONALE"}


def _decision_path(paper_id: str, root: Path) -> Path:
    return root/"engiproof"/"studies"/paper_id.upper()/"discrepancy_decisions.json"


def load_discrepancy_decisions(paper_id: str, root: Path | None=None) -> dict[str,Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); path=_decision_path(pid,root)
    if not path.is_file():
        return {"schema_version":DECISION_SCHEMA,"paper_id":pid,"decisions":[]}
    data=json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("schema_version",DECISION_SCHEMA); data.setdefault("paper_id",pid); data.setdefault("decisions",[])
    return data


def _latest_decisions_by_discrepancy(paper_id: str, root: Path) -> dict[str,dict[str,Any]]:
    data=load_discrepancy_decisions(paper_id,root=root); latest={}
    for item in data.get("decisions",[]):
        did=str(item.get("discrepancy_id","")).upper()
        if did: latest[did]=item
    return latest


def record_discrepancy_decision(paper_id: str, discrepancy_id: str, disposition: str, rationale: str, reviewer: str, evidence_refs: list[str] | None=None, root: Path | None=None) -> dict[str,Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); did=discrepancy_id.upper(); disposition=disposition.upper().strip()
    if disposition not in DECISION_STATES:
        raise ValueError(f"Unsupported disposition {disposition!r}; use one of {sorted(DECISION_STATES)}")
    rationale=str(rationale or "").strip(); reviewer=str(reviewer or "").strip(); refs=[str(x).strip() for x in (evidence_refs or []) if str(x).strip()]
    if len(rationale) < 12: raise ValueError("A substantive rationale is required (at least 12 characters).")
    if not reviewer: raise ValueError("Reviewer/approver name is required.")
    manifest=_manifest(pid,root); discrepancies={str(d.get("id","")).upper():d for d in manifest.get("discrepancies",[])}
    if did not in discrepancies: raise KeyError(f"No discrepancy {did} in study {pid}.")
    if disposition in UNBLOCKING_DECISIONS and not refs: raise ValueError(f"{disposition} requires at least one evidence reference.")
    store=load_discrepancy_decisions(pid,root=root); n=sum(1 for d in store["decisions"] if str(d.get("discrepancy_id","")).upper()==did)+1
    decision={"decision_id":f"{did}-DEC-{n:03d}","discrepancy_id":did,"disposition":disposition,"rationale":rationale,"reviewer":reviewer,"evidence_refs":refs,"effective_promotion_effect":"NONE" if disposition in UNBLOCKING_DECISIONS else "BLOCK_PROMOTION","qualification_effect":"NONE","rule":"Human discrepancy decisions may resolve/bound/accept a review item but never grant engineering qualification."}
    store["decisions"].append(decision); path=_decision_path(pid,root); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(store,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return {"schema_version":DECISION_SCHEMA,"paper_id":pid,"decision":decision,"decision_count":len(store["decisions"])}


def discrepancy_decision_summary(paper_id: str, root: Path | None=None) -> dict[str,Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); data=load_discrepancy_decisions(pid,root=root); latest=_latest_decisions_by_discrepancy(pid,root)
    return {"schema_version":DECISION_SCHEMA,"paper_id":pid,"decision_count":len(data.get("decisions",[])),"latest_by_discrepancy":latest,"decisions":data.get("decisions",[]),"rule":"Decision records are append-only review evidence; the original discrepancy remains in the study manifest."}



def _finite(value: Any) -> float | None:
    try:
        x=float(value)
    except (TypeError,ValueError):
        return None
    return x if math.isfinite(x) else None


def _infer_category(discrepancy: dict[str,Any]) -> tuple[str,list[str]]:
    explicit=discrepancy.get("classification_hint") or discrepancy.get("category")
    if explicit:
        return str(explicit).upper(), ["explicit classification hint"]
    text=" ".join(str(discrepancy.get(k,"")) for k in ("target","observation","engineering_interpretation")).lower()
    status=str(discrepancy.get("status","")).upper()
    if "model-versus-experiment" in text or ("experiment" in text and "model" in text and status=="OBSERVED"):
        return "MODEL_VS_EXPERIMENT_GAP", ["model/experiment wording"]
    if status in OPEN_STATES and any(k in text for k in ("does not reproduce","reports","while table","mismatch","conflict")):
        return "PUBLISHED_REFERENCE_MISMATCH", ["open published-reference mismatch wording"]
    if any(k in text for k in ("positive-frequency","two-sided","convention","normalization")) and status in OPEN_STATES:
        return "SOURCE_CONVENTION_AMBIGUITY", ["source convention/normalization wording"]
    if status in BOUNDED_STATES and any(k in text for k in ("graphical","digitization","precision","rounding","residual")):
        return "BOUNDED_PRECISION_OR_DIGITIZATION", ["bounded precision/digitization wording"]
    if status in OPEN_STATES:
        return "UNRESOLVED_EVIDENCE_CONFLICT", ["open discrepancy without a narrower structured category"]
    return "OBSERVED_DIFFERENCE", ["no stronger category inferred"]


def _rounding_check(metrics: dict[str,Any]) -> dict[str,Any] | None:
    reference=_finite(metrics.get("reference_value")); reproduced=_finite(metrics.get("reproduced_value"))
    decimals=metrics.get("reference_decimals")
    if reference is None or reproduced is None or not isinstance(decimals,int) or decimals < 0:
        return None
    half_unit=0.5*(10.0**(-decimals)); diff=abs(reproduced-reference)
    return {"reference_decimals":decimals,"half_unit_in_last_place":half_unit,"absolute_difference":diff,"beyond_rounding_band":diff>half_unit+1e-15}


def classify_discrepancy(discrepancy: dict[str,Any]) -> dict[str,Any]:
    did=str(discrepancy.get("id","UNNAMED")); state=str(discrepancy.get("status","OBSERVED")).upper()
    category,basis=_infer_category(discrepancy); metrics=dict(discrepancy.get("metrics") or {}); auto=dict(discrepancy.get("automation") or {})
    rounding=_rounding_check(metrics)
    if rounding: basis.append("structured rounding-band check")
    independent=str(auto.get("independent_support") or discrepancy.get("independent_support") or "NOT_RECORDED").upper()
    if independent != "NOT_RECORDED": basis.append(f"independent_support={independent}")
    if state in CLOSED_STATES: priority,effect="LOW","NONE"
    elif state in BOUNDED_STATES: priority,effect="LOW","NONE"
    elif state=="OBSERVED" and category=="MODEL_VS_EXPERIMENT_GAP": priority,effect="MEDIUM","REVIEW_REQUIRED"
    elif state in OPEN_STATES: priority,effect="HIGH",str(auto.get("promotion_effect") or "BLOCK_PROMOTION").upper()
    else: priority,effect="MEDIUM",str(auto.get("promotion_effect") or "REVIEW_REQUIRED").upper()
    if rounding and rounding["beyond_rounding_band"] and independent in {"CORROBORATES_REPRODUCTION","SUPPORTS_REPRODUCTION","AGREES_WITH_REPRODUCTION"}:
        priority,effect="HIGH","BLOCK_PROMOTION"
        if category in {"OBSERVED_DIFFERENCE","UNRESOLVED_EVIDENCE_CONFLICT"}: category="PUBLISHED_REFERENCE_MISMATCH"
        basis.append("difference exceeds recorded rounding band and independent check corroborates reproduction")
    closure=list(discrepancy.get("closure_requirements") or auto.get("closure_requirements") or [])
    if not closure and effect=="BLOCK_PROMOTION":
        closure=["Confirm the exact source reference and transcription.","Confirm the reproduced calculation and units/normalization.","Record an independent check where physically meaningful.","Resolve, bound, or explicitly accept the discrepancy before promotion."]
    return {"schema_version":ASSESSMENT_SCHEMA,"discrepancy_id":did,"target":discrepancy.get("target"),"state":state,"category":category,"review_priority":priority,"promotion_effect":effect,"basis":basis,"metrics":metrics,"rounding_check":rounding,"independent_support":independent,"closure_requirements":closure,"engineering_interpretation":discrepancy.get("engineering_interpretation"),"rule":"Automation classifies review/escalation state only; it does not decide engineering acceptability or qualification."}


def _manifest(paper_id: str, root: Path) -> dict[str,Any]:
    pid=paper_id.upper()
    if root==project_root().resolve(): return load_manifest(pid)
    p=root/"engiproof"/"studies"/pid/"study.json"
    if not p.is_file(): raise KeyError(f"No EngiProof study for {pid}.")
    return json.loads(p.read_text(encoding="utf-8"))


def discrepancy_audit(paper_id: str, root: Path | None=None) -> dict[str,Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); manifest=_manifest(pid,root)
    assessments=[classify_discrepancy(d) for d in manifest.get("discrepancies",[])]
    return {"schema_version":ASSESSMENT_SCHEMA,"paper_id":pid,"evidence_status":manifest.get("evidence_status"),"discrepancy_count":len(assessments),"high_priority_count":sum(a["review_priority"]=="HIGH" for a in assessments),"promotion_blocker_count":sum(a["promotion_effect"]=="BLOCK_PROMOTION" for a in assessments),"assessments":assessments,"qualification":manifest.get("qualification","NOT_CLAIMED")}


def assess_discrepancies(paper_id: str, root: Path | None=None, persist: bool=True) -> dict[str,Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); audit=discrepancy_audit(pid,root=root)
    if persist:
        out=root/"papers"/pid/"results"/"discrepancy_assessment.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); audit={**audit,"artifact":str(out.relative_to(root)).replace("\\","/")}
    return audit


def discrepancy_gate(paper_id: str, root: Path | None=None) -> dict[str,Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); audit=discrepancy_audit(pid,root=root); latest=_latest_decisions_by_discrepancy(pid,root)
    assessments=[]; blockers=[]; reviews=[]
    for a in audit["assessments"]:
        did=str(a["discrepancy_id"]).upper(); decision=latest.get(did); effective=a["promotion_effect"]
        if decision: effective=decision.get("effective_promotion_effect",effective)
        item={**a,"decision":decision,"effective_promotion_effect":effective}; assessments.append(item)
        if effective=="BLOCK_PROMOTION": blockers.append(item)
        elif effective=="REVIEW_REQUIRED": reviews.append(item)
    return {"schema_version":GATE_SCHEMA,"paper_id":pid,"ready":not blockers,"blocking_discrepancy_ids":[a["discrepancy_id"] for a in blockers],"review_required_ids":[a["discrepancy_id"] for a in reviews],"assessments":assessments,"decision_count":len(load_discrepancy_decisions(pid,root=root).get("decisions",[])),"rule":"OPEN/high-priority conflicts block promotion unless a documented human decision RESOLVES, BOUNDS, or ACCEPTS_WITH_RATIONALE the item. Decisions never grant qualification."}


def discrepancy_audit_all(root: Path | None=None) -> dict[str,Any]:
    root=(root or project_root()).resolve(); sroot=root/"engiproof"/"studies"; items=[]
    if sroot.is_dir():
        for d in sorted(p for p in sroot.iterdir() if p.is_dir() and (p/"study.json").is_file()):
            manifest=json.loads((d/"study.json").read_text(encoding="utf-8"))
            if manifest.get("discrepancies"): items.append(discrepancy_audit(d.name,root=root))
    return {"schema_version":"engiproof.discrepancy_audit_all/1.0","study_count":len(items),"studies":items,"total_discrepancies":sum(x["discrepancy_count"] for x in items),"total_promotion_blockers":sum(x["promotion_blocker_count"] for x in items)}
