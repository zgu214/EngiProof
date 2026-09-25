@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Run 00_SETUP_WINDOWS.bat first.
  pause
  exit /b 1
)
call engiproof.cmd doctor || exit /b 1
call engiproof.cmd verify-all || exit /b 1
".venv\Scripts\python.exe" -m unittest discover -s tests -v || exit /b 1
".venv\Scripts\python.exe" tools\build_report.py || exit /b 1
echo.
echo VERIFY PASS
pause
