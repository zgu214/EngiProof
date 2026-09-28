# EngiProof — Work Queue

## Q1 — Continuity architecture dev8
Priority: highest. Verify `continuity-audit`, build source-PDF-free checkpoint bundle, commit/push.

## Q2 — P43 selection and ingestion
Priority: next. Choose materially different mechanics/evidence from P40–P42, then run the full ingestion-to-evidence chain.

## Q3 — Journal Paper A
Parallel/secondary. Keep evidence capture synchronized without displacing engineering work.


## Q4 — P44 optional depth

**State:** deferred / source-gated. Re-open only if additional source-ready geometry, original model output, or authoritative implementation detail becomes available.

## Q5 — P45

**State:** Phase 1 COMPLETED and FROZEN (D-006): local Windows verification PASS; CONDITIONAL / NOT_GRANTED; P45-D001…D006 OPEN.

## Q6 — Paper A readiness review

**Priority: HIGHEST (active).** Review P40–P45 as the evidence matrix and decide the Paper A path. Do NOT create P46 automatically: a P46 is justified only if the review demonstrates a specific evidence gap that no existing study, runtime work or deeper use of P40–P45 can fill.

## Q7 — Runtime hardening: file-idempotent graph-sync

**Priority: low.** A second `graph-sync P45` changed only the persisted sync counters (`added_nodes: 22 -> 0`, `added_edges: 22 -> 0`); no node, edge, engineering value or evidence changed. graph-sync is evidence-idempotent but not file-idempotent because per-run mutation counts are persisted in the tracked graph (same pattern in P40–P43). Make repeated syncs byte-stable (e.g. report counts without persisting them). Do not reopen P45 for this.

## Q8 — Paper A evidence hardening (G1–G5)

**State: COMPLETED** (PR #8 merged `be33392`; manuscript Draft v0.2.1 merged in PR #9, `36dfdcb`).
- **Done:** D-007 approved; taxonomy approved; G1 decisions recorded (D-008).
- **Done (28 Sep 2026):** machine-generated ingestion summaries for P40–P44 from the owner's local intakes (G3 closed). PR #8 is ready to merge on the owner's yes.
- **After PR #8 merges:** finalise the manuscript in PR #9 (Appendix A, related-work references, P42 author list, rebuild).
- G5 optional. No P46.

## Q9 — Runtime hardening: portable P38 runner

**Priority: low.** `papers/P38/run_calculation.py` writes `str(Path.relative_to())` keys, which gives backslashes on Windows. Use `.as_posix()` at the next explicitly approved P38 regeneration: the code hash is recorded in the frozen manifest, so fixing it now would itself be a material change.

## Q10 — Windows dispatcher exit codes (F22)

**Fixed in PR #8.** `engiproof.cmd` returned 0 for every command. Windows CI now asserts that exit codes propagate. After pulling, re-run any local Windows batch whose PASS mattered. Verification of P40–P45 on Windows is covered by CI.

## Q11 — Paper A submission-quality refinement

**Priority: HIGHEST (active, from 28 Sep 2026).** The evidence base is closed. This stage adds no new evidence cases and no P46, and it does not change P40–P45 evidence, decisions or qualification.

1. **Journal format.** Target: Advances in Engineering Software (`docs/PUBLICATION_STRATEGY.md`), Elsevier `elsarticle`. Required front and back matter:
   - highlights and keywords;
   - CRediT statement;
   - competing interests;
   - data and code availability;
   - the Elsevier generative-AI declaration.
2. **Figures and tables.** Redraw figures from repository data, and regenerate the tables from a tagged release.
3. **Wording compression.** Convert list-heavy draft prose into journal prose and meet the length target.
4. **Reproducibility references.** Complete and verify references; tag a software release (DOI if available).
5. **Final source audit.** Check every number against its repository artifact, and every citation against its publisher record.
6. **Final PDF review.**

