"""One offline check per encounter step for the Floor 1 and Floor 3 side passages: Read the Receipt, The Reasoning Dial, The Living Workbench.

No test calls a model or AWS. The scripts run their agents only under ``if __name__ == "__main__":``.
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import shutil
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
RECEIPT = "dungeon/encounters/floor-1-read-the-receipt/read_the_receipt.py"
DIAL = "dungeon/encounters/floor-1-reasoning-dial/reasoning_dial.py"
WORKBENCH = "dungeon/encounters/floor-3-living-workbench/living_workbench.py"
SHELF = "dungeon/encounters/floor-3-living-workbench/shelf/final_beat.py"
REASONING_ON = {"reasoningConfig": {"type": "enabled", "maxReasoningEffort": "low"}}


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


# ---------- Floor 1: Read the Receipt ----------------------------------------


@pytest.fixture
def receipt_mod():
    return load(RECEIPT, "encounter_receipt")


def fake_result(turns: int = 2):
    """A result whose agent has taken `turns` turns of two cycles each, the way the event loop records them."""
    from strands.telemetry.metrics import AgentInvocation, EventLoopCycleMetric, EventLoopMetrics, ToolMetrics, Trace

    metrics = EventLoopMetrics()
    for turn in range(turns):
        cycles = [
            EventLoopCycleMetric(f"t{turn}c0", {"inputTokens": 100, "outputTokens": 20, "totalTokens": 120}),
            EventLoopCycleMetric(f"t{turn}c1", {"inputTokens": 150, "outputTokens": 30, "totalTokens": 180}),
        ]
        metrics.agent_invocations.append(AgentInvocation(cycles=cycles, usage={"inputTokens": 250, "outputTokens": 50, "totalTokens": 300}))
        for index in range(2):
            trace = Trace(f"Cycle {turn * 2 + index + 1}", start_time=0.0)
            model_call = Trace("stream_messages", start_time=0.0)
            model_call.end(0.5)
            trace.add_child(model_call)
            trace.end(2.0)
            metrics.traces.append(trace)
    metrics.accumulated_usage = {"inputTokens": 250 * turns, "outputTokens": 50 * turns, "totalTokens": 300 * turns}
    metrics.tool_metrics = {"roll_d20": ToolMetrics(tool={"name": "roll_d20"}, call_count=2 * turns, success_count=2 * turns, total_time=0.00123456)}
    return types.SimpleNamespace(stop_reason="end_turn", metrics=metrics, context_size=150)


def test_read_the_receipt_turn_usage_is_this_turn_not_the_agents_lifetime(receipt_mod):
    receipt = receipt_mod.read_the_receipt(fake_result(turns=2), 3.14159)
    assert receipt["turn_usage"] == {"inputTokens": 250, "outputTokens": 50, "totalTokens": 300}
    assert receipt["agent_usage_so_far"]["inputTokens"] == 500, "the given field keeps the lifetime total for contrast"
    assert receipt["stop_reason"] == "end_turn"
    assert receipt["seconds"] == 3.14


def test_read_the_receipt_cycles_lists_each_trip_through_the_event_loop(receipt_mod):
    receipt = receipt_mod.read_the_receipt(fake_result(turns=2), 1.0)
    assert receipt["cycles"] == [{"input": 100, "output": 20}, {"input": 150, "output": 30}]


def test_read_the_receipt_tools_reports_calls_errors_and_time(receipt_mod):
    receipt = receipt_mod.read_the_receipt(fake_result(turns=1), 1.0)
    assert receipt["tools_so_far"] == {"roll_d20": {"calls": 2, "errors": 0, "seconds": 0.001}}


def test_read_the_receipt_traces_are_only_the_cycles_of_this_turn(receipt_mod):
    receipt = receipt_mod.read_the_receipt(fake_result(turns=2), 1.0)
    assert [t["name"] for t in receipt["traces"]] == ["Cycle 3", "Cycle 4"], "the last two of four cycle traces"
    assert receipt["traces"][0] == {"name": "Cycle 3", "seconds": 2.0, "steps": [("stream_messages", 0.5)]}


def test_read_the_receipt_agent_has_both_tools_on_nova_2_lite(receipt_mod):
    assert {t.tool_name for t in (receipt_mod.roll_d20, receipt_mod.add_modifier)} == {"roll_d20", "add_modifier"}
    agent = receipt_mod.make_lady_luck()
    assert agent.model.config["model_id"] == NOVA
    assert sorted(agent.tool_names) == ["add_modifier", "roll_d20"]
    assert receipt_mod.add_modifier(die=12, modifier=3) == 15


# ---------- Floor 1: The Reasoning Dial --------------------------------------


@pytest.fixture
def dial_mod():
    return load(DIAL, "encounter_dial")


def test_reasoning_dial_quick_candidate_is_nova_2_lite_with_reasoning_off(dial_mod):
    quick = dial_mod.quick
    assert quick.name == "quick"
    assert quick.model.config["model_id"] == NOVA
    assert "additional_request_fields" not in quick.model.config
    assert quick.description == dial_mod.QUICK_DESCRIPTION


def test_reasoning_dial_deep_candidate_is_the_same_model_with_reasoning_on_and_a_timeout(dial_mod):
    deep, quick = dial_mod.deep, dial_mod.quick
    assert deep.name == "deep"
    assert deep.model.config["model_id"] == NOVA
    assert deep.model.config["additional_request_fields"] == REASONING_ON
    assert deep.model is not quick.model, "the router rejects one model behind two candidates"
    assert deep.model.client.meta.config.read_timeout == dial_mod.DEEP_PATIENCE_SECONDS
    assert deep.description == dial_mod.DEEP_DESCRIPTION


def test_reasoning_dial_classifier_and_fallback_make_the_dial(dial_mod):
    from strands.models.routing.classifier_strategy import ClassifierStrategy
    from strands.models.routing.fallback_strategy import FallbackStrategy

    assert isinstance(dial_mod.dial.classifier, ClassifierStrategy)
    assert isinstance(dial_mod.dial.fallback, FallbackStrategy)
    assert dial_mod.dial.classifier._model.config["model_id"] == NOVA, "the classifier is Nova 2 Lite too"
    assert dial_mod.dial.classifier._system_prompt == dial_mod.DIAL_POLICY
    assert dial_mod.dial.classifier._timeout == 15


def test_reasoning_dial_router_holds_quick_first_and_deep_second(dial_mod):
    from strands.models.routing.router import ModelRouter

    assert isinstance(dial_mod.router, ModelRouter)
    assert [c.name for c in dial_mod.router.candidates] == ["quick", "deep"], "the first candidate is the default when the dial declines"
    assert dial_mod.router._strategy is dial_mod.dial


def test_reasoning_dial_classifier_opens_and_the_fallback_drops_to_reasoning_off(dial_mod):
    from strands.models.routing.fallback_strategy import FallbackStrategy
    from strands.models.routing.strategy import RoutingAttempt, RoutingContext

    class StubClassifier:
        async def select(self, context, **kwargs):
            return context.candidates[1]  # the classifier says: deep

    quick, deep = dial_mod.quick, dial_mod.deep
    strategy = dial_mod.DialStrategy(StubClassifier(), FallbackStrategy())

    def context(attempts=()):
        return RoutingContext(messages=[], system_prompt=None, tool_specs=[], candidates=(quick, deep), invocation_state={}, attempts=tuple(attempts))

    assert asyncio.run(strategy.select(context())) is deep
    assert asyncio.run(strategy.select(context([RoutingAttempt(deep, TimeoutError("read timeout"))]))) is quick
    assert strategy.log == ["deep", "quick"]


def test_reasoning_dial_system_agent_runs_on_the_router(dial_mod):
    system = dial_mod.make_system()
    assert system._model_router is dial_mod.router
    assert sorted(system.tool_names) == ["call_the_drum", "dance_round"]
    kw = agent_call_keywords(DIAL)
    assert names_in(kw["model"]) == {"router"}


def test_reasoning_dial_call_the_drum_scores_the_final_beat_on_the_scoreboard(dial_mod, monkeypatch):
    dial_mod.scoreboard.clear()
    monkeypatch.setattr(dial_mod, "final_beat", lambda crawler: (19, 14))
    won = dial_mod.call_the_drum(opponent="the Bonus-Season Investment Banker", crawler="Cordula")
    assert won["winner"] == "party" and won["final_beat"] == "Cordula 19, the Bonus-Season Investment Banker 14"
    assert dial_mod.party_took_the_last_round()
    monkeypatch.setattr(dial_mod, "final_beat", lambda crawler: (22, 15))
    lost = dial_mod.call_the_drum(opponent="the Bonus-Season Investment Banker")
    assert lost["winner"] == "opponent", "a total over 20 loses"
    assert not dial_mod.party_took_the_last_round()
    dial_mod.scoreboard.clear()
    with pytest.raises(ValueError):
        dial_mod.call_the_drum(opponent="the banker", crawler="Shelly")


# ---------- Floor 3: The Living Workbench ------------------------------------


@pytest.fixture
def workbench_mod():
    return load(WORKBENCH, "encounter_workbench")


@pytest.fixture
def bench(tmp_path, monkeypatch, workbench_mod):
    """A scratch copy of the tools folder, with the working directory set to it the way the script runs."""
    shutil.copytree(ROOT / "dungeon/encounters/floor-3-living-workbench/tools", tmp_path / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(workbench_mod, "TOOLS", tmp_path / "tools")
    return tmp_path / "tools"


def test_living_workbench_agent_watches_the_tools_folder_on_nova_2_lite():
    kw = agent_call_keywords(WORKBENCH)
    assert isinstance(kw["load_tools_from_directory"], ast.Constant) and kw["load_tools_from_directory"].value is True
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA


def test_living_workbench_starts_with_only_the_dice_on_the_bench(workbench_mod, bench):
    agent = workbench_mod.make_workbench()
    assert agent.tool_names == ["roll_d20"]
    assert agent.model.config["model_id"] == NOVA


def test_living_workbench_put_on_the_bench_copies_the_shelf_file(workbench_mod, bench):
    assert not (bench / "final_beat.py").exists()
    workbench_mod.put_on_the_bench()
    assert (bench / "final_beat.py").read_text() == (ROOT / SHELF).read_text()


def test_living_workbench_final_beat_joins_the_running_agent_without_a_restart(workbench_mod, bench):
    agent = workbench_mod.make_workbench()
    before = agent.tool_registry
    workbench_mod.put_on_the_bench()
    agent.tool_registry.reload_tool("final_beat")  # what the watcher calls when it sees the file change
    assert agent.tool_registry is before
    assert sorted(agent.tool_names) == ["final_beat", "roll_d20"]
    assert workbench_mod.wait_for_tool(agent, "final_beat", seconds=1.0)


def test_living_workbench_wait_for_tool_gives_up(workbench_mod):
    bare = types.SimpleNamespace(tool_names=["roll_d20"])
    assert workbench_mod.wait_for_tool(bare, "final_beat", seconds=0.3) is False
    assert workbench_mod.wait_for_tool(bare, "roll_d20", seconds=0.3) is True


def test_living_workbench_final_beat_is_a_decorated_tool():
    shelf = load(SHELF, "encounter_workbench_shelf")
    assert shelf.final_beat.tool_name == "final_beat"
    assert shelf.final_beat.tool_spec["name"] == "final_beat"
    assert "crawler" in shelf.final_beat.tool_spec["inputSchema"]["json"]["properties"]


def test_living_workbench_final_beat_follows_the_handbook_rule(monkeypatch):
    shelf = load(SHELF, "encounter_workbench_shelf_rule")

    def rolls(*dice):
        it = iter(dice)
        monkeypatch.setattr(shelf.random, "randint", lambda a, b: next(it))

    rolls(17, 12)  # Cordula 17 + 1 = 18 against 12
    assert shelf.final_beat(crawler="Cordula") == {"party_total": 18, "opponent_total": 12, "drum_passes": 1, "winner": "party"}
    rolls(18, 15)  # Barnaby 18 + 4 = 22 goes over 20
    assert shelf.final_beat(crawler="Barnaby")["winner"] == "opponent"
    rolls(10, 11, 5, 3)  # 11 against 11: the drum goes again, then 6 against 3
    again = shelf.final_beat(crawler="Cordula")
    assert again["drum_passes"] == 2 and again["winner"] == "party"
    with pytest.raises(ValueError):
        shelf.final_beat(crawler="Shelly")
