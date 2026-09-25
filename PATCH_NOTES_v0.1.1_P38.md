# EngiProof v0.1.1 P38 integration patch

Apply on branch `develop` after the public v0.1.0 release.

This batch adds generic evidence contracts and integrates P38 from `PiP_Library_Continuation_P38_2026-09-25.zip`. It deliberately excludes the copyrighted P38 PDF and raster figure extracts.

## Preservation check

The adapted public P38 runner regenerated these inherited files byte-identically against the supplied PiP package in the build environment:

- `reference_comparisons.csv` — SHA-256 `4d090d3a4d98fe1ea591984575fdcba50fd21a0b3f5aa4a61d5b009040532118`
- `calculated_curves.csv` — `c960044022247ad61d8fe6915588926b68326b316e471e5ab829632407279330`
- `table2_check.csv` — `dcedb023b568b70c9efa56e50584d4a82b1fed9d299a74909c97483e5d6c90cc`
- `independent_work_checks.csv` — `e72613cda7b67aa7e641ce62b4bae1fb5b2281b788042a971d826c6268d69b8e`
- `summary.json` — `aac609cc9f103f8fed46a35553314585207e9ce94837f52b5c90ec511585513a`

The original P38 calculation manifest is preserved as `source_calculation_manifest.json`; the public EngiProof run writes a separate `engiproof_reproduction_manifest.json`.

## Local verification

```bat
python -m pip install -e .
python -m unittest discover -s tests -v
engiproof verify-all
engiproof evidence P38
engiproof discrepancy P38
```

Expected local suite at patch build: **19 tests passed**.
