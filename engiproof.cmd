@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" run_engiproof.py %*
  exit /b %errorlevel%
)

echo ERROR: EngiProof local environment not found.
echo Run 00_SETUP_WINDOWS.bat once, then run this command again.
echo.
echo Example:
echo   engiproof tool P12 table4_fit_force_MN --params "{\"beta\":0.6,\"clearance_mm\":12}"
exit /b 1
