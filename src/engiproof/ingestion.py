from __future__ import annotations

import hashlib
import json
import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from . import __version__
from .core import project_root, load_registry, validate_study_manifest

INGESTION_SCHEMA = "engiproof.ingestion/1.0"
FINGERPRINT_SCHEMA = "engiproof.source_fingerprint/1.0"
TARGET_SCHEMA = "engiproof.target_candidates/1.0"

_FIG_RE = re.compile(r"\b(?:fig(?:ure)?\.?)[\s\u00a0]*(\d+[A-Za-z]?(?:\([A-Za-z]\))?)", re.I)
_TABLE_RE = re.compile(r"\btable[\s\u00a0]*(\d+[A-Za-z]?)", re.I)
_EQ_RE = re.compile(r"\b(?:eq(?:uation)?\.?)[\s\u00a0]*\(?\s*([A-Za-z]?\d+[A-Za-z]?)\s*\)?", re.I)
_EQ_GROUP_RE = re.compile(r"\beqs?\.?[\s\u00a0]*((?:(?:\(|ð)\s*[A-Za-z]?\d+[A-Za-z]?\s*(?:\)|Þ)[,;:\s]*(?:and\s*)?)+)", re.I)
_EQ_GROUP_ITEM_RE = re.compile(r"(?:\(|ð)\s*([A-Za-z]?\d+[A-Za-z]?)\s*(?:\)|Þ)", re.I)
_PRINTED_EQ_RE = re.compile(r"(?:\(|ð)\s*([A-Za-z]?\d+[A-Za-z]?)\s*(?:\)|Þ)\s*$", re.I)
_DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)
_APPENDIX_RE = re.compile(r"\bappendix[\s\u00a0]+([A-Za-z0-9]+)", re.I)
_SIGNAL_WORDS = {
    "comparison": 0.10,
    "compare": 0.08,
    "experimental": 0.10,
    "experiment": 0.08,
    "validation": 0.10,
    "validate": 0.08,
    "finite element": 0.08,
    "numerical": 0.05,
    "analytical": 0.05,
    "measured": 0.07,
    "test": 0.05,
    "results": 0.03,
}


@dataclass(frozen=True)
class SourceText:
    pages: list[str]
    metadata: dict[str, Any]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_source_text(path: Path) -> SourceText:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except Exception as exc:  # pragma: no cover - dependency checked by CI
            raise RuntimeError("PDF ingestion requires pypdf. Install EngiProof dependencies.") from exc
        reader = PdfReader(str(path))
        pages = [(p.extract_text() or "") for p in reader.pages]
        md = reader.metadata or {}
        metadata = {
            "page_count": len(reader.pages),
            "pdf_title": getattr(md, "title", None) or md.get("/Title"),
            "pdf_author": getattr(md, "author", None) or md.get("/Author"),
        }
        return SourceText(pages=pages, metadata=metadata)
    if suffix in {".txt", ".md", ".rst"}:
        text = path.read_text(encoding="utf-8", errors="replace")
        return SourceText(pages=[text], metadata={"page_count": 1})
    raise ValueError(f"Unsupported ingestion source type: {suffix or '<none>'}. Use PDF/TXT/MD/RST.")


def fingerprint_source(source: str | Path) -> dict[str, Any]:
    path = Path(source).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    extracted = _read_source_text(path)
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    out = {
        "schema_version": FINGERPRINT_SCHEMA,
        "canonical_filename": path.name,
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size,
        "mime_type": mime,
        "suffix": path.suffix.lower(),
        "source_path_policy": "basename_only",
        "text_extractable": any(p.strip() for p in extracted.pages),
        **extracted.metadata,
    }
    # Never persist an absolute machine-specific path.
    return out


def _signals(line: str) -> tuple[list[str], float]:
    low = line.lower()
    found = [k for k in _SIGNAL_WORDS if k in low]
    bonus = sum(_SIGNAL_WORDS[k] for k in found)
    return found, min(bonus, 0.25)


def _math_context_score(lines: list[str], idx: int) -> int:
    lo=max(0,idx-8); hi=min(len(lines),idx+1)
    window=" ".join(lines[lo:hi])
    score=len(re.findall(r"[=+\-*/^]",window))
    score += len(re.findall(r"(?:σ|Δ|π|√|¼|½|\bP[pP]?\b|\bD[io]?\b|\bt[io]?\b)",window))
    return score


def _equation_mentions(line: str) -> list[str]:
    nums=[]
    for m in _EQ_RE.finditer(line):
        nums.append(m.group(1))
    for gm in _EQ_GROUP_RE.finditer(line):
        nums.extend(x.group(1) for x in _EQ_GROUP_ITEM_RE.finditer(gm.group(1)))
    # preserve order while removing duplicates
    return list(dict.fromkeys(nums))


def discover_targets(source: str | Path, max_candidates: int = 40) -> dict[str, Any]:
    path = Path(source).expanduser().resolve()
    extracted = _read_source_text(path)
    found: dict[tuple[str, str], dict[str, Any]] = {}

    def add(kind: str, label: str, page: int, line: str, base_score: float, method: str="lexical") -> None:
        sig, bonus = _signals(line)
        key = (kind, label.lower())
        score = round(min(base_score + bonus, 0.99), 3)
        if key not in found:
            found[key] = {
                "kind": kind,
                "label": label,
                "pages": [page],
                "score": score,
                "signals": sig,
                "discovery_methods": [method],
                "status": "CANDIDATE",
                "selection": "REVIEW_REQUIRED",
            }
        else:
            item = found[key]
            if page not in item["pages"]:
                item["pages"].append(page)
            item["score"] = max(item["score"], score)
            item["signals"] = sorted(set(item["signals"]) | set(sig))
            item["discovery_methods"] = sorted(set(item.get("discovery_methods",[])) | {method})

    for page_no, text in enumerate(extracted.pages, 1):
        lines=[_normalize_line(x) for x in text.splitlines()]
        for idx,line in enumerate(lines):
            if not line:
                continue
            for m in _FIG_RE.finditer(line):
                add("figure", f"Figure {m.group(1)}", page_no, line, 0.80)
            for m in _TABLE_RE.finditer(line):
                add("table", f"Table {m.group(1)}", page_no, line, 0.82)
            for num in _equation_mentions(line):
                method="cross_reference_group" if re.search(r"\bEqs?\.",line,re.I) else "equation_reference"
                add("equation", f"Equation ({num})", page_no, line, 0.78, method)
            pm=_PRINTED_EQ_RE.search(line)
            if pm and _math_context_score(lines,idx)>=2:
                add("equation",f"Equation ({pm.group(1)})",page_no,line,0.76,"printed_equation_number")
            for m in _APPENDIX_RE.finditer(line):
                add("appendix", f"Appendix {m.group(1)}", page_no, line, 0.65)

    items = sorted(found.values(), key=lambda x: (-x["score"], x["kind"], x["label"]))[:max_candidates]
    for i, item in enumerate(items, 1):
        item["candidate_id"] = f"T{i:03d}"
    return {
        "schema_version": TARGET_SCHEMA,
        "source_filename": path.name,
        "candidate_count": len(items),
        "review_required": True,
        "candidates": items,
        "notes": [
            "Candidates are lexical/cross-reference discoveries, not verified engineering targets.",
            "Printed equation numbers are recovered only when nearby text is math-like.",
            "No equation, table or figure is promoted to evidence until source review and reproduction are completed.",
        ],
    }

def _intake_root(root: Path) -> Path:
    return root / "engiproof" / "intake"


