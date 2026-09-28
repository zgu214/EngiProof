# Paper A: submission package for Advances in Engineering Software

Build it from the manuscript directory:

```bash
cd publication/PAPER_A_ENGIPROOF/PAPER_A_ENGIPROOF_LATEX/publication/PAPER_A_ENGIPROOF_LATEX
python scripts/build_submission_package.py
```

Requirements: TeX Live with `elsarticle`, `python-docx` and LibreOffice (`soffice`, for the cover-letter PDF). The output goes to `out/`, which is not tracked. Rebuild it from the commit you submit, and keep `out/MANIFEST.txt`, which records that commit and the SHA-256 of every file.

## Files

| File | Upload as | Source |
|---|---|---|
| `EngiProof_PaperA_manuscript.pdf` | Manuscript (PDF) | clean build of `main.tex` |
| `EngiProof_PaperA_latex_source.zip` | LaTeX source files | `main.tex`, `sections/`, `generated/`, `references.bib`, `main.bbl`. The script checks that the zip compiles on its own to the same page count |
| `EngiProof_PaperA_highlights.docx` | Highlights (separate editable file) | read from `main.tex`: 3–5 items, each ≤ 85 characters |
| `EngiProof_PaperA_declaration_of_interest.docx` | Declaration of interest | same wording as the manuscript's competing-interest statement |
| `EngiProof_PaperA_cover_letter.docx` / `.pdf` | Cover letter | `cover_letter.md` in this folder (edit that file, not the .docx) |

## Review model

The package assumes single-anonymized review (owner decision, 28 September 2026). Author details stay in the manuscript, and no separate title page is prepared.

## Checks the build runs

- Generated tables are current (`build_tables.py --check`), and the facts check passes (`check_manuscript_facts.py`).
- Highlights: 3–5 items, each ≤ 85 characters. Keywords: ≤ 6.
- The manuscript builds with 0 undefined references, and the source zip compiles to the same number of pages.
- The cover letter fits on one page.

## Before submitting (author)

- [x] Originality: the author confirmed on 28 September 2026 that the manuscript has not been published previously and is not under consideration elsewhere, as the cover letter states.
- [ ] Read and sign the cover letter.
- [ ] Article type in Editorial Manager: research article.
- [ ] Copy the title, abstract and keywords from the manuscript into the submission form.
- [ ] Upload the files in the table above, with the file types shown.
- [ ] Suggested or opposed reviewers are optional; none are prepared.
- [ ] Complete Elsevier's declarations step. The answers must match the manuscript: no competing interests, no specific funding, generative-AI use disclosed.
