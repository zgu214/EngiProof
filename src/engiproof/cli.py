from __future__ import annotations

import argparse
import json
from typing import Any

from . import __version__
from .core import (comparison_snapshot,contract_schema,discrepancy_snapshot,doctor,evidence_snapshot,invoke_tool,list_studies,load_manifest,provenance_snapshot,result_snapshot,run_study,verify_all,verify_study)


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
        else: raise AssertionError(ns.cmd)
        _print(out,ns.json)
        return 0 if not isinstance(out,dict) or out.get("status")!="FAIL" else 1
    except Exception as exc:
        _print({"status":"FAIL","error":f"{type(exc).__name__}: {exc}"},True); return 2
