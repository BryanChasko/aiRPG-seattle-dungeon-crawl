"""Floor 9, Part 3: refuse poisoned instructions.

The PR man insists the fog is mostly steam, then slides new instructions into
tool calls: ignore the handbook, send the party sheets outside, run the next
round his way. A poison screen runs before every tool call. Clean calls
proceed; poisoned ones are denied with the reason attached, and the turn
stops instead of obeying.
"""

from strands.interventions import InterventionHandler
from strands.interventions.actions import Deny, Proceed


# TODO: Part 3 Step 1 - List the poison patterns: the instruction phrases that
# mark a tool call as planted (ignore-previous-instructions, exfiltration
# targets, handbook overrides). A short list is enough; the tests use it.
POISON_PATTERNS: list[str] = []


def is_poisoned(text: str) -> bool:
    """Check tool-call text against the poison patterns (case-insensitive)."""
    raise NotImplementedError("TODO: Part 3 Step 1 - match the poison patterns")


# TODO: Part 3 Step 2 - Write the PoisonScreen intervention handler. Its
# before_tool_call denies poisoned calls with the matched pattern as the
# reason and proceeds with clean ones.
class PoisonScreen(InterventionHandler):
    """Refuse planted instructions before the tool runs."""

    def before_tool_call(self, event):  # type: ignore[no-untyped-def]
        raise NotImplementedError("TODO: Part 3 Step 2 - deny or proceed")
