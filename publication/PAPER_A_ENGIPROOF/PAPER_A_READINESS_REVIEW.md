# Paper A — Readiness Review (post-P45)

Review date: 27 September 2026 · repository `develop` after PR #5 (`cb2a595`) and the P45 freeze patch (D-006) · framework `0.2.0.dev8`

Supersedes the pre-P45 decision in `PAPER_A_READINESS.md` §5 (“Is P46 required? — after P45, perform a formal readiness review”). Companion files: `CLAIM_EVIDENCE_MATRIX.md`, `PAPER_A_GAPS.md`, `PAPER_A_OUTLINE.md`.

## 1. Question

What can EngiProof now support as a publishable methods/evidence paper, given the actual evidence in P40–P45 and the runtime? The review does not summarise six papers; it tests candidate claims against repository artifacts. Paper count, test count, file count and pages are not treated as evidence of validity.

## 2. Result

| | |
|---|---|
| Claims tested | 30 (`CLAIM_EVIDENCE_MATRIX.md`) |
| SUPPORTED | 20 |
| PARTIALLY_SUPPORTED | 4 |
| NOT_SUPPORTED_YET | 3 |
| OUT_OF_SCOPE | 3 |
| Genuine evidence gaps | 5 (G1–G5, `PAPER_A_GAPS.md`) |
| Gaps requiring a new source (category d) | **0** |
| **Decision gate** | **B — Paper A needs specific runtime/method work, but no P46** |

The central thesis is supported: EngiProof keeps source identity, published methods, independent computations, discrepancies, human decisions, evidence graphs, non-mutating verification and the qualification boundary explicitly separated and machine-auditable, and it does so across six heterogeneous published studies without tuning or silent correction.

What is not yet strong enough is narrower: the human decision boundary has been exercised once, the discrepancy vocabulary is not controlled, ingestion and audit outcomes are recorded only in prose, cross-OS evidence rests on reported local runs, and experimental evidence is never handled as its own population.

## 3. Diversity and stress-test value of P40–P45

| Case | Source (year, venue) | Format stress recorded | Mechanics | Evidence exercised | Extraction/identity failure exposed | Discrepancies | Not reproduced |
|---|---|---|---|---|---|---|---|
| P40 | 2017, ASCE J. Eng. Mech. | Type1/CFF glyph placeholders in Eq. (9) text | Propagation buckling of pipe-in-pipe (closed form + work balance) | PUBLISHED Eqs. 2/3/6/9; INDEPENDENT work balance | Wrong DOI/year accepted at intake; grouped equation references lost | 1 OPEN (PUBLISHED_REFERENCE_MISMATCH), 1 human DEFERRED decision | Source FE model; RST and FE reference populations not re-derived |
| P41 | 2011, ASME OMAE | Punctuation-free ASME captions | PiP axial load sharing, bonding, global buckling | PUBLISHED Eqs. 6–10, 14; INDEPENDENT geometry/EA/EI | Captions not anchored (dev5) | 2 OPEN (force balance; paragraph-vs-axis unit) | Global-buckling FE response |
| P42 | 2019, Elsevier Marine Structures | Split captions | Unbonded flexible pipe, helical armour tension–bending | PUBLISHED analytical families; model-form comparison with FP-RUC | False year conflict from received/copyright dates | 1 OBSERVED (model form), 1 OPEN (implementation provenance) | FP-RUC FE; Figure 16 moment chain |
| P43 | 1976, J. Petroleum Technology (SPE-5620-PA) | not recorded | Variable-tension riser eigenproblem | PUBLISHED Table 1/2; INDEPENDENT Hermite-FE eigen-solution (175 eigenvalues) | DOI recorded PENDING and SPE number recorded as 5820 in error (corrected manually) | 2 OPEN (printed eigenvalues vs internal consistency) | Source power-series recursion |
| P44 | 1994, SPE 28723 conference | not recorded | Quasi-static nonlinear drillstring–riser contact | PUBLISHED Eq. 1; INDEPENDENT section properties, penalty scale | DOI recorded PENDING (completed manually; historical alias 10.2523/28723-MS); ingested through the pipeline, readiness PARTIAL 4/7, no structure extraction run (ingestion summary, 28 Sep 2026) | 1 OPEN (paragraph vs caption time labels) | Full nonlinear FE contact profiles |
| P45 | 1983, Applied Ocean Research | 300 dpi bilevel scan with OCR layer | Nonlinear dynamic riser analysis (geometric stiffness, θ-Wilson integration, Morison loading) | PUBLISHED Appendix 1/2, Eq. 7; INDEPENDENT FE, rigid-body, stability, graphical measurement | Readiness PARTIAL 4/16; Eq. (11), sub-figures, appendices missed; DOI not in source | 6 OPEN (inconsistency, magnitude, unit, typography, convention, claim definition) | All dynamic responses (BLOCKED) |

