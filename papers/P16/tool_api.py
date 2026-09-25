"""Callable, source-bounded P16 tools.

The functions expose printed Table 2 arithmetic and the reviewed Figure 5
vector-curve extraction. They do not implement an independent walking solver.
"""
from __future__ import annotations
import csv
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent

def _read_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def _table_rows():
    return _read_csv(HERE/"reference"/"table2_cycles.csv")

def _curve():
    rows=_read_csv(HERE/"reference"/"figure5_vector_curve.csv")
    x=np.array([float(r["step"]) for r in rows], dtype=float)
    y=np.array([float(r["displacement_mm"]) for r in rows], dtype=float)
    return x,y

def table2_cumulative_displacement_mm(cycle: int) -> float:
    """Cumulative printed Table 2 walking increment through the requested cycle."""
    if int(cycle) != cycle or not 1 <= int(cycle) <= 6:
        raise ValueError("cycle must be an integer from 1 to 6.")
    rows=_table_rows()
    return float(sum(float(r["increment_mm"]) for r in rows[:int(cycle)]))

def figure5_interpolated_displacement_mm(step: float) -> float:
    """Linear interpolation of the reviewed published Figure 5 vector curve."""
    x,y=_curve()
    step=float(step)
    if not np.isfinite(step) or step < x.min() or step > x.max():
        raise ValueError(f"step must lie within the extracted curve range [{x.min()}, {x.max()}].")
    return float(np.interp(step,x,y))

def figure5_table2_discrepancy_mm(cycle: int) -> float:
    """Figure-5 interpolation minus cumulative Table-2 displacement [mm]."""
    if int(cycle) != cycle or not 1 <= int(cycle) <= 6:
        raise ValueError("cycle must be an integer from 1 to 6.")
    row=_table_rows()[int(cycle)-1]
    fig=figure5_interpolated_displacement_mm(float(row["end_step"]))
    tab=table2_cumulative_displacement_mm(int(cycle))
    return float(fig-tab)

def comparison_summary() -> dict:
    vals=[figure5_table2_discrepancy_mm(i) for i in range(1,7)]
    return {
        "cycles": 6,
        "maximum_absolute_discrepancy_mm": float(max(abs(v) for v in vals)),
        "mean_absolute_discrepancy_mm": float(sum(abs(v) for v in vals)/len(vals)),
        "final_table_cumulative_mm": table2_cumulative_displacement_mm(6),
        "evidence_boundary": "Published figure/table consistency only; no independent walking solver.",
    }
