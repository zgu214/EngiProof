import csv, json, math, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from engiproof.core import invoke_tool, load_manifest, validate_study_manifest
from engiproof.discrepancy import discrepancy_audit, discrepancy_gate
from engiproof.ingestion import promotion_gate

class P40EngiProofTests(unittest.TestCase):
    def test_runner_and_open_discrepancy(self):
        p=subprocess.run([sys.executable,str(ROOT/'papers/P40/run_calculation.py')],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        v=json.loads((ROOT/'papers/P40/results/engiproof_verification.json').read_text(encoding='utf-8'))
        self.assertEqual(v['status'],'CONDITIONAL')
        d=v['open_discrepancy']
        self.assertEqual(d['identifier'],'PIP-3')
        self.assertAlmostEqual(d['calculated_eq9_ratio'],0.7056664056684557,places=12)
        self.assertAlmostEqual(d['published_eq9_ratio'],0.66,places=12)
        self.assertGreater(d['relative_to_published_percent'],6.0)

    def test_equation9_limit_to_equation6(self):
        p9=invoke_tool('P40','equation9_pressure_kPa',{
            'Do':80.0,'to':3.0,'Di':0.0,'ti':0.0,'sigma_Yo_MPa':209.0,'sigma_Yi_over_sigma_Yo':0.75})['result']
        p6=invoke_tool('P40','equation6_pressure_kPa',{'D':80.0,'t':3.0,'sigma_Y_MPa':209.0})['result']
        self.assertAlmostEqual(p9,p6,places=12)

    def test_table2_supporting_equations(self):
        s=invoke_tool('P40','table2_reproduction_summary',{})['result']
        for row in s['rows']:
            self.assertLessEqual(abs(row['eq2_ratio']-row['eq2_published_ratio']),0.01)
            self.assertLessEqual(abs(row['eq3_ratio']-row['eq3_published_ratio']),0.01)
            self.assertLessEqual(abs(row['eq6_ratio']-row['eq6_published_ratio']),0.01)
        p1=next(r for r in s['rows'] if r['identifier']=='PIP-1')
        p2=next(r for r in s['rows'] if r['identifier']=='PIP-2')
        p3=next(r for r in s['rows'] if r['identifier']=='PIP-3')
        self.assertLess(abs(p1['eq9_ratio']-p1['eq9_published_ratio']),0.01)
        self.assertLess(abs(p2['eq9_ratio']-p2['eq9_published_ratio']),0.01)
        self.assertGreater(abs(p3['eq9_ratio']-p3['eq9_published_ratio']),0.04)

    def test_independent_work_balance(self):
        s=invoke_tool('P40','table2_reproduction_summary',{})['result']
        self.assertLess(max(abs(r['eq9_vs_independent_percent']) for r in s['rows']),0.1)

    def test_evidence_boundary(self):
        m=load_manifest('P40')
        self.assertEqual(validate_study_manifest(m),[])
        self.assertEqual(m['evidence_status'],'CONDITIONAL')
        self.assertEqual(m['qualification'],'NOT_GRANTED')
        self.assertTrue(any(d['status']=='OPEN' for d in m['discrepancies']))
        self.assertFalse((ROOT/'papers/P40/source.pdf').exists())

    def test_generic_discrepancy_assessment_blocks_promotion(self):
        audit=discrepancy_audit('P40'); self.assertEqual(audit['promotion_blocker_count'],1); item=audit['assessments'][0]; self.assertEqual(item['category'],'PUBLISHED_REFERENCE_MISMATCH'); self.assertTrue(item['rounding_check']['beyond_rounding_band']); self.assertEqual(item['independent_support'],'CORROBORATES_REPRODUCTION'); self.assertFalse(discrepancy_gate('P40')['ready']); gate=promotion_gate('P40'); self.assertFalse(gate['ready']); self.assertTrue(any('P40-D001' in x for x in gate['issues'])); self.assertTrue((ROOT/'papers/P40/results/discrepancy_assessment.json').is_file())

if __name__=='__main__': unittest.main()
