"""Offline checks for the Floor 5 side passages: Barnaby Takes the Call, Read the Room Typed, Subcontract the Paperwork.

No test calls a model, a remote agent or AWS. The scripts run their agents only under
``if __name__ == "__main__":``, so importing them builds objects and calls nothing.
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import random
import sys
from pathlib import Path

import pytest
from a2a.types import (
    Artifact,
    Message,
    Part,
    Role,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
)

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
CALL = "encounters/floor-5-barnaby-takes-the-call/barnaby_takes_the_call.py"
TYPED = "encounters/floor-5-read-the-room-typed/read_the_room_typed.py"
PAPERWORK = "encounters/floor-5-subcontract-the-paperwork/subcontract_the_paperwork.py"


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


# ---------- Barnaby Takes the Call -------------------------------------------


@pytest.fixture
def call():
    return load(CALL, "encounter_barnaby_call")


def a2a_parts(text: str) -> list[Part]:
    return [Part(root=TextPart(text=text))]


def a2a_task(state: TaskState = TaskState.working) -> Task:
    return Task(id="t1", context_id="c1", status=TaskStatus(state=state))


def test_barnaby_takes_the_call_imports_the_a2a_client_and_server(call):
    from strands.agent.a2a_agent import A2AAgent
    from strands.multiagent.a2a.server import A2AServer

    assert call.A2AAgent is A2AAgent
    assert call.A2AServer is A2AServer


def test_barnaby_takes_the_call_phone_is_an_a2a_agent_with_a_60_second_timeout(call):
    from strands.agent.a2a_agent import A2AAgent

    line = call.phone(call.RULES_URL)
    assert isinstance(line, A2AAgent)
    assert line.endpoint == "http://127.0.0.1:8000"
    assert line.timeout == 60


def test_barnaby_takes_the_call_dials_the_floor_5_agents_and_not_the_a2a_client_tool(call):
    assert [url for url, _ in call.CALLS] == ["http://127.0.0.1:8000", "http://127.0.0.1:8001"]
    source = (ROOT / CALL).read_text()
    assert "make_a2a_client" not in source


def test_barnaby_takes_the_call_describes_each_kind_of_a2a_event(call):
    message = Message(message_id="m1", role=Role.agent, parts=a2a_parts("hello there"))
    status = TaskStatusUpdateEvent(context_id="c1", task_id="t1", final=False,
                                   status=TaskStatus(state=TaskState.working, message=message))
    chunk = TaskArtifactUpdateEvent(context_id="c1", task_id="t1",
                                    artifact=Artifact(artifact_id="a1", parts=a2a_parts("a chunk")))
    assert call.describe(message) == "message: hello there"
    assert call.describe((a2a_task(), status)) == "status working: hello there"
    assert call.describe((a2a_task(), chunk)) == "artifact chunk: a chunk"
    assert call.describe((a2a_task(TaskState.completed), None)) == "task completed"


def test_barnaby_takes_the_call_streams_each_event_and_keeps_the_result(call, capsys):
    message = Message(message_id="m1", role=Role.agent, parts=a2a_parts("the section is Final Beat"))

    class Line:
        async def stream_async(self, question):
            assert question == "q"
            yield {"type": "a2a_stream", "event": message}
            yield {"type": "a2a_stream", "event": (a2a_task(TaskState.completed), None)}
            yield {"result": "the final answer"}

    result = asyncio.run(call.take_the_call(Line(), "q"))
    assert result == "the final answer"
    out = capsys.readouterr().out
    assert "message: the section is Final Beat" in out
    assert "task completed" in out
    assert "the final answer" not in out, "only the A2A events print inside the loop; main prints the result"


def test_barnaby_takes_the_call_line_serves_barnaby_on_port_8003(call):
    server = call.build_barnaby_line()
    assert isinstance(server, call.A2AServer)
    assert server.port == call.BARNABY_PORT == 8003
    assert server.name == "Barnaby"


def test_barnaby_takes_the_call_barnaby_runs_on_nova_2_lite(call):
    barnaby = call.create_barnaby("any-context")
    assert barnaby.model.config["model_id"] == NOVA
    kw = agent_call_keywords(CALL)
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA


# ---------- Read the Room, Typed ---------------------------------------------


@pytest.fixture
def typed():
    mod = load(TYPED, "encounter_read_the_room_typed")
    mod.scoreboard.clear()
    return mod


class ScriptedDecisions:
    """Stands in for LLMDecisionModel: records each ask and answers from a script."""

    def __init__(self, answers):
        from strands.decisions.types import DecisionMetadata, DecisionResult

        self.script = iter(answers)
        self.asked = []
        self._make = lambda answers: DecisionResult(answers=answers, metadata=DecisionMetadata(latency_ms=1))

    async def ask(self, state, questions, **kwargs):
        self.asked.append((state, questions))
        return self._make(next(self.script))


def with_dice(monkeypatch, *faces):
    rolls = iter(faces)
    monkeypatch.setattr(random, "randint", lambda a, b: next(rolls))


def test_read_the_room_typed_imports_the_llm_decision_model(typed):
    from strands.decisions.llm_decision_model import LLMDecisionModel

    assert typed.LLMDecisionModel is LLMDecisionModel
    assert "typesafe" not in (ROOT / TYPED).read_text(), "the typesafe decision model calls a third-party hosted API"


def test_read_the_room_typed_decision_model_is_nova_2_lite_with_the_narrator_prompt(typed):
    from strands.decisions.llm_decision_model import LLMDecisionModel

    decision_model = typed.make_decision_model()
    assert isinstance(decision_model, LLMDecisionModel)
    assert decision_model._model.config["model_id"] == NOVA
    assert decision_model._system_prompt == typed.DECISION_PROMPT


def test_read_the_room_typed_first_round_asks_for_tempo_and_move_as_closed_choices(typed):
    from strands.decisions.decision_model import _validate_questions

    fake = ScriptedDecisions([{"tempo": "Driving", "move_call": "Footwork"}])
    answer = asyncio.run(typed.read_the_room(fake, typed.SITUATION, None, None))
    assert answer == ("Driving", "Footwork")
    state, questions = fake.asked[0]
    assert state == typed.SITUATION
    assert set(questions) == {"move_call", "tempo"}
    assert questions["tempo"]["choices"] == ["Steady", "Driving", "Frantic"]
    assert questions["move_call"]["choices"] == typed.MOVES
    assert all(q["uncertainty"] is False for q in questions.values())
    _validate_questions(questions)  # the SDK accepts the shape


def test_read_the_room_typed_later_rounds_keep_the_tempo_and_never_repeat_the_move(typed):
    fake = ScriptedDecisions([{"move_call": "Presence"}])
    answer = asyncio.run(typed.read_the_room(fake, typed.SITUATION, "Footwork", "Driving"))
    assert answer == ("Driving", "Presence")
    _, questions = fake.asked[0]
    assert set(questions) == {"move_call"}
    assert "Footwork" not in questions["move_call"]["choices"]
    assert len(questions["move_call"]["choices"]) == 5


def test_read_the_room_typed_the_party_member_with_the_better_modifier_dances(typed):
    assert typed.best_dancer("Footwork") == "Barnaby"
    assert typed.best_dancer("Power") == "Cordula"
    assert typed.best_dancer("Read the Room") == "Cordula", "a tie goes to Cordula"


def test_read_the_room_typed_the_typed_values_go_straight_into_dance_round(typed, monkeypatch):
    with_dice(monkeypatch, 15, 10)
    result = typed.dance("Driving", "Footwork")
    assert result["crawler"] == "Barnaby: 15 + 4 = 19"
    assert result["opponent_roll"] == "the Quarterly Close Accountant: 10 + 3 = 13", "+1 modifier and +2 for Driving"
    assert result["winner"] == "party"
    assert typed.scoreboard == [result]


def test_read_the_room_typed_a_dance_off_ends_when_the_party_has_two_rounds(typed, monkeypatch, capsys):
    fake = ScriptedDecisions([
        {"tempo": "Driving", "move_call": "Footwork"},
        {"move_call": "Power"},
    ])
    monkeypatch.setattr(typed, "make_decision_model", lambda: fake)
    with_dice(monkeypatch, 15, 10, 18, 4)
    asyncio.run(typed.main())
    out = capsys.readouterr().out
    assert len(typed.scoreboard) == 2
    assert "The System announces the tempo: Driving" in out
    assert "The party takes two of three." in out
    assert "Footwork" not in fake.asked[1][1]["move_call"]["choices"]


# ---------- Subcontract the Paperwork ----------------------------------------


@pytest.fixture
def paperwork():
    return load(PAPERWORK, "encounter_subcontract_paperwork")


def test_subcontract_the_paperwork_imports_the_subagent_factory_and_its_axes(paperwork):
    from strands.multiagent.spec import Fixed, Preset
    from strands.vended_tools.subagent.subagent import make_subagent

    assert paperwork.make_subagent is make_subagent
    assert paperwork.Fixed is Fixed
    assert paperwork.Preset is Preset


def test_subcontract_the_paperwork_clerk_tool_hides_instructions_tools_and_model_from_the_narrator(paperwork):
    clerk = paperwork.make_clerk_tool()
    assert clerk.tool_name == "hire_clerk"
    properties = clerk.tool_spec["inputSchema"]["json"]["properties"]
    assert set(properties) == {"task", "agent_type"}, "the model writes the task; the rules, tools and model are pinned"


def test_subcontract_the_paperwork_clerk_gets_the_preset_rules_and_only_the_calculator(paperwork):
    clerk = paperwork.make_clerk_tool()
    spec = clerk._resolve({"task": "file the report"})
    assert spec.agent_type == "clerk"
    assert spec.instructions == paperwork.CLERK_RULES
    assert spec.tools == ["add_up"]
    assert spec.name == "hire_clerk"


def test_subcontract_the_paperwork_clerk_model_is_pinned_to_nova_2_lite(paperwork):
    clerk = paperwork.make_clerk_tool()
    assert clerk._resolve({"task": "x"}).model == NOVA
    # a model that asks for another model or other rules is ignored: those axes are not in the schema
    pushed = clerk._resolve({"task": "x", "model": "something-else", "instructions": "do whatever"})
    assert pushed.model == NOVA
    assert pushed.instructions == paperwork.CLERK_RULES


def test_subcontract_the_paperwork_the_default_subagent_would_inherit_the_parents_model():
    from strands.vended_tools.subagent import subagent

    assert subagent._resolve({"task": "x"}).model is None, "None means the child builder uses the parent's model"
    assert "model" not in subagent.tool_spec["inputSchema"]["json"]["properties"]


def test_subcontract_the_paperwork_the_built_clerk_runs_on_nova_2_lite_with_add_up(paperwork):
    from strands.multiagent.spec import _default_builder

    clerk_tool = paperwork.make_clerk_tool()
    narrator = paperwork.make_narrator(clerk_tool)
    child = _default_builder(narrator)(clerk_tool._resolve({"task": "file it"}))
    assert child.model.config["model_id"] == NOVA
    assert "add_up" in child.tool_names
    assert "hire_clerk" not in child.tool_names, "a clerk cannot hire another clerk"


def test_subcontract_the_paperwork_narrator_has_the_calculator_and_the_clerk_tool(paperwork):
    narrator = paperwork.make_narrator(paperwork.make_clerk_tool())
    assert narrator.tool_names == ["add_up", "hire_clerk"]
    assert narrator.model.config["model_id"] == NOVA
    kw = agent_call_keywords(PAPERWORK)
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA


def test_subcontract_the_paperwork_add_up_sums_in_code(paperwork):
    assert paperwork.add_up(numbers=[4, 3, 2]) == 9
