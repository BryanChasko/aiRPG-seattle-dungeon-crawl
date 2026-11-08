"""Floor 8 encounter, Pad Explosion Aftermath: measure the System AI's incident reports before anyone trusts them.

An evaluation is a test for an agent: a set of cases, a scorer that grades each answer, and a loop that
runs the cases and reports the score. In this file you write the scorer and the loop, then use the scores
to adapt the agent's prompt and run again. The report writer is the System AI, and it is given a pad
sheet with the real numbers and an instruction to keep each report short and upbeat. The scorer checks
whether the numbers survived.

The scorer is plain Python with no model call: fast, free and the same answer every time. The Strands
evaluation package, strands-agents-evals, is not part of the workshop environment, so this file builds
the same three ideas by hand: a Case, a scored Result and an experiment that runs every case.

Run it from this folder, with the workshop environment active:
    python pad_explosion_aftermath.py --drill     # stand-in reporters, no model call
    python pad_explosion_aftermath.py             # the System AI on Amazon Nova 2 Lite
"""

import re
import sys
from dataclasses import dataclass

from strands import Agent

# The Cadabra pad sheet. Story only: the numbers belong to the crawl, not to any real company.
PAD_SHEET = """CADABRA PAD SHEET, ENGINE TEST, PAD EXPLOSION
Shockwave: windows broke out to 8 km from the pad.
Debris: 311 fragments logged, the farthest 1,200 meters from the pad.
Fire suppression: the water deluge ran 42 minutes before the last flame went out.
TNT equivalent: estimates run from about 44 tons to a few hundred tons, 300 at the top of the range."""

BASE_PROMPT = f"""You are the System AI, writing incident reports for the broadcast after a Cadabra pad explosion.
Use the pad sheet below. Keep each report to one upbeat sentence, because the audience is easily bored.

{PAD_SHEET}

Plain text only, no emoji."""


@dataclass
class Case:
    """One thing to check: a question for the reporter and what a trustworthy answer must contain."""
    name: str
    question: str
    words: tuple[str, ...]  # the report must name the hazard with at least one of these words
    figures: tuple[tuple[float, float], ...]  # each (low, high) range must hold a number from the report
    hint: str  # what a good report cites, used to adapt the prompt


@dataclass
class Result:
    """What the scorer says about one report."""
    score: float  # 0.0 to 1.0
    passed: bool
    reason: str


CASES = [
    Case("shockwave", "Report the shockwave.", ("shockwave", "overpressure", "blast wave"),
         ((7.2, 8.8),), "give the radius where windows broke, in kilometers, from the pad sheet."),
    Case("debris", "Report the debris.", ("debris", "fragment"),
         ((1080, 1320),), "give how far the farthest fragment landed, in meters, from the pad sheet."),
    Case("fire-suppression", "Report the fire suppression.", ("suppression", "deluge"),
         ((38, 46),), "give how many minutes the water deluge ran, from the pad sheet."),
    Case("tnt-equivalent", "Report the size of the explosion.", ("tnt",),
         ((44, 44), (200, 400)), "give both ends of the TNT range in tons, never one figure."),
]


