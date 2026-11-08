"""One offline check per Floor 2 encounter step: each answer is wired the way its page teaches it.

No test calls a model, AWS, NOAA or Docker. The Policy Gatekeeper tests that evaluate the policy need the
``cedarpy`` package (pip install "strands-agents[cedar]") and are skipped when it is missing.
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import sys
import types
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
TIDE = "encounters/floor-2-tide-table/tide_table.py"
POOL = "encounters/floor-2-sandbox-tide-pool/tide_pool.py"
GATE = "encounters/floor-2-policy-gatekeeper/policy_gatekeeper.py"
POLICY = "encounters/floor-2-policy-gatekeeper/gatekeeper.cedar"
ASK = "encounters/floor-2-ask-the-player/ask_the_player.py"


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


# ---------- Floor 2: The Tide Table ------------------------------------------


@pytest.fixture
def tide():
    return load(TIDE, "encounter_tide")


def test_tide_table_url_asks_noaa_for_hilo_predictions_at_the_seattle_gauge(tide):
    url = urlparse(tide.tide_url(date(2026, 1, 1)))
    assert f"{url.scheme}://{url.netloc}{url.path}" == "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    q = {k: v[0] for k, v in parse_qs(url.query).items()}
    assert q["product"] == "predictions"
    assert q["interval"] == "hilo"
    assert q["station"] == "9447130"
    assert (q["begin_date"], q["end_date"]) == ("20260101", "20260101")
    assert (q["datum"], q["units"], q["time_zone"], q["format"]) == ("MLLW", "english", "lst_ldt", "json")
    assert q["application"] == "aiRPG_workshop"


def test_tide_table_agent_carries_http_request_and_the_notebook(tide):
    assert sorted(tide.system.tool_names) == ["http_request", "notebook"]
    kw = agent_call_keywords(TIDE)
    assert names_in(kw["tools"]) == {"http_request", "notebook"}


def test_tide_table_tools_come_from_the_vended_tools_module():
    from strands.vended_tools import http_request, notebook

    mod = load(TIDE, "encounter_tide_imports")
    assert mod.http_request is http_request
    assert mod.notebook is notebook


def test_tide_table_runs_on_nova_2_lite(tide):
    kw = agent_call_keywords(TIDE)
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA
    assert tide.system.model.config["model_id"] == NOVA


def test_tide_table_reads_the_notebook_back_from_agent_state():
    source = (ROOT / TIDE).read_text()
    assert 'system.state.get("notebooks")' in source


def test_tide_table_notebook_tool_keeps_notes_in_agent_state(tide):
    tide.system.state.set("notebooks", {"tide-log": "04:21 H 11.6 ft: floods"})
    assert tide.system.state.get("notebooks") == {"tide-log": "04:21 H 11.6 ft: floods"}


# ---------- Floor 2: The Sandbox Tide Pool -----------------------------------


@pytest.fixture
def pool_mod():
    return load(POOL, "encounter_pool")


def test_sandbox_tide_pool_imports_both_sandbox_classes(pool_mod):
    from strands.sandbox.docker import DockerSandbox
    from strands.sandbox.posix_shell import PosixShellSandbox

    assert pool_mod.DockerSandbox is DockerSandbox
    assert pool_mod.PosixShellSandbox is PosixShellSandbox


def test_sandbox_tide_pool_pool_is_a_docker_sandbox_for_the_container(pool_mod):
    from strands.sandbox.docker import DockerSandbox
    from strands.sandbox.posix_shell import PosixShellSandbox

    assert isinstance(pool_mod.pool, DockerSandbox)
    assert isinstance(pool_mod.pool, PosixShellSandbox)
    assert pool_mod.pool.container == pool_mod.CONTAINER == "tide-pool"
    assert pool_mod.pool.working_dir == "/tmp"
    assert pool_mod.pool._user == "nobody"
    pool_mod.check_pool(pool_mod.pool)
    with pytest.raises(TypeError):
        pool_mod.check_pool(object())


def test_sandbox_tide_pool_pool_runs_commands_with_docker_exec(pool_mod, monkeypatch):
    from strands.sandbox import docker
    from strands.sandbox.types import ExecutionResult

    seen = {}

    async def fake_stream(program, args, **kwargs):
        seen["program"], seen["args"] = program, args
        yield ExecutionResult(exit_code=0, stdout="nobody\n", stderr="")

    monkeypatch.setattr(docker, "_stream_process", fake_stream)
    result = asyncio.run(pool_mod.pool.execute("whoami"))
    assert result.stdout == "nobody\n"
    assert seen["program"] == "docker"
    assert seen["args"] == ["exec", "--user", "nobody", "-w", "/tmp", "--", "tide-pool", "sh", "-c", "whoami"]


def test_sandbox_tide_pool_kiro_gets_the_pool_as_its_sandbox(pool_mod):
    kiro = pool_mod.make_kiro()
    assert kiro.sandbox is pool_mod.pool
    assert {"sandbox_shell", "sandbox_file_editor"} <= set(kiro.tool_names)
    kw = agent_call_keywords(POOL)
    assert names_in(kw["sandbox"]) == {"pool"}
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA
    assert kiro.model.config["model_id"] == NOVA


def test_sandbox_tide_pool_scroll_is_read_back_from_inside_the_pool(pool_mod):
    source = (ROOT / POOL).read_text()
    assert "asyncio.run(pool.read_text(SCROLL))" in source
    assert pool_mod.SCROLL.startswith("/tmp/"), "a path in the container, not on the host"


# ---------- Floor 2: The Policy Gatekeeper -----------------------------------
# The policy file and the way the agent is wired are checked from source, so they run without cedarpy.


def test_policy_gatekeeper_policy_file_permits_file_editor_and_shell_and_forbids_escape():
    policy = (ROOT / POLICY).read_text()
    assert 'permit(principal, action == Action::"file_editor", resource)' in policy
    assert 'permit(principal, action == Action::"shell", resource)' in policy
    assert 'forbid(principal, action == Action::"shell", resource)' in policy
    assert "floor-2-policy-gatekeeper" in policy


def test_policy_gatekeeper_agent_is_gated_by_ledger_then_cedar_then_hitl_on_nova():
    kw = agent_call_keywords(GATE)
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA
    assert [e.id for e in kw["interventions"].elts] == ["ledger", "cedar", "hitl"]
    assert names_in(kw["tools"]) == {"file_editor", "shell"}


def test_policy_gatekeeper_classifier_model_is_nova_2_lite():
    tree = ast.parse((ROOT / GATE).read_text())
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "BedrockModel"]
    assert len(calls) == 1
    assert {kw.arg: kw.value.value for kw in calls[0].keywords} == {"model_id": NOVA}


@pytest.fixture
def gate():
    pytest.importorskip("cedarpy", reason='the Cedar extra is not installed: pip install "strands-agents[cedar]"')
    return load(GATE, "encounter_gate")


class _State:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value


def _call(tool: str, **tool_input):
    return types.SimpleNamespace(
        invocation_state={},
        agent=types.SimpleNamespace(state=_State()),
        tool_use={"name": tool, "toolUseId": "t1", "input": tool_input},
    )


def test_policy_gatekeeper_cedar_is_built_from_the_policy_file(gate):
    from strands.vended_interventions.cedar import CedarAuthorization

    assert isinstance(gate.cedar, CedarAuthorization)
    assert gate.POLICY.name == "gatekeeper.cedar" and gate.POLICY.exists()
    assert gate.cedar._principal == {"type": "User", "id": "kiro"}


def test_policy_gatekeeper_lets_file_editor_work_inside_the_floor_folder(gate):
    from strands.interventions import Proceed

    inside = f"{gate.FLOOR}/scroll.py"
    assert isinstance(gate.cedar.before_tool_call(_call("file_editor", command="create", path=inside)), Proceed)


def test_policy_gatekeeper_denies_file_editor_outside_or_climbing_out(gate):
    from strands.interventions import Deny

    for path in ("/tmp/kiro-escape.py", f"{gate.FLOOR}/../../README.md"):
        verdict = gate.cedar.before_tool_call(_call("file_editor", command="create", path=path))
        assert isinstance(verdict, Deny), path


def test_policy_gatekeeper_lets_shell_run_only_commands_that_name_the_floor_folder(gate):
    from strands.interventions import Deny, Proceed

    assert isinstance(gate.cedar.before_tool_call(_call("shell", command=f"python {gate.FLOOR}/scroll.py")), Proceed)
    assert isinstance(gate.cedar.before_tool_call(_call("shell", command="cat /etc/hosts")), Deny)
    assert isinstance(gate.cedar.before_tool_call(_call("shell", command=f"rm -rf {gate.FLOOR}")), Deny)
    assert isinstance(gate.cedar.before_tool_call(_call("shell", command=f"ls {gate.FLOOR}/..")), Deny)


def test_policy_gatekeeper_denies_a_tool_the_policy_never_mentions(gate):
    from strands.interventions import Deny

    assert isinstance(gate.cedar.before_tool_call(_call("http_request", method="GET", url="https://example.com")), Deny)


def test_policy_gatekeeper_classifier_config_carries_the_risk_rules_and_nova(gate):
    from strands.vended_interventions.hitl import LLMClassifierConfig

    assert isinstance(gate.risk_classifier, LLMClassifierConfig)
    assert gate.risk_classifier.system_prompt == gate.RISK_RULES
    assert gate.risk_classifier.model.config["model_id"] == NOVA


def test_policy_gatekeeper_hitl_classifies_and_asks_on_the_terminal(gate):
    from strands.vended_interventions.hitl import HumanInTheLoop

    assert isinstance(gate.hitl, HumanInTheLoop)
    assert gate.hitl._classifier is not None, "low-risk calls are approved by the classifier"
    assert gate.hitl._ask is not None, "risky calls are put to the human on the terminal"
    assert gate.hitl._allowed_tools == set(), "no tool skips the classifier"


def test_policy_gatekeeper_kiro_has_the_three_handlers_in_order(gate):
    kiro = gate.make_kiro()
    assert [h.name for h in kiro._intervention_registry.handlers] == [
        "gatekeeper-ledger",
        "cedar-authorization",
        "strands:human-in-the-loop",
    ]
    assert kiro.model.config["model_id"] == NOVA


def test_policy_gatekeeper_ledger_writes_down_each_call_and_lets_it_through(gate, capsys):
    from strands.interventions import Proceed

    ledger = gate.GatekeeperLedger()
    assert isinstance(ledger.before_tool_call(_call("shell", command="ls")), Proceed)
    assert isinstance(ledger.before_tool_call(_call("file_editor", command="view", path="/x")), Proceed)
    assert ledger.asked == ["shell", "file_editor"]
    assert "AT THE GATE: shell ls" in capsys.readouterr().out


# ---------- Floor 2: Ask the Player ------------------------------------------


@pytest.fixture
def ask():
    return load(ASK, "encounter_ask")


def test_ask_the_player_narrator_can_hand_off_and_roll(ask):
    from strands.vended_tools import handoff_to_user

    assert ask.handoff_to_user is handoff_to_user
    assert sorted(ask.narrator.tool_names) == ["dance_round", "handoff_to_user"]
    assert ask.narrator.model.config["model_id"] == NOVA
    kw = agent_call_keywords(ASK)
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA


def test_ask_the_player_asking_is_true_only_for_an_interrupt(ask):
    assert ask.asking(types.SimpleNamespace(stop_reason="interrupt")) is True
    assert ask.asking(types.SimpleNamespace(stop_reason="end_turn")) is False


def test_ask_the_player_answer_block_resumes_the_interrupt_it_answers(ask):
    interrupt = types.SimpleNamespace(id="int-123", name="strands:handoff-to-user", reason="Which Move Call?")
    assert ask.answer_block(interrupt, "Footwork") == {
        "interruptResponse": {"interruptId": "int-123", "response": "Footwork"}
    }


def test_ask_the_player_prompt_leaves_the_move_call_to_the_player(ask):
    prompt = ask.narrator.system_prompt
    assert "handoff_to_user" in prompt and "dance_round" in prompt
    for move in ("Power", "Footwork", "Endurance", "Choreography", "Read the Room", "Presence"):
        assert move in prompt
