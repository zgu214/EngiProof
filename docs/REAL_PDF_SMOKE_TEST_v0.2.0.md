# Real-PDF ingestion smoke test — v0.2.0-dev1

A real 8-page pipe-in-pipe conference paper was used as a non-distributed local source to exercise the v0.2.0 ingestion pipeline.

Source identity:

- title: *Global Buckling of Pipe-in-Pipe – Structural Response and Design Criteria*
- paper identifier: OMAE2011-49960
- local source SHA-256: `6f5534b5780372c7576955c422871f3c5ff1f4465e99ceb50f58d0c5e6520466`
- raw PDF distributed with EngiProof: **no**

Observed pipeline output:

- 17 target candidates discovered;
- 17/17 candidates source-located during enrichment;
- 4 equation candidates;
- 3 table candidates;
- 10 figure candidates;
- 19 symbol-definition candidates;
- equation blocks were tied to printed equation numbers where extractable;
- Table 1 was recognized as a caption followed by structured row candidates;
- selected targets produced kind-specific reproduction tasks and comparison templates;
- no absolute source path or full extracted paper text was persisted.

This smoke test demonstrates ingestion/extraction workflow behavior only. It does **not** make any engineering evidence or qualification claim for the paper.
