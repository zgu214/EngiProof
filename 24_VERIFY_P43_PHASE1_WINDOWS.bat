@echo off
setlocal
echo === EngiProof P43 Phase 1 eigenvalue benchmark ===

echo [1/8] Install editable package
python -m pip install -e .
if errorlevel 1 goto :fail

echo [2/8] P43 Phase 1 tests
python -m unittest tests.test_p43_phase1 -v
if errorlevel 1 goto :fail

echo [3/8] Run P43 calculation
python papers\P43\run_calculation.py
if errorlevel 1 goto :fail

echo [4/8] Show P43 Phase 1 summary
call engiproof tool P43 phase1_eigen_benchmark_summary
if errorlevel 1 goto :fail

echo [5/8] Verify study
call engiproof verify P43
if errorlevel 1 goto :fail

echo [6/8] Sync and audit evidence graph
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
echo === P43 PHASE1 VERIFY PASS ===
exit /b 0

:fail
echo.
echo === P43 PHASE1 VERIFY FAIL ===
echo ERRORLEVEL=%ERRORLEVEL%
exit /b 1
