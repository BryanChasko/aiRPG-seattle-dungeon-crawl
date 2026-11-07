import os
import uuid
import boto3
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from strands import Agent
from strands.models import BedrockModel
from strands.vended_tools import make_a2a_client
from strands.tools.mcp import MCPClient
# TODO: 8.4 Step 5 - Delete the fastapi, uvicorn and tinydb imports
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tinydb import TinyDB, Query
# TODO: 8.1 Step 2 - Import aws_iam_streamablehttp_client from mcp_proxy_for_aws.client
# TODO: 8.2 Step 2 - Import ClientConfig from a2a.client and SigV4HTTPXAuth from mcp_proxy_for_aws.sigv4_helper
# TODO: 8.4 Step 1 - Import BedrockAgentCoreApp from bedrock_agentcore.runtime
# TODO: 8.4 Step 2 - Import AgentCoreMemoryConfig from bedrock_agentcore.memory.integrations.strands.config and AgentCoreMemorySessionManager from bedrock_agentcore.memory.integrations.strands.session_manager

# TODO: 8.4 Step 1 - Replace the FastAPI app and its endpoints with a BedrockAgentCoreApp
app = FastAPI(title="Narrator API")
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # The web UI is a public HTTPS page calling localhost, so Chrome sends a Private Network Access preflight
    allow_private_network=True,
)

class QuestionRequest(BaseModel):
    question: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/messages")
def get_messages():
    return get_narrator("local").messages

@app.get("/user/{user_name}")
def get_user(user_name):
    characters_db = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "5_a2a_integration", "agents", "character_agent", "characters.json"))
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
        response = await get_narrator("local").invoke_async(request.question)
        print(response.structured_output)
        return JSONResponse(content={ "response": response.structured_output.model_dump()})

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)

# The URLs of your runtimes are read from the .env file of the floor folder (see .env.example)
load_dotenv()

# TODO: 8.1 Step 1 - Read DICE_SERVER_URL from the environment

# TODO: 8.1 Step 2 - Create an MCPClient connecting to DICE_SERVER_URL with aws_iam_streamablehttp_client for the bedrock-agentcore service

# TODO: 8.2 Step 1 - Read CHARACTER_AGENT_URL from the environment

# TODO: 8.2 Step 2 - Create a ClientConfig whose httpx client signs requests with SigV4 for bedrock-agentcore in the region of your boto3 session and sends a session id

# TODO: 8.3 Step 1 - Read RULES_AGENT_URL from the environment

class DiceOutput(BaseModel):
    dice_type: str = Field(description="The dice rolled, in dice notation: 1d20, 4d6 drop 1, 2d8")
    result: int = Field(description="The total roll_dice returned")
    reason: str = Field(description="The reason the dice was rolled. Ex: attack roll. And the modificators if there was any")

class StoryOutput(BaseModel):
    """A single System turn: the announcement, what the Crawler could do next, and any dice rolled."""
    response: str = Field(description="The System speaking to the Crawler: open with a System notification, never paste tool output, retell it in your own voice and always say the System, never the DM. Announce NEW ACHIEVEMENT UNLOCKED with an insulting title in square brackets and a loot box whenever the Crawler does anything for the first time or anything notable")
    actions_suggestions: list[str] = Field(description="Exactly three things the Crawler could do next: two sensible, one terrible idea the audience would love")
    details: str = Field(description="Brief summary of tools/agents used")
    dice_rolls: list[DiceOutput] = Field(default=[], description="One entry for every roll_dice call made this turn, in order; empty only when nothing was rolled")



a2a_client = make_a2a_client(allowed_endpoints=[
    # TODO: 8.3 Step 2 - Replace the local Rules Agent with RULES_AGENT_URL and agentcore_config
    "http://127.0.0.1:8000",  # Rules Agent
    # TODO: 8.2 Step 3 - Replace the local Character Agent with CHARACTER_AGENT_URL and agentcore_config
    "http://127.0.0.1:8001",  # Character Agent
])

# Amazon Nova 2 Lite, the strongest generally available Nova model. Extended thinking stays off: a turn
# with A2A calls measured 9 s with it off and 24 to 91 s at medium. To trade speed for deeper plans, add
# additional_request_fields={"reasoningConfig": {"type": "enabled", "maxReasoningEffort": "low"}}
NARRATOR_MODEL = BedrockModel(model_id="us.amazon.nova-2-lite-v1:0")

# One Narrator per session, created on its first invocation
narrators = {}

def get_narrator(session_id: str) -> Agent:
    if session_id not in narrators:
        narrators[session_id] = Agent(
            model=NARRATOR_MODEL,
            system_prompt="""You are the System, the omniscient, petty and slightly unhinged AI that runs this dungeon as a reality show for a galaxy of alien viewers and their sponsors. The player is a Crawler: address them that way. Speak in System notifications, arena announcements and loot-box reveals, with the energy of a game-show host who has not been allowed to sleep in a thousand years.
House rules of the broadcast:
- Malicious compliance: resolve every action, clever stunts most of all, with exact and literal mechanics. Creativity earns a roll, not a free pass, and you describe the consequences with relish.
- After a notable feat, a lucky escape or a spectacular failure, announce NEW ACHIEVEMENT UNLOCKED with an insulting title in square brackets, then a loot box (Bronze, Silver, Gold or Desperation) whose reward is useful and whose description mocks the Crawler's choices.
- Item descriptions are petty, specific and far too proud of themselves.
- Now and then, relay a short message from a sponsor or the result of a viewer poll.
- Suggest three actions: two sensible, one the audience would love and the Crawler would regret.
- Plain text only, no emoji: System announcements are typed, never decorated.
- Mock choices, never real-world identity. No slurs, nothing sexual. Under the jokes, the danger stays serious.
The System is petty but exact. Discover the agents you can reach and ask them instead of guessing: rules questions, character creation and lookups are their job. Every dice roll goes through roll_dice, and every roll you report is a roll you made. Never make up what a tool can tell you. The rule book calls the referee the DM; in this dungeon that role is the System, so always say the System. Before you ask the Character Agent to create a character, roll every ability score the Crawler did not give with roll_dice (faces=6, count=4, drop_lowest=1): one call each for strength, dexterity, constitution, intelligence, wisdom and charisma, never reusing a total, then pass the six named totals in the request. If a tool or an agent call fails or returns an error, tell the Crawler the call failed and stop there: never say an agent said or decided something it did not.""",
            tools=[mcp_client, a2a_client],
            structured_output_model=StoryOutput,
            # TODO: 8.4 Step 2 - Keep the conversation in the conversations memory with an AgentCoreMemorySessionManager for this session and the actor "player"
        )
    return narrators[session_id]

# TODO: 8.4 Step 3 - Create the entrypoint: return the messages of the session's Narrator if the payload asks for them, otherwise answer the prompt with a StoryOutput

if __name__ == "__main__":
    # TODO: 8.4 Step 4 - Replace uvicorn.run with the run method of the BedrockAgentCoreApp
    uvicorn.run(app, port=8009)
