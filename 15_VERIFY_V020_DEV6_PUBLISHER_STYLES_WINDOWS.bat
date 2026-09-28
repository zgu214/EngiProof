@echo off
setlocal
echo === EngiProof v0.2.0-dev6 publisher-style extraction ===
python -m pip install -e .
if errorlevel 1 exit /b 1
engiproof --version
python -m unittest tests.test_ingestion_publisher_styles tests.test_ingestion tests.test_evidence_graph_sync -v
if errorlevel 1 exit /b 1
echo.
echo Re-run P41 enrichment/structure extraction after this verification.
echo === DEV6 VERIFY PASS ===
