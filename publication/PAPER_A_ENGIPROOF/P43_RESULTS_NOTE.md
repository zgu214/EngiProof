# P43 publication evidence note

P43 adds an eigenvalue/mode-shape evidence class. The independent Hermite-FE weak solution of Eq. (8) reproduces ordinary Table 1 values to printed precision, and Eq. (10) reproduces Table 2 error trends.

P43-D001 is a source-internal numerical inconsistency: Table1 alpha=0, beta=200, lambda5 is printed as 13.221, whereas independent Eq8 FE and Eq10 give approximately 18.221 and Table2 reports zero Eq10 error for alpha=0. EngiProof preserves the published value and does not silently repair it.

P43-D002: Table 1 alpha=200, beta=100, lambda1 is visibly printed as 6.554. Independent Eq.8 FE gives ~6.654; Eq.10/Table2 internal consistency also supports 6.654. Preserve printed 6.554; inferred correction is not applied.
