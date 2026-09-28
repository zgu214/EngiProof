# P44 — Drillstring / Well / Riser Contact Forces

P44 is a source-bounded contact-mechanics case based on SPE 28723 (Bueno & Morooka, 1994).

Phase 1 does **not** claim recreation of the complete nonlinear whole-well FE model. The paper does not provide the complete time-dependent wall geometry, contact-node layout, environmental coefficient set, or all solver implementation details required for that.

Instead, Phase 1 reproduces the strongest independently checkable evidence:
- Table 1 drillpipe area and second moment from OD/ID;
- Equation (1) equilibrium force in the constant-inclination well section;
- source 10-slice wave-period discretization;
- penalty-stiffness penetration scale;
- Figure 7/8 time-label consistency audit.

The contact spring description is retained as a source model:
K0 negligible before contact, K1 = 1e6 lbf/ft after gap closure.

Qualification remains `NOT_GRANTED`.
