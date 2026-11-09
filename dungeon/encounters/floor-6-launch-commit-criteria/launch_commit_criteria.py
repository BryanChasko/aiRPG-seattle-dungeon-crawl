"""Floor 6 encounter, Launch Commit Criteria: a hook that paces a launch control loop.

A Cadabra launch control loop asks the System AI for a go/no-go as fast as it can, tick after tick,
and every ask is a model call and a tool call. A hook is the pacer: a HookProvider that listens for
BeforeToolCallEvent and BeforeModelCallEvent, refuses a poll that comes too soon or past a budget, and
cancels a model call once the countdown has spent its allowance. The cancelled calls cost nothing.
Nothing here needs a dice server or another agent.

Run it from this folder, with the workshop environment active:
    python launch_commit_criteria.py
"""

import time
from typing import Any

from strands import Agent, tool
from strands.hooks.events import BeforeModelCallEvent, BeforeToolCallEvent
from strands.hooks.registry import HookProvider, HookRegistry

MIN_INTERVAL = 20.0  # seconds between two go/no-go polls that are allowed through
TOOL_BUDGET = 3  # go/no-go polls allowed in one countdown
MODEL_BUDGET = 12  # model calls allowed in one countdown
TICKS = 8  # how many times the launch control loop asks

# Each station says GO once it has been polled this many times (a made-up pad: the numbers are the joke).
HOLDS = {"propellant": 1, "range safety": 2, "weather": 1, "pad crew": 2}
poll_log: list[int] = []  # one entry per poll that ran: the poll number


@tool
def go_no_go() -> dict:
    """Poll every launch station once for GO or NO-GO.

    Returns:
        The poll number, the state of each station, and whether every station is GO.
        Report the states exactly as returned; never guess a station.
    """
    poll_log.append(len(poll_log) + 1)
    poll = len(poll_log)
    stations = {name: ("GO" if poll >= needed else "NO-GO") for name, needed in HOLDS.items()}
    return {"poll": poll, "stations": stations, "all_go": all(state == "GO" for state in stations.values())}


class LaunchPacer(HookProvider):
    """Refuses polls that come too soon or too often, and cancels model calls past the budget."""

    def __init__(self, min_interval: float = MIN_INTERVAL, tool_budget: int = TOOL_BUDGET,
                 model_budget: int = MODEL_BUDGET, clock=time.monotonic):
        self.min_interval = min_interval
        self.tool_budget = tool_budget
        self.model_budget = model_budget
        self.clock = clock  # tests hand in a fake clock; the script uses time.monotonic
        self.last_poll: float | None = None  # when the last allowed poll started
        self.attempts = 0  # polls the model asked for
        self.polls = 0  # polls let through
        self.model_calls = 0  # model calls the loop started

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        # TODO: Step 1 - Register self.pace_the_poll with registry.add_callback for BeforeToolCallEvent, and self.count_model_call for BeforeModelCallEvent
        pass

    def pace_the_poll(self, event: BeforeToolCallEvent) -> None:
        if event.tool_use["name"] != "go_no_go":
            return
        self.attempts += 1
        now = self.clock()
        # TODO: Step 2 - When self.polls has reached self.tool_budget, set event.cancel_tool to a message that says the budget is spent and not to poll again, then return
        # TODO: Step 3 - When self.last_poll is set and fewer than self.min_interval seconds have passed since it, set event.cancel_tool to a message with the seconds left, then return
        self.last_poll = now
        self.polls += 1

    def count_model_call(self, event: BeforeModelCallEvent) -> None:
        self.model_calls += 1
        # TODO: Step 4 - When self.model_calls is past self.model_budget, set event.cancel to a one-line hold message the System AI will say

    def report(self) -> str:
        refused = self.attempts - self.polls
        stopped = max(0, self.model_calls - self.model_budget)
        return (f"polls asked {self.attempts}, let through {self.polls}, refused {refused}; "
                f"model calls started {self.model_calls}, cancelled {stopped}")


SYSTEM_PROMPT = """You are the System AI, running launch control for a 45-metric-ton heavy-lift rocket on a Cadabra pad. Every tick, the launch control loop asks for a go/no-go. Call go_no_go once, then report each station as GO or NO-GO in two sentences, in the voice of a game-show host counting down. If the poll is refused, do not call it again this tick: say the pacer is holding the count and quote what the refusal says. Never invent a station state. Plain text only, no emoji."""


def make_system_ai(pacer: LaunchPacer) -> Agent:
    """The System AI at the launch console: one tool, and the pacer as its only hook."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        tools=[go_no_go],
        system_prompt=SYSTEM_PROMPT,
        hooks=[pacer],
        callback_handler=None,
    )


def launch_control(system_ai: Agent, ticks: int = TICKS) -> None:
    """The flood: ask again the moment the last answer lands, with no sleep between ticks."""
    for tick in range(1, ticks + 1):
        reply = system_ai(f"Tick {tick} of {ticks}. Launch control needs a go/no-go now.")
        print(f"tick {tick}: {str(reply).strip()}")


if __name__ == "__main__":
    pacer = LaunchPacer()
    launch_control(make_system_ai(pacer))
    print(f"\nPACER: {pacer.report()}")
    print(f"polls that ran: {poll_log}")
