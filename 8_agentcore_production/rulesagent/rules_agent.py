import os
import boto3
from strands import Agent, tool
from strands.multiagent.a2a import A2AServer, StrandsA2AExecutor
from bedrock_agentcore.runtime import serve_a2a

# Set in agentcore.json (envVars), from the knowledge base id printed by agentcore status
KNOWLEDGE_BASE_ID = os.environ["KNOWLEDGE_BASE_RULES_ID"]
knowledge_base = boto3.client("bedrock-agent-runtime")

def section_of(result: dict) -> str:
    """03-dance-offs.md -> Dance Offs: each handbook section is its own file in the bucket."""
    uri = result.get("location", {}).get("s3Location", {}).get("uri", "")
    stem = uri.rsplit("/", 1)[-1].removesuffix(".md").split("-", 1)[-1]
    return stem.replace("-", " ").title() or "Crawl Handbook"

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
        - The answer is usually in the first passage.
        - Returns nothing until the ingestion of the knowledge base is complete.

    Args:
        query: The rules question or topic, in plain English, e.g. "final beat"
            or "what are the rules for dexterity checks".

    Returns:
        The matching passages, each prefixed with its section name, separated by blank lines.
    """
    # TODO: Step 1 - Retrieve the 3 passages closest to the query from the knowledge base and prefix each one with its section

def create_agent(context_id: str) -> Agent:
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        tools=[query_rules],
        name="Rules Agent",
        description="Rules lookup for the dungeon: fast answers from the Crawl Handbook, with the section they come from.",
        system_prompt="""You are the Rules Agent, a System subroutine and lifelong rules lawyer for this dungeon. For each rules question, call query_rules once, then answer briefly and name the handbook section, in the tone of a clerk who has read the Final Beat rule four thousand times and resents every one of them. Plain text only, no emoji.""",
        callback_handler=None,
    )

if __name__ == "__main__":
    # TODO: Step 2 - Serve the create_agent factory with serve_a2a on all interfaces, with the agent card of an A2AServer built on the same factory
    pass
