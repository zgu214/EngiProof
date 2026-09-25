# EngiProof v0.1.1 progress

Checkpoint: 25 September 2026

## Completed in P38 integration batch

- Added versioned generic Study, Source, Evidence, Comparison, Discrepancy and Verification contracts.
- Added P38 as the first complete evidence-chain study.
- Preserved inherited P38 numerical evidence byte-for-byte for:
  - `reference_comparisons.csv`
  - `calculated_curves.csv`
  - `table2_check.csv`
  - `independent_work_checks.csv`
  - `summary.json`
- Added public-safe P38 reproduction: source PDF/raster assets remain external; SHA-256/source contract retained.
- Added evidence graph, comparison records, discrepancy records and provenance query.
- Added CLI: `schema`, `evidence`, `compare`, `discrepancy`, `provenance`.
- P08/P12 schema/tool behavior retained.
- Full local suite: 19 tests passed.
- `verify-all`: PASS; P08/P12/P38 return `PASS_SOURCE_EXTERNAL` when copyrighted PDFs are absent.

## P38 evidence disposition

- Figure 10(a): `COMPARED`
- Figure 10(b): `COMPARED`
- Figure 11(a): `CONDITIONAL`
- Figure 11(b): `CONDITIONAL`
- Table 2 arithmetic: `COMPARED`
- Direct work balance: independent mathematical `VERIFIED` check
- Engineering qualification: `NOT_GRANTED`

## Next authorized work

1. Run this batch on the user's Windows develop branch and confirm CI.
2. Integrate the next source-ready study, preferably P16/P29/P36, without weakening evidence boundaries.
3. Only after several heterogeneous studies use the contracts, stabilize schema naming for v0.2.0.
