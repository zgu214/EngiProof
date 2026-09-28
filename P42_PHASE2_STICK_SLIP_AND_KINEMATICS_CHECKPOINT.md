# P42 Phase 2 — stick/slip and model-form kinematics

Implemented published Eqs. (31)-(35) as callable friction/stick-slip relations with explicit contact-pressure inputs.

Regenerated analytical wire-bending stress families from Eqs. (36)-(39), using source geometry/material data and an independent helix-angle calculation.

At `kappa_G = 0.06 1/m`:
- inner transverse amplitude ≈ 84.095 MPa;
- outer transverse amplitude ≈ 84.103 MPa;
- inner normal amplitude ≈ 21.315 MPa;
- outer normal amplitude ≈ 21.294 MPa.

These are analytical-curve reproductions corresponding to the solid-line families in Figures 20-23. FP-RUC points are not digitized.

P42-D001 records the source-documented model-form difference:
analytical bending stress is independent of axial tension `Fz`, whereas FP-RUC results vary with `Fz`. The paper attributes this to sliding interaction and differing wire-path/kinematic assumptions.
