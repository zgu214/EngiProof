@echo off
setlocal
echo === EngiProof: record text-free ingestion summaries (Paper A G3) ===
echo Reads local gitignored intakes; writes engiproof\studies\PXX\ingestion_summary.json (hashes, counts, statuses only).
echo Source format is detected from 01_doc\^<canonical_pdf^> when present and its SHA-256 matches the intake fingerprint.

python -m pip install -e .
if errorlevel 1 goto :fail

if exist engiproof\intake\P40\ingestion.json (
  echo [P40] summarising local intake
  call engiproof ingestion-summary P40 --write
  if errorlevel 1 goto :fail
) else (
  echo [P40] no local intake - existing explicit record kept
)

if exist engiproof\intake\P41\ingestion.json (
  echo [P41] summarising local intake
  call engiproof ingestion-summary P41 --write
  if errorlevel 1 goto :fail
) else (
  echo [P41] no local intake - existing explicit record kept
)

if exist engiproof\intake\P42\ingestion.json (
  echo [P42] summarising local intake
  call engiproof ingestion-summary P42 --write
  if errorlevel 1 goto :fail
) else (
  echo [P42] no local intake - existing explicit record kept
)

if exist engiproof\intake\P43\ingestion.json (
  echo [P43] summarising local intake
  call engiproof ingestion-summary P43 --write
  if errorlevel 1 goto :fail
) else (
  echo [P43] no local intake - existing explicit record kept
)

if exist engiproof\intake\P44\ingestion.json (
  echo [P44] summarising local intake
  call engiproof ingestion-summary P44 --write
  if errorlevel 1 goto :fail
) else (
  echo [P44] no local intake - existing explicit record kept
)

echo [audit]
call engiproof ingestion-summary-audit
if errorlevel 1 goto :fail

echo [tests]
python -m unittest tests.test_ingestion_summary -v
if errorlevel 1 goto :fail

git status --short engiproof/studies
echo === INGESTION SUMMARIES RECORDED - review the diff, then commit ===
exit /b 0

:fail
echo === INGESTION SUMMARY RECORDING FAILED ===
exit /b 1
