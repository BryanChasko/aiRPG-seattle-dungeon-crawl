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

    # ANSWER:
    supported: bool = Field(description="True only when the quoted passages back the claim.")
    citations: list = Field(default_factory=list, description="Handbook section names quoted as evidence.")


VERIFIER_PROMPT = (
    "You check Narrator claims against quoted Crawl Handbook passages. "
    "A claim is supported only when a quoted passage says the same rule. "
    "Fog markers like ties going to the louder dancer or the drum deciding "
    "ties never appear in the handbook, so they can never support a claim. "
    "Reply with supported and the section names you quoted, nothing else."
)


# TODO: Part 1 Step 2 - Create the verifier agent: Amazon Nova 2 Lite, a system
# prompt that says it checks claims against quoted handbook passages and never
# uses outside knowledge, and the Verdict model as its structured output.
def create_verifier() -> Agent:
    """Build the verifier agent. Runs on Amazon Nova 2 Lite."""
    # ANSWER:
    model = BedrockModel(model_id="us.amazon.nova-2-lite-v1:0", max_tokens=1024)
    return Agent(model=model, system_prompt=VERIFIER_PROMPT, structured_output_model=Verdict)


# TODO: Part 1 Step 3 - Verify one claim: ask the verifier whether the claim
# follows from the passages, and return its structured Verdict.
def verify_claim(claim: str, passages: list) -> Verdict:
    """Check a single Narrator claim against handbook passages."""
    # ANSWER:
    agent = create_verifier()
    quoted = "\n".join("- " + p for p in passages)
    prompt = "Claim: " + claim + "\nPassages:\n" + quoted + "\nSupported?"
    result = agent(prompt)
    return result.structured_output
