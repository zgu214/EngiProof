@echo off
setlocal
echo === EngiProof P41 reproduction checkpoint ===
python -m pip install -e .
if errorlevel 1 exit /b 1
engiproof --version
python -m unittest tests.test_p41_engiproof tests.test_ingestion_publisher_styles -v
if errorlevel 1 exit /b 1
python papers\P41\run_calculation.py
if errorlevel 1 exit /b 1
engiproof verify P41
engiproof discrepancy-audit P41
engiproof graph-sync P41
engiproof graph-audit P41
echo.
echo Expected: P41 remains CONDITIONAL and promotion-blocked until Table 2 inner deltaS cell is visually confirmed.
echo === P41 REPRODUCTION VERIFY PASS ===
