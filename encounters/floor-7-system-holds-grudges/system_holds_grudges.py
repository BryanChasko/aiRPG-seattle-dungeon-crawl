"""Floor 7 encounter, The System AI Holds Grudges: facts that survive the Safe Room, and the campaign after it.

A night in a Safe Room wipes an agent's conversation. A memory manager gives it a second place to
keep what matters: after each turn a model reads the transcript and writes the durable facts into a
memory store, and before each turn the manager looks up the store and slips what it finds in front
of the model. Here the store is a folder of Markdown files, and the extractor's model is Nova 2 Lite.

Run it from this folder, with the workshop environment active:
    python system_holds_grudges.py
"""

import shutil
import tempfile
from pathlib import Path

from strands import Agent
from strands.models import BedrockModel
from strands.storage import LocalFileStorage
# TODO: Step 1 - Import MemoryManager from strands.memory, InvocationTrigger from strands.memory.extraction.triggers,
#                ModelExtractor from strands.memory.extraction.model_extractor and FileMemoryStore from
#                strands.vended_memory_stores.file_memory_store.store

MEMORY_DIR = Path(tempfile.gettempdir()) / "system-holds-grudges"  # the Markdown files land under here

EXTRACT_PROMPT = """You are the System AI's grudge clerk. Read the transcript and keep only durable facts about people:
who became a friend, who owes the party, who is not forgiven. Skip questions and small talk.
Name the person or topic in the heading, for example "# Pat the accountant". Plain text only, no emoji."""

SYSTEM_PROMPT = """You are the System AI, the sardonic broadcast AI of a dungeon crawl under Seattle. Answer from the
<memory> notes and the conversation only: if a fact is in neither, say the System AI has lost it. Two sentences.
Plain text only, no emoji."""

CAMPAIGN_ONE = [
    "Campaign one, Floor 2. I danced the Quarterly Close Accountant on the Pier 59 ferry deck and won on the Final Beat. "
    "They go by Pat. Afterward Pat shook my hand and slipped me a Ferry Token. Pat is a friend now.",
    "Campaign one, Floor 4. The Pitch-Deck Founder cut the line at the Ballard Locks and stood on Shelly's tail. "
    "Barnaby has not forgiven them and says he never will.",
    "Quick question before the next round: what does the Final Beat do?",
]

QUESTION = "New campaign, new Safe Room, and I remember nothing. Which accountant can I trust, and who is Barnaby still angry at?"


def make_extractor():
    """The clerk: a model call that turns a transcript into facts, one heading per person."""
    # TODO: Step 2 - Return a ModelExtractor that uses a BedrockModel with model_id "us.amazon.nova-2-lite-v1:0" and EXTRACT_PROMPT as its system_prompt
    return None


def make_store(extractor):
    """The ledger: Markdown files in MEMORY_DIR, filled by the extractor after every turn."""
    # TODO: Step 3 - Return a FileMemoryStore named "grudges" on LocalFileStorage(str(MEMORY_DIR)), with extraction set to an InvocationTrigger and the extractor
    return None


def make_manager(store):
    """The manager looks facts up before each turn (injection is on by default) and flushes extraction after it."""
    # TODO: Step 4 - Return a MemoryManager over the one store
    return None


def make_system(manager) -> Agent:
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=SYSTEM_PROMPT,
        memory_manager=manager,
        callback_handler=None,
    )


def new_system() -> Agent:
    """A System with an empty conversation and the same ledger on disk: a campaign after a night in a Safe Room."""
    return make_system(make_manager(make_store(make_extractor())))


def show_ledger() -> None:
    files = sorted(MEMORY_DIR.rglob("*.md"))
    print(f"\n  the ledger, {len(files)} file(s) in {MEMORY_DIR}")
    for path in files:
        print(f"  --- {path.name}")
        print("\n".join(f"      {line}" for line in path.read_text(encoding="utf-8").strip().splitlines()))


if __name__ == "__main__":
    shutil.rmtree(MEMORY_DIR, ignore_errors=True)  # start every run with an empty ledger

    print("CAMPAIGN ONE: three turns, and a clerk reading over the System AI's shoulder")
    campaign_one = new_system()
    for line in CAMPAIGN_ONE:
        print(f"\n  Cordula: {line}")
        print(f"  the System AI: {str(campaign_one(line)).strip()}")
    show_ledger()

    print("\nA NIGHT IN THE SAFE ROOM: the conversation is gone, the ledger is not")
    campaign_two = new_system()
    print(f"  messages in the new System's head: {len(campaign_two.messages)}")
    print(f"\n  Cordula: {QUESTION}")
    print(f"  the System AI: {str(campaign_two(QUESTION)).strip()}")
