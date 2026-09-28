# EngiProof — Current Handover

Updated: 27 September 2026  
Development line: `v0.2.0-dev8`  
Primary branch: `develop`

## Current objective

Build **Paper Ingestion & Evidence Automation** so that EngiProof can move from a fingerprinted paper source to source-bounded engineering evidence without silently promoting extraction artifacts into verified results.

```text
paper source
  -> fingerprint
  -> source identity audit
  -> target discovery
  -> missing-equation recovery
  -> source enrichment
  -> structure extraction
  -> selected-target readiness gate
  -> DRAFT study scaffold/tasks/templates
  -> reproduction
  -> independent check
  -> comparison/discrepancy
  -> evidence graph
  -> callable engineering method
  -> live registry only after gates
```

## Stable baseline

`v0.1.1` remains the released evidence-runtime baseline with live studies P08/P12/P16/P29/P36/P38. Existing evidence status and qualification boundaries must remain backward compatible.

## v0.2.0-dev2 implemented

- grouped equation-reference discovery, including forms such as `Eqs. (2), (3), (6), and (9)`;
- printed-equation-number recovery, including common Type1/CFF `ð9Þ` extraction artifacts;
- multiline equation-block reconstruction candidates;
- equation recovery that appends missing candidates while preserving existing target IDs;
- true-caption anchored table blocks with header/data/footnote candidates;
- selected-target structural readiness gate (`READY` / `PARTIAL` / `BLOCKED`);
- source identity audit for fingerprint/title/DOI/year consistency;
- metadata repair command that preserves the source SHA-256 and target IDs, then requires re-audit;
- promotion gate now blocks source-identity conflicts and structurally unready selected targets;
- `fonttools` dependency added to reduce CFF/Type1 PDF decoding warnings;
- pipeline exposes source-identity and selected-target-readiness stages.

## Active real-source case — P40

Title: `Propagation Buckling in Subsea Pipe-in-Pipe Systems`  
Canonical basename: `p40-karampour2017.pdf`  
Source SHA-256: `e83902ba46b8e713ddf2f11f5953bdf318ac539f6701ff303651e28d3d5e28bb`  
Selected targets: `Table 2`, `Table 1`, `Equation (9)`  
Evidence status: `DRAFT`  
Live registry: **NO**

### Critical source-identity blocker

The previously entered metadata (`2013`, DOI `10.1016/j.tws.2013.07.003`) does **not** match the P40 source/title. The paper source is a 2017 *Journal of Engineering Mechanics* paper with DOI `10.1061/(ASCE)EM.1943-7889.0001337`.

Do not start P40 reproduction until the local dev2 `audit-source` passes after metadata repair.

### P40 resume sequence

Use the existing local P40 intake/scaffold; do **not** delete it.

```bat
engiproof set-metadata P40 --doi "10.1061/(ASCE)EM.1943-7889.0001337" --year 2017
engiproof audit-source P40 "<local source PDF>"
engiproof recover-equations P40 "<local source PDF>"
engiproof enrich P40 "<local source PDF>"
engiproof extract-structures P40 "<local source PDF>"
engiproof readiness P40
engiproof comparison-templates P40
engiproof pipeline P40
```

Expected dev2 improvement: Eq. (9) should obtain an equation-body candidate; references to Eqs. (2), (3), (6), and (9) should be represented in the candidate set; Table 1/2 should expose caption-anchored data-row candidates. Review is still required before reproduction.

## Next engineering work after dev2 verification

1. Verify dev2 against the user's exact P40 PDF and inspect recovered Eq. (9), Table 1, Table 2.
2. If selected-target readiness is `READY`, implement P40 Table 1 -> Eq. (9) -> Table 2 source-bounded reproduction.
3. Add independent checks: Eq. (9) limiting case to Eq. (6), dimensional/sign checks, and independent arithmetic.
4. Compare analytical results with Table 2 hyperbaric/RST/FE reference populations and record discrepancies without tuning.
5. Add P40 tests, callable method(s), evidence graph nodes and explicit evidence status only after source review.

## Non-negotiable rules

