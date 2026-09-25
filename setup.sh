#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
engiproof doctor
python -m unittest discover -s tests -v
python tools/build_report.py
echo "EngiProof v0.1.0 SETUP PASS"
