"""Tracked, text-free ingestion summaries (Paper A gap G3).

Intake directories (``engiproof/intake/<ID>/``) are local and gitignored
because they can hold source-bounded excerpts. This module derives a small
summary from them that can be tracked: hashes, counts, statuses and target
identifiers only. No source text, excerpts, captions, definitions, locators or
free-text reasons are copied.

When no local intake is available, the summary states that explicitly instead
of backfilling from prose.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

SCHEMA = "engiproof.ingestion_summary/1.0"
SOURCE_FORMATS = {"BORN_DIGITAL", "SCANNED_WITH_TEXT_LAYER", "SCANNED_IMAGE_ONLY", "NOT_RECORDED"}
STATUSES = {"SUMMARISED_FROM_LOCAL_INTAKE", "PENDING_LOCAL_SUMMARY", "NO_INGESTION_RECORD"}
ROUTES = {"ENGIPROOF_PIPELINE_V0_2", "NOT_RECORDED"}
RULE = ("Text-free record: hashes, counts, statuses and target identifiers only. It records what the ingestion "
        "pipeline produced; it is not evidence, and candidate extraction is not reproduction.")
EXCLUDED = ["source text", "excerpts", "captions", "definitions", "line locators", "free-text readiness reasons"]


def _root(root: Path | None) -> Path:
    from .core import project_root
    return (root or project_root()).resolve()


def _load(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def summary_path(paper_id: str, root: Path | None = None) -> Path:
    return _root(root) / "engiproof" / "studies" / paper_id.upper() / "ingestion_summary.json"


def _image_sizes(page: Any) -> list[tuple[int, int]]:
    """Pixel sizes of image XObjects on a page, read from the dictionaries (no decoding)."""
    out = []
    try:
        xobjects = page["/Resources"].get_object().get("/XObject")
        xobjects = xobjects.get_object() if xobjects is not None else {}
        for ref in xobjects.values():
            obj = ref.get_object()
            if obj.get("/Subtype") == "/Image":
                out.append((int(obj.get("/Width", 0)), int(obj.get("/Height", 0))))
    except Exception:
        pass
    return out


def detect_source_format(pdf_path: str | Path) -> dict[str, Any]:
    """Classify a PDF as born-digital or scanned from page-sized raster images.

    A page counts as a raster page when it carries an image whose aspect ratio
    matches the page (within 5 %) at 100-1200 dpi. The PDF is read locally and
    nothing from it is persisted except the counts returned here.
    """
    from pypdf import PdfReader
    reader = PdfReader(str(pdf_path))
    raster_pages = text_pages = 0
    dpis: list[int] = []
    for page in reader.pages:
        w_in = float(page.mediabox.width) / 72.0
        h_in = float(page.mediabox.height) / 72.0
        try:
            if (page.extract_text() or "").strip():
                text_pages += 1
        except Exception:
            pass
        for iw, ih in _image_sizes(page):
            if not (iw and ih and w_in and h_in):
                continue
            dx, dy = iw / w_in, ih / h_in
            if 100 <= dx <= 1200 and 100 <= dy <= 1200 and abs(dx / dy - 1.0) <= 0.05:
                raster_pages += 1
                dpis.append(round((dx + dy) / 2))
                break
    n = len(reader.pages)
    if n and raster_pages >= 0.5 * n:
        fmt = "SCANNED_WITH_TEXT_LAYER" if text_pages else "SCANNED_IMAGE_ONLY"
    else:
        fmt = "BORN_DIGITAL"
    return {"source_format": fmt, "page_count": n, "page_raster_count": raster_pages, "text_page_count": text_pages,
            "raster_dpi_median": sorted(dpis)[len(dpis) // 2] if dpis else None,
            "basis": "AUTOMATIC_PAGE_RASTER_DETECTION"}


def _identity_refs(root: Path, pid: str, manifest: dict[str, Any]) -> list[str]:
    refs = []
    if (manifest.get("source") or {}).get("identity_basis"):
        refs.append(f"engiproof/studies/{pid}/study.json#source.identity_basis")
    for rel in (f"papers/{pid}/reference/source_identity.json", f"papers/{pid}/SOURCE.md"):
        if (root / rel).is_file():
            refs.append(rel)
    return refs


def _counts(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(i.get(key)) for i in items).items()))


def build_ingestion_summary(paper_id: str, root: Path | None = None, source_format: str | None = None,
                            source_format_basis: str | None = None, source_pdf: str | Path | None = None,
                            today: str | None = None) -> dict[str, Any]:
    root = _root(root)
    pid = paper_id.upper()
    intake = root / "engiproof" / "intake" / pid
    manifest = _load(root / "engiproof" / "studies" / pid / "study.json") or {}
    study_sha = (manifest.get("source") or {}).get("sha256")
    ingestion = _load(intake / "ingestion.json")
    base = {"schema_version": SCHEMA, "paper_id": pid, "recorded_on": today or date.today().isoformat(),
            "rule": RULE, "excluded_by_design": EXCLUDED}
    if ingestion is None:
        return {**base, "ingestion_status": "NO_LOCAL_INTAKE",
                "note": f"No local intake at engiproof/intake/{pid}/; nothing summarised."}
    fp = _load(intake / "source_fingerprint.json") or {}
    audit = _load(intake / "source_identity_audit.json") or {}
    cands = (_load(intake / "target_candidates.json") or {}).get("candidates", [])
    dossiers = _load(intake / "target_dossiers.json") or {}
    recovery = _load(intake / "equation_recovery.json") or {}
    structs = _load(intake / "structure_candidates.json") or {}
    ready = _load(intake / "selected_target_readiness.json") or {}

    fmt: dict[str, Any] = {"source_format": "NOT_RECORDED", "basis": None}
    if source_pdf is None:
        canonical = (manifest.get("source") or {}).get("canonical_pdf")
        candidate = root / "01_doc" / canonical if canonical else None
        if candidate is not None and candidate.is_file():
            source_pdf = candidate
    if source_pdf is not None:
        import hashlib
        pdf_sha = hashlib.sha256(Path(source_pdf).read_bytes()).hexdigest()
        if pdf_sha == fp.get("sha256"):
            fmt = detect_source_format(source_pdf)
        else:
            fmt = {"source_format": "NOT_RECORDED", "basis": None,
                   "note": "Local PDF sha256 differs from the intake fingerprint; format not detected."}
    if source_format is not None:
        if source_format not in SOURCE_FORMATS:
            raise ValueError(f"source_format must be one of {sorted(SOURCE_FORMATS)}")
        fmt = {**fmt, "source_format": source_format, "basis": source_format_basis or "MANUAL"}

    targets = ready.get("targets", [])
    selected_ids = ingestion.get("selected_candidate_ids") or []
    summary = {
        **base,
        "ingestion_status": "SUMMARISED_FROM_LOCAL_INTAKE",
        "ingestion_route": "ENGIPROOF_PIPELINE_V0_2",
        "recorded_from": f"engiproof/intake/{pid}/ (local, gitignored)",
        "intake_status": ingestion.get("status"),
        "raw_source_copied": ingestion.get("raw_source_copied"),
        "source": {
            "sha256": fp.get("sha256"),
            "matches_study_manifest_sha256": (fp.get("sha256") == study_sha) if study_sha and fp.get("sha256") else None,
            "size_bytes": fp.get("size_bytes"),
            "page_count": fp.get("page_count"),
            "text_extractable": fp.get("text_extractable"),
            "format": fmt,
        },
        "identity_audit": {
            "status": audit.get("status"),
            "checks": audit.get("checks"),
            "issue_count": len(audit.get("issues") or []),
            "resolution_refs": _identity_refs(root, pid, manifest),
        },
        "candidates": {
            "total": len(cands),
            "by_kind": _counts(cands, "kind"),
            "dossiers_located": dossiers.get("located_count"),
            "dossiers_total": dossiers.get("dossier_count"),
            "equation_candidates_added_by_recovery": recovery.get("added_count"),
        },
        "structures": {
            kind: {"count": len(structs.get(kind) or []), "by_status": _counts(structs.get(kind) or [], "status")}
            for kind in ("equations", "tables", "figures", "definitions")
        },
        "selected_targets": {
            "count": len(selected_ids) or len(targets),
            "readiness_status": ready.get("status"),
            "ready_count": sum(1 for t in targets if t.get("status") == "READY"),
            "by_status": _counts(targets, "status"),
            "targets": [{"label": t.get("label"), "kind": t.get("kind"), "status": t.get("status")} for t in targets],
        },
        "manual_review": {
            "required": ready.get("status") != "READY" or audit.get("status") != "PASS",
            "reasons": [r for r, c in (("selected-target readiness not READY", ready.get("status") != "READY"),
                                        ("source-identity audit not PASS", audit.get("status") != "PASS")) if c],
            "target_review_in_study_manifest": "target_review" in manifest,
            "note": "Manual page-image review, where performed, is recorded in the study manifest, not here.",
        },
    }
    return summary


def pending_summary(paper_id: str, status: str, note: str, documented_in: list[str] | None = None,
                    root: Path | None = None, today: str | None = None, ingestion_route: str = "NOT_RECORDED",
                    identity: dict[str, Any] | None = None, documented_outcomes: dict[str, Any] | None = None,
                    manual_review: dict[str, Any] | None = None) -> dict[str, Any]:
    """Explicit record for a study whose intake is not available to summarise.

    ``documented_outcomes`` may carry only outcomes already written in tracked project records
    (each with its reference); nothing is reconstructed or estimated.
    """
    if status not in {"PENDING_LOCAL_SUMMARY", "NO_INGESTION_RECORD"}:
        raise ValueError("status must be PENDING_LOCAL_SUMMARY or NO_INGESTION_RECORD")
    if ingestion_route not in ROUTES:
        raise ValueError(f"ingestion_route must be one of {sorted(ROUTES)}")
    pid = paper_id.upper()
    manifest = _load(_root(root) / "engiproof" / "studies" / pid / "study.json") or {}
    src = manifest.get("source") or {}
    return {"schema_version": SCHEMA, "paper_id": pid, "recorded_on": today or date.today().isoformat(),
            "ingestion_status": status, "ingestion_route": ingestion_route, "note": note,
            "manifest_ingestion_record": manifest.get("ingestion_record"),
            "source": {"sha256_in_study_manifest": src.get("sha256"), "doi": src.get("doi"),
                       "format": {"source_format": "NOT_RECORDED", "basis": None}},
            "identity": identity or {"status": "NOT_RECORDED"},
            "documented_outcomes": documented_outcomes or {},
            "manual_review": manual_review or {"required": "NOT_RECORDED"},
            "documented_in": documented_in or [],
            "not_backfilled": "Candidate counts, readiness and audit outcomes are not reconstructed or estimated; only outcomes already written in tracked records are listed, with their reference.",
            "rule": RULE}


def write_ingestion_summary(summary: dict[str, Any], root: Path | None = None) -> str:
    if summary.get("ingestion_status") == "NO_LOCAL_INTAKE":
        raise FileNotFoundError(summary["note"])
    path = summary_path(summary["paper_id"], root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(path.relative_to(_root(root))).replace("\\", "/")


def ingestion_summary_audit(paper_ids: list[str] | None = None, root: Path | None = None) -> dict[str, Any]:
    root = _root(root)
    ids = [p.upper() for p in (paper_ids or ["P40", "P41", "P42", "P43", "P44", "P45"])]
    rows, issues = [], []
    for pid in ids:
        s = _load(summary_path(pid, root))
        if s is None:
            issues.append(f"{pid}: no ingestion_summary.json")
            rows.append({"paper_id": pid, "ingestion_status": "MISSING"})
            continue
        if s.get("schema_version") != SCHEMA or s.get("ingestion_status") not in STATUSES:
            issues.append(f"{pid}: invalid schema or status")
        row = {"paper_id": pid, "ingestion_status": s.get("ingestion_status"), "ingestion_route": s.get("ingestion_route")}
        if s.get("ingestion_route") not in ROUTES:
            issues.append(f"{pid}: ingestion_route missing or unknown")
        if s.get("ingestion_status") == "SUMMARISED_FROM_LOCAL_INTAKE":
            row.update(identity_audit=(s.get("identity_audit") or {}).get("status"),
                       readiness=(s.get("selected_targets") or {}).get("readiness_status"),
                       ready=f"{(s.get('selected_targets') or {}).get('ready_count')}/{(s.get('selected_targets') or {}).get('count')}",
                       source_format=((s.get("source") or {}).get("format") or {}).get("source_format"),
                       sha_matches_manifest=(s.get("source") or {}).get("matches_study_manifest_sha256"))
            if row["sha_matches_manifest"] is False:
                issues.append(f"{pid}: summarised intake fingerprint differs from the study manifest source sha256")
        rows.append(row)
    return {"schema_version": "engiproof.ingestion_summary_audit/1.0", "status": "PASS" if not issues else "FAIL",
            "summarised": sum(r["ingestion_status"] == "SUMMARISED_FROM_LOCAL_INTAKE" for r in rows),
            "studies": rows, "issues": issues, "rule": RULE}