- Candidate extraction is not evidence.
- Code execution is not verification.
- Verification is not engineering qualification.
- Never tune unknown inputs to force agreement.
- Preserve `PUBLISHED`, `INDEPENDENT`, `SOLVER_NEW` separation.
- Do not redistribute source PDFs/raster extracts.
- Do not persist absolute paths, usernames, machine names or drive-specific project locations.
- **Update this `HANDOVER_CURRENT.md` at every meaningful development checkpoint before handing work to another chat, Codex session, or developer.**

## Chat continuity / compaction protocol

Use two layers of durable context from v0.2.0 onward:

1. `HANDOVER_CURRENT.md` — authoritative engineering/development handover. Update it at every meaningful checkpoint.
2. `CHAT_COMPACT_CURRENT.md` — short continuation context for a fresh ChatGPT/Codex session.

When the conversation becomes long, do not wait for context loss. At each major checkpoint:
- refresh both files;
- keep the compact file short enough to paste/read quickly;
- record only current state, accepted decisions, blockers, exact next work and resume commands;
- leave detailed history in Git, progress records and evidence artifacts rather than repeating it in chat.

A new chat should start by reading `AGENTS.md`, `ROADMAP_v0.2.0.md`, `PROGRESS_v0.2.0.md`, `HANDOVER_CURRENT.md`, and `CHAT_COMPACT_CURRENT.md`, then verifying the actual repository state before continuing.

The platform may still eventually require a new conversation; these files make that a controlled handover rather than a restart.

## Checkpoint — P40 selected-target readiness achieved

Date: 26 September 2026

P40 dev2 structure extraction now reports:

- `equation_count = 21`
- `table_count = 3`
- `figure_count = 33`
- `definition_count = 4`
- `selected_target_readiness = READY`

Selected targets:
- `Table 2` — READY; 3 data-row candidates under true table caption
- `Table 1` — READY; 3 data-row candidates under true table caption
- `Equation (9)` — READY; equation body candidate extracted

This closes the dev2 robust-ingestion objective for the selected P40 targets. The next engineering stage is source-bounded reproduction, not more discovery work.

Immediate next actions:
1. Generate comparison templates for P40.
2. Export the updated dev2 `structure_candidates.json`.
3. Review the extracted Table 1 rows, Eq. (9) body and Table 2 rows against the source before coding.
4. Implement deterministic published-method reproduction.
5. Add independent checks (Eq. 9 -> Eq. 6 limiting case, dimensional/sign checks where supported).
6. Populate comparison/discrepancy records and tests before any promotion.

Do not promote P40 while it remains `DRAFT` or before reproduction/tests/callable tools are present.

## Checkpoint — P40 dev2 source-structure review

The updated `P40_structures_dev2.json` recovers 21 equation candidates and true-caption table blocks for Tables 1 and 2.

Important result:
- Eq. (2), Eq. (3), and Eq. (6) reproduce the published Table 2 ratios to rounding for all three PIP cases.
- An independent algebraic reconstruction of Eq. (9) from extracted Eq. (8a–d) reproduces the published Table 2 Eq. (9) ratios for PIP-1 and PIP-2, but gives about `0.705` for PIP-3 versus published `0.66`.
- This is now an OPEN discrepancy/review item. Do not tune parameters.
- Direct Eq. (9) extracted text still contains Type1/CFF glyph placeholders, so the printed equation must be visually source-reviewed before implementation as `PUBLISHED`.

Next: visually confirm Eq. (9), Table 1 column meanings and Table 2 PIP-3 column/value in the original PDF; then implement the source-bounded P40 reproduction and independent check.

## Publication track

Paper A is active as a living methods/evidence manuscript under `publication/PAPER_A_ENGIPROOF/` when the publication checkpoint patch is applied. Engineering evidence controls manuscript wording; during v0.2.0 proof-of-concept, keep the effort roughly 85% engineering / 15% evidence capture. Paper B (P40 mechanics) remains parked until the P40 engineering chain is sufficiently deep.

## Checkpoint — P40 deterministic reproduction implemented

