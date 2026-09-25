# P38 source contract — propagation mechanisms and figure consistency

Author: Zhiqiang Gu | Zhiqiang.gu214@gmail.com  
EngiProof integration checkpoint: 25 September 2026

## Primary source

M. Alrsai, H. Karampour and F. Albermani (2018), *Numerical study and parametric analysis of the propagation buckling behaviour of subsea pipe-in-pipe systems*, Thin-Walled Structures 125, 119–128. DOI: **10.1016/j.tws.2018.01.019**.

Canonical local filename: `p38-alrsai2018.pdf`  
Expected SHA-256: `ad96546c33d7dfe114c4ee59461655f2d5fc08bae70690d3fdded68094bcce12`.

The copyrighted source PDF and its extracted raster figures are **not redistributed** in EngiProof. The public study contains the source contract, deterministic digitized point provenance, published-equation implementations, and comparison results. When the canonical PDF is placed in `01_doc/`, EngiProof verifies its SHA-256.

## Selected targets

| Target | Source location | Evidence status |
|---|---|---|
| Figure 10(a), diameter sweep, mode A | PDF p.7 / printed p.125; Eq.6b p.121 and Eqs.12a,b p.124 | `COMPARED` |
| Figure 10(b), diameter sweep, mode B | same | `COMPARED` |
| Figure 11(a), thickness sweep | PDF p.7 / printed p.125 | `CONDITIONAL` |
| Figure 11(b), thickness sweep | same | `CONDITIONAL` |
| Eqs.16a,b on selected published FE points | PDF p.8 / printed p.126 | `COMPARED`, mode-conditioned in-sample published-fit audit |
| Table 2 analytical arithmetic | PDF p.4 / printed p.122 | `COMPARED` within printed input rounding |
| Direct work balance | Eqs.4–5, PDF p.3 / printed p.121 | independent mathematical verification only |

## Evidence boundary

The Figure 10/11 FE markers are published reference data, not independently generated EngiProof FE. Equation 16 is a published fitted relationship and the A/B mode label is supplied from the source evidence; EngiProof does not infer the propagation mode. The direct work-balance check verifies the mathematical reduction behind the analytical expression and is not an independent physical model.

The Figure 11 plotted analytical line remains inconsistent with direct Eq.6b evaluation using the panel-labelled inputs. EngiProof preserves this as an open discrepancy. No coefficient, hidden input, normalization or yield placement is adjusted to force agreement.

No new shell FE, design-pressure qualification or engineering acceptance is claimed by this study.
