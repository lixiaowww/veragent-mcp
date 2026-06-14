"""
Live integration tests for the Veragent MCP client (no mocks — hits the real API).
Run: python test_client.py
"""
from veragent_mcp import client


def test_check_tool_trust_found():
    res = client.check_tool_trust("playwright")
    assert res["found"] is True, res
    assert isinstance(res["trust_score_pct"], int)
    assert res["audit_state"]
    assert res["report_url"].startswith("https://veragent.store/agents/")
    print("check_tool_trust(found):", res["name"], res["trust_score_pct"], res["audit_state"])


def test_check_tool_trust_not_found():
    res = client.check_tool_trust("zzz-nonexistent-tool-xyz-123")
    assert res["found"] is False, res
    print("check_tool_trust(not found): OK")


def test_list_trusted_tools():
    res = client.list_trusted_tools(limit=5)
    assert isinstance(res, list) and len(res) > 0, res
    assert all("report_url" in t for t in res)
    print("list_trusted_tools:", len(res), "tools; top:", res[0]["name"], res[0]["trust_score_pct"])


def test_scan_mcp_stack():
    cfg = {"mcpServers": {"playwright": {"command": "npx", "args": ["-y", "@playwright/mcp"]}}}
    res = client.scan_mcp_stack(cfg)
    assert "total" in res and res["total"] >= 1, res
    print("scan_mcp_stack: total", res["total"], "summary:", res["summary"])


if __name__ == "__main__":
    test_check_tool_trust_found()
    test_check_tool_trust_not_found()
    test_list_trusted_tools()
    test_scan_mcp_stack()
    print("\nAll live client tests passed ✓")