Date: 26 September 2026

Source review:
- title/year/DOI confirmed for the 2017 Journal of Engineering Mechanics paper;
- selected source targets confirmed from the public accepted-manuscript source text and the fingerprinted local extraction;
- published Eq. (9) transcription implemented explicitly.

P40 now contains:
- machine-readable Table 1 inputs;
- Table 2 reference ratios;
- published Eqs. (2), (3), (6), and (9);
- independent work-balance reconstruction from Eqs. (8a-d);
- deterministic `table2_reproduction.csv`;
- callable methods;
- evidence graph;
- five automated P40 tests;
- explicit `P40-D001` OPEN discrepancy.

Numerical outcome:
- Eq. (2), Eq. (3), and Eq. (6) reproduce the Table 2 normalized ratios within the source two-decimal precision.
- Eq. (9) reproduces PIP-1 and PIP-2 to rounding.
- PIP-3 Eq. (9) gives `0.705666` versus Table 2 `0.66`, a `0.045666` absolute ratio difference (~`6.92%` relative to 0.66).
- The independent Eq. (8a-d) work-balance reconstruction agrees with direct Eq. (9) within `0.1%`, so the PIP-3 mismatch is retained as an OPEN source/comparison discrepancy; no tuning is allowed.

Validation:
- full repository test discovery: `49 tests PASS`;
- `engiproof verify P40`: `PASS_SOURCE_EXTERNAL / CONDITIONAL`;
- existing live-study `engiproof verify-all`: `PASS`;
- P40 promotion gate is technically `ready=true`, but live-registry promotion is intentionally deferred for user review of the open discrepancy.

Next highest-value work:
1. apply/run the P40 reproduction patch locally against the exact fingerprinted source;
2. review P40-D001 and decide whether to promote P40 as `CONDITIONAL`;
3. add generic discrepancy classification/escalation automation only after P40 review;
4. then test the ingestion-to-evidence chain on a second heterogeneous paper.

## Checkpoint — v0.2.0-dev3 generic discrepancy automation

Decision implemented: build generic discrepancy classification/escalation before P40 promotion. P40-D001 is `PUBLISHED_REFERENCE_MISMATCH`, HIGH, `BLOCK_PROMOTION`; reproduced Eq. (9) and the independent work-balance agree while Table 2 reports 0.66. Existing live CONDITIONAL studies are not retroactively demoted. Next after local dev3 verification: documented human decision/acceptance workflow, then evidence-graph auto-expansion.
## Checkpoint — v0.2.0-dev4 human discrepancy decisions

Implemented append-only human review for discrepancy blockers. P40-D001 remains unresolved and promotion-blocking until an authorized human records `RESOLVED`, `BOUNDED`, or `ACCEPTED_WITH_RATIONALE` with substantive rationale and evidence references. `DEFERRED` remains blocking.

A discrepancy decision may alter the promotion gate but never grants engineering qualification. Do not close an item solely to make the gate pass.

Next: run dev4 locally; review P40-D001 evidence; if sufficient, user records an explicit decision. Then reevaluate promotion and continue evidence-graph auto-expansion / second heterogeneous paper.

## Checkpoint — v0.2.0-dev5 evidence-graph auto-expansion

Implemented generic additive/idempotent evidence-graph synchronization and provenance coverage auditing. The graph now represents callable methods, comparisons, discrepancies, generic assessments and append-only human decisions. Existing hand-authored graph nodes/edges are preserved.

P40 remains `CONDITIONAL`, `NOT_GRANTED`, and promotion-blocked while the latest P40-D001 decision is `DEFERRED`. Running `graph-sync P40` should add the decision node without changing that gate state.

Next engineering priority: validate dev5 locally, then start a second heterogeneous ingestion-generated case to test whether the v0.2.0 pipeline generalizes beyond P40. Do not spend time polishing the manuscript before the second end-to-end case.

## Checkpoint — v0.2.0-dev6 triggered by P41

