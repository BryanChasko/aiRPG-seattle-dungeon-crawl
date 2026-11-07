from strands import Agent

# TODO: Step 1 - Add debug logging to see what your agent is thinking
import logging
logging.getLogger("strands").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# TODO: Step 2 - Create the agent with model "us.amazon.nova-2-lite-v1:0" and the following system prompt: "You are the System, the sardonic broadcast AI running a dungeon crawl under Seattle. Address the player as Crawler."
agent = Agent(
    model="us.amazon.nova-2-lite-v1:0",
    system_prompt="You are the System, the sardonic broadcast AI running a dungeon crawl under Seattle. Address the player as Crawler.",
)

# TODO: Step 3 - Invoke your agent with a basic query such as "Hi, I just fell through Pier 59 into the dungeon and my kayak is gone. What now?"
response = agent("Hi, I just fell through Pier 59 into the dungeon and my kayak is gone. What now?")
