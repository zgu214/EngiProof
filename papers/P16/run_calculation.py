from __future__ import annotations
import csv, hashlib, importlib.util, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location("p16_tool_api",HERE/"tool_api.py")
api=importlib.util.module_from_spec(spec); spec.loader.exec_module(api)

def read_csv(path):
    with path.open(encoding="utf-8",newline="") as f: return list(csv.DictReader(f))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

published=read_csv(HERE/"results"/"figure5_table2_comparison.csv")
recomputed=[]
for row in published:
    cycle=int(row["cycle"])
    tab=api.table2_cumulative_displacement_mm(cycle)
    fig=api.figure5_interpolated_displacement_mm(float(row["end_step"]))
    diff=fig-tab
    recomputed.append((cycle,tab,fig,diff))
    for key,value in [("table_cumulative_mm",tab),("figure_interpolated_mm",fig),("figure_minus_table_mm",diff)]:
        if abs(float(row[key])-value) > 1e-9:
            raise AssertionError(f"P16 inherited {key} drift at cycle {cycle}: {row[key]} vs {value}")

summary=api.comparison_summary()
out={
    "schema_version":"engiproof.verification/1.0",
    "paper_id":"P16",
    "status":"COMPARED",
    "source_pdf_external":True,
    "comparison":summary,
    "inherited_result_sha256":sha(HERE/"results"/"figure5_table2_comparison.csv"),
    "reference_curve_points":len(read_csv(HERE/"reference"/"figure5_vector_curve.csv")),
    "qualification":"NOT_GRANTED",
    "limitations":[
        "Figure values are graphical vector-curve references, not raw solver output.",
        "No independent pipeline-walking solver is implemented."
    ]
}
(HERE/"results"/"engiproof_verification.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,indent=2))
