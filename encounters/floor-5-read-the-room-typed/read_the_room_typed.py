"""Floor 5 dance-off, Read the Room, Typed: the Narrator picks the tempo and the Move Call as values, not prose.

On Floor 5 the Narrator announces a dance-off in its own words and your code has to hope the words
mean a tempo. A decision model asks the model closed questions instead: each answer comes back as
one of the choices you listed, so "Driving" is a string your code can pass straight to dance_round.
The party dances the Quarterly Close Accountant for three rounds, takes two of three to win, and
every die is rolled by the shared dance floor, never by the model.

Run it from this folder, with the workshop environment active:
    python read_the_room_typed.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from strands.models import BedrockModel
# TODO: Step 1 - Import LLMDecisionModel from strands.decisions.llm_decision_model
from strands.decisions.llm_decision_model import LLMDecisionModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # the shared dance floor lives in encounters/
from dance_floor import MODIFIERS, TEMPO, dance_round, scoreboard

OPPONENT = "the Quarterly Close Accountant"
OPPONENT_MODIFIER = 1  # the accountant is good with a calculator and a little better with a beat
MOVES = ["Power", "Footwork", "Endurance", "Choreography", "Read the Room", "Presence"]

SITUATION = (
    "The Quarterly Close Accountant has the estuary dance floor for the evening: grey suit, reading glasses, "
    "a calculator in one hand and spreadsheet pages in the air. They are precise, they hate improvisation, "
    "and they have been at their desk since dawn. The party: Cordula (strong and steady: Power +3, "
    "Endurance +3, Read the Room +2) and Barnaby (quick and clever: Footwork +4, Choreography +4, Presence +3, "
    "Read the Room +2). Nobody is hurt in a dance-off."
)

DECISION_PROMPT = ("You are the System AI, calling a dance-off between the party and an accountant at work. "
                   "Read the room and pick the tempo and the Move Call that make the best show for the audience. "
                   "Plain text only, no emoji.")


def make_decision_model():
    """The System AI's decision model: Amazon Nova 2 Lite, answering closed questions."""
    # TODO: Step 2 - Return an LLMDecisionModel over a BedrockModel with model_id us.amazon.nova-2-lite-v1:0 and a system_prompt of DECISION_PROMPT
    return LLMDecisionModel(
        model=BedrockModel(model_id="us.amazon.nova-2-lite-v1:0"),  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=DECISION_PROMPT,
    )


def best_dancer(move_call: str) -> str:
    """Whoever in the party has the higher modifier for the move; Cordula on a tie. Chosen in code, not by the model."""
    return max(MODIFIERS, key=lambda name: (MODIFIERS[name][move_call], name == "Cordula"))


async def read_the_room(decision_model, situation: str, last_move: str | None, tempo: str | None) -> tuple[str, str]:
    """Ask for the Move Call, and for the tempo too when none has been announced. Returns (tempo, move_call) as plain strings."""
    questions = {
        "move_call": {
            "question": "Which Move Call should the System AI make next, given what you know about the accountant and the party?",
            "choices": [move for move in MOVES if move != last_move],  # the System AI never calls the same move twice in a row
            "uncertainty": False,  # commit to one of the choices; no "uncertain" answer
        },
    }
    if tempo is None:
        questions["tempo"] = {
            "question": "Which tempo should the System AI announce? Steady is gentle, Driving is brisk, Frantic is a quarter-end scramble.",
            "choices": list(TEMPO),
            "uncertainty": False,
        }
    result = None
    # TODO: Step 3 - Ask the decision model the questions about the situation with ask, and keep the DecisionResult in result
    result = await decision_model.ask(situation, questions)
    answers = result.answers
    return tempo or str(answers["tempo"]), str(answers["move_call"])


def dance(tempo: str, move_call: str) -> dict:
    """Roll one round with the typed values."""
    # TODO: Step 4 - Return dance_round(...) for the opponent, with move_call and tempo as the typed values, crawler=best_dancer(move_call) and opponent_modifier=OPPONENT_MODIFIER
    return dance_round(opponent=OPPONENT, move_call=move_call, tempo=tempo, crawler=best_dancer(move_call),
                       opponent_modifier=OPPONENT_MODIFIER)


async def main() -> None:
    decision_model = make_decision_model()
    tempo, last_move = None, None
    for round_number in (1, 2, 3):
        tempo, move_call = await read_the_room(decision_model, SITUATION, last_move, tempo)
        round_ = dance(tempo, move_call)
        last_move = move_call
        if round_number == 1:
            print(f"The System AI announces the tempo: {tempo}")
        print(f"Round {round_number}, {move_call}: {round_['crawler']} against {round_['opponent_roll']}"
              f"{' (Final Beat: ' + round_['final_beat'] + ')' if round_['final_beat'] else ''}"
              f" -> {round_['winner']}, {round_['groove_lost']} Groove lost")
        wins = sum(1 for r in scoreboard if r["winner"] == "party")
        if wins == 2 or len(scoreboard) - wins == 2:
            break
    if sum(1 for r in scoreboard if r["winner"] == "party") >= 2:
        print("The party takes two of three. The accountant leaves the floor, relieved, and files a very short report.")
    else:
        print("The accountant takes two of three, and reconciles the party's Groove with great pleasure.")


if __name__ == "__main__":
    asyncio.run(main())
