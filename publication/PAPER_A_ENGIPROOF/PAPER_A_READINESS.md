# EngiProof Paper A — Readiness Checkpoint

> **Superseded for the post-P45 decision (27 September 2026):** see `PAPER_A_READINESS_REVIEW.md`, `CLAIM_EVIDENCE_MATRIX.md`, `PAPER_A_GAPS.md` and `PAPER_A_OUTLINE.md`. Result: decision gate B — runtime/method work, no P46. This file is kept as the pre-P45 checkpoint.

**Status:** Pre-submission engineering-evidence review  
**Framework:** EngiProof v0.2.0-dev8  
**Primary repository state:** P44 frozen, P45 next  
**Qualification:** NOT_GRANTED

## 1. Working paper identity

**Working title**

> **EngiProof: A Provenance-Preserving Framework for Converting Published Engineering Research into Reproducible Computational Evidence**

**Primary journal target**

Advances in Engineering Software.

**Central methodological claim**

EngiProof introduces a controlled engineering-evidence lifecycle in which source identity, published methods, independent computations, discrepancies, human decisions, callable implementations, evidence graphs and qualification status remain explicitly linked and machine-auditable.

The paper must not be framed as a generic “PDF-to-code” system.

---

## 2. Current evidence base

### P40 — propagation buckling / published-reference mismatch
Evidence:
- source-bounded Eqs. (2), (3), (6), (9);
- independent work-balance reconstruction;
- published/reference mismatch retained without tuning.

Methodological role:
- demonstrates independent corroboration of a reproduced result that disagrees with a published table;
- establishes `PUBLISHED_REFERENCE_MISMATCH`.

### P41 — pipe-in-pipe axial/global buckling
Evidence:
- independent geometry/EA reconstruction;
- Eqs. (6)–(8) load sharing;
- Table 2 internal force-balance mismatch;
- Figure 10 paragraph/axis unit mismatch.

Methodological role:
- demonstrates cross-equation/table consistency checking;
- demonstrates source-internal unit inconsistency;
- shows that EngiProof does not silently repair the source.

### P42 — flexible-pipe tension/bending
Evidence:
- source-bounded continuum and armour mechanics;
- analytical stress-family reproduction;
- documented tension-dependent FP-RUC versus tension-independent analytical response;
- Figure 16 implementation/provenance gap retained.

Methodological role:
- distinguishes a documented model-form/kinematic difference from a source error;
- establishes `SOURCE_IMPLEMENTATION_PROVENANCE_GAP`;
- demonstrates that equation transcription does not imply full reproducibility.

### P43 — drilling-riser eigenproblem
Evidence:
- independent Hermite-FE solution of the published variable-tension eigenproblem;
- Table 1 eigenvalue reproduction;
- Eq. (10) / Table 2 approximation-error reproduction;
- independent mode-shape/inflection check;
- source-internal numerical inconsistencies retained.

Methodological role:
- demonstrates independent numerical formulation rather than source-code mimicry;
- demonstrates cross-table/equation internal-consistency auditing;
- extends EngiProof beyond algebraic/static calculations into eigenvalue problems.

### P44 — drillstring/well/riser contact
Evidence:
- independent drillpipe section-property reconstruction;
- Equation (1) equilibrium/FEM agreement;
- time-step arithmetic;
- contact-stiffness-scale check;
- source paragraph versus figure-caption time-label mismatch.

Methodological role:
- demonstrates source-bounded handling of nonlinear-contact literature when full reproduction is not justified by available source detail;
- shows that “not reproduced” can be a rigorous evidence outcome rather than a failure.

---

## 3. Current discrepancy taxonomy represented in the paper

The current case set supports at least these distinct evidence/discrepancy classes:

1. `PUBLISHED_REFERENCE_MISMATCH`
2. source-internal force-balance inconsistency
3. source unit inconsistency
4. `MODEL_FORM_KINEMATICS_DIFFERENCE`
5. `SOURCE_IMPLEMENTATION_PROVENANCE_GAP`
6. source figure/text labeling mismatch
7. independently reproduced eigenproblem / cross-table consistency evidence
8. source-bounded non-reproduction due to insufficient implementation provenance

