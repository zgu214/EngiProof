from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .core import project_root
from .discrepancy import discrepancy_audit, load_discrepancy_decisions

GRAPH_SYNC_SCHEMA = "engiproof.evidence_graph_sync/1.0"
GRAPH_AUDIT_SCHEMA = "engiproof.evidence_graph_audit/1.0"


def _manifest(paper_id: str, root: Path) -> dict[str,Any]:
    pid=paper_id.upper(); p=root/"engiproof"/"studies"/pid/"study.json"
    if not p.is_file():
        raise KeyError(f"No EngiProof study for {pid}.")
    return json.loads(p.read_text(encoding="utf-8"))


def _graph_path(manifest: dict[str,Any], root: Path) -> Path:
    rel=manifest.get("evidence_graph") or f"engiproof/studies/{manifest['paper_id']}/evidence_graph.json"
    return root/rel


def _safe(value: str) -> str:
    text=re.sub(r"[^A-Za-z0-9]+","-",str(value).strip()).strip("-").upper()
    return text or "UNNAMED"


def _refs(node: dict[str,Any]) -> set[str]:
    return {str(x) for x in node.get("source_refs",[]) if x is not None}


def _node_by_ref(nodes: list[dict[str,Any]], ref: str, kind: str|None=None) -> dict[str,Any]|None:
    for node in nodes:
        if kind and node.get("kind")!=kind:
            continue
        if ref in _refs(node):
            return node
    return None


def _node_by_id(nodes: list[dict[str,Any]], node_id: str) -> dict[str,Any]|None:
    return next((n for n in nodes if n.get("id")==node_id),None)


def _upsert(nodes: list[dict[str,Any]], node: dict[str,Any], match_refs: list[str]|None=None) -> tuple[dict[str,Any],bool]:
    existing=_node_by_id(nodes,node["id"])
    if existing is None:
        for ref in match_refs or []:
            existing=_node_by_ref(nodes,ref,node.get("kind")) or _node_by_ref(nodes,ref)
            if existing is not None:
                break
    if existing is None:
        nodes.append(node); return node,True
    # Preserve hand-authored labels/status while adding machine refs/provenance.
    refs=list(existing.get("source_refs",[]))
    for ref in node.get("source_refs",[]):
        if ref not in refs: refs.append(ref)
    existing["source_refs"]=refs
    generated=list(existing.get("generated_by",[])) if isinstance(existing.get("generated_by"),list) else ([existing["generated_by"]] if existing.get("generated_by") else [])
    marker=GRAPH_SYNC_SCHEMA
    if marker not in generated: generated.append(marker)
    existing["generated_by"]=generated
    return existing,False


def _edge_key(edge: dict[str,Any]) -> tuple[str,str,str]:
    return str(edge.get("from")),str(edge.get("to")),str(edge.get("relation"))


def _add_edge(edges: list[dict[str,Any]], source: str, target: str, relation: str) -> bool:
    edge={"from":source,"to":target,"relation":relation}
    keys={_edge_key(e) for e in edges}
    if _edge_key(edge) in keys: return False
    edges.append(edge); return True


def _decision_status(disposition: str) -> str:
    return str(disposition or "DEFERRED").upper()