P41 successfully localized all 26 discovered targets, confirming broad source discovery. Its ASME format then exposed a generalization defect: clear captions (`Table 1 Pipeline data`, `Table 2 Axial stiffness and distribution of forces`, `Table 3 Cases analysed`, `Figure 4 - ...`) were not recognized as true caption anchors because dev5 expected punctuation patterns closer to journal PDFs.

Dev6 fixes publisher-style caption recognition and engineering parameter/unit/value table rows before any P41 scaffold is created.

Recommended first P41 engineering chain after dev6 re-extraction:
- T001 Table 1 — geometry/material input;
- T002 Table 2 — axial stiffness and force distribution;
- T024 Eq. (6) — inner-pipe share of soil-friction force increment;
- T025 Eq. (7) — outer-pipe share;
- T026 Eq. (8) — total force increment identity.

Second phase:
- T003 Table 3 + T018 Eq. (9) for partial/full axial bonding criteria and end-expansion cases.

Do not claim the apparent Table 2 inner-force value mismatch until the source table is visually checked; PDF text extraction may have misread the number.


## Checkpoint — P41 first reproduction

P41 has completed its first source-bounded reproduction chain:

`Table 1 -> independent area/EA -> Table 2 -> Eqs. (6)-(8)`.

Key results:
- inner area `0.0127252174 m²` vs Table 2 `0.012725`;
- outer area `0.0240543896 m²` vs `0.024054`;
- inner EA `2.532318261e9 N` vs `2.532e9`;
- outer EA `4.979258637e9 N` vs `4.979e9`;
- Eq. (6) inner share `158.7845 N/m`;
- Eq. (7) outer share `312.2155 N/m`;
- Eq. (8) total `471.0 N/m`.

The extracted Table 2 inner force increment reads `153 N/m`; this is **not** yet classified as a paper mismatch. It is `SOURCE_TRANSCRIPTION_UNCERTAINTY` and blocks promotion until the original PDF cell is visually confirmed. The outer value `312 N/m` agrees to rounding.

P41 verify status: `PASS_SOURCE_EXTERNAL / CONDITIONAL`; graph audit: `PASS`, coverage `1.0`; qualification `NOT_GRANTED`; live registry unchanged.

Next: visually confirm Table 2 inner `ΔS`. Then proceed to Table 3 + Eq. (9) bonding/end-expansion reproduction.

## Checkpoint — P41 Phase 2 axial bonding

Visual source review confirms P41 Table 2 reports fS=471 N/m, inner ΔS=153 N/m, outer ΔS=312 N/m. P41-D001 is now a source-backed `PUBLISHED_REFERENCE_MISMATCH`, not extraction uncertainty. The possible 153->159 typo remains unconfirmed.

Eq. (9) requires about 158.78 N/m internal friction for full bonding when gamma_f=1.0 for the paper's illustrative Table 3 classification. This reproduces Table 3 cases as NO_FRICTION / PARTIAL_BONDING / FULL_BONDING / FULL_BONDING. The paper's dry-friction model also reproduces 1195*0.3=358.5 N/m versus rounded 358 N/m.

Eq. (10) is callable, but direct reproduction of the 1.305 m full-bonding end expansion remains conditional because S0_total cannot be independently reconstructed from explicit source inputs without assumptions.

Next after local verification: sync/audit P41 graph, then proceed either to global-buckling response (Figures 8-10 / Eq.14) or to a third heterogeneous paper.


## Checkpoint — P41 Phase 3 global buckling / Eq.14

P41 Phase 3 is the stop point for this case. Figures 8–10 are retained as source-bounded observations only; no curve digitization or FE recreation is claimed. Independent Table 1 elastic bending stiffness gives outer/inner EI ≈ 3.3966. Eq. (14) is callable.

New P41-D002: source paragraph says ~300/850 MNm while Figure 10 axis is Moment [kNm] on a 0–1000 scale. OPEN PUBLISHED_REFERENCE_MISMATCH, BLOCK_PROMOTION. Do not silently correct.

After local verification: graph-sync/audit P41, freeze P41, then move to a third mechanically different paper.

## Checkpoint — P41 Phase 3 accepted and frozen

Local evidence uploaded after Phase 3 verification confirms:

