@echo off
setlocal
rem Paper A, Advances in Engineering Software (elsarticle class, elsarticle-num BibTeX style).
where pdflatex >nul 2>nul
if errorlevel 1 (
  echo ERROR: pdflatex not found on PATH. Install MiKTeX or TeX Live, then retry.
  exit /b 1
)
where bibtex >nul 2>nul
if errorlevel 1 (
  echo ERROR: bibtex not found on PATH.
  exit /b 1
)
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if errorlevel 1 exit /b 1
bibtex main
if errorlevel 1 exit /b 1
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if errorlevel 1 exit /b 1
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if errorlevel 1 exit /b 1
echo.
echo === ENGIPROOF PAPER A BUILD PASS ===
echo Output: main.pdf
