"""End-to-end tests for the EngiProof MCP adapter through a real MCP client session.

Skipped when the optional 'mcp' dependency is not installed.
"""
import asyncio
import importlib
import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

try:
    from mcp.shared.memory import create_connected_server_and_client_session
    HAVE_MCP = True
except ImportError:
    HAVE_MCP = False

STUDIES = ["P08", "P12", "P16", "P29", "P36", "P38"]


def _load_server(allow_run: bool):
    os.environ.pop("ENGIPROOF_MCP_ALLOW_RUN", None)
    if allow_run:
        os.environ["ENGIPROOF_MCP_ALLOW_RUN"] = "1"
    import engiproof.mcp_server as mod
    mod = importlib.reload(mod)
    os.environ.pop("ENGIPROOF_MCP_ALLOW_RUN", None)
    return mod.mcp


def _run(coro):
    return asyncio.run(coro)


def _json(result):
    if result.structuredContent is not None:
        data = result.structuredContent
        return data.get("result", data) if set(data) == {"result"} else data
    return json.loads(result.content[0].text)


@unittest.skipUnless(HAVE_MCP, "optional 'mcp' dependency not installed")
class EngiProofMCPTests(unittest.TestCase):
    def test_read_only_by_default(self):
        server = _load_server(allow_run=False)

        async def go():
            async with create_connected_server_and_client_session(server._mcp_server) as s:
                return {t.name for t in (await s.list_tools()).tools}

        names = _run(go())
        self.assertIn("call_method", names)
        self.assertNotIn("run_study", names)
        self.assertNotIn("verify_study", names)

    def test_run_tools_opt_in(self):
        server = _load_server(allow_run=True)

        async def go():
            async with create_connected_server_and_client_session(server._mcp_server) as s:
                return {t.name for t in (await s.list_tools()).tools}

        self.assertTrue({"run_study", "verify_study"} <= _run(go()))

    def test_list_and_call_keep_evidence_envelope(self):
        server = _load_server(allow_run=False)

        async def go():
            async with create_connected_server_and_client_session(server._mcp_server) as s:
                studies = _json(await s.call_tool("list_studies", {}))
                p08 = _json(await s.call_tool("call_method", {
                    "paper_id": "P08", "method": "critical_temperature_eq11",
                    "params": {"length_m": 100.0}}))
                p38 = _json(await s.call_tool("call_method", {
                    "paper_id": "P38", "method": "equation16_ratio",
                    "params": {"diameter_ratio": 0.5, "thickness_ratio": 0.6,
                               "yield_ratio": 1.0, "mode": "A"}}))
                return studies, p08, p38

        studies, p08, p38 = _run(go())
        self.assertEqual([s["paper_id"] for s in studies], STUDIES)
        # Same numbers as the direct-core tests in test_engiproof.py.
        self.assertAlmostEqual(p08["result"], 0.9476, places=10)
        self.assertAlmostEqual(p38["result"], 1.2328614965958689, places=12)
        for out in (p08, p38):
            for key in ("evidence", "evidence_class", "evidence_status", "limitations"):
                self.assertIn(key, out)
        self.assertEqual(p38["evidence_status"], "CONDITIONAL")

    def test_p12_fit_stays_independent_with_explicit_boundary(self):
        server = _load_server(allow_run=False)

        async def go():
            async with create_connected_server_and_client_session(server._mcp_server) as s:
                return _json(await s.call_tool("call_method", {
                    "paper_id": "P12", "method": "table4_fit_force_MN",
                    "params": {"beta": 0.6, "clearance_mm": 12.0}}))

        out = _run(go())
        self.assertAlmostEqual(out["result"], 1.6243216727, places=8)
        self.assertEqual(out["evidence_class"], "INDEPENDENT")
        boundary = out["evidence_boundary"]
        self.assertIn("independently performed by EngiProof", boundary)
        self.assertIn("published P12 Table 4", boundary)
        self.assertIn("not independent physical or FE validation", boundary)

    def test_bad_method_is_an_error_not_a_number(self):
        server = _load_server(allow_run=False)

        async def go():
            async with create_connected_server_and_client_session(server._mcp_server) as s:
                return await s.call_tool("call_method", {"paper_id": "P08", "method": "no_such_method"})

        self.assertTrue(_run(go()).isError)

    def test_resources_and_prompt(self):
        server = _load_server(allow_run=False)

        async def go():
            async with create_connected_server_and_client_session(server._mcp_server) as s:
                reg = await s.read_resource("engiproof://registry")
                graph = await s.read_resource("engiproof://studies/P38/evidence-graph")
                src = await s.read_resource("engiproof://studies/P38/source")
                prompt = await s.get_prompt("apply_method", {"paper_id": "p38", "question": "D/t = 20?"})
                return reg, graph, src, prompt

        reg, graph, src, prompt = _run(go())
        self.assertEqual(json.loads(reg.contents[0].text)["studies"], STUDIES)
        self.assertEqual(json.loads(graph.contents[0].text)["paper_id"], "P38")
        self.assertTrue(src.contents[0].text.strip())
        self.assertIn("qualification is not granted", prompt.messages[0].content.text)


if __name__ == "__main__":
    unittest.main()
