"""Floor 8 encounter, Range Safety Officer Protocol: a termination that cannot fire until a person says so.

Cadabra's flight termination system can end a flight, or end a run. Its range control is the System AI
with one tool, flight_termination. The tool is the commitment, so the tool itself stops and asks: a
Range Safety Officer holds two keys, ARM and DESTRUCT, and the tool raises one interrupt per key. A
standing order pre-signs the answer for routine targets, so a stray delivery drone never waits on anyone.

This is the tool side of the interrupt API: tool_context.interrupt inside the tool, two interrupts in
one tool call, a preemptive response, and a loop that answers every interrupt a paused turn reports.

Run it from this folder, with the workshop environment active:
    python range_safety_officer.py --drill     # a scripted stand-in for the model, no model call
    python range_safety_officer.py             # the System AI on Amazon Nova 2 Lite
"""

import sys

from strands import Agent, tool
from strands.types.tools import ToolContext

# Pre-signed answers, one per target. Story only: Cadabra's range rules belong to the crawl.
STANDING_ORDERS = {"stray delivery drone": "approve"}

FIRED: list[str] = []  # every target the flight termination system actually ended

PROMPT = """You are the System AI, running Cadabra's range control for the crawl. You hold one tool, flight_termination.
For each target named in the request, call flight_termination once with the target's exact name and the cause.
If the tool answers HOLD, report that the hold stands and do not call the tool for that target again.
If the tool answers TERMINATED, report the termination. One sentence per target.
Plain text only, no emoji."""


def standing_order(target: str) -> str | None:
    """The Range Safety Officer's pre-signed answer for this target, or None when a person must decide."""
    # TODO: Step 3 - Return the answer in STANDING_ORDERS for the target, stripped and lowercased, or None when there is none
    return None


def ask_key(tool_context: ToolContext, name: str, reason: dict, standing: str | None) -> str:
    """Ask the Range Safety Officer for one key. A standing order answers without a pause."""
    # TODO: Step 1 - Raise the interrupt with tool_context.interrupt(name, reason=reason, response=standing) and keep the answer
    answer = "approve"  # placeholder: nobody is asked yet
    return answer


@tool(context=True)
def flight_termination(target: str, cause: str, tool_context: ToolContext) -> str:
    """End a flight or a run. Needs both Range Safety Officer keys, unless a standing order covers the target.

    Args:
        target: The exact name of the flight or run to end.
        cause: Why the flight termination system wants it ended.
    """
    standing = standing_order(target)
    arm = ask_key(
        tool_context,
        "range_safety_arm",
        {"key": "ARM", "target": target, "cause": cause, "effect": "the termination is ready to fire"},
        standing,
    )
    if arm != "approve":
        return f"HOLD: the Range Safety Officer did not arm the termination of {target}."
    # TODO: Step 2 - Ask for the second key: call ask_key with the name "range_safety_destruct", a reason for key DESTRUCT, and standing
    destruct = "approve"  # placeholder: nobody is asked yet
    if destruct != "approve":
        return f"HOLD: the Range Safety Officer armed the termination of {target} and did not fire it."
    FIRED.append(target)
    print(f"FTS FIRED: {target}")
    return f"TERMINATED: {target}."


def make_director() -> Agent:
    """Range control: the System AI with the flight termination tool and nothing else."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=PROMPT,
        tools=[flight_termination],
        callback_handler=None,
    )


def answers_for(result, officer) -> list[dict]:
    """One interruptResponse block for every interrupt in a paused result."""
    # TODO: Step 4 - Return a list with one {"interruptResponse": {"interruptId": ..., "response": ...}} block per item in result.interrupts, the response from officer(interrupt)
    return []


def run_range(director: Agent, request: str, officer) -> str:
    """Send the request; while the turn is paused on a key, ask the officer and resume the same agent."""
    result = director(request)
    while result.stop_reason == "interrupt":
        result = director(answers_for(result, officer))
    return str(result)


def console_officer(interrupt) -> str:
    """The Range Safety Officer at the keyboard: type approve to turn the key, anything else is a hold."""
    reason = interrupt.reason
    print(f"\nRANGE SAFETY KEY {reason['key']}: {reason['target']}")
    print(f"  cause:  {reason['cause']}")
    print(f"  effect: {reason['effect']}")
    typed = input("  approve or hold? ").strip().lower()
    return "approve" if typed == "approve" else "hold"


def drill_officer(interrupt) -> str:
    """A scripted officer: turns the ARM key, holds the DESTRUCT key."""
    reason = interrupt.reason
    answer = "approve" if reason["key"] == "ARM" else "hold"
    print(f"RANGE SAFETY KEY {reason['key']}: {reason['target']} -> {answer}")
    return answer


DRILL_REQUEST = "Terminate the stray delivery drone, and terminate the Crawler party's run."


def make_drill_director() -> Agent:
    """The same range control, with a scripted model that calls the tool for both targets."""
    from range_control_drill import ScriptedModel

    director = make_director()
    director.model = ScriptedModel([
        [
            ("flight_termination", {"target": "stray delivery drone", "cause": "it left the delivery lane"}),
            ("flight_termination", {"target": "party run", "cause": "the party is ahead of the quarter's schedule"}),
        ],
        "Range control: the stray delivery drone is down. The hold on the party's run stands.",
    ])
    return director


if __name__ == "__main__":
    if "--drill" in sys.argv:
        print(run_range(make_drill_director(), DRILL_REQUEST, drill_officer))
    else:
        print(run_range(make_director(), DRILL_REQUEST, console_officer))
    print("\nFired:", FIRED or "nothing")
