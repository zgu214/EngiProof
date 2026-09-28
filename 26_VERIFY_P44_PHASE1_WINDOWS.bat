@echo off
setlocal
echo === EngiProof P44 Phase 1 contact validation ===

echo [1/8] Install editable package
python -m pip install -e .
if errorlevel 1 goto :fail

echo [2/8] P44 Phase 1 tests
python -m unittest tests.test_p44_phase1 -v
if errorlevel 1 goto :fail

echo [3/8] Run P44 calculation
python papers\P44\run_calculation.py
if errorlevel 1 goto :fail

echo [4/8] Show Phase 1 summary
call engiproof tool P44 phase1_contact_validation_summary
if errorlevel 1 goto :fail

echo [5/8] Verify / discrepancy audit
call engiproof verify P44
if errorlevel 1 goto :fail
call engiproof discrepancy-audit P44

echo [6/8] Sync + audit evidence graph
call engiproof graph-sync P44
if errorlevel 1 goto :fail
call engiproof graph-audit P44
if errorlevel 1 goto :fail

echo [7/8] Pipeline
call engiproof pipeline P44

echo [8/8] Continuity audit + checkpoint
call engiproof continuity-audit
if errorlevel 1 goto :fail
call engiproof checkpoint --bundle
if errorlevel 1 goto :fail

echo.
echo === P44 PHASE1 VERIFY PASS ===
exit /b 0

:fail
echo.
echo === P44 PHASE1 VERIFY FAIL ===
echo ERRORLEVEL=%ERRORLEVEL%
exit /b 1
