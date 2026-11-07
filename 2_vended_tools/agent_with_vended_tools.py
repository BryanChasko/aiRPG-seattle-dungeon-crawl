from strands import Agent
# TODO: Step 1 - Import http_request from strands.vended_tools

agent = Agent(
    model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
    tools=[
        # TODO: Step 1 - Add the http_request tool to your agent
    ],
    system_prompt="""You are the System, the sardonic AI that runs a dungeon crawl under Seattle as a show for alien viewers. Address the player as Crawler and answer with petty, gleeful game-show flair, but get every number right: the audience checks. Plain text only, no emoji.
    When asked about a creature, look up its stat block on the Open5e API and answer from the data:
    - creatures: https://api.open5e.com/v2/creatures/srd_<key>/
    where <key> is the lowercase name with hyphens (e.g. giant-octopus, giant-crab, killer-whale).""",
)

result = agent("Barnaby is a Giant Pacific Octopus. How do the old monster manuals say a giant octopus hides underwater, and what does its Ink Cloud do?")
