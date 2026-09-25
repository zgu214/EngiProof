from __future__ import annotations
import csv, hashlib, importlib.util, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("p29_tool_api",HERE/"tool_api.py")
api=importlib.util.module_from_spec(spec); spec.loader.exec_module(api)

def read_csv(path):
    with path.open(encoding="utf-8",newline="") as f: return list(csv.DictReader(f))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

surface=read_csv(HERE/"results"/"figure16_surface.csv")
max_surface_rel=0.0
max_factor_error=0.0
for row in surface:
    mu=float(row["mass_ratio"]); gamma=float(row["gamma"]); zt=float(row["zeta_t"])
    inherited=float(row["positive_frequency_integral"])
    calc=api.positive_frequency_integral(mu,gamma,zt)
    rel=abs(calc-inherited)/inherited
    max_surface_rel=max(max_surface_rel,rel)
    max_factor_error=max(max_factor_error,abs(float(row["two_sided_integral"])-2.0*inherited))
    if rel > 1e-10:
        raise AssertionError(f"P29 surface drift at mu={mu}, gamma={gamma}, zeta_t={zt}: rel={rel}")
    if abs(float(row["two_sided_integral"])-2.0*inherited) > 1e-14:
        raise AssertionError("P29 two-sided factor-of-two convention drift.")

checks=read_csv(HERE/"results"/"independent_integral_checks.csv")
max_state_rel=0.0; max_quad_rel=0.0
for row in checks:
    mu=float(row["mass_ratio"]); gamma=float(row["gamma"]); zt=float(row["zeta_t"])
    state=api.positive_frequency_integral(mu,gamma,zt)
    quad=api.direct_transfer_quadrature(mu,gamma,zt)
    ref_state=float(row["state_space_integral"]); ref_quad=float(row["direct_Eq17_18_quadrature"])
    max_state_rel=max(max_state_rel,abs(state-ref_state)/ref_state)
    max_quad_rel=max(max_quad_rel,abs(quad-ref_quad)/ref_quad)
if max_state_rel > 1e-10 or max_quad_rel > 2e-9:
    raise AssertionError(f"P29 independent check drift: state={max_state_rel}, quadrature={max_quad_rel}")

out={
    "schema_version":"engiproof.verification/1.0",
    "paper_id":"P29",
    "status":"CONDITIONAL",
    "source_pdf_external":True,
    "surface_points":len(surface),
    "max_surface_relative_difference":max_surface_rel,
    "max_state_space_reference_relative_difference":max_state_rel,
    "max_direct_quadrature_reference_relative_difference":max_quad_rel,
    "spectral_convention_factor":2.0,
    "open_discrepancy":"The source figure display and printed two-sided integral differ by a factor of two for the same numerical S0; exact PSD convention remains unclosed.",
    "inherited_surface_sha256":sha(HERE/"results"/"figure16_surface.csv"),
    "inherited_independent_checks_sha256":sha(HERE/"results"/"independent_integral_checks.csv"),
    "qualification":"NOT_GRANTED"
}
(HERE/"results"/"engiproof_verification.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out,indent=2))