What the set stress-tests well:
- **Eras and formats:** 1976–2019, four publishers/societies (ASCE, ASME, Elsevier, SPE), born-digital sources with font artefacts and a scanned 1983 source.
- **Mechanics:** static collapse, axial load sharing, helical-armour bending, an eigenproblem, quasi-static nonlinear contact and nonlinear time integration. The formulations are genuinely different, not variations of one equation.
- **Independent-check types:** analytical reconstruction (P40), numerical re-formulation (P43, P45), matrix-property checks (P45), graphical measurement against boundary conditions (P45).
- **Discrepancy types:** ten distinct legacy labels over 14 records (seven proposed taxonomy categories), including several found only by cross-checking tables against equations (P41, P43) or against physics (P45-D001, D002).
- **Incomplete reproduction:** four of six studies have a major target that is legitimately not reproducible from source detail.
- **Runtime behaviour:** a real mutation defect was found, inventoried and fixed; recomputation noise across NumPy builds is quantified and classified.

What it does not stress-test:
- **Domain:** a single domain (offshore/subsea structural mechanics), so generality beyond it is out of scope (PA-27).
- **Experimental evidence:** not handled as a separate population within P40–P45. The repository has one MODEL_VS_EXPERIMENT_GAP record (P38-D002), outside the six cases (G5 optional).
- **SOLVER_NEW evidence:** none (PA-25).
- **Extraction accuracy:** not measured (PA-05).
- **Organisational independence:** the checks are methodologically independent only (PA-10).

## 4. Failure register (failures of the framework, not of the sources)

