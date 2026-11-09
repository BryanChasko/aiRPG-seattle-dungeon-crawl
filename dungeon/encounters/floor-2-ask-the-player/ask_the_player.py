"""Floor 2 sidequest, Ask the Player: the Narrator stops mid-turn and asks which Move Call to make.

It starts from the Floor 2 vended tools. Most tools do something and hand back a result. The
handoff_to_user tool does the opposite: it pauses the agent's turn, shows your question to the person
at the keyboard, and picks the turn up again with their answer as the tool's result. The pause is an
interrupt: the result comes back with stop_reason "interrupt", and you resume the same agent with the answer.

Run it from this folder, with the workshop environment active:
    python ask_the_player.py
"""

import sys
from pathlib import Path

from strands import Agent
# TODO: Step 1 - Import handoff_to_user from strands.vended_tools
from strands.vended_tools import handoff_to_user

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # the shared dance floor lives in encounters/
from dance_floor import dance_round, scoreboard

narrator = Agent(
    model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
    tools=[
        # TODO: Step 2 - Add the handoff_to_user and dance_round tools to the agent
        handoff_to_user,
        dance_round,
    ],
    callback_handler=None,
    system_prompt="""You are the Narrator of a dungeon crawl under Seattle, calling a dance-off live for alien viewers.
The party is Cordula and the Quarterly Close Accountant, a person at work who is joked about for their job and never hurt.
The Move Call is the player's to make, not yours. Before any dice are rolled, call handoff_to_user once with a short question
that lists the choices: Power, Footwork, Endurance, Choreography, Read the Room, Presence. Then call dance_round once with
the Move Call the player chose, crawler="Cordula", and opponent="the Quarterly Close Accountant". Report what dance_round
returned in two sentences, and never roll or decide anything yourself. Plain text only, no emoji.""",
)


def asking(result) -> bool:
    """True when the Narrator stopped to ask the player something instead of finishing the turn."""
    # TODO: Step 3 - Return whether the result's stop_reason is "interrupt"
    return result.stop_reason == "interrupt"


def answer_block(interrupt, answer: str) -> dict:
    """The content block that resumes the Narrator: the player's answer, tied to the question it answers."""
    # TODO: Step 4 - Return an "interruptResponse" block holding the interrupt's id as "interruptId" and the answer as "response"
    return {"interruptResponse": {"interruptId": interrupt.id, "response": answer}}


if __name__ == "__main__":
    result = narrator("The round is about to begin. Call it.")
    while asking(result):
        question = result.interrupts[0]
        print(f"\nTHE NARRATOR STOPS THE SHOW: {question.reason}")
        result = narrator([answer_block(question, input("Your Move Call: ").strip())])
    print(f"\nNarrator: {str(result).strip()}")
    for round_ in scoreboard:
        print(f"  {round_['move_call']}: {round_['crawler']} against {round_['opponent_roll']} -> {round_['winner']}")
