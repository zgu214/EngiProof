@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Python 3.10+ not found. Install Python and ensure py or python is on PATH.
    pause
    exit /b 1
  )
  set "PY=python"
)
if not exist .venv (
  %PY% -m venv .venv || exit /b 1
)
".venv\Scripts\python.exe" -m pip install --upgrade pip || exit /b 1
".venv\Scripts\python.exe" -m pip install -e . || exit /b 1
call engiproof.cmd doctor || exit /b 1
".venv\Scripts\python.exe" -m unittest discover -s tests -v || exit /b 1
".venv\Scripts\python.exe" tools\build_report.py || exit /b 1
echo.
echo ===============================
echo EngiProof v0.1.0 SETUP PASS
echo You can now type engiproof from THIS project folder even if the prompt shows (base).
echo Example: engiproof list
echo Open reports\index.html or run 01_DEMO_WINDOWS.bat
echo ===============================
pause
