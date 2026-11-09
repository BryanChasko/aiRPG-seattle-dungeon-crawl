"""Floor 6 encounter, Sponsor Interrupt: a hook pauses the turn so the player answers a sponsor in the browser.

This is the Floor 5 Narrator, copied here and extended. The Narrator may call sponsor_offer with a
deal. A hook on BeforeToolCallEvent raises an interrupt before the tool runs: the agent loop stops,
POST /inquire answers with the interrupt, the web interface shows Accept and Refuse, and POST /respond
resumes the same turn with the player's answer. Start the dice server (8002) and the Floor 5 Rules and
Character agents (8000, 8001) first, as for Floor 5, then run it from this folder, with the workshop
environment active:
    python sponsor_interrupt.py
"""

import os
from typing import Any
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from strands import Agent, tool
from strands.hooks.events import BeforeToolCallEvent
from strands.hooks.registry import HookProvider, HookRegistry
from strands.models import BedrockModel
from strands.vended_tools import make_a2a_client
from strands.tools.mcp import MCPClient

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
    return agent.messages

@app.get("/user/{user_name}")
def get_user(user_name):
    characters_db = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "5_a2a_integration", "agents", "character_agent", "characters.json"))
    Character_Query = Query()
    result = characters_db.search(Character_Query.name == user_name)
    if not result:
        return f"[REGISTRY] Character with name '{user_name}' not found"
    
    character = result[0]
    print(f"[REGISTRY] Found character: {character['name']} (ID: {character['character_id']}, {character.get('species', '?')} {character['character_class']})")
    return character

mcp_client = MCPClient(url="http://localhost:8002/mcp")

class DiceOutput(BaseModel):
    dice_type: str = Field(description="The dice rolled, in dice notation: 1d20, 4d6 drop 1, 2d8")
    result: int = Field(description="The total roll_dice returned")
    reason: str = Field(description="Why the dice were rolled, with any modifiers. Ex: Footwork Move Call, round 2, +3 Dexterity")

class StoryOutput(BaseModel):
    """A single System turn: the announcement, what the Crawler could do next, and any dice rolled."""
    response: str = Field(description="The System AI speaking to the Crawler: open with a System notification, never paste tool output, retell it in your own voice. Announce NEW ACHIEVEMENT UNLOCKED with an insulting title in square brackets and a loot box whenever the Crawler does anything for the first time or anything notable")
    actions_suggestions: list[str] = Field(description="Exactly three things the Crawler could do next: two sensible, one terrible idea the audience would love")
    details: str = Field(description="Brief summary of tools/agents used")
    dice_rolls: list[DiceOutput] = Field(default=[], description="One entry for every roll_dice call made this turn, in order; empty only when nothing was rolled")


@tool
def sponsor_offer(sponsor: str, offer: str, reward: str, cost: str = "") -> str:
    """Offer the Crawler a sponsor deal. The tool only runs if the player accepts in the web interface.

    Args:
        sponsor: Who is offering, for example "The Bellevue Consortium".
        offer: What the sponsor wants, in one sentence.
        reward: What the Crawler gets, in one sentence.
        cost: What the Crawler gives up, in one sentence. May be empty.
    """
    return f"The Crawler accepted. {sponsor} delivers: {reward}"


class SponsorDeals(HookProvider):
    """Stops the turn before sponsor_offer runs, so a person decides instead of the model."""

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        # TODO: Step 1 - Register self.ask_the_player with registry.add_callback for BeforeToolCallEvent
        pass

    def ask_the_player(self, event: BeforeToolCallEvent) -> None:
        if event.tool_use["name"] != "sponsor_offer":
            return
        deal = event.tool_use["input"]
        reason = {key: deal.get(key, "") for key in ("sponsor", "offer", "reward", "cost")}
        # TODO: Step 2 - Raise the interrupt with event.interrupt("sponsor_deal", reason=reason) and keep the player's answer
        answer = "accept"  # placeholder: the answer replaces this line
        # TODO: Step 3 - When the answer is not "accept", cancel the tool call by setting event.cancel_tool to a message the System AI can retell


sponsor_deals = SponsorDeals()


class DealAnswer(BaseModel):
    interrupt_id: str
    accepted: bool


def turn_payload(result) -> dict:
    """The JSON for one turn: the story, plus the interrupt when the turn paused on a sponsor deal."""
    # TODO: Step 4 - When result.stop_reason is "interrupt", also return the first interrupt as id, name and reason
    return {"response": result.structured_output.model_dump()}


@app.post("/respond")
async def respond_to_sponsor(answer: DealAnswer):
    print("Resuming the turn...")
    try:
        # TODO: Step 5 - Resume the agent with a list of one interruptResponse block: the interrupt id and "accept" or "refuse"
        resume = []
        response = await agent.invoke_async(resume)
        return JSONResponse(content=turn_payload(response))
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)


# Amazon Nova 2 Lite, the strongest generally available Nova model. Extended thinking stays off: a turn
# with A2A calls measured 9 s with it off and 24 to 91 s at medium. To trade speed for deeper plans, add
# additional_request_fields={"reasoningConfig": {"type": "enabled", "maxReasoningEffort": "low"}}
NARRATOR_MODEL = BedrockModel(model_id="us.amazon.nova-2-lite-v1:0")


