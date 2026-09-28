from __future__ import annotations
import hashlib, json, subprocess, zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from . import __version__
from .core import project_root

REQUIRED = [
    "AGENTS.md","PROJECT_STATE.json","HANDOVER_CURRENT.md","CHAT_COMPACT_CURRENT.md",
    "WORK_QUEUE.md","BLOCKERS.md","DECISIONS.md","NEW_CHAT_BOOTSTRAP.md",
    "ROADMAP_v0.2.0.md","PROGRESS_v0.2.0.md",
]
BUNDLE_FILES = [
    *REQUIRED, "VERSION", "docs/CONTINUITY_ARCHITECTURE.md",
    "docs/ENGIPROOF_DEVELOPMENT_STANDARD_v0.1.md",
]

def _load(path: Path) -> dict[str,Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _git(root: Path,*args: str) -> str|None:
    try:
        p=subprocess.run(["git",*args],cwd=root,capture_output=True,text=True,timeout=15)
        return p.stdout.strip() if p.returncode==0 else None
    except Exception:
        return None

def git_state(root: Path|None=None) -> dict[str,Any]:
    root=(root or project_root()).resolve()
    status=_git(root,"status","--porcelain")
    dirty=[line[3:].strip() for line in status.splitlines() if len(line)>=4] if status else []
    return {
        "schema_version":"engiproof.git_state/1.0",
        "branch":_git(root,"branch","--show-current"),
        "head":_git(root,"rev-parse","HEAD"),
        "head_subject":_git(root,"log","-1","--pretty=%s"),
        "upstream":_git(root,"rev-parse","--abbrev-ref","--symbolic-full-name","@{u}"),
        "dirty":bool(dirty),"dirty_paths":dirty,"project_root":".",
    }

def _studies(root: Path) -> list[dict[str,Any]]:
    live=set()
    rp=root/"engiproof"/"registry.json"
    if rp.is_file(): live=set(_load(rp).get("studies",[]))
    out=[]
    for p in sorted((root/"engiproof"/"studies").glob("*/study.json")):
        try: m=_load(p)
        except Exception as exc:
            out.append({"paper_id":p.parent.name,"manifest_error":f"{type(exc).__name__}: {exc}"})
            continue
        s=m.get("source",{})
        out.append({
            "paper_id":m.get("paper_id",p.parent.name),"title":m.get("title"),
            "evidence_status":m.get("evidence_status"),"qualification":m.get("qualification","NOT_CLAIMED"),
            "live_registry":m.get("paper_id",p.parent.name) in live,
            "tool_count":len(m.get("tools",[])),"comparison_count":len(m.get("comparisons",[])),
            "discrepancy_count":len(m.get("discrepancies",[])),
            "source":{"canonical_pdf":s.get("canonical_pdf"),"doi":s.get("doi"),"sha256":s.get("sha256")},
            "manifest_path":str(p.relative_to(root)).replace("\\","/"),
        })
    return out

def _open_discrepancies(root: Path) -> dict[str,Any]:
    items=[]
    for p in sorted((root/"engiproof"/"studies").glob("*/study.json")):
        try: m=_load(p)
        except Exception: continue
        for d in m.get("discrepancies",[]):
            if str(d.get("status","OPEN")).upper() in {"RESOLVED","CLOSED"}: continue
            items.append({
                "paper_id":m.get("paper_id",p.parent.name),"id":d.get("id"),
                "status":d.get("status"),"classification_hint":d.get("classification_hint"),
                "target":d.get("target"),
            })
    return {"schema_version":"engiproof.open_discrepancies/1.0","count":len(items),"items":items}

def continuity_audit(root: Path|None=None) -> dict[str,Any]:
    root=(root or project_root()).resolve()
    issues=[]; warnings=[]; checks={}
    for rel in REQUIRED:
        present=(root/rel).is_file(); checks[rel]=present
        if not present: issues.append(f"missing continuity file: {rel}")
    state=None
    sp=root/"PROJECT_STATE.json"
    if sp.is_file():
        try: state=_load(sp)
        except Exception as exc: issues.append(f"PROJECT_STATE invalid: {type(exc).__name__}: {exc}")
    if state:
        if state.get("framework_version") != __version__:
            issues.append(f"PROJECT_STATE framework_version {state.get('framework_version')!r} != runtime {__version__!r}")
        current=state.get("current_study")
        if current and not (root/"engiproof"/"studies"/current/"study.json").is_file():
            issues.append(f"current study manifest missing: {current}")
        last=state.get("last_green_verification")
        if last and not (root/last).is_file(): issues.append(f"last green verification script missing: {last}")
        if state.get("last_green_status")!="PASS": warnings.append("last_green_status is not PASS")
        hand=(root/"HANDOVER_CURRENT.md").read_text(encoding="utf-8") if (root/"HANDOVER_CURRENT.md").is_file() else ""
        comp=(root/"CHAT_COMPACT_CURRENT.md").read_text(encoding="utf-8") if (root/"CHAT_COMPACT_CURRENT.md").is_file() else ""
        if current and current not in hand: warnings.append(f"{current} not mentioned in HANDOVER_CURRENT.md")
        if current and current not in comp: warnings.append(f"{current} not mentioned in CHAT_COMPACT_CURRENT.md")
    gs=git_state(root)
    if state and gs.get("branch") and state.get("primary_branch") and gs["branch"]!=state["primary_branch"]:
        warnings.append(f"git branch {gs['branch']!r} differs from primary_branch {state['primary_branch']!r}")
    return {
        "schema_version":"engiproof.continuity_audit/1.0",
        "status":"FAIL" if issues else ("WARN" if warnings else "PASS"),
        "framework_version":__version__,"checks":checks,"issues":issues,"warnings":warnings,
        "git":gs,"project_state":state,
        "rule":"Critical project state must be recoverable from repository/control files without chat memory.",
    }

def build_checkpoint(*,root: Path|None=None,output_dir: str|Path="checkpoints/current",bundle: bool=False) -> dict[str,Any]:
    root=(root or project_root()).resolve()
    out=(root/Path(output_dir)).resolve(); out.mkdir(parents=True,exist_ok=True)
    audit=continuity_audit(root); gs=git_state(root)
    studies={"schema_version":"engiproof.study_index/1.0","framework_version":__version__,"studies":_studies(root)}
    disc=_open_discrepancies(root)
    state=_load(root/"PROJECT_STATE.json") if (root/"PROJECT_STATE.json").is_file() else {}
    now=datetime.now(timezone.utc).isoformat()
    artifacts={
        "checkpoint_summary.json":{
            "schema_version":"engiproof.checkpoint/1.0","framework_version":__version__,
            "generated_at_utc":now,"project_state":state,"continuity_status":audit["status"],
            "git":{"branch":gs.get("branch"),"head":gs.get("head"),"dirty":gs.get("dirty")},
            "study_count":len(studies["studies"]),"open_discrepancy_count":disc["count"],
            "qualification":state.get("qualification","NOT_CLAIMED"),
            "copyright_boundary":"Source PDFs/private client data excluded."
        },
        "git_state.json":gs,
        "study_index.json":studies,
        "open_discrepancies.json":disc,
        "continuity_audit.json":audit,
    }
    for name,data in artifacts.items():
        (out/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    bundle_rel=None; bundle_sha=None
    if bundle:
        bp=root/"checkpoints"/"EngiProof_CHECKPOINT_CURRENT.zip"; bp.parent.mkdir(parents=True,exist_ok=True)
        include=[]
        for rel in BUNDLE_FILES:
            p=root/rel
            if p.is_file(): include.append((rel,p))
        for name in artifacts: include.append((f"checkpoint/{name}",out/name))
        for rel,_ in include:
            low=rel.lower()
            if low.endswith(".pdf") or low.startswith("private_sources/") or low.startswith("client_data/"):
                raise ValueError(f"forbidden checkpoint content: {rel}")
        manifest=[{"path":rel.replace("\\","/"),"sha256":_sha(p),"bytes":p.stat().st_size} for rel,p in include]
        mp=out/"bundle_manifest.json"
        mp.write_text(json.dumps({
            "schema_version":"engiproof.checkpoint_bundle_manifest/1.0",
            "generated_at_utc":now,"files":manifest,
            "rule":"No copyrighted source PDF or private client data included."
        },indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        include.append(("checkpoint/bundle_manifest.json",mp))
        if bp.exists(): bp.unlink()
        with zipfile.ZipFile(bp,"w",zipfile.ZIP_DEFLATED) as z:
            for rel,p in include: z.write(p,rel.replace("\\","/"))
        bundle_rel=str(bp.relative_to(root)).replace("\\","/"); bundle_sha=_sha(bp)

    return {
        "schema_version":"engiproof.checkpoint_result/1.0",
        "status":"PASS" if audit["status"] in {"PASS","WARN"} else "FAIL",
        "framework_version":__version__,"output_dir":str(out.relative_to(root)).replace("\\","/"),
        "bundle":bundle_rel,"bundle_sha256":bundle_sha,"continuity_audit_status":audit["status"],
        "current_study":state.get("current_study"),"current_checkpoint":state.get("current_checkpoint"),
        "next_action":state.get("next_action"),
        "copyright_boundary":"No source PDF/private client data included."
    }
