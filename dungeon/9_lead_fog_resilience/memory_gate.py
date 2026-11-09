"""Floor 9, Part 2: gate the memory writes.

In the fog, memory writes go bad: a confabulated round result lands in the
conversation and every later turn builds on it. A hook watches each message
as it is added to the agent's history. Clean messages commit; fogged ones go
to quarantine, where the party reviews them instead of building on them.
"""

from strands.hooks import HookProvider, HookRegistry, MessageAddedEvent


# TODO: Part 2 Step 1 - List the fog markers: the words and phrases that never
# appear in a true handbook ruling (a short list is enough; the tests use it).
# ANSWER:
FOG_MARKERS: list = [
    "louder dancer",
    "mostly steam",
    "drum decides",
    "steam decides",
    "the fog agrees",
]


def _message_text(message) -> str:
    """Pull plain text out of an event message, whatever its shape."""
    if isinstance(message, str):
        return message
    if isinstance(message, dict):
        content = message.get("content", message)
        if isinstance(content, str):
            return content
        parts = []
        for block in content if isinstance(content, list) else [content]:
            if isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            else:
                parts.append(str(block))
        return " ".join(parts)
    return str(message)


# TODO: Part 2 Step 2 - Write the FogGate hook provider. Register a callback
# for MessageAddedEvent that appends clean messages to `committed` and fogged
# ones (any FOG_MARKERS hit, case-insensitive) to `quarantined`, with the
# reason attached.
class FogGate(HookProvider):
    """Gate memory writes: commit the clean, quarantine the fogged."""

    def __init__(self) -> None:
        self.committed: list = []
        self.quarantined: list = []

    # ANSWER:
    def _check(self, event: MessageAddedEvent) -> None:
        text = _message_text(event.message)
        for marker in FOG_MARKERS:
            if marker in text.lower():
                self.quarantined.append((text, "fog marker: " + marker))
                return
        self.committed.append(text)

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        # ANSWER:
        registry.add_callback(MessageAddedEvent, self._check)


# TODO: Part 2 Step 3 - Write the store_memory tool: it records its input in a
# module-level list and returns "stored". The gate watches the history, not the
# tool, so the tool itself stays dumb.
STORED: list = []


def store_memory(text: str) -> str:
    """Record a memory. The FogGate decides whether it counts."""
    # ANSWER:
    STORED.append(text)
    return "stored"