- `phase3_global_buckling_summary` produced independent bending-stiffness results:
  - `EI_inner = 2.56400785e7 N m^2`
  - `EI_outer = 8.70887896e7 N m^2`
  - `EI_outer/EI_inner = 3.396588258`
- Eq. (14) scaling check is present (`gamma_C=0.8 -> factor 0.8` for `gamma_f=1`).
- P41 discrepancy audit contains two OPEN, HIGH-priority, promotion-blocking `PUBLISHED_REFERENCE_MISMATCH` records:
  - `P41-D001`: Table 2 force-split mismatch.
  - `P41-D002`: Figure 10 paragraph units `MNm` versus plotted axis `kNm`.
- Pipeline status: `16/17` stages complete, `progress_fraction=0.941176...`, `evidence_status=CONDITIONAL`.
- Only `live_registry` remains incomplete, which is intentional because unresolved discrepancies block promotion.
- Evidence graph audit: `PASS`, `25/25` represented items, `coverage_fraction=1.0`, `issues=[]`.
- Qualification remains `NOT_GRANTED`.

Interpretation:
P41 Phase 3 is accepted as a completed CONDITIONAL evidence case and is now frozen. The absence of live-registry promotion is expected and is not a Phase 3 failure.

Next:
start P42 immediately using a materially different mechanics/evidence class. Do not add more P41 infrastructure unless a later cross-paper requirement justifies it.

## Checkpoint — v0.2.0-dev7 triggered by P42

P42 source identity is not genuinely conflicted. The source first page contains the configured DOI and title, received/revised/accepted dates in 2018, copyright 2018, and the bibliographic citation `Marine Structures 64 (2019) 401–420`. Therefore 2019 is the publication year.

Dev7 fixes the generic identity audit to distinguish publication-year evidence from received/accepted/copyright dates.

P42 also exposed split Elsevier captions:
`Table 1` on one line followed by `Geometric parameters ...` on the next. Dev7 adds generic split/multiline caption recognition.

After applying dev7:
1. rerun `audit-source P42` — expected year/title/DOI MATCH and status PASS;
2. rerun `extract-structures P42` — Tables 1, 3, 4 should have true caption anchors/data blocks;
3. scaffold Phase 1 with `T006,T008,T009,T066,T067`;
4. keep Figure 16 as a source-reviewed comparison target outside the initial readiness gate;
5. proceed to P42 reproduction.

## Checkpoint — P42 Phase 2 analytical stress / kinematics

Phase 2 implements PUBLISHED Eqs. (31)-(35) as callable stick/slip functions and regenerates the analytical Eqs. (36)-(39) stress families used in Figures 20-23.

Source-bounded independent geometry gives lay angles about 24.909° / 24.940°. At kappa_G=0.06 1/m, analytical amplitudes are ~84.095/84.103 MPa transverse and ~21.315/21.294 MPa normal for inner/outer armor.

P42-D001 is OBSERVED `MODEL_FORM_KINEMATICS_DIFFERENCE`: analytical Eqs.36-39 are independent of Fz, while published FP-RUC Figures21/23 vary with Fz. This is not classified as a paper error; the source attributes it to sliding interaction and different wire-path kinematics.

FP-RUC point clouds remain undigitized/unreproduced. No tuning.

Next after local verification: graph sync/audit. Then either implement Eq.41 + fuller Figure16 analytical moment or move to another heterogeneous paper.

## Checkpoint — P42 Phase 3 / freeze point

Final bounded P42 extension completed:
- Eqs.24-26 two-layer axisymmetric solver with exact axial-force/torsion closure;
- Eqs.27-30 explicit nominal/local contact-pressure functions;
- Eq.41 tensile-armor moment callable;
- Eqs.41-43 literal Figure16 analytical probe.

The axisymmetric chain closes and is consistent with Figs.12-14 trends. The literal contact-pressure recursion + Eq.41 does not reconcile with the published Figure16 high-tension scale. No inputs are tuned.

Recorded `P42-D002 = SOURCE_IMPLEMENTATION_PROVENANCE_GAP`, OPEN/REVIEW_REQUIRED, explicitly not a paper error.

