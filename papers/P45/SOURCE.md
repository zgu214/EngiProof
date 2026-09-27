# P45 Source Contract

## Canonical source

V. Hachemi Safai, **Nonlinear dynamic analysis of deep water risers**, *Applied Ocean Research* 5(4), 215–225, 1983 (received 26 July 1982). DOI `10.1016/0141-1187(83)90036-6`.

Canonical external basename: `p45-safai1983.pdf`

SHA-256: `c10b4938dd3c4de6c027f8494386b43a46fc2c3cb011a69de94612dc52686a0d`

The source is an 11-page 300 dpi bilevel scan with an OCR text layer. All evidence values were read from the page images, not the OCR layer. The copyrighted PDF and its page images remain external to the public repository. Source identity details and the manual DOI/year confirmation are in `reference/source_identity.json`.

## Methodological role in Paper A

P45 adds **nonlinear, time-dependent riser dynamics** to the evidence matrix: an updated-Lagrangian beam formulation with geometric stiffness (Appendix 1), step-by-step θ-Wilson integration with internal iterations (Eq. 7–13, Appendix 3), Morison hydrodynamics with an added-mass matrix (Eq. 2–3, Appendix 2), a six-case inter-program comparison (Figures 4–9) and a linear-versus-nonlinear structure comparison (Figure 11).

## Selected Phase-1 targets

| Target | Locator | Treatment |
|---|---|---|
| Table 1 — six comparison cases | p. 218 | PUBLISHED values; INDEPENDENT tension plausibility (P45-D002) |
| Table 2 — riser, environment, head motion | p. 218 | PUBLISHED values; INDEPENDENT geometry, imperial-origin and buoyancy checks (P45-D001, P45-D005) |
| Table 3 — 1200 m riser | p. 221 | PUBLISHED values; INDEPENDENT weight balance (P45-D003) |
| Figures 4(a)–9(a) | pp. 219–221 | head-end tips digitized (numbers only, `extraction/digitize_head_envelopes.py`) |
| Figures 4(b)–9(b) | pp. 219–221 | source review only |
| 1200 m example inputs, Figure 10 | p. 222 | PUBLISHED inputs; head-motion equation typography (P45-D004); tension unit missing (P45-D003) |
| Figure 11 and the "~15%" statement | p. 222 | printed labels; INDEPENDENT arithmetic (P45-D006) |
| Equation (7) | p. 217 | PUBLISHED coefficients; INDEPENDENT reductions and stability of a reconstructed SDOF scheme |
| Appendix 1 | pp. 223–224 | PUBLISHED k1/k2/k3, K, K_G; INDEPENDENT identities, limits, buckling points, Hermite-FE solution, rigid-body modes |
| Appendix 2 | pp. 224–225 | PUBLISHED C1–C4, B_i; INDEPENDENT interpolation and projector identities |

## Evidence boundary

- **PUBLISHED**: formulations and values transcribed from the source.
- **INDEPENDENT**: checks built by EngiProof — table arithmetic, unit conversions, Airy dispersion, an independent beam-column FE solution, a reconstructed single-degree-of-freedom integrator, graphical measurement of published head envelopes, label arithmetic.
- **Cross-program comparison** (RISER vs eight other programs, Figures 4–9): published evidence only; EngiProof neither re-runs the programs nor treats the agreement as independent validation.
- **Model-form difference** (linear vs nonlinear structure, Figure 11): published claim, checked arithmetically from printed labels only.
- **Not reproducible from source detail**: the nonlinear dynamic responses themselves. θ, β, λ, the iteration tolerance ε and limit NL, the structural damping, the discretisation of cases 1–6, the float coverage/mass of the 1200 m riser and the tension unit are not given. No `SOLVER_NEW` evidence is produced, and no unknown input is tuned.

Qualification: `NOT_GRANTED`.
