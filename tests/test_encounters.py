"""One offline check per encounter step: each answer is wired the way its page teaches it.

No test calls a model or AWS. The encounter scripts run their agents only under
``if __name__ == "__main__":``, so importing them builds the agents and calls nothing.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
BOOTH = "encounters/floor-1-commentary-booth/commentary_booth.py"
SHUFFLE = "encounters/floor-3-concurrent-shuffle/concurrent_shuffle.py"
PAPER = "encounters/floor-5-paper-trail/index_audit_report.py"
FLOOD = "encounters/floor-7-context-flood/context_flood.py"


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


# ---------- Floor 1: The Commentary Booth ------------------------------------


def test_commentary_booth_streams_text_and_announces_each_call_once(capsys):
    mod = load(BOOTH, "encounter_booth")
    booth = mod.CommentaryBooth()
    booth(data="The System ")
    booth(data="is live.")
    for partial in ("", '{"dancer": "Cor', '{"dancer": "Cordula", "move_call": "Footwork"}'):
        booth(current_tool_use={"toolUseId": "call-1", "name": "roll_d20", "input": partial})
    booth(current_tool_use={"toolUseId": "call-2", "name": "roll_d20", "input": ""})
    booth(complete=True)
    out = capsys.readouterr().out
    assert "The System is live." in out, "text chunks must print on one line, in order"
    assert out.count("PLAY-BY-PLAY: roll_d20") == 2, "one announcement per toolUseId, not per streamed event"


def test_commentary_booth_receipt_prices_the_turn():
    mod = load(BOOTH, "encounter_booth_receipt")
    result = types.SimpleNamespace(
        stop_reason="end_turn",
        metrics=types.SimpleNamespace(accumulated_usage={"inputTokens": 1_000_000, "outputTokens": 1_000_000, "totalTokens": 2_000_000}),
    )
    values = list(mod.read_the_receipt(result).values())
    assert "end_turn" in values
    assert values.count(1_000_000) == 2, "the receipt carries the input and the output token counts"
    assert any(isinstance(v, float) and v == pytest.approx(2.80) for v in values), "$0.30 + $2.50 per million tokens"


def test_commentary_booth_is_the_agents_callback_handler():
    kw = agent_call_keywords(BOOTH)
    assert "CommentaryBooth" in names_in(kw["callback_handler"])
    assert isinstance(kw["model"], ast.Constant) and kw["model"].value == NOVA


# ---------- Floor 3: The Concurrent Shuffle ----------------------------------


@pytest.fixture
def shuffle():
    return load(SHUFFLE, "encounter_shuffle")


def test_concurrent_shuffle_bands_differ_only_in_their_executor(shuffle):
    from strands.tools.executors import ConcurrentToolExecutor, SequentialToolExecutor

    assert isinstance(shuffle.sequential_band.tool_executor, SequentialToolExecutor)
    assert isinstance(shuffle.concurrent_band.tool_executor, ConcurrentToolExecutor)
    for band in (shuffle.sequential_band, shuffle.concurrent_band):
        assert band.model.config["model_id"] == NOVA
        assert band.tool_names == ["roll_for"]


def test_concurrent_shuffle_roll_adds_the_modifier_and_logs_the_tumble(shuffle, monkeypatch):
    monkeypatch.setattr(shuffle, "TUMBLE_SECONDS", 0)
    monkeypatch.setattr(shuffle.random, "randint", lambda a, b: 12)
    shuffle.tumbles.clear()
    assert shuffle.roll_for(dancer="Cordula", modifier=1) == {"dancer": "Cordula", "die": 12, "modifier": 1, "total": 13}
    assert [t["dancer"] for t in shuffle.tumbles] == ["Cordula"]


# ---------- Floor 5: The Paper Trail -----------------------------------------


@pytest.fixture
def paper():
    return load(PAPER, "encounter_paper")


def test_paper_trail_reads_both_pages_of_the_audit(paper):
    pages = paper.read_pages(paper.REPORT)
    assert len(pages) == 2
    assert "Finding 1: Groove booked as revenue." in pages[0]
    assert "2019 holiday party" in pages[1]
    assert all(ord(c) < 128 for page in pages for c in page), "the report extracts as plain ascii"


def test_paper_trail_passages_cite_their_page(paper):
    found = paper.passages(paper.read_pages(paper.REPORT))
    assert len(found) == 3, "page 1 cuts into two passages, page 2 into one"
    assert len({p["id"] for p in found}) == len(found), "ids must be unique in the collection"
    assert [p["id"] for p in found] == ["audit-report_p1_0", "audit-report_p1_1", "audit-report_p2_0"]
    assert {p["metadata"]["section"] for p in found} == {"Audit Report, page 1", "Audit Report, page 2"}
    assert all(p["metadata"]["source"] == "audit-report.pdf" for p in found)
    assert all(len(p["text"]) <= paper.CHUNK_SIZE for p in found)


def test_paper_trail_pdf_is_the_one_the_generator_writes():
    gen = load("encounters/floor-5-paper-trail/make_audit_report.py", "encounter_paper_generator")
    assert gen.build() == (ROOT / "encounters/floor-5-paper-trail/audit-report.pdf").read_bytes()


def test_paper_trail_targets_the_rules_agents_collection(paper):
    import rules_agent  # on sys.path through conftest.py

    assert Path(rules_agent.KB_PATH).resolve() == paper.KB_PATH.resolve()
    assert paper.COLLECTION == "crawl_handbook"
    assert (paper.CHUNK_SIZE, paper.CHUNK_OVERLAP) == (1000, 200)


# ---------- Floor 7: The Context Flood ---------------------------------------


@pytest.fixture
def flood():
    return load(FLOOD, "encounter_flood")


def flooded(flood, manager, pin: bool):
    narrator = flood.make_narrator(manager)
    narrator.messages[:] = flood.campaign_log()
    if pin:
        flood.pin_cast_sheets(narrator.messages)
    narrator.conversation_manager.reduce_context(narrator)
    return narrator.messages


def test_context_flood_unpinned_window_drops_the_cast_sheets(flood):
    messages = flooded(flood, flood.sliding_window(), pin=False)
    assert len(messages) == flood.WINDOW
    assert messages[0]["role"] == "user"
    assert all(flood.CAST_SHEETS not in m["content"][0]["text"] for m in messages)


def test_context_flood_pinned_cast_sheets_survive_the_window(flood):
    messages = flooded(flood, flood.sliding_window(), pin=True)
    assert len(messages) == flood.WINDOW + 2
    assert flood.CAST_SHEETS in messages[0]["content"][0]["text"]
    assert [m["role"] for m in messages[:3]] == ["user", "assistant", "user"]
    assert messages[-1]["content"][0]["text"].startswith("Turn 60:")


def test_context_flood_summarizer_folds_80_percent_and_keeps_the_window(flood):
    from strands.agent.conversation_manager import SummarizingConversationManager

    manager = flood.summarizing()
    assert isinstance(manager, SummarizingConversationManager)
    assert manager.summary_ratio == pytest.approx(0.8)
    assert manager.preserve_recent_messages == flood.WINDOW


def test_context_flood_turn_3_is_the_developer_advocate_swarm(flood):
    log = flood.campaign_log()
    assert len(log) == 2 + 2 * 60
    assert "the Developer Advocate Swarm" in log[2 + 2 * 2]["content"][0]["text"]


# ---------- The boss battles and their shared dance floor --------------------

BOSSES = "encounters"


@pytest.fixture
def dance_floor():
    mod = load(f"{BOSSES}/dance_floor.py", "dance_floor")
    mod.scoreboard.clear()
    return mod


def with_dice(monkeypatch, mod, *faces):
    rolls = iter(faces)
    monkeypatch.setattr(mod.random, "randint", lambda a, b: next(rolls))


def test_dance_round_party_wins_with_the_cast_modifier(dance_floor, monkeypatch):
    with_dice(monkeypatch, dance_floor, 15, 10)
    result = dance_floor.dance_round(opponent="the Quarterly Close Accountant", move_call="Footwork")
    assert result["crawler"] == "Cordula: 15 + 1 = 16"
    assert result["opponent_roll"] == "the Quarterly Close Accountant: 10 + 0 = 10"
    assert (result["winner"], result["groove_lost"], result["final_beat"]) == ("party", 6, None)
    assert dance_floor.party_took_the_last_round()


def test_dance_round_tempo_and_opponent_modifier_count(dance_floor, monkeypatch):
    with_dice(monkeypatch, dance_floor, 10, 10)
    result = dance_floor.dance_round(opponent="the Regional Managing Director", move_call="Presence", crawler="Barnaby",
                                     opponent_modifier=2, tempo="Frantic")
    assert result["crawler"] == "Barnaby: 10 + 3 = 13"
    assert result["opponent_roll"] == "the Regional Managing Director: 10 + 6 = 16"
    assert (result["winner"], result["groove_lost"]) == ("opponent", 3)
    assert not dance_floor.party_took_the_last_round()


def test_dance_round_tie_goes_to_the_final_beat_and_rerolls_a_level_drum(dance_floor, monkeypatch):
    # round: 10 + 1 = 11 against 11; Final Beat: 14 against 14 is level, then 20 against 5
    with_dice(monkeypatch, dance_floor, 10, 11, 13, 14, 19, 5)
    result = dance_floor.dance_round(opponent="the Bonus-Season Investment Banker", move_call="Footwork")
    assert result["final_beat"] == "Cordula 20, the Bonus-Season Investment Banker 5"
    assert (result["winner"], result["groove_lost"]) == ("party", 1)


def test_dance_round_final_beat_over_20_loses(dance_floor, monkeypatch):
    # round: 10 + 3 = 13 against 11 + 2 = 13; Barnaby's Final Beat: 18 + 4 = 22 goes over and loses to a 7
    with_dice(monkeypatch, dance_floor, 10, 11, 18, 7)
    result = dance_floor.dance_round(opponent="the Keynote Speaker", move_call="Presence", crawler="Barnaby", opponent_modifier=2, tempo="Steady")
    assert result["final_beat"] == "Barnaby 22, the Keynote Speaker 7"
    assert result["winner"] == "opponent"


@pytest.mark.parametrize("kwargs", [{"move_call": "Breakdance"}, {"move_call": "Power", "crawler": "Shelly"},
                                    {"move_call": "Power", "tempo": "Lazy"}, {"move_call": "Power", "opponent_modifier": 5}])
def test_dance_round_rejects_moves_outside_the_handbook(dance_floor, kwargs):
    with pytest.raises(ValueError):
        dance_floor.dance_round(opponent="the Swag Table", **kwargs)
    assert dance_floor.scoreboard == []


def test_earnings_call_graph_runs_the_agenda_in_order_on_won_rounds(dance_floor):
    mod = load(f"{BOSSES}/floor-8-quarterly-earnings-call/quarterly_earnings_call.py", "encounter_earnings_call")
    graph = mod.build_earnings_call()
    assert set(graph.nodes) == {"accountant", "banker", "rmd"}
    assert {node.node_id for node in graph.entry_points} == {"accountant"}
    assert {(e.from_node.node_id, e.to_node.node_id) for e in graph.edges} == {("accountant", "banker"), ("banker", "rmd")}
    assert all(e.condition is mod.party_won for e in graph.edges)
    for node_id, node in graph.nodes.items():
        assert node.executor.model.config["model_id"] == NOVA
        assert node.executor.tool_names == ["dance_round"]
    mod.scoreboard.append({"winner": "opponent"})
    assert mod.party_won(None) is False
    mod.scoreboard.append({"winner": "party"})
    assert mod.party_won(None) is True
    mod.scoreboard.clear()


def test_advocate_swarm_starts_at_the_keynote_and_is_capped():
    mod = load(f"{BOSSES}/floor-5-developer-advocate-swarm/developer_advocate_swarm.py", "encounter_advocate_swarm")
    swarm = mod.build_swarm()
    assert list(swarm.nodes) == ["keynote", "live_demo", "livestream", "swag_table"]
    assert swarm.entry_point.name == "keynote"
    assert (swarm.max_handoffs, swarm.max_iterations) == (4, 6)
    for node in swarm.nodes.values():
        assert node.executor.model.config["model_id"] == NOVA
        assert "dance_round" in node.executor.tool_names
