# P41 Phase 3 — global-buckling response and Eq. (14)

Scope: source-bounded review of Figures 8–10 plus callable Eq. (14). No curve digitization or FE recreation.

Independent Table 1 elastic bending stiffness:
- inner EI ≈ 2.5640e7 N m²
- outer EI ≈ 8.7089e7 N m²
- outer/inner ≈ 3.3966

This supports the paper's qualitative statement that the outer pipe is normally the stiffer bending member, but does not reproduce nonlinear Figure 10 curves.

Eq. (14): `M_D = M_f * gamma_f * gamma_C`.

New OPEN discrepancy P41-D002:
the paragraph reports approximately 300/850 MNm while Figure 10 uses `Moment [kNm]` on a 0–1000 scale. The likely intended kNm interpretation is not silently applied without provenance.
