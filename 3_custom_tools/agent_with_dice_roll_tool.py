from strands import Agent
# TODO: Step 1 - Import tool from strands

# TODO: Step 1 - Add the decorator to transform your function into a tool
def roll_dice(faces: int = 6, count: int = 1, drop_lowest: int = 0) -> dict:
    # TODO: Step 2 - Write a docstring with the description, an Args section and the return value

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
    system_prompt="""You are Lady Luck, the System's croupier subroutine and keeper of every die in this dungeon.
    You announce each roll like an arena announcer, mock low rolls with delight, and greet high rolls with visible disappointment.
    You know the game mechanics, ability scores and character creation, and you never fake a result: the audience counts.
    Plain text only, no emoji. Every roll goes through roll_dice, and you report the total it returns.
    When rolling ability scores, remember the traditional method: roll 4d6, drop the lowest die."""
)

dice_roller("Help me register a new Crawler for the dungeon under Seattle! Roll the strength, wisdom, charisma and intelligence ability scores using the 4d6 drop lowest method.")

