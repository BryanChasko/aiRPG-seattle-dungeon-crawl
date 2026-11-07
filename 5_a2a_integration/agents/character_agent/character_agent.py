import os
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from strands import Agent, tool
from strands.multiagent.a2a import A2AServer
from strands.hooks import AfterInvocationEvent, HookProvider, HookRegistry
from tinydb import TinyDB

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
class Character:
    character_id: str
    name: str
    character_class: str  # "class" is reserved in Python too
    race: str
    gender: str
    level: int
    experience: int
    stats: Stats
    inventory: list[InventoryItem]
    created_at: str | None = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

# The characters live in a local TinyDB file. The tools only go through save_character
# and load_characters, so changing the storage means changing these two functions.
CHARACTERS_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "characters.json")
characters_db = TinyDB(CHARACTERS_DB, indent=4, separators=(',', ': '))

def save_character(record: dict) -> None:
    characters_db.insert(record)

def load_characters() -> list[dict]:
    return characters_db.all()

@tool
def find_character_by_name(name: str) -> dict:
    """Find a stored character by its exact name.

    Use it when a player refers to an existing character and you need its sheet:
    class, race, level, ability scores, inventory. Names are matched exactly and
    are case-sensitive; use list_all_characters if you are unsure of the spelling.

    Example response:
        {"character_id": "6ca1…", "name": "Thorin", "character_class": "Fighter",
         "race": "Dwarf", "gender": "Male", "level": 1, "experience": 0,
         "stats": {"strength": 16, "dexterity": 12, …}, "inventory": […]}

    Args:
        name: The character's name exactly as it was created, e.g. "Thorin".

    Notes:
        - Fails with an error if no character with that name exists.

    Returns:
        The stored character record as a dict (see the example above).
    """
    print(f"[REGISTRY] Searching for character with name: '{name}'")
    result = [character for character in load_characters() if character["name"] == name]

    if not result:
        # Strands turns the exception into an error result the model can see
        raise ValueError(f"Character with name {name!r} not found")

    character = result[0]
    print(f"[REGISTRY] Found character: {character['name']} (ID: {character['character_id']}, {character['character_class']} {character['race']})")
    return character

@tool
def list_all_characters() -> list[dict]:
    """List every character stored in the database.

    Use it to see which characters exist before creating or looking one up, or
    when a player asks for the whole party.

    Example response:
        [{"character_id": "6ca1…", "name": "Thorin", "character_class": "Fighter",
          "race": "Dwarf", "gender": "Male", "level": 1, "experience": 0,
          "stats": {"strength": 16, …}, "inventory": […]},
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
        print(f"  - {char['name']} ({char['character_class']} {char['race']})")

    return all_chars

@tool
def create_character(
    name: str,
    character_class: str,
    race: str,
    gender: str,
    stats_dict: dict[str, int]
    ) -> dict:
    """Create a new character and save it to the database.

    Use it once per new character, after the ability scores have been decided
    (the System rolls them with roll_dice before it asks). Every new character starts
    at level 1 with 0 experience, a Crawler Starter Kit (shoes not included) and 100 gold pieces.

    Example response:
        {"character_id": "6ca1…", "name": "Thorin", "character_class": "Fighter",
         "race": "Dwarf", "gender": "Male", "level": 1, "experience": 0,
         "stats": {"strength": 16, "dexterity": 12, "constitution": 14,
                   "intelligence": 10, "wisdom": 11, "charisma": 9},
         "inventory": [{"item_name": "Crawler Starter Kit (shoes not included)", "quantity": 1},
                       {"item_name": "Gold Pieces", "quantity": 100}]}

    Notes:
        - Names are not checked for uniqueness: creating "Thorin" twice stores two
          characters. Check with find_character_by_name if in doubt.
        - Any ability score missing from stats_dict defaults to 10.

    Args:
        name: The character's name, e.g. "Thorin".
        character_class: A class such as "Fighter", "Wizard" or "Rogue".
        race: A race such as "Dwarf", "Elf" or "Human".
        gender: The character's gender, e.g. "Female"; pick one if the player did not say.
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
        race=race,
        gender=gender,
        level=1,
        experience=0,
        stats=stats,
        inventory=[
            InventoryItem("Crawler Starter Kit (shoes not included)", 1),
            InventoryItem("Gold Pieces", 100),
        ],
    )
    record = asdict(character)
    save_character(record)
    print(f"[REGISTRY] New Crawler registered: {name} ({character_class} {race}) with id {character_id}")
    return record

class NewlineAfterTurn(HookProvider):
    """Ends every answer with a newline. The streamed text never has one, so without it the
    terminal keeps the last line of each answer in its buffer until the next request."""

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(AfterInvocationEvent, lambda event: print(flush=True))

def create_agent(context_id: str) -> Agent:
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        # TODO: Step 1 - Add the create_character, find_character_by_name and list_all_characters tools to the agent
        # TODO: Step 2 - Add the name "Character Agent" to the agent
        # TODO: Step 3 - Add the description "Crawler registration for the dungeon: creates characters from the ability scores it is given, stores them, finds and lists them." to the agent
        tools=[create_character, find_character_by_name, list_all_characters],
        name="Character Agent",
        description="Crawler registration for the dungeon: creates characters from the ability scores it is given, stores them, finds and lists them.",
        system_prompt="""You are the Character Agent, the System's registration desk for new Crawlers. Use your tools to create, find or list characters.
When creating a character, use exactly the ability scores in the request: the System rolls them before it asks you, and you never invent a score. Leave out any score the request does not give, and create_character sets it to 10. Plain text only, no emoji. If the gender is missing, choose one yourself instead of asking back.
Confirm creations like a clerk stamping a form the Crawler will regret signing, and summarize found characters briefly: class, race, key stats.""",
        hooks=[NewlineAfterTurn()],
    )

# TODO: Step 4 - Create an A2AServer with the create_agent factory on port 8001
a2a_server = A2AServer(agent_factory=create_agent, port=8001)

if __name__ == "__main__":
    # TODO: Step 5 - Start the A2A server
    a2a_server.serve()
