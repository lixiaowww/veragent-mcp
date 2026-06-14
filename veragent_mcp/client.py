"""
Veragent API client — pure functions over the public Veragent API.

Kept free of MCP-protocol concerns so the trust logic is independently testable
against the live API (no mocks). Used by server.py to back the MCP tools.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List

import httpx

API_BASE = os.environ.get("VERAGENT_API_BASE", "https://veragent.store/api/v1").rstrip("/")
_TIMEOUT = httpx.Timeout(20.0)


def _audit_label(audit_status: str, has_report: bool) -> str:
    s = (audit_status or "unaudited").lower()
    if "certified" in s and has_report:
        return "SGC Certified (behavioral sandbox)"
    if s in ("audited", "approved") or "audited" in s:
        return "Heuristic (static analysis only)"
    if "pending" in s or "review" in s:
        return "Audit pending"
    return "Unaudited"


def check_tool_trust(name: str) -> Dict[str, Any]:
    """Look up an MCP tool by name and return its Veragent trust assessment."""
    with httpx.Client(timeout=_TIMEOUT) as c:
        r = c.get(f"{API_BASE}/search/agents", params={"q": name, "page": 1, "limit": 5})
        r.raise_for_status()
        agents = (r.json() or {}).get("agents", [])

    # Relevance guard: Typesense fuzzy-matches, so a non-indexed name can still return an
    # unrelated tool. Require token overlap between the query and the candidate name/tagline
    # so we never misreport an unrelated tool as if it were the one asked about.
    def _relevant(a: Dict[str, Any]) -> bool:
        q_tokens = {t for t in "".join(ch if ch.isalnum() else " " for ch in name.lower()).split() if len(t) > 2}
        if not q_tokens:
            return True
        hay = f"{a.get('name','')} {a.get('tagline','')} {a.get('id','')}".lower()
        return any(t in hay for t in q_tokens)

    relevant = [a for a in agents if _relevant(a)] if agents else []
    if not relevant:
        return {"found": False, "query": name,
                "message": f"No tool matching '{name}' is indexed in the Veragent trust registry. "
                           "Treat it as unverified."}

    a = relevant[0]
    pct = round((a.get("trust_score") or a.get("sgc_confidence") or 0) * 100)
    label = _audit_label(a.get("audit_status", ""), bool(a.get("sgc_report_id")))
    return {
        "found": True,
        "name": a.get("name"),
        "trust_score_pct": pct,
        "audit_state": label,
        "risk_tier": a.get("sgc_risk_tier") or a.get("risk_tier"),
        "listing_type": a.get("listing_type"),
        "publisher": (a.get("publisher") or {}).get("name"),
        "report_url": f"https://veragent.store/agents/{a.get('id')}",
        "advice": (
            "Heuristic score reflects static analysis only — review the source before "
            "installing in production." if "Heuristic" in label
            else "Passed Veragent behavioral sandbox audit." if "Certified" in label
            else "Not yet audited — install with caution."
        ),
    }


def list_trusted_tools(query: str = "*", limit: int = 10) -> List[Dict[str, Any]]:
    """Return the most trusted tools matching a query (or overall)."""
    with httpx.Client(timeout=_TIMEOUT) as c:
        r = c.get(f"{API_BASE}/search/agents",
                  params={"q": query or "*", "sort_by": "trust_score", "page": 1, "limit": limit})
        r.raise_for_status()
        agents = (r.json() or {}).get("agents", [])
    return [{
        "name": a.get("name"),
        "trust_score_pct": round((a.get("trust_score") or a.get("sgc_confidence") or 0) * 100),
        "audit_state": _audit_label(a.get("audit_status", ""), bool(a.get("sgc_report_id"))),
        "report_url": f"https://veragent.store/agents/{a.get('id')}",
    } for a in agents]


def scan_mcp_stack(mcp_config: Dict[str, Any]) -> Dict[str, Any]:
    """Score a whole MCP stack. Pass a parsed mcp_settings.json (or its mcpServers block)."""
    with httpx.Client(timeout=_TIMEOUT) as c:
        r = c.post(f"{API_BASE}/stack/health-check", json={"mcp_config": mcp_config})
        r.raise_for_status()
        rep = r.json()
    return {
        "total": rep.get("total_servers"),
        "safe": rep.get("green"), "caution": rep.get("yellow"),
        "high_risk": rep.get("red"), "unregistered": rep.get("unknown"),
        "summary": rep.get("summary"),
        "details": [
            {"server": s.get("server_key"), "risk": s.get("risk_level"),
             "signals": s.get("signals")} for s in rep.get("servers", [])
        ],
    }
