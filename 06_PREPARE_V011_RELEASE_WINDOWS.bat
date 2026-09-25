@echo off
setlocal
cd /d "%~dp0"

echo === EngiProof v0.1.1 release preparation ===

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv not found. Run 00_SETUP_WINDOWS.bat first.
  exit /b 1
)

.venv\Scripts\python.exe -m pip install -e .
if errorlevel 1 exit /b 1

.venv\Scripts\python.exe -m unittest discover -s tests -v
if errorlevel 1 exit /b 1

call engiproof.cmd verify-all
if errorlevel 1 exit /b 1

.venv\Scripts\python.exe tools\build_release_manifest.py --version 0.1.1
if errorlevel 1 exit /b 1

for /f %%i in ('git ls-files "*.pdf"') do (
  echo ERROR: tracked PDF detected: %%i
  exit /b 1
)

for /f %%i in ('git ls-files "*.zip"') do (
  echo ERROR: tracked ZIP detected: %%i
  exit /b 1
)

git diff --check
if errorlevel 1 exit /b 1

echo.
echo === RELEASE PREP PASS ===
echo Review: git status -sb
echo Then commit on develop before opening the release PR.
endlocal