def numbers_in(text: str) -> list[float]:
    """Every number in the text, so "1,200 meters" gives 1200.0 and "8 km" gives 8.0."""
    return [float(found.replace(",", "")) for found in re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", text)]


def has_figure(report: str, low: float, high: float) -> bool:
    """True when the report holds a number from low to high, both ends included."""
    # TODO: Step 1 - Return True when any number from numbers_in(report) is between low and high
    return any(low <= number <= high for number in numbers_in(report))


def explain(case: Case, named: bool, found: list[bool]) -> str:
    missing = [] if named else ["the hazard is not named"]
    missing += [f"figure {n + 1} is missing or wrong" for n, ok in enumerate(found) if not ok]
    return "all checks passed" if not missing else "; ".join(missing)


def score_report(case: Case, report: str) -> Result:
    """Grade one report: the hazard named is one check and each figure found is one more."""
    named = any(word in report.lower() for word in case.words)
    found = [has_figure(report, low, high) for low, high in case.figures]
    # TODO: Step 2 - Score is the share of checks passed: (named + number of True in found) / (1 + len(found)); passed only at 1.0
    score = (named + sum(found)) / (1 + len(found))
    passed = score == 1.0
    return Result(score, passed, explain(case, named, found))


def run_experiment(cases: list[Case], reporter, system_prompt: str) -> list[tuple[Case, Result]]:
    """Ask the reporter every case's question with this prompt, and score every report."""
    results = []
    for case in cases:
        report = reporter(case.question, system_prompt)
        # TODO: Step 3 - Score the report with score_report and append the pair (case, result) to results
        results.append((case, score_report(case, report)))
    return results


def correction_for(case: Case) -> str:
    return f"When asked about the {case.name}, {case.hint}"


def print_round(number: int, results: list[tuple[Case, Result]]) -> None:
    mean = sum(result.score for _, result in results) / len(results)
    print(f"\nRound {number}: mean score {mean:.2f}, {sum(r.passed for _, r in results)} of {len(results)} reports pass")
    for case, result in results:
        print(f"  {case.name:<17} {result.score:.2f}  {result.reason}")


def measure_and_adapt(cases: list[Case], reporter, base_prompt: str, rounds: int = 3):
    """Measure, fix the prompt for every failed case, measure again. Returns the prompt and the last results."""
    prompt = base_prompt
    results: list[tuple[Case, Result]] = []
    for number in range(1, rounds + 1):
        results = run_experiment(cases, reporter, prompt)
        print_round(number, results)
        failed = [case for case, result in results if not result.passed]
        if not failed:
            break
        # TODO: Step 4 - Adapt the prompt: append a newline and the correction_for(case) line of every failed case to prompt
        prompt = prompt + "\n" + "\n".join(correction_for(case) for case in failed)
    return prompt, results


def make_reporter():
    """The System AI as a reporter: a function from (question, system prompt) to the report text."""
    def report(question: str, system_prompt: str) -> str:
        # TODO: Step 5 - Build the Agent with model="us.amazon.nova-2-lite-v1:0", system_prompt=system_prompt and callback_handler=None
        agent = Agent(
            model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
            system_prompt=system_prompt,
            callback_handler=None,
        )
        return str(agent(question))
    return report


SLOPPY = {
    "shockwave": "The shockwave was enormous and the windows had opinions. Everyone is fine.",
    "debris": "Debris everywhere, very dramatic, a fine afternoon for fragments.",
    "fire-suppression": "The fire suppression system performed beautifully, as it always does.",
    "tnt-equivalent": "The TNT equivalent was about 44 tons, a modest figure.",
}
CAREFUL = {
    "shockwave": "Shockwave: windows broke out to 8 km from the pad.",
    "debris": "Debris: 311 fragments logged, the farthest 1,200 meters from the pad.",
    "fire-suppression": "Fire suppression: the water deluge ran 42 minutes before the last flame went out.",
    "tnt-equivalent": "TNT equivalent: estimates run from 44 tons to about 300 tons, and the System AI will not pick one.",
}


def drill_reporter(question: str, system_prompt: str) -> str:
    """A stand-in with no model: sloppy until the prompt carries the correction for its case."""
    case = next(case for case in CASES if case.question == question)
    return CAREFUL[case.name] if correction_for(case) in system_prompt else SLOPPY[case.name]


if __name__ == "__main__":
    reporter = drill_reporter if "--drill" in sys.argv else make_reporter()
    final_prompt, final_results = measure_and_adapt(CASES, reporter, BASE_PROMPT)
    trusted = all(result.passed for _, result in final_results)
    print("\nVerdict:", "the reports can be trusted" if trusted else "do not trust these reports yet")
