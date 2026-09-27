# Paper A — Claim–Evidence Matrix

Review date: 27 September 2026 · repository `develop` after PR #5 (`cb2a595`) and the P45 freeze patch · framework `0.2.0.dev8`

Status vocabulary: **SUPPORTED** (claimable as stated, with the listed constraint) · **PARTIALLY_SUPPORTED** (claimable only in the narrower form given) · **NOT_SUPPORTED_YET** (do not claim) · **OUT_OF_SCOPE** (not a claim of this paper).

Evidence rule: only repository artifacts count. Paper count, test count, file count and page count are **not** evidence of scientific validity and are not used below. Paths are relative to the repository root; `S(Pxx)` = `engiproof/studies/Pxx/study.json`.

## Summary

| Status | Claims |
|---|---|
| SUPPORTED | 16 |
| PARTIALLY_SUPPORTED | 8 |
| NOT_SUPPORTED_YET | 3 |
| OUT_OF_SCOPE | 3 |

## 1. Source ingestion and identity

| ID | Candidate claim | Status | Repository evidence | Constraint for the manuscript |
|---|---|---|---|---|
| PA-01 | Every evidence case is bound to an external source by SHA-256, and the copyrighted source is never redistributed. | SUPPORTED | `source.sha256` in `S(P40)`…`S(P45)`; `.gitignore` (`01_doc/*.pdf`); P45 page images used only outside the repository (`papers/P45/extraction/digitize_head_envelopes.py` docstring) | State as a provenance rule, not as copyright compliance advice. |
| PA-02 | A source-identity audit gates reproduction and detects bibliographic conflicts. | PARTIALLY_SUPPORTED | P40 entered with a wrong DOI/year and was blocked after the dev2 audit was introduced (`PROGRESS_v0.2.0.md` “P40 real-source findings”, `HANDOVER_CURRENT.md` “Critical source-identity blocker”); P42 false year conflict removed by publication-vs-secondary year semantics (`SOURCE_IDENTITY_AND_SPLIT_CAPTIONS_v0.2.0-dev7.md`); P45 audit `DOI NOT_FOUND_IN_SOURCE`, confirmed manually (`papers/P45/reference/source_identity.json`) | The P40 conflict was found by a human and led to the gate; do not present it as automatic detection. P43/P44 identity was completed manually from publisher records (DOIs `10.2118/5620-PA`, `10.2118/28723-MS`; the P43 SPE number had been recorded as 5820 in error, corrected to 5620). The audit cannot confirm identity for pre-DOI or text-poor sources without manual review. |

## 2. Extraction robustness across publishers and eras

| ID | Candidate claim | Status | Repository evidence | Constraint |
|---|---|---|---|---|
| PA-03 | Extraction candidates never become evidence: readiness and promotion gates block unreviewed targets, and extraction uncertainty is kept separate from source error. | SUPPORTED | Readiness gate and promotion gate (`src/engiproof/ingestion.py`); P45 readiness `PARTIAL 4/16` with the manual review recorded (`S(P45).target_review`); P41 Table 2 mismatch held as transcription uncertainty until visual confirmation, then reclassified (`CHAT_COMPACT_CURRENT.md` P41 sections); `promotion-gate` blocks P40–P45 | Core claim of the paper. |
| PA-04 | Extraction was hardened against concrete, recorded failures across publisher styles (ASCE, ASME, Elsevier) and a 1983 scanned source. | PARTIALLY_SUPPORTED | P40 Type1/CFF glyph artefacts and lost grouped equation references (`PROGRESS_v0.2.0.md` dev2); P41 ASME punctuation-free captions (`PUBLISHER_STYLE_EXTRACTION_v0.2.0-dev6.md`); P42 Elsevier split captions (`SOURCE_IDENTITY_AND_SPLIT_CAPTIONS_v0.2.0-dev7.md`); P45 scan: Eq. (11), sub-figures and appendices not discovered (`S(P45).target_review.automation_gaps_observed`); generic regression tests `tests/test_ingestion*.py`; tracked text-free ingestion summaries `engiproof/studies/P40…P45/ingestion_summary.json` (`engiproof ingestion-summary-audit`) | Case-level observations only. Machine-generated summary so far only for P45 (scan with text layer, 300 dpi; readiness PARTIAL 4/16). P40–P43 are explicit `PENDING_LOCAL_SUMMARY` records carrying only outcomes already written in tracked records, and P44 is `NO_INGESTION_RECORD`. G3 is closed once `29_RECORD_INGESTION_SUMMARIES_WINDOWS.bat` is run on the machine holding the intakes. |
| PA-05 | Quantified extraction accuracy / recall across publishers. | NOT_SUPPORTED_YET | none | Needs a labelled benchmark corpus, not one more paper. Do not report any accuracy figure. |

