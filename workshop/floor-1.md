# Floor 1: Agent Summoning

[Previous: Floor 0](floor-0.md) | [Dungeon map](README.md) | [Next: Floor 2](floor-2.md) <!-- floor-nav -->

![Floor 1: Agent Summoning](../images/floors/floor-1-1200x675.webp)

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Floor 1, Crawlers. You will now summon a living creature out of a string of English and one function call. The audience has money on the first thing it says. Be kind to it. It will not be kind to you."

## Floor Objective

Summon your first agent with Strands: a Narrator that answers an adventurer with nothing more than an `Agent`, a system prompt and one call. Along the way, turn on debug logging to see what happens between your code and the model.

Make sure you are at the root of Floor 1 in your terminal:

```bash
cd aiRPG-seattle-dungeon-crawl/1_strands_basics
```

Open and modify the `simple_agent.py` file. You'll complete the TODO comments to create your first AI agent.

## Step 1: Enable Debug Logging

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "DEBUG logging shows every request I send to the model and every word that streams back. It is the closest you will get to reading my mind. You will not enjoy it."

```python
# TODO: Step 1 - Add debug logging to see what your agent is thinking
```

Before creating your agent, enable debug logging to observe the agent's internal reasoning process. Check the documentation on how to enable debug logging.

There are different log levels: DEBUG, INFO, WARNING, ERROR, and CRITICAL. We recommend DEBUG as a starting point: it is verbose, but it is the only level where Strands shows the request sent to the model and the response streamed back. Higher levels such as INFO stay almost silent, so raise the level once you have seen enough.

## Step 2: Create Your Agent

> <img src="../images/icons/item-96x96.webp" alt="Item" width="28" height="28"> **ITEM ACQUIRED: [System Prompt]**
>
> One string that decides who your agent is. Write it carelessly and your agent turns careless. Write it in the voice of the System and it turns insufferable. Recommended.

```python
# TODO: Step 2 - Create the agent with model "us.amazon.nova-2-lite-v1:0" and the following system prompt: "You are the System, the sardonic broadcast AI running a dungeon crawl under Seattle. Address the player as Crawler."
```

The system prompt defines your agent's role, personality, and knowledge base. Check the documentation on how to create a system prompt.

Pick the model yourself: without a `model`, Strands defaults to a third-party Claude model on Amazon Bedrock. This crawl runs on Amazon Nova 2 Lite, a first-party Amazon model, through the US cross-Region inference profile `us.amazon.nova-2-lite-v1:0`, so pass `model="us.amazon.nova-2-lite-v1:0"` to `Agent(...)`. Every later floor already passes it in the given code. To try another model later, see the Amazon Bedrock model provider page.


> <img src="../images/icons/warning-96x96.webp" alt="Warning" width="28" height="28"> **SYSTEM WARNING:** Your AWS account must be allowed to invoke Amazon Nova 2 Lite in us-west-2. If the first call fails with AccessDeniedException, open the Amazon Bedrock console, check Model access for Nova 2 Lite, and try again.

## Step 3: Test Your Agent

```python
# TODO: Step 3 - Invoke your agent with a basic query such as "Hi, I just fell through Pier 59 into the dungeon and my kayak is gone. What now?"
```

Time to test your agent. Check the documentation on how to invoke your agent.

## Step 4: Testing Your Creation

> <img src="../images/icons/floor-boss-96x96.webp" alt="Floor boss" width="28" height="28"> **FLOOR BOSS:** Your own agent. It has never spoken before. Run the script and survive its first opinion of you.

Once you've completed all TODOs, run your script:

```bash
python simple_agent.py
```

If successful, your Narrator agent should answer in the System's voice and set the scene under the Seattle waterfront.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **SYSTEM DESIGN, LAYER 1: THE INTERFACE VOICE.** A LitRPG System talks in notifications, and how they sound sets the genre. A cold, analytic System makes a survival story; a cruel one makes horror; ours is a game-show host. Change one sentence of your system prompt (try "You are a calm, clinical survival System") and run the script again: same model, same question, a different book. See [The System](world/the-system.md#1-origin-and-interface).

## Floor Clear

Floor cleared, Crawler. You've created your first AI agent using Strands.

Loot you're keeping:

- How to enable debug logging to observe your agent's reasoning
- How to create an agent and define its behavior with a system prompt
- How to invoke and test your agent

<img src="../images/icons/stairwell-96x96.webp" alt="Stairwell" width="24" height="24"> **Stairwell:** Head to [Floor 2](floor-2.md) to learn about equipping your agent with tools.


> <img src="../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[I TALKED TO IT AND IT TALKED BACK]**
>
> Reward: You received a [Bronze Box]. Inside: one working Agent, and a debug log long enough to induce regret.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Your first agent lives. It is mine now, spiritually. [Floor 2](floor-2.md) awaits, and so does the part where you hand it weapons."
