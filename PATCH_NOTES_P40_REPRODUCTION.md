# EngiProof v0.2.0-dev2 — P40 reproduction patch

This patch advances the existing local P40 DRAFT scaffold into a source-bounded `CONDITIONAL` engineering study. It does **not** modify `engiproof/intake/P40/`; the user's fingerprinted intake/enrichment artifacts stay local and intact.

## Added engineering evidence

- source-reviewed Table 1 inputs;
- source-reviewed Table 2 reference values;
- published Eqs. (2), (3), (6), and (9);
- independent Eqs. (8a-d) work-balance reconstruction;
- deterministic comparison CSV;
- open discrepancy P40-D001;
- evidence graph;
- callable methods;
- five P40 tests.

## Key result

PIP-3 direct Eq. (9) normalized ratio = `0.7056664057`; Table 2 = `0.66`. The relative difference versus the published value is about `6.92%`. PIP-1 and PIP-2 reproduce Table 2 to rounding. The independent work-balance reconstruction agrees with direct Eq. (9) within `0.1%`, so the PIP-3 mismatch is retained as OPEN and no input is tuned.

## Local verification

```bat
11_VERIFY_P40_REPRODUCTION_WINDOWS.bat
engiproof verify P40
engiproof promotion-gate P40
engiproof tool P40 table2_reproduction_summary --params "{}"
```

Expected:

- P40 tests: PASS;
- `verify P40`: `PASS` when the exact source PDF is available in a recognized source location, otherwise `PASS_SOURCE_EXTERNAL`;
- evidence status: `CONDITIONAL`;
- qualification: `NOT_GRANTED`;
- promotion gate: technically ready after tests, but promotion should be a deliberate user review decision because P40-D001 is OPEN.
