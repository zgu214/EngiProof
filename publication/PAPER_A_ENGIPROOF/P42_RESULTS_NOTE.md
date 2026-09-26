# P42 publication evidence note

P42 adds a third discrepancy class to the EngiProof methodology paper: a documented **model-form / kinematic discrepancy** rather than a source error.

The published analytical model assumes a loxodromic tensile-armor wire path. Through Eqs. (36)-(39), the analytical transverse and normal wire-bending stresses are independent of axial tension `Fz`. In the published FP-RUC results (Figures 21 and 23), both stress components vary with `Fz`.

EngiProof regenerates the analytical stress families from the published equations and source geometry, but does not digitize or claim reproduction of the FP-RUC point clouds.

This should be contrasted with:
- P40/P41 numerical/reference mismatches;
- P41 unit inconsistency;
- P42 model-form/kinematic difference.

The source itself attributes the P42 difference to sliding interaction and the difference between the loxodromic analytical wire-path assumption and FP-RUC kinematics.

## Reproducibility/provenance boundary from the Eq. (41) chain

A further P42 checkpoint shows why source-bounded reproduction must be separated from equation transcription. Eqs. (24)–(26) can be solved with machine-precision axial-force/torsion closure and reproduce the source response trends. However, a literal implementation of the Eqs. (27)–(30) contact-pressure recursion, followed by Eq. (41), does not close against the high-tension Figure 16 moment scale under the explicit zero-pressure comparison boundary.

This is **not** reported as a source error. It is retained as a source-implementation provenance gap. No friction coefficient, contact pressure or geometry is tuned to make the published figure agree.

