from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def project_root() -> Path:
    override = os.environ.get("ENGIPROOF_PROJECT_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    here = Path.cwd().resolve()
    for p in [here, *here.parents]:
        if (p / "engiproof" / "registry.json").is_file() and (p / "papers").is_dir():
            return p
    return Path(__file__).resolve().parents[2]


def data_root() -> Path:
    return project_root() / "engiproof"


def study_root() -> Path:
    return data_root() / "studies"


def _jsonable(value: Any) -> Any:
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def load_registry() -> dict[str, Any]:
    return json.loads((data_root() / "registry.json").read_text(encoding="utf-8"))


def list_studies() -> list[dict[str, Any]]:
    return [load_manifest(pid) for pid in load_registry()["studies"]]


def load_manifest(paper_id: str) -> dict[str, Any]:
    pid = paper_id.upper()
    path = study_root() / pid / "study.json"
    if not path.is_file():
        raise KeyError(f"No live EngiProof study for {pid}.")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_function(module_rel: str, function_name: str):
    root = project_root()
    path = root / module_rel
    if not path.is_file():
        raise FileNotFoundError(path.relative_to(root) if path.is_relative_to(root) else path)
    spec = importlib.util.spec_from_file_location(
        f"engiproof_{path.stem}_{abs(hash(str(path)))}", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {module_rel}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def invoke_tool(paper_id: str, tool_name: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = load_manifest(paper_id)
    tool = next((t for t in manifest.get("tools", []) if t["name"] == tool_name), None)
    if tool is None:
        raise KeyError(f"Tool {tool_name!r} is not exposed by {manifest['paper_id']}.")
    fn = _load_function(tool["module"], tool["function"])
    value = fn(**(params or {}))
    return {
        "engiproof_schema": manifest["schema_version"],
        "paper_id": manifest["paper_id"],
        "tool": tool_name,
        "result": _jsonable(value),
        "returns": tool.get("returns"),
        "evidence": tool.get("evidence"),
        "evidence_class": tool.get("evidence_class"),
        "evidence_status": manifest.get("evidence_status"),
        "limitations": manifest.get("limitations", []),
    }


def run_study(paper_id: str) -> dict[str, Any]:
    root = project_root()
    manifest = load_manifest(paper_id)
    runner = root / manifest["runner"]
    if not runner.is_file():
        return {"paper_id": manifest["paper_id"], "status": "FAIL", "reason": f"Missing runner: {manifest['runner']}"}
    proc = subprocess.run([sys.executable, str(runner)], cwd=root, capture_output=True, text=True)
    return {
        "paper_id": manifest["paper_id"],
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "result_files": manifest.get("result_files", []),
        "evidence_status": manifest.get("evidence_status"),
    }


def verify_study(paper_id: str) -> dict[str, Any]:
    root = project_root()
    manifest = load_manifest(paper_id)
    required = [manifest["runner"], manifest["source_contract"], *manifest.get("result_files", [])]
    missing = [rel for rel in required if not (root / rel).is_file()]

    tests = []
    for test in manifest.get("verification_tests", []):
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", test, "-v"],
            cwd=root,
            env={**os.environ, "PYTHONPATH": str(root / "src")},
            capture_output=True,
            text=True,
        )
        tests.append({
            "test": test,
            "returncode": proc.returncode,
            "passed": proc.returncode == 0,
            "output": (proc.stdout + proc.stderr).strip(),
        })

    source = manifest.get("source", {})
    source_name = source.get("canonical_pdf")
    expected = source.get("sha256")
    candidates = [root / "01_doc" / source_name, root / "literature" / source_name] if source_name else []
    source_path = next((p for p in candidates if p.is_file()), None)
    source_check = {"expected_sha256": expected, "present": bool(source_path)}
    if source_path:
        actual = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_check.update({
            "path": str(source_path.relative_to(root)),
            "actual_sha256": actual,
            "matches": actual == expected,
        })

    all_tests = all(t["passed"] for t in tests)
    if missing or not all_tests or (source_path and source_check.get("matches") is False):
        status = "FAIL"
    elif not source_path:
        status = "PASS_SOURCE_EXTERNAL"
    else:
        status = "PASS"

    return {
        "paper_id": manifest["paper_id"],
        "status": status,
        "evidence_status": manifest.get("evidence_status"),
        "missing_required_files": missing,
        "source_check": source_check,
        "tests": tests,
        "limitations": manifest.get("limitations", []),
    }


def verify_all() -> dict[str, Any]:
    items = [verify_study(m["paper_id"]) for m in list_studies()]
    good = {"PASS", "PASS_SOURCE_EXTERNAL"}
    return {
        "status": "PASS" if all(x["status"] in good for x in items) else "FAIL",
        "studies": items,
    }


def result_snapshot(paper_id: str) -> dict[str, Any]:
    root = project_root()
    manifest = load_manifest(paper_id)
    items = []
    for rel in manifest.get("result_files", []):
        path = root / rel
        item: dict[str, Any] = {"path": rel, "present": path.is_file()}
        if path.is_file():
            item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            if path.suffix.lower() == ".json":
                item["data"] = json.loads(path.read_text(encoding="utf-8"))
        items.append(item)
    return {"paper_id": manifest["paper_id"], "evidence_status": manifest.get("evidence_status"), "results": items}


def doctor() -> dict[str, Any]:
    root = project_root()
    checks = {
        "registry": (root / "engiproof" / "registry.json").is_file(),
        "papers_dir": (root / "papers").is_dir(),
        "results_dir": (root / "results").is_dir(),
        "tests_dir": (root / "tests").is_dir(),
    }
    try:
        import numpy as np
        numpy_version = np.__version__
        checks["numpy"] = True
    except Exception:
        numpy_version = None
        checks["numpy"] = False
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "framework": "EngiProof",
        "version": "0.1.0",
        "python": sys.version.split()[0],
        "numpy": numpy_version,
        "project_root": ".",
        "checks": checks,
    }
