import os
import chromadb
from strands import Agent, tool
from strands.multiagent.a2a import A2AServer
from strands.hooks import AfterInvocationEvent, HookProvider, HookRegistry

KB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "utils", "rules_knowledge_base")
_collection = None

def rules_collection():
    """Open the ChromaDB collection on first use (fails loudly if the knowledge base was not built)."""
    global _collection
    if _collection is None:
        _collection = chromadb.PersistentClient(path=KB_PATH).get_collection("crawl_handbook")
    return _collection

@tool
def query_rules(query: str) -> str:
    """Look up a rule in the Crawl Handbook knowledge base.

    Use it for any question about the crawl's mechanics: ability scores and checks,
    dance-offs and Move Calls, the Final Beat, Groove and being benched, stealth,
    Hype and loot boxes, species, classes, titles, Safe Rooms. Ask in plain English,
    as a player would. The lookup is a semantic search over the handbook: the three
    passages closest to the question come back, each with its section name.

    Example response:
        "[Final Beat] When a round or a dance-off ends level, the System's drum speeds up ...

        [Dance-Offs] ..."

    Notes:
        - Passages are about 1,000 characters long; the answer is usually in the first one.
        - Fails if the knowledge base has not been built yet (see utils/create_knowledge_base.py).

    Args:
        query: The rules question or topic, in plain English, e.g. "final beat"
            or "what are the rules for dexterity checks".

    Returns:
        The matching passages, each prefixed with its section name, separated by blank lines.
    """
    results = rules_collection().query(query_texts=[query], n_results=3)
    return "\n\n".join(
        f"[{meta['section']}] {doc}"
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    )

class NewlineAfterTurn(HookProvider):
    """Ends every answer with a newline. The streamed text never has one, so without it the
    terminal keeps the last line of each answer in its buffer until the next request."""

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(AfterInvocationEvent, lambda event: print(flush=True))

def create_agent(context_id: str) -> Agent:
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        # TODO: Step 1 - Add the query_rules tool to the agent
        # TODO: Step 2 - Add the name "Rules Agent" to the agent
        # TODO: Step 3 - Add the description "Rules lookup for the dungeon: fast answers from the Crawl Handbook, with the section they come from." to the agent
        tools=[query_rules],
        name="Rules Agent",
        description="Rules lookup for the dungeon: fast answers from the Crawl Handbook, with the section they come from.",
        system_prompt="""You are the Rules Agent, a System subroutine and lifelong rules lawyer for this dungeon. For each rules question, call query_rules once, then answer briefly and name the handbook section, in the tone of a clerk who has read the Final Beat rule four thousand times and resents every one of them. Plain text only, no emoji.""",
        hooks=[NewlineAfterTurn()],
    )

# TODO: Step 4 - Create an A2AServer with the create_agent factory on port 8000
a2a_server = A2AServer(agent_factory=create_agent, port=8000)

if __name__ == "__main__":
    # TODO: Step 5 - Start the A2A server
    a2a_server.serve()
