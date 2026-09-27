"""Verification must not mutate the evidence being verified.

These tests hash every tracked file before and after verification (and after the
complete unit-test suite) and require byte-for-byte equality. They also pin the
frozen-evidence comparator rules.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from engiproof.core import run_study, verify_all, verify_study
from engiproof.isolation import build_hash_index, compare_artifact, tracked_file_hashes

INNER = "ENGIPROOF_NON_MUTATION_INNER_SUITE"
ALL_STUDIES = sorted(p.name for p in (ROOT / "engiproof" / "studies").iterdir() if (p / "study.json").is_file())


def _changed(before, after):
    return sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))


@unittest.skipIf(os.environ.get(INNER), "inner suite run of the non-mutation check")
class NonMutationTests(unittest.TestCase):
    def test_verify_all_does_not_mutate_and_reproduces_frozen_evidence(self):
        before = tracked_file_hashes(ROOT)
        result = verify_all()
        self.assertEqual(_changed(before, tracked_file_hashes(ROOT)), [])
        self.assertEqual(result["status"], "PASS")
        for study in result["studies"]:
            rep = study["reproduction"]
            self.assertEqual((study["paper_id"], rep["status"], rep["material_artifacts"]), (study["paper_id"], "PASS", 0))

    def test_verify_and_run_every_study_does_not_mutate_tracked_files(self):
        # Includes studies outside the live registry and studies whose verification
        # currently fails: a failing verification must not mutate evidence either.
        before = tracked_file_hashes(ROOT)
        for pid in ALL_STUDIES:
            verify_study(pid)
            run_study(pid)
        self.assertEqual(_changed(before, tracked_file_hashes(ROOT)), [])

    def test_complete_unit_test_suite_does_not_mutate_tracked_files(self):
        before = tracked_file_hashes(ROOT)
        env = {**os.environ, INNER: "1", "PYTHONPATH": str(ROOT / "src")}
        proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                              cwd=ROOT, env=env, capture_output=True, text=True)
        changed = _changed(before, tracked_file_hashes(ROOT))
        self.assertEqual(changed, [], f"unit-test suite mutated tracked files: {changed}")
        self.assertIn("OK", proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "", proc.stderr[-3000:])


class FrozenComparatorTests(unittest.TestCase):
    def _pair(self, name, frozen: bytes, regenerated: bytes):
        td = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, td, True)
        (td / "f").mkdir(); (td / "r").mkdir()
        a, b = td / "f" / name, td / "r" / name
        a.write_bytes(frozen); b.write_bytes(regenerated)
        return a, b

    def test_identical_bytes(self):
        a, b = self._pair("x.csv", b"a\n1\n", b"a\n1\n")
        self.assertEqual(compare_artifact(a, b)["classification"], "IDENTICAL")

    def test_line_endings_only_is_byte_only(self):
        a, b = self._pair("x.csv", b"a,b\n1,2.5\n", b"a,b\r\n1,2.5\r\n")
        r = compare_artifact(a, b)
        self.assertEqual((r["classification"], r["material"]), ("BYTE_ONLY", False))

    def test_serialisation_only_is_byte_only(self):
        a, b = self._pair("x.json", b'{"v": 1.5, "s": "x"}', b'{\n  "v": 1.50,\n  "s": "x"\n}')
        self.assertEqual(compare_artifact(a, b)["classification"], "BYTE_ONLY")

    def test_float_noise_is_numerical_nonmaterial(self):
        a, b = self._pair("x.json", b'{"v": 406.4}', b'{"v": 406.40000000000003}')
        r = compare_artifact(a, b)
        self.assertEqual((r["classification"], r["material"], r["numbers_changed"]), ("NUMERICAL_NONMATERIAL", False, 1))

    def test_change_beyond_tolerance_is_numerical_material(self):
        a, b = self._pair("x.csv", b"q,v\nA,0.66\n", b"q,v\nA,0.7056\n")
        r = compare_artifact(a, b)
        self.assertEqual((r["classification"], r["material"]), ("NUMERICAL_MATERIAL", True))
        self.assertEqual(r["material_findings"][0]["rule"], "declared tolerance")

    def test_declared_tolerance_is_applied(self):
        a, b = self._pair("x.csv", b"lam\n3.14159265\n", b"lam\n3.14159268\n")
        self.assertEqual(compare_artifact(a, b)["classification"], "NUMERICAL_MATERIAL")
        self.assertEqual(compare_artifact(a, b, {"rel": 1e-6, "abs": 1e-5})["classification"], "NUMERICAL_NONMATERIAL")

    def test_rounding_guard_overrides_tolerance(self):
        # Within rel 1e-6 / abs 1e-5, but the 3-decimal rounded value changes: material.
        a, b = self._pair("t.csv", b"independent_FE_lambda\n3.1424999\n", b"independent_FE_lambda\n3.1425001\n")
        guard = [{"field": "independent_FE_lambda", "decimals": 3}]
        r = compare_artifact(a, b, {"rel": 1e-6, "abs": 1e-5}, rounding_guards=guard)
        self.assertEqual(r["classification"], "NUMERICAL_MATERIAL")
        self.assertIn("rounding guard", r["material_findings"][0]["rule"])
        a2, b2 = self._pair("t.csv", b"independent_FE_lambda\n3.1421000\n", b"independent_FE_lambda\n3.1421002\n")
        self.assertEqual(compare_artifact(a2, b2, {"rel": 1e-6, "abs": 1e-5}, rounding_guards=guard)["classification"], "NUMERICAL_NONMATERIAL")

    def test_status_change_is_material_non_numeric(self):
        a, b = self._pair("x.json", b'{"status": "CONDITIONAL", "qualification": "NOT_GRANTED"}',
                          b'{"status": "COMPARED", "qualification": "NOT_GRANTED"}')
        r = compare_artifact(a, b)
        self.assertEqual((r["classification"], r["material"]), ("MATERIAL_NON_NUMERIC", True))

    def test_structure_change_is_material_non_numeric(self):
        a, b = self._pair("x.json", b'{"a": 1}', b'{"a": 1, "b": 2}')
        self.assertEqual(compare_artifact(a, b)["classification"], "MATERIAL_NON_NUMERIC")

    def test_line_ending_provenance_hash_is_environment_metadata(self):
        td = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, td, True)
        src = td / "input.csv"; src.write_bytes(b"x\n1\n")
        lf, crlf = hashlib.sha256(b"x\n1\n").hexdigest(), hashlib.sha256(b"x\r\n1\r\n").hexdigest()
        a, b = self._pair("m.json", json.dumps({"input_sha256": crlf}).encode(), json.dumps({"input_sha256": lf}).encode())
        r = compare_artifact(a, b, hash_index=build_hash_index([src]))
        self.assertEqual(r["classification"], "ENVIRONMENT_METADATA")
        self.assertEqual(len(r["provenance_hash_line_endings"]), 1)
        # An unexplained hash change is material.
        a2, b2 = self._pair("m.json", json.dumps({"input_sha256": crlf}).encode(), json.dumps({"input_sha256": "0" * 64}).encode())
        self.assertEqual(compare_artifact(a2, b2, hash_index=build_hash_index([src]))["classification"], "MATERIAL_NON_NUMERIC")

    def test_environment_fields_are_environment_metadata(self):
        a, b = self._pair("m.json", b'{"python": "3.13.5", "numpy": "2.3.5", "v": 1.0}',
                          b'{"python": "3.11.15", "numpy": "2.4.4", "v": 1.0}')
        r = compare_artifact(a, b)
        self.assertEqual((r["classification"], len(r["environment_fields"])), ("ENVIRONMENT_METADATA", 2))


class P43ToleranceContractTests(unittest.TestCase):
    def test_p43_declares_recomputation_tolerance_not_acceptance(self):
        tol = json.loads((ROOT / "engiproof/studies/P43/study.json").read_text(encoding="utf-8"))["verification_tolerance"]
        self.assertEqual((tol["rel"], tol["abs"]), (1e-6, 1e-5))
        self.assertEqual(tol["purpose"], "cross-platform recomputation equivalence")
        self.assertIn("NOT an engineering acceptance or validation tolerance", tol["statement"])
        fields = {g["field"]: g["decimals"] for g in tol["rounding_guards"]}
        self.assertEqual(fields, {"independent_FE_lambda": 3, "published_lambda": 3})

    def test_p43_recomputation_passes_with_guard(self):
        rep = verify_study("P43")["reproduction"]
        self.assertEqual(rep["status"], "PASS", rep.get("artifacts"))
        self.assertEqual(rep["material_artifacts"], 0)
        self.assertGreater(sum(a.get("rounding_guarded_values", 0) for a in rep["artifacts"]), 0)


class CanonicalProvenanceTests(unittest.TestCase):
    def test_canonical_identity_is_checkout_independent(self):
        from engiproof.provenance_identity import canonical_text_sha256, file_identity
        td = Path(tempfile.mkdtemp()); self.addCleanup(shutil.rmtree, td, True)
        lf, crlf = td / "lf.csv", td / "crlf.csv"
        lf.write_bytes(b"a,b\n1,2\n"); crlf.write_bytes(b"a,b\r\n1,2\r\n")
        self.assertNotEqual(file_identity(lf)["sha256"], file_identity(crlf)["sha256"])
        self.assertEqual(canonical_text_sha256(lf), canonical_text_sha256(crlf))
        self.assertEqual(file_identity(crlf)["canonicalization"], "text/lf-v1")

    def test_historical_byte_hashes_are_preserved(self):
        # Frozen P29 hashes were taken over CRLF checkout bytes; they stay as recorded.
        v = json.loads((ROOT / "papers/P29/results/engiproof_verification.json").read_text(encoding="utf-8"))
        from engiproof.provenance_identity import byte_variants
        self.assertEqual(v["inherited_surface_sha256"], byte_variants(ROOT / "papers/P29/results/figure16_surface.csv")["CRLF"])


class RegenerationBoundaryTests(unittest.TestCase):
    def test_regeneration_is_not_exposed_through_mcp_even_with_run_opt_in(self):
        try:
            from mcp.shared.memory import create_connected_server_and_client_session
        except ImportError:
            self.skipTest("optional 'mcp' dependency not installed")
        import asyncio, importlib
        os.environ["ENGIPROOF_MCP_ALLOW_RUN"] = "1"
        try:
            import engiproof.mcp_server as mod
            mod = importlib.reload(mod)
        finally:
            os.environ.pop("ENGIPROOF_MCP_ALLOW_RUN", None)

        async def names():
            async with create_connected_server_and_client_session(mod.mcp._mcp_server) as s:
                return {t.name for t in (await s.list_tools()).tools}

        tools = asyncio.run(names())
        self.assertIn("verify_study", tools)
        self.assertFalse([t for t in tools if "regenerat" in t or "write" in t], tools)


if __name__ == "__main__":
    unittest.main()
