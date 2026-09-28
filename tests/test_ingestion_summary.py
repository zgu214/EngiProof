import json
import tempfile
import unittest
from pathlib import Path

from engiproof.core import project_root
from engiproof.ingestion_summary import (STATUSES, build_ingestion_summary, detect_source_format,
                                         ingestion_summary_audit, pending_summary, write_ingestion_summary)

ROOT = project_root()
SECRET = "SOURCE_EXCERPT_MUST_NOT_LEAK"
SHA = "a" * 64

try:
    import PIL  # noqa: F401
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False


def _synthetic_intake(root: Path, sha: str = SHA) -> None:
    intake = root / "engiproof/intake/PX"
    intake.mkdir(parents=True)
    study = root / "engiproof/studies/PX"
    study.mkdir(parents=True)
    (study / "study.json").write_text(json.dumps({"paper_id": "PX", "source": {"canonical_pdf": "px.pdf", "sha256": SHA, "doi": "10.0/x"}}))
    files = {
        "ingestion.json": {"paper_id": "PX", "status": "DRAFT_SCAFFOLDED", "raw_source_copied": False, "selected_candidate_ids": ["T001", "T002"], "title": SECRET},
        "source_fingerprint.json": {"sha256": sha, "size_bytes": 10, "page_count": 2, "text_extractable": True, "pdf_title": SECRET},
        "source_identity_audit.json": {"status": "PASS", "checks": {"title": "MATCH", "doi": "MATCH", "year": "MATCH"}, "issues": [], "source_candidates": {"year_evidence": [SECRET]}},
        "target_candidates.json": {"candidates": [{"kind": "table", "label": "Table 1", "excerpt": SECRET}, {"kind": "equation", "label": "Equation (1)", "excerpt": SECRET}]},
        "target_dossiers.json": {"dossier_count": 2, "located_count": 2, "dossiers": [{"occurrences": [{"excerpt": SECRET}]}]},
        "equation_recovery.json": {"added_count": 1, "added_candidates": [{"text": SECRET}]},
        "structure_candidates.json": {"equations": [{"status": "STRUCTURE_CANDIDATE", "blocks": [SECRET]}], "tables": [], "figures": [],
                                      "definitions": [{"symbol": "D", "definition": SECRET, "locator": "p1:l2", "status": "CANDIDATE"}]},
        "selected_target_readiness.json": {"status": "PARTIAL", "targets": [{"label": "Table 1", "kind": "table", "status": "READY", "reason": SECRET},
                                                                           {"label": "Equation (1)", "kind": "equation", "status": "BLOCKED", "reason": SECRET}]},
    }
    for name, data in files.items():
        (intake / name).write_text(json.dumps(data))


class IngestionSummaryTests(unittest.TestCase):
    def test_summary_is_text_free_and_counts_are_right(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _synthetic_intake(root)
            s = build_ingestion_summary("PX", root=root, today="2026-09-27")
            blob = json.dumps(s)
            self.assertNotIn(SECRET, blob)
            self.assertNotIn("p1:l2", blob)
            self.assertEqual(s["ingestion_status"], "SUMMARISED_FROM_LOCAL_INTAKE")
            self.assertTrue(s["source"]["matches_study_manifest_sha256"])
            self.assertEqual(s["candidates"]["by_kind"], {"equation": 1, "table": 1})
            self.assertEqual(s["selected_targets"]["ready_count"], 1)
            self.assertEqual(s["selected_targets"]["count"], 2)
            self.assertEqual(s["structures"]["definitions"]["count"], 1)
            self.assertEqual(s["source"]["format"]["source_format"], "NOT_RECORDED")
            self.assertEqual(write_ingestion_summary(s, root=root), "engiproof/studies/PX/ingestion_summary.json")

    def test_fingerprint_mismatch_fails_audit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _synthetic_intake(root, sha="b" * 64)
            write_ingestion_summary(build_ingestion_summary("PX", root=root), root=root)
            audit = ingestion_summary_audit(["PX"], root=root)
            self.assertEqual(audit["status"], "FAIL")

    def test_missing_intake_is_stated_not_backfilled(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            s = build_ingestion_summary("PY", root=root)
            self.assertEqual(s["ingestion_status"], "NO_LOCAL_INTAKE")
            with self.assertRaises(FileNotFoundError):
                write_ingestion_summary(s, root=root)
            with self.assertRaises(ValueError):
                pending_summary("PY", "SUMMARISED_FROM_LOCAL_INTAKE", "not allowed", root=root)

    def test_manual_source_format_is_validated(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _synthetic_intake(root)
            s = build_ingestion_summary("PX", root=root, source_format="BORN_DIGITAL", source_format_basis="publisher PDF inspected")
            self.assertEqual(s["source"]["format"]["basis"], "publisher PDF inspected")
            with self.assertRaises(ValueError):
                build_ingestion_summary("PX", root=root, source_format="PHOTOCOPY")

    @unittest.skipUnless(HAVE_PIL, "Pillow not installed")
    def test_format_detection(self):
        from PIL import Image
        from pypdf import PdfWriter
        with tempfile.TemporaryDirectory() as td:
            scan = Path(td) / "scan.pdf"
            Image.new("1", (2550, 3300), 1).save(scan, resolution=300)
            d = detect_source_format(scan)
            self.assertEqual(d["source_format"], "SCANNED_IMAGE_ONLY")
            self.assertEqual(d["raster_dpi_median"], 300)
            blank = Path(td) / "digital.pdf"
            w = PdfWriter()
            w.add_blank_page(612, 792)
            w.write(blank)
            self.assertEqual(detect_source_format(blank)["source_format"], "BORN_DIGITAL")


class RepositoryIngestionSummaryTests(unittest.TestCase):
    def test_every_paper_a_study_has_an_explicit_record(self):
        audit = ingestion_summary_audit(root=ROOT)
        self.assertEqual(audit["status"], "PASS", audit["issues"])
        for row in audit["studies"]:
            self.assertIn(row["ingestion_status"], STATUSES)

    def test_p45_summary_matches_manifest_source(self):
        s = json.loads((ROOT / "engiproof/studies/P45/ingestion_summary.json").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "engiproof/studies/P45/study.json").read_text(encoding="utf-8"))
        self.assertEqual(s["source"]["sha256"], manifest["source"]["sha256"])
        self.assertEqual(s["source"]["format"]["source_format"], "SCANNED_WITH_TEXT_LAYER")
        self.assertEqual(s["selected_targets"]["readiness_status"], "PARTIAL")


if __name__ == "__main__":
    unittest.main()
