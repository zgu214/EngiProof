@echo off
setlocal
echo === EngiProof P44 freeze / low-budget continuity hold ===

call engiproof continuity-audit
if errorlevel 1 goto :fail

call engiproof checkpoint --bundle
if errorlevel 1 goto :fail

git status -sb

echo.
echo === P44 FREEZE CHECKPOINT READY ===
exit /b 0

:fail
echo.
echo === P44 FREEZE CHECKPOINT FAIL ===
exit /b 1
