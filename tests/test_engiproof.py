import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from engiproof.core import doctor, invoke_tool, list_studies, load_manifest, verify_all, verify_study

class EngiProofTests(unittest.TestCase):
    def test_doctor(self):
        self.assertEqual(doctor()['status'],'PASS')
    def test_registry(self):
        self.assertEqual([x['paper_id'] for x in list_studies()],['P08','P12'])
    def test_p08_tool(self):
        out=invoke_tool('P08','critical_temperature_eq11',{'length_m':100.0})
        self.assertAlmostEqual(out['result'],0.9476,places=10)
        self.assertEqual(out['evidence_class'],'PUBLISHED')
    def test_p12_tool(self):
        out=invoke_tool('P12','table4_fit_force_MN',{'beta':0.6,'clearance_mm':12.0})
        self.assertAlmostEqual(out['result'],1.6243216727,places=8)
        self.assertEqual(out['evidence_class'],'INDEPENDENT')
    def test_verify(self):
        for pid in ('P08','P12'):
            v=verify_study(pid)
            self.assertIn(v['status'],{'PASS','PASS_SOURCE_EXTERNAL'})
            self.assertEqual(v['missing_required_files'],[])
    def test_verify_all(self):
        self.assertEqual(verify_all()['status'],'PASS')
    def test_schema(self):
        for pid in ('P08','P12'):
            self.assertEqual(load_manifest(pid)['schema_version'],'engiproof.study/1.0')

if __name__=='__main__': unittest.main()
