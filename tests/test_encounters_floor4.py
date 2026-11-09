"""Offline checks for the Floor 4 side passages: The Locks Turnstile and Trace the Portal.

No test calls a model or AWS, and none opens a port: the turnstile is exercised through its
refusal path, which fails before anything connects, and the tracing is checked with fakes and an
in-memory span exporter.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
TURNSTILE = "dungeon/encounters/floor-4-locks-turnstile/locks_turnstile.py"
TIDE = "dungeon/encounters/floor-4-locks-turnstile/tide_server.py"
PORTAL = "dungeon/encounters/floor-4-trace-the-portal/trace_the_portal.py"


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


# ---------- The Locks Turnstile ----------------------------------------------


@pytest.fixture
def tide():
    return load(TIDE, "encounter_tide")


@pytest.fixture
def turnstile_mod():
    return load(TURNSTILE, "encounter_turnstile")


def test_locks_turnstile_tide_server_is_deterministic_and_on_its_own_port(tide):
    assert 8003 <= tide.PORT <= 8008
    first = tide.tide_table("Ballard-Locks")
    assert first == tide.tide_table("ballard-locks")
    assert first["station"] == "ballard-locks"
    assert [t["kind"] for t in first["turns"]] == ["low", "high", "low", "high"]
    assert tide.next_turn("ballard-locks", after="09:00") == {
        "station": "ballard-locks", "time": "14:40", "feet": 2.1, "kind": "low"}
    assert tide.next_turn("elliott-bay", after="23:00")["time"] == "none"
    with pytest.raises(ValueError, match="Unknown station"):
        tide.tide_table("lake-union-bathtub")


def test_locks_turnstile_imports_the_router_factory(turnstile_mod):
    from strands.vended_tools.mcp_router.mcp_router import make_mcp_router

    assert turnstile_mod.make_mcp_router is make_mcp_router


def test_locks_turnstile_allowlist_holds_the_dice_and_tide_servers(turnstile_mod):
    assert turnstile_mod.ALLOWLIST == {
        "dice": {"url": "http://localhost:8002/mcp"},
        "tide": {"url": turnstile_mod.TIDE_URL},
    }
    assert turnstile_mod.TIDE_URL == "http://localhost:8003/mcp"


def test_locks_turnstile_router_is_named_turnstile_and_capped_at_two(turnstile_mod):
    spec = turnstile_mod.turnstile.tool_spec
    assert turnstile_mod.turnstile.tool_name == "turnstile"
    assert "'dice', 'tide'" in spec["description"], "the model is told the permitted names"
    kw = call_keywords(TURNSTILE, "make_mcp_router")
    assert isinstance(kw["max_connections"], ast.Constant) and kw["max_connections"].value == 2
    assert "ALLOWLIST" in names_in(kw["servers"])


def test_locks_turnstile_gate_holds_only_the_turnstile_on_nova(turnstile_mod):
    kw = agent_call_keywords(TURNSTILE)
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA
    assert "turnstile" in names_in(kw["tools"])
    gate = turnstile_mod.make_gate()
    assert gate.tool_names == ["turnstile"]
    assert gate.model.config["model_id"] == NOVA


def test_locks_turnstile_refuses_a_server_off_the_allowlist(turnstile_mod):
    gate = turnstile_mod.make_gate()
    said = turnstile_mod.knock(gate, "ferry-wifi")
    assert said.startswith("error:")
    assert "not on the MCP server allowlist" in said
    assert "dice, tide" in said


# ---------- Trace the Portal -------------------------------------------------


@pytest.fixture
def portal_mod():
    return load(PORTAL, "encounter_portal")


def test_trace_the_portal_imports_the_telemetry_and_the_instrumentation(portal_mod):
    from strands.telemetry import StrandsTelemetry
    from strands.tools.mcp.mcp_instrumentation import mcp_instrumentation

    assert portal_mod.StrandsTelemetry is StrandsTelemetry
    assert portal_mod.mcp_instrumentation is mcp_instrumentation


def test_trace_the_portal_server_is_on_its_own_port_and_rolls_one_die(portal_mod, monkeypatch):
    assert 8003 <= portal_mod.PORT <= 8008 and portal_mod.PORT != 8003
    monkeypatch.setattr(portal_mod.random, "randint", lambda a, b: 17)
    assert portal_mod.roll_dice(faces=20) == {"faces": 20, "die": 17}
    with pytest.raises(ValueError):
        portal_mod.roll_dice(faces=0)


def test_trace_the_portal_lights_the_console_exporter_then_the_instrumentation(portal_mod, monkeypatch):
    calls: list = []

    class FakeTelemetry:
        def setup_console_exporter(self, **kwargs):
            calls.append(("console", kwargs))
            return self

    monkeypatch.setattr(portal_mod, "StrandsTelemetry", FakeTelemetry)
    monkeypatch.setattr(portal_mod, "mcp_instrumentation", lambda: calls.append(("instrumentation", {})))
    portal_mod.light_the_portal()
    assert calls == [("console", {"formatter": portal_mod.one_line}), ("instrumentation", {})]


def test_trace_the_portal_one_line_shows_trace_span_and_parent(portal_mod):
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    memory = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(memory))
    tracer = provider.get_tracer("test")
    with tracer.start_as_current_span("agent.turn"):
        with tracer.start_as_current_span("tool.call"):
            pass
    child, root = memory.get_finished_spans()
    child_line, root_line = portal_mod.one_line(child), portal_mod.one_line(root)
    root_id = format(root.get_span_context().span_id, "016x")[-4:]
    trace_id = format(root.get_span_context().trace_id, "032x")[-6:]
    assert child_line.endswith("\n") and "tool.call" in child_line
    assert f"parent {root_id}" in child_line
    assert f"trace {trace_id}" in child_line and f"trace {trace_id}" in root_line
    assert "parent none" in root_line


def test_trace_the_portal_watcher_is_tagged_and_holds_the_portal_client_on_nova(portal_mod, monkeypatch):
    kw = agent_call_keywords(PORTAL)
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA
    assert ast.literal_eval(kw["trace_attributes"]) == {"encounter": "trace-the-portal"}

    seen: dict = {}
    monkeypatch.setattr(portal_mod, "Agent", lambda **kwargs: types.SimpleNamespace(**seen, **kwargs))
    watcher = portal_mod.make_watcher("the-client")
    assert watcher.tools == ["the-client"]
    assert watcher.trace_attributes == {"encounter": "trace-the-portal"}
    assert watcher.model == NOVA
