"""Source-bounded callable methods for EngiProof study P38.

Published equations reproduce relationships printed in Alrsai, Karampour and
Albermani (2018). The independent work-balance method checks the analytical
reduction only; none of these functions is a shell-FE solver or design
qualification method.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path

_P=Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location('engiproof_p38_mechanics',_P/'mechanics.py')
_m=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)


def equation6b_ratio(diameter_ratio: float, thickness_ratio: float, yield_ratio: float) -> float:
    return float(_m.equation6b(diameter_ratio,thickness_ratio,yield_ratio))


def equation12a_ratio(diameter_ratio: float, thickness_ratio: float, yield_ratio: float) -> float:
    return float(_m.equation12a(diameter_ratio,thickness_ratio,yield_ratio))


def equation12b_ratio(diameter_ratio: float, thickness_ratio: float, yield_ratio: float) -> float:
    return float(_m.equation12b(diameter_ratio,thickness_ratio,yield_ratio))


def equation16_ratio(diameter_ratio: float, thickness_ratio: float, yield_ratio: float, mode: str) -> float:
    return float(_m.equation16(diameter_ratio,thickness_ratio,yield_ratio,mode))


def independent_work_balance_ratio(
    outer_diameter_m: float,
    outer_thickness_m: float,
    inner_diameter_m: float,
    inner_thickness_m: float,
    outer_yield_Pa: float,
    inner_yield_Pa: float,
) -> float:
    pip=_m.work_balance(outer_diameter_m,outer_thickness_m,inner_diameter_m,inner_thickness_m,outer_yield_Pa,inner_yield_Pa)['pressure_Pa']
    single=_m.work_balance(outer_diameter_m,outer_thickness_m,0.0,0.0,outer_yield_Pa,inner_yield_Pa)['pressure_Pa']
    return float(pip/single)


def table1_analytical_pressures() -> dict[str,float]:
    import json
    c=json.loads((_P/'inputs/table1_case.json').read_text(encoding='utf-8'))
    Do,to,Di,ti,so,si=[c[k] for k in ['outer_diameter_m','outer_thickness_m','inner_diameter_m','inner_thickness_m','outer_yield_Pa','inner_yield_Pa']]
    single=_m.equation1(Do,to,so)
    ratio=_m.equation6b(Di/Do,ti/to,si/so)
    return {'single_pressure_Pa':float(single),'PiP_pressure_Pa':float(single*ratio),'PiP_single_ratio':float(ratio)}
