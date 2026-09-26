@echo off
setlocal
where pdflatex >nul 2>nul
if errorlevel 1 (
  echo ERROR: pdflatex not found on PATH.
  echo Install MiKTeX or TeX Live, then retry.
  exit /b 1
)
where biber >nul 2>nul
if errorlevel 1 (
  echo ERROR: biber not found on PATH.
  echo Install the biber package in your TeX distribution, then retry.
  exit /b 1
)
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if errorlevel 1 exit /b 1
biber main
if errorlevel 1 exit /b 1
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if errorlevel 1 exit /b 1
pdflatex -interaction=nonstopmode -halt-on-error main.tex
if errorlevel 1 exit /b 1
echo.
echo === ENGIPROOF LATEX DRAFT BUILD PASS ===
echo Output: main.pdf
