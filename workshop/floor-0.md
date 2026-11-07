# Floor 0: The Stairwell

![Floor 0: The Stairwell](../images/floors/floor-0-1200x675.webp)

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Attention, Crawlers! Welcome to Floor 0. Pier 59 just folded into Elliott Bay and took the Seattle waterfront with it. Before you can out-dance an accountant, deploy agents, or cry to your alien sponsors about missing package managers, you need to clear the stairwell and secure a Safe Room. Wring out your socks, fire up your terminal, and try not to slip on the syntax."

## Floor Objective

Prepare your development environment: clone the workshop repo, install uv and Python, install the dependencies and activate the virtual environment. Everything else in this workshop runs from there.

> <img src="../images/icons/warning-96x96.webp" alt="Warning" width="28" height="28"> **SYSTEM WARNING:** Floor 8 deploys the game to AgentCore and also needs the AgentCore CLI. The Floor 8 page installs it (Node.js 20 or later).

## The Crawl You Are Building

This workshop builds the AI behind a LitRPG, *Dungeon Crawl: Seattle*. The System, a broadcast AI filming for alien viewers, collapsed the waterfront at Pier 59 and turned the Puget Sound underneath into an eight-floor dungeon. The leads are Cordula "Core" Vance, a Marine Corps Reserve crew chief who patrols the Sound by kayak, and Barnaby, an uplifted Giant Pacific Octopus who rides on her back in a water tank and runs the party. Shelly the geoduck and Chonks the spiny lumpsucker round it out. You play as this party. Conflict is a dance-off. Nobody dies: a Crawler who loses is Benched and wakes up in a Safe Room.

The lore lives in the [world guide](world/README.md): [the setting](world/seattle.md), [the cast](world/cast.md), [the System design](world/the-system.md) and the [Crawl Handbook](world/crawl-handbook/), the rules your Rules Agent searches on Floor 5.

Stuck at any point? [Ask the System](../study/README.md): `python study/ask_the_system.py` answers questions about any floor or Strands API from these pages and the API reference.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **SYSTEM DESIGN, LAYER 0: THE PREMISE.** Every LitRPG starts with where the System came from and why it is doing this to you. Ours is a game-show host with too much power: it is petty, it is theatrical, and it never lies about a number. Each floor of this workshop builds one Strands capability and one more layer of the System that uses it. The full map is in [The System](world/the-system.md#what-each-floor-adds-to-the-system).

## What is Strands?

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Strands is the SDK. You are the Crawler. I am the System. Learn the difference now, it matters on Floor 5."

[Strands](https://strandsagents.com/) is an Open Source Python and TypeScript SDK designed to simplify the creation of AI agents and multi-agent systems. Built with developer experience in mind, Strands provides an intuitive framework for building sophisticated AI applications that can interact with various tools, APIs, and services.

## Claim Your Safe Room (Installation)

### Step 1: Claim Your Starter Safe Room (Clone the Repo)

Grab the repository before the ceiling collapses and buries you in uncompiled garbage:

```bash
git clone https://github.com/BryanChasko/aiRPG-seattle-dungeon-crawl.git
cd aiRPG-seattle-dungeon-crawl
```

### Step 2: Equip Your Basic Tools (uv and Python)

> <img src="../images/icons/item-96x96.webp" alt="Item" width="28" height="28"> **ITEM ACQUIRED: [uv]**
>
> A package manager so fast it finishes before you finish doubting yourself. Rarity: Common. Durability: infinite. Judgment: considerable.

If you don't have uv, install it by following the [uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/).

If you don't have Python, install the latest version by running the following command:

```bash
uv python install
```

### Step 3: Imbibe the Mana Potions (Install Dependencies)

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "uv sync pulls everything the crawl needs, including the harness for Floor 7. If it fails, the audience gets a replay. Read the error before you paste it anywhere."

Force-feed your environment all the required Python packages:

```bash
uv sync
```

### Step 4: Lock the Safe Room Door (Activate Your Virtual Environment)

> <img src="../images/icons/sponsor-96x96.webp" alt="Sponsor" width="28" height="28"> **SPONSOR MESSAGE:** This Safe Room is brought to you by .venv. What gets installed in .venv stays in .venv.

Step inside, seal the door behind you, and isolate your environment from the rest of your filthy operating system.

Your virtual environment is where your dependencies have been installed. To activate it, run the command for your operating system.

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

## Floor Clear

Floor cleared, Crawler. You've set up your development environment for the Strands workshop.

Loot you're keeping:

- Installed uv and the latest Python
- Cloned the workshop repository
- Set up and activated the Python virtual environment

<img src="../images/icons/stairwell-96x96.webp" alt="Stairwell" width="24" height="24"> **Stairwell:** Head to [Floor 1](floor-1.md) where you'll create your first AI agent.


> <img src="../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[PEDANTIC LITTLE PIGGY]**
>
> Reward: You received a [Crawler's Trash Can]. Inside: a pair of unwashed socks, half a bottle of mana potion, and a sticky note that says "Sanctum is for nerds."

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Congratulations! You managed to open a terminal, copy four commands, and not immediately blow up your local environment. Don't get cocky. Next up is Floor 1, where you'll attempt to build your first AI agent. Try not to let it gain sentience and judge you."
