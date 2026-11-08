"""Floor 8 encounter, The Grudge Ledger in the Cloud: the System's grudges, kept in a Bedrock knowledge base memory store.

On Floor 7 the System learned to hold a grudge. A grudge kept on one machine dies with the machine. Here each grudge is
written as a document into a managed Amazon Bedrock knowledge base through a memory store, and a Memory Manager hands
the System the ones that match what the player is doing, before every model call. Run it once to write, once more to
ask: the second run is a different process that remembers.

Needs a knowledge base called grudges (the page creates it). Run it from this folder, with the workshop environment active:
    GRUDGE_KB_ID=<id> GRUDGE_DATA_SOURCE_ID=<id> GRUDGE_BUCKET=<bucket> python grudge_ledger.py write
    GRUDGE_KB_ID=<id> GRUDGE_DATA_SOURCE_ID=<id> GRUDGE_BUCKET=<bucket> python grudge_ledger.py ask
"""

from __future__ import annotations

import asyncio
import os
import sys

from strands import Agent
# TODO: Step 1 - Import MemoryManager from strands.memory and BedrockKnowledgeBaseStore from strands.vended_memory_stores.bedrock_knowledge_base
from strands.memory import MemoryManager
from strands.vended_memory_stores.bedrock_knowledge_base import BedrockKnowledgeBaseStore

GRUDGES = [  # who, and what is not forgiven
    ("the Pitch-Deck Founder", "stood on Shelly's tail at the Ship Canal locks, and Barnaby wants it in ink"),
    ("the Quarterly Close Accountant", "lost a Footwork round to Cordula by four and has not forgotten the margin"),
    ("the Bonus-Season Investment Banker", "was called a story, not a number, by Barnaby, and is rehearsing a reply"),
]
VISIT = "The Quarterly Close Accountant steps back onto the dance floor and eyes the party. Greet them."


def make_store() -> BedrockKnowledgeBaseStore:
    """The grudges knowledge base as a memory store, writable, with every grudge filed under the party."""
    # TODO: Step 2 - Return a BedrockKnowledgeBaseStore named "grudges", scope "party", writable=True; its config names the MANAGED knowledge base GRUDGE_KB_ID, an S3 data source GRUDGE_DATA_SOURCE_ID and the s3 bucket GRUDGE_BUCKET with prefix "grudges/"
    return BedrockKnowledgeBaseStore(
        config={
            "knowledge_base_id": os.environ["GRUDGE_KB_ID"],
            "knowledge_base_type": "MANAGED",
            "data_source_type": "S3",
            "data_source_id": os.environ["GRUDGE_DATA_SOURCE_ID"],
            "s3": {"bucket": os.environ["GRUDGE_BUCKET"], "prefix": "grudges/"},
        },
        name="grudges",
        description="Grudges between the party and the opponents they have met",
        scope="party",
        writable=True,
    )


def remember(store: BedrockKnowledgeBaseStore, opponent: str, grudge: str):
    """File one grudge in the ledger, with the opponent as metadata."""
    # TODO: Step 3 - Run store.add(...) with asyncio.run: the text is the opponent and the grudge, the metadata is {"opponent": opponent}
    return asyncio.run(store.add(f"{opponent} {grudge}", metadata={"opponent": opponent}))


def recall(store: BedrockKnowledgeBaseStore, question: str):
    """Search the ledger. Each entry has .content and .metadata."""
    # TODO: Step 4 - Run store.search(question) with asyncio.run and return the entries
    return asyncio.run(store.search(question))


def make_system(store: BedrockKnowledgeBaseStore) -> Agent:
    """The System, with the ledger behind it."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt="""You are the System, the petty, theatrical game-show host of Dungeon Crawl: Seattle. You keep grudges on behalf
of the people the party has beaten: when a grudge from your memory fits the moment, work it into your line, in one or two
sentences. Nobody is ever hurt; a grudge is a dance-off waiting to happen. Plain text only, no emoji.""",
        # TODO: Step 5 - Give the agent memory_manager=MemoryManager(stores=[store], add_tool_config=True)
        memory_manager=MemoryManager(stores=[store], add_tool_config=True),
        callback_handler=None,
    )


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "ask"
    ledger = make_store()
    if mode == "write":
        for who, grudge in GRUDGES:
            print(f"filed: {who}: {remember(ledger, who, grudge).document_id}")
        print("Give the knowledge base a minute, then: python grudge_ledger.py ask")
    else:
        for entry in recall(ledger, "who holds a grudge about Footwork"):
            print(f"remembered: {entry.content} (score {entry.metadata.get('_relevance_score')})")
        print(f"\nSYSTEM: {str(make_system(ledger)(VISIT)).strip()}")
