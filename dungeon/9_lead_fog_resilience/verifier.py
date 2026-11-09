"""Floor 9, Part 1: catch the fog before it reaches the table.

The lead fog makes the System AI misremember: the Narrator states handbook
facts that are not in the handbook. A verifier agent re-checks every claim
against the handbook passages and returns a typed verdict, so a confabulated
Move Call never reaches the dance floor.
"""

from pydantic import BaseModel, Field

from strands import Agent
from strands.models import BedrockModel


# TODO: Part 1 Step 1 - Define the Verdict model: supported (bool) plus the
# section names that support the claim (list of str, may be empty when the
# claim is unsupported).
class Verdict(BaseModel):
    """Whether a Narrator claim is supported by the handbook, and by what."""

    raise NotImplementedError("TODO: Part 1 Step 1 - define supported and citations")


# TODO: Part 1 Step 2 - Create the verifier agent: Amazon Nova 2 Lite, a system
# prompt that says it checks claims against quoted handbook passages and never
# uses outside knowledge, and the Verdict model as its structured output.
def create_verifier() -> Agent:
    """Build the verifier agent. Runs on Amazon Nova 2 Lite."""
    raise NotImplementedError("TODO: Part 1 Step 2 - build the verifier agent")


# TODO: Part 1 Step 3 - Verify one claim: ask the verifier whether the claim
# follows from the passages, and return its structured Verdict.
def verify_claim(claim: str, passages: list[str]) -> Verdict:
    """Check a single Narrator claim against handbook passages."""
    raise NotImplementedError("TODO: Part 1 Step 3 - verify the claim")
