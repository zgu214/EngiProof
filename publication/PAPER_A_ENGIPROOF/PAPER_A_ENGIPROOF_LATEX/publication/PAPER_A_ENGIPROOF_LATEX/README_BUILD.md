# EngiProof journal manuscript - LaTeX draft v0.1

This is a generic, compile-ready journal manuscript draft. It intentionally does **not** use a publisher-specific class yet. After P42/P43 establish stronger heterogeneous evidence, select the target journal and migrate the content to that journal's template.

## Windows

From this folder:

```bat
BUILD_LATEX_WINDOWS.bat
```

or directly:

```bat
pdflatex -interaction=nonstopmode -halt-on-error main.tex
biber main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

## Linux/macOS

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
biber main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

## Draft rules

- Do not turn `OPEN` discrepancies into source errors without an erratum/author clarification.
- Do not add extraction accuracy/generalization percentages before the benchmark corpus is fixed.
- Do not add publisher raster figures to the repository.
- Generate final manuscript tables from machine-readable EngiProof evidence before submission.
- Keep `HANDOVER_CURRENT.md`, `CHAT_COMPACT_CURRENT.md`, and the publication claim-evidence matrix synchronized at meaningful checkpoints.
