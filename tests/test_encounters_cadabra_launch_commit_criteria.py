"""One offline check per step of Launch Commit Criteria, the Floor 6 Cadabra encounter.

No test calls a model or AWS. The pacer is a plain HookProvider, so each test builds the real strands
hook events by hand, feeds them to the pacer or to a real HookRegistry, and reads what the pacer set.
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import sys
import types
from pathlib import Path

import pytest
from strands.hooks.events import BeforeModelCallEvent, BeforeToolCallEvent

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
LCC = "dungeon/encounters/floor-6-launch-commit-criteria/launch_commit_criteria.py"


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


class FakeClock:
    """A clock the test moves by hand."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


class FakeAgent:
    """Records the keywords given to Agent(...) and the prompts the loop sends."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.prompts: list[str] = []

    def __call__(self, prompt):
        self.prompts.append(prompt)
        return f"reply {len(self.prompts)}"


@pytest.fixture
def lcc():
    return load(LCC, "encounter_launch_commit_criteria")


@pytest.fixture
def clock():
    return FakeClock()


def tool_event(name: str = "go_no_go") -> BeforeToolCallEvent:
    agent = types.SimpleNamespace()
    tool_use = {"toolUseId": "t1", "name": name, "input": {}}
    return BeforeToolCallEvent(agent=agent, selected_tool=None, tool_use=tool_use, invocation_state={})


def model_event() -> BeforeModelCallEvent:
    return BeforeModelCallEvent(agent=types.SimpleNamespace(), invocation_state={})


# ---------- Step 1: register the callbacks ------------------------------------


def test_launch_commit_criteria_registers_a_callback_for_tool_and_model_events(lcc):
    registry = lcc.HookRegistry()
    pacer = lcc.LaunchPacer()
    pacer.register_hooks(registry)
    assert set(registry._registered_callbacks) == {BeforeToolCallEvent, BeforeModelCallEvent}
    assert [c.callback for c in registry._registered_callbacks[BeforeToolCallEvent]] == [pacer.pace_the_poll]
    assert [c.callback for c in registry._registered_callbacks[BeforeModelCallEvent]] == [pacer.count_model_call]


def test_launch_commit_criteria_pacer_works_through_a_real_registry(lcc, clock):
    registry = lcc.HookRegistry()
    pacer = lcc.LaunchPacer(clock=clock)
    pacer.register_hooks(registry)
    first, _ = asyncio.run(registry.invoke_callbacks_async(tool_event()))
    second, _ = asyncio.run(registry.invoke_callbacks_async(tool_event()))
    assert first.cancel_tool is False
    assert isinstance(second.cancel_tool, str) and "too soon" in second.cancel_tool


# ---------- Step 2: the budget of polls --------------------------------------


def test_launch_commit_criteria_lets_polls_through_up_to_the_budget(lcc, clock):
    pacer = lcc.LaunchPacer(min_interval=5.0, tool_budget=3, clock=clock)
    for _ in range(3):
        event = tool_event()
        pacer.pace_the_poll(event)
        assert event.cancel_tool is False
        clock.now += 10.0
    assert pacer.polls == 3


def test_launch_commit_criteria_cancels_the_poll_once_the_budget_is_spent(lcc, clock):
    pacer = lcc.LaunchPacer(min_interval=5.0, tool_budget=2, clock=clock)
    for _ in range(2):
        pacer.pace_the_poll(tool_event())
        clock.now += 10.0
    event = tool_event()
    pacer.pace_the_poll(event)
    assert isinstance(event.cancel_tool, str)
    assert "budget" in event.cancel_tool and "Do NOT" in event.cancel_tool
    assert pacer.polls == 2, "a refused poll is not counted as a poll"
    assert pacer.attempts == 3


# ---------- Step 3: the minimum interval --------------------------------------


def test_launch_commit_criteria_cancels_a_poll_that_comes_too_soon(lcc, clock):
    pacer = lcc.LaunchPacer(min_interval=20.0, tool_budget=9, clock=clock)
    pacer.pace_the_poll(tool_event())
    clock.now += 5.0
    event = tool_event()
    pacer.pace_the_poll(event)
    assert isinstance(event.cancel_tool, str)
    assert "15 seconds" in event.cancel_tool, "the message tells the System AI how long is left"
    assert pacer.polls == 1


def test_launch_commit_criteria_a_refused_poll_does_not_restart_the_interval(lcc, clock):
    pacer = lcc.LaunchPacer(min_interval=20.0, tool_budget=9, clock=clock)
    pacer.pace_the_poll(tool_event())
    clock.now += 19.0
    pacer.pace_the_poll(tool_event())
    clock.now += 1.0
    event = tool_event()
    pacer.pace_the_poll(event)
    assert event.cancel_tool is False, "20 seconds after the last allowed poll is enough"
    assert pacer.polls == 2


def test_launch_commit_criteria_first_poll_is_never_too_soon(lcc, clock):
    pacer = lcc.LaunchPacer(clock=clock)
    event = tool_event()
    pacer.pace_the_poll(event)
    assert event.cancel_tool is False and pacer.last_poll == clock.now


def test_launch_commit_criteria_other_tools_are_not_paced(lcc, clock):
    pacer = lcc.LaunchPacer(min_interval=20.0, tool_budget=1, clock=clock)
    pacer.pace_the_poll(tool_event())
    event = tool_event(name="roll_dice")
    pacer.pace_the_poll(event)
    assert event.cancel_tool is False
    assert pacer.attempts == 1


def test_launch_commit_criteria_a_flood_ends_with_two_polls_let_through(lcc, clock):
    pacer = lcc.LaunchPacer(min_interval=20.0, tool_budget=3, clock=clock)
    cancelled = 0
    for _ in range(8):
        event = tool_event()
        pacer.pace_the_poll(event)
        cancelled += bool(event.cancel_tool)
        clock.now += 4.0
    assert pacer.polls == 2 and cancelled == 6
    assert "refused 6" in pacer.report()


# ---------- Step 4: the budget of model calls --------------------------------


def test_launch_commit_criteria_model_calls_pass_until_the_budget_is_spent(lcc):
    pacer = lcc.LaunchPacer(model_budget=3)
    for _ in range(3):
        event = model_event()
        pacer.count_model_call(event)
        assert event.cancel is False
    event = model_event()
    pacer.count_model_call(event)
    assert isinstance(event.cancel, str) and "model calls" in event.cancel
    assert pacer.model_calls == 4
    assert "cancelled 1" in pacer.report()


# ---------- the given pieces --------------------------------------------------


def test_launch_commit_criteria_go_no_go_turns_every_station_go_by_the_second_poll(lcc):
    lcc.poll_log.clear()
    first = lcc.go_no_go()
    assert first["poll"] == 1 and first["all_go"] is False
    assert first["stations"]["range safety"] == "NO-GO" and first["stations"]["weather"] == "GO"
    second = lcc.go_no_go()
    assert second["poll"] == 2 and second["all_go"] is True
    assert lcc.poll_log == [1, 2]
    lcc.poll_log.clear()


def test_launch_commit_criteria_system_ai_has_the_pacer_and_the_tool_on_nova(lcc, monkeypatch):
    monkeypatch.setattr(lcc, "Agent", FakeAgent)
    pacer = lcc.LaunchPacer()
    system_ai = lcc.make_system_ai(pacer)
    kwargs = system_ai.kwargs
    assert kwargs["model"] == NOVA
    assert kwargs["hooks"] == [pacer]
    assert [t.tool_name for t in kwargs["tools"]] == ["go_no_go"]
    assert kwargs["system_prompt"].endswith("Plain text only, no emoji.")


def test_launch_commit_criteria_agent_model_is_nova_2_lite_in_the_source():
    keywords = agent_call_keywords(LCC)
    assert ast.literal_eval(keywords["model"]) == NOVA
    assert "pacer" in names_in(keywords["hooks"])


def test_launch_commit_criteria_loop_asks_once_per_tick_with_no_sleep(lcc, monkeypatch, capsys):
    system_ai = FakeAgent()
    monkeypatch.setattr(lcc.time, "sleep", lambda s: pytest.fail("the flood does not wait"))
    lcc.launch_control(system_ai, ticks=5)
    assert len(system_ai.prompts) == 5
    assert "Tick 3 of 5" in system_ai.prompts[2]
    assert "tick 5: reply 5" in capsys.readouterr().out


def test_launch_commit_criteria_importing_calls_no_model():
    tree = ast.parse((ROOT / LCC).read_text())
    top_level_calls = [n for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)]
    assert top_level_calls == []


def test_launch_commit_criteria_keeps_four_todo_steps():
    todos = [line for line in (ROOT / LCC).read_text().splitlines() if line.lstrip().startswith("# TODO: Step")]
    assert len(todos) == 4
