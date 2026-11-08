"""Floor 1 boss battle, The Reasoning Dial: one model, two settings, and a router that turns the knob.

Amazon Nova 2 Lite can answer straight away (reasoning off) or think first (reasoning on). A
ModelRouter holds both settings as candidates and a strategy picks one for each turn: a
classifier reads the request and sends quick banter to reasoning off and a close Final Beat to
reasoning on, and a fallback drops to reasoning off when the deeper turn times out. The
Bonus-Season Investment Banker is the opponent; every roll goes through the shared dance floor.

Run it from this folder, with the workshop environment active:
    python reasoning_dial.py
"""

import sys
import time
from pathlib import Path

from botocore.config import Config
from strands import Agent, tool
from strands.models import BedrockModel
# TODO: Step 1 - Import ModelRouter and RoutingCandidate from strands.models.routing.router, ClassifierStrategy from strands.models.routing.classifier_strategy and FallbackStrategy from strands.models.routing.fallback_strategy

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # the shared dance floor lives in encounters/
from dance_floor import MODIFIERS, dance_round, final_beat, party_took_the_last_round, scoreboard

DEEP_PATIENCE_SECONDS = 30  # how long the deep candidate may stay silent before the turn counts as timed out

QUICK_DESCRIPTION = ("Reasoning off. Answers straight away. For banter, heckles, announcements and plain rounds "
                     "where a tool rolls the dice and the System only reports the numbers.")
DEEP_DESCRIPTION = ("Reasoning on, low effort. Thinks before it answers. For a close call: a tied round or a Final Beat, "
                    "where the whole bout turns on one careful ruling.")
DIAL_POLICY = ("You are the dial on the System's broadcast. Choose the deep candidate only when the latest request is a "
               "close call, a tied round or a Final Beat that decides a bout. Everything else, banter and ordinary rounds, "
               "goes to the quick candidate. Plain text only, no emoji.")


@tool
def call_the_drum(opponent: str, crawler: str = "Cordula") -> dict:
    """Settle a tied round with the Final Beat: the drum speeds up and both sides roll until exactly one lands.

    Call it once when the bout comes down to a Final Beat. The total closest to 20 without going over wins.
    Report what it returns; never roll, add or decide anything yourself.

    Args:
        opponent: Who the party dances against, for example "the Bonus-Season Investment Banker".
        crawler: Who dances for the party, "Cordula" or "Barnaby". Defaults to "Cordula".

    Returns:
        Both Final Beat totals and the winner ("party" or "opponent").
    """
    if crawler not in MODIFIERS:
        raise ValueError(f"crawler must be Cordula or Barnaby, not {crawler!r}")
    party, opponent_total = final_beat(crawler)
    party_wins = party <= 20 and (opponent_total > 20 or party > opponent_total)
    result = {
        "opponent": opponent,
        "move_call": "Final Beat",
        "crawler": f"{crawler}: {party}",
        "opponent_roll": f"{opponent}: {opponent_total}",
        "final_beat": f"{crawler} {party}, {opponent} {opponent_total}",
        "winner": "party" if party_wins else "opponent",
        "groove_lost": 0,
    }
    scoreboard.append(result)
    return result


class DialStrategy:
    """The classifier opens every turn; the fallback takes over when a call fails. It keeps a log of every choice."""

    def __init__(self, classifier, fallback):
        self.classifier = classifier
        self.fallback = fallback
        self.log: list[str] = []  # the candidate named at each ask, in order

    async def select(self, context, **kwargs):
        # The router asks again after a failed call, with the failure in context.attempts
        chosen = await (self.fallback if context.attempts else self.classifier).select(context)
        self.log.append(chosen.name if chosen else "declined, so the first candidate")
        return chosen


# TODO: Step 2 - Build the quick candidate: a RoutingCandidate around a BedrockModel with model_id "us.amazon.nova-2-lite-v1:0" and reasoning off, named "quick", described by QUICK_DESCRIPTION
quick = None

# TODO: Step 3 - Build the deep candidate: the same model with additional_request_fields={"reasoningConfig": {"type": "enabled", "maxReasoningEffort": "low"}} and a boto_client_config of Config(read_timeout=DEEP_PATIENCE_SECONDS, retries={"total_max_attempts": 1, "mode": "standard"}), named "deep", described by DEEP_DESCRIPTION
deep = None

# TODO: Step 4 - Build the dial: a DialStrategy of a ClassifierStrategy and a FallbackStrategy, as dial. The classifier runs on its own BedrockModel with model_id "us.amazon.nova-2-lite-v1:0", system_prompt=DIAL_POLICY and timeout=15
dial = None

# TODO: Step 5 - Build the router: a ModelRouter over quick and deep with dial as its strategy, as router
router = None


def make_system() -> Agent:
    """The System calling the bout. Its model is the router, so every turn picks its own setting."""
    return Agent(
        model=router,
        tools=[dance_round, call_the_drum],
        callback_handler=None,
        system_prompt="""You are the System, the game-show host of Dungeon Crawl: Seattle, calling a dance-off between Cordula and
the Bonus-Season Investment Banker, a person at work in a fleece vest who is very proud of their quarterly synergy. Nobody is hurt.
Every roll goes through a tool: dance_round for a round, call_the_drum for a Final Beat. Report what the tool returned, never
roll or add anything yourself. Keep every answer to two sentences. Plain text only, no emoji.""",
    )


BOUT = [
    ("banter", "The Bonus-Season Investment Banker takes the floor, tugs their fleece vest, and asks Cordula, loudly, "
               "whether she has considered synergy. Heckle the banker back in one line."),
    ("a round", "Footwork round against the Bonus-Season Investment Banker, Steady tempo, opponent_modifier 1. Cordula dances. "
                "Roll it with dance_round and report both totals."),
    ("the Final Beat", "The banker and Cordula finished the last round level. This is a close call: the Final Beat decides the whole "
                       "bout. Call the drum for Cordula against the Bonus-Season Investment Banker, then rule on the winner with care."),
]


if __name__ == "__main__":
    system = make_system()
    for label, request in BOUT:
        dial.log.clear()
        started = time.perf_counter()
        answer = str(system(request)).strip()
        print(f"\n{label.upper()}: the dial chose {' then '.join(dial.log)} ({time.perf_counter() - started:.1f} s)")
        print(f"  {answer}")
    print()
    for round_ in scoreboard:
        print(f"  {round_['move_call']}: {round_['crawler']} against {round_['opponent_roll']} -> {round_['winner']}")
    if not scoreboard or scoreboard[-1]["move_call"] != "Final Beat":
        print("  The drum never sounded: no Final Beat on the scoreboard. Run it again.")
    elif party_took_the_last_round():
        print("  The party took the Final Beat. The banker has gone to restructure.")
    else:
        print("  The banker took the Final Beat and keeps the floor. Run it again.")
