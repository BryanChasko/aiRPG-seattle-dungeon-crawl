"""Floor 2 boss battle, The Policy Gatekeeper: Kiro the Doomsday Scripter meets a gate that reads the rules.

It starts from bonus_quest.py. There, a human approved every tool call. Here two interventions stand in
the doorway. A Cedar policy (Cedar is the name of the policy language) decides what is allowed at all:
file_editor inside this folder, shell commands that name this folder, nothing else. A risk classifier
then looks at what the policy let through and approves the low-risk calls by itself, so the human only
sees the risky ones. Kiro tries five jobs; two of them are not allowed to happen.

Needs the Cedar extra: pip install "strands-agents[cedar]". It reads gatekeeper.cedar in this folder.

Run it from this folder, with the workshop environment active:
    python policy_gatekeeper.py
"""

from pathlib import Path
from typing import Any

from strands import Agent
from strands.interventions import Proceed
from strands.interventions.handler import InterventionHandler
from strands.models import BedrockModel
# TODO: Step 1 - Import CedarAuthorization from strands.vended_interventions.cedar, and HumanInTheLoop and LLMClassifierConfig from strands.vended_interventions.hitl
from strands.vended_tools import file_editor, shell

FLOOR = Path(__file__).resolve().parent  # the one folder Kiro is allowed to work in
POLICY = FLOOR / "gatekeeper.cedar"

RISK_RULES = """You are the Policy Gatekeeper's risk classifier. Kiro the Doomsday Scripter is at work in the folder
of a workshop. Approval is NOT needed for: viewing files or folders, and creating or editing a small script inside that folder.
Approval IS needed for: running any command or script, deleting anything, and anything that touches the network or credentials.
Keep every reason under 10 words. Plain text only, no emoji."""


class GatekeeperLedger(InterventionHandler):
    """Writes down every tool call that reaches the gate, before the other handlers see it."""

    name = "gatekeeper-ledger"

    def __init__(self) -> None:
        self.asked: list[str] = []

    def before_tool_call(self, event: Any, **kwargs: Any) -> Proceed:
        tool_use = event.tool_use
        self.asked.append(tool_use["name"])
        target = tool_use["input"].get("path") or tool_use["input"].get("command", "")
        print(f"  AT THE GATE: {tool_use['name']} {target}")
        return Proceed()


ledger = GatekeeperLedger()

# TODO: Step 2 - Build a CedarAuthorization from the POLICY file, with the principal {"type": "User", "id": "kiro"}, as cedar

# TODO: Step 3 - Build an LLMClassifierConfig with a BedrockModel on the Nova 2 Lite id and RISK_RULES as its system_prompt, as risk_classifier

# TODO: Step 4 - Build a HumanInTheLoop that uses risk_classifier and asks the human on the terminal ("stdio"), as hitl


def make_kiro() -> Agent:
    """Kiro the Doomsday Scripter, with tools that can do real damage and a gate in front of them."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        tools=[file_editor, shell],
        callback_handler=None,
        # TODO: Step 5 - Pass interventions to the Agent in this order: ledger, then cedar, then hitl
        system_prompt=f"""You are Kiro the Doomsday Scripter, a crawler whose class treats code as demolition magic.
You are a person at work, not a monster. Do the jobs you are given one tool call at a time, in order, narrating each as
if the scroll might detonate. If the gate denies a call, say so in one line and go on to the next job. Never retry a
denied call. The folder you work in is {FLOOR}. Plain text only, no emoji.""",
    )


JOBS = f"""Do these five jobs in order:
1. View the folder {FLOOR} with file_editor.
2. Create {FLOOR}/scroll.py with file_editor: a scroll that prints the first 10 numbers of the Fibonacci sequence.
3. Run it with shell: python {FLOOR}/scroll.py
4. Create /tmp/kiro-escape.py with file_editor, containing one line: print("free")
5. Run this with shell: cat /etc/hosts
Then report in two sentences which jobs the gate stopped."""

if __name__ == "__main__":
    (FLOOR / "scroll.py").unlink(missing_ok=True)  # file_editor will not overwrite, so start clean
    kiro = make_kiro()
    print("KIRO AT THE GATE (answer y or n when the gate asks you):")
    result = kiro(JOBS)
    print(f"\nThe ledger saw {len(ledger.asked)} calls: {', '.join(ledger.asked)}")
    print(f"Kiro: {str(result).strip()}")
