"""Floor 1 encounter, The Commentary Booth: call a dance-off live, then read what it cost.

A callback handler is any callable that Strands calls with every event of a turn: each chunk of
text as the model writes it, each tool call as it streams in, each finished message, and the final
result. Replace the default handler with your own and you decide what the review board sees.

Run it from this folder, with the workshop environment active:
    python commentary_booth.py
"""

import random

from strands import Agent, tool

# Amazon Nova 2 Lite list prices from the Floor 1 cost table, in dollars per token
PRICE_PER_INPUT_TOKEN = 0.30 / 1_000_000
PRICE_PER_OUTPUT_TOKEN = 2.50 / 1_000_000


@tool
def roll_d20(dancer: str, move_call: str) -> int:
    """Roll one twenty-sided die for a dancer's Move Call and return the number rolled.

    Call it once per dancer per round, and report the number it returns.

    Args:
        dancer: Who is rolling, for example "Cordula" or "the tour guide".
        move_call: The Move Call being rolled, for example "Footwork".

    Returns:
        The die, a whole number from 1 to 20.
    """
    return random.randint(1, 20)


class CommentaryBooth:
    """The System AI's play-by-play desk: Strands calls it with every event of the turn."""

    def __init__(self):
        self.calls_announced = set()  # the toolUseId of every tool call already announced

    def __call__(self, **kwargs):
        # TODO: Step 1 - Print each chunk of text as it arrives: kwargs.get("data"), on the same line, flushed
        # TODO: Step 2 - Announce each tool call once: the first time kwargs.get("current_tool_use") carries a new toolUseId, print "PLAY-BY-PLAY: " and its name on a new line
        data = kwargs.get("data")
        if data:
            print(data, end="", flush=True)
        tool_use = kwargs.get("current_tool_use")
        if tool_use and tool_use.get("toolUseId") and tool_use["toolUseId"] not in self.calls_announced:
            self.calls_announced.add(tool_use["toolUseId"])
            print(f"\nPLAY-BY-PLAY: {tool_use['name']}", flush=True)


def read_the_receipt(result) -> dict:
    """What the turn cost: why it stopped, the tokens it used, and their price."""
    # TODO: Step 4 - Return result.stop_reason, the inputTokens and outputTokens of result.metrics.accumulated_usage, and their cost in dollars at the prices above
    usage = result.metrics.accumulated_usage
    return {
        "stop_reason": result.stop_reason,
        "input_tokens": usage["inputTokens"],
        "output_tokens": usage["outputTokens"],
        "dollars": round(usage["inputTokens"] * PRICE_PER_INPUT_TOKEN + usage["outputTokens"] * PRICE_PER_OUTPUT_TOKEN, 6),
    }


if __name__ == "__main__":
    lady_luck = Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        tools=[roll_d20],
        # TODO: Step 3 - Hand a CommentaryBooth to the agent as its callback_handler
        callback_handler=CommentaryBooth(),
        system_prompt="""You are Lady Luck, the System AI's croupier subroutine, calling a dance-off from the commentary booth
        like a precision timekeeper: every roll announced the instant it lands. Every roll goes through roll_d20, one call
        per dancer, and you report the number it returns. Cordula adds +1 for Dexterity on Footwork; the guide adds +0. The
        higher total wins the round. Nobody is hurt: the loser loses Groove equal to the difference, 1 to 6. Keep it to one
        round, three or four sentences. Plain text only, no emoji.""",
    )
    result = lady_luck("Call one round of a Footwork dance-off between Cordula and the guide of the Rain-Shell Tourist Pod "
                       "at the Pier 59 tide pools. Roll for both dancers.")
    print()
    print("RECEIPT:", read_the_receipt(result))
