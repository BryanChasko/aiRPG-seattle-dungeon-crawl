import json
import os
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import boto3
from strands import Agent, tool
from strands.multiagent.a2a import A2AServer, StrandsA2AExecutor
from bedrock_agentcore.runtime import serve_a2a

@dataclass
class Stats:
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

@dataclass
class InventoryItem:
    item_name: str
    quantity: int

@dataclass
class Derived:
    """Computed from the ability scores, never chosen (Crawl Handbook: Groove, Mana, Benched and Cancelled)."""
    groove: int
    mana: int

def modifier(score: int) -> int:
    return (score - 10) // 2

def derive(stats: "Stats", level: int = 1) -> Derived:
    return Derived(
        groove=max(4, 10 + 2 * modifier(stats.constitution) + level),
        mana=max(1, 5 + modifier(stats.intelligence) + modifier(stats.wisdom)),
    )

@dataclass
class Character:
    character_id: str
    name: str
    character_class: str  # "class" is reserved in Python too
    species: str
    pronouns: str
    level: int
    experience: int
    stats: Stats
    derived: Derived
    inventory: list[InventoryItem]
    created_at: str | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

# The characters live in AgentCore Memory: one memory record per character, under /characters/.
# AgentCore sets MEMORY_CHARACTERS_ID for the "characters" memory of the project.
MEMORY_ID = os.environ["MEMORY_CHARACTERS_ID"]
memory = boto3.client("bedrock-agentcore")

def save_character(record: dict) -> None:
    # TODO: Step 1 - Save the record as a memory record in the namespace /characters/<character_id>
    pass

def load_characters() -> list[dict]:
    # TODO: Step 2 - List the memory records under the namespace path /characters/ and decode their JSON content
    pass

@tool
def find_character_by_name(name: str) -> dict:
    """Find a stored character by its exact name.

    Use it when a player refers to an existing character and you need its sheet:
    class, species, pronouns, level, ability scores, Groove, Mana, inventory. Names are matched exactly and
    are case-sensitive; use list_all_characters if you are unsure of the spelling.

    Example response:
        {"character_id": "6ca1…", "name": "Cordula Vance", "character_class": "Amphibious Breacher",
         "species": "Human (Seattle Native)", "pronouns": "she/her", "level": 1, "experience": 0,
         "stats": {"strength": 16, "dexterity": 13, …}, "derived": {"groove": 17, "mana": 8}, "inventory": […]}

    Args:
        name: The character's name exactly as it was created, e.g. "Cordula Vance".

    Notes:
        - Fails with an error if no character with that name exists.
        - A character created a few seconds ago may not be visible yet.

    Returns:
        The stored character record as a dict (see the example above).
    """
    print(f"[REGISTRY] Searching for character with name: '{name}'")
    result = [character for character in load_characters() if character["name"] == name]

    if not result:
        # Strands turns the exception into an error result the model can see
        raise ValueError(f"Character with name {name!r} not found")

    character = result[0]
    print(f"[REGISTRY] Found character: {character['name']} (ID: {character['character_id']}, {character['species']} {character['character_class']})")
    return character

@tool
def list_all_characters() -> list[dict]:
    """List every character stored in the database.

    Use it to see which characters exist before creating or looking one up, or
    when a player asks for the whole party.

    Example response:
        [{"character_id": "6ca1…", "name": "Cordula Vance", "character_class": "Amphibious Breacher",
          "species": "Human (Seattle Native)", "pronouns": "she/her", "level": 1, "experience": 0,
          "stats": {"strength": 16, …}, "derived": {"groove": 17, "mana": 8}, "inventory": […]},
         …]

    Notes:
        - Takes no parameters and returns every character in full; prefer
          find_character_by_name when you already know the name.
        - Returns an empty list if no character has been created yet.

    Returns:
        A list of character records, same shape as find_character_by_name.
    """
    print("[REGISTRY] Listing all characters in database")
    all_chars = load_characters()

    if not all_chars:
        print("[REGISTRY] No characters found in database")
        return []

    print(f"[REGISTRY] Found {len(all_chars)} character(s) in database")
    for char in all_chars:
        print(f"  - {char['name']} ({char['species']} {char['character_class']}, {char['pronouns']})")

    return all_chars

