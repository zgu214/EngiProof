# P45 — Safai (1983), Nonlinear dynamic analysis of deep water risers

Phase 1: source-bounded checks of the published tables, formulations and figure statements. Evidence status `CONDITIONAL`; qualification `NOT_GRANTED`. See `SOURCE.md` for the evidence boundary.

```bat
python papers\P45\run_calculation.py
engiproof verify P45
engiproof tool P45 phase1_summary
engiproof tool P45 appendix1_stiffness_coefficients --params "{\"F_N\":-2.0,\"EI_Nm2\":1.0,\"L_m\":1.0}"
engiproof discrepancy P45
```

| Path | Content |
|---|---|
| `reference/` | Transcribed source values with page locators; digitized head-end envelopes (numbers only) |
| `extraction/digitize_head_envelopes.py` | Provenance tool for the digitized envelopes (needs the private source page images) |
| `mechanics.py` | PUBLISHED formulations (Appendix 1, Eq. 7, Appendix 2) and INDEPENDENT check machinery |
| `tool_api.py` | Callable tools and the Phase 1 summary |
| `results/` | Frozen Phase 1 evidence (`phase1_summary.json`, `engiproof_verification.json`) |

Open discrepancies: P45-D001 (buoyed element weight), P45-D002 (Table 1 tension magnitude, cases 3–6), P45-D003 (1200 m tension unit), P45-D004 (head-motion equation typography), P45-D005 (meaning of head-motion "amplitude"), P45-D006 (definition of the "~15%" claim).
