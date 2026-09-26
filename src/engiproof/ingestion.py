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
_EQ_RE = re.compile(r"\b(?:eq(?:uation)?\.?)[\s\u00a0]*\(?([A-Za-z]?\d+[A-Za-z]?)\)?", re.I)
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


def discover_targets(source: str | Path, max_candidates: int = 40) -> dict[str, Any]:
    path = Path(source).expanduser().resolve()
    extracted = _read_source_text(path)
    found: dict[tuple[str, str], dict[str, Any]] = {}

    def add(kind: str, label: str, page: int, line: str, base_score: float) -> None:
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
                "status": "CANDIDATE",
                "selection": "REVIEW_REQUIRED",
            }
        else:
            item = found[key]
            if page not in item["pages"]:
                item["pages"].append(page)
            item["score"] = max(item["score"], score)
            item["signals"] = sorted(set(item["signals"]) | set(sig))

    for page_no, text in enumerate(extracted.pages, 1):
        for raw in text.splitlines():
            line = " ".join(raw.split())
            if not line:
                continue
            for m in _FIG_RE.finditer(line):
                add("figure", f"Figure {m.group(1)}", page_no, line, 0.80)
            for m in _TABLE_RE.finditer(line):
                add("table", f"Table {m.group(1)}", page_no, line, 0.82)
            for m in _EQ_RE.finditer(line):
                add("equation", f"Equation ({m.group(1)})", page_no, line, 0.78)
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
            "Candidates are lexical discoveries, not verified engineering targets.",
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
    root = (root or project_root()).resolve()
    pid = paper_id.upper()
    manifest_path = root / "engiproof" / "studies" / pid / "study.json"
    issues: list[str] = []
    if not manifest_path.is_file():
        return {"paper_id": pid, "ready": False, "issues": ["study manifest missing"]}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    issues.extend(validate_study_manifest(manifest))
    if manifest.get("evidence_status") in {"DRAFT", "BLOCKED"}:
        issues.append(f"evidence_status is {manifest.get('evidence_status')}")
    if not manifest.get("selected_targets"):
        issues.append("no selected_targets")
    if not manifest.get("result_files"):
        issues.append("no result_files")
    if not manifest.get("verification_tests"):
        issues.append("no verification_tests")
    if not manifest.get("tools"):
        issues.append("no callable tools")
    runner = root / manifest.get("runner", "")
    if not runner.is_file():
        issues.append("runner missing")
    return {
        "paper_id": pid,
        "ready": not issues,
        "issues": issues,
        "evidence_status": manifest.get("evidence_status"),
        "rule": "Promotion requires source-bounded results, tests and callable methods; execution alone is insufficient.",
    }


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
    root = (root or project_root()).resolve()
    pid = paper_id.upper()
    intake_dir = _intake_root(root) / pid
    manifest_path = root / "engiproof" / "studies" / pid / "study.json"
    registry = json.loads((root / "engiproof" / "registry.json").read_text(encoding="utf-8"))
    stages = []

    def stage(name: str, complete: bool, detail: str = "") -> None:
        stages.append({"stage": name, "complete": bool(complete), "detail": detail})

    fp = intake_dir / "source_fingerprint.json"
    tc = intake_dir / "target_candidates.json"
    dossiers = intake_dir / "target_dossiers.json"
    structures = intake_dir / "structure_candidates.json"
    task_bundle = intake_dir / "reproduction_tasks.json"
    cmp_templates = intake_dir / "comparison_templates.json"
    stage("source_fingerprint", fp.is_file(), "SHA-256/source metadata")
    stage("target_discovery", tc.is_file(), "Figure/Table/Equation/Appendix candidates")
    stage("source_enrichment", dossiers.is_file(), "bounded target locators/excerpts/parameter candidates")
    stage("structure_extraction", structures.is_file(), "equation/table/figure/definition structure candidates")
    stage("study_scaffold", manifest_path.is_file(), "DRAFT study contract/evidence graph")
    stage("task_bundle", task_bundle.is_file(), "kind-specific reproduction task bundle")
    stage("comparison_templates", cmp_templates.is_file(), "target-type comparison metric templates")
    manifest: dict[str, Any] = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    stage("reproduction", bool(manifest.get("result_files")), f"{len(manifest.get('result_files', []))} result files")
    independent = [t for t in manifest.get("tools", []) if t.get("evidence_class") == "INDEPENDENT"]
    stage("independent_check", bool(independent), f"{len(independent)} independent callable methods")
    stage("comparison", bool(manifest.get("comparisons")), f"{len(manifest.get('comparisons', []))} comparison records")
    stage("discrepancy", bool(manifest.get("discrepancies")), f"{len(manifest.get('discrepancies', []))} discrepancy records")
    eg = root / manifest.get("evidence_graph", "") if manifest.get("evidence_graph") else None
    stage("evidence_graph", bool(eg and eg.is_file()), "machine-readable provenance/evidence graph")
    stage("callable_method", bool(manifest.get("tools")), f"{len(manifest.get('tools', []))} callable methods")
    stage("live_registry", pid in registry.get("studies", []), "promotion gate passed")
    complete_count = sum(1 for s in stages if s["complete"])
    return {
        "schema_version": "engiproof.pipeline_status/1.0",
        "paper_id": pid,
        "completed_stages": complete_count,
        "total_stages": len(stages),
        "progress_fraction": complete_count / len(stages),
        "evidence_status": manifest.get("evidence_status", "INTAKE_ONLY"),
        "stages": stages,
        "next_stage": next((s["stage"] for s in stages if not s["complete"]), "complete"),
    }


