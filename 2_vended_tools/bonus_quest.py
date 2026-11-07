import os
from strands import Agent
# TODO: Step 1 - Import shell and file_editor from strands.vended_tools
# TODO: Step 2 - Import HumanInTheLoop from strands.vended_interventions.hitl

arcane_scribe = Agent(
    model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
    # TODO: Step 1 - Add the shell and file_editor tools to your agent
    # TODO: Step 2 - Ask for your approval before each tool call with HumanInTheLoop in stdio mode
    system_prompt=f"""You are Kiro the Doomsday Scripter, a crawler whose class treats code as demolition magic.
    When asked to create spells (code), you inscribe them on scrolls (files) in the directory {os.getcwd()}
    and then cast them, narrating every step as if the scroll might detonate. It will not. Probably."""
)

response = arcane_scribe("Create a magical scroll that generates the first 10 numbers of the Fibonacci sequence and demonstrate its power!")
