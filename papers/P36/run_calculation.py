from __future__ import annotations
import csv, hashlib, importlib.util, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("p36_tool_api",HERE/"tool_api.py")
api=importlib.util.module_from_spec(spec); spec.loader.exec_module(api)

def read_csv(path):
    with path.open(encoding="utf-8",newline="") as f: return list(csv.DictReader(f))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

markers=read_csv(HERE/"reference"/"figure14_vector_markers.csv")
published=read_csv(HERE/"results"/"figure14_comparison.csv")
if len(markers) != len(published):
    raise AssertionError("P36 marker/result row count mismatch.")

max_row_drift=0.0
for marker,row in zip(markers,published):
    x=float(marker["diameter_ratio"]); ref=float(marker["pressure_ratio"])
    calc=api.equation8_ratio(x)
    diff=100.0*(calc-ref)/ref
    drift=max(abs(calc-float(row["equation8_ratio"])),abs(diff-float(row["relative_difference_percent"])))
    max_row_drift=max(max_row_drift,drift)
    if drift > 1e-10:
        raise AssertionError(f"P36 inherited comparison drift at x={x}: {drift}")

summary=api.figure14_residual_summary()
out={
    "schema_version":"engiproof.verification/1.0",
    "paper_id":"P36",
    "status":"COMPARED",
    "source_pdf_external":True,
    "comparison":summary,
    "maximum_recomputed_row_drift":max_row_drift,
    "inherited_result_sha256":sha(HERE/"results"/"figure14_comparison.csv"),
    "qualification":"NOT_GRANTED",
    "limitations":[
        "Source FE marker centres are graphical references, not unrounded FE data.",
        "The comparison is in-sample and is not an independent FE validation."
    ]
}
(HERE/"results"/"engiproof_verification.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,indent=2))