After local verification and graph-sync/audit, freeze P42 and move to P43.

## Windows batch chaining rule — discovered during P42 Phase 3

The repository provides `engiproof.cmd` as the Windows dispatcher. When an EngiProof command is invoked **inside another `.bat`/`.cmd` file**, it must be prefixed with `call`.

Correct:
`call engiproof graph-sync P42`

Incorrect inside a batch file:
`engiproof graph-sync P42`

Without `call`, Windows transfers control to `engiproof.cmd` and does not return to the parent verification batch. This explains why the original `22_VERIFY_P42_PHASE3_WINDOWS.bat` stopped after `engiproof tool ...` and never printed its final PASS marker.

Apply this rule to all future Windows verification/automation batches.

## Checkpoint — P42 frozen and three-layer continuity architecture started

P42 Phase 3 local verification completed with `=== P42 PHASE3 VERIFY PASS ===`.
P42 is frozen CONDITIONAL/NOT_GRANTED with P42-D001/P42-D002 preserved and no tuning.

v0.2.0-dev8 introduces the three-layer continuity architecture:
1. repository source of truth;
2. durable continuity control plane;
3. replaceable conversation/session context.

New controls: PROJECT_STATE, queue, blockers, decisions, bootstrap, architecture document and root AGENTS.
New commands: `engiproof continuity-audit`, `engiproof checkpoint`, `engiproof checkpoint --bundle`.

After local dev8 verification: commit/push, copy checkpoint bundle to private cloud, then start P43.

## Checkpoint — P43 Phase 1 eigenvalue benchmark implemented

P43 source: Dareing & Huang (1976), `Natural Frequencies of Marine Drilling Risers`, SHA-256 `4ab7c3b9a8377cc3d5a7f5eecb64712496aa825f969760e47ee17ccba03ffccf`.

Phase 1 implements:
- source dimensionless alpha/beta definitions;
- independent cubic-Hermite FE weak solution of Eq. (8);
- Eq. (10) approximate eigenvalue;
- natural-frequency/period conversion;
- selected Table 1 and Table 2 comparisons;
- Figure 6 first-mode inflection-location check.

The independent FE method intentionally differs from the source Eq. (9) power-series implementation, whose coefficient details are referred to earlier papers rather than repeated in P43.

Selected benchmark results:
- alpha=50, beta=100, lambda1..5 independently reproduce Table 1 to source 3-decimal precision;
- Eq. (10) errors reproduce Table 2 rounding;
- worked example reproduces about 0.815 rad/s, 7.71 s exact and 7.68 s approximate;
- alpha=250, beta=100 first-mode inflection is independently found about 0.09 below the top, consistent with the source's approximately 0.1 statement.

No source figure digitization. Qualification remains NOT_GRANTED.

## Checkpoint — P43 Phase 2 full matrix implemented

P43 Phase 1 local verification PASS.

Phase 2 expands to the complete Table 1 and Table 2 alpha-beta grids: 35 Table 1 rows / 175 eigenvalue cells, the full Eq.10 error matrix, Figures 4-5 parameter families, and independent first three mode shapes for Figure 6.

All ordinary Table1 eigenvalues reproduce to source rounding with the independent Eq8 Hermite-FE solution.

`P43-D001`: Table1 at alpha=0, beta=200 visibly prints lambda5=13.221. Independent Eq8 FE and Eq10 both give approximately 18.221, while Table2 reports zero approximation error at alpha=0. Classified `PUBLISHED_REFERENCE_MISMATCH`, OPEN/BLOCK_PROMOTION. The likely correction 18.221 is inference only and is not substituted into the published record.

After local Phase2 PASS: freeze P43 CONDITIONAL, update checkpoint bundle, then move to P44.

P43-D002: Table 1 alpha=200, beta=100, lambda1 is visibly printed as 6.554. Independent Eq.8 FE gives ~6.654; Eq.10/Table2 internal consistency also supports 6.654. Preserve printed 6.554; inferred correction is not applied.