ENRICHMENT_SCHEMA = "engiproof.source_enrichment/1.0"
DOSSIER_SCHEMA = "engiproof.target_dossiers/1.0"
TASK_BUNDLE_SCHEMA = "engiproof.reproduction_tasks/1.0"

_UNIT_RE = re.compile(r"(?<![A-Za-z])(?:mm|cm|m|km|Pa|kPa|MPa|GPa|bar|N|kN|MN|N/m|N/m2|N/m\^2|kg|kg/m|Hz|ms|K|degC|°C|1/m)(?![A-Za-z])")
_SYMBOL_RE = re.compile(r"(?<![A-Za-z0-9_])(?:Delta|delta|sigma|epsilon|alpha|beta|gamma|mu|nu|rho|E|G|I|A|D|t|L|S|N|p|T|H|f|k|w|x|y)(?:_[A-Za-z0-9]+)?(?![A-Za-z0-9_])")
_MATHISH_RE = re.compile(r"[=+\-*/^]|\b(?:sin|cos|tan|ln|log|exp|sqrt)\b", re.I)


def _normalize_line(raw: str) -> str:
    return " ".join(raw.replace("\u00a0", " ").split())


def _bounded_excerpt(text: str, limit: int = 240) -> str:
    text = _normalize_line(text)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _candidate_patterns(candidate: dict[str, Any]) -> list[re.Pattern[str]]:
    kind = candidate.get("kind")
    label = candidate.get("label", "")
    if kind == "figure":
        num = label.replace("Figure", "").strip()
        return [re.compile(rf"\b(?:fig(?:ure)?\.?)\s*{re.escape(num)}\b", re.I)]
    if kind == "table":
        num = label.replace("Table", "").strip()
        return [re.compile(rf"\btable\s*{re.escape(num)}\b", re.I)]
    if kind == "equation":
        num = label.replace("Equation", "").strip().strip("()")
        return [re.compile(rf"\b(?:eq(?:uation)?\.?)\s*\(?{re.escape(num)}\)?\b", re.I), re.compile(rf"\({re.escape(num)}\)\s*$", re.I)]
    if kind == "appendix":
        num = label.replace("Appendix", "").strip()
        return [re.compile(rf"\bappendix\s+{re.escape(num)}\b", re.I)]
    return [re.compile(re.escape(label), re.I)] if label else []


def _page_lines(extracted: SourceText) -> list[list[str]]:
    return [[_normalize_line(x) for x in page.splitlines()] for page in extracted.pages]


def _parameter_inventory(lines: list[str], center: int, radius: int = 5) -> dict[str, Any]:
    lo=max(0,center-radius); hi=min(len(lines),center+radius+1)
    window=" ".join(lines[lo:hi])
    units=sorted(set(m.group(0) for m in _UNIT_RE.finditer(window)), key=str.lower)
    symbols=sorted(set(m.group(0) for m in _SYMBOL_RE.finditer(window)), key=str.lower)
    return {"units": units[:30], "symbol_candidates": symbols[:40]}


def _equation_block(lines: list[str], center: int, equation_label: str | None = None) -> dict[str, Any] | None:
    expected=None
    if equation_label:
        expected=equation_label.replace("Equation","").strip().strip("()")
    lo=max(0,center-6); hi=min(len(lines),center+7)
    if expected:
        exact=[]
        pat=re.compile(rf"\({re.escape(expected)}\)\s*$",re.I)
        for idx in range(lo,hi):
            line=lines[idx]
            if line and pat.search(line):
                exact.append((idx,line))
        if exact:
            idx,line=min(exact,key=lambda x:abs(x[0]-center))
            # PDF extraction often places the equation body on the previous line
            # and the printed equation number on a line by itself.
            text=line
            if re.fullmatch(rf"\({re.escape(expected)}\)",line.strip(),re.I):
                prev=next((lines[j] for j in range(idx-1,max(-1,idx-4),-1) if lines[j]),"")
                if prev and ("=" in prev or re.search(r"[+*/^]",prev)):
                    text=f"{prev} {line}"
            return {
                "page_line": idx+1,
                "text": _bounded_excerpt(text, 320),
                "operator_count": len(_MATHISH_RE.findall(text)),
                "status": "EXTRACTED_TEXT_CANDIDATE",
                "review_required": True,
            }
        # Do not attach a different numbered equation merely because it is nearby.
        return None
    candidates=[]
    for idx in range(lo,hi):
        line=lines[idx]
        if not line or len(line)>320:
            continue
        has_eq="=" in line or bool(re.search(r"[+*/^]",line))
        if has_eq:
            score=len(_MATHISH_RE.findall(line))+(2 if "=" in line else 0)
            candidates.append((score,idx,line))
    if not candidates:
        return None
    _,idx,line=max(candidates,key=lambda x:(x[0],-abs(x[1]-center)))
    return {
        "page_line": idx+1,
        "text": _bounded_excerpt(line, 320),
        "operator_count": len(_MATHISH_RE.findall(line)),
        "status": "EXTRACTED_TEXT_CANDIDATE",
        "review_required": True,
    }


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


