# EngiProof v0.1.1 development

> **Windows R1 note:** run `00_SETUP_WINDOWS.bat` once. After that, from this repository folder you can type `engiproof ...` directly even if your prompt still shows `(base)`. The repository-root `engiproof.cmd` dispatches to the local `.venv`.

**From Published Research to Verified Engineering.**

EngiProof turns selected published engineering methods into **source-bounded, callable, reproducible and independently checked engineering studies**. It is not a paper summarizer and it does not silently invent missing inputs.

Initial live studies:

- **P08** — Vaz & Patel (1999), lateral buckling of bundled pipe systems: Figure 7, Eqs. (11)–(12), Appendix A.
- **P12** — Zhang, Duan & Guedes Soares (2018), PiP lateral-buckling critical force: Table 4, Eq. (22), Table 5 consistency audit.
- **P38** — Alrsai, Karampour & Albermani (2018), propagation buckling: Figures 10–11, Eqs. (6b)/(12)/(16), Table 2, plus an independent direct work-balance check. P38 is intentionally `CONDITIONAL` overall because the Figure 11 plotted analytical line conflicts with direct Eq. (6b) evaluation.

## 60-second Windows start

1. Extract this ZIP to a normal folder, for example `D:\Engineering\EngiProof_v0.1.0`.
2. Double-click **`00_SETUP_WINDOWS.bat`**.
3. Double-click **`01_DEMO_WINDOWS.bat`**.
4. Double-click **`02_VERIFY_WINDOWS.bat`**.

Expected verification status for the bundled studies is `PASS_SOURCE_EXTERNAL` when the original PDFs are not present. That is intentional: the runnable evidence is bundled, but copyrighted source PDFs are not redistributed.

## Command-line start

```bat
.venv\Scripts\activate
engiproof doctor
engiproof list
engiproof verify-all
engiproof tool P08 critical_temperature_eq11 --params "{\"length_m\":100}"
engiproof tool P12 table4_fit_force_MN --params "{\"beta\":0.6,\"clearance_mm\":12}"
```

The same commands also work without installation:

```bat
python run_engiproof.py doctor
python run_engiproof.py list
python run_engiproof.py verify-all
```


## v0.1.1 evidence-runtime commands

The develop branch adds versioned generic contracts and queryable evidence/provenance interfaces:

```bat
engiproof schema
engiproof schema study
engiproof evidence P38
engiproof compare P38
engiproof discrepancy P38
engiproof provenance P38
engiproof verify P38
engiproof tool P38 equation16_ratio --params "{\"diameter_ratio\":0.5,\"thickness_ratio\":0.6,\"yield_ratio\":1.0,\"mode\":\"A\"}"
```

P38's copyrighted PDF and extracted raster figures are not distributed. The source SHA-256, DOI, extraction contract and deterministic digitized-point provenance are retained. The public runner reproduces the inherited numerical evidence without changing the five numerical result files.

## Evidence contract

Every callable result carries:

- `paper_id`
- `evidence`
- `evidence_class` (`PUBLISHED`, `INDEPENDENT`, later `SOLVER_NEW` where justified)
- `evidence_status`
- explicit limitations

The framework must not promote evidence status merely because code runs. Missing source inputs remain missing; source inconsistencies remain visible; regression/fitted comparisons are not relabelled as independent physics.

## Add a new paper

```bat
python tools\new_study.py P13 "Paper title" --doi "10.xxxx/xxxxx"
```

This creates a **DRAFT** study scaffold only. It does not claim reproduction or validation.

## GitHub

For a fast repository launch, read `docs/GITHUB_RELEASE.md`. If GitHub CLI (`gh`) is installed, `03_PUBLISH_GITHUB_WINDOWS.bat` can create and push a repository after you choose public/private.

## Source PDFs

Place legally obtained originals in `01_doc/` using the canonical filenames recorded in each `study.json`. PDFs are ignored by Git and are **not** included in this package.

## Status

v0.1.1 development extends the public v0.1.0 baseline into a reusable engineering-evidence runtime. P08 and P12 remain backward compatible; P38 is the first complete evidence-chain study. This remains research/verification software, not an engineering qualification certificate or replacement for project-specific design verification.
