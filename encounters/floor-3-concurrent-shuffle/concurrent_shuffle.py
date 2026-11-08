"""Floor 3 encounter, The Concurrent Shuffle: roll both sides of a round at the same time.

When the model asks for several tool calls in one response, the agent's tool executor decides
how they run. The ConcurrentToolExecutor, the default, runs them side by side; the
SequentialToolExecutor runs them one after the other, in the order the model asked. The dice in
this file take a second to land, so the difference shows on the clock.

Run it from this folder, with the workshop environment active:
    python concurrent_shuffle.py
"""

import random
import threading
import time

from strands import Agent, tool
# TODO: Step 1 - Import ConcurrentToolExecutor and SequentialToolExecutor from strands.tools.executors
from strands.tools.executors import ConcurrentToolExecutor, SequentialToolExecutor

TUMBLE_SECONDS = 1.0  # how long a die takes to land
tumbles: list[dict] = []  # one entry per roll of the current round: who, when the die left the hand, when it landed
_lock = threading.Lock()


@tool
def roll_for(dancer: str, modifier: int = 0) -> dict:
    """Roll 1d20 for one dancer's Move Call and add their ability modifier.

    The die takes about a second to land. When a round needs a roll for both dancers,
    ask for both rolls in the same response, one call per dancer, so they can land together.

    Args:
        dancer: Who is rolling, for example "Cordula" or "the accountant".
        modifier: The dancer's ability modifier for this Move Call, for example 1 for Cordula's Footwork.

    Returns:
        The dancer, the die, the modifier and the total. Report the total; never add it up yourself.
    """
    left = time.perf_counter()
    time.sleep(TUMBLE_SECONDS)
    die = random.randint(1, 20)
    with _lock:
        tumbles.append({"dancer": dancer, "left": left, "landed": time.perf_counter()})
    return {"dancer": dancer, "die": die, "modifier": modifier, "total": die + modifier}


SYSTEM_PROMPT = """You are Lady Luck, the System's croupier subroutine, calling one round of a dance-off.
Roll for both dancers with roll_for, both calls in the same response, then report each side as
die + modifier = total and name who took the round. Two sentences after the rolls. Plain text only, no emoji."""

ROUND = ("Footwork, round one: Cordula, modifier +1, against the Quarterly Close Accountant, modifier +0. "
         "Roll for both dancers at once, then call it.")


def make_band(executor) -> Agent:
    """One Lady Luck: the same model, tool and prompt every time; only the tool executor changes."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        tools=[roll_for],
        system_prompt=SYSTEM_PROMPT,
        tool_executor=executor,
        callback_handler=None,
    )


def dance(band: Agent, label: str) -> None:
    """Run one round and show how the dice moved: the order they landed in, and how long they were in the air."""
    tumbles.clear()
    result = band(ROUND)
    print(f"\n{label}")
    if not tumbles:
        print("  no dice rolled: is roll_for on the agent?")
        return
    first = min(t["left"] for t in tumbles)
    for t in sorted(tumbles, key=lambda t: t["landed"]):
        print(f"  {t['dancer']}: left the hand at {t['left'] - first:4.2f} s, landed at {t['landed'] - first:4.2f} s")
    print(f"  dice in the air: {max(t['landed'] for t in tumbles) - first:4.2f} s")
    print(f"  model responses: {result.metrics.cycle_count} (2 means both rolls came in one response)")
    print(f"  Lady Luck: {str(result).strip()}")


# TODO: Step 2 - Build the sequential band: make_band with a SequentialToolExecutor, as sequential_band
sequential_band = make_band(SequentialToolExecutor())

# TODO: Step 3 - Build the concurrent band: make_band with a ConcurrentToolExecutor, as concurrent_band
concurrent_band = make_band(ConcurrentToolExecutor())

if __name__ == "__main__":
    dance(sequential_band, "SEQUENTIAL: one die at a time, in the order Lady Luck asked")
    dance(concurrent_band, "CONCURRENT: both dice in the air together")