def ingest_source(
    source: str | Path,
    paper_id: str,
    title: str | None = None,
    doi: str | None = None,
    year: int | None = None,
    max_candidates: int = 40,
    root: Path | None = None,
) -> dict[str, Any]:
    root = (root or project_root()).resolve()
    pid = paper_id.upper()
    source_path = Path(source).expanduser().resolve()
    fp = fingerprint_source(source_path)
    targets = discover_targets(source_path, max_candidates=max_candidates)
    inferred_title = title or fp.get("pdf_title") or source_path.stem
    intake_dir = _intake_root(root) / pid
    if intake_dir.exists():
        raise FileExistsError(f"Intake already exists for {pid}: {intake_dir.relative_to(root)}")
    intake_dir.mkdir(parents=True, exist_ok=False)
    fingerprint_path = intake_dir / "source_fingerprint.json"
    targets_path = intake_dir / "target_candidates.json"
    fingerprint_path.write_text(json.dumps(fp, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    targets_path.write_text(json.dumps(targets, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ingestion = {
        "schema_version": INGESTION_SCHEMA,
        "paper_id": pid,
        "title": inferred_title,
        "year": int(year or 0),
        "doi": doi or "PENDING",
        "source_fingerprint": str(fingerprint_path.relative_to(root)).replace("\\", "/"),
        "target_candidates": str(targets_path.relative_to(root)).replace("\\", "/"),
        "raw_source_copied": False,
        "status": "TARGET_REVIEW_REQUIRED",
        "candidate_count": targets["candidate_count"],
        "next_actions": [
            "Review and select source-backed equation/table/figure targets.",
            "Create a DRAFT study scaffold from the reviewed intake.",
            "Implement reproduction and independent checks before any promotion to the live registry.",
        ],
    }
    (intake_dir / "ingestion.json").write_text(json.dumps(ingestion, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (intake_dir / "REVIEW.md").write_text(
        f"# {pid} intake review\n\n"
        f"**Title:** {inferred_title}\n\n"
        f"**Status:** `TARGET_REVIEW_REQUIRED`\n\n"
        f"The original source is not copied into the repository. Fingerprint: `{fp['sha256']}`.\n\n"
        "Review `target_candidates.json`. Candidate discovery is lexical only and does not establish evidence.\n",
        encoding="utf-8",
    )
    return ingestion


def list_intakes(root: Path | None = None) -> list[dict[str, Any]]:
    root = (root or project_root()).resolve()
    idir = _intake_root(root)
    if not idir.is_dir():
        return []
    out = []
    for d in sorted(p for p in idir.iterdir() if p.is_dir()):
        p = d / "ingestion.json"
        if p.is_file():
            out.append(json.loads(p.read_text(encoding="utf-8")))
    return out


def load_intake(paper_id: str, root: Path | None = None) -> dict[str, Any]:
    root = (root or project_root()).resolve()
    pid = paper_id.upper()
    idir = _intake_root(root) / pid
    ingest = idir / "ingestion.json"
    if not ingest.is_file():
        raise KeyError(f"No EngiProof intake for {pid}.")
    data = json.loads(ingest.read_text(encoding="utf-8"))
    candidates = json.loads((idir / "target_candidates.json").read_text(encoding="utf-8"))
    fingerprint = json.loads((idir / "source_fingerprint.json").read_text(encoding="utf-8"))
    return {"ingestion": data, "fingerprint": fingerprint, "targets": candidates}


def _norm_doi(value: str | None) -> str:
    if not value:
        return ""
    v=value.strip().lower()
    for prefix in ("https://doi.org/","http://doi.org/","doi:"):
        if v.startswith(prefix): v=v[len(prefix):]
    return v.rstrip(".,; ")


def _source_identity_candidates(extracted: SourceText) -> dict[str, Any]:
    head="\n".join(extracted.pages[:2])
    dois=[]
    for m in _DOI_RE.finditer(head):
        d=_norm_doi(m.group(0))
        if d and d not in dois:
            dois.append(d)

    lines=[_normalize_line(x) for x in head.splitlines() if _normalize_line(x)]
    publication_years=[]
    secondary_years=[]
    year_evidence=[]

    def add_year(year: int, role: str, line: str) -> None:
        rec={"year":int(year),"role":role,"excerpt":_bounded_excerpt(line,180)}
        if rec not in year_evidence:
            year_evidence.append(rec)
        target=publication_years if role=="PUBLICATION" else secondary_years
        if int(year) not in target:
            target.append(int(year))

    for line in lines:
        years=[int(y) for y in re.findall(r"\b((?:19|20)\d{2})\b",line)]
        if not years:
            continue
        low=line.lower()

        # Administrative/history dates are not publication-year evidence.
        if re.search(r"\b(received|accepted|revised|submitted|copyright)\b|©",line,re.I):
            for y in years:
                add_year(y,"SECONDARY",line)
            continue

        # Strong publication-year patterns:
        #   Marine Structures 64 (2019) 401–420
        #   Published Online: October 31, 2011
        #   Publication date: 2019
        #   Proceedings ... 2011 ...
        citation_years=[int(y) for y in re.findall(r"\b\d{1,4}\s*\(((?:19|20)\d{2})\)\s*\d+\s*[–—-]\s*\d+",line)]
        if citation_years:
            for y in citation_years:
                add_year(y,"PUBLICATION",line)
            continue
        if re.search(r"\b(?:published(?:\s+online)?|publication\s+date)\b",line,re.I):
            for y in years:
                add_year(y,"PUBLICATION",line)
            continue
        if re.search(r"\bproceedings\b",line,re.I):
            for y in years:
                add_year(y,"PUBLICATION",line)
            continue

        # General year evidence is kept as secondary unless a stronger
        # publication pattern is available.
        for y in years:
            add_year(y,"SECONDARY",line)

    # Publication-year candidates are authoritative for the year check.
    # If none exist, do not turn received/accepted/copyright years into a
    # false publication-year conflict; leave year as NOT_CONFIRMED.
    years=publication_years[:8]

    title=(extracted.metadata.get("pdf_title") or "").strip()
    first_lines=lines
    return {
        "doi_candidates":dois[:8],
        "year_candidates":years,
        "secondary_year_candidates":secondary_years[:8],
        "year_evidence":year_evidence[:20],
        "pdf_title":title or None,
        "head_lines":first_lines[:30],
    }


def audit_source_identity(paper_id: str, source: str | Path, root: Path | None = None) -> dict[str, Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); intake=load_intake(pid,root=root)
    source_path=Path(source).expanduser().resolve(); fp=fingerprint_source(source_path)
    expected_sha=intake["fingerprint"].get("sha256")
    if fp["sha256"] != expected_sha:
        raise ValueError(f"Source fingerprint mismatch for {pid}: expected {expected_sha}, got {fp['sha256']}")
    extracted=_read_source_text(source_path); cand=_source_identity_candidates(extracted); ing=intake["ingestion"]
    expected_doi=_norm_doi(ing.get("doi")); found_dois=[_norm_doi(x) for x in cand["doi_candidates"]]
    issues=[]
    doi_status="NOT_FOUND_IN_SOURCE"
    if expected_doi and expected_doi!="pending":
        if expected_doi in found_dois: doi_status="MATCH"
        elif found_dois:
            doi_status="CONFLICT"; issues.append(f"configured DOI {expected_doi} conflicts with source DOI candidate(s): {', '.join(found_dois)}")
    expected_year=int(ing.get("year") or 0); found_years=cand["year_candidates"]
    year_status="NOT_CONFIRMED"
    if expected_year and found_years:
        if expected_year in found_years: year_status="MATCH"
        else:
            year_status="CONFLICT"; issues.append(f"configured year {expected_year} conflicts with source year candidate(s): {found_years}")
    expected_title=(ing.get("title") or "").strip()
    head_key=re.sub(r"[^a-z0-9]+","", " ".join(cand["head_lines"]).lower())
    title_key=re.sub(r"[^a-z0-9]+","",expected_title.lower())
    title_status="MATCH" if title_key and title_key in head_key else "NOT_CONFIRMED"
    status="CONFLICT" if issues else ("PASS" if doi_status=="MATCH" and title_status=="MATCH" else "REVIEW_REQUIRED")
    doc={
        "schema_version":"engiproof.source_identity_audit/1.0","paper_id":pid,"status":status,
        "source_sha256":fp["sha256"],"source_filename":fp["canonical_filename"],
        "configured":{"title":expected_title,"doi":ing.get("doi"),"year":expected_year},
        "source_candidates":{"doi":cand["doi_candidates"],"year":found_years,"secondary_years":cand.get("secondary_year_candidates",[]),"year_evidence":cand.get("year_evidence",[]),"pdf_title":cand["pdf_title"]},
        "checks":{"title":title_status,"doi":doi_status,"year":year_status},"issues":issues,
        "rule":"A DOI/year conflict is a source-identity blocker. Do not reproduce or promote until resolved."
    }
    idir=_intake_root(root)/pid; out=idir/"source_identity_audit.json"; out.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    ing["source_identity_audit"]=f"engiproof/intake/{pid}/source_identity_audit.json"
    if status=="CONFLICT":
        ing["status"]="SOURCE_IDENTITY_CONFLICT"
    elif status=="PASS" and ing.get("status")=="SOURCE_IDENTITY_CONFLICT":
        ing["status"]="SOURCE_IDENTITY_VERIFIED"
    elif status=="REVIEW_REQUIRED" and ing.get("status")=="SOURCE_IDENTITY_CONFLICT":
        ing["status"]="SOURCE_IDENTITY_REVIEW_REQUIRED"
    (idir/"ingestion.json").write_text(json.dumps(ing,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return doc


def load_source_identity_audit(paper_id: str, root: Path | None = None) -> dict[str, Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); p=_intake_root(root)/pid/"source_identity_audit.json"
    if not p.is_file(): raise KeyError(f"No source identity audit for {pid}; run engiproof audit-source {pid} <source>.")
    return json.loads(p.read_text(encoding="utf-8"))


def update_intake_metadata(paper_id: str, title: str | None = None, doi: str | None = None, year: int | None = None, root: Path | None = None) -> dict[str, Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); idir=_intake_root(root)/pid; intake=load_intake(pid,root=root); ing=intake["ingestion"]
    if title is not None: ing["title"]=title
    if doi is not None: ing["doi"]=doi
    if year is not None: ing["year"]=int(year)
    ing["status"]="METADATA_UPDATED_REAUDIT_REQUIRED"
    audit=idir/"source_identity_audit.json"
    if audit.is_file(): audit.unlink()
    (idir/"ingestion.json").write_text(json.dumps(ing,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    manifest_path=root/"engiproof"/"studies"/pid/"study.json"
    if manifest_path.is_file():
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        if title is not None: manifest["title"]=title
        if year is not None: manifest["year"]=int(year)
        if doi is not None: manifest.setdefault("source",{})["doi"]=doi
        manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    source_md=root/"papers"/pid/"SOURCE.md"
    if source_md.is_file() and title is not None:
        txt=source_md.read_text(encoding="utf-8")
        txt=re.sub(r"(?m)^\*\*Paper:\*\*.*$",f"**Paper:** {title}",txt)
        source_md.write_text(txt,encoding="utf-8")
    return {"paper_id":pid,"status":"METADATA_UPDATED_REAUDIT_REQUIRED","title":ing.get("title"),"doi":ing.get("doi"),"year":ing.get("year"),"source_sha256":intake["fingerprint"].get("sha256"),"next_action":f"engiproof audit-source {pid} <source>"}


def recover_equation_candidates(paper_id: str, source: str | Path, root: Path | None = None) -> dict[str, Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); intake=load_intake(pid,root=root); fp=fingerprint_source(source)
    if fp["sha256"] != intake["fingerprint"].get("sha256"): raise ValueError(f"Source fingerprint mismatch for {pid}")
    fresh=discover_targets(source,max_candidates=500)
    targets=intake["targets"]; existing=targets.get("candidates",[]); by_label={x.get("label"):x for x in existing}
    max_id=max([int(x.get("candidate_id","T000")[1:]) for x in existing if re.fullmatch(r"T\d+",x.get("candidate_id",""))] or [0])
    added=[]
    for c in fresh.get("candidates",[]):
        if c.get("kind")!="equation" or c.get("label") in by_label: continue
        max_id+=1; c=dict(c); c["candidate_id"]=f"T{max_id:03d}"; c["selection"]="REVIEW_REQUIRED"; existing.append(c); by_label[c["label"]]=c; added.append(c)
    targets["candidate_count"]=len(existing); targets["candidates"]=existing
    targets.setdefault("notes",[]).append("dev2 equation recovery appended cross-reference/printed-number candidates while preserving existing candidate IDs.")
    idir=_intake_root(root)/pid; (idir/"target_candidates.json").write_text(json.dumps(targets,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    doc={"schema_version":"engiproof.equation_recovery/1.0","paper_id":pid,"added_count":len(added),"added_candidates":added,"candidate_count":len(existing),"next_actions":[f"Re-run engiproof enrich {pid} <source>",f"Re-run engiproof extract-structures {pid} <source>",f"Run engiproof readiness {pid}"]}
    (idir/"equation_recovery.json").write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return doc


def scaffold_from_intake(
    paper_id: str,
    target_ids: Iterable[str] | None = None,
    top_targets: int = 3,
    root: Path | None = None,
) -> dict[str, Any]:
    root = (root or project_root()).resolve()
    pid = paper_id.upper()
    intake = load_intake(pid, root=root)
    pdir = root / "papers" / pid
    sdir = root / "engiproof" / "studies" / pid
    if pdir.exists() or sdir.exists():
        raise FileExistsError(f"Study scaffold already exists for {pid}.")
    candidates = intake["targets"].get("candidates", [])
    wanted = {x.upper() for x in target_ids or []}
    if wanted:
        selected = [c for c in candidates if c["candidate_id"].upper() in wanted]
        missing = wanted - {c["candidate_id"].upper() for c in selected}
        if missing:
            raise KeyError(f"Unknown target candidate IDs: {sorted(missing)}")
    else:
        selected = candidates[: max(0, int(top_targets))]
    pdir.mkdir(parents=True)
    sdir.mkdir(parents=True)
    ingestion = intake["ingestion"]
    fp = intake["fingerprint"]
    selected_labels = [x["label"] for x in selected]
    (pdir / "SOURCE.md").write_text(
        f"# {pid} source contract\n\n"
        f"**Paper:** {ingestion['title']}\n\n"
        f"**Source fingerprint:** `{fp['sha256']}`\n\n"
        f"**Selected candidate targets:** {', '.join(selected_labels) if selected_labels else 'NONE'}\n\n"
        "**Status:** `DRAFT`\n\n"
        "## Evidence boundary\n\n"
        "Targets were discovered automatically and remain DRAFT until a human/agent source review confirms the exact source location, inputs and method boundary. No reproduction is claimed by scaffolding.\n",
        encoding="utf-8",
    )
    (pdir / "tool_api.py").write_text('"""DRAFT callable tools. Do not expose until source-bounded and tested."""\n', encoding="utf-8")
    (pdir / "run_calculation.py").write_text('raise SystemExit("DRAFT: implement source-bounded reproduction before running")\n', encoding="utf-8")
    graph = {
        "schema_version": "engiproof.evidence_graph/1.0",
        "paper_id": pid,
        "nodes": [
            {
                "id": f"SOURCE-{pid}",
                "kind": "source",
                "label": ingestion["title"],
                "evidence_class": "PUBLISHED",
                "status": "SOURCE_READY",
                "source_refs": [ingestion.get("doi", "PENDING"), fp["sha256"]],
            }
        ] + [
            {
                "id": f"TARGET-{c['candidate_id']}",
                "kind": c["kind"],
                "label": c["label"],
                "evidence_class": "PUBLISHED",
                "status": "DRAFT",
                "source_refs": [f"page:{p}" for p in c["pages"]],
            }
            for c in selected
        ],
        "edges": [
            {"from": f"SOURCE-{pid}", "to": f"TARGET-{c['candidate_id']}", "relation": "contains_candidate"}
            for c in selected
        ],
        "qualification": "NOT_GRANTED",
    }
    (sdir / "evidence_graph.json").write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": "engiproof.study/1.1",
        "framework": "EngiProof",
        "framework_version": __version__,
        "paper_id": pid,
        "title": ingestion["title"],
        "year": ingestion.get("year", 0),
        "evidence_status": "DRAFT",
        "category": "UNCLASSIFIED",
        "source": {
            "canonical_pdf": fp["canonical_filename"],
            "sha256": fp["sha256"],
            "doi": ingestion.get("doi", "PENDING"),
        },
        "selected_targets": selected_labels,
        "runner": f"papers/{pid}/run_calculation.py",
        "source_contract": f"papers/{pid}/SOURCE.md",
        "evidence_graph": f"engiproof/studies/{pid}/evidence_graph.json",
        "result_files": [],
        "verification_tests": [],
        "tools": [],
        "comparisons": [],
        "discrepancies": [],
        "limitations": [
            "Automatically generated DRAFT scaffold only; no reproduction or engineering acceptance claimed.",
            "Target discovery is lexical and requires source review before implementation.",
            "Raw source is external to the repository; source SHA-256 is retained.",
        ],
        "next_actions": [
            "Confirm exact source target locators and required inputs.",
            "Implement source-bounded reproduction.",
            "Add an independent check where physically meaningful.",
            "Add comparison/discrepancy records and verification tests before promotion.",
        ],
        "qualification": "NOT_GRANTED",
        "ingestion_record": f"engiproof/intake/{pid}/ingestion.json",
    }
    (sdir / "study.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ingestion["status"] = "DRAFT_SCAFFOLDED"
    ingestion["selected_candidate_ids"] = [c["candidate_id"] for c in selected]
    (_intake_root(root) / pid / "ingestion.json").write_text(json.dumps(ingestion, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "paper_id": pid,
        "status": "DRAFT_SCAFFOLDED",
        "selected_targets": selected_labels,
        "registered_live": pid in load_registry().get("studies", []) if root == project_root().resolve() else False,
        "study_manifest": f"engiproof/studies/{pid}/study.json",
    }


def promotion_gate(paper_id: str, root: Path | None = None) -> dict[str, Any]:
    root = (root or project_root()).resolve(); pid = paper_id.upper(); manifest_path = root / "engiproof" / "studies" / pid / "study.json"; issues=[]
    if not manifest_path.is_file(): return {"paper_id":pid,"ready":False,"issues":["study manifest missing"]}
    manifest=json.loads(manifest_path.read_text(encoding="utf-8")); issues.extend(validate_study_manifest(manifest))
    if manifest.get("evidence_status") in {"DRAFT","BLOCKED"}: issues.append(f"evidence_status is {manifest.get('evidence_status')}")
    if not manifest.get("selected_targets"): issues.append("no selected_targets")
    if not manifest.get("result_files"): issues.append("no result_files")
    if not manifest.get("verification_tests"): issues.append("no verification_tests")
    if not manifest.get("tools"): issues.append("no callable tools")
    if not (root/manifest.get("runner","")).is_file(): issues.append("runner missing")
    if manifest.get("ingestion_record"):
        audit_path=_intake_root(root)/pid/"source_identity_audit.json"
        if not audit_path.is_file(): issues.append("source identity not audited")
        else:
            audit=json.loads(audit_path.read_text(encoding="utf-8"))
            if audit.get("status")=="CONFLICT": issues.append("source identity conflict")
        ready_path=_intake_root(root)/pid/"selected_target_readiness.json"
        if not ready_path.is_file(): issues.append("selected-target readiness not assessed")
        else:
            rr=json.loads(ready_path.read_text(encoding="utf-8"))
            if rr.get("status")!="READY": issues.append(f"selected-target readiness is {rr.get('status')}")
    from .discrepancy import discrepancy_gate
    dgate=discrepancy_gate(pid,root=root)
    for did in dgate.get("blocking_discrepancy_ids",[]): issues.append(f"unresolved discrepancy blocks promotion: {did}")
    return {"paper_id":pid,"ready":not issues,"issues":issues,"evidence_status":manifest.get("evidence_status"),"discrepancy_gate":dgate,"rule":"Promotion requires identity-consistent source, structurally ready selected targets, source-bounded results, tests and callable methods; unresolved high-priority evidence conflicts must also be resolved, bounded, or explicitly accepted. Execution alone is insufficient."}

def promote_study(paper_id: str, root: Path | None = None) -> dict[str, Any]:
    root = (root or project_root()).resolve()
    pid = paper_id.upper()
    gate = promotion_gate(pid, root=root)
    if not gate["ready"]:
        return {**gate, "status": "BLOCKED"}
    # A promotion gate must include actual computational verification, not field presence alone.
    from .core import verify_study
    if root == project_root().resolve():
        verification = verify_study(pid)
        if verification.get("status") not in {"PASS", "PASS_SOURCE_EXTERNAL"}:
            return {**gate, "status": "BLOCKED", "verification": verification, "issues": gate["issues"] + ["verification failed"]}
    reg_path = root / "engiproof" / "registry.json"
    registry = json.loads(reg_path.read_text(encoding="utf-8"))
    if pid not in registry["studies"]:
        registry["studies"].append(pid)
        registry["studies"] = sorted(registry["studies"])
        reg_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    idir = _intake_root(root) / pid / "ingestion.json"
    if idir.is_file():
        ingestion = json.loads(idir.read_text(encoding="utf-8"))
        ingestion["status"] = "PROMOTED_TO_LIVE_REGISTRY"
        idir.write_text(json.dumps(ingestion, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {**gate, "status": "PROMOTED", "registered_live": True}


def build_reproduction_plan(paper_id: str, root: Path | None = None) -> dict[str, Any]:
    root = (root or project_root()).resolve()
    pid = paper_id.upper()
    manifest_path = root / "engiproof" / "studies" / pid / "study.json"
    if not manifest_path.is_file():
        raise KeyError(f"No study scaffold for {pid}; run engiproof scaffold {pid} first.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    targets = manifest.get("selected_targets", [])
    plan = {
        "schema_version": "engiproof.reproduction_plan/1.0",
        "paper_id": pid,
        "status": "PLANNED_NOT_EXECUTED",
        "source": manifest.get("source", {}),
        "targets": [],
        "global_gates": [
            "Confirm exact source locator and published inputs before coding.",
            "Do not infer or tune missing inputs to force agreement.",
            "Keep PUBLISHED, INDEPENDENT and SOLVER_NEW evidence distinct.",
            "Record discrepancies instead of hiding them.",
            "Do not expose callable tools until verification tests pass.",
        ],
    }
    for i, label in enumerate(targets, 1):
        plan["targets"].append({
            "target_id": f"R{i:03d}",
            "label": label,
            "tasks": [
                "confirm_source_locator",
                "extract_published_inputs_and_units",
                "implement_source_bounded_reproduction",
                "run_deterministic_reproduction",
                "design_independent_check_if_physically_meaningful",
                "compare_against_published_reference",
                "record_metrics_and_discrepancy",
                "update_evidence_graph",
                "add_verification_test",
                "expose_callable_tool_only_after_gate",
            ],
            "status": "NOT_STARTED",
        })
    out = root / "engiproof" / "intake" / pid / "reproduction_plan.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return plan


def pipeline_status(paper_id: str, root: Path | None = None) -> dict[str, Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); intake_dir=_intake_root(root)/pid; manifest_path=root/"engiproof"/"studies"/pid/"study.json"; registry=json.loads((root/"engiproof"/"registry.json").read_text(encoding="utf-8")); stages=[]
    def stage(name,complete,detail=""): stages.append({"stage":name,"complete":bool(complete),"detail":detail})
    fp=intake_dir/"source_fingerprint.json"; tc=intake_dir/"target_candidates.json"; identity=intake_dir/"source_identity_audit.json"; dossiers=intake_dir/"target_dossiers.json"; structures=intake_dir/"structure_candidates.json"; readiness=intake_dir/"selected_target_readiness.json"; task_bundle=intake_dir/"reproduction_tasks.json"; cmp_templates=intake_dir/"comparison_templates.json"
    stage("source_fingerprint",fp.is_file(),"SHA-256/source metadata")
    stage("target_discovery",tc.is_file(),"Figure/Table/Equation/Appendix candidates")
    identity_doc=json.loads(identity.read_text(encoding="utf-8")) if identity.is_file() else {}
    stage("source_identity",identity.is_file() and identity_doc.get("status")!="CONFLICT",f"{identity_doc.get('status','not audited')} DOI/title/year audit")
    stage("source_enrichment",dossiers.is_file(),"bounded target locators/excerpts/parameter candidates")
    stage("structure_extraction",structures.is_file(),"structure candidates generated; existence alone is not readiness")
    readiness_doc=json.loads(readiness.read_text(encoding="utf-8")) if readiness.is_file() else {}
    stage("selected_target_readiness",readiness_doc.get("status")=="READY",readiness_doc.get("summary","not assessed"))
    stage("study_scaffold",manifest_path.is_file(),"DRAFT study contract/evidence graph")
    stage("task_bundle",task_bundle.is_file(),"kind-specific reproduction task bundle")
    stage("comparison_templates",cmp_templates.is_file(),"target-type comparison metric templates")
    manifest=json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    stage("reproduction",bool(manifest.get("result_files")),f"{len(manifest.get('result_files',[]))} result files")
    independent=[t for t in manifest.get("tools",[]) if t.get("evidence_class")=="INDEPENDENT"]
    stage("independent_check",bool(independent),f"{len(independent)} independent callable methods")
    stage("comparison",bool(manifest.get("comparisons")),f"{len(manifest.get('comparisons',[]))} comparison records")
    stage("discrepancy",bool(manifest.get("discrepancies")),f"{len(manifest.get('discrepancies',[]))} discrepancy records")
    disc_assessment=root/"papers"/pid/"results"/"discrepancy_assessment.json"
    stage("discrepancy_assessment",disc_assessment.is_file(),"generic classification/escalation assessment")
    eg=root/manifest.get("evidence_graph","") if manifest.get("evidence_graph") else None
    stage("evidence_graph",bool(eg and eg.is_file()),"machine-readable provenance/evidence graph")
    stage("callable_method",bool(manifest.get("tools")),f"{len(manifest.get('tools',[]))} callable methods")
    stage("live_registry",pid in registry.get("studies",[]),"promotion gate passed")
    complete_count=sum(1 for x in stages if x["complete"])
    return {"schema_version":"engiproof.pipeline_status/1.1","paper_id":pid,"completed_stages":complete_count,"total_stages":len(stages),"progress_fraction":complete_count/len(stages),"evidence_status":manifest.get("evidence_status","INTAKE_ONLY"),"stages":stages,"next_stage":next((x["stage"] for x in stages if not x["complete"]),"complete")}


ENRICHMENT_SCHEMA = "engiproof.source_enrichment/1.0"
DOSSIER_SCHEMA = "engiproof.target_dossiers/1.0"
TASK_BUNDLE_SCHEMA = "engiproof.reproduction_tasks/1.0"

_UNIT_RE = re.compile(r"(?<![A-Za-z])(?:mm|cm|m|km|Pa|kPa|MPa|GPa|bar|N|kN|MN|N/m|N/m2|N/m\^2|kg|kg/m|Hz|ms|K|degC|°C|1/m)(?![A-Za-z])")
_SYMBOL_RE = re.compile(r"(?<![A-Za-z0-9_])(?:Delta|delta|sigma|epsilon|alpha|beta|gamma|mu|nu|rho|E|G|I|A|D|t|L|S|N|p|T|H|f|k|w|x|y)(?:_[A-Za-z0-9]+)?(?![A-Za-z0-9_])")
_MATHISH_RE = re.compile(r"[=+\-*/^]|\b(?:sin|cos|tan|ln|log|exp|sqrt)\b", re.I)


def _normalize_line(raw: str) -> str:
    text=" ".join(raw.replace("\u00a0"," ").split())
    # Several Type1/CFF engineering PDFs expose printed equation parentheses as ð...Þ.
    text=re.sub(r"ð\s*([A-Za-z]?\d+[A-Za-z]?)\s*Þ",r"(\1)",text)
    return text


def _bounded_excerpt(text: str, limit: int = 240) -> str:
    text = _normalize_line(text)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _candidate_patterns(candidate: dict[str, Any]) -> list[re.Pattern[str]]:
    kind=candidate.get("kind"); label=candidate.get("label","")
    if kind=="figure":
        num=label.replace("Figure","").strip(); return [re.compile(rf"\b(?:fig(?:ure)?\.?)\s*{re.escape(num)}\b",re.I)]
    if kind=="table":
        num=label.replace("Table","").strip(); return [re.compile(rf"\btable\s*{re.escape(num)}\b",re.I)]
    if kind=="equation":
        num=label.replace("Equation","").strip().strip("()")
        return [re.compile(rf"\b(?:eq(?:uation)?s?\.?)\s*\(?\s*{re.escape(num)}\s*\)?\b",re.I),re.compile(rf"(?:\(|ð)\s*{re.escape(num)}\s*(?:\)|Þ)\s*$",re.I)]
    if kind=="appendix":
        num=label.replace("Appendix","").strip(); return [re.compile(rf"\bappendix\s+{re.escape(num)}\b",re.I)]
    return [re.compile(re.escape(label),re.I)] if label else []

def _page_lines(extracted: SourceText) -> list[list[str]]:
    return [[_normalize_line(x) for x in page.splitlines()] for page in extracted.pages]


def _parameter_inventory(lines: list[str], center: int, radius: int = 5) -> dict[str, Any]:
    lo=max(0,center-radius); hi=min(len(lines),center+radius+1)
    window=" ".join(lines[lo:hi])
    units=sorted(set(m.group(0) for m in _UNIT_RE.finditer(window)), key=str.lower)
    symbols=sorted(set(m.group(0) for m in _SYMBOL_RE.finditer(window)), key=str.lower)
    return {"units": units[:30], "symbol_candidates": symbols[:40]}


def _looks_prose(line: str) -> bool:
    words=line.split()
    return len(words)>=9 and not re.search(r"[=+*/^σΔπ¼½]",line) and bool(re.search(r"[A-Za-z]{3,}",line))


def _equation_block(lines: list[str], center: int, equation_label: str | None = None) -> dict[str, Any] | None:
    expected=equation_label.replace("Equation","").strip().strip("()") if equation_label else None
    lo=max(0,center-18); hi=min(len(lines),center+10); matches=[]
    if expected:
        pat=re.compile(rf"(?:\(|ð)\s*{re.escape(expected)}\s*(?:\)|Þ)\s*$",re.I)
        for idx in range(lo,hi):
            if lines[idx] and pat.search(lines[idx]): matches.append(idx)
        if not matches: return None
        idx=min(matches,key=lambda j:abs(j-center)); collected=[]
        current=pat.sub("",lines[idx]).strip()
        if current: collected.append(current)
        prose_hits=0
        for j in range(idx-1,max(-1,idx-13),-1):
            line=lines[j]
            if not line:
                if collected: break
                continue
            if _looks_prose(line):
                prose_hits+=1
                if collected or prose_hits>=1: break
                continue
            # Short PDF-fragment lines are common inside displayed equations.
            if len(line)<=140:
                collected.append(line)
            else: break
        collected=list(reversed(collected))
        text=" ".join(collected).strip()
        if not text: return None
        math_score=len(_MATHISH_RE.findall(text))+len(re.findall(r"[σΔπ¼½]",text))
        if math_score<1: return None
        return {"page_line":idx+1,"line_start":max(1,idx-len(collected)+1),"line_end":idx+1,"text":_bounded_excerpt(text,700),"operator_count":math_score,"status":"EXTRACTED_TEXT_CANDIDATE","review_required":True,"printed_equation_number":expected}
    return None

def enrich_source(
    paper_id: str,
    source: str | Path,
    root: Path | None = None,
    excerpt_limit: int = 240,
) -> dict[str, Any]:
    """Re-open an external source, verify its fingerprint, and build target dossiers.

    The source itself is never copied. Only bounded target excerpts, locators, hashes,
    units/symbol candidates and task metadata are persisted.
    """
    root=(root or project_root()).resolve(); pid=paper_id.upper()
    intake=load_intake(pid,root=root)
    source_path=Path(source).expanduser().resolve()
    fp=fingerprint_source(source_path)
    expected=intake["fingerprint"].get("sha256")
    if fp["sha256"] != expected:
        raise ValueError(f"Source fingerprint mismatch for {pid}: expected {expected}, got {fp['sha256']}")
    extracted=_read_source_text(source_path); pages=_page_lines(extracted)
    candidates=intake["targets"].get("candidates",[])
    dossiers=[]
    for c in candidates:
        occurrences=[]
        pats=_candidate_patterns(c)
        page_filter=set(c.get("pages",[]))
        for pno,lines in enumerate(pages,1):
            if page_filter and pno not in page_filter:
                continue
            for idx,line in enumerate(lines):
                if not line or not any(p.search(line) for p in pats):
                    continue
                before=next((lines[j] for j in range(idx-1,max(-1,idx-4),-1) if lines[j]),"")
                after=next((lines[j] for j in range(idx+1,min(len(lines),idx+4)) if lines[j]),"")
                occ={
                    "page":pno,
                    "line":idx+1,
                    "locator":f"p{pno}:l{idx+1}",
                    "excerpt":_bounded_excerpt(line,excerpt_limit),
                    "before":_bounded_excerpt(before,min(excerpt_limit,160)),
                    "after":_bounded_excerpt(after,min(excerpt_limit,160)),
                    "parameter_inventory":_parameter_inventory(lines,idx),
                }
                if c.get("kind")=="equation":
                    occ["equation_block_candidate"]=_equation_block(lines,idx,c.get("label"))
                occurrences.append(occ)
        dossiers.append({
            "candidate_id":c["candidate_id"],
            "kind":c["kind"],
            "label":c["label"],
            "discovery_score":c.get("score"),
            "occurrence_count":len(occurrences),
            "occurrences":occurrences[:12],
            "source_status":"LOCATED" if occurrences else "NOT_LOCATED",
            "review_required":True,
        })
    page_map=[]
    for pno,lines in enumerate(pages,1):
        normalized="\n".join(lines).encode("utf-8")
        page_map.append({
            "page":pno,
            "line_count":len(lines),
            "nonblank_line_count":sum(bool(x) for x in lines),
            "text_sha256":hashlib.sha256(normalized).hexdigest(),
        })
    idir=_intake_root(root)/pid
    source_map={
        "schema_version":"engiproof.source_map/1.0",
        "paper_id":pid,
        "source_filename":fp["canonical_filename"],
        "source_sha256":fp["sha256"],
        "page_count":len(pages),
        "pages":page_map,
        "raw_text_persisted":False,
        "policy":"Only target-bounded excerpts are persisted; full extracted source text remains ephemeral.",
    }
    dossier_doc={
        "schema_version":DOSSIER_SCHEMA,
        "paper_id":pid,
        "source_sha256":fp["sha256"],
        "dossier_count":len(dossiers),
        "located_count":sum(d["source_status"]=="LOCATED" for d in dossiers),
        "dossiers":dossiers,
        "notes":[
            "Dossiers are automated source-location aids, not evidence promotion.",
            "Equation text candidates are extraction hints and require source review before implementation.",
        ],
    }
    (idir/"source_map.json").write_text(json.dumps(source_map,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (idir/"target_dossiers.json").write_text(json.dumps(dossier_doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    ingestion=intake["ingestion"]
    ingestion["source_enrichment"]="engiproof/intake/%s/target_dossiers.json"%pid
    ingestion["status"]="SOURCE_ENRICHED_REVIEW_REQUIRED"
    (idir/"ingestion.json").write_text(json.dumps(ingestion,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return {
        "schema_version":ENRICHMENT_SCHEMA,
        "paper_id":pid,
        "status":"SOURCE_ENRICHED_REVIEW_REQUIRED",
        "source_sha256":fp["sha256"],
        "candidate_count":len(dossiers),
        "located_count":dossier_doc["located_count"],
        "source_map":f"engiproof/intake/{pid}/source_map.json",
        "target_dossiers":f"engiproof/intake/{pid}/target_dossiers.json",
    }


def load_target_dossiers(paper_id: str, root: Path | None = None) -> dict[str, Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper()
    p=_intake_root(root)/pid/"target_dossiers.json"
    if not p.is_file():
        raise KeyError(f"No enriched target dossiers for {pid}; run engiproof enrich {pid} <source>.")
    return json.loads(p.read_text(encoding="utf-8"))


def target_dossier(paper_id: str, candidate_id: str, root: Path | None = None) -> dict[str, Any]:
    doc=load_target_dossiers(paper_id,root=root); cid=candidate_id.upper()
    item=next((d for d in doc.get("dossiers",[]) if d.get("candidate_id","").upper()==cid),None)
    if item is None:
        raise KeyError(f"No target dossier {cid} for {paper_id.upper()}.")
    return {"schema_version":DOSSIER_SCHEMA,"paper_id":paper_id.upper(),"dossier":item}


def _task_template(kind: str) -> list[str]:
    common=[
        "confirm_source_locator",
        "confirm_published_inputs_units_and_assumptions",
        "implement_source_bounded_reproduction",
        "run_deterministic_reproduction",
        "design_independent_check_if_physically_meaningful",
        "compare_against_published_reference",
        "record_metrics_and_discrepancy",
        "update_evidence_graph",
        "add_verification_test",
        "expose_callable_tool_only_after_gate",
    ]
    prefixes={
        "equation":["transcribe_equation_and_symbol_definitions","dimension_and_sign_convention_check"],
        "table":["define_table_schema","extract_or_import_published_table_values","audit_units_rounding_and_duplicates"],
        "figure":["identify_axes_series_and_normalization","choose_graphical_or_raw_reference_path","record_digitization_uncertainty_if_applicable"],
        "appendix":["map_appendix_equations_to_main_method","confirm_branch_and_applicability_conditions"],
    }
    return prefixes.get(kind,[])+common


def build_task_bundle(paper_id: str, root: Path | None = None) -> dict[str, Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper()
    dossiers=load_target_dossiers(pid,root=root)
    manifest_path=root/"engiproof"/"studies"/pid/"study.json"
    manifest=json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    selected=set(manifest.get("selected_targets",[]))
    tasks=[]
    for d in dossiers.get("dossiers",[]):
        if selected and d["label"] not in selected:
            continue
        first=(d.get("occurrences") or [{}])[0]
        inv=first.get("parameter_inventory",{})
        tasks.append({
            "task_id":f"TASK-{d['candidate_id']}",
            "candidate_id":d["candidate_id"],
            "kind":d["kind"],
            "label":d["label"],
            "source_status":d["source_status"],
            "primary_locator":first.get("locator"),
            "unit_candidates":inv.get("units",[]),
            "symbol_candidates":inv.get("symbol_candidates",[]),
            "steps":_task_template(d["kind"]),
            "status":"READY_FOR_SOURCE_REVIEW" if d["source_status"]=="LOCATED" else "BLOCKED_SOURCE_NOT_LOCATED",
            "promotion_rule":"Do not convert this task into live evidence until exact inputs, method boundary, comparison and verification are recorded.",
        })
    bundle={
        "schema_version":TASK_BUNDLE_SCHEMA,
        "paper_id":pid,
        "status":"TASKS_GENERATED_NOT_EXECUTED",
        "task_count":len(tasks),
        "tasks":tasks,
        "global_gates":[
            "Never tune unknowns to match a published result.",
            "Preserve PUBLISHED / INDEPENDENT / SOLVER_NEW evidence separation.",
            "Graphical references must carry digitization/precision limitations.",
            "A callable method requires verification tests and an explicit evidence status.",
        ],
    }
    out=_intake_root(root)/pid/"reproduction_tasks.json"
    out.write_text(json.dumps(bundle,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return bundle

STRUCTURE_SCHEMA = "engiproof.structure_candidates/1.0"
COMPARISON_TEMPLATE_SCHEMA = "engiproof.comparison_templates/1.0"
_DEFINITION_RE = re.compile(r"^\s*([A-Za-zΑ-Ωα-ωΔδΣσΕεΜμΝνΡρ][A-Za-z0-9_Α-Ωα-ωΔδΣσΕεΜμΝνΡρ]{0,12})\s*=\s*(.{2,220})$")


def _definition_candidates(pages: list[list[str]], max_items: int = 120) -> list[dict[str, Any]]:
    out=[]; seen=set()
    for pno, lines in enumerate(pages,1):
        for idx,line in enumerate(lines):
            m=_DEFINITION_RE.match(line)
            if not m:
                continue
            symbol=m.group(1); definition=_bounded_excerpt(m.group(2),180)
            key=(symbol.lower(),definition.lower())
            if key in seen:
                continue
            seen.add(key)
            out.append({"symbol":symbol,"definition":definition,"locator":f"p{pno}:l{idx+1}","status":"CANDIDATE","review_required":True})
            if len(out)>=max_items:
                return out
    return out


def _caption_candidates(lines: list[str], kind: str, number: str) -> list[tuple[int,str]]:
    if kind=="figure":
        pat=re.compile(rf"\b(?:fig(?:ure)?\.?)\s*{re.escape(number)}\b",re.I)
    else:
        pat=re.compile(rf"\btable\s*{re.escape(number)}\b",re.I)
    return [(i,line) for i,line in enumerate(lines) if line and pat.search(line)]


_CAPTION_REFERENCE_START = re.compile(
    r"^(?:and\b|or\b|is\b|are\b|was\b|were\b|shows?\b|compares?\b|"
    r"listed\b|given\b|see\b|as\b|in\b|from\b|with\b|and\s+table\b)",
    re.I,
)


def _caption_remainder(line: str, kind: str, number: str) -> str | None:
    if kind=="figure":
        m=re.match(rf"^\s*(?:fig(?:ure)?\.?)\s*{re.escape(number)}\s*(.*)$", line, re.I)
    else:
        m=re.match(rf"^\s*table\s*{re.escape(number)}\s*(.*)$", line, re.I)
    return m.group(1).strip() if m else None


def _is_true_caption(line: str, kind: str, number: str) -> bool:
    """Recognize publisher caption styles without treating ordinary cross-references as captions.

    Supported examples include:
      Table 1. Pipeline data
      Table 1 Pipeline data
      Table 1 - Pipeline data
      Figure 4 - Case 1
      Fig. 4. Case 1
    """
    remainder=_caption_remainder(line,kind,number)
    if remainder is None:
        return False
    if not remainder:
        return False
    cleaned=remainder.lstrip(" .:-–—").strip()
    if not cleaned:
        return False
    if _CAPTION_REFERENCE_START.match(cleaned):
        return False
    # A punctuation delimiter is strong caption evidence.  For punctuation-free
    # publisher styles, require some title-like text after the number.
    had_delimiter=bool(re.match(r"^[.:\-–—]",remainder))
    if had_delimiter:
        return True
    words=re.findall(r"[A-Za-z][A-Za-z0-9/-]*",cleaned)
    return len(words)>=2


def _next_nonblank_line(lines: list[str], idx: int, max_ahead: int = 3) -> tuple[int,str] | None:
    for j in range(idx+1,min(len(lines),idx+1+max_ahead)):
        if lines[j]:
            return j,lines[j]
    return None


def _looks_like_split_caption_title(line: str) -> bool:
    if not line or len(line)>220:
        return False
    if re.match(r"^(?:table|fig(?:ure)?\.?|eq(?:uation)?\.?|references?\b|©)",line,re.I):
        return False
    # Avoid page/journal footers and bare numeric fragments.
    if re.search(r"\b(?:Marine Structures|Journal|Proceedings)\b.*\b\d{3,4}\b",line,re.I):
        return False
    words=re.findall(r"[A-Za-z][A-Za-z0-9'/-]*",line)
    return len(words)>=2


def _is_true_caption_at(lines: list[str], idx: int, kind: str, number: str) -> bool:
    line=lines[idx]
    if _is_true_caption(line,kind,number):
        return True
    remainder=_caption_remainder(line,kind,number)
    if remainder is None:
        return False
    # Publisher style:
    #   Table 1
    #   Geometric parameters of ...
    # and analogous split figure captions.
    cleaned=remainder.lstrip(" .:-–—").strip()
    if cleaned:
        return False
    nxt=_next_nonblank_line(lines,idx)
    return bool(nxt and _looks_like_split_caption_title(nxt[1]))


def _caption_display_at(lines: list[str], idx: int, kind: str, number: str) -> str:
    line=lines[idx]
    remainder=_caption_remainder(line,kind,number)
    if remainder is not None and not remainder.lstrip(" .:-–—").strip():
        nxt=_next_nonblank_line(lines,idx)
        if nxt and _looks_like_split_caption_title(nxt[1]):
            return f"{line} — {nxt[1]}"
    return line


def _is_any_table_caption_at(lines: list[str], idx: int) -> bool:
    line=lines[idx]
    m=re.match(r"^\s*table\s*(\d+[A-Za-z]?)\s*(.*)$",line,re.I)
    return bool(m and _is_true_caption_at(lines,idx,"table",m.group(1)))


def _is_any_figure_caption_at(lines: list[str], idx: int) -> bool:
    line=lines[idx]
    m=re.match(r"^\s*(?:fig(?:ure)?\.?)\s*(\d+[A-Za-z]?)\s*(.*)$",line,re.I)
    return bool(m and _is_true_caption_at(lines,idx,"figure",m.group(1)))


def _is_any_table_caption(line: str) -> bool:
    m=re.match(r"^\s*table\s*(\d+[A-Za-z]?)\s*(.*)$",line,re.I)
    if not m:
        return False
    return _is_true_caption(line,"table",m.group(1))


def _is_any_figure_caption(line: str) -> bool:
    m=re.match(r"^\s*(?:fig(?:ure)?\.?)\s*(\d+[A-Za-z]?)\s*(.*)$",line,re.I)
    if not m:
        return False
    return _is_true_caption(line,"figure",m.group(1))


def _strip_table_tags(line: str) -> str:
    return re.sub(r"\bT\d+:\d+\b","",line).strip()


def _table_rows(lines: list[str], caption_idx: int, max_rows: int = 48) -> list[str]:
    rows=[]
    for idx in range(caption_idx+1,min(len(lines),caption_idx+1+max_rows)):
        line=_strip_table_tags(lines[idx])
        if not line:
            continue
        if idx>caption_idx+1 and (
            _is_any_table_caption_at(lines,idx)
            or _is_any_figure_caption_at(lines,idx)
            or re.match(r"^(?:©|References\b)",line,re.I)
        ):
            break
        rows.append(_bounded_excerpt(line,260))
    return rows


def _numeric_token_count(line: str) -> int:
    return len(re.findall(r"(?<![A-Za-z])[-+]?\d+(?:[,.]\d+)*(?:[Ee][-+]?\d+)?(?:%|[A-Za-z]+)?",line))


def _looks_engineering_property_row(line: str) -> bool:
    # Common engineering tables use a parameter/symbol in the first column,
    # an optional [unit], then one or more numeric values.
    # Examples: D [mm] 298.5 394.0; EAS [N] 2.532E+9 4.979E+9.
    if not re.match(r"^[A-Za-zΑ-Ωα-ωΔδΣσ][A-Za-z0-9_Α-Ωα-ωΔδΣσ]{0,15}\s*(?:\[[^\]]+\])?\s+",line):
        return False
    return _numeric_token_count(line)>=1


def _table_block(lines: list[str], caption_idx: int, max_lines: int = 56) -> dict[str, Any]:
    raw=_table_rows(lines,caption_idx,max_rows=max_lines); headers=[]; data=[]; footnotes=[]; data_started=False
    for line in raw:
        looks_data=bool(re.match(r"^(?:PIP[- ]?\d+|Case\b|\d+[A-Za-z-]*\b)",line,re.I)) and _numeric_token_count(line)>=2
        if not looks_data and _looks_engineering_property_row(line):
            looks_data=True
        if not looks_data and _numeric_token_count(line)>=4 and len(line.split())<=24:
            looks_data=True
        if looks_data:
            data_started=True; data.append(line); continue
        if data_started:
            footnotes.append(line)
        else:
            headers.append(line)
    status="TABLE_DATA_CANDIDATE" if data else ("HEADER_ONLY" if headers else "NOT_EXTRACTED")
    return {"status":status,"header_lines":headers[:24],"data_rows":data[:40],"footnotes":footnotes[:16],"data_row_count":len(data),"review_required":True}

def extract_structures(paper_id: str, source: str | Path, root: Path | None = None) -> dict[str, Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); intake=load_intake(pid,root=root); fp=fingerprint_source(source)
    if fp["sha256"] != intake["fingerprint"].get("sha256"): raise ValueError(f"Source fingerprint mismatch for {pid}")
    extracted=_read_source_text(Path(source).expanduser().resolve()); pages=_page_lines(extracted); dossiers=load_target_dossiers(pid,root=root); tables=[]; figures=[]; equations=[]
    for d in dossiers.get("dossiers",[]):
        kind=d.get("kind"); label=d.get("label","")
        if kind=="equation":
            blocks=[]; seen=set()
            for occ in d.get("occurrences",[]):
                b=occ.get("equation_block_candidate")
                if b and b.get("text") and b["text"] not in seen:
                    seen.add(b["text"]); blocks.append({"locator":f"p{occ['page']}:l{b['page_line']}","line_start":b.get("line_start"),"line_end":b.get("line_end"),"text":b["text"],"printed_equation_number":b.get("printed_equation_number"),"review_required":True})
            equations.append({"candidate_id":d["candidate_id"],"label":label,"blocks":blocks,"status":"STRUCTURE_CANDIDATE" if blocks else "BLOCK_NOT_EXTRACTED"})
        elif kind in {"table","figure"}:
            num=label.replace("Table","").replace("Figure","").strip(); items=[]
            for pno in sorted({o['page'] for o in d.get('occurrences',[])}):
                lines=pages[pno-1]
                for idx,caption in _caption_candidates(lines,kind,num):
                    is_true_caption=_is_true_caption_at(lines,idx,kind,num)
                    display_caption=_caption_display_at(lines,idx,kind,num)
                    item={"locator":f"p{pno}:l{idx+1}","caption_candidate":_bounded_excerpt(display_caption,260),"caption_anchor":is_true_caption,"review_required":True}
                    if kind=="table":
                        item["row_candidates"]=_table_rows(lines,idx)
                        item["table_block_candidate"]=_table_block(lines,idx) if is_true_caption else None
                    items.append(item)
            rec={"candidate_id":d["candidate_id"],"label":label,"occurrences":items[:12],"status":"STRUCTURE_CANDIDATE" if items else "NOT_EXTRACTED"}; (tables if kind=="table" else figures).append(rec)
    definitions=_definition_candidates(pages)
    doc={"schema_version":"engiproof.structure_candidates/1.1","paper_id":pid,"source_sha256":fp["sha256"],"equations":equations,"tables":tables,"figures":figures,"definitions":definitions,"review_required":True,"notes":["Structure extraction is heuristic and source-review only.","Printed equation recovery handles common Type1/CFF ð...Þ numbering artifacts.","Table readiness requires a recognized publisher caption anchor and at least one data-row candidate.","No extracted structure is engineering evidence until reviewed, reproduced and verified."]}
    out=_intake_root(root)/pid/"structure_candidates.json"; out.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    ingestion=intake["ingestion"]; ingestion["structure_candidates"]=f"engiproof/intake/{pid}/structure_candidates.json"; ingestion["status"]="STRUCTURE_REVIEW_REQUIRED"; (_intake_root(root)/pid/"ingestion.json").write_text(json.dumps(ingestion,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    manifest_path=root/"engiproof"/"studies"/pid/"study.json"
    readiness=selected_target_readiness(pid,root=root,structures=doc,write=True) if manifest_path.is_file() else {"status":"NOT_ASSESSED"}
    return {"paper_id":pid,"status":"STRUCTURE_REVIEW_REQUIRED","equation_count":len(equations),"table_count":len(tables),"figure_count":len(figures),"definition_count":len(definitions),"selected_target_readiness":readiness["status"],"artifact":f"engiproof/intake/{pid}/structure_candidates.json"}


def selected_target_readiness(paper_id: str, root: Path | None = None, structures: dict[str, Any] | None = None, write: bool = True) -> dict[str, Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); manifest_path=root/"engiproof"/"studies"/pid/"study.json"
    if not manifest_path.is_file(): raise KeyError(f"No study scaffold for {pid}.")
    manifest=json.loads(manifest_path.read_text(encoding="utf-8")); structures=structures or load_structure_candidates(pid,root=root); by_label={}
    for kind,key in (("equation","equations"),("table","tables"),("figure","figures")):
        for item in structures.get(key,[]): by_label[item.get("label")]=(kind,item)
    items=[]
    for label in manifest.get("selected_targets",[]):
        kind_item=by_label.get(label)
        if not kind_item:
            items.append({"label":label,"status":"BLOCKED","reason":"selected target absent from structure candidates"}); continue
        kind,item=kind_item; status="BLOCKED"; reason=""
        if kind=="equation":
            blocks=[b for b in item.get("blocks",[]) if b.get("text")]
            status="READY" if blocks else "BLOCKED"; reason="equation body candidate extracted" if blocks else "equation body not extracted"
        elif kind=="table":
            blocks=[o.get("table_block_candidate") for o in item.get("occurrences",[]) if o.get("caption_anchor") and o.get("table_block_candidate")]
            data_rows=sum((b or {}).get("data_row_count",0) for b in blocks)
            status="READY" if data_rows>0 else ("PARTIAL" if blocks else "BLOCKED"); reason=f"{data_rows} data-row candidate(s) under true table caption" if blocks else "true table caption/data block not extracted"
        else:
            caps=[o for o in item.get("occurrences",[]) if o.get("caption_anchor")]
            status="PARTIAL" if caps else "BLOCKED"; reason="figure caption located; axes/series still require review" if caps else "figure caption not located"
        items.append({"label":label,"kind":kind,"status":status,"reason":reason})
    overall="READY" if items and all(x["status"]=="READY" for x in items) else ("PARTIAL" if any(x["status"] in {"READY","PARTIAL"} for x in items) else "BLOCKED")
    summary=f"{sum(x['status']=='READY' for x in items)}/{len(items)} selected targets READY"
    doc={"schema_version":"engiproof.selected_target_readiness/1.0","paper_id":pid,"status":overall,"summary":summary,"targets":items,"rule":"Reproduction is blocked until selected equation/table targets are structurally ready; figure targets remain review-gated unless axes/series are resolved."}
    if write:
        out=_intake_root(root)/pid/"selected_target_readiness.json"; out.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return doc


def load_selected_target_readiness(paper_id: str, root: Path | None = None) -> dict[str, Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); p=_intake_root(root)/pid/"selected_target_readiness.json"
    if not p.is_file(): return selected_target_readiness(pid,root=root)
    return json.loads(p.read_text(encoding="utf-8"))

def load_structure_candidates(paper_id: str, root: Path | None = None) -> dict[str, Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); p=_intake_root(root)/pid/"structure_candidates.json"
    if not p.is_file():
        raise KeyError(f"No structure candidates for {pid}; run engiproof extract-structures {pid} <source>.")
    return json.loads(p.read_text(encoding="utf-8"))


def build_comparison_templates(paper_id: str, root: Path | None = None) -> dict[str, Any]:
    root=(root or project_root()).resolve(); pid=paper_id.upper(); manifest_path=root/"engiproof"/"studies"/pid/"study.json"
    if not manifest_path.is_file():
        raise KeyError(f"No study scaffold for {pid}.")
    manifest=json.loads(manifest_path.read_text(encoding="utf-8")); selected=set(manifest.get("selected_targets",[]))
    structures=load_structure_candidates(pid,root=root)
    templates=[]
    for group,kind in ((structures.get('equations',[]),'equation'),(structures.get('tables',[]),'table'),(structures.get('figures',[]),'figure')):
        for item in group:
            if selected and item.get('label') not in selected:
                continue
            if kind=='equation': metrics=['absolute_difference','relative_difference_percent','dimensional_consistency']
            elif kind=='table': metrics=['row_match_count','absolute_difference','relative_difference_percent','rounding_tolerance']
            else: metrics=['point_count','mean_absolute_error','max_absolute_error','normalized_rmse','digitization_uncertainty']
            templates.append({
                "template_id":f"CMP-{item['candidate_id']}","candidate_id":item['candidate_id'],"label":item['label'],"kind":kind,
                "reference_type":"PUBLISHED","suggested_metrics":metrics,"status":"TEMPLATE_ONLY",
                "required_fields":["reference_population","reproduced_population","units_or_normalization","metrics","limitations"],
                "rule":"Populate metrics only after source-backed reproduction; do not use template creation as evidence promotion."
            })
    doc={"schema_version":COMPARISON_TEMPLATE_SCHEMA,"paper_id":pid,"template_count":len(templates),"templates":templates,"status":"TEMPLATES_GENERATED_NOT_EVALUATED"}
    out=_intake_root(root)/pid/"comparison_templates.json"; out.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return doc
