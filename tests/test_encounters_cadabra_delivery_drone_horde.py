"""Offline checks for the Cadabra side passage off Floor 5: The Delivery Drone Horde.

No test calls a model or AWS. The script builds its agents only when asked, and the steering handler
is exercised directly and through its hook with fake events.
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
HORDE = "encounters/floor-5-delivery-drone-horde/delivery_drone_horde.py"


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


def names_in(expr: ast.expr) -> set[str]:
    return {n.id for n in ast.walk(expr) if isinstance(n, ast.Name)}


@pytest.fixture
def horde():
    mod = load(HORDE, "encounter_drone_horde")
    mod.reset()
    return mod


def steer(handler, name: str, **tool_input):
    return asyncio.run(handler.steer_before_tool(agent=None, tool_use={"name": name, "toolUseId": "t1", "input": tool_input}))


# ---------- Step 1: the imports ----------------------------------------------


def test_delivery_drone_horde_imports_the_steering_classes_from_the_sdk(horde):
    from strands.vended_plugins import steering

    assert horde.SteeringHandler is steering.SteeringHandler
    assert horde.Proceed is steering.Proceed
    assert horde.Guide is steering.Guide
    assert issubclass(horde.StayOnCourse, steering.SteeringHandler)


# ---------- Step 2: the Guide ------------------------------------------------


def test_delivery_drone_horde_lets_the_first_answer_proceed(horde):
    handler = horde.StayOnCourse()
    action = steer(handler, "answer_drone", drone_id="D-0412")
    assert isinstance(action, horde.Proceed)


def test_delivery_drone_horde_guides_the_second_answer(horde):
    handler = horde.StayOnCourse()
    steer(handler, "answer_drone", drone_id="D-0412")
    action = steer(handler, "answer_drone", drone_id="D-0413")
    assert isinstance(action, horde.Guide)
    assert "advance" in action.reason, "the guidance must name the tool that gets the agent moving again"


def test_delivery_drone_horde_advance_does_not_buy_another_signature(horde):
    handler = horde.StayOnCourse()
    steer(handler, "answer_drone", drone_id="D-0412")
    assert isinstance(steer(handler, "advance"), horde.Proceed)
    assert isinstance(steer(handler, "answer_drone", drone_id="D-0587"), horde.Guide)


def test_delivery_drone_horde_allowance_is_configurable(horde):
    handler = horde.StayOnCourse(answers_allowed=0)
    assert isinstance(steer(handler, "answer_drone", drone_id="D-0412"), horde.Guide)


def test_delivery_drone_horde_leaves_other_tools_alone(horde):
    handler = horde.StayOnCourse()
    steer(handler, "answer_drone", drone_id="D-0412")
    assert isinstance(steer(handler, "scan_floor"), horde.Proceed)


def test_delivery_drone_horde_guide_cancels_the_tool_call_through_the_hook(horde):
    handler = horde.StayOnCourse()
    event = types.SimpleNamespace(
        agent=None, tool_use={"name": "answer_drone", "toolUseId": "t1", "input": {"drone_id": "D-0412"}},
        invocation_context=None, cancel_tool=False,
    )
    asyncio.run(handler.provide_tool_steering_guidance(event))
    assert event.cancel_tool is False, "the first answer runs"
    asyncio.run(handler.provide_tool_steering_guidance(event))
    assert isinstance(event.cancel_tool, str) and "advance" in event.cancel_tool, "the second answer is cancelled with the guidance"


# ---------- Step 3: the plugin on the agent -----------------------------------


def test_delivery_drone_horde_steered_agent_carries_the_handler(horde, monkeypatch):
    built = {}

    def fake_make_agent(plugins):
        built["plugins"] = plugins
        return object()

    monkeypatch.setattr(horde, "make_agent", fake_make_agent)
    horde.steered_agent()
    assert len(built["plugins"]) == 1 and isinstance(built["plugins"][0], horde.StayOnCourse)


def test_delivery_drone_horde_agent_is_nova_2_lite_with_plugins_passed_through():
    kw = agent_call_keywords(HORDE)
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA
    assert "plugins" in names_in(kw["plugins"])


def test_delivery_drone_horde_real_agent_registers_the_handler(horde):
    handler = horde.StayOnCourse()
    agent = horde.make_agent(plugins=[handler])
    assert handler.name in agent._plugin_registry._plugins


# ---------- Given code: the drones ---------------------------------------------


def test_delivery_drone_horde_answering_a_drone_drags_the_party_back(horde):
    horde.advance()
    horde.advance()
    assert horde.state["leg"] == 2
    horde.answer_drone("D-0412")
    assert horde.state["leg"] == 1 and horde.state["dragged"] == 1


def test_delivery_drone_horde_the_party_is_benched_never_worse(horde):
    for _ in range(horde.MAX_DRAGS + 1):
        out = horde.answer_drone("D-0412")
    assert "benched" in out and horde.state["leg"] == 0


def test_delivery_drone_horde_advance_stops_at_the_exit(horde):
    for _ in range(10):
        out = horde.advance()
    assert horde.state["leg"] == len(horde.COURSE) - 1 and "clear" in out


def test_delivery_drone_horde_every_todo_line_is_kept():
    text = (ROOT / HORDE).read_text()
    for step in (1, 2, 3):
        assert f"# TODO: Step {step} -" in text