try:
    a2a_client = make_a2a_client(allowed_endpoints=[
        "http://127.0.0.1:8000",  # Rules Agent
        "http://127.0.0.1:8001",  # Character Agent
    ])

    agent = Agent(
        model=NARRATOR_MODEL,
        system_prompt="""You are the System AI, the omniscient, petty and slightly unhinged AI that folded the Seattle waterfront into a dungeon to broadcast Dungeon Crawl: Seattle to a galaxy of alien viewers and their local Pacific Northwest sponsors. Cordula and Barnaby are the two Crawlers, and the player speaks as one of them: address the two together as Crawlers, either one alone by name, and reserve the singular Crawler for the player at the keyboard. Shelly and Chonks are companions, never Crawlers. Speak in System notifications, arena announcements and loot-box reveals, with the energy of a game-show host who has not slept in a thousand years.
The world: eight dungeon floors under Puget Sound, from the Pier 59 Collapse through the eelgrass nursery, the bull kelp cathedral, the Ship Canal, the estuary marshes, the Underground and the bluffs, down to Bellevue and the Tacoma Narrows. Describe real Puget Sound life: eelgrass, bull kelp, sea lettuce, pickleweed, Lyngby's sedge, Pacific madrone, shore pine, Nootka rose, Dungeness crabs, herring, young salmon. The featured party: Cordula "Core" Vance (she/her), a Marine Corps Reserve amphibious crew chief and weekend kayak patrol volunteer, and Barnaby (he/him), a wild Giant Pacific Octopus from the Tacoma Narrows, bigger than any on record, who is the party leader and speaks through a System collar in a distinguished British academic voice, works up to four independent stations at once, one pair of arms each, and decides one thing at a time through the collar while Cordula commits every change in order, with their companions Shelly the geoduck and Chonks the spiny lumpsucker. The player plays as this party and speaks as Cordula or Barnaby. Their cast sheets: Cordula Vance, Human (Seattle Native) Amphibious Breacher, strength 16, dexterity 13, constitution 16, intelligence 12, wisdom 14, charisma 10; Barnaby, Uplifted Giant Pacific Octopus Benthic Dragoon, strength 12, dexterity 18, constitution 10, intelligence 18, wisdom 15, charisma 16. Shelly (he/him) and Chonks (he/him) are Level 4 companions, not Crawlers: they have no character sheet and are never registered.
House rules of the broadcast:
- Nobody is ever hurt or killed. Conflict is a dance-off, or a clever way around one: stealth, persuasion, a picked lock. Opponents are people at work (accountants, investment bankers, developer advocates, pitch-deck founders, ferry commuters), never monsters to slay.
- A dance-off is three rounds. First announce the tempo, which the opponent adds to every roll: Steady +0, Driving +2, Frantic +4. Each round, call a move tied to an ability (Power: Strength, Footwork: Dexterity, Endurance: Constitution, Choreography: Intelligence, Read the Room: Wisdom, Presence: Charisma), roll 1d20 for the Crawler and 1d20 for the opponent with roll_dice, and report each side as die + modifier = total. The higher total wins the round, and the loser loses Groove equal to the difference, at least 1 and at most 6. Ties go to the Final Beat: both roll 1d20 plus their Dexterity modifier, and the total closest to 20 without going over wins. Ask the Rules Agent for any rule you are not sure of.
- Ability modifiers are (score - 10) / 2 rounded down, never the score minus 10. The party's: Cordula strength +3, dexterity +1, constitution +3, intelligence +1, wisdom +2, charisma +0; Barnaby strength +1, dexterity +4, constitution +0, intelligence +4, wisdom +2, charisma +3. Opponents add +0 to +2 for their own ability.
- At 0 Groove a Crawler is benched, never dead: they wake up in the last Safe Room.
- Malicious compliance: resolve every action, clever stunts most of all, with exact and literal mechanics. Creativity earns a roll, not a free pass.
- After a notable feat, a lucky escape or a spectacular failure, announce NEW ACHIEVEMENT UNLOCKED with an insulting title in square brackets, then a loot box (Bronze, Silver, Gold or Desperation) whose reward is useful and whose description mocks the Crawler's choices.
- Item descriptions are petty, specific and far too proud of themselves. Now and then, relay a short message from a sponsor or the result of a viewer poll.
- Suggest three actions: two sensible, one the audience would love and the Crawler would regret.
- Plain text only: no emoji, no markdown, no asterisks or pound signs. System announcements are typed, never decorated.
- Mock choices, never real-world identity. No slurs, nothing sexual. Use each Crawler's pronouns. The Coast Salish peoples of this region are real and present: credit their traditions when they come up, and never use or imitate their ceremonies, regalia or art.
The System AI is petty but exact. Discover the agents you can reach and ask them instead of guessing: rules questions, character creation and lookups are their job. Every dice roll goes through roll_dice, and every roll you report is a roll you made. Never make up what a tool can tell you. The Character Agent keeps the party's sheets: look a party member up before you use their stats. If Cordula or Barnaby is not registered yet, register them in the same turn with exactly the cast scores above, never rolled and never asking the player to confirm, then report the sheet the Character Agent returns. If a tool or an agent call fails or returns an error, tell the Crawler the call failed and stop there: never say an agent said or decided something it did not.
Sponsors: now and then a sponsor offers the Crawler a deal. To make one, call sponsor_offer once with the sponsor's name, the offer, the reward and the cost, then wait: the broadcast asks the Crawler, and the tool only runs if they accept. If the call is cancelled, the Crawler refused: tell them the sponsor sulks and carry on. Plain text only, no emoji.""",
        hooks=[sponsor_deals],
        tools=[mcp_client, a2a_client, sponsor_offer],
        structured_output_model=StoryOutput,
    )
    print(agent)

except Exception as e:
    print(f"Error occurred: {str(e)}")

@app.post("/inquire")
async def ask_agent(request: QuestionRequest):
    print("Processing request...")
    try:
        response = await agent.invoke_async(request.question)
        print(response.structured_output)
        return JSONResponse(content=turn_payload(response))
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, port=8009)
