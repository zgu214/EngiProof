# P43 Source Contract

## Canonical source

D. W. Dareing and T. Huang, **Natural Frequencies of Marine Drilling Risers**, Journal of Petroleum Technology, July 1976, SPE 5820.

Canonical external basename:

`p43-dareing1976.pdf`

SHA-256:

`4ab7c3b9a8377cc3d5a7f5eecb64712496aa825f969760e47ee17ccba03ffccf`

The copyrighted source PDF is external to the public repository.

## Selected source targets

- Eq. (8): dimensionless variable-tension eigenvalue equation.
- Eq. (9): source power-series solution form.
- Eq. (10): uniformly tensioned-beam approximation.
- Table 1: published eigenvalues for the first five modes.
- Table 2: published approximation errors.
- Figure 6: first three non-trigonometric mode shapes for alpha=250, beta=100.
- Published worked example: 500-ft riser, bottom pull 286,000 lb.

## Evidence boundary

The paper states that details of the source power-series coefficient solution are documented in earlier references and are not repeated in this paper. EngiProof therefore does not reconstruct hidden source implementation details.

Instead, EngiProof independently solves Eq. (8) by a Hermite beam finite-element weak formulation. This is classified as `INDEPENDENT`, then compared against the published Table 1 eigenvalues.

No source figure raster is redistributed.
