# P41 source contract

**Paper:** Global Buckling of Pipe-in-Pipe: Structural Response and Design Criteria  
**Paper no.:** OMAE2011-49960  
**Year:** 2011  
**DOI:** `10.1115/OMAE2011-49960`  
**Canonical local source:** `p41-goplen2011.pdf`  
**Expected SHA-256:** `21c3765eb4e9bd16b5bf36b1a58f3c5f72bf4a08058fc7b7ca5241c045ee619d`

## Selected first reproduction chain

- Table 1 — pipeline geometry/material data.
- Table 2 — axial stiffness and distribution of forces.
- Eq. (6) — inner-pipe share of soil-friction force increment.
- Eq. (7) — outer-pipe share.
- Eq. (8) — total force-increment identity.

## Evidence boundary

The first P41 reproduction independently recalculates steel cross-sectional areas and axial stiffnesses from Table 1, then evaluates the published load-sharing relationships in Eqs. (6)-(8). It does **not** reproduce the paper's global-buckling FE model or acceptance-criteria analysis.

The PDF text-extraction result for the Table 2 inner force increment currently reads `153 N/m`, while the published equations and extracted stiffness values give approximately `158.8 N/m` (`159 N/m` to integer precision). This is retained as **source transcription review required**, not as a confirmed paper discrepancy, until the original Table 2 cell is visually checked.

The DOI is externally confirmed but was not present in the extracted PDF text. This provenance condition remains explicit.
