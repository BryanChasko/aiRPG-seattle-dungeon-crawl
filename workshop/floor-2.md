# Floor 2: The Vending Machines

![Floor 2: The Vending Machines](../images/floors/floor-2-1200x675.webp)

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Floor 2. The vending machines are open. Everything on offer ships with the SDK, nothing is free of consequences, and the optional shell tool will run exactly what you approve. Approve with care. The sponsors are hoping you will not."

## Floor Objective

Tools are the primary mechanism for extending agent capabilities, enabling them to perform actions beyond text generation. Tools allow agents to interact with external systems, access data, and manipulate their environment. On this floor, you'll use your first vended tool, the name Strands gives to the tools that ship with the SDK, by adding the `http_request` tool to your agent, so your Narrator can look up real creature stat blocks on a public role-playing game API.

Make sure you are at the root of Floor 2 in your terminal:

```bash
cd aiRPG-seattle-dungeon-crawl/2_vended_tools
```

Open and modify the `agent_with_vended_tools.py` file.

## Your Arsenal: Vended Tools

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Vended tools ship in strands.vended_tools. No pip install, no shopping, no excuses. The shell tool runs exactly what you approve, and the audience adores a Crawler who approves everything."

The Strands SDK ships with a set of ready-to-use tools, the vended tools. They live in `strands.vended_tools`, so there is nothing extra to install. Here are some of them:

- `http_request`: calls external APIs (GET, POST, ...)
- `notebook`: keeps persistent notes in the agent's state
- `file_editor`: views, creates and edits files
- `shell`: runs shell commands
- `web_fetch`: fetches a web page and answers a question about it
- `handoff_to_user`: pauses to ask the user a question

View the complete list in the documentation.

## Step 1: Equip Your Agent with http_request

> <img src="../images/icons/item-96x96.webp" alt="Item" width="28" height="28"> **ITEM ACQUIRED: [http_request]**
>
> Calls external APIs on your agent's behalf. Rarity: Common. Comes with the Open5e API pre-bookmarked, because the System refuses to invent a stat block in front of a live audience.

```python
# TODO: Step 1 - Import http_request from strands.vended_tools
```

```python
# TODO: Step 1 - Add the http_request tool to your agent
```

Import the `http_request` tool from `strands.vended_tools`, then pass it to your agent's `tools` parameter (see adding tools to agents). The system prompt already tells your Narrator where to find creatures: the free [Open5e API](https://open5e.com/), which serves the System Reference Document 5.1 under the Creative Commons Attribution 4.0 license. The documentation describes what the tool can do.

## Step 2: Test Your Agent

> <img src="../images/icons/floor-boss-96x96.webp" alt="Floor boss" width="28" height="28"> **FLOOR BOSS:** Barnaby's homework. The party leader wants to know how the surface world's monster manuals rated his species, and he has a doctorate's worth of opinions ready. Your agent must look it up instead of guessing. Barnaby will check.

Once you've completed both TODOs, run your script:

```bash
python agent_with_vended_tools.py
```

Your agent will:

- Receive the question "Barnaby is a Giant Pacific Octopus. How do the old monster manuals say a giant octopus hides underwater, and what does its Ink Cloud do?"
- Determine that it needs to use the `http_request` tool
- Call the API at `https://api.open5e.com/v2/creatures/srd_giant-octopus/`
- Answer from the data it received: Underwater Camouflage gives advantage on Dexterity (Stealth) checks underwater, and Ink Cloud fills a 20-foot radius that stays heavily obscured for 1 minute, after which the octopus can Dash as a bonus action

This demonstrates that your agent can autonomously select and use tools to answer questions.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **SYSTEM DESIGN, LAYER 2: OUTSIDE KNOWLEDGE.** A System that makes up facts loses its readers the first time a number contradicts itself. Giving the agent a tool means it looks things up and quotes the source instead of guessing. Barnaby's own abilities in [the cast sheet](world/cast.md) (Chromatophore Stealth, Ink Cloud) are built on exactly what this API returns, adapted to the dance floor. See [The System](world/the-system.md#what-each-floor-adds-to-the-system).

