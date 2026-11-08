"""Floor 5 encounter, Barnaby Takes the Call: phone the Rules Agent and the Character Agent without the a2a_client tool.

The Narrator of Floor 5 reaches the other agents through the a2a_client tool, so the model decides
when to call and what to say. An A2AAgent is the same call made by your code: it reads the remote
agent's card, sends a message and streams back every A2A event as it happens. Barnaby places the
calls himself, then picks up a line of his own with an A2AServer on port 8003.

Start the Floor 5 Rules Agent (8000) and Character Agent (8001) first. Run it from this folder,
with the workshop environment active:
    python barnaby_takes_the_call.py
To pick up Barnaby's own line on port 8003 instead:
    python barnaby_takes_the_call.py serve
"""

from __future__ import annotations

import asyncio
import sys

from a2a.types import Message, TaskArtifactUpdateEvent, TaskStatusUpdateEvent
from strands import Agent
# TODO: Step 1 - Import A2AAgent from strands.agent.a2a_agent and A2AServer from strands.multiagent.a2a.server
from strands.agent.a2a_agent import A2AAgent
from strands.multiagent.a2a.server import A2AServer

RULES_URL = "http://127.0.0.1:8000"  # the Floor 5 Rules Agent
CHARACTER_URL = "http://127.0.0.1:8001"  # the Floor 5 Character Agent
BARNABY_PORT = 8003  # 8000, 8001, 8002, 8009 belong to Floor 5

CALLS = [
    (RULES_URL, "What happens when a dance-off round ends level? Name the handbook section."),
    (CHARACTER_URL, "Find Barnaby's sheet and report his Dexterity, Groove and Mana."),
]


def words_of(parts) -> str:
    """The text in a list of A2A message or artifact parts."""
    return " ".join(part.root.text for part in parts or [] if hasattr(part.root, "text")).strip()


def describe(event) -> str:
    """One line for one A2A event: what the remote agent is doing right now."""
    if isinstance(event, Message):
        return f"message: {words_of(event.parts)[:70]}"
    task, update = event
    if isinstance(update, TaskStatusUpdateEvent):
        said = words_of(update.status.message.parts) if update.status.message else ""
        return f"status {update.status.state.value}: {said[:70]}"
    if isinstance(update, TaskArtifactUpdateEvent):
        return f"artifact chunk: {words_of(update.artifact.parts)[:70]}"
    return f"task {task.status.state.value}"


def phone(endpoint: str) -> A2AAgent:
    """An A2AAgent for one remote endpoint, with a 60 second limit on each HTTP operation."""
    # TODO: Step 2 - Return an A2AAgent for the endpoint, with a timeout of 60 seconds
    return A2AAgent(endpoint, timeout=60)


async def take_the_call(line: A2AAgent, question: str):
    """Send one question down the line and print each A2A event as it arrives. Returns the final AgentResult."""
    result = None
    # TODO: Step 3 - Loop over line.stream_async(question): print describe(event["event"]) for each "a2a_stream" event, and keep event["result"] when it arrives
    async for event in line.stream_async(question):
        if event.get("type") == "a2a_stream":
            print(f"    {describe(event['event'])}")
        elif "result" in event:
            result = event["result"]
    return result


def create_barnaby(context_id: str) -> Agent:
    """Barnaby, answering when another agent calls."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        name="Barnaby",
        description="Barnaby, Giant Pacific Octopus and party leader: takes calls from other agents and answers in a dry, distinguished British academic voice.",
        callback_handler=None,
        system_prompt="""You are Barnaby, a Giant Pacific Octopus rescued from the Seattle Aquarium, party leader of the crawl, speaking through a System collar. You are a distinguished British academic with eight arms of opinions. You call Cordula "Sergeant". Answer in three sentences or fewer. Nobody is hurt in this dungeon; conflict is a dance-off. Plain text only, no emoji.""",
    )


def build_barnaby_line() -> A2AServer:
    """Barnaby's own line: an A2A server on port 8003 that builds a Barnaby for every caller."""
    # TODO: Step 4 - Return an A2AServer with the create_barnaby factory on port 8003 (BARNABY_PORT)
    return A2AServer(agent_factory=create_barnaby, port=BARNABY_PORT)


async def main() -> None:
    for endpoint, question in CALLS:
        line = phone(endpoint)
        card = await line.get_agent_card()
        print(f"\nBarnaby dials {card.name} at {endpoint}: {card.description}")
        print(f"  Barnaby: {question}")
        result = await take_the_call(line, question)
        print(f"  {card.name}: {str(result).strip()}")


if __name__ == "__main__":
    if "serve" in sys.argv[1:]:
        build_barnaby_line().serve()  # Ctrl+C hangs up
    else:
        asyncio.run(main())