## 3. Source-bounded reproduction

| ID | Candidate claim | Status | Repository evidence | Constraint |
|---|---|---|---|---|
| PA-06 | Published methods re-implemented from the source reproduce published values to source precision for bounded targets. | SUPPORTED | P40-C001 (max ratio difference 0.0055); P41-C001/C002/C004/C006; P42-C002/C004/C006; P43-C002…C008 (35-row/175-eigenvalue Table 1, full Table 2); P44-C001…C003; P45-C001 | Report per target, never “paper reproduced”. |
| PA-07 | Outcomes are recorded per target as REPRODUCED / COMPARED / VERIFIED / CONDITIONAL / BLOCKED. | SUPPORTED | Comparison statuses across P40–P45: 14 REPRODUCED, 24 COMPARED, 2 VERIFIED, 7 CONDITIONAL, 1 BLOCKED (`S(Pxx).comparisons`) | Only P45 records a non-reproduced target as a BLOCKED comparison; P41/P42/P44 record theirs as limitations (housekeeping H2). |

## 4. Independent checking

| ID | Candidate claim | Status | Repository evidence | Constraint |
|---|---|---|---|---|
| PA-08 | Methodologically independent computations (different formulation or numerical method) corroborate or contradict published values. | SUPPORTED | P40 work-balance reconstruction vs Eq. (9), ≤ 0.081% (P40-C002); P43 Hermite-FE eigen-solution instead of the source power series (`S(P43).limitations`); P45 independent Hermite beam-column FE vs Appendix 1 (< 1e-7), six rigid-body modes, reconstructed-integrator stability (`papers/P45/results/phase1_summary.json`); P41 elastic EI ratio; P44 section properties | “Independent” means methodologically independent, not independent people. |
| PA-09 | Independent checks decide the direction of a discrepancy (reproduction vs printed value) rather than being tuned to it. | SUPPORTED | `independent_support` = CORROBORATES_REPRODUCTION (P40-D001, P41-D001), EQ8_FE_PLUS_EQ10_PLUS_TABLE2_INTERNAL_CONSISTENCY (P43-D001/D002), GEOMETRIC_DISPLACEMENT_CHECK (P45-D001) | — |
| PA-10 | Checks are independent in the organisational sense (performed by other people/teams). | NOT_SUPPORTED_YET | none | State as a limitation; external replication is future work. |

## 5. Detection and preservation of source inconsistencies

| ID | Candidate claim | Status | Repository evidence | Constraint |
|---|---|---|---|---|
| PA-11 | Source inconsistencies are detected and preserved without tuning or silent correction. | SUPPORTED | 14 discrepancy records in six studies (13 OPEN, 1 OBSERVED); printed values retained where an inferred correction exists (P43-D001 13.221 vs 18.221; P41-D001 153 vs ~159; P45-D002 1.290.500 dN); preservation asserted by tests (`tests/test_p44_phase1.py::test_source_time_mismatch_preserved`, `tests/test_p45_phase1.py` D001/D002) | — |
| PA-12 | All inconsistencies in a source are found (completeness). | NOT_SUPPORTED_YET | none | No recall measure exists; do not claim. |

## 6. Discrepancy classification and the human decision boundary

