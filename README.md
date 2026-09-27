# EngiProof v0.2.0 development

> **Windows R1 note:** run `00_SETUP_WINDOWS.bat` once. After that, from this repository folder you can type `engiproof ...` directly even if your prompt still shows `(base)`. The repository-root `engiproof.cmd` dispatches to the local `.venv`.

**From Published Research to Verified Engineering.**

EngiProof turns selected published engineering methods into **source-bounded, callable, reproducible and independently checked engineering studies**. It is not a paper summarizer and it does not silently invent missing inputs.

Live studies:

- **P08** — Vaz & Patel (1999), lateral buckling of bundled pipe systems: Figure 7, Eqs. (11)–(12), Appendix A.
- **P12** — Zhang, Duan & Guedes Soares (2018), PiP lateral-buckling critical force: Table 4, Eq. (22), Table 5 consistency audit.
- **P16** — Chen & Chia (2010), PiP walking: Figure 5 vs Table 2 source-consistency audit. `COMPARED`; no independent walking solver.
- **P29** — Bi & Hao (2016), vibration control: Figure 16 and Eqs. (1)/(16)–(18), with independent state-space and transfer-quadrature evaluation. `CONDITIONAL` because the source PSD/integral convention retains an unresolved factor-of-two issue.
- **P36** — Gong & Li (2015), propagation buckle pressure: Figure 14 vs empirical Eq. (8), using 27 graphical FE-marker centres. `COMPARED`; not a new FE prediction.
- **P38** — Alrsai, Karampour & Albermani (2018), propagation buckling: Figures 10–11, Eqs. (6b)/(12)/(16), Table 2, plus an independent direct work-balance check. P38 is intentionally `CONDITIONAL` overall because the Figure 11 plotted analytical line conflicts with direct Eq. (6b) evaluation.

## 60-second Windows start

1. Clone or extract EngiProof to a normal folder.
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
engiproof tool P16 table2_cumulative_displacement_mm --params "{\"cycle\":6}"
engiproof tool P29 positive_frequency_integral --params "{\"mass_ratio\":0.853,\"gamma\":0.2,\"zeta_t\":0.1}"
engiproof tool P36 equation8_ratio --params "{\"diameter_ratio\":0.6}"
```

The same commands also work without installation:

```bat
python run_engiproof.py doctor
python run_engiproof.py list
python run_engiproof.py verify-all
```

## Evidence-runtime commands

EngiProof v0.1.1 adds versioned generic contracts and queryable evidence/provenance interfaces:

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

P16/P29/P36/P38 copyrighted PDFs and raster snapshots are not distributed. Their DOI/source SHA-256 and source-backed numerical/reference evidence are retained. The runners independently recompute or audit the published relationships without overwriting inherited numerical evidence files.


## v0.2.0 paper ingestion automation

The development branch now adds a conservative intake layer before live studies:

```bat
engiproof ingest "D:\papers\paper.pdf" --paper-id P40 --title "Paper title" --doi "10.xxxx/xxxxx" --year 2026
engiproof intakes
engiproof intake P40
engiproof scaffold P40 --top-targets 3
engiproof promotion-gate P40
```

The original PDF is not copied. EngiProof stores its SHA-256 fingerprint and discovers Figure/Table/Equation/Appendix **candidates** for review. A scaffold remains `DRAFT` and outside the live registry until source-bounded results, tests and callable tools satisfy the promotion gate.

See `docs/INGESTION_AUTOMATION.md` and `ROADMAP_v0.2.0.md`.


## v0.2.0-dev1 source-enrichment commands

After `ingest`, EngiProof can re-open the same external source, verify its SHA-256, and build bounded source locators/target dossiers without copying the paper:

```bat
engiproof enrich P40 "D:\papers\paper.pdf"
engiproof dossiers P40
engiproof dossier P40 T001
engiproof extract-structures P40 "D:\papers\paper.pdf"
engiproof structures P40
engiproof task-bundle P40
engiproof comparison-templates P40
engiproof pipeline P40
```

The enrichment layer records page/line locators, short target-bounded excerpts, unit/symbol candidates, page text hashes, equation/table/figure/definition structure candidates, kind-specific reproduction tasks and target-type comparison templates. Full extracted source text is not persisted by default. Generated structures/tasks/templates remain review/planning artifacts and cannot promote evidence automatically.


## v0.2.0-dev2 robust source/structure gates

Dev2 adds identity and structural-readiness checks before reproduction:

```bat
engiproof audit-source P40 "D:\papers\p40.pdf"
engiproof recover-equations P40 "D:\papers\p40.pdf"
engiproof enrich P40 "D:\papers\p40.pdf"
engiproof extract-structures P40 "D:\papers\p40.pdf"
engiproof readiness P40
engiproof pipeline P40
```

If title/DOI/year metadata is wrong, use `engiproof set-metadata ...` and re-run `audit-source`. Missing-equation recovery preserves existing candidate IDs. A generated structure file no longer implies that selected targets are structurally ready for reproduction.

Project continuity is recorded in `HANDOVER_CURRENT.md`, which must be updated at every meaningful development checkpoint.


## Use EngiProof from an AI agent (MCP)

EngiProof ships an MCP server so Claude Code, Codex, Gemini CLI or any MCP client can call the live studies directly, with the evidence envelope attached to every result.

```bat
pip install -e .[mcp]
claude mcp add engiproof -- engiproof-mcp
```

Exposed to the agent:

- **Tools:** `list_studies`, `describe_study`, `call_method`, `get_evidence_graph`, `get_comparisons`, `get_discrepancies`, `get_provenance`, `get_contract`
- **Resources:** `engiproof://registry`, `engiproof://studies/{id}/manifest`, `.../source`, `.../evidence-graph`
- **Prompt:** `apply_method` — answer a question with a study's methods, staying inside argument ranges and reporting evidence class, status, discrepancies, limitations and any `evidence_boundary`. `INDEPENDENT` is not presented as independent physical or FE validation unless the boundary says so

The server is read-only by default. `run_study` and `verify_study` remain **disabled by default** because the current verification/test paths may rewrite tracked result artifacts (committed CSV/JSON evidence files). Setting `ENGIPROOF_MCP_ALLOW_RUN=1` is an explicit opt-in to those mutating paths, and remains the only way to expose them until non-mutating verification is implemented.

The MCP adapter never upgrades evidence status and never grants qualification.

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

## Source PDFs

Place legally obtained originals in `01_doc/` using the canonical filenames recorded in each `study.json`. PDFs are ignored by Git and are **not** included in public releases.

## Status

v0.2.0 development builds paper-ingestion and evidence automation on top of the v0.1.1 engineering-evidence runtime. It preserves backward compatibility with P08/P12, adds heterogeneous walking, vibration and local-integrity evidence types through P16/P29/P36, and uses P38 as the first complete evidence-chain showcase. This remains research/verification software, not an engineering qualification certificate or replacement for project-specific design verification.

## v0.2.0-dev3 discrepancy automation

Use `engiproof discrepancy-audit P40`, `engiproof assess-discrepancies P40`, `engiproof discrepancy-gate P40`, and `engiproof discrepancy-audit-all`. The engine classifies review/escalation without deciding physical acceptability. P40-D001 is the first real blocking case.
