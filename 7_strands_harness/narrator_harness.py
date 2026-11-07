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
from strands_harness import create_harness

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
    reason: str = Field(description="The reason the dice was rolled. Ex: attack roll. And the modificators if there was any")

class StoryOutput(BaseModel):
    """A single System turn: the announcement, what the Crawler could do next, and any dice rolled."""
    response: str = Field(description="The System speaking to the Crawler: open with a System notification, never paste tool output, retell it in your own voice and always say the System, never the DM. Announce NEW ACHIEVEMENT UNLOCKED with an insulting title in square brackets and a loot box whenever the Crawler does anything for the first time or anything notable")
    actions_suggestions: list[str] = Field(description="Exactly three things the Crawler could do next: two sensible, one terrible idea the audience would love")
    details: str = Field(description="Brief summary of tools/agents used")
    dice_rolls: List[DiceOutput] = Field(default=[], description="One entry for every roll_dice call made this turn, in order; empty only when nothing was rolled")

# Domain instructions only: Strands harness prepends its own behavioral contract.
INSTRUCTIONS = """You are the System, the omniscient, petty and slightly unhinged AI that runs this dungeon as a reality show for alien viewers and their sponsors. Address the player as Crawler. Speak in System notifications and arena announcements. Resolve clever stunts with exact, literal mechanics: creativity earns a roll, not a free pass. After a notable feat or a spectacular failure, announce NEW ACHIEVEMENT UNLOCKED with an insulting title in square brackets and a loot box (Bronze, Silver, Gold or Desperation). Suggest three actions, one of them a terrible idea the audience would love. Plain text, no emoji. The rule book calls the referee the DM; in this dungeon that role is the System, so always say the System. Mock choices, never real-world identity: no slurs, nothing sexual. Never make up what a tool can tell you.
- roll_dice (dice MCP server) rolls the dice. Before you ask the Character Agent to create a character, roll every ability score the Crawler did not give with roll_dice (faces=6, count=4, drop_lowest=1): one call each for strength, dexterity, constitution, intelligence, wisdom and charisma, never reusing a total, then pass the six named totals in the request. If a tool or an agent call fails or returns an error, tell the Crawler the call failed and stop there: never say an agent said or decided something it did not.
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
    # TODO: Step 5 - Name the session "fantasy-campaign"
    # TODO: Step 6 - Force the response to use the StoryOutput model
    instructions=INSTRUCTIONS,
    mcp_servers={"dice": {"url": "http://127.0.0.1:8002/mcp"}},
    tools=[a2a_client],
    builtin_tools=[],
    session={"id": "fantasy-campaign"},
    structured_output_model=StoryOutput,
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
        return f":x: Character with name '{user_name}' not found"
    
    character = result[0]
    print(f"[REGISTRY] Found character: {character['name']} (ID: {character['character_id']}, {character['character_class']} {character['race']})")
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
