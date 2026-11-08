"""A scripted stand-in for the model, so the Range Safety Officer drill runs with no model call.

Not part of the lesson. It plays back a fixed list of turns through the real Strands agent loop:
a turn is either a list of (tool name, input) pairs the model "decides" to call, or a text reply.
"""

import json
from collections.abc import AsyncIterator
from typing import Any

from strands.models.model import Model


class ScriptedModel(Model):
    """A Model that replays its turns in order and repeats the last one when they run out."""

    def __init__(self, turns: list) -> None:
        self.turns = list(turns)
        self.played = 0
        self.config: dict[str, Any] = {"model_id": "scripted-drill"}

    def update_config(self, **model_config: Any) -> None:
        self.config.update(model_config)

    def get_config(self) -> Any:
        return self.config

    async def structured_output(self, output_model, prompt, system_prompt=None, **kwargs) -> AsyncIterator:
        raise NotImplementedError("the drill model gives no structured output")
        yield  # pragma: no cover

    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs) -> AsyncIterator:
        turn = self.turns[min(self.played, len(self.turns) - 1)]
        self.played += 1
        yield {"messageStart": {"role": "assistant"}}
        if isinstance(turn, str):
            yield {"contentBlockStart": {"start": {}}}
            yield {"contentBlockDelta": {"delta": {"text": turn}}}
            yield {"contentBlockStop": {}}
            yield {"messageStop": {"stopReason": "end_turn"}}
        else:
            for number, (name, tool_input) in enumerate(turn):
                tool_use_id = f"drill-{self.played}-{number}"
                yield {"contentBlockStart": {"start": {"toolUse": {"toolUseId": tool_use_id, "name": name}}}}
                yield {"contentBlockDelta": {"delta": {"toolUse": {"input": json.dumps(tool_input)}}}}
                yield {"contentBlockStop": {}}
            yield {"messageStop": {"stopReason": "tool_use"}}
        yield {"metadata": {"usage": {"inputTokens": 1, "outputTokens": 1, "totalTokens": 2}, "metrics": {"latencyMs": 1}}}
