from pathlib import Path
import csv, json
import importlib.util

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/paper_studies5'; OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('p08_tool_api', Path(__file__).with_name('tool_api.py'))
api=importlib.util.module_from_spec(spec); spec.loader.exec_module(api)

coef_independent=api.independent_euler_thermal_coefficient()
coef_published=api.PUBLISHED_EQ11_COEFF_C_M2
rows=[]
for L in [10,20,30,50,75,100,150,200,300]:
    row={'L_m':L,'T_eq11_C':api.critical_temperature_eq11(L),'T_independent_C':coef_independent/L**2}
    for n in [1,2,3,4]:
        row[f'T_beta004_n{n}_C']=api.critical_temperature_appendix_a(L,n)
    rows.append(row)
with (OUT/'p08_figure7_reconstruction.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
summary={
 'source':'Vaz & Patel (1999), Fig. 7, Eqs. (11)-(12), Appendix A Eq. (A.1)',
 'published_coefficient_C_m2':coef_published,
 'independent_coefficient_C_m2':coef_independent,
 'relative_difference_percent':100*(coef_independent-coef_published)/coef_published,
 'status':'COMPARED',
 'boundary':'Case-study analytical reconstruction; soil friction and pressure differential are excluded as in the source case study.'}
(OUT/'p08_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(f"P08: independent coefficient={coef_independent:.3f} vs published 9476; diff={summary['relative_difference_percent']:.3f}%")
