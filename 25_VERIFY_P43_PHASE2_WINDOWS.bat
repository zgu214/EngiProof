@echo off
setlocal
echo === EngiProof P43 Phase 2 full matrix / freeze gate ===
echo [1/8] Install editable package
python -m pip install -e .
if errorlevel 1 goto :fail
echo [2/8] P43 Phase 1-2 tests
python -m unittest tests.test_p43_phase1 tests.test_p43_phase2 -v
if errorlevel 1 goto :fail
echo [3/8] Run P43 calculation
python papers\P43\run_calculation.py
if errorlevel 1 goto :fail
echo [4/8] Show Phase 2 summary
call engiproof tool P43 phase2_full_matrix_summary
if errorlevel 1 goto :fail
echo [5/8] Discrepancy audit
call engiproof discrepancy-audit P43
echo [6/8] Sync + audit evidence graph
call engiproof graph-sync P43
if errorlevel 1 goto :fail
call engiproof graph-audit P43
if errorlevel 1 goto :fail
echo [7/8] Pipeline
call engiproof pipeline P43
if errorlevel 1 goto :fail
echo [8/8] Continuity audit + checkpoint
call engiproof continuity-audit
if errorlevel 1 goto :fail
call engiproof checkpoint --bundle
if errorlevel 1 goto :fail
echo.
echo === P43 PHASE2 VERIFY PASS ===
exit /b 0
:fail
echo.
echo === P43 PHASE2 VERIFY FAIL ===
echo ERRORLEVEL=%ERRORLEVEL%
exit /b 1
