"""Floor 1 encounter, Read the Receipt: open the result of a turn and read everything on it.

Calling an agent returns an AgentResult, and its metrics carry more than a token count: this
turn's usage on its own, one entry per trip through the event loop, how long each trip took, and
how often each tool ran. The Commentary Booth priced a turn from accumulated_usage; this
encounter goes further, over two turns on the same agent, so you can see which numbers belong to
the turn and which keep adding up for as long as the agent lives.

Run it from this folder, with the workshop environment active:
    python read_the_receipt.py
"""

import random
import time

from strands import Agent, tool


@tool
def roll_d20(dancer: str, move_call: str) -> int:
    """Roll one twenty-sided die for a dancer's Move Call and return the number rolled.

    Call it once per dancer per round, and report the number it returns.

    Args:
        dancer: Who is rolling, for example "Cordula" or "the banker".
        move_call: The Move Call being rolled, for example "Footwork".

    Returns:
        The die, a whole number from 1 to 20.
    """
    return random.randint(1, 20)


@tool
def add_modifier(die: int, modifier: int) -> int:
    """Add a dancer's ability modifier to a die and return the total.

    Call it once per dancer, after rolling. Never add the numbers up yourself.

    Args:
        die: The die rolled for the dancer, 1 to 20.
        modifier: The dancer's ability modifier for this Move Call, for example 1 for Cordula's Footwork.

    Returns:
        The total, die plus modifier.
    """
    return die + modifier


def read_the_receipt(result, seconds: float) -> dict:
    """Everything on the receipt of one turn. `seconds` is the wall clock of the call, measured by the caller."""
    metrics = result.metrics
    turn = metrics.latest_agent_invocation  # the invocation this result belongs to: this turn, and nothing before it
    receipt = {
        "stop_reason": str(result.stop_reason),
        "seconds": round(seconds, 2),
        "context_size": result.context_size,
        "agent_usage_so_far": dict(metrics.accumulated_usage),  # every turn this agent has taken, not just this one
    }
    # TODO: Step 1 - Add "turn_usage": the usage of this turn alone, turn.usage, as a dict
    # TODO: Step 2 - Add "cycles": one {"input": ..., "output": ...} per cycle of this turn, from turn.cycles and the inputTokens and outputTokens of each cycle's usage
    # TODO: Step 3 - Add "tools_so_far": for each name and tool in metrics.tool_metrics, its call_count, error_count and total_time rounded to 3 places
    # TODO: Step 4 - Add "traces": for the last len(turn.cycles) entries of metrics.traces, its name, its duration() in seconds and the (name, duration) of each of its children
    return receipt


def print_receipt(label: str, receipt: dict) -> None:
    """Print one receipt, one field per line."""
    print(f"\n{label}")
    for key, value in receipt.items():
        if key in ("cycles", "traces"):
            print(f"  {key}:")
            for entry in value:
                print(f"    {entry}")
        else:
            print(f"  {key}: {value}")


def make_lady_luck() -> Agent:
    """Lady Luck, the System's croupier: two tools, so a turn has tool calls to count."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        tools=[roll_d20, add_modifier],
        callback_handler=None,
        system_prompt="""You are Lady Luck, the System's croupier subroutine, calling one round of a dance-off.
Roll each dancer's die with roll_d20, one call per dancer, then add the dancer's modifier with add_modifier, one call per dancer.
Report each side as die + modifier = total and name who took the round. Two sentences after the rolls. Plain text only, no emoji.""",
    )


def take_a_turn(agent: Agent, prompt: str) -> dict:
    """Run one turn on the stopwatch and read its receipt."""
    started = time.perf_counter()
    result = agent(prompt)
    return read_the_receipt(result, time.perf_counter() - started)


if __name__ == "__main__":
    lady_luck = make_lady_luck()
    print_receipt("ROUND ONE", take_a_turn(lady_luck, "Footwork, round one: Cordula, modifier +1, against the Bonus-Season Investment Banker, modifier +0."))
    print_receipt("ROUND TWO", take_a_turn(lady_luck, "Presence, round two: Barnaby, modifier +3, against the Bonus-Season Investment Banker, modifier +0."))
