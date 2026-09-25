from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXCLUDED_DIRS = {
    ".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".idea", ".vscode", "private_sources", "client_data",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".pyd", ".odb", ".sim", ".pdf", ".zip"}
EXCLUDED_NAMES = {"SHA256SUMS.txt", "RELEASE_MANIFEST.json"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_public_files(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in EXCLUDED_DIRS or part.endswith(".egg-info") for part in rel.parts):
            continue
        if p.name in EXCLUDED_NAMES or p.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        yield p, rel


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="0.1.1")
    ns = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    registry = json.loads((root / "engiproof" / "registry.json").read_text(encoding="utf-8"))
    files = []
    for p, rel in iter_public_files(root):
        files.append({
            "path": rel.as_posix(),
            "sha256": sha256(p),
            "size_bytes": p.stat().st_size,
        })

    manifest = {
        "project": "EngiProof",
        "version": ns.version,
        "date": "2026-09-25",
        "tagline": "From Published Research to Verified Engineering",
        "live_studies": registry.get("studies", []),
        "source_pdfs_included": False,
        "engineering_qualification_granted": False,
        "test_command": "python -m unittest discover -s tests -v",
        "verification_command": "engiproof verify-all",
        "files": files,
    }
    manifest_path = root / "RELEASE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    checksum_rows = []
    for p, rel in iter_public_files(root):
        checksum_rows.append(f"{sha256(p)}  {rel.as_posix()}")
    checksum_rows.append(f"{sha256(manifest_path)}  RELEASE_MANIFEST.json")
    (root / "SHA256SUMS.txt").write_text("\n".join(checksum_rows) + "\n", encoding="utf-8")

    print(f"release manifest: {manifest_path.name}")
    print(f"version: {ns.version}")
    print(f"live studies: {', '.join(registry.get('studies', []))}")
    print(f"public files hashed: {len(files) + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
