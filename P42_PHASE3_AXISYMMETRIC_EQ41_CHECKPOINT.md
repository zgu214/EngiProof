# P42 Phase 3 — axisymmetric chain, Eq. (41), and Figure 16 reproducibility boundary

## What closes

Eqs. (24)–(26) are solved directly for the two counter-wound tensile-armor layers. The resulting axial-force and torsion residuals close to machine precision. The stress, axial-strain and twist-rate trends are linear with `Fz` and consistent with the source Figures 12–14.

## What is callable

Eqs. (27)–(30) are implemented explicitly, including fill factor and local wire pressure. Eq. (41) is implemented with its stick/slip transition and is combined with Eqs. (42)–(43).

## What does not close

For the Figure 16 probe, the comparison cases use the source-stated zero pressure and zero applied torsion. A literal outer-to-inner pressure recursion is therefore evaluated with an explicit zero outer nominal-pressure boundary.

That literal implementation does **not** reconcile with the high-tension Figure 16 moment scale. EngiProof does not tune `mu`, pressures, geometry or other source inputs to force agreement.

The result is recorded as `P42-D002 = SOURCE_IMPLEMENTATION_PROVENANCE_GAP`, not as a paper error.

## Engineering boundary

Figure 16 remains **not reproduced** until the exact source implementation convention for Eqs. (27)–(30), or equivalent source code/theory documentation, is available.
