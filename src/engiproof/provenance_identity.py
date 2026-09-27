"""Checkout-independent file identity for provenance records.

Historical EngiProof provenance hashes are raw SHA-256 over the bytes of the
checkout that produced them. For text files those bytes depend on the checkout's
line endings (a Windows ``core.autocrlf`` checkout yields CRLF, a Linux checkout
LF), so identical content can carry two different hashes. Historical byte hashes
are preserved as recorded; new text provenance should use the canonical identity
below, which is the same on every checkout.

Canonicalisation ``text/lf-v1``: decode as UTF-8 (a leading BOM is dropped),
convert CRLF and lone CR to LF, re-encode as UTF-8, SHA-256. Binary files (PDFs,
images, archives) keep raw-byte SHA-256.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

CANONICALISATION = "text/lf-v1"
TEXT_SUFFIXES = frozenset({".csv", ".tsv", ".json", ".md", ".txt", ".py", ".yml", ".yaml", ".toml", ".cff", ".bat", ".cmd", ".sh"})


def is_text_path(path: Path) -> bool:
    return Path(path).suffix.lower() in TEXT_SUFFIXES


def canonical_text_bytes(data: bytes) -> bytes:
    text = data.decode("utf-8-sig")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def canonical_text_sha256(path: Path) -> str:
    """Checkout-independent SHA-256 of a text file (``text/lf-v1``)."""
    return hashlib.sha256(canonical_text_bytes(Path(path).read_bytes())).hexdigest()


def file_identity(path: Path) -> dict[str, Any]:
    """Raw-byte SHA-256 (historical, checkout-dependent for text) plus canonical identity for text."""
    data = Path(path).read_bytes()
    out: dict[str, Any] = {"sha256": hashlib.sha256(data).hexdigest()}
    if is_text_path(Path(path)):
        try:
            out["canonical_sha256"] = hashlib.sha256(canonical_text_bytes(data)).hexdigest()
            out["canonicalization"] = CANONICALISATION
        except UnicodeDecodeError:
            pass
    return out


def byte_variants(path: Path) -> dict[str, str]:
    """SHA-256 of the LF and CRLF renderings of a text file, keyed by variant.

    Used to recognise a historical byte hash that was taken over the other
    line-ending rendering of the same content.
    """
    lf = canonical_text_bytes(Path(path).read_bytes())
    return {"LF": hashlib.sha256(lf).hexdigest(), "CRLF": hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()}
