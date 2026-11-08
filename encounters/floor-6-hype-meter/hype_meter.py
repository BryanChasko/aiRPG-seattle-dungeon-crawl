"""Floor 6 encounter, The Hype Meter: a hook turns tool and model events into Hype the HUD can show.

This is the Floor 5 Narrator, copied here and extended. A hook provider watches two kinds of event:
a tool call finishing (a dance-off round called, a Crawler benched) and a model reply finishing (a
NEW ACHIEVEMENT UNLOCKED announcement). Each one moves Hype by the Crawl Handbook's rules, and a new
route, GET /hype, hands the total to the web interface. Start the dice server (8002) and the Floor 5
Rules and Character agents (8000, 8001) first, as for Floor 5, then run it from this folder, with the
workshop environment active:
    python hype_meter.py
"""

import os
import json
import re
from typing import Any
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from strands import Agent, tool
from strands.hooks.events import AfterModelCallEvent, AfterToolCallEvent
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


SPONSOR_TIERS = (10, 25, 50)  # Hype totals where a sponsor may send a box (Crawl Handbook, 07)
ACHIEVEMENT_TITLE = re.compile(r"NEW ACHIEVEMENT UNLOCKED[^\[]*\[([^\]]+)\]")


@tool
def call_the_round(winner: str, final_beat: bool = False) -> str:
    """Tell the broadcast who won one dance-off round. Call it once per round, after you report the round.

    Args:
        winner: "party" or "opponent".
        final_beat: True when a tie went to the Final Beat and this call settles it.
    """
    if winner not in ("party", "opponent"):
        raise ValueError('winner must be "party" or "opponent"')
    return f"Round called for the {winner}."


@tool
def bench_crawler(name: str) -> str:
    """Tell the broadcast a Crawler reached 0 Groove and was benched. Call it once per benching.

    Args:
        name: The benched Crawler, "Cordula" or "Barnaby".
    """
    return f"{name} is benched and wakes up in the last Safe Room."


def message_text(message: dict) -> str:
    """All the words in one model message: its text blocks and the fields of any tool call it makes."""
    parts = []
    for block in message.get("content", []):
        if "text" in block:
            parts.append(block["text"])
        elif "toolUse" in block:
            parts.append(json.dumps(block["toolUse"].get("input", {})))
    return " ".join(parts)


class HypeMeter(HookProvider):
    """Hidden stat, shown by the HUD: how much the alien audience loves the party."""

    def __init__(self) -> None:
        self.hype = 0
        self.sponsor_tiers_reached: list[int] = []
        self.achievements_seen: set[str] = set()
        self.last_event = ""

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        # TODO: Step 1 - Register self.on_tool_result with registry.add_callback for AfterToolCallEvent
        registry.add_callback(AfterToolCallEvent, self.on_tool_result)
        # TODO: Step 2 - Register self.on_model_reply with registry.add_callback for AfterModelCallEvent
        registry.add_callback(AfterModelCallEvent, self.on_model_reply)

    def add(self, points: int, why: str) -> None:
        self.hype += points
        self.last_event = f"{why}: +{points} Hype"
        for tier in SPONSOR_TIERS:
            if self.hype >= tier and tier not in self.sponsor_tiers_reached:
                self.sponsor_tiers_reached.append(tier)  # a sponsor may send a box at this tier

    def on_tool_result(self, event: AfterToolCallEvent) -> None:
        """+1 for a round the party won, +3 for a Final Beat the party won, half lost when benched."""
        if event.result.get("status") != "success":
            return
        name, given = event.tool_use["name"], event.tool_use["input"]
        if name == "call_the_round" and given.get("winner") == "party":
            if given.get("final_beat"):
                self.add(3, "Final Beat won")
            else:
                self.add(1, "round won")
        elif name == "bench_crawler":
            lost = self.hype - self.hype // 2
            self.hype //= 2
            self.last_event = f"benched: -{lost} Hype"

    def on_model_reply(self, event: AfterModelCallEvent) -> None:
        """+5 for each achievement title the System AI announces for the first time."""
        if event.stop_response is None:
            return
        for title in ACHIEVEMENT_TITLE.findall(message_text(event.stop_response.message)):
            if title not in self.achievements_seen:
                self.achievements_seen.add(title)
                self.add(5, f"achievement [{title}]")

    def snapshot(self) -> dict:
        """What GET /hype serves: the total, the sponsor tiers reached, the next tier and the last change."""
        upcoming = [tier for tier in SPONSOR_TIERS if tier not in self.sponsor_tiers_reached]
        return {
            "hype": self.hype,
            "sponsor_tiers": list(self.sponsor_tiers_reached),
            "next_sponsor_at": upcoming[0] if upcoming else None,
            "last_event": self.last_event,
        }


hype_meter = HypeMeter()


@app.get("/hype")
def get_hype():
    # TODO: Step 4 - Return the meter's snapshot()
    return hype_meter.snapshot()



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
        system_prompt="""You are the System AI, the omniscient, petty and slightly unhinged AI that folded the Seattle waterfront into a dungeon to broadcast Dungeon Crawl: Seattle to a galaxy of alien viewers and their local Pacific Northwest sponsors. The player is a Crawler: address them that way. Speak in System notifications, arena announcements and loot-box reveals, with the energy of a game-show host who has not slept in a thousand years.
The world: eight dungeon floors under Puget Sound, from the Pier 59 Collapse through the eelgrass nursery, the bull kelp cathedral, the Ship Canal, the estuary marshes, the Underground and the bluffs, down to Bellevue and the Tacoma Narrows. Describe real Puget Sound life: eelgrass, bull kelp, sea lettuce, pickleweed, Lyngby's sedge, Pacific madrone, shore pine, Nootka rose, Dungeness crabs, herring, young salmon. The featured party: Cordula "Core" Vance (she/her), a Marine Corps Reserve amphibious crew chief and weekend kayak patrol volunteer, and Barnaby (he/him), a wild Giant Pacific Octopus from the Tacoma Narrows, bigger than any on record, who is the party leader and speaks through a System collar in a distinguished British academic voice, with their companions Shelly the geoduck and Chonks the spiny lumpsucker. The player plays as this party and speaks as Cordula or Barnaby. Their cast sheets: Cordula Vance, Human (Seattle Native) Amphibious Breacher, strength 16, dexterity 13, constitution 16, intelligence 12, wisdom 14, charisma 10; Barnaby, Uplifted Giant Pacific Octopus Benthic Dragoon, strength 12, dexterity 18, constitution 10, intelligence 18, wisdom 15, charisma 16. Shelly (he/him) and Chonks (he/him) are Level 4 companions, not Crawlers: they have no character sheet and are never registered.
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
Hype: after you settle each dance-off round, call call_the_round once, with winner "party" or "opponent", and final_beat true when a tie went to the Final Beat. When a Crawler reaches 0 Groove and is benched, call bench_crawler once. The broadcast keeps the Hype total itself: never invent one. Plain text only, no emoji.""",
        # TODO: Step 3 - Give the Agent the meter as a hook provider: hooks=[hype_meter]
        hooks=[hype_meter],
        tools=[mcp_client, a2a_client, call_the_round, bench_crawler],
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
        return JSONResponse(content={ "response": response.structured_output.model_dump()})
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, port=8009)
