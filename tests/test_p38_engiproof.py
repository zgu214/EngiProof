import csv
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from engiproof.core import evidence_snapshot, load_manifest, validate_study_manifest
P=ROOT/'papers/P38'
spec=importlib.util.spec_from_file_location('p38mechanics',P/'mechanics.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class P38EngiProofTests(unittest.TestCase):
    def test_runner_reproduces_key_evidence(self):
        p=subprocess.run([sys.executable,str(P/'run_calculation.py')],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        s=json.loads((P/'results/summary.json').read_text(encoding='utf-8'))
        self.assertEqual(s['targets']['Fig10a'],'COMPARED')
        self.assertEqual(s['targets']['Fig11a'],'CONDITIONAL')
        self.assertAlmostEqual(s['table2'][0]['calculated'],578769.223126549,places=6)
        self.assertAlmostEqual(s['work_check']['max_rounding_difference_percent'],0.06464990760955018,places=10)
        self.assertEqual(s['qualification'],'NOT_GRANTED')
        with (P/'results/reference_comparisons.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),46)
        with (P/'results/calculated_curves.csv').open(encoding='utf-8') as f: curves=list(csv.DictReader(f))
        self.assertEqual(len(curves),644)

    def test_source_issue_is_preserved(self):
        s=json.loads((P/'results/summary.json').read_text(encoding='utf-8'))
        self.assertEqual(s['targets']['Fig11a'],'CONDITIONAL')
        self.assertEqual(s['targets']['Fig11b'],'CONDITIONAL')
        self.assertIn('differs from direct Eq6b',s['source_line_issue'])
        man=load_manifest('P38')
        self.assertTrue(any(d['id']=='P38-D001' and d['status']=='OPEN' for d in man['discrepancies']))

    def test_independent_work_balance(self):
        d=m.work_balance(.06,.002,.04,.0016,139e6,172e6)
        self.assertLess(abs(d['relative_work_residual']),1e-14)
        exact=d['pressure_Pa']/m.work_balance(.06,.002,0,0,139e6,172e6)['pressure_Pa']
        published=m.equation6b(2/3,.8,172/139)
        self.assertLess(abs(published/exact-1),0.001)

    def test_pixel_provenance(self):
        with (P/'reference/pixel_points.csv').open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
        self.assertEqual(sum(r['kind']=='published_FE' for r in rows),30)
        self.assertEqual(sum(r['kind']=='published_Eq6b_line' for r in rows),16)
        self.assertFalse((P/'source.pdf').exists())
        self.assertFalse((P/'reference/figure10.png').exists())
        self.assertFalse((P/'reference/figure11.jpeg').exists())

    def test_evidence_graph(self):
        g=evidence_snapshot('P38')['graph']
        self.assertEqual(g['qualification'],'NOT_GRANTED')
        ids={n['id'] for n in g['nodes']}
        self.assertIn('D-F11',ids)
        self.assertIn('I-WORK',ids)
        self.assertGreaterEqual(len(g['edges']),10)

    def test_contract_is_valid(self):
        self.assertEqual(validate_study_manifest(load_manifest('P38')),[])

    def test_mode_is_explicit(self):
        with self.assertRaises(ValueError): m.equation16(.5,.8,1,'auto')
        self.assertNotEqual(m.equation16(.5,.8,1,'A'),m.equation16(.5,.8,1,'B'))


if __name__=='__main__': unittest.main()