## Checkpoint — P44 Phase 1 contact validation implemented

P44 source: Bueno & Morooka (1994), SPE 28723, `Analysis Method for Contact Forces Between Drillstring-Well-Riser`, SHA-256 `ca8b476b5f6c54f8a2a3c55c7836770ef55bc27d3cf05b8c6f4a953ca896b80b`.

Phase 1 covers source-bounded drillstring/well/riser contact evidence:
- Table1 drillpipe geometry independently reconstructs area and second moment;
- Eq1 equilibrium reproduces the published 429.098 lb arithmetic and independently gives 429.111 lb using exact sin60, matching the published FEM value 429.11 lb;
- 5.8 s / 10-slice discretization independently gives 0.58 s;
- K1=1e6 lbf/ft gives ~0.00515 in penetration at the reference 429.11 lb force;
- Figures7/8 are source-reviewed without digitization.

P44-D001 is OPEN `SOURCE_FIGURE_TEXT_MISMATCH`: the paragraph says Figures7/8 correspond to 4.06 s and 2.32 s, while captions say 0.58 s and 1.74 s; Figure2 also uses 0.58/1.74 s. No intended pair is inferred.

Full nonlinear contact-force profiles are not claimed reproduced because essential wall/riser geometry and implementation data are not fully supplied. Qualification NOT_GRANTED.

## Checkpoint — P44 frozen / low-budget continuity hold

User confirmed local `=== P44 PHASE1 VERIFY PASS ===`.

P44 is frozen as `FROZEN_CONDITIONAL_EVIDENCE_CASE`.
`P44-D001` remains preserved. Full nonlinear FE contact profiles remain not reproduced because the source is insufficient to reconstruct the full time-dependent contact model without unsupported assumptions.

Weekly model budget is nearly exhausted. Before pausing:
1. run `engiproof continuity-audit`;
2. run `engiproof checkpoint --bundle`;
3. archive the bundle privately;
4. commit/push the freeze/control-file changes.

After reset, resume directly at P45 using `NEW_CHAT_BOOTSTRAP.md`, `PROJECT_STATE.json`, and this handover.


## Checkpoint — post-dev8 runtime changes (PR #2–#4)

- PR #2: read-only MCP server (`engiproof-mcp`); tool-level `evidence_boundary` passed through `invoke_tool`; durable continuity-test invariants.
- PR #3: non-mutating verification (D-005). `verify`, `verify-all`, `run` recompute in a sandbox and classify regenerated artifacts (IDENTICAL, BYTE_ONLY, ENVIRONMENT_METADATA, NUMERICAL_NONMATERIAL pass; NUMERICAL_MATERIAL, MATERIAL_NON_NUMERIC fail). `engiproof regenerate Pxx` is the only evidence-rewriting operation and is not exposed through MCP. P43 declares a recomputation tolerance with a 3-decimal Table 1 guard. P41 verification-contract drift fixed.
- PR #4: generated `*.egg-info` untracked.

## Checkpoint — P45 Phase 1 nonlinear dynamic riser evidence

Safai (1983), Applied Ocean Research 5(4) 215–225. Ingestion ran on the 1983 scan: 32 candidates, readiness PARTIAL (4/16); all figures/appendices reviewed manually from page images. Source-bounded checks of Tables 1–3, Appendix 1 (stiffness functions, K, K_G), Eq. (7), Appendix 2, Airy regime; head-end envelopes of Figures 4(a)–9(a) digitized (numbers only). Six OPEN discrepancies P45-D001…D006 preserved without tuning. Nonlinear dynamic responses BLOCKED (source insufficient). No SOLVER_NEW. CONDITIONAL / NOT_GRANTED / outside live registry. Details: `P45_PHASE1_NONLINEAR_DYNAMICS_CHECKPOINT.md`.

Next: run `28_VERIFY_P45_PHASE1_WINDOWS.bat` locally; on PASS record it as `last_green_verification` and freeze P45. Then the Paper A readiness review (P40–P45) decides whether P46 exists.

## Checkpoint — P45 frozen (27 September 2026)

