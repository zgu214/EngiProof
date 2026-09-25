from pathlib import Path
import csv, json, math
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/paper_studies5'; OUT.mkdir(parents=True,exist_ok=True)
betas=np.array([0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
r0mm=np.array([2.,4.,8.,12.,16.,20.,24.])
Fc=np.array([
[3.37,3.09,2.89,2.71,2.66,2.62,2.60],
[2.67,2.41,2.29,2.17,2.13,2.11,2.08],
[2.23,2.02,1.91,1.83,1.80,1.78,1.76],
[1.94,1.76,1.66,1.61,1.58,1.57,1.55],
[1.72,1.58,1.50,1.45,1.42,1.41,1.40],
[1.57,1.45,1.37,1.33,1.31,1.29,1.28],
[1.44,1.34,1.26,1.24,1.21,1.20,1.19],
[1.35,1.25,1.18,1.16,1.14,1.13,1.12]])
# Delta r from Table 3 geometry: outer-pipe inside radius minus inner-pipe outside radius.
Do=0.3556; to=0.0111; Di=0.2731
delta_r_mm=((Do-2*to)/2-Di/2)*1000
X=[]; y=[]; meta=[]
for i,b in enumerate(betas):
  for j,r in enumerate(r0mm):
    X.append([1/b,math.log(r/delta_r_mm),1.0]); y.append(Fc[i,j]); meta.append((b,r,Fc[i,j]))
X=np.asarray(X); y=np.asarray(y)
coef=np.linalg.lstsq(X,y,rcond=None)[0]
pred=X@coef
# Published Eq.22 coefficients, multiplied by one common dimensional scale S.
eq22=np.array([0.321,-0.0739,0.129])
S=(coef@eq22)/(eq22@eq22)
coef_scaled=S*eq22
pred22=X@coef_scaled
rows=[]
for (b,r,obs),pf,p22 in zip(meta,pred,pred22):
  rows.append({'beta':b,'clearance_mm':r,'r0_over_Delta_r':r/delta_r_mm,'published_Fc_MN':obs,
               'direct_regression_MN':pf,'eq22_scaled_MN':p22,'eq22_diff_percent':100*(p22-obs)/obs})
with (OUT/'p12_table4_eq22_reconstruction.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
# Table 5 visible duplicate-row audit.
t5_beta03=[2.33,1.84,1.54,1.34,1.18,1.08,0.99]
t5_beta10=[2.33,1.84,1.54,1.34,1.18,1.08,0.99]
audit=[]
for r,a,b in zip(r0mm,t5_beta03,t5_beta10):
  audit.append({'clearance_mm':r,'table5_beta03':a,'table5_beta10':b,'difference':b-a})
with (OUT/'p12_table5_duplicate_row_audit.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=audit[0].keys());w.writeheader();w.writerows(audit)
summary={
 'source':'Zhang, Duan & Guedes Soares (2018), Table 4 and Eq. (22)',
 'delta_r_mm':delta_r_mm,
 'direct_fit_coefficients_MN':[float(x) for x in coef],
 'eq22_coefficients':[float(x) for x in eq22],
 'common_scale_MN':float(S),
 'ratio_direct_b_over_a':float(coef[1]/coef[0]),
 'ratio_eq22_b_over_a':float(eq22[1]/eq22[0]),
 'ratio_direct_c_over_a':float(coef[2]/coef[0]),
 'ratio_eq22_c_over_a':float(eq22[2]/eq22[0]),
 'eq22_scaled_mean_abs_error_percent':float(np.mean(np.abs((pred22-y)/y))*100),
 'eq22_scaled_max_abs_error_percent':float(np.max(np.abs((pred22-y)/y))*100),
 'table5_beta10_duplicates_beta03':bool(t5_beta03==t5_beta10),
 'status':'COMPARED',
 'boundary':'This reconstructs the stiffness-ratio/clearance dependence from the published Table 4 data. It does not independently predict the FE-derived Table 4 values from soil/contact mechanics.'}
(OUT/'p12_summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(f"P12: Eq22 coefficient-ratio recovery; scaled mean abs error={summary['eq22_scaled_mean_abs_error_percent']:.3f}%, max={summary['eq22_scaled_max_abs_error_percent']:.3f}%")
print(f"P12: direct ratios b/a={summary['ratio_direct_b_over_a']:.6f} vs Eq22={summary['ratio_eq22_b_over_a']:.6f}; c/a={summary['ratio_direct_c_over_a']:.6f} vs Eq22={summary['ratio_eq22_c_over_a']:.6f}")
