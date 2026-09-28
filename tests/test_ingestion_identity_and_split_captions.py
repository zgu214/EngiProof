import json, tempfile, unittest
from pathlib import Path

from engiproof.ingestion import (
    ingest_source, audit_source_identity, enrich_source, extract_structures,
    load_structure_candidates
)

IDENTITY_SAMPLE = """Tension-bending analysis of flexible pipe by a repeated unit cell finite element model
https://doi.org/10.1016/j.marstruc.2018.09.010
Received 20 March 2018; Received in revised form 16 July 2018; Accepted 24 September 2018
Marine Structures 64 (2019) 401-420
0951-8339/ © 2018 Elsevier Ltd. All rights reserved.
"""

SPLIT_CAPTION_SAMPLE = """Flexible pipe study
Table 1
Geometric parameters of the flexible pipe cross section.
Layer Number Geometric Parameters Symbol Value
Core 0 Thickness t0 12.0 mm
Tensile armor 1 Wire thickness t1 5.0 mm
Tensile armor 2 Wire thickness t2 5.0 mm
Table 3
Material properties used to model the core, the tensile armor and the outer sheath.
Material parameter Core Tensile armor Outer sheath
E [MPa] 210000 210000 400
nu [-] 0.3 0.3 0.4
Table 4
Contact interaction properties used in FP-RUC.
Contact option Contact interaction parameters Settings
mu [-] 0.12
slip [mm] 0.005
Figure 16
Cross-section moment as a function of curvature for various tension levels.
"""

class IdentityAndSplitCaptionTests(unittest.TestCase):
    def _root(self, td):
        root=Path(td)
        (root/"engiproof").mkdir()
        (root/"papers").mkdir()
        (root/"engiproof/registry.json").write_text(json.dumps({
            "schema_version":"engiproof.registry/1.0",
            "framework":"EngiProof","version":"0.2.0.dev7","studies":[]
        }),encoding="utf-8")
        return root

    def test_publication_year_beats_received_accepted_and_copyright_year(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/"paper.txt"; src.write_text(IDENTITY_SAMPLE,encoding="utf-8")
            ingest_source(src,"PY1",
                title="Tension-bending analysis of flexible pipe by a repeated unit cell finite element model",
                doi="10.1016/j.marstruc.2018.09.010",year=2019,root=root)
            a=audit_source_identity("PY1",src,root=root)
            self.assertEqual(a["status"],"PASS")
            self.assertEqual(a["checks"]["year"],"MATCH")
            self.assertEqual(a["source_candidates"]["year"],[2019])
            self.assertIn(2018,a["source_candidates"]["secondary_years"])

    def test_different_true_publication_year_is_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/"paper.txt"; src.write_text(IDENTITY_SAMPLE,encoding="utf-8")
            ingest_source(src,"PY2",
                title="Tension-bending analysis of flexible pipe by a repeated unit cell finite element model",
                doi="10.1016/j.marstruc.2018.09.010",year=2020,root=root)
            a=audit_source_identity("PY2",src,root=root)
            self.assertEqual(a["status"],"CONFLICT")
            self.assertEqual(a["source_candidates"]["year"],[2019])

    def test_received_year_alone_does_not_create_false_conflict(self):
        sample="Paper title\n10.1234/example\nReceived 20 March 2018; Accepted 24 September 2018\n"
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/"paper.txt"; src.write_text(sample,encoding="utf-8")
            ingest_source(src,"PY3",title="Paper title",doi="10.1234/example",year=2019,root=root)
            a=audit_source_identity("PY3",src,root=root)
            self.assertNotEqual(a["status"],"CONFLICT")
            self.assertEqual(a["checks"]["year"],"NOT_CONFIRMED")

    def test_split_table_caption_is_anchor_and_has_rows(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/"paper.txt"; src.write_text(SPLIT_CAPTION_SAMPLE,encoding="utf-8")
            ingest_source(src,"PS1",title="Flexible pipe study",max_candidates=100,root=root)
            enrich_source("PS1",src,root=root)
            extract_structures("PS1",src,root=root)
            s=load_structure_candidates("PS1",root=root)
            for label in ("Table 1","Table 3","Table 4"):
                table=next(x for x in s["tables"] if x["label"]==label)
                anchor=next(o for o in table["occurrences"] if o["caption_anchor"])
                self.assertIn("—",anchor["caption_candidate"])
                self.assertGreater(anchor["table_block_candidate"]["data_row_count"],0)

    def test_split_figure_caption_is_anchor(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/"paper.txt"; src.write_text(SPLIT_CAPTION_SAMPLE,encoding="utf-8")
            ingest_source(src,"PS2",title="Flexible pipe study",max_candidates=100,root=root)
            enrich_source("PS2",src,root=root)
            extract_structures("PS2",src,root=root)
            s=load_structure_candidates("PS2",root=root)
            f=next(x for x in s["figures"] if x["label"]=="Figure 16")
            self.assertTrue(any(o["caption_anchor"] for o in f["occurrences"]))

if __name__=="__main__":
    unittest.main()
