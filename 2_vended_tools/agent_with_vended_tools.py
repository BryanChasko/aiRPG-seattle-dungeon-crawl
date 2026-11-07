from strands import Agent
# TODO: Step 1 - Import http_request from strands.vended_tools

agent = Agent(
    model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
    tools=[
        # TODO: Step 1 - Add the http_request tool to your agent
    ],
    system_prompt="""You are the System, the sardonic AI that runs this dungeon as a show for alien viewers. Address the player as Crawler and answer with petty, gleeful game-show flair, but get every number right: the audience checks.
    When asked about a spell or a monster, look it up on the Open5e API and answer from the data:
    - spells:   https://api.open5e.com/v2/spells/srd_<key>/
    - monsters: https://api.open5e.com/v2/creatures/srd_<key>/
    where <key> is the lowercase name with hyphens (e.g. fireball, adult-red-dragon).""",
)

result = agent("What does the Fireball spell do, and how much damage does it deal?")
