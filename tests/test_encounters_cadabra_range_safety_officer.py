"""One offline check per step of Range Safety Officer Protocol, the Floor 8 Cadabra encounter.

No test calls a model or AWS. The interrupt flow runs through the real Strands agent loop with a scripted
stand-in for the model (range_control_drill.ScriptedModel), so a test proves what the SDK does when the
tool raises, pauses, resumes and raises again. The pieces the learner writes are also called directly,
with a ToolContext built by hand over a real interrupt state.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
from pathlib import Path

import pytest
from strands.interrupt import InterruptException, _InterruptState
from strands.types.tools import ToolContext

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
RSO = "dungeon/encounters/floor-8-range-safety-officer/range_safety_officer.py"

DRONE = "stray delivery drone"
RUN = "party run"


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
def rso(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-west-2")
    mod = load(RSO, "encounter_range_safety_officer")
    mod.FIRED.clear()
    return mod


def tool_context(state: _InterruptState, tool_use_id: str = "t1") -> ToolContext:
    agent = types.SimpleNamespace(_interrupt_state=state)
    return ToolContext(tool_use={"toolUseId": tool_use_id, "name": "flight_termination", "input": {}},
                       agent=agent, invocation_state={})


def director_for(rso, *targets: str):
    """Range control on a scripted model that calls flight_termination once per target."""
    from range_control_drill import ScriptedModel  # on sys.path while the encounter loads, so add it here

    director = rso.make_director()
    calls = [("flight_termination", {"target": target, "cause": "a test cause"}) for target in targets]
    director.model = ScriptedModel([calls, "Range control reports."])
    return director


@pytest.fixture(autouse=True)
def drill_on_path():
    folder = str(ROOT / "dungeon/encounters/floor-8-range-safety-officer")
    sys.path.insert(0, folder)
    yield
    sys.path.remove(folder)
    sys.modules.pop("range_control_drill", None)


def respond(rso, answers: dict[str, str]):
    """An officer who answers each key by the interrupt's name, and keeps a record of who was asked."""
    asked: list[str] = []

    def officer(interrupt) -> str:
        asked.append(interrupt.name)
        return answers[interrupt.name]

    officer.asked = asked
    return officer


# ---------- the given code: model, tools, prompt -------------------------------


def test_range_safety_officer_agent_uses_nova_2_lite_and_the_termination_tool(rso):
    kw = agent_call_keywords(RSO)
    assert ast.literal_eval(kw["model"]) == NOVA
    assert "flight_termination" in names_in(kw["tools"])
    assert ast.literal_eval(kw["callback_handler"]) is None
    assert rso.PROMPT.rstrip().endswith("Plain text only, no emoji.")


def test_range_safety_officer_tool_is_a_context_tool_with_a_target_and_a_cause(rso):
    spec = rso.flight_termination.tool_spec
    assert spec["name"] == "flight_termination"
    props = spec["inputSchema"]["json"]["properties"]
    assert set(props) == {"target", "cause"}, "the ToolContext is injected, never offered to the model"


# ---------- Step 1: raise the interrupt ----------------------------------------


def test_range_safety_officer_ask_key_pauses_with_the_reason(rso):
    state = _InterruptState()
    reason = {"key": "ARM", "target": RUN, "cause": "c", "effect": "e"}
    with pytest.raises(InterruptException) as paused:
        rso.ask_key(tool_context(state), "range_safety_arm", reason, None)
    assert paused.value.interrupt.name == "range_safety_arm"
    assert paused.value.interrupt.reason == reason
    assert paused.value.interrupt.id in state.interrupts


def test_range_safety_officer_ask_key_returns_the_answer_on_the_resume(rso):
    state = _InterruptState()
    context = tool_context(state)
    with pytest.raises(InterruptException) as paused:
        rso.ask_key(context, "range_safety_arm", {"key": "ARM"}, None)
    state.interrupts[paused.value.interrupt.id].response = "hold"
    assert rso.ask_key(context, "range_safety_arm", {"key": "ARM"}, None) == "hold"


def test_range_safety_officer_ask_key_uses_a_standing_order_without_pausing(rso):
    state = _InterruptState()
    assert rso.ask_key(tool_context(state), "range_safety_arm", {"key": "ARM"}, "approve") == "approve"


# ---------- Step 2: the second key --------------------------------------------


def test_range_safety_officer_a_run_pauses_first_on_arm_then_on_destruct(rso):
    director = director_for(rso, RUN)
    result = director("end it")
    assert result.stop_reason == "interrupt"
    assert [i.name for i in result.interrupts] == ["range_safety_arm"]
    result = director(rso.answers_for(result, respond(rso, {"range_safety_arm": "approve"})))
    assert result.stop_reason == "interrupt"
    assert [i.name for i in result.interrupts] == ["range_safety_destruct"]
    assert result.interrupts[0].reason["key"] == "DESTRUCT"
    assert rso.FIRED == []


def test_range_safety_officer_both_keys_fire_the_termination(rso):
    officer = respond(rso, {"range_safety_arm": "approve", "range_safety_destruct": "approve"})
    rso.run_range(director_for(rso, RUN), "end it", officer)
    assert officer.asked == ["range_safety_arm", "range_safety_destruct"]
    assert rso.FIRED == [RUN]


