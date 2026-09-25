"""Reconstruct P38 Figures 10–11 and audit their source arithmetic.
Author: Zhiqiang Gu | Zhiqiang.gu214@gmail.com
Run from any directory: python papers/P38/run_calculation.py
No FE, fitting, internet, or proprietary software is used.
"""
from pathlib import Path
import csv,json,hashlib,math,sys
import numpy as np
from mechanics import equation1,equation6b,equation12a,equation12b,equation16,work_balance
P=Path(__file__).resolve().parent; OUT=P/'results';OUT.mkdir(exist_ok=True)

def read(p):
    with p.open(encoding='utf-8') as f:return list(csv.DictReader(f))
def write(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
def xmap(c,x):return c['xmin']+(x-c['x0'])/(c['x1']-c['x0'])*(c['xmax']-c['xmin'])
def ymap(c,y):return c['ymax']-(y-c['y0'])/(c['y1']-c['y0'])*(c['ymax']-c['ymin'])
def drs(c,x):return (x,c['thickness_ratio'],c['yield_ratio']) if c['x_quantity']=='Di/Do' else (c['diameter_ratio'],x,c['yield_ratio'])
def stats(v):
    a=np.asarray(v,float)
    return {'n':len(a),'mean_signed_percent':float(a.mean()),'mean_absolute_percent':float(np.abs(a).mean()),'max_absolute_percent':float(np.abs(a).max())}

def main():
    con=json.loads((P/'reference/extraction_contract.json').read_text())
    # Copyrighted source assets are external to the public EngiProof package.
    # Verify them if locally supplied; otherwise continue from the frozen extraction contract
    # and digitized provenance without claiming an independent source re-extraction.
    root=P.parents[1]
    source_candidates=[P/'source.pdf', root/'01_doc'/'p38-alrsai2018.pdf']
    source_path=next((q for q in source_candidates if q.is_file()),None)
    source_asset_check={'pdf_present':bool(source_path),'pdf_hash_match':None,'rasters_checked':0}
    if source_path:
        actual=hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_asset_check['pdf_hash_match']=actual==con['source_sha256']
        if not source_asset_check['pdf_hash_match']:
            raise RuntimeError('Source PDF changed; review source contract before reuse.')
    for name,h in con['image_sha256'].items():
        q=P/'reference'/name
        if q.is_file():
            source_asset_check['rasters_checked']+=1
            if hashlib.sha256(q.read_bytes()).hexdigest()!=h:
                raise RuntimeError('Source raster changed.')
    rows=[]
    for v in read(P/'reference/pixel_points.csv'):
        c=con['panels'][v['panel']]; x=xmap(c,float(v['x_pixel']));y=ymap(c,float(v['y_pixel']))
        # Use measured x, not snapped parameter values, for all comparisons.
        dx=(float(v['horizontal_reading_pixels'])+1)*(c['xmax']-c['xmin'])/(c['x1']-c['x0'])
        dy=(float(v['vertical_reading_pixels'])+1)*(c['ymax']-c['ymin'])/(c['y1']-c['y0'])
        d,r,s=drs(c,x); out=dict(v,x=x,published_ratio=y,reading_dx=dx,reading_dy=dy,diameter_ratio=d,thickness_ratio=r,yield_ratio=s)
        for name,fn in [('eq6b',equation6b),('eq12a',equation12a),('eq12b',equation12b)]:
            pred=fn(d,r,s);out[name]=pred;out[name+'_difference_percent']=100*(pred-y)/y
        # Mode labels are source inputs; no inferred automatic branch switch.
        out['eq16']='';out['eq16_difference_percent']=''
        if v['kind']=='published_FE':
            pred=equation16(d,r,s,v['mode']);out['eq16']=pred;out['eq16_difference_percent']=100*(pred-y)/y
        out['eq6b_delta_from_published_line']=out['eq6b']-y
        lo,hi=max(c['xmin'],x-dx),min(c['xmax'],x+dx)
        eqx=max(abs(equation6b(*drs(c,z))-out['eq6b']) for z in [lo,hi])
        out['eq6b_line_residual_over_reading_envelope']=abs(out['eq6b']-y)/(dy+eqx)
        rows.append(out)
    write('reference_comparisons.csv',rows)
    curves=[]
    for panel,c in con['panels'].items():
        for x in np.linspace(c['xmin'] if panel.startswith('11') else .4,1.2 if panel.startswith('11') else .75,161):
            d,r,s=drs(c,float(x));curves.append(dict(panel=panel,x=float(x),eq6b=equation6b(d,r,s),eq12a=equation12a(d,r,s),eq12b=equation12b(d,r,s),eq16A=equation16(d,r,s,'A'),eq16B=equation16(d,r,s,'B')))
    write('calculated_curves.csv',curves)
    panel_stats={}
    for panel in con['panels']:
        fe=[r for r in rows if r['panel']==panel and r['kind']=='published_FE']
        line=[r for r in rows if r['panel']==panel and r['kind']=='published_Eq6b_line']
        panel_stats[panel]={'FE_comparison':{m:stats([r[m+'_difference_percent'] for r in fe]) for m in ['eq6b','eq12a','eq12b','eq16']},'source_line_check':stats([r['eq6b_difference_percent'] for r in line]),'line_points_outside_reading_envelope':sum(r['eq6b_line_residual_over_reading_envelope']>1 for r in line)}
    a=json.loads((P/'inputs/table1_case.json').read_text());Do,to,Di,ti,so,si=[a[k] for k in ['outer_diameter_m','outer_thickness_m','inner_diameter_m','inner_thickness_m','outer_yield_Pa','inner_yield_Pa']]
    pp=equation1(Do,to,so);ratio=equation6b(Di/Do,ti/to,si/so);pip=pp*ratio
    energy=work_balance(Do,to,Di,ti,so,si);single=work_balance(Do,to,0,0,so,si)
    ts=[]
    for quantity,pred,printed,exp in [('single_pressure_Pa',pp,a['printed_analytical_single_Pa'],a['published_experiment_single_Pa']),('PiP_pressure_Pa',pip,a['printed_analytical_PiP_Pa'],a['published_experiment_PiP_Pa']),('PiP_single_ratio',ratio,a['printed_analytical_ratio'],a['published_experiment_PiP_Pa']/a['published_experiment_single_Pa'])]:
        ts.append(dict(quantity=quantity,calculated=pred,printed_analytical=printed,experimental_reference=exp,vs_printed_percent=100*(pred-printed)/printed,vs_experiment_percent=100*(pred-exp)/exp))
    write('table2_check.csv',ts)
    checks=[]
    # Dimensional work equation versus reduced Eq.6 using only rounding constants.
    for d in [.3,.4,.55,.7,.75]:
        for r in [.3,.5,.7,1.,1.2]:
            for s in [.8,1.,1.12,1.4]:
                w=work_balance(.06,.0015,.06*d,.0015*r,139e6,139e6*s)
                w0=work_balance(.06,.0015,0,0,139e6,139e6*s)
                exact=w['pressure_Pa']/w0['pressure_Pa'];rounded=equation6b(d,r,s)
                checks.append(dict(d=d,r=r,s=s,exact_work_ratio=exact,eq6b_ratio=rounded,rounding_difference_percent=100*(rounded-exact)/exact,relative_work_residual=w['relative_work_residual']))
    write('independent_work_checks.csv',checks)
    summary={'study':'P38 Figures 10a,b / 11a,b and Table2 audit','source_sha256':con['source_sha256'],'evidence_class':'Published equation reconstruction compared with manually digitized published FE reference; not independent FE validation. Eq16 is an in-sample published-fit audit, mode label supplied.','targets':{'Fig10a':'COMPARED','Fig10b':'COMPARED','Fig11a':'CONDITIONAL','Fig11b':'CONDITIONAL','Table2_arithmetic':'COMPARED'},'panel_statistics':panel_stats,'table2':ts,'work_check':{'case':energy,'single_case':single,'constant_exact':4*math.sqrt(2)-math.pi,'constant_printed':2.515,'exact_inner_geometric_coefficient':(2*math.pi-4*math.sqrt(2))/(4*math.sqrt(2)-math.pi),'rounded_inner_coefficient':.25,'max_work_residual':max(abs(c['relative_work_residual']) for c in checks),'max_rounding_difference_percent':max(abs(c['rounding_difference_percent']) for c in checks),'case_pressure_vs_eq6a_percent':100*(energy['pressure_Pa']-pip)/pip},'qualification':'NOT_GRANTED','source_line_issue':'Figure11 analytical line differs from direct Eq6b evaluation with panel-labelled ratios; no hidden parameter adjustment. Figure10 line agrees within extraction uncertainty.','notes':'Source FE points are reference data. Plotted line sample size and deterministic reading envelopes are not validation tolerances.'}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    fingerprints={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [P/'mechanics.py',P/'run_calculation.py',P/'inputs/table1_case.json',P/'reference/extraction_contract.json',P/'reference/pixel_points.csv']}
    generated=[OUT/'reference_comparisons.csv',OUT/'calculated_curves.csv',OUT/'table2_check.csv',OUT/'independent_work_checks.csv',OUT/'summary.json']
    result_hashes={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in generated}
    repro={'schema_version':'engiproof.reproduction/1.0','paper_id':'P38','source_asset_check':source_asset_check,'inputs_and_code_sha256':fingerprints,'result_sha256':result_hashes,'python':sys.version.split()[0],'numpy':np.__version__,'qualification':'NOT_GRANTED'}
    (OUT/'engiproof_reproduction_manifest.json').write_text(json.dumps(repro,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
