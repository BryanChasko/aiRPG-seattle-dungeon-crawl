"""Floor 5 boss battle, The Developer Advocate Swarm: four advocates, and they pass the mic themselves.

A swarm is a team of agents that hand the work to each other: every agent gets a handoff tool,
and the agent holding the floor decides who takes it next. Nobody draws the order in advance,
unlike the graph of The Quarterly Earnings Call. Here the advocate holding the floor calls one
move; if the party takes it, they hand the mic to an advocate who has not danced yet. The party
wins by out-dancing whoever holds the floor until nobody is left.

Run it from this folder, with the workshop environment active:
    python developer_advocate_swarm.py
"""

import sys
from pathlib import Path

from strands import Agent
# TODO: Step 1 - Import Swarm from strands.multiagent

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # the shared dance floor lives in encounters/
from dance_floor import dance_round, party_took_the_last_round, scoreboard

ADVOCATES = [
    # agent name, who, their act, the move they call, their modifier
    ("keynote", "the Keynote Speaker", "opens with a product vision and a fog machine", "Presence", 2),
    ("live_demo", "the Live Demo", "codes on stage and hopes the network holds", "Choreography", 1),
    ("livestream", "the Livestreamer", "narrates everything to forty thousand viewers", "Read the Room", 1),
    ("swag_table", "the Swag Table", "throws stickers and socks at the front row", "Power", 0),
]

CHALLENGE = ("The Developer Advocate Swarm has taken over the estuary dance floor mid-demo. Cordula and Barnaby "
             "challenge whoever holds the mic. The Keynote Speaker has it.")


def advocate(name: str, who: str, act: str, move: str, modifier: int) -> Agent:
    """One advocate: dance one move, then pass the mic only if the party took it."""
    others = ", ".join(a[0] for a in ADVOCATES if a[0] != name)
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        name=name,
        description=f"{who} of the Developer Advocate Swarm: {act}. Calls {move}.",
        tools=[dance_round],
        callback_handler=None,
        system_prompt=f"""You are {who} of the Developer Advocate Swarm: you {act}. You are a person at work, not a monster;
nobody gets hurt. When you hold the floor, call dance_round exactly once with opponent="{who}", move_call="{move}",
opponent_modifier={modifier}, tempo="Driving", and crawler="Barnaby" for Presence or Choreography, "Cordula" otherwise.
Report both totals the tool returned in one sentence, in character.
If the party won the round, hand off to one advocate from this list who has not danced yet in this conversation:
{others}. If every advocate has danced, do not hand off: say the party out-danced the whole swarm.
If the swarm won the round, do not hand off: say the swarm keeps the floor. Plain text only, no emoji.""",
    )


def build_swarm():
    """The four advocates as a swarm, the Keynote Speaker holding the mic first."""
    advocates = [advocate(*row) for row in ADVOCATES]
    # TODO: Step 2 - Create a Swarm of the four advocates with the keynote as its entry point
    # TODO: Step 3 - Cap it so a swarm that keeps passing the mic cannot dance forever: at most 4 handoffs and 6 iterations
    return None


if __name__ == "__main__":
    swarm = build_swarm()
    result = swarm(CHALLENGE)
    print(f"\nTHE DEVELOPER ADVOCATE SWARM: {result.status}")
    for round_ in scoreboard:
        print(f"  {round_['opponent']}, {round_['move_call']}: {round_['crawler']} against {round_['opponent_roll']}"
              f"{' (Final Beat: ' + round_['final_beat'] + ')' if round_['final_beat'] else ''} -> {round_['winner']}")
    print(f"  the mic went: {' -> '.join(node.node_id for node in result.node_history)}")
    if len(scoreboard) == len(ADVOCATES) and party_took_the_last_round():
        print("  The party out-danced the whole swarm. The advocates have gone to find better lighting.")
