"""The tool on the shelf: the Final Beat, waiting to be put on the bench.

This file sits outside the tools folder, so the agent cannot see it yet. The script copies it in while
the agent is running; the tool watcher notices and registers it.
"""

import random

# TODO: Step 2 - Import tool from strands.tools.decorator
from strands.tools.decorator import tool

FOOTWORK = {"Cordula": 1, "Barnaby": 4}  # the party's Dexterity modifiers


# TODO: Step 3 - Mark final_beat as a tool with the @tool decorator
@tool
def final_beat(crawler: str = "Cordula") -> dict:
    """Settle a tied round with the Final Beat: both sides roll until exactly one lands closest to 20 without going over.

    Call it once when a round ends level. The party rolls 1d20 plus Footwork, the opponent rolls 1d20 at +0.
    A total over 20 loses; if both go over, or both land on the same total, the drum goes again.
    Report what it returns; never roll, add or decide anything yourself.

    Args:
        crawler: Who dances for the party, "Cordula" or "Barnaby". Defaults to "Cordula".

    Returns:
        The final totals of both sides, how many times the drum sounded, and the winner ("party" or "opponent").
    """
    if crawler not in FOOTWORK:
        raise ValueError(f"crawler must be Cordula or Barnaby, not {crawler!r}")
    passes = 0
    while True:
        passes += 1
        party = random.randint(1, 20) + FOOTWORK[crawler]
        opponent = random.randint(1, 20)
        party_in, opponent_in = party <= 20, opponent <= 20
        if party_in != opponent_in or (party_in and party != opponent):
            winner = "party" if party_in and (not opponent_in or party > opponent) else "opponent"
            return {"party_total": party, "opponent_total": opponent, "drum_passes": passes, "winner": winner}
