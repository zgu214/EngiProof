from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import __version__


ALLOWED_EVIDENCE_CLASSES={"PUBLISHED","INDEPENDENT","SOLVER_NEW"}
ALLOWED_EVIDENCE_STATUSES={"DRAFT","SOURCE_READY","REPRODUCED","COMPARED","VERIFIED","CONDITIONAL","BLOCKED"}


def project_root() -> Path:
    override=os.environ.get("ENGIPROOF_PROJECT_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    here=Path.cwd().resolve()
    for p in [here,*here.parents]:
        if (p/"engiproof"/"registry.json").is_file() and (p/"papers").is_dir():
            return p
    return Path(__file__).resolve().parents[2]


def data_root() -> Path:
    return project_root()/"engiproof"


def study_root() -> Path:
    return data_root()/"studies"


def _jsonable(value: Any) -> Any:
    if hasattr(value,"tolist"):
        return value.tolist()
    if isinstance(value,Path):
        return str(value)
    if isinstance(value,dict):
        return {str(k):_jsonable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [_jsonable(v) for v in value]
    return value


def _load_json(path: Path) -> dict[str,Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_registry() -> dict[str,Any]:
    return _load_json(data_root()/"registry.json")


def load_contracts() -> dict[str,Any]:
    path=data_root()/"contracts"/"contracts.json"
    if not path.is_file():
        return {"schema_version":"engiproof.contracts/0","contracts":{}}
    return _load_json(path)


def contract_schema(name: str|None=None) -> dict[str,Any]:
    c=load_contracts()
    if name is None:
        return c
    key=name.lower()
    if key not in c.get("contracts",{}):
        raise KeyError(f"Unknown EngiProof contract: {name}")
    return {"schema_version":c.get("schema_version"),"name":key,"contract":c["contracts"][key],"evidence_classes":c.get("evidence_classes",[]),"evidence_statuses":c.get("evidence_statuses",[])}


def list_studies() -> list[dict[str,Any]]:
    return [load_manifest(pid) for pid in load_registry()["studies"]]


def load_manifest(paper_id: str) -> dict[str,Any]:
    pid=paper_id.upper()
    path=study_root()/pid/"study.json"
    if not path.is_file():
        raise KeyError(f"No live EngiProof study for {pid}.")
    return _load_json(path)


def validate_study_manifest(manifest: dict[str,Any]) -> list[str]:
    required=["schema_version","paper_id","title","evidence_status","source","runner","source_contract","result_files","verification_tests","tools","limitations"]
    issues=[f"missing field: {k}" for k in required if k not in manifest]
    status=manifest.get("evidence_status")
    if status not in ALLOWED_EVIDENCE_STATUSES:
        issues.append(f"unsupported evidence_status: {status}")
    source=manifest.get("source",{})
    for k in ("canonical_pdf","sha256","doi"):
        if not source.get(k): issues.append(f"source missing: {k}")
    for tool in manifest.get("tools",[]):
        if tool.get("evidence_class") not in ALLOWED_EVIDENCE_CLASSES:
            issues.append(f"tool {tool.get('name')} has unsupported evidence_class: {tool.get('evidence_class')}")
        for k in ("name","module","function","returns","evidence"):
            if k not in tool: issues.append(f"tool missing {k}: {tool.get('name','<unnamed>')}")
    return issues


def _load_function(module_rel: str,function_name: str):
    root=project_root(); path=root/module_rel
    if not path.is_file():
        raise FileNotFoundError(path.relative_to(root) if path.is_relative_to(root) else path)
    spec=importlib.util.spec_from_file_location(f"engiproof_{path.stem}_{abs(hash(str(path)))}",path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_rel}")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return getattr(module,function_name)


def invoke_tool(paper_id: str,tool_name: str,params: dict[str,Any]|None=None) -> dict[str,Any]:
    manifest=load_manifest(paper_id)
    tool=next((t for t in manifest.get("tools",[]) if t["name"]==tool_name),None)
    if tool is None:
        raise KeyError(f"Tool {tool_name!r} is not exposed by {manifest['paper_id']}.")
    fn=_load_function(tool["module"],tool["function"])
    value=fn(**(params or {}))
    return {"engiproof_schema":manifest["schema_version"],"paper_id":manifest["paper_id"],"tool":tool_name,"result":_jsonable(value),"returns":tool.get("returns"),"evidence":tool.get("evidence"),"evidence_class":tool.get("evidence_class"),"evidence_status":manifest.get("evidence_status"),"limitations":manifest.get("limitations",[])}


def run_study(paper_id: str) -> dict[str,Any]:
    root=project_root(); manifest=load_manifest(paper_id); runner=root/manifest["runner"]
    if not runner.is_file():
        return {"paper_id":manifest["paper_id"],"status":"FAIL","reason":f"Missing runner: {manifest['runner']}"}
    proc=subprocess.run([sys.executable,str(runner)],cwd=root,capture_output=True,text=True)
    return {"paper_id":manifest["paper_id"],"status":"PASS" if proc.returncode==0 else "FAIL","returncode":proc.returncode,"stdout":proc.stdout.strip(),"stderr":proc.stderr.strip(),"result_files":manifest.get("result_files",[]),"evidence_status":manifest.get("evidence_status")}


def _source_check(manifest: dict[str,Any]) -> dict[str,Any]:
    root=project_root(); source=manifest.get("source",{}); source_name=source.get("canonical_pdf"); expected=source.get("sha256")
    candidates=[root/"01_doc"/source_name,root/"literature"/source_name,root/"papers"/manifest.get("paper_id","")/"source.pdf"] if source_name else []
    source_path=next((p for p in candidates if p.is_file()),None)
    out={"expected_sha256":expected,"present":bool(source_path)}
    if source_path:
        actual=_sha256(source_path); out.update({"path":str(source_path.relative_to(root)),"actual_sha256":actual,"matches":actual==expected})
    return out


def verify_study(paper_id: str) -> dict[str,Any]:
    root=project_root(); manifest=load_manifest(paper_id)
    required=[manifest["runner"],manifest["source_contract"],*manifest.get("result_files",[])]
    if manifest.get("evidence_graph"): required.append(manifest["evidence_graph"])
    missing=[rel for rel in required if not (root/rel).is_file()]
    contract_issues=validate_study_manifest(manifest)
    tests=[]
    for test in manifest.get("verification_tests",[]):
        proc=subprocess.run([sys.executable,"-m","unittest",test,"-v"],cwd=root,env={**os.environ,"PYTHONPATH":str(root/"src")},capture_output=True,text=True)
        tests.append({"test":test,"returncode":proc.returncode,"passed":proc.returncode==0,"output":(proc.stdout+proc.stderr).strip()})
    source_check=_source_check(manifest); all_tests=all(t["passed"] for t in tests)
    if missing or contract_issues or not all_tests or (source_check.get("present") and source_check.get("matches") is False): status="FAIL"
    elif not source_check.get("present"): status="PASS_SOURCE_EXTERNAL"
    else: status="PASS"
    return {"paper_id":manifest["paper_id"],"status":status,"evidence_status":manifest.get("evidence_status"),"contract_issues":contract_issues,"missing_required_files":missing,"source_check":source_check,"tests":tests,"limitations":manifest.get("limitations",[]),"qualification":manifest.get("qualification","NOT_CLAIMED")}


def verify_all() -> dict[str,Any]:
    items=[verify_study(m["paper_id"]) for m in list_studies()]; good={"PASS","PASS_SOURCE_EXTERNAL"}
    return {"status":"PASS" if all(x["status"] in good for x in items) else "FAIL","studies":items}


def result_snapshot(paper_id: str) -> dict[str,Any]:
    root=project_root(); manifest=load_manifest(paper_id); items=[]
    for rel in manifest.get("result_files",[]):
        path=root/rel; item={"path":rel,"present":path.is_file()}
        if path.is_file():
            item["sha256"]=_sha256(path)
            if path.suffix.lower()==".json": item["data"]=_load_json(path)
        items.append(item)
    return {"paper_id":manifest["paper_id"],"evidence_status":manifest.get("evidence_status"),"results":items}


def evidence_snapshot(paper_id: str) -> dict[str,Any]:
    root=project_root(); manifest=load_manifest(paper_id); rel=manifest.get("evidence_graph")
    if rel and (root/rel).is_file():
        graph=_load_json(root/rel)
    else:
        nodes=[{"id":f"SOURCE-{manifest['paper_id']}","kind":"source","label":manifest['title'],"evidence_class":"PUBLISHED","status":"SOURCE_READY","source_refs":[manifest.get('source',{}).get('doi')]}]
        nodes += [{"id":f"TOOL-{i+1}","kind":"implementation","label":t['name'],"evidence_class":t.get('evidence_class'),"status":manifest.get('evidence_status'),"source_refs":[t.get('evidence')]} for i,t in enumerate(manifest.get('tools',[]))]
        graph={"schema_version":"engiproof.evidence_graph/1.0","paper_id":manifest["paper_id"],"nodes":nodes,"edges":[],"synthetic_from_manifest":True}
    return {"paper_id":manifest["paper_id"],"evidence_status":manifest.get("evidence_status"),"graph":graph}


def comparison_snapshot(paper_id: str) -> dict[str,Any]:
    manifest=load_manifest(paper_id)
    return {"paper_id":manifest["paper_id"],"evidence_status":manifest.get("evidence_status"),"comparisons":manifest.get("comparisons",[])}


def discrepancy_snapshot(paper_id: str) -> dict[str,Any]:
    manifest=load_manifest(paper_id)
    return {"paper_id":manifest["paper_id"],"evidence_status":manifest.get("evidence_status"),"discrepancies":manifest.get("discrepancies",[])}


def provenance_snapshot(paper_id: str) -> dict[str,Any]:
    root=project_root(); manifest=load_manifest(paper_id)
    rels=[manifest.get("source_contract"),manifest.get("runner"),manifest.get("evidence_graph"),*[t.get("module") for t in manifest.get("tools",[])],*manifest.get("result_files",[])]
    files=[]; seen=set()
    for rel in rels:
        if not rel or rel in seen: continue
        seen.add(rel); path=root/rel
        files.append({"path":rel,"present":path.is_file(),**({"sha256":_sha256(path)} if path.is_file() else {})})
    return {"schema_version":"engiproof.provenance/1.0","paper_id":manifest["paper_id"],"framework_version":manifest.get("framework_version",__version__),"source":manifest.get("source",{}),"source_check":_source_check(manifest),"files":files,"qualification":manifest.get("qualification","NOT_CLAIMED"),"provenance_note":manifest.get("provenance_note")}


def doctor() -> dict[str,Any]:
    root=project_root(); checks={"registry":(root/"engiproof"/"registry.json").is_file(),"contracts":(root/"engiproof"/"contracts"/"contracts.json").is_file(),"papers_dir":(root/"papers").is_dir(),"results_dir":(root/"results").is_dir(),"tests_dir":(root/"tests").is_dir()}
    try:
        import numpy as np; numpy_version=np.__version__; checks["numpy"]=True
    except Exception:
        numpy_version=None; checks["numpy"]=False
    return {"status":"PASS" if all(checks.values()) else "FAIL","framework":"EngiProof","version":__version__,"python":sys.version.split()[0],"numpy":numpy_version,"project_root":".","checks":checks}
