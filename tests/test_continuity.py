import json, zipfile, unittest
from engiproof.checkpoint import build_checkpoint, continuity_audit
from engiproof.core import project_root

class ContinuityArchitectureTests(unittest.TestCase):
    def test_continuity_audit(self):
        a=continuity_audit()
        self.assertIn(a["status"],{"PASS","WARN"},a)
        self.assertEqual(a["project_state"]["framework_version"],"0.2.0.dev8")
        self.assertEqual(a["project_state"]["current_checkpoint"],"P42_PHASE3_FROZEN")

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
