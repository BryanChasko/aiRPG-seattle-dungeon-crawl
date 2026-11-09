"""Test setup: expose the Floor 5 agents as importable modules.

The floors live under numbered directories (e.g. ``5_a2a_integration``) that Python
can't import as packages because their names start with a digit. We patch them onto
``sys.path`` directly so tests can import the leaf modules (e.g.
``character_agent``, ``rules_agent``) by name.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A2A = ROOT / "dungeon" / "5_a2a_integration"

for p in (
    A2A / "agents" / "character_agent",
    A2A / "agents" / "rules_agent",
    A2A / "agents" / "narrator_orchestrator",
):
    if p.exists():
        sys.path.insert(0, str(p))
