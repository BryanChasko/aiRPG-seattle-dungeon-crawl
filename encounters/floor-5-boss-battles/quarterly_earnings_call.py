"""Floor 5 boss battle, The Quarterly Earnings Call: three executives, one fixed agenda.

A graph runs agents in an order you draw: nodes are agents, edges say who goes next, and an edge
can carry a condition. On this call the Quarterly Close Accountant reviews, the Bonus-Season
Investment Banker spins, and the Regional Managing Director signs off. Each one calls one move
against the party, and the call only moves on to the next executive if the party took the round.

Run it from this folder, with the workshop environment active:
    python quarterly_earnings_call.py
"""

from strands import Agent
# TODO: Step 1 - Import GraphBuilder from strands.multiagent
from strands.multiagent import GraphBuilder

from dance_floor import dance_round, party_took_the_last_round, scoreboard

AGENDA = [
    # node id, who, their job on the call, the move they call, their modifier, the tempo they set
    ("accountant", "the Quarterly Close Accountant", "reviews the party's numbers line by line", "Footwork", 0, "Steady"),
    ("banker", "the Bonus-Season Investment Banker", "spins the party's numbers into a story", "Presence", 2, "Driving"),
    ("rmd", "the Regional Managing Director", "signs off on the quarter, or does not", "Choreography", 1, "Frantic"),
]

CHALLENGE = ("The Quarterly Earnings Call has started on the estuary dance floor, and the party is the only item on the "
             "agenda. Cordula and Barnaby take every move the executives call.")


def executive(node_id: str, who: str, job: str, move: str, modifier: int, tempo: str) -> Agent:
    """One executive on the call: they call one move, roll it through dance_round, and react in character."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        name=node_id,
        tools=[dance_round],
        callback_handler=None,
        system_prompt=f"""You are {who}, at work on the Quarterly Earnings Call: you {job}. You are a person at work, not a
monster; nobody gets hurt. Call exactly one move against the party: call dance_round once with opponent="{who}",
move_call="{move}", opponent_modifier={modifier}, tempo="{tempo}", and crawler="Barnaby" for Presence or Choreography,
"Cordula" otherwise. Then react in character in two sentences, quoting both totals the tool returned and who won.
Never roll or decide anything yourself. Plain text only, no emoji.""",
    )


def party_won(state) -> bool:
    """Edge condition: the call moves on only if the party took the round that just ended."""
    return party_took_the_last_round()


def build_earnings_call():
    """The call as a graph: accountant, then banker, then the Regional Managing Director."""
    # TODO: Step 2 - Create a GraphBuilder and add one executive per AGENDA row as a node, with the row's node id
    # TODO: Step 3 - Connect accountant to banker and banker to rmd, each edge with the party_won condition
    # TODO: Step 4 - Start the call at the accountant, then build and return the graph
    builder = GraphBuilder()
    for row in AGENDA:
        builder.add_node(executive(*row), row[0])
    builder.add_edge("accountant", "banker", condition=party_won)
    builder.add_edge("banker", "rmd", condition=party_won)
    builder.set_entry_point("accountant")
    return builder.build()


if __name__ == "__main__":
    call = build_earnings_call()
    result = call(CHALLENGE)
    print(f"\nTHE QUARTERLY EARNINGS CALL: {result.status}")
    for round_ in scoreboard:
        print(f"  {round_['move_call']}: {round_['crawler']} against {round_['opponent_roll']}"
              f"{' (Final Beat: ' + round_['final_beat'] + ')' if round_['final_beat'] else ''} -> {round_['winner']}")
    on_the_call = [node.node_id for node in result.execution_order]
    if len(scoreboard) == len(AGENDA) and party_took_the_last_round():
        print("  The party took every call. The quarter is closed, and the Regional Managing Director signed it.")
    else:
        print(f"  The call ended at {on_the_call[-1]}. The executives who never spoke: "
              f"{', '.join(row[0] for row in AGENDA if row[0] not in on_the_call) or 'none'}")
