@echo off
setlocal
echo === EngiProof v0.2.0-dev7 source identity + split captions ===
python -m pip install -e .
if errorlevel 1 exit /b 1
engiproof --version
python -m unittest tests.test_ingestion_identity_and_split_captions tests.test_ingestion_publisher_styles tests.test_ingestion -v
if errorlevel 1 exit /b 1
echo.
echo Re-run P42 audit-source and extract-structures after this verification.
echo === DEV7 VERIFY PASS ===