def sync_evidence_graph(paper_id: str, root: Path|None=None, persist: bool=True) -> dict[str,Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); manifest=_manifest(pid,root); path=_graph_path(manifest,root)
    if path.is_file():
        graph=json.loads(path.read_text(encoding="utf-8"))
    else:
        graph={"schema_version":"engiproof.evidence_graph/1.1","paper_id":pid,"nodes":[],"edges":[],"qualification":manifest.get("qualification","NOT_CLAIMED")}
    nodes=graph.setdefault("nodes",[]); edges=graph.setdefault("edges",[])
    graph["schema_version"]="engiproof.evidence_graph/1.1"; graph["paper_id"]=pid; graph["qualification"]=manifest.get("qualification","NOT_CLAIMED")
    added_nodes=0; added_edges=0

    # Source node: reuse any existing source node, otherwise create one.
    source=manifest.get("source",{}); doi=str(source.get("doi","")).strip(); sha=str(source.get("sha256","")).strip()
    source_node=next((n for n in nodes if n.get("kind")=="source"),None)
    if source_node is None:
        source_node={"id":f"AUTO-SOURCE-{pid}","kind":"source","label":manifest.get("title",pid),"evidence_class":"PUBLISHED","status":"SOURCE_READY","source_refs":[x for x in (f"doi:{doi}" if doi else "",f"sha256:{sha}" if sha else "") if x],"generated_by":[GRAPH_SYNC_SCHEMA]}
        nodes.append(source_node); added_nodes+=1
    source_id=source_node["id"]

    tool_nodes={}
    for tool in manifest.get("tools",[]):
        name=str(tool.get("name","unnamed")); evidence=str(tool.get("evidence","")).strip(); module=str(tool.get("module","")).strip()
        refs=[f"tool:{name}"]+[x for x in (evidence,module) if x]
        node={"id":f"AUTO-TOOL-{_safe(name)}","kind":"implementation","label":name,"evidence_class":tool.get("evidence_class","INDEPENDENT"),"status":manifest.get("evidence_status","DRAFT"),"source_refs":refs,"generated_by":[GRAPH_SYNC_SCHEMA]}
        actual,added=_upsert(nodes,node,refs)
        added_nodes+=int(added); tool_nodes[name]=actual["id"]
        added_edges+=int(_add_edge(edges,source_id,actual["id"],"supports_implementation"))

    comparison_nodes={}
    for cmp in manifest.get("comparisons",[]):
        cid=str(cmp.get("id") or f"CMP-{len(comparison_nodes)+1}"); refs=[cid]
        if cmp.get("reference"): refs.append(str(cmp["reference"]))
        node={"id":f"AUTO-COMPARISON-{_safe(cid)}","kind":"comparison","label":cmp.get("target",cid),"evidence_class":"INDEPENDENT","status":cmp.get("status","COMPARED"),"source_refs":refs,"generated_by":[GRAPH_SYNC_SCHEMA]}
        actual,added=_upsert(nodes,node,[cid]); added_nodes+=int(added); comparison_nodes[cid]=actual["id"]
        added_edges+=int(_add_edge(edges,source_id,actual["id"],"provides_reference_context"))

    discrepancy_nodes={}
    for disc in manifest.get("discrepancies",[]):
        did=str(disc.get("id") or f"D-{len(discrepancy_nodes)+1}"); refs=[did]
        node={"id":f"AUTO-DISCREPANCY-{_safe(did)}","kind":"discrepancy","label":disc.get("target",did),"evidence_class":"INDEPENDENT","status":disc.get("status","OPEN"),"source_refs":refs,"generated_by":[GRAPH_SYNC_SCHEMA]}
        actual,added=_upsert(nodes,node,[did]); added_nodes+=int(added); discrepancy_nodes[did]=actual["id"]
        added_edges+=int(_add_edge(edges,source_id,actual["id"],"contains_discrepancy_context"))

    # Generic automated assessments.
    audit=discrepancy_audit(pid,root=root)
    assessment_nodes={}
    for a in audit.get("assessments",[]):
        did=str(a.get("discrepancy_id")); refs=[did,f"assessment:{did}"]
        status="CONDITIONAL" if a.get("promotion_effect")=="BLOCK_PROMOTION" else "COMPARED"
        node={"id":f"AUTO-ASSESSMENT-{_safe(did)}","kind":"discrepancy_assessment","label":f"{a.get('category','DISCREPANCY')} assessment for {did}","evidence_class":"INDEPENDENT","status":status,"source_refs":refs,"generated_by":[GRAPH_SYNC_SCHEMA]}
        actual,added=_upsert(nodes,node,[f"assessment:{did}"]); added_nodes+=int(added); assessment_nodes[did]=actual["id"]
        disc_id=discrepancy_nodes.get(did) or (_node_by_ref(nodes,did) or {}).get("id")
        if disc_id: added_edges+=int(_add_edge(edges,disc_id,actual["id"],"classified_by"))

    decisions=load_discrepancy_decisions(pid,root=root)
    for decision in decisions.get("decisions",[]):
        decision_id=str(decision.get("decision_id")); did=str(decision.get("discrepancy_id")); refs=[decision_id,did,*[str(x) for x in decision.get("evidence_refs",[])]]
        node={"id":f"AUTO-DECISION-{_safe(decision_id)}","kind":"discrepancy_decision","label":f"{decision.get('disposition','DEFERRED')} decision for {did}","evidence_class":"INDEPENDENT","status":_decision_status(decision.get("disposition")),"source_refs":refs,"reviewer":decision.get("reviewer"),"qualification_effect":decision.get("qualification_effect","NONE"),"generated_by":[GRAPH_SYNC_SCHEMA]}
        actual,added=_upsert(nodes,node,[decision_id]); added_nodes+=int(added)
        disc_id=discrepancy_nodes.get(did) or (_node_by_ref(nodes,did) or {}).get("id")
        if disc_id: added_edges+=int(_add_edge(edges,disc_id,actual["id"],"reviewed_by"))
        assess_id=assessment_nodes.get(did)
        if assess_id: added_edges+=int(_add_edge(edges,assess_id,actual["id"],"informs_decision"))

    graph["sync"]={"schema_version":GRAPH_SYNC_SCHEMA,"added_nodes":added_nodes,"added_edges":added_edges,"tool_count":len(manifest.get("tools",[])),"comparison_count":len(manifest.get("comparisons",[])),"discrepancy_count":len(manifest.get("discrepancies",[])),"decision_count":len(decisions.get("decisions",[])),"rule":"Synchronization is additive: existing hand-authored nodes/edges are preserved and qualification is never promoted."}
    if persist:
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(graph,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return {"paper_id":pid,"status":"SYNCED" if persist else "PREVIEW","evidence_graph":str(path.relative_to(root)).replace("\\","/"),"added_nodes":added_nodes,"added_edges":added_edges,"node_count":len(nodes),"edge_count":len(edges),"decision_count":len(decisions.get("decisions",[])),"qualification":graph.get("qualification")}


def audit_evidence_graph(paper_id: str, root: Path|None=None) -> dict[str,Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); manifest=_manifest(pid,root); path=_graph_path(manifest,root)
    if not path.is_file():
        return {"schema_version":GRAPH_AUDIT_SCHEMA,"paper_id":pid,"status":"FAIL","issues":["evidence graph missing"],"coverage_fraction":0.0}
    graph=json.loads(path.read_text(encoding="utf-8")); nodes=graph.get("nodes",[])
    issues=[]; represented=0; expected=0
    if any(n.get("kind")=="source" for n in nodes): represented+=1
    else: issues.append("source node missing")
    expected+=1
    for tool in manifest.get("tools",[]):
        expected+=1; refs=[f"tool:{tool.get('name')}",str(tool.get("module","")),str(tool.get("evidence",""))]
        if any(any(ref and ref in _refs(n) for ref in refs) for n in nodes): represented+=1
        else: issues.append(f"tool not represented: {tool.get('name')}")
    for cmp in manifest.get("comparisons",[]):
        expected+=1; cid=str(cmp.get("id"))
        if _node_by_ref(nodes,cid): represented+=1
        else: issues.append(f"comparison not represented: {cid}")
    for disc in manifest.get("discrepancies",[]):
        expected+=2; did=str(disc.get("id"))
        if _node_by_ref(nodes,did): represented+=1
        else: issues.append(f"discrepancy not represented: {did}")
        if _node_by_ref(nodes,f"assessment:{did}"): represented+=1
        else: issues.append(f"discrepancy assessment not represented: {did}")
    decisions=load_discrepancy_decisions(pid,root=root)
    for decision in decisions.get("decisions",[]):
        expected+=1; did=str(decision.get("decision_id"))
        if _node_by_ref(nodes,did): represented+=1
        else: issues.append(f"decision not represented: {did}")
    coverage=1.0 if expected==0 else represented/expected
    return {"schema_version":GRAPH_AUDIT_SCHEMA,"paper_id":pid,"status":"PASS" if not issues else "FAIL","expected_items":expected,"represented_items":represented,"coverage_fraction":coverage,"issues":issues,"node_count":len(nodes),"edge_count":len(graph.get("edges",[])),"qualification":graph.get("qualification",manifest.get("qualification","NOT_CLAIMED")),"rule":"Graph coverage checks provenance representation only; PASS does not imply verification or engineering qualification."}