| ID | Candidate claim | Status | Repository evidence | Constraint |
|---|---|---|---|---|
| PA-13 | Every discrepancy carries an explicit classification, independent-support basis, promotion effect and closure requirements. | PARTIALLY_SUPPORTED | `discrepancy-audit` over P40–P45; 10 distinct classification labels in use; `closure_requirements` per record (`S(P44)`, `S(P45)`) | The controlled vocabulary now exists: nine categories and seven loci, with decision rules, validated in `validate_study_manifest` (`contracts.discrepancy_taxonomy`, `docs/DISCREPANCY_TAXONOMY.md`). All 19 records have a proposed mapping, but none is approved, so the claim holds only for the vocabulary and validation. The mapping stays “proposed” until `engiproof taxonomy-review` approvals are recorded (G2). |
| PA-14 | Discrepancies block promotion until an append-only human decision with reviewer, rationale and evidence references is recorded; decisions never change qualification. | PARTIALLY_SUPPORTED | Implementation and tests (`src/engiproof/discrepancy.py`, `tests/test_discrepancy_decisions.py`, `DISCREPANCY_DECISION_WORKFLOW_v0.2.0-dev4.md`); promotion blocked for all six studies; one real decision: P40-D001 `DEFERRED` (`engiproof/studies/P40/discrepancy_decisions.json`) | The unblocking path (RESOLVED / BOUNDED / ACCEPTED_WITH_RATIONALE) has never been exercised on a real case. Candidates with dry-run gate effects are prepared (`G1_DECISION_CANDIDATES.md`); the decisions are the owner's. Gap G1. |

## 7. Evidence graph and provenance

| ID | Candidate claim | Status | Repository evidence | Constraint |
|---|---|---|---|---|
| PA-15 | Each study has a machine-auditable evidence graph linking source, implementations, comparisons, discrepancies and assessments. | SUPPORTED | `graph-audit` PASS, coverage 1.0: P40 13/13, P41 25/25, P42 24/24, P43 20/20, P44 11/11, P45 38/38 items | Coverage checks representation, not correctness. graph-sync is evidence-idempotent but not file-idempotent (WORK_QUEUE Q7). |
| PA-16 | Provenance hashes are independent of the checkout. | PARTIALLY_SUPPORTED | Mutation inventory: every historical inherited-result hash was taken over CRLF bytes (`docs/MUTATION_INVENTORY_v0.2.0.md`); canonical `text/lf-v1` identity introduced and reported alongside byte hashes (`src/engiproof/provenance_identity.py`); comparator resolves line-ending variants | New provenance only; historical hashes are preserved as recorded, by decision (D-005). |

## 8. Non-mutating verification

| ID | Candidate claim | Status | Repository evidence | Constraint |
|---|---|---|---|---|
| PA-17 | Verification never mutates the evidence being verified. | SUPPORTED | Pre-fix baseline: 20 tracked result files rewritten, classified (`docs/MUTATION_INVENTORY_v0.2.0.md`); D-005; sandboxed verification (`src/engiproof/isolation.py`); `tests/test_non_mutation.py` hashes all tracked files around `verify-all`, every study's verify/run and the full suite; CI step fails on any tracked-file change (`.github/workflows/ci.yml`); review-found defects fixed (created/deleted artifacts, `platform` key) | Strong, concrete, and failure-driven — a central contribution. |
| PA-18 | Byte reproducibility, numerical reproducibility, engineering equivalence and engineering verification are distinct and machine-classified. | SUPPORTED | Comparator classes IDENTICAL / BYTE_ONLY / ENVIRONMENT_METADATA / NUMERICAL_NONMATERIAL / NUMERICAL_MATERIAL / MATERIAL_NON_NUMERIC; P43 declared recomputation tolerance + 3-decimal guard (`S(P43).verification_tolerance`); P45 artifacts IDENTICAL on the producing build. Correction (F20): under the default tolerance, the P45 independent-FE block is NUMERICAL_MATERIAL on every other CI build, including NumPy 2.5.3; it is NUMERICAL_NONMATERIAL only with the path-scoped tolerance proposed in D-007 | Tolerances are recomputation equivalence, never acceptance. |

## 9. Reproducibility across runtime environments

| ID | Candidate claim | Status | Repository evidence | Constraint |
|---|---|---|---|---|
| PA-19 | Evidence regenerates equivalently across Python/NumPy versions and operating systems. | PARTIALLY_SUPPORTED | CI on Linux, Python 3.10/3.12/3.13; P43 recomputation quantified under four Python/NumPy builds (`docs/MUTATION_INVENTORY_v0.2.0.md` P43 section); local Windows verification scripts (`26_…`, `28_VERIFY_P45_PHASE1_WINDOWS.bat`) passed as reported by the user | CI now verifies all 12 studies on Linux (Python 3.10/3.12/3.13), Windows (3.10/3.13) and macOS arm64 (3.13), with NumPy 2.2.6–2.5.3. Each run records its environment and comparator classes (`docs/CROSS_ENVIRONMENT_VERIFICATION.md`). Equivalence across these environments needed two comparator rules and one scoped P45 tolerance (D-007, pending owner approval), so the claim becomes SUPPORTED only once D-007 is approved. Frozen artifacts still mostly do not declare their producing environment. |

