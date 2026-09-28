<!-- Source of the cover letter. scripts/build_submission_package.py turns it into cover_letter.docx and cover_letter.pdf.
     One paragraph per blank-line-separated block. The {date} placeholder is replaced by the build date. Edit this file, not the generated .docx. -->
{date}

The Editor
Advances in Engineering Software

Dear Editor,

Please consider the enclosed manuscript, "EngiProof: A provenance-preserving framework for converting published engineering research into reproducible computational evidence", for publication as a research article in Advances in Engineering Software.

When a published engineering paper is internally inconsistent or omits an input, computational reuse tends to normalise the problem away. The manuscript presents EngiProof, a framework that converts selected published engineering methods into source-bounded, reproducible and independently checked evidence. It keeps separate what was published, what was reproduced, what was checked independently, what disagrees, what was decided by a human, and what remains unqualified. Engineering qualification is never granted by the framework.

The framework is evaluated by capability on six heterogeneous offshore and subsea structural-mechanics studies published between 1976 and 2019, including a scanned 1983 source. Source-bounded implementations reproduce 14 targets to source precision and compare 19 more, and 14 discrepancy records are preserved without tuning. Where a source lacks inputs, the target is recorded as blocked with the missing parameters named. The framework's own failures, among them a verification step that rewrote 20 tracked result files, are reported as evidence together with how each was corrected or bounded.

I believe the paper fits the scope of the journal because it concerns the design, verification and reproducibility of engineering software: how computational evidence derived from published engineering methods can be made traceable, independently checked and verifiable without being altered by its own verification.

The software, study records and the scripts that generate the manuscript's tables are openly available under the Apache License 2.0 and archived on Zenodo (version 0.2.0, https://doi.org/10.5281/zenodo.23017727). Copyrighted source publications are not redistributed.

The manuscript is original, has not been published previously, and is not under consideration for publication elsewhere. I am the sole author. I declare no competing interests, and the research received no specific funding. The use of generative AI tools is disclosed in the manuscript.

Thank you for considering this submission.

Yours sincerely,

Zhiqiang Gu
Independent researcher, Norway
Zhiqiang.gu214@gmail.com
