import json, tempfile, unittest
from pathlib import Path

from engiproof.ingestion import (
    ingest_source, enrich_source, extract_structures, load_structure_candidates,
    scaffold_from_intake, selected_target_readiness
)

ASME_SAMPLE = """Global Buckling of Pipe-in-Pipe
Table 1 Pipeline data
Pipe Inner Outer
D [mm] 298.5 394.0
t [mm] 14.25 20.5
E [N/m2] 1.99E+11 2.07E+11
SMYS [N/m2] 550 360
Table 2 Axial stiffness and distribution of forces
Pipe Inner Outer
AS [m2] 0.012725 0.024054
EAS [N] 2.532E+9 4.979E+9
fS [N/m] 471
SDelta [N/m] 153 312
Table 3 Cases analysed
Case fI [N/m] EndExpansion
1 0 1.355
2 87.5 1.311
3 175 1.305
Figure 4 - Case 1 - No axial friction between pipes
Equation (6)
DeltaS_inner = fS * EAS_inner / (EAS_inner + EAS_outer) (6)
"""

class PublisherStyleIngestionTests(unittest.TestCase):
    def _root(self, td):
        root=Path(td)
        (root/"engiproof").mkdir()
        (root/"papers").mkdir()
        (root/"engiproof/registry.json").write_text(json.dumps({
            "schema_version":"engiproof.registry/1.0","framework":"EngiProof",
            "version":"0.2.0.dev6","studies":[]
        }),encoding="utf-8")
        return root

    def test_punctuationless_table_caption_is_anchor(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/"paper.txt"; src.write_text(ASME_SAMPLE,encoding="utf-8")
            ingest_source(src,"PX1",title="ASME sample",root=root)
            enrich_source("PX1",src,root=root)
            extract_structures("PX1",src,root=root)
            s=load_structure_candidates("PX1",root=root)
            t1=next(x for x in s["tables"] if x["label"]=="Table 1")
            anchor=next(o for o in t1["occurrences"] if o["caption_candidate"].startswith("Table 1 Pipeline"))
            self.assertTrue(anchor["caption_anchor"])
            self.assertGreaterEqual(anchor["table_block_candidate"]["data_row_count"],4)

    def test_next_punctuationless_table_stops_previous_block(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/"paper.txt"; src.write_text(ASME_SAMPLE,encoding="utf-8")
            ingest_source(src,"PX2",title="ASME sample",root=root)
            enrich_source("PX2",src,root=root)
            extract_structures("PX2",src,root=root)
            s=load_structure_candidates("PX2",root=root)
            t2=next(x for x in s["tables"] if x["label"]=="Table 2")
            anchor=next(o for o in t2["occurrences"] if o["caption_candidate"].startswith("Table 2 Axial"))
            block=anchor["table_block_candidate"]
            self.assertTrue(anchor["caption_anchor"])
            self.assertFalse(any("Table 3" in x for x in block["header_lines"]+block["data_rows"]+block["footnotes"]))

    def test_hyphenated_figure_caption_is_anchor(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/"paper.txt"; src.write_text(ASME_SAMPLE,encoding="utf-8")
            ingest_source(src,"PX3",title="ASME sample",root=root)
            enrich_source("PX3",src,root=root)
            extract_structures("PX3",src,root=root)
            s=load_structure_candidates("PX3",root=root)
            f4=next(x for x in s["figures"] if x["label"]=="Figure 4")
            self.assertTrue(any(o["caption_anchor"] for o in f4["occurrences"]))

    def test_selected_asme_tables_become_ready(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/"paper.txt"; src.write_text(ASME_SAMPLE,encoding="utf-8")
            ingest_source(src,"PX4",title="ASME sample",root=root)
            enrich_source("PX4",src,root=root)
            # Discover order may vary; select by IDs corresponding to labels in the intake.
            intake=json.loads((root/"engiproof/intake/PX4/target_candidates.json").read_text())
            ids={c["label"]:c["candidate_id"] for c in intake["candidates"]}
            scaffold_from_intake("PX4",target_ids=[ids["Table 1"],ids["Table 2"]],root=root)
            extract_structures("PX4",src,root=root)
            ready=selected_target_readiness("PX4",root=root)
            self.assertEqual(ready["status"],"READY")
            self.assertTrue(all(t["status"]=="READY" for t in ready["targets"]))

if __name__=="__main__":
    unittest.main()
