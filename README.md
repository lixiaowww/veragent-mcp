# Veragent MCP Server

The trust layer for MCP — as an MCP tool. Let Claude (or any MCP client/agent) check
whether an MCP tool is **safe before installing it**, look up the most trusted tools,
or score an entire MCP stack — all backed by the [Veragent](https://veragent.store)
trust registry.

## Tools

| Tool | What it does |
|------|--------------|
| `check_tool_trust(name)` | Veragent trust score + audit state for a tool/server/agent. Use **before** installing. |
| `list_trusted_tools(query, limit)` | The most trusted MCP tools, optionally filtered. |
| `scan_mcp_stack(mcp_config)` | Score a whole `mcp_settings.json` — per-server risk + summary. |

## Install (Claude Desktop)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "veragent": {
      "command": "uvx",
      "args": ["veragent-mcp"]
    }
  }
}
```

Then ask Claude: *"Is the playwright-mcp server safe? Check Veragent."*

## Run locally

```bash
uvx veragent-mcp
# or
pip install veragent-mcp && veragent-mcp
```

## Configuration

- `VERAGENT_API_BASE` — override the API base (default `https://veragent.store/api/v1`).

## Honesty

Veragent labels static-analysis results as **Heuristic** and reserves **SGC Certified**
for behavioral-sandbox passes. Scores are reported with this distinction.
