import json, zipfile, unittest
from engiproof import __version__
from engiproof.checkpoint import build_checkpoint, continuity_audit
from engiproof.core import project_root

class ContinuityArchitectureTests(unittest.TestCase):
    def test_continuity_audit(self):
        # Durable invariants: they must hold at every checkpoint, so freezing a
        # new study or phase does not require editing this test.
        a=continuity_audit()
        self.assertIn(a["status"],{"PASS","WARN"},a)
        state=a["project_state"]
        self.assertIsNotNone(state,"PROJECT_STATE.json missing or invalid")
        self.assertEqual(state["framework_version"],__version__)
        study=state.get("current_study")
        self.assertRegex(study or "",r"^P\d+$","current_study must be a study id such as P44")
        self.assertTrue((project_root()/"engiproof"/"studies"/study/"study.json").is_file(),
                        f"current_study {study} has no study manifest")
        checkpoint=state.get("current_checkpoint") or ""
        self.assertTrue(checkpoint.startswith(f"{study}_"),
                        f"current_checkpoint {checkpoint!r} does not belong to current_study {study}")
        self.assertEqual(state.get("last_green_status"),"PASS")
        script=state.get("last_green_verification")
        self.assertTrue(script,"last_green_verification not recorded")
        self.assertTrue((project_root()/script).is_file(),
                        f"recorded verification script missing: {script}")

    def test_checkpoint_snapshot(self):
        r=build_checkpoint(bundle=False)
        self.assertEqual(r["status"],"PASS")
        out=project_root()/r["output_dir"]
        for n in ("checkpoint_summary.json","git_state.json","study_index.json","open_discrepancies.json","continuity_audit.json"):
            self.assertTrue((out/n).is_file(),n)

    def test_bundle_excludes_pdfs(self):
        r=build_checkpoint(bundle=True)
        self.assertEqual(r["status"],"PASS")
        with zipfile.ZipFile(project_root()/r["bundle"]) as z:
            names=z.namelist()
        self.assertFalse(any(n.lower().endswith(".pdf") for n in names))
        self.assertIn("PROJECT_STATE.json",names)
        self.assertIn("checkpoint/bundle_manifest.json",names)

    def test_p42_open_items_preserved(self):
        r=build_checkpoint(bundle=False)
        data=json.loads((project_root()/r["output_dir"]/"open_discrepancies.json").read_text(encoding="utf-8"))
        ids={x["id"] for x in data["items"]}
        self.assertIn("P42-D001",ids)
        self.assertIn("P42-D002",ids)

if __name__=="__main__": unittest.main()