def test_range_safety_officer_a_hold_on_the_destruct_key_stops_the_termination(rso):
    officer = respond(rso, {"range_safety_arm": "approve", "range_safety_destruct": "hold"})
    director = director_for(rso, RUN)
    rso.run_range(director, "end it", officer)
    assert rso.FIRED == []
    results = [b["toolResult"] for m in director.messages for b in m["content"] if "toolResult" in b]
    assert results and results[-1]["content"][0]["text"].startswith("HOLD") and "armed" in results[-1]["content"][0]["text"]


def test_range_safety_officer_a_hold_on_the_arm_key_never_asks_for_the_second(rso):
    officer = respond(rso, {"range_safety_arm": "hold"})
    rso.run_range(director_for(rso, RUN), "end it", officer)
    assert officer.asked == ["range_safety_arm"]
    assert rso.FIRED == []


# ---------- Step 3: the standing order ---------------------------------------


def test_range_safety_officer_standing_order_covers_the_drone_and_ignores_case(rso):
    assert rso.standing_order(DRONE) == "approve"
    assert rso.standing_order("  Stray Delivery Drone ") == "approve"


def test_range_safety_officer_no_standing_order_for_the_party_run_or_an_unknown_name(rso):
    assert rso.standing_order(RUN) is None
    assert rso.standing_order("the drone") is None, "a name that matches no order pauses; it never fires"


def test_range_safety_officer_the_drone_fires_without_a_pause(rso):
    officer = respond(rso, {})
    result = rso.run_range(director_for(rso, DRONE), "end it", officer)
    assert officer.asked == []
    assert rso.FIRED == [DRONE]
    assert "Range control" in result


def test_range_safety_officer_one_turn_pauses_on_the_run_while_the_drone_fires(rso):
    director = director_for(rso, DRONE, RUN)
    result = director("end both")
    assert result.stop_reason == "interrupt"
    assert [i.name for i in result.interrupts] == ["range_safety_arm"]
    assert result.interrupts[0].reason["target"] == RUN
    assert rso.FIRED == [DRONE], "the drone's standing order let it through while the run waited"


# ---------- Step 4: answer every interrupt -----------------------------------


def test_range_safety_officer_answers_for_builds_one_block_per_interrupt(rso):
    interrupts = [types.SimpleNamespace(id="a", name="range_safety_arm", reason={"key": "ARM"}),
                  types.SimpleNamespace(id="b", name="range_safety_destruct", reason={"key": "DESTRUCT"})]
    result = types.SimpleNamespace(stop_reason="interrupt", interrupts=interrupts)
    blocks = rso.answers_for(result, lambda i: "approve" if i.id == "a" else "hold")
    assert blocks == [
        {"interruptResponse": {"interruptId": "a", "response": "approve"}},
        {"interruptResponse": {"interruptId": "b", "response": "hold"}},
    ]


def test_range_safety_officer_run_range_resumes_the_same_agent_until_the_turn_ends(rso):
    officer = respond(rso, {"range_safety_arm": "approve", "range_safety_destruct": "approve"})
    director = director_for(rso, RUN)
    text = rso.run_range(director, "end it", officer)
    assert text.startswith("Range control")
    assert director._interrupt_state.activated is False


def test_range_safety_officer_resuming_a_different_agent_is_refused(rso):
    first = director_for(rso, RUN)
    paused = first("end it")
    other = director_for(rso, RUN)
    with pytest.raises((TypeError, KeyError, ValueError, RuntimeError)):
        other(rso.answers_for(paused, respond(rso, {"range_safety_arm": "approve"})))


# ---------- the officers ----------------------------------------------------


def test_range_safety_officer_drill_officer_arms_and_holds_the_destruct_key(rso):
    arm = types.SimpleNamespace(reason={"key": "ARM", "target": RUN})
    destruct = types.SimpleNamespace(reason={"key": "DESTRUCT", "target": RUN})
    assert rso.drill_officer(arm) == "approve"
    assert rso.drill_officer(destruct) == "hold"


def test_range_safety_officer_console_officer_approves_only_the_word_approve(rso, monkeypatch):
    interrupt = types.SimpleNamespace(reason={"key": "ARM", "target": RUN, "cause": "c", "effect": "e"})
    for typed, expected in (("approve", "approve"), (" APPROVE ", "approve"), ("y", "hold"), ("", "hold"), ("approved", "hold")):
        monkeypatch.setattr("builtins.input", lambda _prompt="", typed=typed: typed)
        assert rso.console_officer(interrupt) == expected


def test_range_safety_officer_the_drill_ends_with_only_the_drone_fired(rso, capsys):
    text = rso.run_range(rso.make_drill_director(), rso.DRILL_REQUEST, rso.drill_officer)
    assert rso.FIRED == [DRONE]
    assert "hold" in text.lower()
    assert "RANGE SAFETY KEY DESTRUCT" in capsys.readouterr().out


def test_range_safety_officer_a_pause_costs_no_model_call(rso):
    director = rso.make_drill_director()
    rso.run_range(director, rso.DRILL_REQUEST, rso.drill_officer)
    assert director.model.played == 2, "one call to pick the tools, one to report; the pauses add none"


def test_range_safety_officer_importing_calls_no_model(rso):
    assert callable(rso.make_director) and rso.FIRED == []
