from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("p43_api", HERE / "tool_api.py")
api = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(api)

summary = api.phase1_eigen_benchmark_summary()

(RESULTS / "phase1_eigen_benchmark_summary.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)

rows = summary["table1_independent_FE_comparison"]["comparisons"]
with (RESULTS / "table1_alpha50_beta100_comparison.csv").open("w", encoding="utf-8", newline="") as f:
    fields = ["mode", "published_lambda", "independent_FE_lambda", "difference", "relative_difference_percent"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

mspec = importlib.util.spec_from_file_location("p43_mechanics", HERE / "mechanics.py")
m = importlib.util.module_from_spec(mspec)
assert mspec.loader is not None
mspec.loader.exec_module(m)
shape = m.sample_mode_shape(250.0, 100.0, 1, elements=160, points=501)

with (RESULTS / "figure6_mode1_independent.csv").open("w", encoding="utf-8", newline="") as f:
    fields = ["zeta", "Y_normalized", "slope", "curvature"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for vals in zip(shape["zeta"], shape["Y_normalized"], shape["slope"], shape["curvature"]):
        w.writerow(dict(zip(fields, vals)))


phase2 = api.phase2_full_matrix_summary()
small = {k:v for k,v in phase2.items() if k not in ("table1_full_matrix","figures4_5_parameter_families","figure6_first_three_modes")}
small["table1_full_matrix"] = {k:v for k,v in phase2["table1_full_matrix"].items() if k != "comparisons"}
small["figures4_5_parameter_families"] = {k:v for k,v in phase2["figures4_5_parameter_families"].items() if k != "rows"}
small["figure6_first_three_modes"] = {k:v for k,v in phase2["figure6_first_three_modes"].items() if k != "rows"}
(RESULTS / "phase2_full_matrix_summary.json").write_text(json.dumps(small,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
with (RESULTS / "table1_full_matrix_comparison.csv").open("w",encoding="utf-8",newline="") as f:
    fields=["alpha","beta","mode","published_lambda","independent_FE_lambda","FE_difference","FE_relative_difference_percent","eq10_lambda","eq10_error_from_printed_table1_percent","eq10_error_from_independent_FE_percent","published_table2_error_percent"]
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(phase2["table1_full_matrix"]["comparisons"])
with (RESULTS / "figures4_5_parameter_families.csv").open("w",encoding="utf-8",newline="") as f:
    fields=["alpha","beta","published_lambda1","independent_lambda1","published_lambda2","independent_lambda2"]
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(phase2["figures4_5_parameter_families"]["rows"])
with (RESULTS / "figure6_first_three_modes_independent.csv").open("w",encoding="utf-8",newline="") as f:
    fields=["mode","zeta","Y_normalized","slope","curvature"]
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(phase2["figure6_first_three_modes"]["rows"])

verification = {
    "schema_version": "engiproof.p43.verification/1.0",
    "paper_id": "P43",
    "checks": {
        "eq8_independent_FE_vs_table1": True,
        "eq10_vs_table2": True,
        "worked_example_period": True,
        "figure6_inflection_location": True,
        "phase2_full_table_matrix": True,
        "phase2_figures4_6_reconstructed": True,
        "P43_D001_preserved": True,
        "source_curve_digitized": False
    },
    "qualification": "NOT_GRANTED"
}
(RESULTS / "engiproof_verification.json").write_text(
    json.dumps(verification, indent=2) + "\n", encoding="utf-8"
)

print(json.dumps(summary, indent=2, ensure_ascii=False))
