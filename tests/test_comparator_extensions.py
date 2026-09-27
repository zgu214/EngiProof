"""Path-scoped recomputation tolerances and provenance-hash inheritance (G4 cross-OS findings)."""
import hashlib
import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from engiproof.isolation import compare_artifact, reproduce_against_frozen, sandbox

RUNNER = textwrap.dedent('''
    import hashlib, json, pathlib
    VALUE = {value!r}
    d = pathlib.Path(__file__).parent / "results"
    d.mkdir(exist_ok=True)
    (d / "a.csv").write_text("x,y\\n1,%r\\n" % VALUE, encoding="utf-8", newline="\\n")
    h = hashlib.sha256((d / "a.csv").read_bytes()).hexdigest()
    (d / "manifest.json").write_text(json.dumps({{"result_sha256": {{"results/a.csv": h}}, "other": {other!r}}}), encoding="utf-8")
''')


def _project(td: str, frozen_value: float, new_value: float, frozen_other: str = "x", new_other: str = "x") -> tuple[Path, dict]:
    root = Path(td)
    study = root / "papers" / "PX"
    study.mkdir(parents=True)
    (study / "run.py").write_text(RUNNER.format(value=frozen_value, other=frozen_other), encoding="utf-8")
    import subprocess, sys
    subprocess.run([sys.executable, str(study / "run.py")], check=True)
    (study / "run.py").write_text(RUNNER.format(value=new_value, other=new_other), encoding="utf-8")
    manifest = {"paper_id": "PX", "runner": "papers/PX/run.py",
                "result_files": ["papers/PX/results/a.csv", "papers/PX/results/manifest.json"]}
    return root, manifest


def _run(root, manifest):
    with sandbox(root) as box:
        return reproduce_against_frozen(root, manifest, box)


class ProvenanceHashInheritanceTests(unittest.TestCase):
    def _by_path(self, rep):
        return {Path(a["path"]).name: a for a in rep["artifacts"]}

    def test_hash_of_nonmaterially_changed_artifact_is_nonmaterial(self):
        with tempfile.TemporaryDirectory() as td:
            rep = _run(*_project(td, 1.0, 1.0 + 1e-13))
            arts = self._by_path(rep)
            self.assertEqual(rep["status"], "PASS", arts)
            self.assertEqual(arts["a.csv"]["classification"], "NUMERICAL_NONMATERIAL")
            self.assertEqual(arts["manifest.json"]["classification"], "NUMERICAL_NONMATERIAL")
            self.assertEqual(arts["manifest.json"]["derived_hash_refs"], ["papers/PX/results/a.csv"])

    def test_hash_of_materially_changed_artifact_is_material(self):
        with tempfile.TemporaryDirectory() as td:
            rep = _run(*_project(td, 1.0, 1.5))
            arts = self._by_path(rep)
            self.assertEqual(rep["status"], "FAIL")
            self.assertEqual(arts["manifest.json"]["classification"], "NUMERICAL_MATERIAL")

    def test_other_text_change_stays_material(self):
        with tempfile.TemporaryDirectory() as td:
            rep = _run(*_project(td, 1.0, 1.0 + 1e-13, "x", "y"))
            self.assertEqual(self._by_path(rep)["manifest.json"]["classification"], "MATERIAL_NON_NUMERIC")

    def test_unrelated_hash_change_stays_material(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "f.json").write_text(json.dumps({"h": "a" * 64}))
            (root / "g.json").write_text(json.dumps({"h": "b" * 64}))
            self.assertEqual(compare_artifact(root / "f.json", root / "g.json", provenance_index={})["classification"], "MATERIAL_NON_NUMERIC")


class PathScopedToleranceTests(unittest.TestCase):
    def _files(self, td, a, b):
        root = Path(td)
        (root / "f.json").write_text(json.dumps(a))
        (root / "g.json").write_text(json.dumps(b))
        return root / "f.json", root / "g.json"

    TOL = {"rel": 1e-9, "abs": 1e-12, "path_tolerances": [{"path_prefix": ".fe", "rel": 1e-6, "abs": 1e-7}]}

    def test_scoped_prefix_uses_declared_tolerance(self):
        with tempfile.TemporaryDirectory() as td:
            f, g = self._files(td, {"fe": {"k": 2.0, "err": 3e-8}}, {"fe": {"k": 2.0 + 1e-8, "err": 3.6e-8}})
            res = compare_artifact(f, g, self.TOL)
            self.assertEqual(res["classification"], "NUMERICAL_NONMATERIAL")
            self.assertEqual(res["path_scoped_tolerance_values"], 2)

    def test_default_tolerance_applies_outside_the_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            f, g = self._files(td, {"other": 2.0}, {"other": 2.0 + 1e-8})
            self.assertEqual(compare_artifact(f, g, self.TOL)["classification"], "NUMERICAL_MATERIAL")

    def test_scoped_tolerance_is_still_finite(self):
        with tempfile.TemporaryDirectory() as td:
            f, g = self._files(td, {"fe": {"k": 2.0}}, {"fe": {"k": 2.001}})
            self.assertEqual(compare_artifact(f, g, self.TOL)["classification"], "NUMERICAL_MATERIAL")


if __name__ == "__main__":
    unittest.main()
