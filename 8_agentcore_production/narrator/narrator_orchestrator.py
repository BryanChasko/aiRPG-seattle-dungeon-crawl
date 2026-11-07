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
# TODO: 8.1 Step 2 - Import aws_iam_streamablehttp_client from mcp_proxy_for_aws.client
from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client
# TODO: 8.2 Step 2 - Import ClientConfig from a2a.client and SigV4HTTPXAuth from mcp_proxy_for_aws.sigv4_helper
from a2a.client import ClientConfig
from mcp_proxy_for_aws.sigv4_helper import SigV4HTTPXAuth
# TODO: 8.4 Step 1 - Import BedrockAgentCoreApp from bedrock_agentcore.runtime
from bedrock_agentcore.runtime import BedrockAgentCoreApp
# TODO: 8.4 Step 2 - Import AgentCoreMemoryConfig from bedrock_agentcore.memory.integrations.strands.config and AgentCoreMemorySessionManager from bedrock_agentcore.memory.integrations.strands.session_manager
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager

# TODO: 8.4 Step 1 - Replace the FastAPI app and its endpoints with a BedrockAgentCoreApp
app = BedrockAgentCoreApp()

# The URLs of your runtimes are read from the .env file of the floor folder (see .env.example)
load_dotenv()

# TODO: 8.1 Step 1 - Read DICE_SERVER_URL from the environment
DICE_SERVER_URL = os.environ["DICE_SERVER_URL"]

# TODO: 8.1 Step 2 - Create an MCPClient connecting to DICE_SERVER_URL with aws_iam_streamablehttp_client for the bedrock-agentcore service
mcp_client = MCPClient(lambda: aws_iam_streamablehttp_client(endpoint=DICE_SERVER_URL, aws_service="bedrock-agentcore"))

# TODO: 8.2 Step 1 - Read CHARACTER_AGENT_URL from the environment
CHARACTER_AGENT_URL = os.environ["CHARACTER_AGENT_URL"]

# TODO: 8.2 Step 2 - Create a ClientConfig whose httpx client signs requests with SigV4 for bedrock-agentcore in the region of your boto3 session and sends a session id
agentcore_config = ClientConfig(httpx_client=httpx.AsyncClient(
    auth=SigV4HTTPXAuth(boto3.Session().get_credentials(), "bedrock-agentcore", boto3.Session().region_name),
    # AgentCore runs one microVM per session; the id must be at least 33 characters long
    headers={"X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": str(uuid.uuid4())},
    timeout=300,
))

# TODO: 8.3 Step 1 - Read RULES_AGENT_URL from the environment
RULES_AGENT_URL = os.environ["RULES_AGENT_URL"]

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
    (RULES_AGENT_URL, agentcore_config),  # Rules Agent, on AgentCore
    # TODO: 8.2 Step 3 - Replace the local Character Agent with CHARACTER_AGENT_URL and agentcore_config
    (CHARACTER_AGENT_URL, agentcore_config),  # Character Agent, on AgentCore
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
            session_manager=AgentCoreMemorySessionManager(
                AgentCoreMemoryConfig(memory_id=os.environ["MEMORY_CONVERSATIONS_ID"], session_id=session_id, actor_id="player"),
            ),
            callback_handler=None,
        )
    return narrators[session_id]

# TODO: 8.4 Step 3 - Create the entrypoint: return the messages of the session's Narrator if the payload asks for them, otherwise answer the prompt with a StoryOutput
@app.entrypoint
async def invoke(payload, context):
    narrator = get_narrator(context.session_id)
    if payload.get("messages"):
        return narrator.messages
    response = await narrator.invoke_async(payload["prompt"])
    return response.structured_output.model_dump()

if __name__ == "__main__":
    # TODO: 8.4 Step 4 - Replace uvicorn.run with the run method of the BedrockAgentCoreApp
    app.run()
