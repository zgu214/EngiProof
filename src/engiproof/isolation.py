"""Non-mutating verification: isolated recomputation compared against frozen evidence.

Design rule: verification must not mutate the evidence being verified.

* Committed result artifacts are frozen evidence. Verification never writes to them.
* Runners and verification tests execute inside a disposable copy of the project
  (a sandbox). Whatever they write lands in the sandbox.
* The regenerated artifacts are compared with the frozen ones under a declared
  numerical tolerance. Byte identity is not required: line endings, float
  serialisation noise and checkout-dependent provenance hashes are reported, not
  hidden, and never counted as engineering differences.
* Replacing frozen evidence is a separate, explicit regeneration operation
  (``regenerate_in_place``), never part of verification and never exposed through
  MCP.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .provenance_identity import byte_variants, canonical_text_bytes, is_text_path

COMPARISON_SCHEMA = "engiproof.frozen_comparison/1.1"

# Default tolerance only absorbs floating-point serialisation/summation noise.
# A study whose recomputation is legitimately platform-sensitive (for example an
# eigen-solver) must declare its own ``verification_tolerance`` with a rationale.
DEFAULT_TOLERANCE = {"rel": 1e-9, "abs": 1e-12}

# Fields that describe the execution environment, not the evidence. They are
# reported when they differ but never compared.
ENVIRONMENT_KEYS = frozenset({"python", "numpy", "python_version", "numpy_version"})
# Deliberately NOT included: "platform". In offshore engineering a platform (TLP,
# semisubmersible, drillship, ...) is physical system data, and a change to it is
# material evidence content.

_SANDBOX_IGNORE = shutil.ignore_patterns(
    ".git", ".venv", "venv", "__pycache__", "*.pyc", ".pytest_cache", "checkpoints", "*.egg-info"
)


# ------------------------------------------------------------------ sandbox
@contextmanager
def sandbox(root: Path) -> Iterator[Path]:
    """Disposable copy of the project tree. Nothing written inside it reaches ``root``."""
    root = Path(root).resolve()
    with tempfile.TemporaryDirectory(prefix="engiproof_verify_") as td:
        box = Path(td) / "project"
        shutil.copytree(root, box, ignore=_SANDBOX_IGNORE, symlinks=True)
        yield box


def sandbox_env(box: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["ENGIPROOF_PROJECT_ROOT"] = str(box)
    env["PYTHONPATH"] = os.pathsep.join([str(box / "src"), *filter(None, [env.get("PYTHONPATH")])])
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_python(box: Path, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=box, env=sandbox_env(box), capture_output=True, text=True)


def _file_states(base: Path) -> dict[str, tuple[int, str]]:
    """(mtime_ns, sha256) per file, so rewrites with identical bytes are still seen as written."""
    out = {}
    for p in base.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts:
            out[p.relative_to(base).as_posix()] = (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
    return out


# ------------------------------------------------------------- comparison
# Classification of a difference between a regenerated and a frozen artifact.
# Ordered by severity; an artifact takes the most severe class of its components.
IDENTICAL = "IDENTICAL"
BYTE_ONLY = "BYTE_ONLY"                          # same content; bytes differ (line endings, BOM, serialisation)
ENVIRONMENT_METADATA = "ENVIRONMENT_METADATA"    # environment records or checkout-dependent provenance hashes
NUMERICAL_NONMATERIAL = "NUMERICAL_NONMATERIAL"  # numbers differ within the declared tolerance and guards
NUMERICAL_MATERIAL = "NUMERICAL_MATERIAL"        # a number crosses the declared tolerance or a rounding guard
MATERIAL_NON_NUMERIC = "MATERIAL_NON_NUMERIC"    # status/discrepancy/classification/qualification/interpretation/structure changed
SEVERITY = [IDENTICAL, BYTE_ONLY, ENVIRONMENT_METADATA, NUMERICAL_NONMATERIAL, NUMERICAL_MATERIAL, MATERIAL_NON_NUMERIC]
MATERIAL = frozenset({NUMERICAL_MATERIAL, MATERIAL_NON_NUMERIC})


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _as_float(s: str) -> float | None:
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _is_sha256(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def _fmt(x: float, decimals: int) -> str:
    return f"{x:.{decimals}f}"


class _Comparator:
    def __init__(self, tol: dict[str, Any], hash_index: dict[str, tuple[str, str]], guards: list[dict[str, Any]],
                 provenance_index: dict[str, dict[str, str]] | None = None):
        self.rel = float(tol.get("rel", DEFAULT_TOLERANCE["rel"]))
        self.abs = float(tol.get("abs", DEFAULT_TOLERANCE["abs"]))
        # Declared path-scoped recomputation tolerances, longest prefix first.
        self.paths = sorted(((str(p["path_prefix"]), float(p["rel"]), float(p["abs"])) for p in tol.get("path_tolerances", [])),
                            key=lambda x: -len(x[0]))
        self.path_scoped_values = 0
        self.hash_index = hash_index
        self.provenance_index = provenance_index or {}
        self.derived_refs: set[str] = set()
        self.guards = {g["field"]: int(g["decimals"]) for g in guards}
        self.classes: set[str] = set()
        self.numbers = 0
        self.numbers_changed = 0
        self.max_abs = 0.0
        self.max_rel = 0.0
        self.guarded_values = 0
        self.findings: list[dict[str, Any]] = []
        self.environment: list[str] = []
        self.hash_line_endings: list[str] = []

    def _material(self, cls: str, item: dict[str, Any]) -> None:
        self.classes.add(cls)
        self.findings.append({"class": cls, **item})

    def num(self, where: str, field: str | None, a: float, b: float) -> None:
        self.numbers += 1
        decimals = self.guards.get(field) if field else None
        if decimals is not None:
            self.guarded_values += 1
            if _fmt(a, decimals) != _fmt(b, decimals):
                self._material(NUMERICAL_MATERIAL, {"at": where, "rule": f"rounding guard: {decimals} decimals",
                                                    "frozen": a, "regenerated": b})
                return
        if a == b or (math.isnan(a) and math.isnan(b)):
            return
        rel_tol, abs_tol = self.rel, self.abs
        for prefix, prel, pabs in self.paths:
            if where.startswith(prefix):
                rel_tol, abs_tol = prel, pabs
                self.path_scoped_values += 1
                break
        self.numbers_changed += 1
        d = abs(a - b)
        r = d / max(abs(a), abs(b)) if max(abs(a), abs(b)) > 0 else 0.0
        self.max_abs = max(self.max_abs, d)
        self.max_rel = max(self.max_rel, r)
        if math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol):
            self.classes.add(NUMERICAL_NONMATERIAL)
        else:
            self._material(NUMERICAL_MATERIAL, {"at": where, "rule": "declared tolerance", "frozen": a,
                                                "regenerated": b, "abs_diff": d, "rel_diff": r})

    def text(self, where: str, a: str, b: str, key: str | None = None) -> None:
        if a == b:
            return
        if key in ENVIRONMENT_KEYS:
            self.classes.add(ENVIRONMENT_METADATA)
            self.environment.append(f"{where}: {a} -> {b}")
            return
        if _is_sha256(a) and _is_sha256(b):
            fa, fb = self.hash_index.get(a), self.hash_index.get(b)
            if fa and fb and fa[0] == fb[0] and fa[1] != fb[1]:
                self.classes.add(ENVIRONMENT_METADATA)
                self.hash_line_endings.append(f"{where}: {fa[0]} ({fa[1]} vs {fb[1]} rendering)")
                return
            pa, pb = self.provenance_index.get(a), self.provenance_index.get(b)
            if pa and pb and pa.get("frozen") and pb.get("regenerated") and pa["frozen"] == pb["regenerated"]:
                # Provenance hash of a regenerated artifact: it changes exactly when that artifact
                # changes, so it inherits that artifact's own classification (resolved by the caller).
                self.derived_refs.add(pa["frozen"])
                return
        self._material(MATERIAL_NON_NUMERIC, {"at": where, "frozen": a, "regenerated": b})

    def json_value(self, where: str, a: Any, b: Any, key: str | None = None) -> None:
        if isinstance(a, dict) and isinstance(b, dict):
            if set(a) != set(b):
                self._material(MATERIAL_NON_NUMERIC, {"at": where or "$", "structure": "keys differ",
                                                      "only_frozen": sorted(set(a) - set(b)), "only_regenerated": sorted(set(b) - set(a))})
            for k in sorted(set(a) & set(b)):
                self.json_value(f"{where}.{k}", a[k], b[k], k)
        elif isinstance(a, list) and isinstance(b, list):
            if len(a) != len(b):
                self._material(MATERIAL_NON_NUMERIC, {"at": where or "$", "structure": f"list length {len(a)} vs {len(b)}"})
            for i, (x, y) in enumerate(zip(a, b)):
                self.json_value(f"{where}[{i}]", x, y, key)
        elif _is_number(a) and _is_number(b):
            self.num(where, key, float(a), float(b))
        elif isinstance(a, str) and isinstance(b, str):
            self.text(where, a, b, key)
        elif a != b:
            self._material(MATERIAL_NON_NUMERIC, {"at": where or "$", "frozen": a, "regenerated": b})

    def csv_text(self, a: str, b: str) -> None:
        ra, rb = list(csv.reader(io.StringIO(a))), list(csv.reader(io.StringIO(b)))
        if len(ra) != len(rb):
            self._material(MATERIAL_NON_NUMERIC, {"at": "rows", "structure": f"{len(ra)} vs {len(rb)} rows"})
        header = ra[0] if ra else []
        for i, (x, y) in enumerate(zip(ra, rb)):
            if len(x) != len(y):
                self._material(MATERIAL_NON_NUMERIC, {"at": f"row {i}", "structure": f"{len(x)} vs {len(y)} columns"})
                continue
            for j, (u, v) in enumerate(zip(x, y)):
                col = header[j] if i and j < len(header) else None
                fu, fv = (_as_float(u), _as_float(v)) if i else (None, None)
                if fu is not None and fv is not None:
                    self.num(f"row {i} [{col}]", col, fu, fv)
                else:
                    self.text(f"row {i} [{col if col is not None else j}]", u, v, col)


def build_hash_index(files: list[Path]) -> dict[str, tuple[str, str]]:
    """Map SHA-256 of the LF and CRLF renderings of each text file to (file name, variant)."""
    index: dict[str, tuple[str, str]] = {}
    for p in files:
        if not p.is_file() or not is_text_path(p):
            continue
        try:
            for variant, h in byte_variants(p).items():
                index[h] = (p.name, variant)
        except UnicodeDecodeError:
            continue
    return index


def compare_artifact(frozen: Path, regenerated: Path, tolerance: dict[str, Any] | None = None,
                     hash_index: dict[str, tuple[str, str]] | None = None,
                     rounding_guards: list[dict[str, Any]] | None = None,
                     provenance_index: dict[str, dict[str, str]] | None = None) -> dict[str, Any]:
    """Compare one regenerated artifact with its frozen counterpart and classify the difference.

    ``classification`` is the most severe of the component classes found. It is
    material (verification fails) when a number crosses the declared tolerance or a
    rounding guard (NUMERICAL_MATERIAL), or when any non-numeric evidence content or
    structure changes (MATERIAL_NON_NUMERIC).
    """
    a, b = frozen.read_bytes(), regenerated.read_bytes()
    if a == b:
        return {"classification": IDENTICAL, "material": False}
    cmp = _Comparator(tolerance or DEFAULT_TOLERANCE, hash_index or {}, rounding_guards or [], provenance_index)
    try:
        ta, tb = canonical_text_bytes(a).decode("utf-8"), canonical_text_bytes(b).decode("utf-8")
    except UnicodeDecodeError:
        cmp._material(MATERIAL_NON_NUMERIC, {"at": "$", "structure": "binary content differs"})
        ta = tb = None
    suffix = frozen.suffix.lower()
    if ta is not None and ta != tb:
        if suffix == ".json":
            try:
                ja, jb = json.loads(ta), json.loads(tb)
            except json.JSONDecodeError as exc:
                cmp._material(MATERIAL_NON_NUMERIC, {"at": "$", "structure": f"invalid JSON: {exc}"})
            else:
                cmp.json_value("", ja, jb)
        elif suffix in {".csv", ".tsv"}:
            cmp.csv_text(ta, tb)
        else:
            cmp._material(MATERIAL_NON_NUMERIC, {"at": "$", "structure": "text differs"})
    classes = set(cmp.classes)
    line_endings_differ = (b"\r\n" in a) != (b"\r\n" in b) or a.startswith(b"\xef\xbb\xbf") != b.startswith(b"\xef\xbb\xbf")
    if line_endings_differ or not classes:
        # Bytes differ but no value, text or structure difference was found:
        # line endings, BOM or serialisation only.
        classes.add(BYTE_ONLY)
    classification = max(classes, key=SEVERITY.index)
    out: dict[str, Any] = {
        "classification": classification,
        "material": classification in MATERIAL,
        "components": sorted(classes, key=SEVERITY.index),
        "numbers_compared": cmp.numbers,
        "numbers_changed": cmp.numbers_changed,
        "max_abs_diff": cmp.max_abs,
        "max_rel_diff": cmp.max_rel,
    }
    if cmp.guarded_values:
        out["rounding_guarded_values"] = cmp.guarded_values
    if cmp.path_scoped_values:
        out["path_scoped_tolerance_values"] = cmp.path_scoped_values
    if cmp.derived_refs:
        out["derived_hash_refs"] = sorted(cmp.derived_refs)
    if cmp.environment:
        out["environment_fields"] = cmp.environment
    if cmp.hash_line_endings:
        out["provenance_hash_line_endings"] = cmp.hash_line_endings
    if cmp.findings:
        out["material_findings"] = cmp.findings[:20]
        out["material_finding_count"] = len(cmp.findings)
    return out


# ------------------------------------------------------ study reproduction
def study_tolerance(manifest: dict[str, Any]) -> dict[str, Any]:
    declared = manifest.get("verification_tolerance")
    if declared:
        return {"rel": float(declared["rel"]), "abs": float(declared["abs"]), "source": "study manifest",
                "purpose": declared.get("purpose"), "not_an_acceptance_tolerance": True,
                "rounding_guards": declared.get("rounding_guards", []),
                "path_tolerances": declared.get("path_tolerances", [])}
    return {**DEFAULT_TOLERANCE, "source": "default (floating-point serialisation noise only)",
            "not_an_acceptance_tolerance": True, "rounding_guards": []}


def _tol_for(tol: dict[str, Any], rel: str) -> dict[str, Any]:
    """Tolerance for one artifact: path-scoped entries apply only to the artifacts they list."""
    return {**tol, "path_tolerances": [p for p in tol.get("path_tolerances", []) if rel in p.get("artifacts", [])]}


def provenance_hash_index(root: Path, box: Path, study_rel: str) -> dict[str, dict[str, str]]:
    """Map SHA-256 renderings of study files to their relative path, for frozen and regenerated trees."""
    index: dict[str, dict[str, str]] = {}
    for label, base in (("frozen", root), ("regenerated", box)):
        d = base / study_rel
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(base).as_posix()
            hashes = {hashlib.sha256(p.read_bytes()).hexdigest()}
            if is_text_path(p):
                try:
                    hashes |= set(byte_variants(p).values())
                except UnicodeDecodeError:
                    pass
            for h in hashes:
                index.setdefault(h, {})[label] = rel
    return index


def _guards_for(tol: dict[str, Any], rel: str) -> list[dict[str, Any]]:
    return [g for g in tol.get("rounding_guards", []) if rel in g.get("artifacts", [])]


def _result_dirs(manifest: dict[str, Any]) -> set[str]:
    """Result directories of a study: papers/<id>/results/ plus the directories of declared result files."""
    dirs = {f"papers/{manifest['paper_id']}/results/"}
    for rel in manifest.get("result_files", []):
        parent = Path(rel).parent.as_posix()
        if parent not in ("", "."):
            dirs.add(parent + "/")
    return dirs


def _in_result_dir(rel: str, dirs: set[str]) -> bool:
    return any(rel.startswith(d) for d in dirs)


def runtime_environment() -> dict[str, Any]:
    """The Python/NumPy/platform of the running verification (ENVIRONMENT_METADATA, never material)."""
    import platform
    try:
        import numpy
        numpy_version = numpy.__version__
    except Exception:  # pragma: no cover - numpy is a hard dependency
        numpy_version = None
    return {"python_version": platform.python_version(), "python_implementation": platform.python_implementation(),
            "numpy_version": numpy_version, "os": platform.system(), "os_release": platform.release(),
            "machine": platform.machine()}


def declared_environment(paths: list[Path], root: Path) -> dict[str, dict[str, Any]]:
    """Environment keys that frozen JSON artifacts themselves declare (empty when none do)."""
    out: dict[str, dict[str, Any]] = {}

    def walk(node: Any, found: dict[str, Any]) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ENVIRONMENT_KEYS and not isinstance(v, (dict, list)):
                    found.setdefault(k, v)
                else:
                    walk(v, found)
        elif isinstance(node, list):
            for v in node:
                walk(v, found)

    for path in paths:
        if path.suffix.lower() != ".json" or not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        found: dict[str, Any] = {}
        walk(data, found)
        if found:
            out[path.relative_to(root).as_posix()] = found
    return out


def reproduce_against_frozen(root: Path, manifest: dict[str, Any], box: Path) -> dict[str, Any]:
    """Run the study runner inside ``box`` and compare every artifact it writes with ``root``."""
    runner = manifest.get("runner")
    tol = study_tolerance(manifest)
    if not runner or not (box / runner).is_file():
        return {"schema_version": COMPARISON_SCHEMA, "status": "FAIL", "reason": f"missing runner: {runner}", "tolerance": tol}
    before = _file_states(box)
    proc = run_python(box, [runner])
    after = _file_states(box)
    # Union of the pre- and post-run file sets, so deletions are visible too.
    written = sorted(p for p in after if p in before and before[p] != after[p])
    created = sorted(p for p in after if p not in before)
    deleted = sorted(p for p in before if p not in after)
    result_dirs = _result_dirs(manifest)
    allowed = set(manifest.get("verification_allowed_artifact_changes", []))
    study_dir = box / "papers" / manifest["paper_id"]
    index = build_hash_index([p for p in study_dir.rglob("*") if p.is_file()])
    compared, new_files = [], []
    counts = {c: 0 for c in SEVERITY}
    max_abs = max_rel = 0.0
    for rel in created:
        if (root / rel).is_file():
            written.append(rel)  # absent in the sandbox before the run but frozen in the tree
        elif _in_result_dir(rel, result_dirs) and rel not in allowed:
            counts[MATERIAL_NON_NUMERIC] += 1
            compared.append({"path": rel, "classification": MATERIAL_NON_NUMERIC, "material": True,
                             "structure": "result artifact created that is not in the frozen evidence"})
        else:
            new_files.append(rel)
    for rel in deleted:
        if _in_result_dir(rel, result_dirs) and rel not in allowed:
            counts[MATERIAL_NON_NUMERIC] += 1
            compared.append({"path": rel, "classification": MATERIAL_NON_NUMERIC, "material": True,
                             "structure": "frozen result artifact deleted by the runner"})
        else:
            new_files.append(f"(deleted) {rel}")
    prov = provenance_hash_index(root, box, f"papers/{manifest['paper_id']}")
    regenerated: dict[str, dict[str, Any]] = {}
    for rel in sorted(written):
        regenerated[rel] = {"path": rel, **compare_artifact(root / rel, box / rel, _tol_for(tol, rel), index, _guards_for(tol, rel), prov)}
    # A provenance hash inherits the classification of the artifact it identifies.
    for res in regenerated.values():
        refs = res.get("derived_hash_refs") or []
        if not refs:
            continue
        inherited = []
        for ref in refs:
            target = regenerated.get(ref)
            inherited.append(target["classification"] if target else MATERIAL_NON_NUMERIC)
        worst = max([res["classification"], *inherited], key=SEVERITY.index)
        res["derived_hash_inherited"] = dict(zip(refs, inherited))
        if worst != res["classification"]:
            res["classification"], res["material"] = worst, worst in MATERIAL
            res["components"] = sorted(set(res.get("components", [])) | {worst}, key=SEVERITY.index)
    for rel in sorted(regenerated):
        res = regenerated[rel]
        counts[res["classification"]] += 1
        max_abs = max(max_abs, res.get("max_abs_diff", 0.0))
        max_rel = max(max_rel, res.get("max_rel_diff", 0.0))
        compared.append(res)
    material = counts[NUMERICAL_MATERIAL] + counts[MATERIAL_NON_NUMERIC]
    status = "FAIL" if proc.returncode != 0 or material else "PASS"
    return {
        "schema_version": COMPARISON_SCHEMA,
        "status": status,
        "runner": runner,
        "runner_returncode": proc.returncode,
        "runner_stderr": proc.stderr.strip()[-2000:] if proc.returncode else "",
        "tolerance": tol,
        "artifacts_regenerated": len(written),
        "result_artifacts_created": [a["path"] for a in compared if a.get("structure", "").startswith("result artifact created")],
        "result_artifacts_deleted": [a["path"] for a in compared if a.get("structure", "").startswith("frozen result artifact deleted")],
        "classification_counts": counts,
        "material_artifacts": material,
        "max_abs_diff": max_abs,
        "max_rel_diff": max_rel,
        "non_evidence_file_changes": new_files,
        "verification_environment": runtime_environment(),
        "frozen_environment_declared": declared_environment([root / rel for rel in sorted(written)], root),
        "artifacts": compared,
        "rule": ("Frozen evidence is compared, never overwritten. Tolerances here define recomputation "
                 "equivalence only; they are not engineering acceptance or validation tolerances."),
    }


# ------------------------------------------------------ explicit regeneration
def tracked_file_hashes(root: Path) -> dict[str, str]:
    """SHA-256 of every tracked file (git), or of every project file when git is unavailable."""
    root = Path(root).resolve()
    try:
        names = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, text=True, check=True).stdout.split("\0")
        files = [root / n for n in names if n]
    except (OSError, subprocess.CalledProcessError):
        files = [p for p in root.rglob("*") if p.is_file() and not ({".git", ".venv", "__pycache__", "checkpoints"} & set(p.relative_to(root).parts))]
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}


def regenerate_in_place(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Explicitly replace committed evidence by running the study runner in the real tree.

    This is the only operation that writes frozen evidence. It is never called by
    verification and is not exposed through MCP. Review the reported changes before
    committing them.
    """
    root = Path(root).resolve()
    runner = manifest.get("runner")
    if not runner or not (root / runner).is_file():
        return {"paper_id": manifest.get("paper_id"), "status": "FAIL", "reason": f"missing runner: {runner}"}
    before = tracked_file_hashes(root)
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(root / "src"), *filter(None, [env.get("PYTHONPATH")])])
    proc = subprocess.run([sys.executable, str(root / runner)], cwd=root, env=env, capture_output=True, text=True)
    after = tracked_file_hashes(root)
    changed = [{"path": p, "before_sha256": before[p], "after_sha256": after.get(p)} for p in sorted(before) if after.get(p) != before[p]]
    return {
        "paper_id": manifest.get("paper_id"),
        "operation": "REGENERATE_IN_PLACE",
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "tracked_files_changed": changed,
        "warning": "Committed evidence was rewritten. Review with verify/compare before committing.",
    }


# ------------------------------------------------------------------ tests
def run_runner_for_test(testcase: Any, root: Path, runner_rel: str) -> tuple[subprocess.CompletedProcess, Path]:
    """Test helper: run a study runner in a sandbox that lives until the test finishes.

    Returns ``(completed_process, sandbox_root)``. Read regenerated results from
    ``sandbox_root``; the real project tree is never written.
    """
    td = tempfile.mkdtemp(prefix="engiproof_test_")
    testcase.addCleanup(shutil.rmtree, td, True)
    box = Path(td) / "project"
    shutil.copytree(Path(root).resolve(), box, ignore=_SANDBOX_IGNORE, symlinks=True)
    return run_python(box, [runner_rel]), box
