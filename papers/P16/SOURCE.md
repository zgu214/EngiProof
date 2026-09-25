# P16 source contract

**Paper:** Chen and Chia (2010), *Pipe-in-Pipe Walking: Understanding the Mechanism, Evaluating and Mitigating the Phenomenon*  
**DOI:** 10.1115/OMAE2010-20058  
**Canonical local PDF:** `p16-chen2010.pdf`  
**Expected SHA-256:** `9fed9062ddbeb777e82e32197e9c0f4f67c60a326f8ac5be39238672495575e0`

## Selected target

Figure 5 and Table 2.

## Evidence boundary

Status: `COMPARED`.

EngiProof preserves the source-backed vector extraction of the published Figure 5 curve and the printed Table 2 walking increments. It compares cumulative Table 2 movement with linear interpolation of the source figure at the published end steps.

This is **not** an independent pipeline-walking solver. The source graph and table have finite graphical/printed precision, and raw author solver output is unavailable. No FE reproduction or engineering qualification is claimed.

The copyrighted PDF and raster snapshot are intentionally external to the public package; the expected source fingerprint and extraction contract are retained.
