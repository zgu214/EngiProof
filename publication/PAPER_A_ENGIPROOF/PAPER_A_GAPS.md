# Paper A — Evidence Gaps

Review date: 27 September 2026. Derived from `CLAIM_EVIDENCE_MATRIX.md`; only gaps that block or materially weaken a claim Paper A intends to make are listed.

Categories: **a** no new paper (work or decisions on existing records) · **b** software/runtime work · **c** deeper use of an existing P40–P45 case · **d** a genuinely new P46 source.

**Result: five gaps; none is category d. P46 is not required.**

---

## G1 — Human decision boundary exercised only once

- **Missing claim (PA-14):** discrepancies block promotion until a documented human decision, and such decisions (including unblocking ones) are recorded append-only without changing qualification.
- **Why P40–P45 are insufficient:** the workflow is implemented and unit-tested (`tests/test_discrepancy_decisions.py`), and promotion is blocked in all six studies, but the only real decision is P40-D001 `DEFERRED`. The unblocking dispositions (RESOLVED, BOUNDED, ACCEPTED_WITH_RATIONALE) have never been applied to real evidence, so the paper cannot show the boundary working end to end.
- **Category:** a — the records exist; what is missing is reviewer decisions.
- **Work:** the reviewer (not the agent) records decisions on a few existing discrepancies where the evidence supports a disposition, keeping others DEFERRED, for example:
  - P45-D004 (a `/g` printed where the text states 9 s) is a candidate for ACCEPTED_WITH_RATIONALE;
  - P36/P16 already carry BOUNDED statuses in the manifest (not recorded decisions) and could be formalised.

  Then run `discrepancy-gate` and `promotion-gate` to show the effect. No evidence value changes; qualification stays NOT_GRANTED.
- **Blocks submission:** recommended; without it, state explicitly that only the blocking path has been exercised.

## G2 — Discrepancy classification is not a controlled vocabulary

- **Missing claim (PA-13):** each discrepancy is classified in a defined taxonomy that is applied consistently.
- **Why P40–P45 are insufficient:** `classification_hint` is free text. There are ten labels over 14 records, and similar phenomena carry different labels:
  - P41-D002 (paragraph MNm vs axis kNm) is PUBLISHED_REFERENCE_MISMATCH;
  - P44-D001 (paragraph vs caption) is SOURCE_FIGURE_TEXT_MISMATCH;
  - P45-D003 (missing unit) is SOURCE_UNIT_AMBIGUITY.

  Paper A's taxonomy table would expose this inconsistency.
- **Category:** b, plus human review of the reclassification.
- **Work:**
  - define the vocabulary with definitions and decision rules in `engiproof/contracts/contracts.json`;
  - validate `classification_hint` against it in `validate_study_manifest`;
  - propose a mapping of the 14 existing records for reviewer approval. Reclassification changes labels only, never observations, values or status.
- **Blocks submission:** yes — Table A2 depends on it.

## G3 — Source identity and ingestion records incomplete

- **Missing claims (PA-02, PA-04):** every case has confirmed source identity, and ingestion/extraction outcomes are traceable in the repository.
- **Why P40–P45 are insufficient:**
  - P43 and P44 record `doi: PENDING`. Public search did not confirm them here, and guessing a DOI from the SPE pattern is not identity evidence.
  - P40 and P44 have no `ingestion_record`.
  - Candidate counts, readiness results and audit statuses exist only in prose (handover, dev notes), because intake directories are local and gitignored by design (they can hold source excerpts).
  - Source format (born-digital vs scan) is not recorded for P43/P44.
- **Category:** a (obtain the DOIs from the publisher records) + b (a tracked, text-free ingestion summary per study: fingerprint, audit checks, candidate/readiness counts, format — no excerpts).
- **Work:**
  - confirm the P43/P44 DOIs from OnePetro or the user's copies;
  - add `ingestion_summary` to each manifest, or as a small tracked JSON;
  - for cases that were scaffolded without the pipeline, state so rather than backfilling.
- **Blocks submission:** yes — provenance is the paper's thesis.

## G4 — Cross-OS reproducibility not recorded as artifacts

- **Missing claim (PA-19):** evidence regenerates equivalently across Python/NumPy versions and operating systems.
- **Why P40–P45 are insufficient:**
  - CI covers Linux only (Python 3.10/3.12/3.13).
  - Windows evidence is the user's reported local runs of the verification batches, with no stored record.
  - macOS is untested.
  - Frozen artifacts (e.g. P43) do not record the environment that produced them, so a cross-environment difference cannot be attributed.
- **Category:** b.
- **Work:**
  - add `windows-latest` (optionally `macos-latest`) to the CI matrix with the existing non-mutation gate;
  - record the producing Python/NumPy/platform in verification records as ENVIRONMENT_METADATA (non-material by construction).
- **Blocks submission:** recommended; otherwise scope the claim to “Linux CI plus reported Windows runs”.

## G5 — Experimental data never handled as a distinct evidence population

- **Missing claim (PA-26):** EngiProof distinguishes model-versus-experiment evidence from reproduction and from source inconsistency.
- **Why P40–P45 are insufficient:** P40 Table 2 already contains hyperbaric-chamber propagation pressures (`papers/P40/reference/table2.csv`, `Pp_kPa`), but they are used only as the published normalisation of the analytical ratios. The MODEL_VS_EXPERIMENT_GAP category exists in `src/engiproof/discrepancy.py` and has never been instantiated.
- **Category:** c — deeper use of P40; no new source.
- **Work:**
  - record the hyperbaric values as a PUBLISHED experimental population;
  - compare Eqs. (2), (3), (6), (9) against it as COMPARED;
  - record the model-versus-experiment gaps as OBSERVED MODEL_VS_EXPERIMENT_GAP. Do not re-open P40-D001, and do not tune.
- **Blocks submission:** optional. Needed only if Paper A claims experimental-evidence handling; recommended because the evidence model already defines it.

---

## Considered and rejected as gaps

| Candidate | Why not a gap for Paper A |
|---|---|
| SOLVER_NEW evidence (PA-25) | Defined but reserved. Demonstrating it needs solver adapters on existing cases (roadmap), not a new paper. Present as defined-not-exercised. |
| Generality beyond offshore/subsea mechanics (PA-27) | One more paper cannot establish generality. State the domain scope. |
| Extraction accuracy (PA-05) | Needs a labelled benchmark corpus. Do not claim. |
| Organisational independence (PA-10) | Needs external replicators. State as a limitation / future work. |
| Detection completeness (PA-12) | No recall measure is possible without ground truth. Do not claim. |

## Housekeeping (not evidence gaps)

- **H1:** graph-sync file idempotency (WORK_QUEUE Q7).
- **H2:** record the non-reproduced targets of P41/P42/P44 as BLOCKED comparisons, as P45 does. This adds records only; no evidence changes.
- **H3:** flatten the nested `PAPER_A_ENGIPROOF_LATEX/publication/PAPER_A_ENGIPROOF_LATEX/` manuscript path.
- **H4:** manuscript Draft v0.1 covers P40–P41 only; the synthesis should follow `PAPER_A_OUTLINE.md`.
