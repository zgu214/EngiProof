@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" goto :noenv

rem Run outside a parenthesised block: inside one, %errorlevel% is expanded when the
rem block is parsed (before Python runs), so every exit code would be reported as 0.
".venv\Scripts\python.exe" run_engiproof.py %*
exit /b %errorlevel%

:noenv
echo ERROR: EngiProof local environment not found.
echo Run 00_SETUP_WINDOWS.bat once, then run this command again.
echo.
echo Example:
echo   engiproof tool P12 table4_fit_force_MN --params "{\"beta\":0.6,\"clearance_mm\":12}"
exit /b 1
