import random
import logging
from mcp.server import FastMCP

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# TODO: Step 1 - Create the MCP server as mcp, listening on all interfaces, on the default port, with stateless HTTP

@mcp.tool()
def roll_dice(faces: int = 6, count: int = 1, drop_lowest: int = 0) -> dict:
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
    if faces < 1:
        raise ValueError("Dice must have at least 1 face")
    if count < 1 or not 0 <= drop_lowest < count:
        raise ValueError("Roll at least one die and keep at least one")

    rolls = [random.randint(1, faces) for _ in range(count)]
    kept = sorted(rolls)[drop_lowest:]
    result = {"rolls": rolls, "kept": kept, "total": sum(kept)}

    notation = f"{count}d{faces}" + (f" drop {drop_lowest}" if drop_lowest else "")
    logging.info(f"[SYSTEM] DICE ROLL: {notation} = {rolls} -> {result['total']}")

    return result

if __name__ == "__main__":
    print("Starting Dice Roll MCP Server...")
    mcp.run(transport="streamable-http")