| # | Failure | Found in | Response | Reference |
|---|---|---|---|---|
| F1 | Incorrect DOI/year accepted at intake | P40 | Source-identity audit; mandatory re-audit after metadata repair | `PROGRESS_v0.2.0.md` dev2; `HANDOVER_CURRENT.md` |
| F2 | Type1/CFF glyph placeholders in extracted equation text | P40 | Visual source review required before PUBLISHED implementation | `HANDOVER_CURRENT.md` |
| F3 | Grouped equation references (“Eqs. (2), (3), (6), and (9)”) lost | P40 | Grouped-reference recovery | `PROGRESS_v0.2.0.md` dev2 |
| F4 | Punctuation-free publisher captions not anchored | P41 | Broadened caption recognition | `PUBLISHER_STYLE_EXTRACTION_v0.2.0-dev6.md` |
| F5 | Numeric table mismatch initially indistinguishable from transcription error | P41 | Held as transcription uncertainty until visual confirmation | `CHAT_COMPACT_CURRENT.md` P41 |
| F6 | Received/copyright year raised a false identity conflict | P42 | Publication vs secondary year semantics | `SOURCE_IDENTITY_AND_SPLIT_CAPTIONS_v0.2.0-dev7.md` |
| F7 | Split captions not recognised | P42 | Split-caption anchors | same |
| F8 | Literal implementation of published equations does not close against a figure | P42 | Classified as implementation-provenance gap, not source error | `S(P42)` P42-D002 |
| F9 | Windows verification batches stopped silently (missing `call`) | P42 | `call` rule for all batch chaining | `HANDOVER_CURRENT.md` |
| F10 | Verification and tests rewrote 20 tracked evidence files | runtime | Non-mutating verification (D-005) | `docs/MUTATION_INVENTORY_v0.2.0.md` |
| F11 | Provenance hashes depended on checkout line endings | runtime | Canonical `text/lf-v1` identity | same |
| F12 | Study verification contract drifted from its tests | P41 | Contract fixed; drift made visible by verification | PR #3 commit `7a788ae` |
| F13 | Continuity test hard-coded a historical checkpoint | runtime | Durable invariants | PR #2 |
| F14 | Eigen-solution differs ~1e-8 across NumPy/BLAS builds | P43 | Declared recomputation tolerance + published-precision guard | `S(P43).verification_tolerance` |
| F15 | Comparator blind to deleted artifacts; `platform` treated as environment | runtime (review) | Structural changes material; `platform` removed | PR #3 commit `15f0c78` |
| F16 | Automated readiness PARTIAL on a scanned source | P45 | Manual page-image review, recorded in the manifest | `S(P45).target_review` |
| F17 | graph-sync persists per-run counters | runtime | Recorded as low-priority hardening | WORK_QUEUE Q7 |
| F18 | Source identity recorded incompletely or wrongly (P43/P44 DOI PENDING; P43 SPE number 5820 instead of 5620); ingestion records missing | P43, P44 (P40) | Identity corrected from publisher records (27 Sep 2026); tracked ingestion summaries for all six cases (28 Sep 2026, G3 closed) | `S(P43)`, `S(P44)`, `papers/P43/SOURCE.md` |
| F19 | Generated packaging metadata tracked in Git | runtime | Untracked | PR #4 |
| F20 | Frozen P45 evidence was not recomputation-equivalent across NumPy/BLAS builds under the default tolerance: the ill-conditioned independent FE check changes by ≤ 2.9e-7 abs. CI missed this because `verify-all` covers only live studies, and the earlier “NUMERICAL_NONMATERIAL under NumPy 2.5.3” statement was wrong. | P45 (cross-OS CI) | CI verifies every study (`environment-record`); path-scoped recomputation tolerance on the FE block only, with the engineering boolean still compared exactly (D-007, approved 28 Sep 2026) | `docs/CROSS_ENVIRONMENT_VERIFICATION.md` |
| F21 | Provenance manifests are platform-dependent: hashes of non-materially changed CSVs, and OS path separators in keys, made P38 fail on Windows/macOS | P38 (cross-OS CI) | Provenance-hash inheritance and separator-rendering rules (D-007, approved 28 Sep 2026); runner fix deferred to the next approved regeneration | same |
| F22 | The Windows dispatcher `engiproof.cmd` expanded `%errorlevel%` inside a parenthesised block, so it returned 0 for every command whenever `.venv` existed. `call engiproof … / if errorlevel 1 goto :fail` in the Windows batches therefore never stopped on an EngiProof failure. Earlier “VERIFY PASS” banners certified the `python -m unittest` steps, but not the `engiproof verify` steps. Found when `29_RECORD_INGESTION_SUMMARIES_WINDOWS.bat` continued past `invalid choice` errors. | runtime (Windows, owner's run) | Dispatcher fixed; Windows CI asserts that a failing command returns non-zero. The cross-OS CI verification (F20/F21) now covers what the local banners did not. P45 Windows verification was re-run after the fix and passed (28 Sep 2026, D-006 addendum). | `engiproof.cmd`, `.github/workflows/ci.yml` |

These failures are themselves Paper A evidence: each was surfaced by the evidence process, recorded, and either corrected or left visible.

## 5. Gaps (detail in `PAPER_A_GAPS.md`)

| Gap | Missing claim | Category | Blocks submission? |
|---|---|---|---|
| G1 | Human decision boundary exercised beyond a single DEFERRED decision | a — human decisions on existing records | Recommended |
| G2 | Controlled discrepancy vocabulary applied consistently | b — runtime/method | Yes (Table A2 depends on it) |
| G3 | Tracked, text-free ingestion summaries and source-format / audit-outcome records for all six cases | b | Yes (extraction claims otherwise rest on prose) |
| G4 | Cross-OS reproducibility recorded as artifacts | b — runtime/CI | Recommended |
| G5 | Experimental data handled as a distinct evidence population | c — deeper use of P40 | Optional; needed only if the claim is kept |

Not gaps (scope statements for the manuscript):
- SOLVER_NEW is reserved, and would be exercised later through solver adapters on existing cases.
- Generality is limited to the offshore/subsea domain.
- There is no extraction-accuracy benchmark.
- Independence is methodological, not organisational.
- Autonomous discovery is not claimed.

Housekeeping (not evidence gaps):
- H1: graph-sync file idempotency (Q7).
- H2: record non-reproduced targets of P41/P42/P44 as BLOCKED comparisons, as P45 does.
- H3: flatten the nested LaTeX path.
- H4: the manuscript Draft v0.1 covers P40–P41 only.

## 6. Is P46 required?

**No.** Every gap has a route that needs no new source:
- **G1** needs reviewer decisions on existing discrepancy records.
- **G2–G4** need runtime or method work.
- **G5** can use the hyperbaric-chamber data already in P40 Table 2.

A single additional paper could not supply the claims that are out of scope: domain generality and extraction accuracy need corpora, not one case, and organisational independence needs external replicators. A P46 would add volume without closing a defined gap. Revisit only if the manuscript decides to claim something that P40–P45 cannot support in principle.

## 7. Decision gate

**B — Paper A needs specific runtime/method work, but no P46.**

G5 is a C-type item (deeper use of P40). It is recommended but not blocking.

## 8. Next highest-value action

Update, 28 September 2026: G1–G4 are closed. D-007 and the taxonomy were approved and the G1 decisions recorded (D-008). Machine-generated ingestion summaries now cover all six cases (from the owner's local run), and a Windows dispatcher defect was found and fixed (F22). Next: merge PR #8, then finalise the manuscript in PR #9 (rebase, regenerate Appendix A, related-work references, rebuild). G5 is optional; there is no P46.

Contextual literature, including the ScientistTwo / Chain-of-Evidence direction, belongs in related work as architectural context only. It is not engineering validation evidence and does not replace P40–P45.
