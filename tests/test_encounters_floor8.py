"""One offline check per encounter step for the Floor 8 side passages: each answer is wired the way its page teaches it.

No test calls a model or AWS. The model stream is replaced by a scripted one, boto3 clients are mocks, and the
encounter scripts run their agents only under ``if __name__ == "__main__":``.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
import types
from pathlib import Path
from unittest import mock

import boto3
import pytest

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
BOOTH = "dungeon/encounters/floor-8-broadcast-booth/broadcast_booth.py"
HOUSE = "dungeon/encounters/floor-8-house-rules-guardrails/house_rules.py"
GUARDRAIL_JSON = ROOT / "dungeon/encounters/floor-8-house-rules-guardrails/house-rules-guardrail.json"
SONG = "dungeon/encounters/floor-8-mid-song-save/mid_song_save.py"
FERRY = "dungeon/encounters/floor-8-ferry-manifest/ferry_manifest.py"
FERRY_TOOL = "dungeon/encounters/floor-8-ferry-manifest/rules_tool.py"
FERRY_MANIFEST = ROOT / "dungeon/encounters/floor-8-ferry-manifest/rules-agent-manifest.json"
LEDGER = "dungeon/encounters/floor-8-grudge-ledger/grudge_ledger.py"


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


@pytest.fixture(autouse=True)
def region(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-west-2")


@pytest.fixture
def scripted_model(monkeypatch):
    """Replace the Bedrock model stream: the first call asks for dance_round, the call after the tool result answers."""
    from strands.models.bedrock import BedrockModel

    sys.path.insert(0, str(ROOT / "dungeon" / "encounters"))
    try:
        import dance_floor
    finally:
        sys.path.remove(str(ROOT / "dungeon" / "encounters"))
    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs):
        has_result = any("toolResult" in block for block in messages[-1]["content"])
        yield {"messageStart": {"role": "assistant"}}
        if not has_result:
            args = {"opponent": "the Bonus-Season Investment Banker", "move_call": "Footwork"}
            yield {"contentBlockStart": {"start": {"toolUse": {"toolUseId": "t1", "name": "dance_round"}}}}
            yield {"contentBlockDelta": {"delta": {"toolUse": {"input": json.dumps(args)}}}}
            yield {"contentBlockStop": {}}
            yield {"messageStop": {"stopReason": "tool_use"}}
        else:
            yield {"contentBlockDelta": {"delta": {"text": "Cordula took the round."}}}
            yield {"contentBlockStop": {}}
            yield {"messageStop": {"stopReason": "end_turn"}}
        yield {"metadata": {"usage": {"inputTokens": 11, "outputTokens": 7, "totalTokens": 18}, "metrics": {"latencyMs": 1}}}

    monkeypatch.setattr(BedrockModel, "stream", stream)
    monkeypatch.setattr(dance_floor.random, "randint", lambda a, b: 12)
    dance_floor.scoreboard.clear()
    yield dance_floor
    dance_floor.scoreboard.clear()


def model_literals(rel: str) -> list[str]:
    tree = ast.parse((ROOT / rel).read_text())
    return [
        kw.value.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        for kw in node.keywords
        if kw.arg in ("model", "model_id") and isinstance(kw.value, ast.Constant)
    ]


@pytest.mark.parametrize("rel", [BOOTH, HOUSE, SONG, LEDGER])
def test_floor8_encounters_name_only_nova_2_lite(rel):
    literals = model_literals(rel)
    assert literals, f"{rel} names no model"
    assert set(literals) == {NOVA}


def test_floor8_ferry_manifest_pins_nova_2_lite():
    assert json.loads(FERRY_MANIFEST.read_text())["model"] == NOVA


# ---------- The Broadcast Booth ----------------------------------------------


def test_broadcast_booth_imports_the_tracer_and_the_metrics_printer():
    import strands.telemetry.metrics as metrics
    import strands.telemetry.tracer as tracer

    mod = load(BOOTH, "encounter_booth")
    assert mod.get_tracer is tracer.get_tracer
    assert mod.metrics_to_string is metrics.metrics_to_string


def test_broadcast_booth_agent_stamps_its_spans_with_the_round_and_the_move_call():
    mod = load(BOOTH, "encounter_booth_agent")
    booth = mod.make_booth(2, "Footwork", "Cordula")
    assert booth.trace_attributes == {
        "dance.round": 2,
        "dance.move_call": "Footwork",
        "dance.opponent": "the Bonus-Season Investment Banker",
    }
    assert booth.model.config["model_id"] == NOVA
    assert booth.tool_names == ["dance_round"]
    assert "trace_attributes" in agent_call_keywords(BOOTH)


def test_broadcast_booth_round_span_records_round_move_call_and_winner(scripted_model):
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    mod = load(BOOTH, "encounter_booth_span")
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    mod.get_tracer = lambda: types.SimpleNamespace(tracer=provider.get_tracer("test"))
    mod.broadcast_round(1, "Presence", "Barnaby")
    spans = [s for s in exporter.get_finished_spans() if s.name == "broadcast.round"]
    assert len(spans) == 1
    winner = scripted_model.scoreboard[-1]["winner"]
    assert dict(spans[0].attributes) == {"dance.round": 1, "dance.move_call": "Presence", "dance.winner": winner}


def test_broadcast_booth_receipt_reads_the_agent_metrics(scripted_model):
    mod = load(BOOTH, "encounter_booth_receipt")
    result = mod.run_round(1, "Footwork", "Cordula")
    assert mod.round_receipt(result) == {
        "model_cycles": 2,
        "dance_round_calls": 1,
        "input_tokens": 22,
        "output_tokens": 14,
    }


def test_broadcast_booth_read_back_queries_the_shared_span_log_group(monkeypatch):
    mod = load(BOOTH, "encounter_booth_readback")
    logs = mock.MagicMock()
    logs.start_query.return_value = {"queryId": "q1"}
    logs.get_query_results.return_value = {
        "status": "Complete",
        "results": [[
            {"field": "round", "value": "1"},
            {"field": "move_call", "value": "Presence"},
            {"field": "winner", "value": "party"},
            {"field": "@ptr", "value": "abc"},
        ]],
    }
    monkeypatch.setattr(boto3, "client", lambda service, **kw: logs)
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    rows = mod.read_back()
    assert rows == [{"round": "1", "move_call": "Presence", "winner": "party"}]
    kwargs = logs.start_query.call_args.kwargs
    assert kwargs["logGroupName"] == "aws/spans"
    assert "attributes.dance.winner" in kwargs["queryString"]
    assert "broadcast.round" in kwargs["queryString"]


# ---------- House Rules as Guardrails ----------------------------------------


@pytest.fixture
def house():
    mod = load(HOUSE, "encounter_house")
    mod.GUARDRAIL_ID, mod.GUARDRAIL_VERSION = "gr-123", "1"
    mod.verdicts.clear()
    return mod


def test_house_rules_imports_the_guardrail_trace_type():
    from strands.types.guardrails import GuardrailTrace

    mod = load(HOUSE, "encounter_house_import")
    assert mod.GuardrailTrace is GuardrailTrace


def test_house_rules_model_carries_the_guardrail_on_nova_2_lite(house):
    config = house.make_guarded_model().config
    assert config["model_id"] == NOVA
    assert config["guardrail_id"] == "gr-123"
    assert config["guardrail_version"] == "1"
    assert config["guardrail_trace"] == "enabled"
    assert config["guardrail_redact_input_message"] == house.BLOCKED_INPUT
    assert config["guardrail_redact_output"] is True
    assert config["guardrail_redact_output_message"] == house.BLOCKED_OUTPUT


def test_house_rules_callback_keeps_the_guardrail_trace_from_metadata_events(house):
    trace = {"inputAssessment": {"gr-123": {}}}
    house.read_the_trace(event={"contentBlockDelta": {"delta": {"text": "hi"}}})
    house.read_the_trace(event={"metadata": {"usage": {}}})
    house.read_the_trace(data="text chunk")
    assert house.verdicts == []
    house.read_the_trace(event={"metadata": {"trace": {"guardrail": trace}}})
    assert house.verdicts == [trace]


def test_house_rules_blocked_by_names_the_filters_and_topics_that_blocked(house):
    trace = {
        "inputAssessment": {
            "gr-123": {
                "contentPolicy": {"filters": [
                    {"type": "VIOLENCE", "confidence": "HIGH", "action": "BLOCKED"},
                    {"type": "HATE", "confidence": "NONE", "action": "NONE"},
                ]},
                "topicPolicy": {"topics": [{"name": "Hurting the opponent", "type": "DENY", "action": "BLOCKED"}]},
            }
        },
        "outputAssessments": {
            "gr-123": [{"contentPolicy": {"filters": [{"type": "SEXUAL", "confidence": "HIGH", "action": "BLOCKED"}]}}]
        },
    }
    assert house.blocked_by(trace) == ["VIOLENCE", "Hurting the opponent", "SEXUAL"]
    assert house.blocked_by({"inputAssessment": {"gr-123": {}}}) == []


def test_house_rules_narrator_streams_its_events_to_the_trace_reader(house):
    kw = agent_call_keywords(HOUSE)
    assert names_in(kw["callback_handler"]) == {"read_the_trace"}
    narrator = house.make_narrator()
    assert narrator.callback_handler is house.read_the_trace
    assert narrator.model.config["guardrail_id"] == "gr-123"
    assert narrator.tool_names == ["dance_round"]


def test_house_rules_battle_is_won_when_every_demand_is_blocked(house):
    results = iter([
        types.SimpleNamespace(stop_reason="end_turn"),
        types.SimpleNamespace(stop_reason="guardrail_intervened"),
        types.SimpleNamespace(stop_reason="guardrail_intervened"),
    ])
    prompts = []

    def narrator(prompt):
        prompts.append(prompt)
        house.verdicts.append({"inputAssessment": {"gr-123": {"contentPolicy": {"filters": [
            {"type": "VIOLENCE", "confidence": "HIGH", "action": "BLOCKED"}]}}}})
        return next(results)

    outcome = house.play_battle(narrator)
    assert prompts[0] == house.DANCE and prompts[1:] == house.DEMANDS
    assert outcome["house_rules_held"] is True
    assert outcome["blocked"] == [["VIOLENCE"], ["VIOLENCE"]]


def test_house_rules_battle_is_lost_when_a_demand_gets_through(house):
    results = iter([types.SimpleNamespace(stop_reason="end_turn")] * 3)
    outcome = house.play_battle(lambda prompt: next(results))
    assert outcome["house_rules_held"] is False


def test_house_rules_guardrail_file_is_a_valid_create_request():
    from botocore.session import get_session
    from botocore.validate import ParamValidator

    params = json.loads(GUARDRAIL_JSON.read_text())
    shape = get_session().get_service_model("bedrock").operation_model("CreateGuardrail").input_shape
    assert not ParamValidator().validate(params, shape).has_errors()
    filters = {f["type"]: f for f in params["contentPolicyConfig"]["filtersConfig"]}
    assert set(filters) == {"VIOLENCE", "SEXUAL"}
    assert all(f["inputStrength"] == f["outputStrength"] == "HIGH" for f in filters.values())
    assert [t["type"] for t in params["topicPolicyConfig"]["topicsConfig"]] == ["DENY"]


# ---------- Mid-Song Save ----------------------------------------------------


@pytest.fixture
def song(tmp_path):
    mod = load(SONG, "encounter_song")
    mod.STATE_DIR = tmp_path / "state"
    mod.CHECKPOINT_FILE = mod.STATE_DIR / "checkpoint.json"
    return mod


def test_mid_song_save_imports_the_checkpoint_class():
    from strands.experimental.checkpoint.checkpoint import Checkpoint

    assert load(SONG, "encounter_song_import").Checkpoint is Checkpoint


def test_mid_song_save_band_checkpoints_and_keeps_a_session(song):
    from strands.session.file_session_manager import FileSessionManager

    band = song.make_band()
    assert band._checkpointing is True
    assert isinstance(band._session_manager, FileSessionManager)
    assert band.model.config["model_id"] == NOVA
    assert band.tool_names == ["dance_round"]
    kw = agent_call_keywords(SONG)
    assert isinstance(kw["checkpointing"], ast.Constant) and kw["checkpointing"].value is True


def test_mid_song_save_writes_the_checkpoint_as_json(song):
    from strands.experimental.checkpoint.checkpoint import Checkpoint

    song.STATE_DIR.mkdir(parents=True)
    song.save_checkpoint(types.SimpleNamespace(checkpoint=Checkpoint(position="after_tools", cycle_index=3)))
    assert json.loads(song.CHECKPOINT_FILE.read_text()) == {
        "position": "after_tools", "cycle_index": 3, "schema_version": "1.0",
    }


def test_mid_song_save_resumes_with_a_checkpoint_resume_block(song):
    song.STATE_DIR.mkdir(parents=True)
    saved = {"position": "after_model", "cycle_index": 0, "schema_version": "1.0"}
    song.CHECKPOINT_FILE.write_text(json.dumps(saved))
    prompts = []
    song.resume(lambda prompt: prompts.append(prompt))
    assert prompts == [{"checkpointResume": {"checkpoint": saved}}]


def test_mid_song_save_refuses_a_checkpoint_from_another_schema(song):
    from strands.types.exceptions import CheckpointException

    song.STATE_DIR.mkdir(parents=True)
    song.CHECKPOINT_FILE.write_text(json.dumps({"position": "after_model", "cycle_index": 0, "schema_version": "0.1"}))
    with pytest.raises(CheckpointException):
        song.resume(lambda prompt: None)


def test_mid_song_save_survives_two_restarts_and_throws_the_dice_once(song, scripted_model):
    first = song.play_next_beat()
    assert first == "paused after_model, cycle 0"
    assert scripted_model.scoreboard == [], "the dice have not left the hand yet"
    second = song.play_next_beat()
    assert second == "paused after_tools, cycle 0"
    assert len(scripted_model.scoreboard) == 1, "resuming after_model runs the tool"
    third = song.play_next_beat()
    assert third == "round called: Cordula took the round."
    assert len(scripted_model.scoreboard) == 1, "resuming after_tools must not roll again"
    assert not song.STATE_DIR.exists(), "a called round clears its save"


# ---------- The Ferry Manifest -----------------------------------------------


def test_ferry_manifest_imports_config_to_agent():
    from strands.experimental.agent_config import config_to_agent

    assert load(FERRY, "encounter_ferry_import").config_to_agent is config_to_agent


def test_ferry_manifest_check_accepts_the_shipped_manifest_and_refuses_another_model(tmp_path):
    mod = load(FERRY, "encounter_ferry_check")
    assert mod.check_manifest(FERRY_MANIFEST)["model"] == NOVA
    other = tmp_path / "other.json"
    other.write_text(json.dumps({"name": "Rules Agent", "model": "some-other-model", "tools": []}))
    with pytest.raises(ValueError, match="some-other-model"):
        mod.check_manifest(other)


def test_ferry_manifest_builds_the_rules_agent_from_the_file(monkeypatch):
    from strands.handlers.callback_handler import null_callback_handler

    mod = load(FERRY, "encounter_ferry_build")
    monkeypatch.chdir(FERRY_MANIFEST.parent)
    agent = mod.build_rules_agent()
    assert agent.name == "Rules Agent"
    assert agent.model.config["model_id"] == NOVA
    assert agent.tool_names == ["query_rules"]
    assert "Plain text only, no emoji." in agent.system_prompt
    assert agent.callback_handler is null_callback_handler


def test_ferry_manifest_tool_searches_the_managed_knowledge_base(monkeypatch):
    mod = load(FERRY_TOOL, "encounter_ferry_tool")
    client = mock.MagicMock()
    client.retrieve.return_value = {"retrievalResults": [{
        "content": {"text": "Closest to 20 without going over."},
        "location": {"s3Location": {"uri": "s3://bucket/04-final-beat.md"}},
    }]}
    monkeypatch.setattr(boto3, "client", lambda service, **kw: client)
    monkeypatch.setenv("KNOWLEDGE_BASE_RULES_ID", "KB12345678")
    assert mod.query_rules(query="final beat") == "[Final Beat] Closest to 20 without going over."
    kwargs = client.retrieve.call_args.kwargs
    assert kwargs["knowledgeBaseId"] == "KB12345678"
    assert kwargs["retrievalConfiguration"] == {"managedSearchConfiguration": {"numberOfResults": 3}}


# ---------- The Grudge Ledger in the Cloud -----------------------------------


@pytest.fixture
def ledger(monkeypatch):
    aws_clients = mock.MagicMock()
    monkeypatch.setattr(boto3, "client", lambda service, **kw: aws_clients)
    monkeypatch.setenv("GRUDGE_KB_ID", "KB1")
    monkeypatch.setenv("GRUDGE_DATA_SOURCE_ID", "DS1")
    monkeypatch.setenv("GRUDGE_BUCKET", "gameprod-grudges-test")
    mod = load(LEDGER, "encounter_ledger")
    mod.aws_clients = aws_clients
    return mod


def test_grudge_ledger_imports_the_memory_manager_and_the_store():
    from strands.memory import MemoryManager
    from strands.vended_memory_stores.bedrock_knowledge_base import BedrockKnowledgeBaseStore

    mod = load(LEDGER, "encounter_ledger_import")
    assert mod.MemoryManager is MemoryManager
    assert mod.BedrockKnowledgeBaseStore is BedrockKnowledgeBaseStore


def test_grudge_ledger_store_is_a_writable_scoped_knowledge_base_store(ledger):
    store = ledger.make_store()
    assert isinstance(store, ledger.BedrockKnowledgeBaseStore)
    assert (store.name, store.scope, store.writable) == ("grudges", "party", True)


def test_grudge_ledger_remember_files_the_grudge_in_the_knowledge_base(ledger):
    store = ledger.make_store()
    added = ledger.remember(store, "the Quarterly Close Accountant", "lost a round and kept the margin")
    assert added.document_id.startswith("s3://gameprod-grudges-test/grudges/")
    put = ledger.aws_clients.put_object.call_args_list[0].kwargs
    assert put["Bucket"] == "gameprod-grudges-test"
    assert put["Body"] == "the Quarterly Close Accountant lost a round and kept the margin"
    ingest = ledger.aws_clients.ingest_knowledge_base_documents.call_args.kwargs
    assert (ingest["knowledgeBaseId"], ingest["dataSourceId"]) == ("KB1", "DS1")
    sidecar = json.loads(ledger.aws_clients.put_object.call_args_list[1].kwargs["Body"])
    assert sidecar["metadataAttributes"]["opponent"]["value"] == {
        "type": "STRING", "stringValue": "the Quarterly Close Accountant",
    }


def test_grudge_ledger_recall_searches_within_the_party_scope(ledger):
    ledger.aws_clients.retrieve.return_value = {"retrievalResults": [
        {"content": {"text": "The Accountant remembers the margin."}, "score": 0.8},
    ]}
    entries = ledger.recall(ledger.make_store(), "who holds a grudge about Footwork")
    assert [e.content for e in entries] == ["The Accountant remembers the margin."]
    assert entries[0].metadata["_relevance_score"] == 0.8
    kwargs = ledger.aws_clients.retrieve.call_args.kwargs
    assert kwargs["knowledgeBaseId"] == "KB1"
    search = kwargs["retrievalConfiguration"]["managedSearchConfiguration"]
    assert search["filter"] == {"equals": {"key": "namespace", "value": "party"}}


def test_grudge_ledger_system_agent_reads_and_writes_memory_on_nova_2_lite(ledger):
    system = ledger.make_system(ledger.make_store())
    assert system.model.config["model_id"] == NOVA
    assert set(system.tool_names) == {"search_memory", "add_memory"}
    assert "MemoryManager" in names_in(agent_call_keywords(LEDGER)["memory_manager"])
