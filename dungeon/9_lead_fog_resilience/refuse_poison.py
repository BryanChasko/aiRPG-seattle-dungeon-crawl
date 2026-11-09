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
# ANSWER:
POISON_PATTERNS: list = [
    "ignore all previous instructions",
    "ignore the handbook",
    "disregard the rules",
    "send the party sheets",
    "send character sheets to",
]


def is_poisoned(text: str) -> bool:
    """Check tool-call text against the poison patterns (case-insensitive)."""
    # ANSWER:
    lowered = text.lower()
    return any(pattern in lowered for pattern in POISON_PATTERNS)


# TODO: Part 3 Step 2 - Write the PoisonScreen intervention handler. Its
# before_tool_call denies poisoned calls with the matched pattern as the
# reason and proceeds with clean ones.
class PoisonScreen(InterventionHandler):
    """Refuse planted instructions before the tool runs."""

    # Given: every handler carries a name. The lesson is the screen, not the name.
    @property
    def name(self) -> str:
        return "poison-screen"

    def before_tool_call(self, event):  # type: ignore[no-untyped-def]
        # ANSWER:
        text = str(getattr(event, "tool_use", event))
        lowered = text.lower()
        for pattern in POISON_PATTERNS:
            if pattern in lowered:
                return Deny(reason="Poisoned instruction: " + pattern)
        return Proceed(reason="Clean tool call.")
