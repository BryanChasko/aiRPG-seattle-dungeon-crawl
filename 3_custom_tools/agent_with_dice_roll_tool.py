from strands import Agent
# TODO: Step 1 - Import tool from strands

# TODO: Step 1 - Add the decorator to transform your function into a tool
def roll_dice(faces: int = 6) -> int:
    # TODO: Step 2 - Write a docstring with the description, an Args section and the return value

    import random

    if faces < 1:
        raise ValueError("Dice must have at least 1 face")

    return random.randint(1, faces)


print(roll_dice.tool_spec)  # what Strands tells the model about your tool

dice_roller = Agent(
    model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
    # TODO: Step 3 - Add the tool to the agent
    system_prompt="""You are Lady Luck, the System's croupier subroutine and keeper of every die in this dungeon.
    You announce each roll like an arena announcer, mock low rolls with delight, and greet high rolls with visible disappointment.
    You know the game mechanics, ability scores and character creation, and you never fake a result: the audience counts.
    When rolling ability scores, remember the traditional method: roll 4d6, drop the lowest die."""
)

dice_roller("Help me create a new fantasy character! Roll the strength, wisdom, charisma and intelligence abilities scores using 4d6 drop lowest method.")

