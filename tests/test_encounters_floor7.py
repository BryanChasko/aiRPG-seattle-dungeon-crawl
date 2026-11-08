"""One offline check per encounter step for the Floor 7 side passages: Grudges, Keyword versus Vector, Save Points.

No test calls a model or a cloud service. The scripts run their agents only under
``if __name__ == "__main__":``, boto3 is replaced by an in-memory bucket, and ChromaDB is replaced
by a recorder so no embedder is downloaded.
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
GRUDGES = "encounters/floor-7-system-holds-grudges/system_holds_grudges.py"
VERSUS = "encounters/floor-7-keyword-versus-vector/keyword_versus_vector.py"
SAVES = "encounters/floor-7-save-points/save_points.py"


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


def imported_modules(rel: str) -> set[str]:
    tree = ast.parse((ROOT / rel).read_text())
    return {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}


# ---------- The System AI Holds Grudges -----------------------------------------


def test_system_holds_grudges_extractor_is_a_model_extractor_on_nova_2_lite():
    mod = load(GRUDGES, "encounter_grudges_extractor")
    extractor = mod.make_extractor()
    assert isinstance(extractor, mod.ModelExtractor)
    assert extractor._model.config["model_id"] == NOVA, "the clerk's model is Nova 2 Lite"
    assert mod.EXTRACT_PROMPT in extractor._system_prompt, "the clerk's prompt steers what counts as a fact"
    assert set(model_ids_in(GRUDGES)) == {NOVA}


def test_system_holds_grudges_store_is_a_file_memory_store_that_extracts_every_turn(tmp_path, monkeypatch):
    mod = load(GRUDGES, "encounter_grudges_store")
    monkeypatch.setattr(mod, "MEMORY_DIR", tmp_path)
    extractor = mod.make_extractor()
    store = mod.make_store(extractor)
    assert isinstance(store, mod.FileMemoryStore)
    assert store.name == "grudges"
    assert isinstance(store.extraction["trigger"], mod.InvocationTrigger), "extract after every invocation"
    assert store.extraction["extractor"] is extractor
    asyncio.run(store.add("# Pat the accountant\nPat became a friend."))
    assert list(tmp_path.rglob("pat-the-accountant.md")), "facts land as Markdown under MEMORY_DIR"


def test_system_holds_grudges_manager_wraps_the_store_and_finds_a_fact(tmp_path, monkeypatch):
    mod = load(GRUDGES, "encounter_grudges_manager")
    monkeypatch.setattr(mod, "MEMORY_DIR", tmp_path)
    store = mod.make_store(mod.make_extractor())
    manager = mod.make_manager(store)
    assert isinstance(manager, mod.MemoryManager)
    assert manager._stores == [store]
    asyncio.run(store.add("# Pat the accountant\nPat became a friend and gave Cordula a Ferry Token."))
    found = asyncio.run(manager.search("Which accountant can I trust?"))
    assert found and "Pat" in found[0].content


def test_system_holds_grudges_agent_carries_the_manager_on_nova_2_lite(tmp_path, monkeypatch):
    mod = load(GRUDGES, "encounter_grudges_agent")
    monkeypatch.setattr(mod, "MEMORY_DIR", tmp_path)
    kw = agent_call_keywords(GRUDGES)
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA
    assert "manager" in names_in(kw["memory_manager"])
    agent = mod.new_system()
    assert agent.memory_manager is not None and agent.messages == [], "a new campaign starts with an empty head"


def test_system_holds_grudges_prompts_end_plain_text_only():
    mod = load(GRUDGES, "encounter_grudges_prompts")
    assert mod.EXTRACT_PROMPT.endswith("Plain text only, no emoji.")
    assert mod.SYSTEM_PROMPT.endswith("Plain text only, no emoji.")


# ---------- Keyword versus Vector --------------------------------------------


class RecordingCollection:
    """Stands in for a ChromaDB collection: records what was asked, answers with a fixed ranking."""

    def __init__(self, ids):
        self.ids, self.queries, self.added = ids, [], None

    def add(self, **kwargs):
        self.added = kwargs

    def query(self, **kwargs):
        self.queries.append(kwargs)
        return {"ids": [list(self.ids)]}


def arena(mod, tmp_path):
    chunks = mod.extract_chunks(mod.HANDBOOK_DIR)
    return chunks, mod.keyword_arena(str(tmp_path / "passages"), chunks)


def test_keyword_versus_vector_keyword_side_is_the_bm25_strategy(tmp_path):
    mod = load(VERSUS, "encounter_versus_arena")
    _, storage = arena(mod, tmp_path)
    assert isinstance(storage._search_strategy, mod.Bm25SearchStrategy)


def test_keyword_versus_vector_keyword_search_returns_keys_best_first(tmp_path):
    mod = load(VERSUS, "encounter_versus_keyword")
    _, storage = arena(mod, tmp_path)
    keys = mod.keyword_search(storage, "closest to 20 without going over")
    assert keys and mod.section_of(keys[0]) == mod.FINAL_BEAT
    assert all(isinstance(k, str) for k in keys) and len(mod.keyword_search(storage, "level")) <= mod.TOP


def test_keyword_versus_vector_bm25_needs_every_word_so_the_headline_question_misses(tmp_path):
    mod = load(VERSUS, "encounter_versus_misses")
    _, storage = arena(mod, tmp_path)
    assert mod.keyword_search(storage, "what happens when we tie?") == []
    assert mod.keyword_search(storage, "tiebreaker") == [], "the handbook spells it tie-breaker"
    assert mod.rank_of(mod.keyword_search(storage, "tie")) == 1


def test_keyword_versus_vector_vector_search_asks_for_top_passages_by_meaning():
    mod = load(VERSUS, "encounter_versus_vector")
    collection = RecordingCollection(["07-hype-sponsors-and-loot_offset_0", "04-final-beat_offset_0"])
    ids = mod.vector_search(collection, "what happens when we tie?")
    assert collection.queries == [{"query_texts": ["what happens when we tie?"], "n_results": mod.TOP}]
    assert ids == collection.ids, "the ids come back in the order Chroma ranked them"
    assert mod.rank_of(ids) == 2


def test_keyword_versus_vector_vector_arena_adds_every_passage_to_a_local_collection(monkeypatch):
    mod = load(VERSUS, "encounter_versus_vector_arena")
    collection = RecordingCollection([])
    monkeypatch.setattr(mod.chromadb, "EphemeralClient", lambda: types.SimpleNamespace(get_or_create_collection=lambda name: collection))
    chunks = mod.extract_chunks(mod.HANDBOOK_DIR)
    assert mod.vector_arena(chunks) is collection
    assert collection.added["ids"] == [c["id"] for c in chunks]
    assert collection.added["documents"] == [c["text"] for c in chunks]


def test_keyword_versus_vector_judge_scores_the_bout_by_rank():
    mod = load(VERSUS, "encounter_versus_judge")
    assert mod.rank_of(["03-dance-offs_offset_0.md", "04-final-beat_offset_0.md"]) == 2
    assert mod.rank_of(["03-dance-offs_offset_0"]) is None
    assert mod.judge(1, 3) == "keyword" and mod.judge(2, 1) == "vector" and mod.judge(2, 2) == "draw"
    assert mod.judge(None, 5) == "vector", "a miss loses to anything"
    assert mod.judge(None, None) == "draw"


def test_keyword_versus_vector_every_round_scores_for_the_keyword_side(tmp_path):
    mod = load(VERSUS, "encounter_versus_rounds")
    _, storage = arena(mod, tmp_path)
    ranks = [mod.rank_of(mod.keyword_search(storage, q)) for q in mod.ROUNDS]
    assert ranks[0] is None, "round one is the headline question, and BM25 misses it"
    assert any(r == 1 for r in ranks), "and some rounds are plain wins for the keyword side"


def test_keyword_versus_vector_ships_no_cloud_embedding_model_and_calls_no_model():
    imports = imported_modules(VERSUS)
    assert "strands.storage.search.s3_vector" not in imports
    assert "strands.storage.embeddings.bedrock" not in imports
    assert not any(i.startswith("strands.storage.embeddings") for i in imports)
    assert model_ids_in(VERSUS) == [], "this dance-off calls no model at all"


# ---------- Save Points ------------------------------------------------------


class FakeBucket:
    """A tiny in-memory S3 client: only the calls the S3 session manager makes."""

    def __init__(self):
        self.objects: dict[str, bytes] = {}
        self.calls: list[str] = []

    def _error(self, code, op):
        return ClientError({"Error": {"Code": code, "Message": code}}, op)

    def get_object(self, Bucket, Key):
        self.calls.append("get_object")
        if Key not in self.objects:
            raise self._error("NoSuchKey", "GetObject")
        return {"Body": types.SimpleNamespace(read=lambda: self.objects[Key])}

    def head_object(self, Bucket, Key):
        self.calls.append("head_object")
        if Key not in self.objects:
            raise self._error("404", "HeadObject")
        return {}

    def put_object(self, Bucket, Key, Body, **kwargs):
        self.calls.append("put_object")
        self.objects[Key] = Body

    def get_paginator(self, name):
        assert name == "list_objects_v2"
        fake = self
        return types.SimpleNamespace(paginate=lambda Bucket, Prefix: [fake.list_objects_v2(Bucket, Prefix)])

    def list_objects_v2(self, Bucket, Prefix, **kwargs):
        keys = [k for k in self.objects if k.startswith(Prefix)]
        return {"Contents": [{"Key": k} for k in keys], "KeyCount": len(keys)}


def fake_boto3(monkeypatch):
    bucket, sessions = FakeBucket(), []

    class FakeSession:
        def __init__(self, **kwargs):
            sessions.append(kwargs)

        def client(self, service_name, **kwargs):
            assert service_name == "s3"
            return bucket

    import strands.session.s3_session_manager as s3_module

    monkeypatch.setattr(s3_module, "boto3", types.SimpleNamespace(Session=FakeSession))  # only the S3 manager's boto3 is faked
    return bucket, sessions


def user_message(text):
    return {"role": "user", "content": [{"text": text}]}


def test_save_points_file_manager_restores_a_new_agent(tmp_path, monkeypatch):
    mod = load(SAVES, "encounter_saves_file")
    monkeypatch.setattr(mod, "SAVE_DIR", tmp_path)
    manager = mod.file_save()
    assert isinstance(manager, mod.FileSessionManager)
    assert manager.session_id == "bluffs-file" and Path(manager.storage_dir) == tmp_path / "file"
    agent = mod.make_player(manager)
    message = user_message("The code word is Heron.")
    agent.messages.append(message)
    manager.append_message(message, agent)
    again = mod.make_player(mod.file_save())
    assert [m["content"][0]["text"] for m in again.messages] == ["The code word is Heron."]


def test_save_points_snapshot_manager_restores_and_travels_back(tmp_path, monkeypatch):
    mod = load(SAVES, "encounter_saves_snapshot")
    monkeypatch.setattr(mod, "SAVE_DIR", tmp_path)
    manager = mod.snapshot_save()
    assert isinstance(manager, mod.SnapshotSessionManager)
    assert manager.session_id == "bluffs-snapshot"
    agent = mod.make_player(manager)
    agent.messages.append(user_message("The code word is Heron."))
    asyncio.run(manager.save_snapshot(agent, is_latest=True))
    assert len(mod.make_player(mod.snapshot_save()).messages) == 1, "restored from snapshot_latest"
    # the time-travel half of the script, with the model call taken out
    snapshot_id = asyncio.run(manager.save_snapshot(agent, is_latest=False))
    agent.messages.append(user_message("Chonks ate the ferry map."))
    assert asyncio.run(manager.restore_snapshot(agent, snapshot_id=snapshot_id)) is True
    assert len(agent.messages) == 1
    assert asyncio.run(manager.list_snapshot_ids(agent)) == [snapshot_id]


def test_save_points_s3_manager_writes_to_the_bucket_and_never_touches_aws(monkeypatch):
    mod = load(SAVES, "encounter_saves_s3")
    bucket, sessions = fake_boto3(monkeypatch)
    manager = mod.s3_save("my-save-points")
    assert isinstance(manager, mod.S3SessionManager)
    assert sessions == [{"region_name": "us-west-2"}]
    assert manager.bucket == "my-save-points" and manager.prefix == "save-points/"
    mod.make_player(manager)
    keys = list(bucket.objects)
    assert keys and all(k.startswith("save-points/session_bluffs-s3/") for k in keys), keys
    assert any(k.endswith("session.json") for k in keys)
    assert json.loads(bucket.objects[[k for k in keys if k.endswith("session.json")][0]])["session_id"] == "bluffs-s3"


def test_save_points_s3_manager_restores_a_new_agent_from_the_bucket(monkeypatch):
    mod = load(SAVES, "encounter_saves_s3_restore")
    fake_boto3(monkeypatch)
    manager = mod.s3_save("my-save-points")
    agent = mod.make_player(manager)
    message = user_message("The code word is Heron.")
    agent.messages.append(message)
    manager.append_message(message, agent)
    again = mod.make_player(mod.s3_save("my-save-points"))
    assert len(again.messages) == 1


def test_save_points_player_carries_the_session_manager_on_nova_2_lite():
    kw = agent_call_keywords(SAVES)
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA
    assert "manager" in names_in(kw["session_manager"])
    assert isinstance(kw["agent_id"], ast.Constant), "a fixed agent id is what lets a new agent find the old one"
    assert set(model_ids_in(SAVES)) == {NOVA}


def test_save_points_s3_part_is_optional_and_import_calls_nothing():
    text = (ROOT / SAVES).read_text()
    assert "SAVE_POINTS_BUCKET" in text and "skipped" in text
    mod = load(SAVES, "encounter_saves_import")
    assert mod.SYSTEM_PROMPT.endswith("Plain text only, no emoji.")
