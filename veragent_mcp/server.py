"""
Veragent MCP server — the trust layer, as an MCP tool.

Exposes Veragent's trust registry as MCP tools so Claude (and any MCP client/agent)
can vet MCP tools *before* installing them, or score an existing stack — turning
Veragent from "a site you visit" into "a tool the agent calls".

Run:
    uvx veragent-mcp            # or: python -m veragent_mcp.server
"""
from __future__ import annotations

from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

from veragent_mcp import client

mcp = FastMCP("veragent")


@mcp.tool()
def check_tool_trust(name: str) -> Dict[str, Any]:
    """Check the Veragent trust score and audit state of an MCP tool / server / agent by name.
    Use this BEFORE installing or recommending an MCP tool to verify it is safe."""
    return client.check_tool_trust(name)


@mcp.tool()
def list_trusted_tools(query: str = "*", limit: int = 10) -> Any:
    """List the most trusted MCP tools, optionally filtered by a search query."""
    return client.list_trusted_tools(query=query, limit=limit)


@mcp.tool()
def scan_mcp_stack(mcp_config: Dict[str, Any]) -> Dict[str, Any]:
    """Score a whole MCP stack for security. Pass a parsed mcp_settings.json object
    (or just its mcpServers block). Returns per-server risk levels and a summary."""
    return client.scan_mcp_stack(mcp_config)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
