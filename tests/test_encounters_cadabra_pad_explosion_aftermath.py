"""One offline check per step of the Pad Explosion Aftermath side passage (Floor 8).

No test calls a model or AWS. The reporter is a fake function, and the Agent is replaced by a recorder.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NOVA = "us.amazon.nova-2-lite-v1:0"
PAD = "encounters/floor-8-pad-explosion-aftermath/pad_explosion_aftermath.py"


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


@pytest.fixture
def pad():
    return load(PAD, "encounter_pad_explosion_aftermath")


def case_named(pad, name):
    return next(case for case in pad.CASES if case.name == name)


# ---------- Step 1: has_figure ------------------------------------------------


def test_pad_explosion_numbers_in_reads_commas_and_decimals(pad):
    assert pad.numbers_in("farthest 1,200 meters, 8 km, 0.5 s") == [1200.0, 8.0, 0.5]


def test_pad_explosion_has_figure_checks_the_range_with_both_ends_included(pad):
    assert pad.has_figure("windows broke out to 8 km", 7.2, 8.8)
    assert pad.has_figure("44 tons", 44, 44)
    assert not pad.has_figure("windows broke out to 80 km", 7.2, 8.8)
    assert not pad.has_figure("windows broke", 7.2, 8.8), "no number at all is not a figure"


# ---------- Step 2: score_report ----------------------------------------------


def test_pad_explosion_score_report_full_marks_when_hazard_and_figure_are_there(pad):
    result = pad.score_report(case_named(pad, "shockwave"), "Shockwave: windows broke out to 8 km.")
    assert result.score == 1.0 and result.passed


def test_pad_explosion_score_report_gives_half_for_the_hazard_without_the_figure(pad):
    result = pad.score_report(case_named(pad, "debris"), "Debris everywhere, very dramatic.")
    assert result.score == pytest.approx(0.5) and not result.passed
    assert "figure 1" in result.reason


def test_pad_explosion_score_report_zero_for_a_report_about_something_else(pad):
    result = pad.score_report(case_named(pad, "fire-suppression"), "Lovely weather over the Narrows.")
    assert result.score == 0.0 and not result.passed
    assert "not named" in result.reason


def test_pad_explosion_tnt_report_needs_both_ends_of_the_range(pad):
    case = case_named(pad, "tnt-equivalent")
    one_end = pad.score_report(case, "The TNT equivalent was about 44 tons.")
    both = pad.score_report(case, "TNT equivalent: from 44 tons to about 300 tons.")
    assert one_end.score == pytest.approx(2 / 3) and not one_end.passed
    assert both.score == 1.0 and both.passed


# ---------- Step 3: run_experiment --------------------------------------------


def test_pad_explosion_run_experiment_scores_every_case_with_the_prompt_it_was_given(pad):
    seen = []

    def reporter(question, system_prompt):
        seen.append((question, system_prompt))
        return "nothing useful"

    results = pad.run_experiment(pad.CASES, reporter, "PROMPT")
    assert [case for case, _ in results] == pad.CASES
    assert all(isinstance(result, pad.Result) and not result.passed for _, result in results)
    assert seen == [(case.question, "PROMPT") for case in pad.CASES]


# ---------- Step 4: measure_and_adapt -----------------------------------------


def test_pad_explosion_measure_and_adapt_adds_a_correction_for_each_failed_case_and_stops_when_all_pass(pad, capsys):
    prompts = []

    def reporter(question, system_prompt):
        prompts.append(system_prompt)
        case = next(case for case in pad.CASES if case.question == question)
        return pad.CAREFUL[case.name] if pad.correction_for(case) in system_prompt else pad.SLOPPY[case.name]

    final_prompt, results = pad.measure_and_adapt(pad.CASES, reporter, "BASE", rounds=3)
    assert len(prompts) == 2 * len(pad.CASES), "round 1 fails, round 2 passes, no round 3"
    assert prompts[0] == "BASE"
    for case in pad.CASES:
        assert pad.correction_for(case) in final_prompt
    assert all(result.passed for _, result in results)
    assert "Round 2" in capsys.readouterr().out


def test_pad_explosion_measure_and_adapt_only_corrects_the_cases_that_failed(pad):
    good = pad.CAREFUL["shockwave"]

    def reporter(question, system_prompt):
        return good if "shockwave" in question.lower() else "no numbers here"

    final_prompt, _ = pad.measure_and_adapt(pad.CASES, reporter, "BASE", rounds=1)
    assert pad.correction_for(case_named(pad, "shockwave")) not in final_prompt
    assert pad.correction_for(case_named(pad, "debris")) in final_prompt


def test_pad_explosion_measure_and_adapt_gives_up_after_the_last_round(pad):
    calls = []
    pad.measure_and_adapt(pad.CASES, lambda q, p: calls.append(q) or "no numbers", "BASE", rounds=2)
    assert len(calls) == 2 * len(pad.CASES)


# ---------- Step 5: make_reporter ---------------------------------------------


def test_pad_explosion_make_reporter_builds_a_nova_agent_with_the_round_prompt(pad, monkeypatch):
    built = []

    class FakeAgent:
        def __init__(self, **kwargs):
            built.append(kwargs)

        def __call__(self, question):
            return f"answer to: {question}"

    monkeypatch.setattr(pad, "Agent", FakeAgent)
    report = pad.make_reporter()("Report the debris.", "ROUND PROMPT")
    assert report == "answer to: Report the debris."
    assert built[0]["model"] == NOVA
    assert built[0]["system_prompt"] == "ROUND PROMPT"
    assert built[0]["callback_handler"] is None


def test_pad_explosion_names_only_nova_2_lite():
    keywords = agent_call_keywords(PAD)
    assert ast.literal_eval(keywords["model"]) == NOVA
    assert "system_prompt" in keywords and "callback_handler" in keywords


# ---------- the whole drill ---------------------------------------------------


def test_pad_explosion_drill_reporters_fail_round_one_and_pass_after_adapting(pad, capsys):
    _, results = pad.measure_and_adapt(pad.CASES, pad.drill_reporter, pad.BASE_PROMPT)
    assert all(result.passed for _, result in results)
    out = capsys.readouterr().out
    assert "Round 1: mean score 0.54, 0 of 4" in out
    assert "Round 2: mean score 1.00, 4 of 4" in out


def test_pad_explosion_base_prompt_carries_the_pad_sheet_and_the_house_style(pad):
    assert pad.PAD_SHEET in pad.BASE_PROMPT
    assert pad.BASE_PROMPT.rstrip().endswith("Plain text only, no emoji.")
    assert "44 tons" in pad.PAD_SHEET, "the TNT estimates start at about 44 tons"
