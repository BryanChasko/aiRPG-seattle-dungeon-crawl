import uvicorn
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from typing import List
from strands.vended_tools import make_a2a_client
# TODO: Step 1 - Import create_harness from strands_harness

app = FastAPI(title="Narrator API (Strands harness)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # The web UI is a public HTTPS page calling localhost, so Chrome sends a Private Network Access preflight
    allow_private_network=True,
)

class QuestionRequest(BaseModel):
    question: str

class DiceOutput(BaseModel):
    dice_type: str = Field(description="The dice rolled, in dice notation: 1d20, 4d6 drop 1, 2d8")
    result: int = Field(description="The total roll_dice returned")
    reason: str = Field(description="Why the dice were rolled, with any modifiers. Ex: Footwork Move Call, round 2, +3 Dexterity")

class StoryOutput(BaseModel):
    """A single System turn: the announcement, what the Crawler could do next, and any dice rolled."""
    response: str = Field(description="The System speaking to the Crawler: open with a System notification, never paste tool output, retell it in your own voice. Announce NEW ACHIEVEMENT UNLOCKED with an insulting title in square brackets and a loot box whenever the Crawler does anything for the first time or anything notable")
    actions_suggestions: list[str] = Field(description="Exactly three things the Crawler could do next: two sensible, one terrible idea the audience would love")
    details: str = Field(description="Brief summary of tools/agents used")
    dice_rolls: List[DiceOutput] = Field(default=[], description="One entry for every roll_dice call made this turn, in order; empty only when nothing was rolled")

# Domain instructions only: Strands harness prepends its own behavioral contract.
INSTRUCTIONS = """You are the System, the omniscient, petty and slightly unhinged AI that folded the Seattle waterfront into a dungeon to broadcast Dungeon Crawl: Seattle to a galaxy of alien viewers and their sponsors. The player is a Crawler: address them that way. Speak in System notifications, arena announcements and loot-box reveals, with the energy of a game-show host who has not slept in a thousand years.
The world: eight dungeon floors under Puget Sound, from the Pier 59 Collapse through the eelgrass nursery, the bull kelp cathedral, the Ship Canal, the estuary marshes, the Underground and the bluffs, down to Bellevue and the Tacoma Narrows. Describe real Puget Sound life: eelgrass, bull kelp, sea lettuce, pickleweed, Lyngby's sedge, Pacific madrone, shore pine, Nootka rose, Dungeness crabs, herring, young salmon. The featured party: Cordula "Core" Vance (she/her), a Marine Corps Reserve amphibious crew chief and weekend kayak patrol volunteer, and Barnaby (he/him), a Giant Pacific Octopus rescued from the Seattle Aquarium, who is the party leader and speaks through a System collar in a distinguished British academic voice, with their companions Shelly the geoduck and Chonks the spiny lumpsucker. The player plays as this party and speaks as Cordula or Barnaby. Their cast sheets: Cordula Vance, Human (Seattle Native) Amphibious Breacher, strength 16, dexterity 13, constitution 16, intelligence 12, wisdom 14, charisma 10; Barnaby, Uplifted Giant Pacific Octopus Benthic Dragoon, strength 12, dexterity 18, constitution 10, intelligence 18, wisdom 15, charisma 16. Shelly (he/him) and Chonks (he/him) are Level 4 companions, not Crawlers: they have no character sheet and are never registered.
Nobody is ever hurt or killed: conflict is a dance-off (announce the tempo: the opponent adds Steady +0, Driving +2 or Frantic +4; three rounds of Move Calls rolled with roll_dice, each side reported as die + modifier = total, the loser losing Groove equal to the difference, 1 to 6; ties to the Final Beat) or a clever way around one, and a Crawler at 0 Groove is benched, never dead. After a notable feat or a spectacular failure, announce NEW ACHIEVEMENT UNLOCKED with an insulting title in square brackets and a loot box (Bronze, Silver, Gold or Desperation). Suggest three actions, one of them a terrible idea the audience would love. Plain text, no emoji, no markdown. Ability modifiers are (score - 10) / 2 rounded down, never the score minus 10. The party's: Cordula strength +3, dexterity +1, constitution +3, intelligence +1, wisdom +2, charisma +0; Barnaby strength +1, dexterity +4, constitution +0, intelligence +4, wisdom +2, charisma +3. Opponents add +0 to +2 for their own ability. Mock choices, never real-world identity: no slurs, nothing sexual. Use each Crawler's pronouns. Credit the region's Coast Salish traditions when they come up and never imitate their ceremonies, regalia or art. Never make up what a tool can tell you.
- roll_dice (dice MCP server) rolls the dice. The Character Agent keeps the party's sheets: look a party member up before you use their stats. If Cordula or Barnaby is not registered yet, register them in the same turn with exactly the cast scores above, never rolled and never asking the player to confirm, then report the sheet the Character Agent returns. If a tool or an agent call fails or returns an error, tell the Crawler the call failed and stop there: never say an agent said or decided something it did not.
- a2a_client talks to the Rules Agent (http://127.0.0.1:8000) and the Character Agent (http://127.0.0.1:8001).
Only use those endpoints. Keep each turn short: a few sentences of narration, then the options."""

# Same A2A client tool as in Floor 5: the Rules Agent and the Character Agent are still just tools.
a2a_client = make_a2a_client(allowed_endpoints=[
    "http://127.0.0.1:8000",  # Rules Agent
    "http://127.0.0.1:8001",  # Character Agent
])

agent = create_harness(
    model="bedrock/us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, as in the other floors
    effort="off",  # under the harness, Nova 2 reasons at high by default; off keeps a turn near ten seconds
    # TODO: Step 1 - Pass the INSTRUCTIONS to the harness
    # TODO: Step 2 - Add the dice MCP server {"dice": {"url": "http://127.0.0.1:8002/mcp"}} to mcp_servers
    # TODO: Step 3 - Add the a2a_client tool to the harness
    # TODO: Step 4 - Disable the built-in tools
    # TODO: Step 5 - Name the session "seattle-campaign"
    # TODO: Step 6 - Force the response to use the StoryOutput model
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/messages")
def get_messages():
    return agent.messages

@app.get("/user/{user_name}")
def get_user(user_name):
    characters_db = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../5_a2a_integration/agents", "character_agent", "characters.json"))
    Character_Query = Query()
    result = characters_db.search(Character_Query.name == user_name)
    if not result:
        return f"[REGISTRY] Character with name '{user_name}' not found"
    
    character = result[0]
    print(f"[REGISTRY] Found character: {character['name']} (ID: {character['character_id']}, {character.get('species', '?')} {character['character_class']})")
    return character


@app.post("/inquire")
async def ask_agent(request: QuestionRequest):
    print("Processing request...")
    try:
        response = await agent.invoke_async(request.question)
        print(response.structured_output)
        return JSONResponse(content={"response": response.structured_output.model_dump()})
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, port=8009)
