import json
import tempfile
import unittest
from pathlib import Path

from engiproof.ingestion import (
    discover_targets,
    fingerprint_source,
    ingest_source,
    list_intakes,
    load_intake,
    promotion_gate,
    scaffold_from_intake,
    build_reproduction_plan,
    build_comparison_templates,
    build_task_bundle,
    enrich_source,
    extract_structures,
    load_structure_candidates,
    load_target_dossiers,
    pipeline_status,
    target_dossier, audit_source_identity, recover_equation_candidates, selected_target_readiness, update_intake_metadata,
)

SAMPLE = """Engineering study\nFigure 3 Comparison with experimental results\nTable 2 Test parameters\nEquation (7) analytical model\nFig. 5 numerical validation\n"""


class IngestionTests(unittest.TestCase):
    def _root(self, td: str) -> Path:
        root = Path(td)
        (root / 'engiproof').mkdir()
        (root / 'papers').mkdir()
        (root / 'engiproof' / 'registry.json').write_text(json.dumps({
            'schema_version':'engiproof.registry/1.0','framework':'EngiProof','version':'0.2.0.dev2','studies':[]
        }))
        return root

    def test_fingerprint_does_not_store_absolute_path(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'paper.txt'; p.write_text(SAMPLE)
            fp=fingerprint_source(p)
            self.assertEqual(fp['canonical_filename'],'paper.txt')
            self.assertNotIn(str(Path(td).resolve()),json.dumps(fp))
            self.assertEqual(len(fp['sha256']),64)

    def test_target_discovery(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'paper.txt'; p.write_text(SAMPLE)
            out=discover_targets(p)
            labels={x['label'] for x in out['candidates']}
            self.assertIn('Figure 3',labels)
            self.assertIn('Table 2',labels)
            self.assertIn('Equation (7)',labels)
            self.assertTrue(out['review_required'])

    def test_ingest_and_scaffold_do_not_register_live(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            src=root/'local-source.txt'; src.write_text(SAMPLE)
            out=ingest_source(src,'P90',title='Synthetic source',doi='10.example/test',year=2026,root=root)
            self.assertEqual(out['status'],'TARGET_REVIEW_REQUIRED')
            self.assertEqual(len(list_intakes(root)),1)
            self.assertEqual(load_intake('P90',root)['fingerprint']['canonical_filename'],'local-source.txt')
            scaffold=scaffold_from_intake('P90',top_targets=2,root=root)
            self.assertEqual(scaffold['status'],'DRAFT_SCAFFOLDED')
            reg=json.loads((root/'engiproof/registry.json').read_text())
            self.assertEqual(reg['studies'],[])
            manifest=json.loads((root/'engiproof/studies/P90/study.json').read_text())
            self.assertEqual(manifest['evidence_status'],'DRAFT')

    def test_promotion_gate_blocks_draft(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            src=root/'local-source.txt'; src.write_text(SAMPLE)
            ingest_source(src,'P91',title='Synthetic source',root=root)
            scaffold_from_intake('P91',root=root)
            gate=promotion_gate('P91',root=root)
            self.assertFalse(gate['ready'])
            self.assertTrue(any('DRAFT' in x for x in gate['issues']))

    def test_plan_and_pipeline(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            src=root/'local-source.txt'; src.write_text(SAMPLE)
            ingest_source(src,'P92',title='Synthetic source',root=root)
            scaffold_from_intake('P92',top_targets=2,root=root)
            plan=build_reproduction_plan('P92',root=root)
            self.assertEqual(plan['status'],'PLANNED_NOT_EXECUTED')
            self.assertEqual(len(plan['targets']),2)
            status=pipeline_status('P92',root=root)
            self.assertTrue(status['stages'][0]['complete'])
            self.assertEqual(status['next_stage'],'source_identity')


    def test_source_enrichment_builds_locators_without_full_text(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            src=root/'local-source.txt'; src.write_text(SAMPLE)
            ingest_source(src,'P93',title='Synthetic source',root=root)
            out=enrich_source('P93',src,root=root)
            self.assertEqual(out['status'],'SOURCE_ENRICHED_REVIEW_REQUIRED')
            doc=load_target_dossiers('P93',root=root)
            self.assertGreaterEqual(doc['located_count'],3)
            eq=next(d for d in doc['dossiers'] if d['label']=='Equation (7)')
            self.assertEqual(eq['source_status'],'LOCATED')
            self.assertTrue(eq['occurrences'][0]['locator'].startswith('p1:l'))
            source_map=json.loads((root/'engiproof/intake/P93/source_map.json').read_text())
            self.assertFalse(source_map['raw_text_persisted'])
            self.assertNotIn(str(root.resolve()),json.dumps(doc))

    def test_enrichment_rejects_wrong_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            src=root/'paper.txt'; src.write_text(SAMPLE)
            wrong=root/'wrong.txt'; wrong.write_text(SAMPLE+'changed')
            ingest_source(src,'P94',title='Synthetic source',root=root)
            with self.assertRaises(ValueError):
                enrich_source('P94',wrong,root=root)

    def test_target_dossier_and_task_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            src=root/'local-source.txt'; src.write_text(SAMPLE)
            ingest_source(src,'P95',title='Synthetic source',root=root)
            enrich_source('P95',src,root=root)
            intake=load_target_dossiers('P95',root=root)
            first=intake['dossiers'][0]['candidate_id']
            d=target_dossier('P95',first,root=root)
            self.assertEqual(d['dossier']['candidate_id'],first)
            scaffold_from_intake('P95',top_targets=3,root=root)
            bundle=build_task_bundle('P95',root=root)
            self.assertEqual(bundle['status'],'TASKS_GENERATED_NOT_EXECUTED')
            self.assertEqual(bundle['task_count'],3)
            self.assertTrue(all(t['steps'] for t in bundle['tasks']))
            self.assertTrue((root/'engiproof/intake/P95/reproduction_tasks.json').is_file())

    def test_pipeline_exposes_enrichment_and_task_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            src=root/'local-source.txt'; src.write_text(SAMPLE)
            ingest_source(src,'P96',title='Synthetic source',root=root)
            enrich_source('P96',src,root=root)
            scaffold_from_intake('P96',top_targets=2,root=root)
            extract_structures('P96',src,root=root)
            build_task_bundle('P96',root=root)
            build_comparison_templates('P96',root=root)
            status=pipeline_status('P96',root=root)
            stages={x['stage']:x['complete'] for x in status['stages']}
            self.assertTrue(stages['source_enrichment'])
            self.assertTrue(stages['structure_extraction'])
            self.assertTrue(stages['task_bundle'])
            self.assertTrue(stages['comparison_templates'])


    def test_structure_extraction_and_comparison_templates(self):
        sample = SAMPLE + "\nTable 3 Results\nCase  A  B\n1  2.0  3.0\nS = Effective axial force\n"
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            src=root/'local-source.txt'; src.write_text(sample, encoding='utf-8')
            ingest_source(src,'P97',title='Synthetic source',root=root)
            enrich_source('P97',src,root=root)
            out=extract_structures('P97',src,root=root)
            self.assertEqual(out['status'],'STRUCTURE_REVIEW_REQUIRED')
            structures=load_structure_candidates('P97',root=root)
            self.assertTrue(structures['tables'])
            self.assertTrue(structures['equations'])
            self.assertTrue(any(x['symbol']=='S' for x in structures['definitions']))
            scaffold_from_intake('P97',top_targets=4,root=root)
            templates=build_comparison_templates('P97',root=root)
            self.assertGreaterEqual(templates['template_count'],1)
            self.assertTrue(all(t['status']=='TEMPLATE_ONLY' for t in templates['templates']))

    def test_structure_extraction_rejects_wrong_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td)
            src=root/'paper.txt'; src.write_text(SAMPLE)
            wrong=root/'wrong.txt'; wrong.write_text(SAMPLE+'x')
            ingest_source(src,'P98',title='Synthetic source',root=root)
            enrich_source('P98',src,root=root)
            with self.assertRaises(ValueError):
                extract_structures('P98',wrong,root=root)

    def test_grouped_equation_recovery_preserves_existing_ids(self):
        sample="Study title\nEqs. ( 2), (3), ( 6), and (9) are compared.\nX = a + b ( 9 )\n"
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/'paper.txt'; src.write_text(sample, encoding='utf-8')
            ingest_source(src,'P81',title='Study title',root=root)
            data=load_intake('P81',root=root)['targets']; labels={x['label'] for x in data['candidates']}
            self.assertTrue({'Equation (2)','Equation (3)','Equation (6)','Equation (9)'}.issubset(labels))
            ids={x['label']:x['candidate_id'] for x in data['candidates']}
            out=recover_equation_candidates('P81',src,root=root)
            data2=load_intake('P81',root=root)['targets']; ids2={x['label']:x['candidate_id'] for x in data2['candidates']}
            self.assertEqual(ids['Equation (9)'],ids2['Equation (9)'])
            self.assertEqual(out['added_count'],0)

    def test_type1_equation_number_reconstructs_multiline_block(self):
        sample="Study title\nEquation (9) is proposed.\nPp2 =\n3*pi*sigma\n* (t/D)^2\nð9Þ\nTable 1. Inputs\nCase 1 2 3\n"
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/'paper.txt'; src.write_text(sample, encoding='utf-8')
            ingest_source(src,'P82',title='Study title',root=root); enrich_source('P82',src,root=root); extract_structures('P82',src,root=root)
            st=load_structure_candidates('P82',root=root); eq=next(x for x in st['equations'] if x['label']=='Equation (9)')
            self.assertTrue(eq['blocks']); self.assertIn('Pp2',eq['blocks'][0]['text'])

    def test_table_block_extracts_data_rows_and_readiness(self):
        sample="Study title\nTable 1. Properties\nIdentifier A B C\nPIP-1 80 2 40\nPIP-2 60 2 40\nEquation (9) model\nP = k * x (9)\n"
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/'paper.txt'; src.write_text(sample, encoding='utf-8')
            ingest_source(src,'P83',title='Study title',root=root); enrich_source('P83',src,root=root)
            data=load_intake('P83',root=root)['targets']; wanted=[x['candidate_id'] for x in data['candidates'] if x['label'] in {'Table 1','Equation (9)'}]
            scaffold_from_intake('P83',target_ids=wanted,root=root); extract_structures('P83',src,root=root)
            ready=selected_target_readiness('P83',root=root); self.assertEqual(ready['status'],'READY')

    def test_source_identity_conflict_blocks_promotion(self):
        sample="Propagation Buckling in Subsea Pipe-in-Pipe Systems\nDOI: 10.1061/(ASCE)EM.1943-7889.0001337\n© 2017 ASCE\nEquation (9) model\nP = k*x (9)\n"
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/'paper.txt'; src.write_text(sample, encoding='utf-8')
            ingest_source(src,'P84',title='Propagation Buckling in Subsea Pipe-in-Pipe Systems',doi='10.1016/j.tws.2013.07.003',year=2013,root=root)
            audit=audit_source_identity('P84',src,root=root); self.assertEqual(audit['status'],'CONFLICT'); self.assertEqual(audit['checks']['doi'],'CONFLICT')
            scaffold_from_intake('P84',root=root); gate=promotion_gate('P84',root=root); self.assertFalse(gate['ready']); self.assertIn('source identity conflict',gate['issues'])

    def test_metadata_repair_requires_reaudit_and_syncs_scaffold(self):
        sample="Correct Title\nDOI: 10.1061/test.correct\n© 2017 Publisher\nTable 1. Values\nCase 1 2 3\n"
        with tempfile.TemporaryDirectory() as td:
            root=self._root(td); src=root/'paper.txt'; src.write_text(sample, encoding='utf-8')
            ingest_source(src,'P85',title='Wrong Title',doi='10.1000/wrong',year=2013,root=root); scaffold_from_intake('P85',root=root)
            self.assertEqual(audit_source_identity('P85',src,root=root)['status'],'CONFLICT')
            out=update_intake_metadata('P85',title='Correct Title',doi='10.1061/test.correct',year=2017,root=root)
            self.assertEqual(out['status'],'METADATA_UPDATED_REAUDIT_REQUIRED')
            self.assertFalse((root/'engiproof/intake/P85/source_identity_audit.json').exists())
            manifest=json.loads((root/'engiproof/studies/P85/study.json').read_text())
            self.assertEqual(manifest['source']['doi'],'10.1061/test.correct'); self.assertEqual(manifest['year'],2017)
            self.assertEqual(audit_source_identity('P85',src,root=root)['status'],'PASS')

if __name__=='__main__': unittest.main()
