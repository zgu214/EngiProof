@echo off
setlocal
echo === EngiProof P42 Phase 3 / freeze verification ===

echo [1/8] Install editable package
python -m pip install -e .
if errorlevel 1 goto :fail

echo [2/8] Run P42 Phase 1-3 tests
python -m unittest tests.test_p42_phase1 tests.test_p42_phase2 tests.test_p42_phase3 -v
if errorlevel 1 goto :fail

echo [3/8] Run P42 calculation
python papers\P42\run_calculation.py
if errorlevel 1 goto :fail

echo [4/8] Show Phase 3 summary
call engiproof tool P42 phase3_axisymmetric_and_moment_summary
if errorlevel 1 goto :fail

echo [5/8] Audit discrepancies
call engiproof discrepancy-audit P42

echo [6/8] Sync evidence graph
call engiproof graph-sync P42
if errorlevel 1 goto :fail

echo [7/8] Audit evidence graph
call engiproof graph-audit P42
if errorlevel 1 goto :fail

echo [8/8] Show pipeline
call engiproof pipeline P42
if errorlevel 1 goto :fail

echo.
echo === P42 PHASE3 VERIFY PASS ===
exit /b 0

:fail
echo.
echo === P42 PHASE3 VERIFY FAIL ===
echo ERRORLEVEL=%ERRORLEVEL%
exit /b 1
