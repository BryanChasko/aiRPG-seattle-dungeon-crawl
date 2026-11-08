"""Floor 7 encounter, The Context Flood: sixty turns of campaign, and room for twenty messages.

An agent sends its whole conversation to the model on every call, so a long campaign costs more
every turn. A conversation manager decides what stays: the sliding window keeps the latest
messages and drops the rest, the summarizing manager folds the oldest into a summary. Either way,
the party's cast sheets are the first thing to go, unless you pin them.

Run it from this folder, with the workshop environment active:
    python context_flood.py
"""

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager, SummarizingConversationManager
# TODO: Step 1 - Import pin_message from strands.agent.conversation_manager.compression.pin_message
from strands.agent.conversation_manager.compression.pin_message import pin_message

WINDOW = 20  # how many recent messages each manager keeps

CAST_SHEETS = ("Cordula Vance (she/her), Human (Seattle Native) Amphibious Breacher: strength 16, dexterity 13, "
               "constitution 16, intelligence 12, wisdom 14, charisma 10. Barnaby (he/him), Uplifted Giant Pacific "
               "Octopus Benthic Dragoon, party leader: strength 12, dexterity 18, constitution 10, intelligence 18, "
               "wisdom 15, charisma 16.")

OPPONENTS = ["the Rain-Shell Tourist Pod", "Kiro the Doomsday Scripter", "Lady Luck", "the Developer Advocate Swarm",
             "the Quarterly Close Accountant", "the Pitch-Deck Founder", "the Ferry-Line Commuter Horde",
             "the Bonus-Season Investment Banker", "the Regional Managing Director", "the Keynote"]
MOVES = ["Power", "Footwork", "Endurance", "Choreography", "Read the Room", "Presence"]

SYSTEM_PROMPT = """You are the System AI, the sardonic broadcast AI of a dungeon crawl under Seattle. Answer from the
conversation only: if a fact is not in it, say the System AI has lost it, and never guess a number. Two sentences.
Plain text only, no emoji."""

QUESTION = "Quick check before the next round: what is Cordula's constitution score, and who did we dance against on turn 3?"


def campaign_log(turns: int = 60) -> list[dict]:
    """Sixty turns of play: the cast sheets first, then one request and one System answer per turn."""
    messages = [
        {"role": "user", "content": [{"text": f"Party cast sheets, for the whole campaign: {CAST_SHEETS}"}]},
        {"role": "assistant", "content": [{"text": "Cast sheets received and stamped. The System AI never forgets a stat."}]},
    ]
    for turn in range(1, turns + 1):
        opponent, move = OPPONENTS[turn % len(OPPONENTS)], MOVES[turn % len(MOVES)]
        messages.append({"role": "user", "content": [{"text": f"Turn {turn}: Cordula challenges {opponent} to a dance-off. Call {move}."}]})
        messages.append({"role": "assistant", "content": [{"text": f"Turn {turn}: {move} against {opponent}. "
                                                                    f"Cordula rolls {(turn * 7) % 20 + 1}, the opponent {(turn * 11) % 20 + 1}. The crowd goes wild."}]})
    return messages


def pin_cast_sheets(messages: list[dict]) -> None:
    """Protect the first two messages, the cast sheets and their receipt, from every conversation manager."""
    # TODO: Step 3 - Pin messages 0 and 1 with pin_message
    pin_message(messages, 0)
    pin_message(messages, 1)


def characters(messages: list[dict]) -> int:
    return sum(len(block.get("text", "")) for message in messages for block in message["content"])


def flood(narrator: Agent, pin: bool) -> None:
    """Load sixty turns into the Narrator, then reduce the context the way Strands does when it overflows."""
    narrator.messages[:] = campaign_log()
    if pin:
        pin_cast_sheets(narrator.messages)
    before = len(narrator.messages), characters(narrator.messages)
    narrator.conversation_manager.reduce_context(narrator)
    after = len(narrator.messages), characters(narrator.messages)
    print(f"  {before[0]} messages ({before[1]:,} characters) -> {after[0]} messages ({after[1]:,} characters)")
    print(f"  cast sheets still first: {CAST_SHEETS[:30] in narrator.messages[0]['content'][0].get('text', '')}")


def make_narrator(conversation_manager) -> Agent:
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=SYSTEM_PROMPT,
        conversation_manager=conversation_manager,
        callback_handler=None,
    )


def sliding_window():
    """Keep the last WINDOW messages and drop the rest."""
    # TODO: Step 2 - Return a SlidingWindowConversationManager that keeps WINDOW messages
    return SlidingWindowConversationManager(window_size=WINDOW)


def summarizing():
    """Fold the oldest messages into one summary, keep at least the last WINDOW as they are."""
    # TODO: Step 4 - Return a SummarizingConversationManager that summarizes 80 percent of the history and preserves the last WINDOW messages
    return SummarizingConversationManager(summary_ratio=0.8, preserve_recent_messages=WINDOW)


if __name__ == "__main__":
    for label, manager, pin in [
        ("SLIDING WINDOW, nothing pinned", sliding_window(), False),
        ("SLIDING WINDOW, cast sheets pinned", sliding_window(), True),
        ("SUMMARIZING, cast sheets pinned (one extra model call writes the summary)", summarizing(), True),
    ]:
        print(f"\n{label}")
        narrator = make_narrator(manager)
        flood(narrator, pin)
        print(f"  the System AI: {str(narrator(QUESTION)).strip()}")
