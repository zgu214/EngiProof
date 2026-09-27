# P44 Source Contract

## Canonical source

R. C. S. Bueno and C. K. Morooka, **Analysis Method for Contact Forces Between Drillstring-Well-Riser**, SPE 28723, presented at the 1994 SPE International Petroleum Conference & Exhibition of Mexico, Veracruz, 10–13 October 1994. DOI `10.2118/28723-MS` (canonical).

Identity note (2026-09-27): DOI confirmed by the study owner from the publisher record. Older references may cite the historical alias `10.2523/28723-MS`; `10.2118/28723-MS` is canonical.

Canonical external basename:

`p44-bueno1994.pdf`

SHA-256:

`ca8b476b5f6c54f8a2a3c55c7836770ef55bc27d3cf05b8c6f4a953ca896b80b`

The copyrighted source PDF remains external to the public repository.

## Selected Phase-1 targets

- Table 1 — drillpipe data.
- Table 2 — marine riser system data.
- Figure 3 — gap/contact spring idealization.
- Figures 7–8 — contact-force profiles and their stated time labels.
- Figure 9 — maximum contact force versus time, source-reviewed only.
- Equation (1) — constant-inclination equilibrium check inside the well.

## Evidence boundary

The paper describes a nonlinear 2D quasi-static finite-element workflow with large displacement, Newton–Raphson iteration, beam elements, tool-joint contact points and gap springs. It does not provide enough source detail to reconstruct the complete whole-well/riser FE model or the time-dependent wall geometry without additional implementation data.

Phase 1 therefore reproduces only source-bounded checks that are independently reconstructable:
- drillpipe section area and second moment from OD/ID;
- Equation (1) equilibrium force;
- the 5.8 s / 10-slice time discretization;
- a penalty-stiffness penetration diagnostic using the published K1;
- source-internal consistency of Figure 7/8 time labels.

No published figure raster is redistributed and no curve digitization is claimed.
