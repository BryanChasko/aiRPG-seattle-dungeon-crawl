"""The Rules Agent's one tool, query_rules from Floor 8.3, in a file of its own so a manifest can name it.

Given code, nothing to complete. It reads the Crawl Handbook in the managed knowledge base you deployed in 8.3.
The knowledge base id comes from KNOWLEDGE_BASE_RULES_ID when the tool runs, not when the file is loaded.
"""

import os

import boto3
from strands import tool


def section_of(result: dict) -> str:
    """03-dance-offs.md -> Dance Offs: each handbook section is its own file in the bucket."""
    uri = result.get("location", {}).get("s3Location", {}).get("uri", "")
    stem = uri.rsplit("/", 1)[-1].removesuffix(".md").split("-", 1)[-1]
    return stem.replace("-", " ").title() or "Crawl Handbook"


@tool
def query_rules(query: str) -> str:
    """Look up a rule in the Crawl Handbook knowledge base.

    Use it for any question about the crawl's mechanics: ability scores and checks, dance-offs and Move Calls,
    the Final Beat, Groove and being benched, stealth, Hype and loot boxes, species, classes, titles, Safe Rooms.
    Ask in plain English, as a player would. The three passages closest to the question come back, each with
    its section name.

    Args:
        query: The rules question or topic, in plain English, e.g. "final beat".

    Returns:
        The matching passages, each prefixed with its section name, separated by blank lines.
    """
    knowledge_base = boto3.client("bedrock-agent-runtime")
    results = knowledge_base.retrieve(
        knowledgeBaseId=os.environ["KNOWLEDGE_BASE_RULES_ID"],
        retrievalQuery={"text": query},
        retrievalConfiguration={"managedSearchConfiguration": {"numberOfResults": 3}},
    )["retrievalResults"]
    return "\n\n".join(f"[{section_of(result)}] {result['content']['text']}" for result in results)
