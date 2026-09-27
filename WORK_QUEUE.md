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

**Priority: HIGHEST (active).** The PR `feature/paper-a-evidence-hardening` implements G2–G4 and prepares G1. Owner actions:
- approve D-007;
- review the taxonomy labels (`engiproof taxonomy-review`);
- record G1 decisions (`publication/PAPER_A_ENGIPROOF/G1_DECISION_CANDIDATES.md`);
- run `29_RECORD_INGESTION_SUMMARIES_WINDOWS.bat` where the P40–P43 intakes are.

G5 is optional. Then manuscript synthesis. No P46.

## Q9 — Runtime hardening: portable P38 runner

**Priority: low.** `papers/P38/run_calculation.py` writes `str(Path.relative_to())` keys, which gives backslashes on Windows. Use `.as_posix()` at the next explicitly approved P38 regeneration: the code hash is recorded in the frozen manifest, so fixing it now would itself be a material change.
