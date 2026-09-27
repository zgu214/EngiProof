import json
import tempfile
import unittest
from pathlib import Path

from engiproof.environment_record import compact_line
from engiproof.isolation import ENVIRONMENT_KEYS, declared_environment, runtime_environment


class EnvironmentRecordTests(unittest.TestCase):
    def test_runtime_environment_fields(self):
        env = runtime_environment()
        for k in ("python_version", "numpy_version", "os", "machine"):
            self.assertTrue(env.get(k), k)

    def test_environment_keys_are_not_broadened(self):
        # The OS is recorded in verification output, not accepted as a non-material
        # difference inside frozen evidence (review decision, PR #3).
        self.assertEqual(ENVIRONMENT_KEYS, frozenset({"python", "numpy", "python_version", "numpy_version"}))

    def test_declared_environment_found_at_any_depth(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.json").write_text(json.dumps({"meta": {"python": "3.12.1", "numpy": "2.0"}, "x": 1}))
            (root / "b.json").write_text(json.dumps({"x": [1, 2]}))
            (root / "c.csv").write_text("python,1\n")
            out = declared_environment([root / "a.json", root / "b.json", root / "c.csv"], root)
            self.assertEqual(out, {"a.json": {"python": "3.12.1", "numpy": "2.0"}})

    def test_compact_line_reports_only_non_identical(self):
        rec = {"status": "PASS", "environment": {"python_version": "3.13.0", "numpy_version": "2.3.0", "os": "Windows", "machine": "AMD64"},
               "study_count": 2, "classification_totals": {"IDENTICAL": 3, "BYTE_ONLY": 1},
               "studies": [{"paper_id": "PA", "classification_counts": {"IDENTICAL": 2, "BYTE_ONLY": 0}},
                           {"paper_id": "PB", "classification_counts": {"IDENTICAL": 1, "BYTE_ONLY": 1}}]}
        line = json.loads(compact_line(rec))
        self.assertEqual(line["nonidentical"], {"PB": {"BYTE_ONLY": 1}})
        self.assertEqual(line["os"], "Windows")


if __name__ == "__main__":
    unittest.main()
