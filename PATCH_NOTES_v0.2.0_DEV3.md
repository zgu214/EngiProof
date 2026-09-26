# EngiProof v0.2.0-dev3 — Generic Discrepancy Automation

This checkpoint converts discrepancy handling from paper-specific narrative into a generic machine-readable workflow. P40-D001 is intentionally the first real blocking case. The engine records a high-priority published-reference mismatch, corroboration by an independent calculation, and a promotion block. It does not conclude that the paper is wrong and does not tune inputs.

Important behavior: `promotion-gate P40` is expected to return `ready=false` while P40-D001 remains OPEN. This is success, not failure.