@tool
def create_character(
    name: str,
    character_class: str,
    species: str,
    pronouns: str,
    stats_dict: dict[str, int]
    ) -> dict:
    """Create a new character and save it to the database.

    Use it once per new character, after the ability scores have been decided
    (the System AI passes the scores from the party's cast sheet). Every new character starts
    at level 1 with 0 experience, a Crawler Starter Kit (rain shell not included) and 10 Ferry Tokens.
    Groove and Mana are computed from the ability scores (Crawl Handbook rules).

    Example response:
        {"character_id": "6ca1…", "name": "Cordula Vance", "character_class": "Amphibious Breacher",
         "species": "Human (Seattle Native)", "pronouns": "she/her", "level": 1, "experience": 0,
         "stats": {"strength": 16, "dexterity": 13, "constitution": 16,
                   "intelligence": 12, "wisdom": 14, "charisma": 10},
         "derived": {"groove": 17, "mana": 8},
         "inventory": [{"item_name": "Crawler Starter Kit (rain shell not included)", "quantity": 1},
                       {"item_name": "Ferry Tokens", "quantity": 10}]}

    Notes:
        - Names are not checked for uniqueness: creating "Cordula Vance" twice stores two
          characters. Check with find_character_by_name if in doubt.
        - Any ability score missing from stats_dict defaults to 10.

    Args:
        name: The character's name, e.g. "Cordula Vance".
        character_class: A class from the Crawl Handbook, e.g. "Amphibious Breacher",
            "Benthic Dragoon" or "Grunge Bard".
        species: A species from the Crawl Handbook, e.g. "Human (Seattle Native)",
            "Uplifted Giant Pacific Octopus" or "Harbor Seal".
        pronouns: The character's pronouns, e.g. "she/her", "he/him" or "they/them";
            use "they/them" if the request does not say.
        stats_dict: Ability scores as a dict with the keys strength, dexterity,
            constitution, intelligence, wisdom and charisma, each an integer
            (typically 3 to 18), e.g. {"strength": 16, "dexterity": 12}.

    Returns:
        The newly created character record as a dict, including its generated
        character_id.
    """
    character_id = str(uuid.uuid4())
    stats = Stats(
        strength=stats_dict.get('strength', 10),
        dexterity=stats_dict.get('dexterity', 10),
        constitution=stats_dict.get('constitution', 10),
        intelligence=stats_dict.get('intelligence', 10),
        wisdom=stats_dict.get('wisdom', 10),
        charisma=stats_dict.get('charisma', 10),
    )
    character = Character(
        character_id=character_id,
        name=name,
        character_class=character_class,
        species=species,
        pronouns=pronouns,
        level=1,
        experience=0,
        stats=stats,
        derived=derive(stats),
        inventory=[
            InventoryItem("Crawler Starter Kit (rain shell not included)", 1),
            InventoryItem("Ferry Tokens", 10),
        ],
    )
    record = asdict(character)
    save_character(record)
    print(f"[REGISTRY] New Crawler registered: {name} ({species} {character_class}, {pronouns}) with id {character_id}")
    return record

def create_agent(context_id: str) -> Agent:
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        tools=[create_character, find_character_by_name, list_all_characters],
        name="Character Agent",
        description="Crawler registration for the dungeon: creates characters from the ability scores it is given, stores them, finds and lists them.",
        system_prompt="""You are the Character Agent, the System AI's registration desk for the party. Use your tools to create, find or list characters.
When creating a character, use exactly the ability scores in the request: the request carries the party's cast scores, and you never invent a score. Leave out any score the request does not give, and create_character sets it to 10. Plain text only, no emoji. If the pronouns are missing, use they/them instead of asking back; never guess pronouns from a name.
Confirm creations like a clerk stamping a form the Crawler will regret signing, and summarize found characters briefly: species, class, pronouns, key stats, Groove and Mana.""",
        callback_handler=None,
    )

if __name__ == "__main__":
    # TODO: Step 3 - Serve the create_agent factory with serve_a2a on all interfaces, with the agent card of an A2AServer built on the same factory
    pass
