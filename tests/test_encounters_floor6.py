"""One offline check per Floor 6 encounter step: The Hype Meter and Sponsor Interrupt.

No test calls a model, AWS, or the dice server. Each narrator script builds its Agent at import, and
building it would try to reach the dice server on port 8002, so these tests swap in a recording stand-in
for ``strands.Agent`` before the script loads and read what the script passed to it.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
from pathlib import Path

import pytest
import strands
from fastapi.testclient import TestClient
from strands.hooks.events import AfterModelCallEvent, AfterToolCallEvent, BeforeToolCallEvent
from strands.interrupt import Interrupt, InterruptException, _InterruptState

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
HYPE = "encounters/floor-6-hype-meter/hype_meter.py"
SPONSOR = "encounters/floor-6-sponsor-interrupt/sponsor_interrupt.py"
FLOOR5_NARRATOR = "5_a2a_integration/agents/narrator_orchestrator/narrator_orchestrator.py"


class FakeAgent:
    """Records the keywords a narrator script gives Agent(...) and replays scripted results."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.messages = []
        self.calls = []
        self.script = []

    async def invoke_async(self, prompt):
        self.calls.append(prompt)
        return self.script.pop(0)


def load(rel: str, name: str, monkeypatch):
    """Import an encounter script under a unique module name, with Agent swapped for FakeAgent."""
    monkeypatch.setattr(strands, "Agent", FakeAgent)
    path = ROOT / rel
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.remove(str(path.parent))


def tool_names(tools) -> list[str]:
    return [getattr(t, "tool_name", None) for t in tools if getattr(t, "tool_name", None)]


def story(mod, text="SYSTEM: the turn.") -> object:
    return mod.StoryOutput(response=text, actions_suggestions=["a", "b", "c"], details="none", dice_rolls=[])


def tool_event(tool_name: str, status: str = "success", /, **given):
    """A stand-in AfterToolCallEvent; positional-only so a tool input called "name" can pass through."""
    return types.SimpleNamespace(result={"status": status}, tool_use={"name": tool_name, "input": given})


def model_event(text: str):
    message = {"content": [{"text": text}]}
    return types.SimpleNamespace(stop_response=types.SimpleNamespace(message=message))


def story_output_class(rel: str) -> str:
    tree = ast.parse((ROOT / rel).read_text())
    cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "StoryOutput")
    return ast.dump(cls)


