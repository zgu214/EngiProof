from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"src"))
from engiproof.discrepancy import assess_discrepancies
_spec=importlib.util.spec_from_file_location("p40_tool_api",HERE/"tool_api.py")
api=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(api)

summary=api.table2_reproduction_summary()
rows=summary["rows"]
out_csv=HERE/"results"/"table2_reproduction.csv"
out_csv.parent.mkdir(parents=True,exist_ok=True)
fields=[
    "identifier","eq2_ratio","eq2_published_ratio","eq3_ratio","eq3_published_ratio",
    "eq6_ratio","eq6_published_ratio","eq9_ratio","eq9_published_ratio",
    "independent_work_balance_ratio","eq9_vs_independent_percent","eq9_ratio_difference"
]
with out_csv.open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

max_support=max(
    abs(r[k]-r[p])
    for r in rows
    for k,p in (("eq2_ratio","eq2_published_ratio"),("eq3_ratio","eq3_published_ratio"),("eq6_ratio","eq6_published_ratio"))
)
max_eq9_ind=max(abs(r["eq9_vs_independent_percent"]) for r in rows)
verification={
    "schema_version":"engiproof.verification/1.0",
    "paper_id":"P40",
    "status":"CONDITIONAL",
    "source_pdf_external":True,
    "supporting_equations_max_absolute_ratio_difference":max_support,
    "published_eq9_vs_independent_max_percent":max_eq9_ind,
    "open_discrepancy":summary["open_discrepancy"],
    "qualification":"NOT_GRANTED",
    "limitations":[
        "PIP-3 Table 2 reports Eq. (9) normalized ratio 0.66, while direct Eq. (9) evaluation from Table 1 inputs gives approximately 0.7057.",
        "The discrepancy is preserved and no source parameter is tuned to force agreement.",
        "The independent work-balance check reproduces the Eq. (9) mechanics to within rounding of the published 0.626/2.515 reduction.",
        "No source FE model is reproduced."
    ]
}
(HERE/"results"/"engiproof_verification.json").write_text(json.dumps(verification,indent=2)+"\n",encoding="utf-8")
assessment=assess_discrepancies("P40",root=ROOT,persist=True)
verification["discrepancy_assessment"]={"promotion_blocker_count":assessment["promotion_blocker_count"],"artifact":assessment.get("artifact")}
(HERE/"results"/"engiproof_verification.json").write_text(json.dumps(verification,indent=2)+"\n",encoding="utf-8")
print(json.dumps(verification,indent=2))
