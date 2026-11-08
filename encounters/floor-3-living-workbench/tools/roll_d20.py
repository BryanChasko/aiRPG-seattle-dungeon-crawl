"""The first tool on the bench: one twenty-sided die. Strands loads every tool file in this folder."""

import random

from strands import tool


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