This diversity is more important than raw paper count.

---

## 4. What P45 must contribute

**P45 target:** V. Hachemi Safai (1983), *Nonlinear dynamic analysis of deep water risers*.

P45 should be selected for a specific methodological reason, not because the project simply needs “one more paper.”

Desired contribution:
- nonlinear dynamic response;
- time integration / structural nonlinearity;
- comparison between nonlinear and simplified “linear structure” assumptions;
- multi-program comparison evidence;
- one source-backed dynamic benchmark that materially differs from P40–P44.

High-value source targets:
- the six comparison cases against other programs;
- Tables 1–3;
- Figures 4–9 comparison envelopes;
- Figure 11 / stated ~15% near-head stress underestimation from the linear-structure simplification;
- explicit time-varying displacement/tension definitions in the deep-water example.

P45 should answer:

> Can the EngiProof evidence lifecycle handle nonlinear time-dependent structural mechanics and model-form simplification effects without collapsing reproduction, comparison and qualification into one claim?

If yes, Paper A becomes substantially stronger.

---

## 5. Is P46 required?

**Decision: not automatically.**

After P45, perform a formal Paper-A readiness review.

Proceed directly to submission if the paper already demonstrates:
- heterogeneous mechanics;
- source identity/provenance;
- independent computation;
- reproducibility;
- multiple discrepancy classes;
- at least one explicit non-reproducibility/provenance boundary;
- evidence graph / machine-auditable linkage;
- callable implementations;
- explicit qualification separation;
- a convincing evaluation section.

Only add P46 if a clearly identified evidence gap remains.

A useful P46, if needed, should preferably add one of:
- modern experimental validation;
- strong commercial/open solver cross-check;
- cross-domain engineering case outside subsea mechanics;
- standards/code-linked evidence case.

Do not add P46 merely to increase the paper count.

---

## 6. Manuscript structure

1. Introduction
2. Problem: why literature-to-code is not engineering evidence
3. EngiProof evidence model
4. Source identity and provenance control
5. Reproduction versus independent verification
6. Discrepancy taxonomy and human decision workflow
7. Evidence graph and callable methods
8. Case-study evaluation
   - P40
   - P41
   - P42
   - P43
   - P44
   - P45
9. Cross-case results
10. Qualification boundary
11. Limitations
12. Discussion: toward engineering-evidence infrastructure
13. Conclusions

---

## 7. Figures/tables that Paper A should contain

### Core figures
- **Figure A1:** EngiProof evidence lifecycle
- **Figure A2:** evidence graph architecture
- **Figure A3:** discrepancy decision/promotion flow
- **Figure A4:** cross-case evidence map showing which methodological capability each P40–P45 case exercises

### Core tables
- **Table A1:** P40–P45 mechanics/evidence-class matrix
- **Table A2:** discrepancy taxonomy with examples
- **Table A3:** source/reproduction/independent/qualification status matrix
- **Table A4:** reproducibility checklist and repository artifacts

Use source-derived numerical results only where already evidence-controlled. Do not reproduce copyrighted publisher figures unless permission/licensing supports it; regenerate independent plots where appropriate.

---

## 8. Submission gate

Paper A is ready to submit when all of the following are true:

- P45 has completed a bounded, source-linked engineering chain;
- all main-text numerical claims trace to repository evidence;
- every case distinguishes PUBLISHED versus INDEPENDENT evidence;
- open discrepancies remain visibly open;
- no case implies engineering qualification;
- repository contains a reproducibility entry point;
- manuscript claim-evidence matrix is complete;
- all main figures are original/regenerated or appropriately licensed;
- limitations section clearly states what EngiProof does not establish;
- abstract and conclusions describe a methodology, not an AI novelty claim.

---

## 9. Current decision

**Do not start heavy P45 work while model budget is nearly exhausted.**

Current best action:
1. preserve this readiness checkpoint;
2. preserve the publication strategy;
3. wait for budget reset;
4. begin P45 with the explicit methodological targets above;
5. perform Paper-A submission review immediately after P45;
6. add P46 only if a specific evidence gap remains.

This prevents publication work from becoming detached from the engineering evidence base.
