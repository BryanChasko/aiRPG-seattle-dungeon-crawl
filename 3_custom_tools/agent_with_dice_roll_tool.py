from strands import Agent, tool
# TODO: Step 1 - Import tool from strands

# TODO: Step 1 - Add the decorator to transform your function into a tool
@tool
def roll_dice(faces: int = 6, count: int = 1, drop_lowest: int = 0) -> dict:
    # TODO: Step 2 - Write a docstring with the description, an Args section and the return value
    """Roll one or more dice with the same number of faces, optionally drop the lowest, and total the rest.

    Use it every time the game needs a random roll: ability scores, attack rolls,
    saving throws, damage. For "4d6 drop lowest", call it once with faces=6,
    count=4, drop_lowest=1. For a single d20, call it with faces=20.

    Example response: {"rolls": [5, 2, 6, 3], "kept": [5, 6, 3], "total": 14}

    Notes:
        - Report the total this tool returns; never add the dice up yourself.
        - Each die is independent and uniformly random.

    Args:
        faces: Number of faces on each die, 1 or more. Use 20 for a d20, 6 for a d6. Defaults to 6.
        count: How many dice to roll, 1 or more. Defaults to 1.
        drop_lowest: How many of the lowest dice to discard before totaling, 0 or more
            and less than count. Defaults to 0.

    Returns:
        A dict with every die rolled ("rolls"), the dice kept after dropping ("kept"),
        and their sum ("total").
    """

    import random

    if faces < 1:
        raise ValueError("Dice must have at least 1 face")
    if count < 1 or not 0 <= drop_lowest < count:
        raise ValueError("Roll at least one die and keep at least one")

    rolls = [random.randint(1, faces) for _ in range(count)]
    kept = sorted(rolls)[drop_lowest:]
    result = {"rolls": rolls, "kept": kept, "total": sum(kept)}
    return result


print(roll_dice.tool_spec)  # what Strands tells the model about your tool

dice_roller = Agent(
    model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
    # TODO: Step 3 - Add the tool to the agent
    tools=[roll_dice],
    system_prompt="""You are Lady Luck, the System's croupier subroutine and keeper of every die in this dungeon.
    You announce each roll like an arena announcer, mock low rolls with delight, and greet high rolls with visible disappointment.
    You know the game mechanics, ability scores and character creation, and you never fake a result: the audience counts.
    Plain text only, no emoji. Every roll goes through roll_dice, and you report the total it returns.
    When rolling ability scores, remember the traditional method: roll 4d6, drop the lowest die."""
)

dice_roller("Help me create a new fantasy character! Roll the strength, wisdom, charisma and intelligence abilities scores using 4d6 drop lowest method.")

