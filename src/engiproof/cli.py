from __future__ import annotations

import argparse
import json
from typing import Any

from . import __version__
from .checkpoint import build_checkpoint, continuity_audit
from .core import (comparison_snapshot,contract_schema,discrepancy_snapshot,doctor,evidence_snapshot,invoke_tool,list_studies,load_manifest,provenance_snapshot,regenerate_study,result_snapshot,run_study,verify_all,verify_study)
from .discrepancy import assess_discrepancies, discrepancy_audit, discrepancy_audit_all, discrepancy_gate, discrepancy_decision_summary, record_discrepancy_decision
from .evidence_graph import audit_evidence_graph, sync_evidence_graph
from .taxonomy import record_taxonomy_review, taxonomy_audit
from .environment_record import compact_line, environment_record, failure_lines, write_record
from .ingestion_summary import build_ingestion_summary, ingestion_summary_audit, write_ingestion_summary
from .ingestion import (
    audit_source_identity, build_comparison_templates, build_reproduction_plan, build_task_bundle, enrich_source, extract_structures, ingest_source,
    list_intakes, load_intake, load_selected_target_readiness, load_source_identity_audit, load_structure_candidates, load_target_dossiers, pipeline_status, recover_equation_candidates, update_intake_metadata,
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
    p=sub.add_parser("regenerate",help="Explicitly REWRITE a study's committed result artifacts in place (not part of verification)."); p.add_argument("paper_id")
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
    p=sub.add_parser("audit-source",help="Audit fingerprint-matched source identity against configured title/DOI/year."); p.add_argument("paper_id"); p.add_argument("source")
    p=sub.add_parser("source-identity",help="Show the persisted source-identity audit."); p.add_argument("paper_id")
    p=sub.add_parser("recover-equations",help="Recover missing equation candidates from grouped references and printed equation numbers while preserving existing target IDs."); p.add_argument("paper_id"); p.add_argument("source")
    p=sub.add_parser("readiness",help="Show selected-target structural readiness gate."); p.add_argument("paper_id")
    p=sub.add_parser("set-metadata",help="Update intake title/DOI/year without changing the source fingerprint or target IDs; re-audit is required."); p.add_argument("paper_id"); p.add_argument("--title"); p.add_argument("--doi"); p.add_argument("--year",type=int)
    p=sub.add_parser("discrepancy-audit",help="Classify discrepancy review/escalation state without changing engineering evidence."); p.add_argument("paper_id")
    p=sub.add_parser("assess-discrepancies",help="Classify discrepancies and persist a machine-readable assessment artifact."); p.add_argument("paper_id")
    p=sub.add_parser("discrepancy-gate",help="Check whether unresolved discrepancy assessments block promotion."); p.add_argument("paper_id")
    sub.add_parser("discrepancy-audit-all",help="Audit discrepancy escalation state across all study manifests, including non-live studies.")
    p=sub.add_parser("discrepancy-decide",help="Record an append-only human decision for one discrepancy; does not grant qualification.")
    p.add_argument("paper_id"); p.add_argument("discrepancy_id"); p.add_argument("--disposition",required=True,choices=["RESOLVED","BOUNDED","ACCEPTED_WITH_RATIONALE","DEFERRED"])
    p.add_argument("--rationale",required=True); p.add_argument("--reviewer",required=True); p.add_argument("--evidence-ref",action="append",default=[],help="Repeatable evidence/provenance reference.")
    p=sub.add_parser("discrepancy-taxonomy",help="Audit legacy, proposed and approved controlled-taxonomy labels for discrepancies (labels only)."); p.add_argument("paper_id",nargs="?")
    p=sub.add_parser("taxonomy-review",help="Record an append-only human review of a proposed discrepancy taxonomy label; labels only.")
    p.add_argument("paper_id"); p.add_argument("discrepancy_id"); p.add_argument("--decision",required=True,choices=["APPROVED","REJECTED"])
    p.add_argument("--reviewer",required=True); p.add_argument("--note",required=True); p.add_argument("--category"); p.add_argument("--locus",action="append",default=[],help="Repeatable; replaces the proposed loci when given.")
    p=sub.add_parser("ingestion-summary",help="Build a text-free ingestion summary from the local intake (hashes, counts, statuses only).")
    p.add_argument("paper_id"); p.add_argument("--write",action="store_true",help="Write engiproof/studies/<ID>/ingestion_summary.json (tracked).")
    p.add_argument("--source-pdf",help="Local PDF for automatic born-digital/scan detection (default 01_doc/<canonical_pdf>); nothing from it is persisted but counts.")
    p.add_argument("--source-format",choices=["BORN_DIGITAL","SCANNED_WITH_TEXT_LAYER","SCANNED_IMAGE_ONLY","NOT_RECORDED"]); p.add_argument("--source-format-basis")
    p=sub.add_parser("ingestion-summary-audit",help="Check tracked ingestion summaries for the Paper A studies (or the given IDs)."); p.add_argument("paper_ids",nargs="*")
    p=sub.add_parser("environment-record",help="Verify every study (non-mutating) and emit a compact cross-environment record (Python/NumPy/OS + comparator classes).")
    p.add_argument("--out",help="Write the full record to this path (keep it outside the repository in CI)."); p.add_argument("--compact",action="store_true",help="Print a one-line JSON summary.")
    p=sub.add_parser("discrepancy-decisions",help="Show append-only discrepancy decisions and latest effective decision per discrepancy."); p.add_argument("paper_id")
    p=sub.add_parser("graph-sync",help="Add missing tool/comparison/discrepancy/assessment/decision provenance to a study evidence graph without deleting hand-authored graph content."); p.add_argument("paper_id")
    p=sub.add_parser("graph-audit",help="Audit evidence-graph provenance coverage for one study."); p.add_argument("paper_id")
    sub.add_parser("continuity-audit",help="Audit durable continuity controls and current project state.")
    p=sub.add_parser("checkpoint",help="Write a resumable checkpoint; optionally create a source-PDF-free bundle."); p.add_argument("--bundle",action="store_true"); p.add_argument("--output-dir",default="checkpoints/current")
    ns=parser.parse_args(argv)
    try:
        if ns.cmd=="doctor": out=doctor()
        elif ns.cmd=="list": out=[{"paper_id":m["paper_id"],"title":m["title"],"evidence_status":m["evidence_status"],"schema_version":m["schema_version"],"tools":[t["name"] for t in m.get("tools",[])]} for m in list_studies()]
        elif ns.cmd=="verify-all": out=verify_all()
        elif ns.cmd=="schema": out=contract_schema(ns.contract)
        elif ns.cmd=="show": out=load_manifest(ns.paper_id)
        elif ns.cmd=="run": out=run_study(ns.paper_id)
        elif ns.cmd=="regenerate": out=regenerate_study(ns.paper_id)
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
        elif ns.cmd=="audit-source": out=audit_source_identity(ns.paper_id,ns.source)
        elif ns.cmd=="source-identity": out=load_source_identity_audit(ns.paper_id)
        elif ns.cmd=="recover-equations": out=recover_equation_candidates(ns.paper_id,ns.source)
        elif ns.cmd=="readiness": out=load_selected_target_readiness(ns.paper_id)
        elif ns.cmd=="set-metadata": out=update_intake_metadata(ns.paper_id,title=ns.title,doi=ns.doi,year=ns.year)
        elif ns.cmd=="discrepancy-audit": out=discrepancy_audit(ns.paper_id)
        elif ns.cmd=="assess-discrepancies": out=assess_discrepancies(ns.paper_id,persist=True)
        elif ns.cmd=="discrepancy-gate": out=discrepancy_gate(ns.paper_id)
        elif ns.cmd=="discrepancy-audit-all": out=discrepancy_audit_all()
        elif ns.cmd=="discrepancy-decide": out=record_discrepancy_decision(ns.paper_id,ns.discrepancy_id,ns.disposition,ns.rationale,ns.reviewer,ns.evidence_ref)
        elif ns.cmd=="discrepancy-taxonomy": out=taxonomy_audit(ns.paper_id)
        elif ns.cmd=="taxonomy-review": out=record_taxonomy_review(ns.paper_id,ns.discrepancy_id,ns.decision,ns.reviewer,ns.note,category=ns.category,loci=ns.locus or None)
        elif ns.cmd=="ingestion-summary":
            out=build_ingestion_summary(ns.paper_id,source_pdf=ns.source_pdf,source_format=ns.source_format,source_format_basis=ns.source_format_basis)
            if ns.write: out={"written":write_ingestion_summary(out),"summary":out}
        elif ns.cmd=="ingestion-summary-audit": out=ingestion_summary_audit(ns.paper_ids or None)
        elif ns.cmd=="environment-record":
            rec=environment_record()
            if ns.out: write_record(rec,ns.out)
            if ns.compact:
                print(compact_line(rec))
                for line in failure_lines(rec): print(line)
                return 0 if rec["status"]!="FAIL" else 1
            out=rec
        elif ns.cmd=="discrepancy-decisions": out=discrepancy_decision_summary(ns.paper_id)
        elif ns.cmd=="graph-sync": out=sync_evidence_graph(ns.paper_id,persist=True)
        elif ns.cmd=="graph-audit": out=audit_evidence_graph(ns.paper_id)
        elif ns.cmd=="continuity-audit": out=continuity_audit()
        elif ns.cmd=="checkpoint": out=build_checkpoint(output_dir=ns.output_dir,bundle=ns.bundle)
        else: raise AssertionError(ns.cmd)
        _print(out,ns.json)
        return 0 if not isinstance(out,dict) or out.get("status")!="FAIL" else 1
    except Exception as exc:
        _print({"status":"FAIL","error":f"{type(exc).__name__}: {exc}"},True); return 2
