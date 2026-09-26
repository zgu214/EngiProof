from __future__ import annotations

import argparse
import json
from typing import Any

from . import __version__
from .core import (comparison_snapshot,contract_schema,discrepancy_snapshot,doctor,evidence_snapshot,invoke_tool,list_studies,load_manifest,provenance_snapshot,result_snapshot,run_study,verify_all,verify_study)
from .ingestion import (
    build_comparison_templates, build_reproduction_plan, build_task_bundle, enrich_source, extract_structures, ingest_source,
    list_intakes, load_intake, load_structure_candidates, load_target_dossiers, pipeline_status,
    scaffold_from_intake, promotion_gate, promote_study, target_dossier,
)


def _jsonable(value: Any) -> Any:
    if hasattr(value,"tolist"): return value.tolist()
    if isinstance(value,dict): return {str(k):_jsonable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [_jsonable(v) for v in value]
    return value


def _print(obj: Any,as_json: bool) -> None:
    if as_json or not isinstance(obj,str): print(json.dumps(_jsonable(obj),indent=2,ensure_ascii=False))
    else: print(obj)


def main(argv: list[str]|None=None) -> int:
    parser=argparse.ArgumentParser(description="EngiProof — from published research to verified engineering.")
    parser.add_argument("--json",action="store_true",help="Emit machine-readable JSON.")
    parser.add_argument("--version",action="version",version=f"EngiProof {__version__}")
    sub=parser.add_subparsers(dest="cmd",required=True)
    sub.add_parser("doctor",help="Check local runtime and repository structure.")
    sub.add_parser("list",help="List live studies and callable tools.")
    sub.add_parser("verify-all",help="Verify every live study.")
    p=sub.add_parser("schema",help="Show versioned EngiProof contracts."); p.add_argument("contract",nargs="?",help="study/source/evidence/comparison/discrepancy/verification")
    for name in ("show","run","verify","results","evidence","compare","provenance","discrepancy"):
        p=sub.add_parser(name); p.add_argument("paper_id")
    p=sub.add_parser("tool"); p.add_argument("paper_id"); p.add_argument("tool_name"); p.add_argument("--params",default="{}",help="JSON object of keyword arguments")
    p=sub.add_parser("ingest",help="Fingerprint a local paper/source and discover candidate targets without copying the source.")
    p.add_argument("source"); p.add_argument("--paper-id",required=True); p.add_argument("--title"); p.add_argument("--doi"); p.add_argument("--year",type=int); p.add_argument("--max-candidates",type=int,default=40)
    sub.add_parser("intakes",help="List paper intakes awaiting review/scaffolding.")
    p=sub.add_parser("intake",help="Show one intake, fingerprint and discovered targets."); p.add_argument("paper_id")
    p=sub.add_parser("scaffold",help="Create a DRAFT study scaffold from an intake without registering it live."); p.add_argument("paper_id"); p.add_argument("--targets",default="",help="Comma-separated candidate IDs such as T001,T004"); p.add_argument("--top-targets",type=int,default=3)
    p=sub.add_parser("promotion-gate",help="Check whether a DRAFT study has sufficient evidence to enter the live registry."); p.add_argument("paper_id")
    p=sub.add_parser("promote",help="Promote a study to the live registry only when the evidence gate passes."); p.add_argument("paper_id")
    p=sub.add_parser("plan",help="Generate a conservative reproduction task plan from the reviewed DRAFT scaffold."); p.add_argument("paper_id")
    p=sub.add_parser("pipeline",help="Show progress across the paper-to-evidence pipeline."); p.add_argument("paper_id")
    p=sub.add_parser("enrich",help="Re-open a fingerprint-matched external source and build bounded target dossiers/source locators."); p.add_argument("paper_id"); p.add_argument("source")
    p=sub.add_parser("dossiers",help="Show all enriched target dossiers for an intake."); p.add_argument("paper_id")
    p=sub.add_parser("dossier",help="Show one source-located target dossier."); p.add_argument("paper_id"); p.add_argument("candidate_id")
    p=sub.add_parser("task-bundle",help="Generate kind-specific reproduction tasks from enriched target dossiers."); p.add_argument("paper_id")
    p=sub.add_parser("extract-structures",help="Extract conservative equation/table/figure/definition structure candidates from the exact fingerprint-matched source."); p.add_argument("paper_id"); p.add_argument("source")
    p=sub.add_parser("structures",help="Show extracted structure candidates for an intake."); p.add_argument("paper_id")
    p=sub.add_parser("comparison-templates",help="Generate target-type comparison metric templates from selected source structures."); p.add_argument("paper_id")
    ns=parser.parse_args(argv)
    try:
        if ns.cmd=="doctor": out=doctor()
        elif ns.cmd=="list": out=[{"paper_id":m["paper_id"],"title":m["title"],"evidence_status":m["evidence_status"],"schema_version":m["schema_version"],"tools":[t["name"] for t in m.get("tools",[])]} for m in list_studies()]
        elif ns.cmd=="verify-all": out=verify_all()
        elif ns.cmd=="schema": out=contract_schema(ns.contract)
        elif ns.cmd=="show": out=load_manifest(ns.paper_id)
        elif ns.cmd=="run": out=run_study(ns.paper_id)
        elif ns.cmd=="verify": out=verify_study(ns.paper_id)
        elif ns.cmd=="results": out=result_snapshot(ns.paper_id)
        elif ns.cmd=="evidence": out=evidence_snapshot(ns.paper_id)
        elif ns.cmd=="compare": out=comparison_snapshot(ns.paper_id)
        elif ns.cmd=="provenance": out=provenance_snapshot(ns.paper_id)
        elif ns.cmd=="discrepancy": out=discrepancy_snapshot(ns.paper_id)
        elif ns.cmd=="tool": out=invoke_tool(ns.paper_id,ns.tool_name,json.loads(ns.params))
        elif ns.cmd=="ingest": out=ingest_source(ns.source,ns.paper_id,title=ns.title,doi=ns.doi,year=ns.year,max_candidates=ns.max_candidates)
        elif ns.cmd=="intakes": out=list_intakes()
        elif ns.cmd=="intake": out=load_intake(ns.paper_id)
        elif ns.cmd=="scaffold":
            ids=[x.strip() for x in ns.targets.split(',') if x.strip()]
            out=scaffold_from_intake(ns.paper_id,target_ids=ids or None,top_targets=ns.top_targets)
        elif ns.cmd=="promotion-gate": out=promotion_gate(ns.paper_id)
        elif ns.cmd=="promote": out=promote_study(ns.paper_id)
        elif ns.cmd=="plan": out=build_reproduction_plan(ns.paper_id)
        elif ns.cmd=="pipeline": out=pipeline_status(ns.paper_id)
        elif ns.cmd=="enrich": out=enrich_source(ns.paper_id,ns.source)
        elif ns.cmd=="dossiers": out=load_target_dossiers(ns.paper_id)
        elif ns.cmd=="dossier": out=target_dossier(ns.paper_id,ns.candidate_id)
        elif ns.cmd=="task-bundle": out=build_task_bundle(ns.paper_id)
        elif ns.cmd=="extract-structures": out=extract_structures(ns.paper_id,ns.source)
        elif ns.cmd=="structures": out=load_structure_candidates(ns.paper_id)
        elif ns.cmd=="comparison-templates": out=build_comparison_templates(ns.paper_id)
        else: raise AssertionError(ns.cmd)
        _print(out,ns.json)
        return 0 if not isinstance(out,dict) or out.get("status")!="FAIL" else 1
    except Exception as exc:
        _print({"status":"FAIL","error":f"{type(exc).__name__}: {exc}"},True); return 2
