# Cross-environment verification record

Recorded 28 September 2026 from CI at commit `a50cd9d`. The machine-readable form is `docs/CROSS_ENVIRONMENT_VERIFICATION.json`. Every job ran `engiproof environment-record`: non-mutating verification of all 12 studies with a manifest (live P08–P38 and frozen P40–P45) against frozen evidence, then the tracked-file non-mutation gate and the full test suite.

This establishes **recomputation equivalence**, not engineering acceptance. Verification is not qualification.

| OS | Machine | Python | NumPy | Status | IDENTICAL | BYTE_ONLY | ENVIRONMENT_METADATA | NUMERICAL_NONMATERIAL | NUMERICAL_MATERIAL | MATERIAL_NON_NUMERIC |
|---|---|---|---|---|---|---|---|---|---|---|
| Darwin | arm64 | 3.13.15 | 2.5.3 | PASS | 14 | 8 | 2 | 15 | 0 | 0 |
| Linux | x86_64 | 3.10.21 | 2.2.6 | PASS | 15 | 10 | 2 | 12 | 0 | 0 |
| Linux | x86_64 | 3.12.14 | 2.5.3 | PASS | 14 | 9 | 3 | 13 | 0 | 0 |
| Linux | x86_64 | 3.13.15 | 2.5.3 | PASS | 14 | 9 | 4 | 12 | 0 | 0 |
| Windows | AMD64 | 3.10.11 | 2.2.6 | PASS | 23 | 1 | 0 | 15 | 0 | 0 |
| Windows | AMD64 | 3.13.15 | 2.5.3 | PASS | 24 | 1 | 0 | 14 | 0 | 0 |

Counts are regenerated artifacts per class, summed over the 12 studies.

## Non-identical artifacts by study

| Study | Darwin 3.13.15 | Linux 3.10.21 | Linux 3.12.14 | Linux 3.13.15 | Windows 3.10.11 | Windows 3.13.15 |
|---|---|---|---|---|---|---|
| P08 | B1 | B1 | B1 | B1 | = | = |
| P12 | B1 N2 | B2 | B1 N2 | B1 N2 | N2 | N2 |
| P16 | E1 | N1 | E1 | E1 | N1 | = |
| P29 | N1 | N1 | N1 | E1 | N1 | N1 |
| P36 | E1 | E1 | E1 | E1 | = | = |
| P38 | B3 N2 | B4 E1 | B4 E1 | B4 E1 | N2 | N2 |
| P40 | B1 | B1 | B1 | B1 | = | = |
| P41 | B1 | B1 | B1 | B1 | = | = |
| P42 | B1 N2 | B1 N2 | B1 N2 | B1 N2 | N1 | N1 |
| P43 | N7 | N7 | N7 | N7 | N7 | N7 |
| P44 | = | = | = | = | = | = |
| P45 | N1 | N1 | N1 | N1 | B1 N1 | B1 N1 |

Legend: `=` all regenerated artifacts IDENTICAL; `B` BYTE_ONLY; `E` ENVIRONMENT_METADATA; `N` NUMERICAL_NONMATERIAL; `NM!` NUMERICAL_MATERIAL; `M!` MATERIAL_NON_NUMERIC (the last two would fail verification). The number after each letter is the count of artifacts in that class.

## Findings that led to D-007 (approved by the owner, 28 September 2026)

The first cross-OS runs (commits `be809a7`, `c102cde`, `d3979a5`) failed. Frozen evidence was not changed to make them pass:

- **F20 — P45, all environments.** The independent Appendix-1 FE check (fine-mesh `numpy.linalg`) moves by ≤ 2.9e-7 absolute. Its FE-vs-analytic residual (~3e-8) moves by ≤ 1e-8, up to 47 % relative, which is NUMERICAL_MATERIAL under the default 1e-9/1e-12. Handled by a path-scoped recomputation tolerance on that block only. The engineering boolean `appendix1_matches_independent_fe` (residual < 1e-6) is still compared exactly.
- **F21 — P38 on Windows and macOS.** Provenance hashes of CSVs that changed non-materially were flagged material; they now inherit the CSV's own class. Relative-path keys are written with the OS separator; the separator is now treated as a rendering difference and the values are still compared.
- A Windows-only test failure was a test-encoding bug (cp1252 default) and was fixed in the test.

Regenerate the record from the CI annotations of a later commit when the matrix or the frozen evidence changes.
