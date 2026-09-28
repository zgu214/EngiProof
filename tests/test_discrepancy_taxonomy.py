import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from engiproof.core import load_contracts, project_root, validate_study_manifest
from engiproof.discrepancy import discrepancy_gate
from engiproof.taxonomy import load_mapping, record_taxonomy_review, taxonomy_audit, taxonomy_markdown

ROOT = project_root()
PAPER_A = {"P40", "P41", "P42", "P43", "P44", "P45"}


def _studies():
    for p in sorted((ROOT / "engiproof" / "studies").iterdir()):
        if (p / "study.json").is_file():
            yield p.name, json.loads((p / "study.json").read_text(encoding="utf-8"))


class TaxonomyContractTests(unittest.TestCase):
    def setUp(self):
        self.tax = load_contracts()["contracts"]["discrepancy_taxonomy"]

    def test_decision_order_covers_every_category_once(self):
        self.assertEqual(self.tax["decision_order"], list(self.tax["categories"]))
        for name, c in self.tax["categories"].items():
            for k in ("definition", "decision_rule", "not_this_when"):
                self.assertTrue(c.get(k), f"{name} missing {k}")

    def test_every_existing_hint_is_registered(self):
        allowed = set(self.tax["categories"]) | set(self.tax["legacy_classification_hints"])
        for pid, m in _studies():
            for d in m.get("discrepancies", []):
                if d.get("classification_hint"):
                    self.assertIn(d["classification_hint"], allowed, d["id"])

    def test_mapping_covers_every_discrepancy_record(self):
        expected = {d["id"] for pid, m in _studies() for d in m.get("discrepancies", [])}
        paper_a = {d["id"] for pid, m in _studies() if pid in PAPER_A for d in m.get("discrepancies", [])}
        mapped = {r["discrepancy_id"] for r in load_mapping()["records"]}
        self.assertEqual(len(paper_a), 14)
        self.assertEqual(mapped, expected)

    def test_repository_audit_passes_and_every_label_is_reviewer_approved(self):
        # Owner approved the proposed mapping as documented (PR #8 review, 2026-09-28).
        audit = taxonomy_audit()
        self.assertEqual(audit["status"], "PASS", audit["issues"])
        self.assertEqual(audit["review_status_counts"], {"APPROVED": 19})
        for r in audit["records"]:
            self.assertIsNotNone(r["effective"], r["discrepancy_id"])
            self.assertTrue(r["effective"]["reviewer"], r["discrepancy_id"])
            self.assertEqual({"category": r["effective"]["category"], "loci": r["effective"]["loci"]}, r["proposed"], r["discrepancy_id"])


    def test_reviewer_document_is_current(self):
        doc = (ROOT / "docs" / "DISCREPANCY_TAXONOMY.md").read_text(encoding="utf-8").replace("\r\n", "\n")
        self.assertEqual(doc, taxonomy_markdown(), "regenerate with: engiproof discrepancy-taxonomy --markdown")


class TaxonomyValidationTests(unittest.TestCase):
    def _manifest(self, **disc):
        m = json.loads((ROOT / "engiproof/studies/P44/study.json").read_text(encoding="utf-8"))
        m["discrepancies"] = [dict(m["discrepancies"][0], **disc)]
        return m

    def test_free_text_hint_is_rejected(self):
        issues = validate_study_manifest(self._manifest(classification_hint="SOMETHING_NEW"))
        self.assertTrue(any("classification_hint" in i for i in issues), issues)

    def test_taxonomy_category_as_hint_is_accepted(self):
        self.assertEqual(validate_study_manifest(self._manifest(classification_hint="NUMERICAL_VALUE_CONFLICT")), [])

    def test_taxonomy_field_is_validated(self):
        ok = self._manifest(taxonomy={"category": "NUMERICAL_VALUE_CONFLICT", "loci": ["WITHIN_SOURCE"]})
        self.assertEqual(validate_study_manifest(ok), [])
        bad = self._manifest(taxonomy={"category": "TYPO", "loci": []})
        issues = validate_study_manifest(bad)
        self.assertTrue(any("unknown taxonomy category" in i for i in issues), issues)
        self.assertTrue(any("non-empty" in i for i in issues), issues)


