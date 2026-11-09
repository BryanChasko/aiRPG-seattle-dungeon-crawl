"""One offline check per encounter step for Static Fire on the Pad (Floor 7 side passage, Cadabra obstacle).

No test calls a model or a cloud service. The script runs its agent only under ``if __name__ == "__main__":``;
building an Agent from a model id string makes no network call, and the one test that runs the main block
replaces ``Agent.__call__`` first.
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from strands import Agent, AgentSkills
from strands.hooks import BeforeInvocationEvent, BeforeToolCallEvent
from strands.plugins import Plugin

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
STATIC_FIRE = "dungeon/encounters/floor-7-static-fire/static_fire.py"


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


def model_ids_in(rel: str) -> list[str]:
    """Every model=... and model_id=... string literal in a script."""
    tree = ast.parse((ROOT / rel).read_text())
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg in ("model", "model_id") and isinstance(node.value, ast.Constant):
            found.append(node.value.value)
    return found


def imported_from(rel: str) -> dict[str, set[str]]:
    """Map each ``from X import a, b`` module to the names imported from it."""
    tree = ast.parse((ROOT / rel).read_text())
    found: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            found.setdefault(node.module, set()).update(alias.name for alias in node.names)
    return found


@pytest.fixture
def fire(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-west-2")
    mod = load(STATIC_FIRE, "encounter_static_fire")
    mod.range_log.clear()
    return mod


def tool_event(agent, name: str) -> BeforeToolCallEvent:
    return BeforeToolCallEvent(
        agent=agent, selected_tool=None, tool_use={"name": name, "toolUseId": "t1", "input": {}}, invocation_state={}
    )


# ---------- Static Fire on the Pad ----------------------------------------------


def test_static_fire_step_1_imports_the_plugin_pieces_from_their_modules():
    found = imported_from(STATIC_FIRE)
    assert {"AgentSkills", "tool"} <= found["strands"]
    assert {"Plugin", "hook"} <= found["strands.plugins"]
    assert "BeforeToolCallEvent" in found["strands.hooks"]


def test_static_fire_step_2_range_crew_is_a_plugin_that_brings_two_tools_and_one_hook(fire):
    crew = fire.RangeCrew()
    assert isinstance(crew, Plugin)
    assert crew.name == "range-crew"
    assert [t.tool_name for t in crew.tools] == ["read_countdown", "debris_check"]
    assert [h.__name__ for h in crew.hooks] == ["note_call"]
    assert crew.hooks[0]._hook_event_types == [BeforeToolCallEvent]


def test_static_fire_step_2_countdown_reader_returns_the_pad_clock(fire):
    reading = fire.RangeCrew().read_countdown()
    assert reading == {"t_minus_seconds": 180, "chamber_pressure_pct": 97, "propellant_load_pct": 100}


def test_static_fire_step_2_debris_check_defaults_to_the_exclusion_radius(fire):
    crew = fire.RangeCrew()
    inside = crew.debris_check()
    assert [d["distance_m"] for d in inside] == [400], "only the kayak tour is inside 500 meters"
    assert "kayak" in inside[0]["item"]
    assert [d["distance_m"] for d in crew.debris_check(1000)] == [400, 900]
    assert crew.debris_check(100) == [], "an empty list means the radius is clear"
    assert fire.EXCLUSION_RADIUS_M == 500


def test_static_fire_step_2_note_call_logs_the_tool_name_before_each_tool_runs(fire):
    crew = fire.RangeCrew()
    crew.note_call(SimpleNamespace(tool_use={"name": "debris_check"}))
    crew.note_call(SimpleNamespace(tool_use={"name": "read_countdown"}))
    assert fire.range_log == ["debris_check", "read_countdown"]


def test_static_fire_step_3_skills_plugin_serves_both_skills(fire):
    assert isinstance(fire.skills_plugin, AgentSkills)
    director = fire.make_director(fire.RangeCrew())
    names = [s.name for s in fire.skills_plugin.get_available_skills(director)]
    assert names == ["hold-call", "pad-callout"]
    hold = {s.name: s for s in fire.skills_plugin.get_available_skills(director)}["hold-call"]
    assert "500" in hold.instructions and "HOLD" in hold.instructions, "the hold rules live in the skill"


def test_static_fire_step_4_agent_gets_both_plugins_on_nova_2_lite():
    kwargs = agent_call_keywords(STATIC_FIRE)
    assert names_in(kwargs["plugins"]) == {"crew", "skills_plugin"}
    assert model_ids_in(STATIC_FIRE) == [NOVA]


def test_static_fire_step_4_director_carries_the_crew_tools_the_skills_tool_and_the_hook(fire):
    director = fire.make_director(fire.RangeCrew())
    assert director.model.config["model_id"] == NOVA
    assert director.tool_names == ["read_countdown", "debris_check", "skills"]
    director.hooks.invoke_callbacks(tool_event(director, "read_countdown"))
    assert fire.range_log == ["read_countdown"], "the plugin's hook is registered on the agent"


def test_static_fire_skills_reach_the_system_prompt_as_names_and_descriptions_only(fire):
    director = fire.make_director(fire.RangeCrew())
    assert "hold-call" not in director.system_prompt, "nothing is injected until an invocation starts"
    asyncio.run(director.hooks.invoke_callbacks_async(BeforeInvocationEvent(agent=director)))
    prompt = director.system_prompt
    assert "<name>hold-call</name>" in prompt and "<name>pad-callout</name>" in prompt
    assert "GO or HOLD" in prompt
    assert "exclusion radius of 500 meters" not in prompt, "the full instructions stay out until the skill is activated"


def test_static_fire_activating_a_skill_returns_its_instructions_and_is_remembered(fire):
    director = fire.make_director(fire.RangeCrew())
    result = director.tool.skills(skill_name="hold-call")
    assert result["status"] == "success"
    assert "exclusion radius of 500 meters" in result["content"][0]["text"]
    assert fire.skills_plugin.get_activated_skills(director) == ["hold-call"]


def test_static_fire_main_block_runs_the_call_and_prints_the_logs(monkeypatch, capsys):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-west-2")
    calls = []
    monkeypatch.setattr(Agent, "__call__", lambda self, prompt, **kw: calls.append(prompt) or "T-minus 3:00 HOLD")
    runpy.run_path(str(ROOT / STATIC_FIRE), run_name="__main__")
    out = capsys.readouterr().out
    assert len(calls) == 1 and "45 metric tons" in calls[0]
    assert "Range desk: T-minus 3:00 HOLD" in out
    assert "tools called, in order: []" in out
    assert "skills activated: []" in out
