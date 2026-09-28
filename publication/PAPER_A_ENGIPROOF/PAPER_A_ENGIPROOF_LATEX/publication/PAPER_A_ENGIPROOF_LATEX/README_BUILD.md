# EngiProof Paper A: LaTeX build

Target journal: **Advances in Engineering Software** (Elsevier). The manuscript uses the `elsarticle` class (`preprint,12pt`) and the numbered Elsevier BibTeX style `elsarticle-num`.

## Requirements

TeX Live or MiKTeX with the `elsarticle`, `lm` (Latin Modern) and `pgf/tikz` packages. On Debian/Ubuntu these come from `texlive-publishers` and `lmodern`.

## Build

Windows:

```bat
BUILD_LATEX_WINDOWS.bat
```

Linux/macOS:

```bash
latexmk -pdf main.tex
# or: pdflatex main && bibtex main && pdflatex main && pdflatex main
```

## Generated content and checks

- Appendix A comes from `publication/PAPER_A_ENGIPROOF/CLAIM_EVIDENCE_MATRIX.md`:
  ```bash
  python scripts/build_claim_appendix.py
  ```
- Style-only edits are guarded by `scripts/prose_audit.py [REV]`. It compares numbers, citations, cross-references, evidence identifiers, status macros, mathematics and table contents with a git revision; column specs and line-break hints are treated as layout.

- The per-study evidence table (`tab:evidence`), the cross-environment table (`tab:crossenv`) and `generated/facts.json` are generated from repository data; the facts check then confirms that the prose numbers match:
  ```bash
  python scripts/build_tables.py            # add --check to fail on stale output
  python scripts/check_manuscript_facts.py  # PASS / FAIL / OPEN per stated fact
  ```

## Author items

Text marked **[author to confirm]** can only be confirmed by the author: affiliation, CRediT statement, competing interests, funding and the generative-AI declaration.

## Draft rules

- Do not turn `OPEN` discrepancies into source errors without an erratum or author clarification.
- Do not add extraction-accuracy or generalisation figures.
- Do not add publisher raster figures to the repository.
- Regenerate the generated tables and Appendix A from the tagged release before submission.