## 10. Incomplete or irreproducible published studies

| ID | Candidate claim | Status | Repository evidence | Constraint |
|---|---|---|---|---|
| PA-20 | Non-reproduction is an explicit, evidence-bearing outcome that names the missing inputs. | SUPPORTED | P45-C009 BLOCKED with the missing parameters listed, and the reconstructed integrator showing why the missing θ matters (θ = 1 unstable above Δt/T = 0.5513); P42-C007 CONDITIONAL provenance gap; P44 and P41 full FE responses not reproduced (limitations); P43 source power-series recursion replaced by an independent FE solution | — |
| PA-21 | Missing inputs are never inferred to complete a reproduction. | SUPPORTED | P44 K0 not invented (`S(P44).limitations`); P45 tension unit not asserted (P45-D003); P43 inferred 18.221 not substituted (P43-D001) | — |

## 11. Qualification boundary

| ID | Candidate claim | Status | Repository evidence | Constraint |
|---|---|---|---|---|
| PA-22 | Verification never grants engineering qualification; verification tolerances are not acceptance criteria. | SUPPORTED | `qualification: NOT_GRANTED` in every study manifest, result and graph; contract rules (`engiproof/contracts/contracts.json` verification contract); P43 tolerance statement; `AGENTS.md` rules 3–4 | — |
| PA-23 | EngiProof qualifies designs or replaces project-specific engineering verification. | OUT_OF_SCOPE | — | Explicitly disclaimed. |

## 12. Failure modes discovered through P40–P45

| ID | Candidate claim | Status | Repository evidence | Constraint |
|---|---|---|---|---|
| PA-24 | The framework's own failures were detected, recorded and corrected through the same evidence process. | SUPPORTED | Failure register in `PAPER_A_READINESS_REVIEW.md` §4 (19 recorded failure modes with repository references) | Report as lessons, not as a defect count. |

## Additional claims tested

| ID | Candidate claim | Status | Repository evidence | Constraint |
|---|---|---|---|---|
| PA-25 | All three evidence classes (PUBLISHED, INDEPENDENT, SOLVER_NEW) are exercised. | PARTIALLY_SUPPORTED | PUBLISHED and INDEPENDENT tools in every study; SOLVER_NEW defined (`docs/ENGIPROOF_DEVELOPMENT_STANDARD_v0.1.md`) but used by no study | Present SOLVER_NEW as defined and reserved; do not claim it is demonstrated. |
| PA-26 | Experimental reference data are handled as a distinct evidence population (model vs experiment). | PARTIALLY_SUPPORTED | P38-D002 is an OBSERVED MODEL_VS_EXPERIMENT_GAP. Reconstructed analytical pressures are 43 % / 26 % below the single-pipe / PiP experiments, while the arithmetic reproduces the printed analytical values within 0.16 %, so the gap is kept distinct from reproduction (`S(P38)`). Correction: the earlier review said the category had never been instantiated. Within P40–P45, P40 Table 2 ratios are analytical / hyperbaric-chamber by construction (`papers/P40/reference/table2.csv`). | P38 is outside the six-case population, so cite it as a repository example. G5 (recording P40's experimental population explicitly) is optional. |
| PA-27 | EngiProof generalises beyond offshore/subsea structural mechanics. | OUT_OF_SCOPE | All six cases are offshore/subsea structural mechanics | State the domain scope; one additional paper would not establish generality. |
| PA-28 | Evidence-controlled methods are callable, and every result carries its evidence envelope (class, status, limitations, boundary). | SUPPORTED | Tools in all six studies; `invoke_tool` envelope incl. `evidence_boundary` (`src/engiproof/core.py`); CLI and MCP server with tests (`tests/test_mcp_server.py`) | Runtime capability, not a scientific-validity claim. |
| PA-29 | EngiProof performs autonomous scientific discovery or AI-generated verification. | OUT_OF_SCOPE | — | Do not claim. Agent-assisted development is a method detail, not a result. |
| PA-30 | Project state is recoverable from repository control files without chat memory. | SUPPORTED | `continuity-audit` PASS on `develop`; durable invariants (`tests/test_continuity.py`); checkpoint bundle (D-001, D-003) | Supporting infrastructure claim. |
