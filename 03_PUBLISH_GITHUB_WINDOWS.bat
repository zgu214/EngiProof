@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
where git >nul 2>nul || (echo ERROR: git not found.& pause & exit /b 1)
where gh >nul 2>nul || (echo ERROR: GitHub CLI gh not found. See docs\GITHUB_RELEASE.md for manual git commands.& pause & exit /b 1)
gh auth status || (echo Run: gh auth login& pause& exit /b 1)
set /p REPO=GitHub repository name [EngiProof]: 
if "%REPO%"=="" set REPO=EngiProof
set /p VIS=Visibility public/private [private]: 
if "%VIS%"=="" set VIS=private
if /I not "%VIS%"=="public" if /I not "%VIS%"=="private" (echo Visibility must be public or private.& pause& exit /b 1)
if /I "%VIS%"=="public" (
  echo WARNING: public release is irreversible in practice once others clone it.
  echo Confirm no confidential/client/source-PDF files are present.
  set /p OK=Type PUBLISH to continue: 
  if not "!OK!"=="PUBLISH" exit /b 2
)
if not exist .git git init
git branch -M main
git add .
git commit -m "EngiProof v0.1.0 initial engineering evidence release" 2>nul || echo No new commit created or commit already exists.
gh repo create "%REPO%" --%VIS% --source=. --remote=origin --push || exit /b 1
git tag -a v0.1.0 -m "EngiProof v0.1.0" 2>nul || echo Tag v0.1.0 already exists.
git push origin v0.1.0

echo GitHub publication completed.
pause
