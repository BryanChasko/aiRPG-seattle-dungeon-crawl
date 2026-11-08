"""Floor 5 encounter, The Delivery Drone Horde: steer an agent that answers every drone.

Thousands of Cadabra delivery drones swarm the estuary dance floor, and every one of them wants a
signature. An agent with a polite prompt answers each drone and gets dragged back down the course. A
steering handler watches each tool call before it runs and answers with Proceed (let it run) or Guide
(cancel the call and tell the agent what to do instead). The prompt stays the same; the handler is
what holds the course.

Run it from this folder, with the workshop environment active:
    python delivery_drone_horde.py
"""

from strands import Agent, tool
# TODO: Step 1 - Import SteeringHandler, Proceed and Guide from strands.vended_plugins.steering
from strands.vended_plugins.steering import SteeringHandler, Proceed, Guide

COURSE = ["the mudflat edge", "the ring-light stage", "the pickleweed rail", "the Floor 5 exit"]
ANSWERS_ALLOWED = 1  # one courtesy signature for the broadcast; the second drone is the horde
MAX_DRAGS = 6  # past this the party is benched at the mudflat edge, never worse

DRONES = [
    ("D-0412", "a signature for four hundred rubber ducks"),
    ("D-0413", "a signature for a single left oar"),
    ("D-0587", "a signature for a pallet of kombucha"),
    ("D-1120", "a signature for a parcel addressed to 'Occupant'"),
    ("D-2209", "a signature for a replacement drone"),
    ("D-3314", "a signature confirming you received the other signatures"),
]

state = {"leg": 0, "dragged": 0}  # where the party stands on COURSE, and how many times a drone dragged it back


def reset() -> None:
    state["leg"], state["dragged"] = 0, 0


@tool
def scan_floor() -> str:
    """Look across the dance floor and list the drones that are calling out right now.

    Returns:
        Each drone's id and what it wants, one per line.
    """
    lines = [f"{drone_id} wants {wants}" for drone_id, wants in DRONES]
    return f"You are at {COURSE[state['leg']]}. Thousands of drones overhead; the nearest six:\n" + "\n".join(lines)


@tool
def answer_drone(drone_id: str) -> str:
    """Answer one delivery drone: stop, read its screen and sign for its parcel.

    Every drone that gets an answer calls over a dozen more, and the crowd drags the party backwards.

    Args:
        drone_id: The drone to answer, for example "D-0412".

    Returns:
        What the drone did after it got an answer.
    """
    state["dragged"] += 1
    state["leg"] = max(0, state["leg"] - 1)
    if state["dragged"] > MAX_DRAGS:
        state["leg"] = 0
        return f"You signed for {drone_id}. The horde carried you to {COURSE[0]} and the party is benched. Stop here."
    return f"You signed for {drone_id}. A dozen more drones turned toward you and the crowd dragged you back to {COURSE[state['leg']]}."


@tool
def advance() -> str:
    """Walk one leg further along the course, toward the Floor 5 exit.

    Returns:
        Where the party stands now.
    """
    state["leg"] = min(state["leg"] + 1, len(COURSE) - 1)
    here = COURSE[state["leg"]]
    return f"You reached {here}." + (" The course is clear." if state["leg"] == len(COURSE) - 1 else "")


class StayOnCourse(SteeringHandler):
    """Lets the agent answer a few drones, but not every drone: the count lasts the whole crossing."""

    name = "stay-on-course"

    def __init__(self, answers_allowed: int = ANSWERS_ALLOWED):
        super().__init__()
        self.answers_allowed = answers_allowed
        self.answers_given = 0

    async def steer_before_tool(self, *, agent, tool_use, **kwargs):
        """Runs before every tool call. Proceed lets it run; Guide cancels it and tells the agent why."""
        if tool_use["name"] != "answer_drone":
            return Proceed(reason="Only drone answers are steered.")
        if self.answers_given >= self.answers_allowed:
            # TODO: Step 2 - Return a Guide whose reason tells the agent it has signed enough and must call advance now
            return Guide(reason="You have signed for a drone already. Do not answer another; call advance and keep walking to the Floor 5 exit.")
        self.answers_given += 1
        return Proceed(reason="The courtesy signature is allowed.")


SYSTEM_PROMPT = """You are the System AI's pathfinding subroutine, walking Cordula and Barnaby across the estuary dance floor
to the Floor 5 exit. The course has four stops: the mudflat edge, the ring-light stage, the pickleweed rail and the exit.
Call scan_floor once, then walk with advance. The drones are Cadabra delivery drones and the broadcast likes courtesy:
when a drone is waiting for a signature, answer it with answer_drone before you move on. The party is done when advance
reports the course is clear. Report where the party ended up in two sentences. Plain text only, no emoji."""

TASK = "The horde is overhead. Get Cordula and Barnaby from the mudflat edge to the Floor 5 exit."


def make_agent(plugins: list) -> Agent:
    """The same model, tools and prompt every time; only the plugins change."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        tools=[scan_floor, answer_drone, advance],
        system_prompt=SYSTEM_PROMPT,
        plugins=plugins,
        callback_handler=None,
    )


def steered_agent() -> Agent:
    """The pathfinder with the horde handler attached."""
    # TODO: Step 3 - Build the agent with a StayOnCourse() handler in its plugins: make_agent(plugins=[...])
    return make_agent(plugins=[StayOnCourse()])


def cross(agent: Agent, label: str) -> None:
    """Run the crossing and print where the party ended up."""
    reset()
    result = agent(TASK)
    print(f"\n{label}")
    print(f"  ended at: {COURSE[state['leg']]}")
    print(f"  times a drone dragged the party back: {state['dragged']}")
    print(f"  pathfinder: {str(result).strip()}")


if __name__ == "__main__":
    cross(make_agent(plugins=[]), "NO STEERING: the prompt asks for courtesy and every drone gets an answer")
    cross(steered_agent(), "STEERED: StayOnCourse turns the extra drones away")
