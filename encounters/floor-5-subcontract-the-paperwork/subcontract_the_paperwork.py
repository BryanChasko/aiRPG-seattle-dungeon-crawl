"""Floor 5 encounter, Subcontract the Paperwork: the Narrator hires a one-off clerk for the party's forms.

On Floor 5 the Narrator calls agents that run in their own terminals. A subagent tool is lighter: the
Narrator writes the task, Strands builds a fresh child agent for that one call, the child works in its
own context and hands back a report, and then it is gone. You decide what the clerk may be: its rules,
its tools and its model. Left alone, a clerk takes whatever model its parent runs, so this file pins
Amazon Nova 2 Lite on the clerk itself.

Run it from this folder, with the workshop environment active:
    python subcontract_the_paperwork.py
"""

from __future__ import annotations

from strands import Agent, tool
# TODO: Step 1 - Import make_subagent from strands.vended_tools.subagent.subagent, and Fixed and Preset from strands.multiagent.spec

CLERK_RULES = """You are a one-off clerk hired by the System AI to file the party's paperwork. You work from the task as written and cannot ask questions.
Return a tidy form: a title line, one line per item, and a total line. Every sum goes through the add_up tool; never add numbers yourself.
You are a person at work, not a monster, and a little proud of your stamp. Plain text only, no emoji."""

PAPERWORK = """File the party's Ferry Token expense report for the run to Bainbridge Island.
Cordula bought 4 tokens for the crew. Barnaby bought 3, paid in loose change from his collar. Chonks bought 2 and ate one.
Shelly's siphon is listed as a line item the System AI never finishes. Total the tokens bought and report the form."""


@tool
def add_up(numbers: list[int]) -> int:
    """Add a list of whole numbers and return the total. Use it for every sum.

    Args:
        numbers: The numbers to add, for example [4, 3, 2].

    Returns:
        The total. Report it as given; never add the numbers yourself.
    """
    return sum(numbers)


def make_clerk_tool():
    """The tool the Narrator calls to hire a clerk for one task."""
    # TODO: Step 2 - Build the tool with make_subagent: name hire_clerk, one preset "clerk" with the CLERK_RULES instructions and only the add_up tool, and instructions=Fixed() so the model cannot rewrite them
    # TODO: Step 3 - Pin the clerk's model in the same call with model=Fixed(...) set to Amazon Nova 2 Lite, so it never falls back to the parent's
    return None


def make_narrator(clerk_tool) -> Agent:
    """The Narrator, with the clerk tool and the calculator the clerk borrows."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        # TODO: Step 4 - Give the Narrator the add_up tool and the clerk_tool
        tools=[],
        callback_handler=None,
        system_prompt="""You are the System AI. When the party has paperwork, hire a clerk with hire_clerk, pass it the whole task, then report the clerk's form to the Crawler in two sentences and name the total. You never do the filing yourself. Plain text only, no emoji.""",
    )


def clerks_hired(narrator: Agent) -> int:
    """How many times the Narrator called hire_clerk this run."""
    return sum(1 for m in narrator.messages for b in m["content"] if b.get("toolUse", {}).get("name") == "hire_clerk")


if __name__ == "__main__":
    narrator = make_narrator(make_clerk_tool())
    print(narrator(PAPERWORK))
    print(f"\nclerks hired: {clerks_hired(narrator)}")
