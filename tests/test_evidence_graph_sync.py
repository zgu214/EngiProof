import json, tempfile, unittest
from pathlib import Path
from engiproof.discrepancy import record_discrepancy_decision
from engiproof.evidence_graph import audit_evidence_graph, sync_evidence_graph

class EvidenceGraphSyncTests(unittest.TestCase):
    def _root(self, td):
        root=Path(td); (root/'engiproof/studies/PX').mkdir(parents=True); (root/'papers/PX').mkdir(parents=True)
        manifest={
            'schema_version':'engiproof.study/1.1','paper_id':'PX','title':'Synthetic evidence graph study','evidence_status':'CONDITIONAL','qualification':'NOT_GRANTED',
            'source':{'canonical_pdf':'px.pdf','sha256':'a'*64,'doi':'10.example/px'},'runner':'papers/PX/run.py','source_contract':'papers/PX/SOURCE.md','evidence_graph':'engiproof/studies/PX/evidence_graph.json','result_files':[],'verification_tests':[],
            'tools':[{'name':'published_method','module':'papers/PX/tool.py','function':'f','returns':'x','evidence':'Eq. 1','evidence_class':'PUBLISHED'}],
            'comparisons':[{'id':'PX-C001','target':'method vs table','status':'CONDITIONAL','reference':'Table 1','metrics':{}}],
            'discrepancies':[{'id':'PX-D001','target':'ratio','status':'OPEN','observation':'mismatch','engineering_interpretation':'retain','classification_hint':'PUBLISHED_REFERENCE_MISMATCH','metrics':{'reference_value':1.0,'reproduced_value':1.2,'reference_decimals':2},'automation':{'independent_support':'CORROBORATES_REPRODUCTION'}}],
            'limitations':['synthetic']
        }
        (root/'engiproof/studies/PX/study.json').write_text(json.dumps(manifest),encoding='utf-8')
        graph={'schema_version':'engiproof.evidence_graph/1.0','paper_id':'PX','nodes':[{'id':'MANUAL-SOURCE','kind':'source','label':'Manual source','evidence_class':'PUBLISHED','status':'SOURCE_READY','source_refs':['10.example/px']}],'edges':[],'qualification':'NOT_GRANTED'}
        (root/'engiproof/studies/PX/evidence_graph.json').write_text(json.dumps(graph),encoding='utf-8')
        return root

    def test_sync_adds_manifest_and_decision_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            record_discrepancy_decision('PX','PX-D001','DEFERRED','Awaiting additional provenance before closure.','Reviewer',[],root=root)
            first=sync_evidence_graph('PX',root=root)
            self.assertGreater(first['added_nodes'],0)
            audit=audit_evidence_graph('PX',root=root)
            self.assertEqual(audit['status'],'PASS')
            self.assertEqual(audit['coverage_fraction'],1.0)
            graph=json.loads((root/'engiproof/studies/PX/evidence_graph.json').read_text())
            self.assertTrue(any(n.get('kind')=='discrepancy_decision' and n.get('status')=='DEFERRED' for n in graph['nodes']))
            self.assertEqual(graph['qualification'],'NOT_GRANTED')

    def test_sync_is_idempotent_and_preserves_manual_nodes(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            sync_evidence_graph('PX',root=root)
            graph1=json.loads((root/'engiproof/studies/PX/evidence_graph.json').read_text())
            second=sync_evidence_graph('PX',root=root)
            graph2=json.loads((root/'engiproof/studies/PX/evidence_graph.json').read_text())
            self.assertEqual(second['added_nodes'],0)
            self.assertEqual(second['added_edges'],0)
            self.assertEqual(len(graph1['nodes']),len(graph2['nodes']))
            self.assertTrue(any(n.get('id')=='MANUAL-SOURCE' for n in graph2['nodes']))

    def test_audit_fails_before_sync(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            audit=audit_evidence_graph('PX',root=root)
            self.assertEqual(audit['status'],'FAIL')
            self.assertIn('tool not represented: published_method',audit['issues'])

if __name__=='__main__': unittest.main()
