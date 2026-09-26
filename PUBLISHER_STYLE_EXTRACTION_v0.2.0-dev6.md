# EngiProof v0.2.0-dev6 — Publisher-style structure robustness

The second real ingestion case (P41, ASME OMAE2011-49960) exposed a generalization issue in dev5:

- ASME table captions use forms such as `Table 1 Pipeline data` with no period.
- Figure captions use forms such as `Figure 4 - Case 1 ...`.
- dev5's true-caption rule was too narrow and therefore failed to mark clear publisher captions as anchors.
- engineering property tables also use symbol/unit/value rows such as `D [mm] 298.5 394.0`, which require table-row recognition beyond PIP/case identifiers.

Dev6 broadens caption recognition conservatively, stops table blocks at subsequent punctuation-free captions, and recognizes parameter/unit/numeric engineering rows.

This change is driven by P41 and is intended to improve publisher-format generality, not to special-case P41.
