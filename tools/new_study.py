from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description='Create a DRAFT EngiProof study scaffold.')
    ap.add_argument('paper_id')
    ap.add_argument('title')
    ap.add_argument('--doi',default='')
    ap.add_argument('--year',type=int,default=0)
    ns=ap.parse_args()
    pid=ns.paper_id.upper()
    pdir=ROOT/'papers'/pid; sdir=ROOT/'engiproof'/'studies'/pid
    if pdir.exists() or sdir.exists(): raise SystemExit(f'{pid} already exists')
    pdir.mkdir(parents=True); sdir.mkdir(parents=True)
    (pdir/'SOURCE.md').write_text(f'# {pid} source contract\n\n**Paper:** {ns.title}\n\n**Status:** `DRAFT`\n\n## Evidence boundary\n\nDefine exact selected targets and unavailable inputs before implementation.\n',encoding='utf-8')
    (pdir/'tool_api.py').write_text('"""DRAFT callable tools. Do not expose until source-bounded and tested."""\n',encoding='utf-8')
    (pdir/'run_calculation.py').write_text('raise SystemExit("DRAFT: implement source-bounded reproduction before running")\n',encoding='utf-8')
    manifest={
      'schema_version':'engiproof.study/1.0','framework':'EngiProof','framework_version':'0.1.0',
      'paper_id':pid,'title':ns.title,'year':ns.year,'evidence_status':'DRAFT','category':'UNCLASSIFIED',
      'source':{'canonical_pdf':f'{pid.lower()}.pdf','sha256':'','doi':ns.doi},
      'selected_targets':[],'runner':f'papers/{pid}/run_calculation.py','source_contract':f'papers/{pid}/SOURCE.md',
      'result_files':[],'verification_tests':[],'tools':[],
      'limitations':['DRAFT scaffold only; no reproduction or engineering acceptance claimed.'],
      'next_actions':['Define source targets and exact evidence boundary.']
    }
    (sdir/'study.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    regp=ROOT/'engiproof'/'registry.json'; reg=json.loads(regp.read_text())
    reg['studies'].append(pid); regp.write_text(json.dumps(reg,indent=2)+'\n',encoding='utf-8')
    print(f'Created DRAFT study {pid}. Review files under papers/{pid} and engiproof/studies/{pid}.')
if __name__=='__main__': main()
