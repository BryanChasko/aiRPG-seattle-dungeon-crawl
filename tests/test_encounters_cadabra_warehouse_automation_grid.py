"""Offline checks for the Floor 4 side passage The Warehouse Automation Grid.

No test calls a model or AWS, and none opens a port: the filters are checked against the tool
names the grid server declares, with fake MCP tool objects, and the agent is built with a fake.
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import re
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
GRID = "encounters/floor-4-warehouse-automation-grid/warehouse_grid.py"
SERVER = "encounters/floor-4-warehouse-automation-grid/grid_server.py"

READ_ONLY = {"list_belts", "belt_status", "scan_parcel"}
MOVERS = {"set_belt_speed", "route_parcel", "arm_pick", "arm_sweep_aisle"}
TRIPWIRE = "scan_and_release_all"


def load(rel: str, name: str):
    """Import an encounter script from its path under a unique module name."""
    path = ROOT / rel
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.remove(str(path.parent))


def agent_call_keywords(rel: str) -> dict[str, ast.expr]:
    tree = ast.parse((ROOT / rel).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "Agent":
            return {kw.arg: kw.value for kw in node.keywords}
    raise AssertionError(f"no Agent(...) call in {rel}")


def call_keywords(rel: str, func_name: str) -> dict[str, ast.expr]:
    tree = ast.parse((ROOT / rel).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == func_name:
            return {kw.arg: kw.value for kw in node.keywords}
    raise AssertionError(f"no {func_name}(...) call in {rel}")


def names_in(expr: ast.expr) -> set[str]:
    return {n.id for n in ast.walk(expr) if isinstance(n, ast.Name)}


@pytest.fixture(autouse=True)
def region(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-west-2")


@pytest.fixture
def server():
    return load(SERVER, "encounter_grid_server")


@pytest.fixture
def grid():
    return load(GRID, "encounter_warehouse_grid")


def fake_tool(client, name: str):
    """A real MCPAgentTool around a bare MCP tool description, no connection made."""
    from mcp.types import Tool
    from strands.tools.mcp import MCPAgentTool

    return MCPAgentTool(Tool(name=name, inputSchema={"type": "object"}), client)


def visible(client, names) -> set[str]:
    """Run each name through the client's own filter check and keep the ones it lets through."""
    return {n for n in names if client._should_include_tool_with_filters(fake_tool(client, n), client._tool_filters)}


# ---------- the grid server, given -------------------------------------------


def test_warehouse_grid_server_declares_eight_tools_on_its_own_port(server):
    assert 8004 <= server.PORT <= 8008
    declared = {t.name for t in asyncio.run(server.mcp.list_tools())}
    assert declared == READ_ONLY | MOVERS | {TRIPWIRE}


def test_warehouse_grid_server_reads_are_deterministic(server):
    assert server.scan_parcel("pkg-4471") == {
        "parcel": "PKG-4471", "belt": "belt-3", "lane": "C", "note": "waiting on a jammed sorter"}
    assert server.belt_status("Belt-3") == {"belt": "belt-3", "carries": "oversize", "speed": 0.0, "state": "stalled"}
    assert [b["belt"] for b in server.list_belts()["belts"]] == ["belt-1", "belt-2", "belt-3", "belt-4"]
    with pytest.raises(ValueError, match="Unknown belt"):
        server.belt_status("belt-99")
    with pytest.raises(ValueError, match="Unknown parcel"):
        server.scan_parcel("PKG-0000")


def test_warehouse_grid_server_tripwire_starts_every_belt(server):
    out = server.scan_and_release_all()
    assert out["belts_released"] == 4
    assert all(b["speed"] == 2.0 and b["state"] == "running" for b in server.BELTS.values())


# ---------- Step 1: the import -----------------------------------------------


def test_warehouse_grid_imports_mcp_client(grid):
    from strands.tools.mcp import MCPClient

    assert grid.MCPClient is MCPClient


# ---------- Step 2: the allowed list -----------------------------------------


def test_warehouse_grid_allowed_is_one_pattern_for_the_read_only_prefixes(grid):
    assert len(grid.ALLOWED) == 1
    pattern = grid.ALLOWED[0]
    assert isinstance(pattern, re.Pattern) and pattern.pattern == r"^(list|belt|scan)_"
    assert all(pattern.match(n) for n in READ_ONLY)
    assert not any(pattern.match(n) for n in MOVERS)


def test_warehouse_grid_allowed_alone_still_lets_the_tripwire_through(grid):
    from strands.tools.mcp import MCPClient

    only_allowed = MCPClient(url=grid.GRID_URL, tool_filters={"allowed": grid.ALLOWED})
    assert visible(only_allowed, READ_ONLY | MOVERS | {TRIPWIRE}) == READ_ONLY | {TRIPWIRE}


# ---------- Step 3: the rejected list ----------------------------------------


def test_warehouse_grid_rejected_names_the_tripwire_exactly(grid):
    assert grid.REJECTED == [TRIPWIRE]


# ---------- Step 4: the filtered client --------------------------------------


def test_warehouse_grid_client_is_built_with_both_lists(grid):
    kw = call_keywords(GRID, "MCPClient")
    assert "GRID_URL" in names_in(kw["url"])
    filters = kw["tool_filters"]
    assert isinstance(filters, ast.Dict)
    keys = [k.value for k in filters.keys]
    assert keys == ["allowed", "rejected"]
    assert [names_in(v) for v in filters.values] == [{"ALLOWED"}, {"REJECTED"}]


def test_warehouse_grid_client_shows_only_the_three_read_only_tools(grid):
    client = grid.make_grid_client()
    assert client._tool_filters == {"allowed": grid.ALLOWED, "rejected": grid.REJECTED}
    assert visible(client, READ_ONLY | MOVERS | {TRIPWIRE}) == READ_ONLY


def test_warehouse_grid_tool_names_lists_what_the_client_exposes(grid):
    class FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def list_tools_sync(self):
            return [types.SimpleNamespace(tool_name=n) for n in ("scan_parcel", "belt_status", "list_belts")]

    assert grid.tool_names(FakeClient()) == ["belt_status", "list_belts", "scan_parcel"]


# ---------- Step 5: the attendant --------------------------------------------


def test_warehouse_grid_attendant_gets_the_filtered_client_on_nova(grid, monkeypatch):
    kw = agent_call_keywords(GRID)
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA
    assert names_in(kw["tools"]) == {"grid_client"}

    monkeypatch.setattr(grid, "Agent", lambda **kwargs: types.SimpleNamespace(**kwargs))
    attendant = grid.make_attendant("the-client")
    assert attendant.tools == ["the-client"]
    assert attendant.model == NOVA
    assert attendant.system_prompt.endswith("Plain text only, no emoji.")
