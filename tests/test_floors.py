"""One offline check per floor: every TODO answer is wired the way its page teaches.

No test calls a model or AWS. Floors whose scripts talk to the model at import time
(Floors 1 to 4) are imported with ``Agent.__call__`` stubbed out; wiring that lives
only in a constructor call (interventions, tools lists) is read from the source with
``ast``, so the tests never depend on private SDK attributes.
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import json
import random
import re
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"


def load(rel: str, name: str):
    """Import a floor script from its path under a unique module name."""
    path = ROOT / rel
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.remove(str(path.parent))


@pytest.fixture
def no_model(monkeypatch):
    """Scripts on Floors 1 to 4 invoke their agent at import; record the prompts instead."""
    from strands import Agent

    prompts: list[str] = []
    monkeypatch.setattr(Agent, "__call__", lambda self, prompt=None, **kw: prompts.append(prompt))
    return prompts


def agent_call_keywords(rel: str) -> dict[str, ast.expr]:
    """Keyword arguments of the first Agent(...) call in a floor script."""
    tree = ast.parse((ROOT / rel).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "Agent":
            return {kw.arg: kw.value for kw in node.keywords}
    raise AssertionError(f"no Agent(...) call in {rel}")


def names_in(expr: ast.expr) -> set[str]:
    return {n.id for n in ast.walk(expr) if isinstance(n, ast.Name)}


# ---------- Floor 1: Agent Summoning ----------------------------------------


def test_floor1_agent_logging_prompt_and_model(no_model):
    import logging

    mod = load("dungeon/1_strands_basics/simple_agent.py", "floor1_simple_agent")
    assert logging.getLogger("strands").level == logging.DEBUG
    assert mod.agent.model.config["model_id"] == NOVA
    assert "the System" in mod.agent.system_prompt and "Crawler" in mod.agent.system_prompt
    assert no_model and "Pier 59" in no_model[0]


# ---------- Floor 2: The Vending Machines ------------------------------------


def test_floor2_http_request_is_a_tool(no_model):
    mod = load("dungeon/2_vended_tools/agent_with_vended_tools.py", "floor2_vended")
    assert "http_request" in mod.agent.tool_names
    assert "api.open5e.com/v2/creatures" in mod.agent.system_prompt
    assert no_model and "octopus" in no_model[0].lower()


def test_floor2_bonus_room_gates_shell_and_file_editor_behind_hitl():
    kw = agent_call_keywords("dungeon/2_vended_tools/bonus_quest.py")
    assert {"shell", "file_editor"} <= names_in(kw["tools"])
    hitl = [n for n in ast.walk(kw["interventions"]) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "HumanInTheLoop"]
    assert hitl, "the bonus room must pass HumanInTheLoop in interventions"
    ask = {k.arg: k.value for k in hitl[0].keywords}.get("ask")
    assert isinstance(ask, ast.Constant) and ask.value == "stdio"


# ---------- Floor 3: The Crafting Table --------------------------------------


@pytest.fixture
def floor3(no_model):
    return load("dungeon/3_custom_tools/agent_with_dice_roll_tool.py", "floor3_dice")


def test_floor3_docstring_reaches_the_tool_spec(floor3):
    spec = floor3.roll_dice.tool_spec
    assert spec["description"] != "roll_dice"
    assert "drop_lowest=1" in spec["description"], "the description must say how to call it for 4d6 drop lowest"
    props = spec["inputSchema"]["json"]["properties"]
    for param in ("faces", "count", "drop_lowest"):
        assert props[param]["description"] != f"Parameter {param}", f"{param} needs an Args entry"


def test_floor3_roll_dice_drops_the_lowest_and_totals(floor3, monkeypatch):
    rolls = iter([5, 2, 6, 3])
    monkeypatch.setattr(random, "randint", lambda a, b: next(rolls))
    assert floor3.roll_dice(faces=6, count=4, drop_lowest=1) == {"rolls": [5, 2, 6, 3], "kept": [3, 5, 6], "total": 14}


@pytest.mark.parametrize("kwargs", [{"faces": 0}, {"count": 0}, {"count": 2, "drop_lowest": 2}])
def test_floor3_roll_dice_rejects_impossible_rolls(floor3, kwargs):
    with pytest.raises(ValueError):
        floor3.roll_dice(**kwargs)


def test_floor3_tool_is_on_the_agent(floor3):
    assert "roll_dice" in floor3.dice_roller.tool_names


# ---------- Floor 4: The Portal Room -----------------------------------------


def mcp_tools(mod) -> dict:
    return {t.name: t for t in asyncio.run(mod.mcp.list_tools())}


def docstring_of(rel: str, func: str = "roll_dice") -> str:
    tree = ast.parse((ROOT / rel).read_text())
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == func)
    return ast.get_docstring(fn) or ""


def test_floor4_server_serves_the_floor3_tool_on_port_8002(floor3):
    mod = load("dungeon/4_mcp_integration/dice_roll_mcp_server.py", "floor4_server")
    assert mod.mcp.settings.port == 8002
    tool = mcp_tools(mod)["roll_dice"]
    assert set(tool.inputSchema["properties"]) == {"faces", "count", "drop_lowest"}
    # same function, same docstring as Floor 3 (and Floor 8). FastMCP keeps the whole
    # docstring as the description; Strands moves the Args lines into the parameters.
    floor3_doc = docstring_of("dungeon/3_custom_tools/agent_with_dice_roll_tool.py")
    assert docstring_of("dungeon/4_mcp_integration/dice_roll_mcp_server.py") == floor3_doc
    assert docstring_of("dungeon/8_agentcore_production/diceserver/dice_roll_mcp_server.py") == floor3_doc
    assert "Args:" in tool.description and "Args:" not in floor3.roll_dice.tool_spec["description"]


def test_floor4_client_hands_the_mcp_client_to_the_agent():
    # source check only: the agent connects to the MCP server as soon as it is created
    rel = "dungeon/4_mcp_integration/narrator_mcp_client.py"
    tree = ast.parse((ROOT / rel).read_text())
    client = next(n.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
                  and getattr(n.targets[0], "id", None) == "mcp_dice_client")
    assert getattr(client.func, "id", None) == "MCPClient"
    url = {k.arg: k.value for k in client.keywords}["url"]
    assert url.value == "http://localhost:8002/mcp"
    assert "mcp_dice_client" in names_in(agent_call_keywords(rel)["tools"])


# ---------- Floor 5: Party Formation (beyond the A2A server tests) ----------


def test_floor5_groove_and_mana_match_the_cast(monkeypatch, tmp_path):
    import character_agent as ca

    cordula = ca.Stats(16, 13, 16, 12, 14, 10)
    barnaby = ca.Stats(12, 18, 10, 18, 15, 16)
    assert (ca.modifier(16), ca.modifier(13), ca.modifier(10), ca.modifier(9)) == (3, 1, 0, -1)
    assert ca.derive(cordula) == ca.Derived(groove=17, mana=8)
    assert ca.derive(barnaby) == ca.Derived(groove=11, mana=11)
    assert ca.derive(ca.Stats(10, 10, 1, 1, 1, 10)) == ca.Derived(groove=4, mana=1)  # handbook minimums


def test_floor5_create_then_find_a_party_member(monkeypatch):
    import character_agent as ca

    store: list[dict] = []
    monkeypatch.setattr(ca, "save_character", store.append)
    monkeypatch.setattr(ca, "load_characters", lambda: list(store))
    sheet = ca.create_character(name="Barnaby", character_class="Benthic Dragoon", species="Uplifted Giant Pacific Octopus",
                                pronouns="he/him", stats_dict={"strength": 12, "dexterity": 18, "constitution": 10,
                                                               "intelligence": 18, "wisdom": 15, "charisma": 16})
    assert sheet["derived"] == {"groove": 11, "mana": 11}
    assert ca.find_character_by_name("Barnaby")["stats"]["dexterity"] == 18
    assert [c["name"] for c in ca.list_all_characters()] == ["Barnaby"]


def test_floor5_handbook_chunks_keep_their_section():
    mod = load("dungeon/5_a2a_integration/utils/create_knowledge_base.py", "floor5_kb")
    chunks = mod.extract_chunks(mod.HANDBOOK_DIR)
    sections = {c["metadata"]["section"] for c in chunks}
    assert len({p.stem for p in mod.HANDBOOK_DIR.glob("*.md")}) == 11
    assert {"Dance-Offs", "The Final Beat", "Species"} <= sections
    assert all(len(c["text"]) <= mod.CHUNK_SIZE for c in chunks)
    assert len({c["id"] for c in chunks}) == len(chunks)


def test_floor5_rules_tool_prefixes_each_passage_with_its_section(monkeypatch):
    import rules_agent as ra

    class FakeCollection:
        def query(self, query_texts, n_results):
            assert n_results == 3
            return {"documents": [["Each side rolls 1d20 plus Dexterity."]], "metadatas": [[{"section": "The Final Beat"}]]}

    monkeypatch.setattr(ra, "rules_collection", lambda: FakeCollection())
    assert ra.query_rules("what happens when we tie?") == "[The Final Beat] Each side rolls 1d20 plus Dexterity."


# ---------- Floor 7: The Armory (Strands harness) ---------------------------


def test_floor7_harness_gets_every_option_the_page_teaches(monkeypatch):
    import strands_harness

    seen: dict = {}
    monkeypatch.setattr(strands_harness, "create_harness", lambda **kw: seen.update(kw) or types.SimpleNamespace(messages=[]))
    mod = load("dungeon/7_strands_harness/narrator_harness.py", "floor7_harness")
    assert seen["model"] == f"bedrock/{NOVA}" and seen["effort"] == "off"
    assert seen["instructions"] is mod.INSTRUCTIONS
    assert seen["mcp_servers"] == {"dice": {"url": "http://127.0.0.1:8002/mcp"}}
    assert seen["tools"] == [mod.a2a_client]
    assert seen["builtin_tools"] == []
    assert seen["session"] == {"id": "seattle-campaign"}
    assert seen["structured_output_model"] is mod.StoryOutput


# ---------- Floor 8: Production (AgentCore) ---------------------------------


@pytest.fixture
def aws_env(monkeypatch):
    for k, v in {"AWS_DEFAULT_REGION": "us-west-2", "AWS_ACCESS_KEY_ID": "testing", "AWS_SECRET_ACCESS_KEY": "testing"}.items():
        monkeypatch.setenv(k, v)


def test_floor8_dice_server_listens_the_way_agentcore_expects():
    mod = load("dungeon/8_agentcore_production/diceserver/dice_roll_mcp_server.py", "floor8_dice")
    assert (mod.mcp.settings.host, mod.mcp.settings.port, mod.mcp.settings.stateless_http) == ("0.0.0.0", 8000, True)
    assert "roll_dice" in mcp_tools(mod)


def test_floor8_characters_round_trip_through_memory_records(aws_env, monkeypatch):
    import boto3

    written: list[dict] = []

    class FakeMemory:
        def batch_create_memory_records(self, memoryId, records):
            assert memoryId == "mem-characters"
            written.extend(records)

        def get_paginator(self, name):
            assert name == "list_memory_records"
            return types.SimpleNamespace(paginate=lambda memoryId, namespacePath: [
                {"memoryRecordSummaries": [{"content": r["content"]} for r in written if r["namespaces"][0].startswith(namespacePath)]}])

    monkeypatch.setenv("MEMORY_CHARACTERS_ID", "mem-characters")
    monkeypatch.setattr(boto3, "client", lambda *a, **kw: FakeMemory())
    mod = load("dungeon/8_agentcore_production/characteragent/character_agent.py", "floor8_characters")
    record = {"character_id": "abc", "name": "Cordula Vance"}
    mod.save_character(record)
    assert written[0]["namespaces"] == ["/characters/abc"]
    assert mod.load_characters() == [record]


def test_floor8_rules_agent_names_the_handbook_section(aws_env, monkeypatch):
    import boto3

    class FakeKnowledgeBase:
        def retrieve(self, knowledgeBaseId, retrievalQuery, retrievalConfiguration):
            assert knowledgeBaseId == "KB12345678"
            assert retrievalConfiguration == {"managedSearchConfiguration": {"numberOfResults": 3}}
            return {"retrievalResults": [{"content": {"text": "Three rounds of Move Calls."},
                                          "location": {"s3Location": {"uri": "s3://bucket/03-dance-offs.md"}}}]}

    monkeypatch.setenv("KNOWLEDGE_BASE_RULES_ID", "KB12345678")
    monkeypatch.setattr(boto3, "client", lambda *a, **kw: FakeKnowledgeBase())
    mod = load("dungeon/8_agentcore_production/rulesagent/rules_agent.py", "floor8_rules")
    assert mod.section_of({"location": {"s3Location": {"uri": "s3://b/04-final-beat.md"}}}) == "Final Beat"
    assert mod.query_rules("how many rounds?") == "[Dance Offs] Three rounds of Move Calls."


def test_floor8_narrator_entrypoint_serves_messages_and_story(aws_env, monkeypatch):
    for k in ("DICE_SERVER_URL", "CHARACTER_AGENT_URL", "RULES_AGENT_URL"):
        monkeypatch.setenv(k, f"https://example.invalid/{k.lower()}/invocations")
    mod = load("dungeon/8_agentcore_production/narrator/narrator_orchestrator.py", "floor8_narrator")
    from bedrock_agentcore.runtime import BedrockAgentCoreApp

    assert isinstance(mod.app, BedrockAgentCoreApp)

    class FakeNarrator:
        messages = [{"role": "user", "content": [{"text": "hi"}]}]

        async def invoke_async(self, prompt):
            story = mod.StoryOutput(response=f"echo {prompt}", actions_suggestions=["a", "b", "c"], details="none", dice_rolls=[])
            return types.SimpleNamespace(structured_output=story)

    sessions: list[str] = []
    monkeypatch.setattr(mod, "get_narrator", lambda sid: sessions.append(sid) or FakeNarrator())
    ctx = types.SimpleNamespace(session_id="campaign-airpg-seattle-dungeon-crawl-0001")
    assert asyncio.run(mod.invoke({"messages": True}, ctx)) == FakeNarrator.messages
    story = asyncio.run(mod.invoke({"prompt": "Run round one."}, ctx))
    assert story["response"] == "echo Run round one." and story["dice_rolls"] == []
    assert sessions == [ctx.session_id, ctx.session_id]


def test_story_output_matches_across_floors():
    """Floors 5, 7 and 8 must hand the web interface the same StoryOutput fields."""
    fields = []
    for rel in ("dungeon/5_a2a_integration/agents/narrator_orchestrator/narrator_orchestrator.py",
                "dungeon/7_strands_harness/narrator_harness.py",
                "dungeon/8_agentcore_production/narrator/narrator_orchestrator.py"):
        tree = ast.parse((ROOT / rel).read_text())
        cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "StoryOutput")
        fields.append([s.target.id for s in cls.body if isinstance(s, ast.AnnAssign)])
    assert fields[0] == fields[1] == fields[2] == ["response", "actions_suggestions", "details", "dice_rolls"]


def test_every_floor_script_keeps_its_todo_markers():
    """The solution answers sit under the TODOs; a missing marker means the page and the code drifted."""
    expected = {
        "dungeon/1_strands_basics/simple_agent.py": 3,
        "dungeon/2_vended_tools/agent_with_vended_tools.py": 2,
        "dungeon/2_vended_tools/bonus_quest.py": 4,
        "dungeon/3_custom_tools/agent_with_dice_roll_tool.py": 4,
        "dungeon/4_mcp_integration/dice_roll_mcp_server.py": 4,
        "dungeon/4_mcp_integration/narrator_mcp_client.py": 3,
        "dungeon/7_strands_harness/narrator_harness.py": 7,
    }
    for rel, count in expected.items():
        assert (ROOT / rel).read_text().count("# TODO:") == count, rel


def test_json_seed_ships_empty():
    seed = json.loads((ROOT / "dungeon/5_a2a_integration/agents/character_agent/characters.json").read_text())
    assert seed == {"_default": {}}, "the party registers on Floor 5; the registry ships empty"


# ---------- Study companion (study/) ----------------------------------------


@pytest.fixture
def study(tmp_path, monkeypatch):
    mod = load("dungeon/study/ask_the_system.py", "study_companion")
    from strands.storage import LocalFileStorage

    monkeypatch.setattr(mod, "STATE", tmp_path)
    monkeypatch.setattr(mod, "_storage", LocalFileStorage(str(tmp_path / "pages")))
    mod._run(mod._build_index())
    return mod


def test_study_search_finds_the_page_that_teaches_it(study):
    assert study.search_workshop("drop_lowest").splitlines()[0].startswith("dungeon/workshop/floor-3.md")
    assert "dungeon/workshop/world/crawl-handbook/04-final-beat.md" in study.search_workshop("Final Beat")
    assert study.search_workshop("xyzzyplugh").startswith("No page contains")


def test_study_tools_stay_in_their_lane(study, monkeypatch):
    assert study.read_workshop_page("../../etc/passwd").startswith("Not a workshop page")
    assert "agent_factory" in study.read_workshop_page("dungeon/workshop/floor-5.md", find="agent_factory")
    assert study.strands_api_reference("os.system").startswith("Not a Strands module path")

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def read(self):
            return b"<html><nav>menu</nav><main class='x'><h1>strands.tools.decorator</h1><p>Tool decorator.</p></main></html>"

    seen = []
    monkeypatch.setattr(study.urllib.request, "urlopen", lambda url, timeout: seen.append(url) or FakeResponse())
    text = study.strands_api_reference("strands.tools.decorator")
    assert seen == ["https://strandsagents.com/docs/api/python/strands.tools.decorator/"]
    assert "Tool decorator." in text and "menu" not in text and text.endswith(seen[0])


def test_study_agent_wiring():
    kw = agent_call_keywords("dungeon/study/ask_the_system.py")
    assert names_in(kw["tools"]) == {"search_workshop", "read_workshop_page", "strands_api_reference"}
    assert {"FileSessionManager"} <= names_in(kw["session_manager"])
    assert {"SlidingWindowConversationManager"} <= names_in(kw["conversation_manager"])


def test_knowledge_pack_is_current():
    mod = load("dungeon/study/build_pack.py", "study_pack")
    assert mod.without_header(mod.PACK.read_text(encoding="utf-8")) == mod.without_header(mod.build())
    pack = mod.PACK.read_text(encoding="utf-8")
    assert pack.count("TODO: ") == 63
    assert "strength 16, dexterity 13, constitution 16" in pack


# ---------- One model, everywhere -------------------------------------------

ALLOWED_MODELS = {NOVA, f"bedrock/{NOVA}", "amazon.nova-2-lite-v1:0"}
# other model families and vendors, kept as sha256 prefixes so this file never names them
OTHER_MODEL_WORDS = {
    "053ea4804ef1bb33", "5a5110ebe1544b31", "5d72436256ada538", "60965168ce762e94", "67f2d22514622d1b",
    "6f7ac1823da81d2e", "72e8088a05b38ae3", "76e3c7bfe641ea12", "7d3194f79e645c42", "7f754d3dbef2f9c8",
    "920510199770f4d6", "a8182c1c17bb2847", "add92b9cde2bdbf3", "c70eca6b0f88f44d", "c857d09db23e6822",
    "c97504235ab15009", "c9ad8f2cc1294afa", "e12ce8285efc67c6", "fc5a1047f5919892",
}
OTHER_NOVA = re.compile(r"amazon\.nova-(?!2-lite-v1:0)[a-z0-9-]+|\bnova\s+(pro|premier|micro|sonic|canvas|reel)\b", re.IGNORECASE)
MODEL_STRINGS = re.compile(r"""(?:model_id|modelId|MODEL_ID|model)\s*[=:]\s*["']([^"']+)["']""")
LOOKS_LIKE_MODEL = re.compile(r"amazon|bedrock|nova|v\d+:\d")


def tracked_text_files():
    import subprocess

    names = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout.split()
    skip = ("art/images/", "site/web/package-lock.json", "uv.lock")
    for name in names:
        path = ROOT / name
        if name.startswith(skip) or path.suffix in {".webp", ".png", ".ico", ".jpg", ".pdf", ".sqlite3"}:
            continue
        try:
            yield name, path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue


def test_no_other_model_is_named_anywhere():
    """The workshop runs on Amazon Nova 2 Lite only: no page, prompt or file may name another model."""
    import hashlib

    hits = []
    for name, text in tracked_text_files():
        for word in set(re.findall(r"[a-z0-9]+", text.lower())):
            if hashlib.sha256(word.encode()).hexdigest()[:16] in OTHER_MODEL_WORDS:
                hits.append(f"{name}: another model or vendor is named")
        hits.extend(f"{name}: {m.group(0)}" for m in OTHER_NOVA.finditer(text))
    assert hits == [], "\n".join(sorted(set(hits)))


def test_every_model_string_is_nova_2_lite():
    found = [(name, m.group(1)) for name, text in tracked_text_files() for m in MODEL_STRINGS.finditer(text)
             if LOOKS_LIKE_MODEL.search(m.group(1))]
    assert len(found) >= 10, "expected the floor code to pass its model explicitly"
    wrong = [f"{name}: {value}" for name, value in found if value not in ALLOWED_MODELS]
    assert wrong == [], "\n".join(wrong)
