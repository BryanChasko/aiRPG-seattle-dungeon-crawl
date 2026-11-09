"""Floor 7 encounter, Static Fire on the Pad: one rocket test, three capabilities, composed as plugins and skills.

Cadabra is test-firing a heavy-lift rocket rated for 45 metric tons on the tidal flat below the
bluffs, and the range desk has three jobs at once: read the countdown, check the debris, make the hold call.
The first two are tools and a hook, packaged as one Plugin you write. The third is a skill: a block of
instructions the agent loads only when it needs them, served by the AgentSkills plugin. Both plug into the
same Agent through plugins=[...].

Run it from this folder, with the workshop environment active:
    python static_fire.py
"""

from strands import Agent, Skill
# TODO: Step 1 - Import AgentSkills and tool from strands, Plugin and hook from strands.plugins, and BeforeToolCallEvent from strands.hooks
from strands import AgentSkills, tool
from strands.hooks import BeforeToolCallEvent
from strands.plugins import Plugin, hook

EXCLUSION_RADIUS_M = 500  # nothing may be inside this radius of the pad at ignition

COUNTDOWN = {"t_minus_seconds": 180, "chamber_pressure_pct": 97, "propellant_load_pct": 100}
BEACH = [
    {"item": "a team-building kayak tour from Bellevue, six people in matching vests and one clipboard", "distance_m": 400},
    {"item": "a surveyor's tripod standing on the tidal flat", "distance_m": 900},
    {"item": "a parked Cadabra delivery drone, charging", "distance_m": 1200},
]
range_log: list[str] = []  # the name of every tool the range desk calls, in order

# A skill is a name, a one-line description and instructions. The agent sees only the name and description
# until it decides the skill fits, then loads the instructions with one tool call.
HOLD_CALL = Skill(
    name="hold-call",
    description="How to decide GO or HOLD on a static fire once the countdown and the debris check are in",
    instructions=(
        "Use this after read_countdown and debris_check have both returned. Never call GO on a guess.\n"
        "Call HOLD if any one of these is true: anything at all is inside the exclusion radius of 500 meters; "
        "chamber_pressure_pct is outside 90 to 105; propellant_load_pct is below 100. Otherwise call GO.\n"
        "Say the call in one line: HOLD or GO, then the single reason that decided it, quoting the number or the "
        "item exactly as the tool returned it. Never round a number and never soften a HOLD."
    ),
)
PAD_CALLOUT = Skill(
    name="pad-callout",
    description="How to word the range callout for the broadcast once the hold call is made",
    instructions=(
        "Open with the clock as T-minus M:SS, converted from t_minus_seconds (180 seconds is T-minus 3:00). "
        "Then the call, HOLD or GO, in capitals. Then one short sentence of reason. "
        "Three sentences at most: the audience is a galaxy of viewers and the pad is loud."
    ),
)


def pad_clock() -> dict:
    """The pad clock as it stands now."""
    return dict(COUNTDOWN)


def beach_scan(radius_m: int) -> list[dict]:
    """Everything on the beach and the water within radius_m meters of the pad."""
    return [thing for thing in BEACH if thing["distance_m"] <= radius_m]


# TODO: Step 2 - Write class RangeCrew(Plugin): name "range-crew", a @tool method read_countdown that returns pad_clock(), a @tool method debris_check(radius_m: int = EXCLUSION_RADIUS_M) that returns beach_scan(radius_m), and a @hook method note_call(self, event: BeforeToolCallEvent) that appends event.tool_use["name"] to range_log
class RangeCrew(Plugin):
    name = "range-crew"

    @tool
    def read_countdown(self) -> dict:
        """Read the pad clock: seconds to launch, chamber pressure and propellant load.

        Returns:
            t_minus_seconds, chamber_pressure_pct (the safe band is 90 to 105) and propellant_load_pct.
        """
        return pad_clock()

    @tool
    def debris_check(self, radius_m: int = EXCLUSION_RADIUS_M) -> list:
        """List everything on the beach and the water within radius_m meters of the pad.

        Args:
            radius_m: How far from the pad to look, in meters. The default is the exclusion radius.

        Returns:
            One entry per thing found, with its item and distance_m. An empty list means the radius is clear.
        """
        return beach_scan(radius_m)

    @hook
    def note_call(self, event: BeforeToolCallEvent):
        range_log.append(event.tool_use["name"])

# TODO: Step 3 - Build the skills plugin: AgentSkills with skills=[HOLD_CALL, PAD_CALLOUT], as skills_plugin
skills_plugin = AgentSkills(skills=[HOLD_CALL, PAD_CALLOUT])

SYSTEM_PROMPT = """You are the range desk for a static fire on the pad below the bluffs, a subroutine of the System AI.
A hold call needs both numbers: read the countdown and check the debris before you call anything, and
activate the skills that fit the call. Quote every number and every item exactly as the tools return them.
Plain text only, no emoji."""

CALL = ("T-minus three minutes on the heavy-lift rocket rated for 45 metric tons. "
        "Read the countdown, check the debris inside the exclusion radius, then make the hold call.")


def make_director(crew: "RangeCrew") -> Agent:
    """The range desk: Amazon Nova 2 Lite with the crew plugin and the skills plugin."""
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        system_prompt=SYSTEM_PROMPT,
        callback_handler=None,
        # TODO: Step 4 - Give the agent both plugins: plugins=[crew, skills_plugin]
        plugins=[crew, skills_plugin],
    )


if __name__ == "__main__":
    crew = RangeCrew()
    director = make_director(crew)
    result = director(CALL)
    print(f"\nRange desk: {str(result).strip()}")
    print(f"\ntools called, in order: {range_log}")
    print(f"skills activated: {skills_plugin.get_activated_skills(director)}")