class TaxonomyReviewTests(unittest.TestCase):
    def _copy(self, td):
        root = Path(td)
        shutil.copytree(ROOT / "engiproof" / "contracts", root / "engiproof" / "contracts")
        for pid in ("P44", "P45"):
            (root / "engiproof" / "studies" / pid).mkdir(parents=True)
            shutil.copy(ROOT / "engiproof/studies" / pid / "study.json", root / "engiproof/studies" / pid / "study.json")
        return root

    @staticmethod
    def _hash(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def test_approval_is_append_only_and_changes_labels_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._copy(td)
            study = root / "engiproof/studies/P45/study.json"
            before = self._hash(study)
            n_before = {r["discrepancy_id"]: len(r.get("reviews") or []) for r in load_mapping(root)["records"]}
            gate_before = discrepancy_gate("P45", root=root)
            out = record_taxonomy_review("P45", "P45-D004", "APPROVED", "Reviewer", "Notation-only conflict; period stated in text.", root=root, today="2026-09-27")
            self.assertEqual(out["effective"]["category"], "NOTATION_OR_TYPOGRAPHY")
            record_taxonomy_review("P45", "P45-D003", "APPROVED", "Reviewer", "Reviewer prefers the unit reading.", category="UNIT_OR_DIMENSION", loci=["SOURCE_INCOMPLETE"], root=root)
            rec = next(r for r in load_mapping(root)["records"] if r["discrepancy_id"] == "P45-D003")
            self.assertEqual(rec["reviews"][-1]["loci"], ["SOURCE_INCOMPLETE"])
            record_taxonomy_review("P45", "P45-D004", "REJECTED", "Reviewer", "Revisited: reject pending source check.", root=root)
            rec = next(r for r in load_mapping(root)["records"] if r["discrepancy_id"] == "P45-D004")
            self.assertEqual([r["decision"] for r in rec["reviews"]][-2:], ["APPROVED", "REJECTED"])
            audit = taxonomy_audit("P45", root=root)
            self.assertEqual(audit["status"], "PASS", audit["issues"])
            eff = {r["discrepancy_id"]: r["effective"] for r in audit["records"]}
            self.assertIsNone(eff["P45-D004"])
            self.assertEqual(eff["P45-D003"]["loci"], ["SOURCE_INCOMPLETE"])
            self.assertEqual(self._hash(study), before)
            n_after = {r["discrepancy_id"]: len(r.get("reviews") or []) for r in load_mapping(root)["records"]}
            self.assertEqual(n_after["P45-D004"] - n_before["P45-D004"], 2)  # append-only
            self.assertEqual(n_after["P45-D003"] - n_before["P45-D003"], 1)
            gate_after = discrepancy_gate("P45", root=root)
            self.assertEqual(gate_after["blocking_discrepancy_ids"], gate_before["blocking_discrepancy_ids"])

    def test_invalid_review_inputs_raise(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._copy(td)
            with self.assertRaises(ValueError):
                record_taxonomy_review("P45", "P45-D004", "APPROVED", "Reviewer", "Valid note text here.", category="TYPO", root=root)
            with self.assertRaises(ValueError):
                record_taxonomy_review("P45", "P45-D004", "MAYBE", "Reviewer", "Valid note text here.", root=root)
            with self.assertRaises(ValueError):
                record_taxonomy_review("P45", "P45-D004", "APPROVED", "", "Valid note text here.", root=root)
            with self.assertRaises(KeyError):
                record_taxonomy_review("P44", "P45-D004", "APPROVED", "Reviewer", "Valid note text here.", root=root)


if __name__ == "__main__":
    unittest.main()