## Bonus Room: The Multi-Tool Challenge (optional)

Ready to go deeper? Open `2_vended_tools/bonus_quest.py`. Kiro the Doomsday Scripter, a crawler whose class treats code as demolition magic, will write a Fibonacci script to a file and run it: two tools and one safeguard, wired the same way as the main floor. Each step below has two TODOs in the code: the import at the top of the file, and its use in the agent.

> <img src="../images/icons/warning-96x96.webp" alt="Warning" width="28" height="28"> **SYSTEM WARNING:** Windows users: the `shell` tool runs commands through `sh`, and `file_editor` expects POSIX paths (starting with `/`), so this bonus room does not run on native Windows. To try it on Windows, run it inside WSL (Windows Subsystem for Linux).

### Step 1: Equip the Tools

```python
# TODO: Step 1 - Import shell and file_editor from strands.vended_tools
```

```python
# TODO: Step 1 - Add the shell and file_editor tools to your agent
```

Both are vended tools: `file_editor` writes the scroll, `shell` casts it. Import them, then pass them in the agent's `tools` parameter, exactly like `http_request` in the main floor (see adding tools to agents).

### Step 2: Add the Safeguard

> <img src="../images/icons/item-96x96.webp" alt="Item" width="28" height="28"> **ITEM ACQUIRED: [HumanInTheLoop]**
>
> An intervention that makes every tool call wait for your y/n. Rarity: Uncommon. Side effect: you become personally responsible for everything that happens next.

```python
# TODO: Step 2 - Import HumanInTheLoop from strands.vended_interventions.hitl
```

```python
# TODO: Step 2 - Ask for your approval before each tool call with HumanInTheLoop in stdio mode
```

Writing files and running commands change your system. Strands lets you gate tool calls behind your approval with an intervention: import `HumanInTheLoop`, then pass `HumanInTheLoop(ask="stdio")` in the agent's `interventions` parameter, as shown in the Human-in-the-loop documentation. Every tool call now pauses and asks for your permission in the terminal:

```
Approve "file_editor"?
  Input: {"command": "create", "path": ".../fibonacci_scroll.py", ...} (y/n):
```

Type `y` and press Enter to allow the tool to execute, or `n` to refuse. Without this step, the agent writes files and runs commands without asking you anything: try it once with Step 2 left out to see the difference.

### Step 3: Cast the Spell

```bash
python bonus_quest.py
```

Approve each call as it comes:

- `Approve "file_editor"?`: Kiro writes `fibonacci_scroll.py` in the floor folder. Type `y`.
- `Approve "shell"?`: Kiro casts the scroll, usually `python3 fibonacci_scroll.py`, sometimes after a `cd` into the folder. Type `y` for each shell call.
- Kiro reports the first ten Fibonacci numbers.

Try `n` on one of the calls to see how the agent reacts to a refusal.

### Tool Consent and Safety

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "allowed_tools=["*"] removes every prompt. The sponsors call it brave. The System calls it content."

- Approval prompts: tools run with the permissions of your Python process. With `HumanInTheLoop`, nothing that alters your system happens without your explicit approval.
- Letting some tools through: `allowed_tools=["file_editor"]` lets a tool run freely while the others still ask. Use `["*"]` to disable the prompts entirely, for testing only.

## Floor Clear

Floor cleared, Crawler. You've equipped your agent with the `http_request` vended tool, and it can now decide on its own when to use it.

Loot you're keeping:

- How to import a vended tool and add it to your agent
- How an agent autonomously decides when to use a tool
- Tool consent and safety (covered with the bonus room's `HumanInTheLoop` intervention)

<img src="../images/icons/stairwell-96x96.webp" alt="Stairwell" width="24" height="24"> **Stairwell:** Journey to [Floor 3](floor-3.md) where you'll create custom tools for your specific use cases.


> <img src="../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[VENDED, NOT EARNED]**
>
> Reward: You received a [Bronze Box]. Inside: an http_request tool, a stern reminder about HumanInTheLoop, and a coupon for one (1) apology to your own filesystem.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Your agent now decides on its own when to reach for a tool. The sponsors call this "emergent behavior." I call it Tuesday."