Local Windows `28_VERIFY_P45_PHASE1_WINDOWS.bat` PASS after PR #5 merged (`cb2a595`); continuity-audit PASS; checkpoint bundle PASS. P45 frozen CONDITIONAL / NOT_GRANTED (D-006); P45-D001…D006 OPEN; dynamic responses BLOCKED; no tuning.

Active task: Paper A readiness review across P40–P45 (WORK_QUEUE Q6). Create P46 only if the review demonstrates a specific evidence gap. Low-priority runtime item: graph-sync persists per-run counters, so repeated syncs rewrite the tracked graph without changing evidence (Q7).

## Checkpoint — Paper A evidence hardening (27 September 2026)

- PR #7 (Paper A readiness package, P43/P44 source identity) merged into `develop` (`eeb84fc`).
- Branch `feature/paper-a-evidence-hardening`:
  - **G2:** controlled discrepancy taxonomy (`contracts.discrepancy_taxonomy`), proposed mapping for all 19 records (none approved).
  - **G3:** tracked text-free `ingestion_summary.json` for P40–P45 (P45 machine-generated; P40–P43 pending local intakes; P44 none recorded).
  - **G4:** CI on Linux/Windows/macOS, verifying every study and recording its environment.
  - **G1:** decision candidates prepared.
- Cross-OS findings F20 (P45 FE-check recomputation noise) and F21 (P38 platform-dependent provenance) are handled by D-007, which the owner approved on 28 September 2026.
- Qualification remains NOT_GRANTED everywhere, and all discrepancies keep their status. No P46.

## Checkpoint — owner approvals recorded (28 September 2026)

- D-007 is approved.
- The taxonomy (G2) is approved: all 19 labels, with an append-only review trail.
- The G1 decisions are recorded (D-008):
  - P45-D004 and P41-D002: ACCEPTED_WITH_RATIONALE;
  - P43-D001, P43-D002 and P44-D001: DEFERRED;
  - P16-D001 and P36-D001: BOUNDED.
- Before/after gate evidence: `publication/PAPER_A_ENGIPROOF/G1_GATE_EVIDENCE.json`.
- Graphs were synced for P16, P36 and P41–P45; all audits PASS at coverage 1.0.
- The owner ran `29_RECORD_INGESTION_SUMMARIES_WINDOWS.bat` locally (commit `f651f07`), so P40–P44 now have machine-generated summaries and G3 is closed.
  - All fingerprints match.
  - Readiness: P40 3/3, P41 5/5, P42 5/5, P43 3/5, P44 4/7.
  - P44 was ingested through the pipeline.
- That run exposed F22: `engiproof.cmd` swallowed exit codes. It is fixed in `c62f038`.
- Qualification remains NOT_GRANTED. No P46.

## Checkpoint — P45 Windows verification re-run after F22 (28 September 2026)

- `28_VERIFY_P45_PHASE1_WINDOWS.bat` was re-run by the owner on the PR #8 branch (`bab6764`), using the fixed `engiproof.cmd`, so every `call engiproof` step's exit code was checked.
- Result: `=== P45 PHASE1 VERIFY PASS ===`. Environment: Windows 10 AMD64, CPython 3.12.10, NumPy 2.5.3. `verify P45` = PASS_SOURCE_EXTERNAL; reproduction classes BYTE_ONLY 1, NUMERICAL_NONMATERIAL 1, 0 material.
- This is now the authoritative local P45 Windows verification.
- The only local change was the P45 graph counters (Q7), which were not committed.
- The pre-F22 banner of 27 September is superseded as evidence (D-006 addendum).
- No P45 evidence, discrepancy or qualification changed.

## Stage change — Paper A submission refinement (28 September 2026)

- PR #9 (manuscript Draft v0.2.1) is merged into `develop` (`36dfdcb`).
- Paper A evidence gathering is closed. The active stage is submission-quality refinement (WORK_QUEUE Q11): journal format, figures and tables, wording compression, reproducibility references, final source audit, final PDF review.
- No new evidence cases and no P46. P40–P45 evidence, decisions and qualification are frozen for this stage.

