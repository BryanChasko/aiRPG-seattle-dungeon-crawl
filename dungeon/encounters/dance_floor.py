"""The dance floor every dance-off encounter shares: one round of a dance-off, rolled and scored in code.

Given code, nothing to complete. It sits in encounters/, one folder above the encounters that use it,
which add that folder to their import path. The rules are the Crawl Handbook's (Dance-Offs, The Final
Beat), and every number is decided here, never by the model: the Floor 3 lesson. Each round lands on
the scoreboard, which the boss battles read to decide what happens next.
"""

import random

from strands import tool

# The party's modifiers for each Move Call, from the cast sheets: (score - 10) / 2, rounded down
MODIFIERS = {
    "Cordula": {"Power": 3, "Footwork": 1, "Endurance": 3, "Choreography": 1, "Read the Room": 2, "Presence": 0},
    "Barnaby": {"Power": 1, "Footwork": 4, "Endurance": 0, "Choreography": 4, "Read the Room": 2, "Presence": 3},
}
TEMPO = {"Steady": 0, "Driving": 2, "Frantic": 4}

scoreboard: list[dict] = []  # every round danced this run, in order


def final_beat(crawler: str) -> tuple[int, int]:
    """Both sides roll 1d20 plus Dexterity until exactly one lands closest to 20 without going over."""
    while True:
        party = random.randint(1, 20) + MODIFIERS[crawler]["Footwork"]
        opponent = random.randint(1, 20)  # opponents dance the Final Beat at +0 Dexterity
        party_in, opponent_in = party <= 20, opponent <= 20
        if party_in != opponent_in or (party_in and party != opponent):
            return party, opponent


@tool
def dance_round(opponent: str, move_call: str, crawler: str = "Cordula", opponent_modifier: int = 0,
                tempo: str = "Steady") -> dict:
    """Dance one round of a dance-off against one opponent, roll both sides and score it.

    Call it once per round. It rolls 1d20 for the Crawler plus their modifier for the Move Call,
    and 1d20 for the opponent plus their modifier and the tempo bonus. A tie goes to the Final
    Beat. Report what it returns; never roll, add or decide anything yourself.

    Args:
        opponent: Who the party dances against, for example "the Quarterly Close Accountant".
        move_call: Power, Footwork, Endurance, Choreography, Read the Room or Presence.
        crawler: Who dances for the party, "Cordula" or "Barnaby". Defaults to "Cordula".
        opponent_modifier: The opponent's own modifier for this Move Call, 0 to 2. Defaults to 0.
        tempo: Steady, Driving or Frantic: the opponent adds +0, +2 or +4. Defaults to Steady.

    Returns:
        Both sides as die + modifier = total, whether the Final Beat was needed, the winner
        ("party" or "opponent"), and the Groove the loser loses, 1 to 6.
    """
    if crawler not in MODIFIERS:
        raise ValueError(f"crawler must be Cordula or Barnaby, not {crawler!r}")
    if move_call not in MODIFIERS[crawler]:
        raise ValueError(f"move_call must be one of {', '.join(MODIFIERS[crawler])}")
    if tempo not in TEMPO or not 0 <= opponent_modifier <= 2:
        raise ValueError("tempo is Steady, Driving or Frantic, and opponent_modifier is 0 to 2")

    party_die, opponent_die = random.randint(1, 20), random.randint(1, 20)
    party_total = party_die + MODIFIERS[crawler][move_call]
    opponent_total = opponent_die + opponent_modifier + TEMPO[tempo]
    final = None
    if party_total == opponent_total:
        final = final_beat(crawler)
        party_wins = final[0] <= 20 and (final[1] > 20 or final[0] > final[1])
    else:
        party_wins = party_total > opponent_total
    groove_lost = min(6, max(1, abs(party_total - opponent_total)))

    result = {
        "opponent": opponent,
        "move_call": move_call,
        "crawler": f"{crawler}: {party_die} + {MODIFIERS[crawler][move_call]} = {party_total}",
        "opponent_roll": f"{opponent}: {opponent_die} + {opponent_modifier + TEMPO[tempo]} = {opponent_total}",
        "final_beat": None if final is None else f"{crawler} {final[0]}, {opponent} {final[1]}",
        "winner": "party" if party_wins else "opponent",
        "groove_lost": groove_lost,
    }
    scoreboard.append(result)
    return result


def party_took_the_last_round() -> bool:
    """True when the party won the round danced most recently."""
    return bool(scoreboard) and scoreboard[-1]["winner"] == "party"
