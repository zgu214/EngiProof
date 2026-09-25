"""Callable source-bounded P36 Eq. (8) tools."""
from __future__ import annotations
import csv, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
CFG=json.loads((HERE/"inputs"/"figure14.json").read_text(encoding="utf-8"))

def equation8_ratio(
    diameter_ratio: float,
    A: float = CFG["A"],
    B: float = CFG["B"],
    exponent: float = CFG["exponent"],
) -> float:
    """Published P36 Eq. (8): normalized propagation-pressure ratio."""
    x=float(diameter_ratio)
    if not np.isfinite(x) or x <= 0:
        raise ValueError("diameter_ratio must be positive and finite.")
    if exponent <= 0:
        raise ValueError("exponent must be > 0.")
    den=1.0-float(B)*x
    if den <= 0:
        raise ValueError("Eq. (8) denominator is non-positive for this diameter ratio.")
    return float(1.0+float(A)*x**float(exponent)/den)

def figure14_residual_summary() -> dict:
    with (HERE/"reference"/"figure14_vector_markers.csv").open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    diffs=[]
    for row in rows:
        ref=float(row["pressure_ratio"])
        calc=equation8_ratio(float(row["diameter_ratio"]))
        diffs.append(100.0*(calc-ref)/ref)
    return {
        "reference_markers":len(rows),
        "mean_absolute_percent":float(np.mean(np.abs(diffs))),
        "maximum_absolute_percent":float(np.max(np.abs(diffs))),
        "evidence_boundary":"Graphical FE symbol centres; in-sample empirical equation audit, not new FE prediction.",
    }