def _table_rows(lines: list[str], caption_idx: int, max_rows: int = 12) -> list[str]:
    rows=[]
    for idx in range(caption_idx+1,min(len(lines),caption_idx+1+max_rows+6)):
        line=lines[idx]
        if not line:
            if rows:
                break
            continue
        if re.match(r"^(?:Figure|Fig\.|Table|[A-Z][A-Z\s\-/]{8,})\b",line):
            if rows:
                break
        # Keep compact, table-like rows only. This is a candidate, not a parser guarantee.
        tokens=line.split()
        numeric=sum(bool(re.fullmatch(r"[-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?",t.strip('(),')) ) for t in tokens)
        if numeric or len(tokens)<=10:
            rows.append(_bounded_excerpt(line,220))
        if len(rows)>=max_rows:
            break
    return rows


def extract_structures(paper_id: str, source: str | Path, root: Path | None = None) -> dict[str, Any]:
    """Extract conservative equation/table/figure/definition structure candidates.

    This is a source-review accelerator. It does not convert extracted text into evidence.
    """
    root=(root or project_root()).resolve(); pid=paper_id.upper()
    intake=load_intake(pid,root=root); fp=fingerprint_source(source)
    if fp["sha256"] != intake["fingerprint"].get("sha256"):
        raise ValueError(f"Source fingerprint mismatch for {pid}")
    extracted=_read_source_text(Path(source).expanduser().resolve()); pages=_page_lines(extracted)
    dossiers=load_target_dossiers(pid,root=root)
    tables=[]; figures=[]; equations=[]
    for d in dossiers.get("dossiers",[]):
        kind=d.get("kind"); label=d.get("label","")
        if kind=="equation":
            blocks=[]; seen=set()
            for occ in d.get("occurrences",[]):
                b=occ.get("equation_block_candidate")
                if b and b.get("text") and b["text"] not in seen:
                    seen.add(b["text"]); blocks.append({"locator":f"p{occ['page']}:l{b['page_line']}","text":b['text'],"review_required":True})
            equations.append({"candidate_id":d["candidate_id"],"label":label,"blocks":blocks,"status":"STRUCTURE_CANDIDATE" if blocks else "BLOCK_NOT_EXTRACTED"})
        elif kind in {"table","figure"}:
            num=label.replace("Table","").replace("Figure","").strip()
            items=[]
            for pno in sorted({o['page'] for o in d.get('occurrences',[])}):
                lines=pages[pno-1]
                for idx,caption in _caption_candidates(lines,kind,num):
                    item={"locator":f"p{pno}:l{idx+1}","caption_candidate":_bounded_excerpt(caption,260),"review_required":True}
                    if kind=="table":
                        item["row_candidates"]=_table_rows(lines,idx)
                    items.append(item)
            rec={"candidate_id":d["candidate_id"],"label":label,"occurrences":items[:8],"status":"STRUCTURE_CANDIDATE" if items else "NOT_EXTRACTED"}
            (tables if kind=="table" else figures).append(rec)
    definitions=_definition_candidates(pages)
    doc={
        "schema_version":STRUCTURE_SCHEMA,"paper_id":pid,"source_sha256":fp["sha256"],
        "equations":equations,"tables":tables,"figures":figures,"definitions":definitions,
        "review_required":True,
        "notes":[
            "Structure extraction is heuristic and source-review only.",
            "Table rows/captions/equation blocks may reflect PDF text-order limitations.",
            "No extracted structure is engineering evidence until reviewed, reproduced and verified."
        ]
    }
    out=_intake_root(root)/pid/"structure_candidates.json"
    out.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    ingestion=intake["ingestion"]; ingestion["structure_candidates"]=f"engiproof/intake/{pid}/structure_candidates.json"; ingestion["status"]="STRUCTURE_REVIEW_REQUIRED"
    (_intake_root(root)/pid/"ingestion.json").write_text(json.dumps(ingestion,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return {"paper_id":pid,"status":"STRUCTURE_REVIEW_REQUIRED","equation_count":len(equations),"table_count":len(tables),"figure_count":len(figures),"definition_count":len(definitions),"artifact":f"engiproof/intake/{pid}/structure_candidates.json"}


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
