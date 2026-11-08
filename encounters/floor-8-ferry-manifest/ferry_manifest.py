"""Floor 8 encounter, The Ferry Manifest: build the Rules Agent from a configuration file.

A ferry leaves with a manifest: who is aboard, and nobody else. The Rules Agent gets one too. In 8.3 its name, model,
prompt and tool were Python; here they are a JSON file, rules-agent-manifest.json, and one call turns the file
into an agent. The manifest pins Amazon Nova 2 Lite, and this script refuses to sail with any other model on it.

Needs the knowledge base from 8.3. Run it from this folder, with the workshop environment active:
    KNOWLEDGE_BASE_RULES_ID=<id> python ferry_manifest.py
"""

import json
from pathlib import Path

# TODO: Step 1 - Import config_to_agent from strands.experimental.agent_config

NOVA = "us.amazon.nova-2-lite-v1:0"  # Amazon Nova 2 Lite, US cross-Region inference profile
MANIFEST = Path(__file__).resolve().parent / "rules-agent-manifest.json"
QUESTION = "How does the Final Beat work?"


def check_manifest(path: Path) -> dict:
    """Read the manifest and refuse to sail unless it pins Nova 2 Lite."""
    # TODO: Step 2 - Load the JSON from path and raise ValueError unless its "model" is NOVA; return the manifest
    return {}


def build_rules_agent(path: Path = MANIFEST):
    """The Rules Agent, built from the manifest. The manifest names its tool by a relative path: run from this folder."""
    check_manifest(path)
    # TODO: Step 3 - Return config_to_agent(str(path)) with callback_handler=None passed as a keyword argument
    return None


if __name__ == "__main__":
    manifest = check_manifest(MANIFEST)
    print(f"FERRY MANIFEST: {manifest['name']} aboard, model {manifest['model']}, tools {manifest['tools']}")
    agent = build_rules_agent()
    print(f"  boarded as {agent.name} with tools {agent.tool_names}")
    print(f"  {QUESTION}\n  {str(agent(QUESTION)).strip()}")