def uvicorn_port(rel: str) -> int:
    tree = ast.parse((ROOT / rel).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "run":
            for kw in node.keywords:
                if kw.arg == "port":
                    return kw.value.value
    raise AssertionError(f"no uvicorn.run(..., port=...) in {rel}")


def todo_count(rel: str) -> int:
    return sum(1 for line in (ROOT / rel).read_text().splitlines() if line.lstrip().startswith("# TODO: Step"))


# ---------- The Hype Meter ----------------------------------------------------


@pytest.fixture
def hype(monkeypatch):
    return load(HYPE, "encounter_hype_meter", monkeypatch)


def test_hype_meter_registers_a_callback_for_tool_and_model_events(hype):
    registry = hype.HookRegistry()
    meter = hype.HypeMeter()
    meter.register_hooks(registry)
    assert set(registry._registered_callbacks) == {AfterToolCallEvent, AfterModelCallEvent}
    tool_callbacks = registry._registered_callbacks[AfterToolCallEvent]
    model_callbacks = registry._registered_callbacks[AfterModelCallEvent]
    assert [c.callback for c in tool_callbacks] == [meter.on_tool_result]
    assert [c.callback for c in model_callbacks] == [meter.on_model_reply]


def test_hype_meter_scores_rounds_final_beats_and_benching(hype):
    meter = hype.HypeMeter()
    meter.on_tool_result(tool_event("call_the_round", winner="party"))
    meter.on_tool_result(tool_event("call_the_round", winner="party"))
    assert meter.hype == 2, "+1 for each round the party won"
    meter.on_tool_result(tool_event("call_the_round", winner="opponent"))
    assert meter.hype == 2, "a lost round earns nothing"
    meter.on_tool_result(tool_event("call_the_round", winner="party", final_beat=True))
    assert meter.hype == 5, "+3 for a Final Beat the party won"
    meter.on_tool_result(tool_event("bench_crawler", name="Cordula"))
    assert meter.hype == 2, "half of all Hype is lost when a Crawler is benched"


def test_hype_meter_ignores_tool_calls_that_failed_or_are_not_its_own(hype):
    meter = hype.HypeMeter()
    meter.on_tool_result(tool_event("call_the_round", "error", winner="party"))
    meter.on_tool_result(tool_event("roll_dice", dice_type="1d20"))
    assert meter.hype == 0


def test_hype_meter_scores_each_achievement_title_once(hype):
    meter = hype.HypeMeter()
    meter.on_model_reply(model_event("NEW ACHIEVEMENT UNLOCKED [SMASH THAT LIKE BUTTON] Bronze Box"))
    meter.on_model_reply(model_event("again: NEW ACHIEVEMENT UNLOCKED [SMASH THAT LIKE BUTTON] Bronze Box"))
    assert meter.hype == 5, "+5 for an achievement, and a repeated title does not pay twice"
    meter.on_model_reply(model_event("NEW ACHIEVEMENT UNLOCKED [OPENING NIGHT JITTERS] Silver Box"))
    assert meter.hype == 10


def test_hype_meter_reads_achievements_out_of_the_structured_story_call(hype):
    meter = hype.HypeMeter()
    message = {"content": [{"toolUse": {"toolUseId": "t", "name": "StoryOutput",
                                         "input": {"response": "NEW ACHIEVEMENT UNLOCKED [FOG MACHINE] Gold Box"}}}]}
    meter.on_model_reply(types.SimpleNamespace(stop_response=types.SimpleNamespace(message=message)))
    assert meter.hype == 5
    meter.on_model_reply(types.SimpleNamespace(stop_response=None))
    assert meter.hype == 5, "a model call that failed has no reply to read"


def test_hype_meter_reaches_sponsor_tiers_at_10_25_and_50(hype):
    meter = hype.HypeMeter()
    assert hype.SPONSOR_TIERS == (10, 25, 50)
    meter.add(9, "setup")
    assert meter.snapshot()["sponsor_tiers"] == [] and meter.snapshot()["next_sponsor_at"] == 10
    meter.add(1, "setup")
    assert meter.snapshot()["sponsor_tiers"] == [10] and meter.snapshot()["next_sponsor_at"] == 25
    meter.add(60, "setup")
    snap = meter.snapshot()
    assert snap["sponsor_tiers"] == [10, 25, 50] and snap["next_sponsor_at"] is None
    meter.on_tool_result(tool_event("bench_crawler", name="Barnaby"))
    assert meter.snapshot()["sponsor_tiers"] == [10, 25, 50], "a box already sent stays sent"


def test_hype_meter_agent_gets_the_meter_as_a_hook(hype):
    kwargs = hype.agent.kwargs
    assert kwargs["hooks"] == [hype.hype_meter]
    assert isinstance(hype.hype_meter, hype.HypeMeter)
    assert {"call_the_round", "bench_crawler"} <= set(tool_names(kwargs["tools"]))
    assert kwargs["structured_output_model"] is hype.StoryOutput
    assert kwargs["model"] is hype.NARRATOR_MODEL
    assert hype.NARRATOR_MODEL.config["model_id"] == NOVA


def test_hype_meter_route_serves_the_meter_snapshot(hype):
    client = TestClient(hype.app)
    first = client.get("/hype").json()
    assert first == {"hype": 0, "sponsor_tiers": [], "next_sponsor_at": 10, "last_event": ""}
    hype.hype_meter.add(12, "round won")
    second = client.get("/hype").json()
    assert second["hype"] == 12 and second["sponsor_tiers"] == [10] and second["next_sponsor_at"] == 25
    assert second["last_event"] == "round won: +12 Hype"


def test_hype_meter_serves_the_floor5_routes_on_the_same_port(hype):
    paths = {route.path for route in hype.app.routes}
    assert {"/health", "/messages", "/user/{user_name}", "/inquire", "/hype"} <= paths
    assert uvicorn_port(HYPE) == uvicorn_port(FLOOR5_NARRATOR) == 8009
    assert story_output_class(HYPE) == story_output_class(FLOOR5_NARRATOR), "StoryOutput must match Floor 5 field for field"


def test_hype_meter_inquire_still_returns_the_plain_story(hype):
    hype.agent.script.append(types.SimpleNamespace(structured_output=story(hype, "SYSTEM: hello")))
    body = TestClient(hype.app).post("/inquire", json={"question": "hi"}).json()
    assert body["response"]["response"] == "SYSTEM: hello"
    assert "interrupt" not in body


def test_hype_meter_tools_check_who_won(hype):
    assert hype.call_the_round(winner="party", final_beat=True) == "Round called for the party."
    with pytest.raises(ValueError):
        hype.call_the_round(winner="nobody")
    assert "Cordula" in hype.bench_crawler(name="Cordula")


def test_hype_meter_keeps_four_todo_steps():
    assert todo_count(HYPE) == 4


# ---------- Sponsor Interrupt -------------------------------------------------


@pytest.fixture
def sponsor(monkeypatch):
    return load(SPONSOR, "encounter_sponsor_interrupt", monkeypatch)


DEAL = {"sponsor": "The Bellevue Consortium", "offer": "Wear the logo for one floor.",
        "reward": "a Silver Box", "cost": "your dignity"}


def deal_event(state: _InterruptState, name: str = "sponsor_offer", given: dict | None = None):
    agent = types.SimpleNamespace(_interrupt_state=state)
    tool_use = {"toolUseId": "t1", "name": name, "input": DEAL if given is None else given}
    return BeforeToolCallEvent(agent=agent, selected_tool=None, tool_use=tool_use, invocation_state={})


def test_sponsor_interrupt_registers_a_callback_for_before_tool_call(sponsor):
    registry = sponsor.HookRegistry()
    deals = sponsor.SponsorDeals()
    deals.register_hooks(registry)
    assert list(registry._registered_callbacks) == [BeforeToolCallEvent]
    assert [c.callback for c in registry._registered_callbacks[BeforeToolCallEvent]] == [deals.ask_the_player]


def test_sponsor_interrupt_pauses_the_turn_with_the_deal_as_the_reason(sponsor):
    state = _InterruptState()
    with pytest.raises(InterruptException) as paused:
        sponsor.SponsorDeals().ask_the_player(deal_event(state))
    assert paused.value.interrupt.name == "sponsor_deal"
    assert paused.value.interrupt.reason == DEAL
    assert paused.value.interrupt.id in state.interrupts


def test_sponsor_interrupt_lets_other_tools_through(sponsor):
    state = _InterruptState()
    event = deal_event(state, name="roll_dice", given={"dice_type": "1d20"})
    sponsor.SponsorDeals().ask_the_player(event)
    assert state.interrupts == {} and event.cancel_tool is False


def test_sponsor_interrupt_accepting_lets_the_tool_run(sponsor):
    state = _InterruptState()
    deals = sponsor.SponsorDeals()
    with pytest.raises(InterruptException) as paused:
        deals.ask_the_player(deal_event(state))
    state.interrupts[paused.value.interrupt.id].response = "accept"
    event = deal_event(state)
    deals.ask_the_player(event)
    assert event.cancel_tool is False


def test_sponsor_interrupt_refusing_cancels_the_tool_with_a_message(sponsor):
    state = _InterruptState()
    deals = sponsor.SponsorDeals()
    with pytest.raises(InterruptException) as paused:
        deals.ask_the_player(deal_event(state))
    state.interrupts[paused.value.interrupt.id].response = "refuse"
    event = deal_event(state)
    deals.ask_the_player(event)
    assert isinstance(event.cancel_tool, str) and "refused" in event.cancel_tool


def test_sponsor_interrupt_agent_has_the_hook_and_the_tool_on_nova(sponsor):
    kwargs = sponsor.agent.kwargs
    assert kwargs["hooks"] == [sponsor.sponsor_deals]
    assert isinstance(sponsor.sponsor_deals, sponsor.SponsorDeals)
    assert "sponsor_offer" in tool_names(kwargs["tools"])
    assert kwargs["structured_output_model"] is sponsor.StoryOutput
    assert kwargs["model"] is sponsor.NARRATOR_MODEL
    assert sponsor.NARRATOR_MODEL.config["model_id"] == NOVA


def test_sponsor_interrupt_inquire_returns_the_interrupt_beside_a_holding_story(sponsor):
    paused = Interrupt(id="v1:before_tool_call:t1:abc", name="sponsor_deal", reason=DEAL)
    sponsor.agent.script.append(types.SimpleNamespace(stop_reason="interrupt", interrupts=[paused], structured_output=None))
    body = TestClient(sponsor.app).post("/inquire", json={"question": "hi"}).json()
    assert body["interrupt"] == {"id": "v1:before_tool_call:t1:abc", "name": "sponsor_deal", "reason": DEAL}
    holding = body["response"]
    assert set(holding) == {"response", "actions_suggestions", "details", "dice_rolls"}, "the plain HUD can still draw it"
    assert "The Bellevue Consortium" in holding["response"]
    assert holding["actions_suggestions"] == []


def test_sponsor_interrupt_inquire_without_a_deal_returns_the_plain_story(sponsor):
    done = types.SimpleNamespace(stop_reason="end_turn", interrupts=None, structured_output=story(sponsor, "SYSTEM: hello"))
    sponsor.agent.script.append(done)
    body = TestClient(sponsor.app).post("/inquire", json={"question": "hi"}).json()
    assert body["response"]["response"] == "SYSTEM: hello"
    assert "interrupt" not in body


@pytest.mark.parametrize("accepted, word", [(True, "accept"), (False, "refuse")])
def test_sponsor_interrupt_respond_resumes_the_agent_with_the_answer(sponsor, accepted, word):
    done = types.SimpleNamespace(stop_reason="end_turn", interrupts=None, structured_output=story(sponsor, "SYSTEM: resumed"))
    sponsor.agent.script.append(done)
    reply = TestClient(sponsor.app).post("/respond", json={"interrupt_id": "id-1", "accepted": accepted})
    assert reply.status_code == 200 and reply.json()["response"]["response"] == "SYSTEM: resumed"
    assert sponsor.agent.calls == [[{"interruptResponse": {"interruptId": "id-1", "response": word}}]]


def test_sponsor_interrupt_respond_can_pause_again_on_a_second_deal(sponsor):
    again = Interrupt(id="second", name="sponsor_deal", reason=DEAL)
    sponsor.agent.script.append(types.SimpleNamespace(stop_reason="interrupt", interrupts=[again], structured_output=None))
    body = TestClient(sponsor.app).post("/respond", json={"interrupt_id": "first", "accepted": True}).json()
    assert body["interrupt"]["id"] == "second"


def test_sponsor_interrupt_serves_the_floor5_routes_on_the_same_port(sponsor):
    paths = {route.path for route in sponsor.app.routes}
    assert {"/health", "/messages", "/user/{user_name}", "/inquire", "/respond"} <= paths
    assert uvicorn_port(SPONSOR) == uvicorn_port(FLOOR5_NARRATOR) == 8009
    assert story_output_class(SPONSOR) == story_output_class(FLOOR5_NARRATOR), "StoryOutput must match Floor 5 field for field"


def test_sponsor_interrupt_keeps_five_todo_steps():
    assert todo_count(SPONSOR) == 5
