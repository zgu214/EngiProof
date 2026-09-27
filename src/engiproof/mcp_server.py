"""EngiProof MCP server.

Exposes every live EngiProof study to MCP clients (Claude Code, Codex,
Gemini CLI, ...) as callable tools, readable resources and one evidence-
reporting prompt. It is a thin adapter over ``engiproof.core``: all physics,
contracts and evidence rules stay in the studies themselves.

Design rules
------------
* Every method call returns the full EngiProof envelope (evidence,
  evidence_class, evidence_status, limitations). The adapter never strips or
  upgrades evidence information.
* Read-only by default. ``run_study`` and ``verify_study`` remain disabled by
  default because the current legacy verification paths may rewrite tracked
  result artifacts. ``ENGIPROOF_MCP_ALLOW_RUN=1`` is an explicit opt-in to
  those mutating paths until non-mutating verification is implemented.
* Qualification is never granted by this adapter.

Start (stdio transport)::

    engiproof-mcp
    # or: python -m engiproof.mcp_server

Claude Code::

    claude mcp add engiproof -- engiproof-mcp
"""
from __future__ import annotations

import os
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - exercised only without the extra
    raise ImportError(
        "The EngiProof MCP server needs the optional 'mcp' dependency. "
        "Install it with: pip install -e .[mcp]"
    ) from exc

from . import __version__
from .core import (
    comparison_snapshot,
    contract_schema,
    discrepancy_snapshot,
    evidence_snapshot,
    invoke_tool,
    list_studies as _list_studies,
    load_manifest,
    project_root,
    provenance_snapshot,
    run_study as _run_study,
    verify_study as _verify_study,
)

ALLOW_RUN_ENV = "ENGIPROOF_MCP_ALLOW_RUN"

INSTRUCTIONS = f"""EngiProof {__version__}: source-bounded, independently checked
engineering methods from published papers (subsea pipelines, pipe-in-pipe,
buckling, vibration). Start with list_studies, then describe_study for the
argument ranges of a method, then call_method. Always report the returned
evidence, evidence_class, evidence_status and limitations with any number.
CONDITIONAL studies carry open discrepancies (see get_discrepancies). No
result from this server is an engineering qualification."""

mcp = FastMCP("engiproof", instructions=INSTRUCTIONS)


def _tool_summary(tool: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": tool["name"],
        "arguments": tool.get("arguments", {}),
        "returns": tool.get("returns"),
        "evidence": tool.get("evidence"),
        "evidence_class": tool.get("evidence_class"),
    }


# --------------------------------------------------------------------- tools
@mcp.tool()
def list_studies() -> list[dict[str, Any]]:
    """List every live EngiProof study with its evidence status and callable methods."""
    return [
        {
            "paper_id": m["paper_id"],
            "title": m["title"],
            "year": m.get("year"),
            "category": m.get("category"),
            "doi": m.get("source", {}).get("doi"),
            "evidence_status": m["evidence_status"],
            "methods": [_tool_summary(t) for t in m.get("tools", [])],
        }
        for m in _list_studies()
    ]


@mcp.tool()
def describe_study(paper_id: str) -> dict[str, Any]:
    """Full study manifest: source, selected targets, methods with argument ranges,
    comparisons, discrepancies and limitations. Read this before calling a method."""
    return load_manifest(paper_id)


@mcp.tool()
def call_method(paper_id: str, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Call a published or independently checked method from a study.

    ``params`` are the keyword arguments listed for the method in
    describe_study. The response keeps the full evidence envelope; quote its
    evidence_class, evidence_status and limitations alongside the result.
    """
    return invoke_tool(paper_id, method, params or {})


@mcp.tool()
def get_evidence_graph(paper_id: str) -> dict[str, Any]:
    """Evidence graph linking source -> target -> implementation -> check -> comparison -> discrepancy."""
    return evidence_snapshot(paper_id)


@mcp.tool()
def get_comparisons(paper_id: str) -> dict[str, Any]:
    """Published-vs-reproduced/independent comparisons, with reference population and boundary."""
    return comparison_snapshot(paper_id)


@mcp.tool()
def get_discrepancies(paper_id: str) -> dict[str, Any]:
    """Open source inconsistencies and their engineering interpretation. Never tuned away."""
    return discrepancy_snapshot(paper_id)


@mcp.tool()
def get_provenance(paper_id: str) -> dict[str, Any]:
    """Source DOI and SHA-256, file hashes and qualification state for a study."""
    return provenance_snapshot(paper_id)


@mcp.tool()
def get_contract(name: str | None = None) -> dict[str, Any]:
    """EngiProof contract definitions (study/source/evidence/comparison/discrepancy/verification)."""
    return contract_schema(name)


def _register_run_tools() -> None:
    @mcp.tool()
    def run_study(paper_id: str) -> dict[str, Any]:
        """Execute a study's runner. Opt-in only: may rewrite tracked result artifacts."""
        return _run_study(paper_id)

    @mcp.tool()
    def verify_study(paper_id: str) -> dict[str, Any]:
        """Run contract, file and unit-test verification for a study.
        Opt-in only: legacy verification paths may rewrite tracked result artifacts."""
        return _verify_study(paper_id)


if os.environ.get(ALLOW_RUN_ENV) == "1":
    _register_run_tools()


# ----------------------------------------------------------------- resources
def _read_text(rel: str) -> str:
    return (project_root() / rel).read_text(encoding="utf-8")


@mcp.resource("engiproof://registry", mime_type="application/json")
def registry_resource() -> str:
    """Registry of live studies."""
    return _read_text("engiproof/registry.json")


@mcp.resource("engiproof://studies/{paper_id}/manifest", mime_type="application/json")
def manifest_resource(paper_id: str) -> str:
    """study.json for one study."""
    return _read_text(f"engiproof/studies/{paper_id.upper()}/study.json")


@mcp.resource("engiproof://studies/{paper_id}/source", mime_type="text/markdown")
def source_resource(paper_id: str) -> str:
    """Source contract (SOURCE.md): what was taken from the paper and how."""
    return _read_text(load_manifest(paper_id)["source_contract"])


@mcp.resource("engiproof://studies/{paper_id}/evidence-graph", mime_type="application/json")
def evidence_graph_resource(paper_id: str) -> str:
    """Evidence graph JSON, where the study ships one."""
    rel = load_manifest(paper_id).get("evidence_graph")
    if not rel:
        raise FileNotFoundError(f"{paper_id.upper()} has no evidence graph yet.")
    return _read_text(rel)


# ------------------------------------------------------------------- prompts
@mcp.prompt()
def apply_method(paper_id: str, question: str) -> str:
    """Answer an engineering question with a study's methods, reporting evidence honestly."""
    return (
        f"Use EngiProof study {paper_id.upper()} to answer: {question}\n\n"
        "1. Call describe_study and check the question lies inside each method's argument ranges "
        "and the study's selected targets. If it does not, say so instead of extrapolating.\n"
        "2. Call the needed methods with call_method.\n"
        "3. If evidence_status is CONDITIONAL, call get_discrepancies and state how the open "
        "discrepancy affects this answer.\n"
        "4. Report every number with its evidence reference, evidence_class and limitations. "
        "Do not describe PUBLISHED fits as independent validation.\n"
        "5. State that engineering qualification is not granted by EngiProof."
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
