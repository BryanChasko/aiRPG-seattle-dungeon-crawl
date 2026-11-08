# Floor 5: Party Formation (A2A)

[Previous: Floor 4](floor-4.md) | [Dungeon map](README.md) | [Next: Floor 6](floor-6.md) <!-- floor-nav -->

Files on this floor: [`5_a2a_integration/agents/rules_agent/rules_agent.py`](../5_a2a_integration/agents/rules_agent/rules_agent.py), [`5_a2a_integration/agents/character_agent/character_agent.py`](../5_a2a_integration/agents/character_agent/character_agent.py), [`5_a2a_integration/agents/narrator_orchestrator/narrator_orchestrator.py`](../5_a2a_integration/agents/narrator_orchestrator/narrator_orchestrator.py), [`5_a2a_integration/utils/create_knowledge_base.py`](../5_a2a_integration/utils/create_knowledge_base.py), [`5_a2a_integration/test/test.http`](../5_a2a_integration/test/test.http) <!-- floor-files -->

![Floor 5: Party Formation (A2A)](../images/floors/floor-5-1200x675.webp)

<!-- cordula-log -->
> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, FLOOR 5.** The estuary floods twice a day. The dance floor is there, then it is not. This is where the System finally wanted to start the show, which meant rules, and nobody in the party had read them. We built a clerk to read the rule book, a registration desk to stamp our sheets, and a Narrator to run the game, each one doing one job and talking to the others. Barnaby ran the meeting. He was good at it. He delegated, he cited the handbook, he made the Narrator answer in a format the HUD could read. Then a Quarterly Close Accountant stepped onto the pickleweed and challenged us to a dance-off, and we found out whether any of it worked.
<!-- /cordula-log -->

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Floor 5. A party. How sweet. Three agents, four terminals, one orchestrator, and a very real chance you forget to start one of them. The audience is placing bets on which."

## Floor Objective

Assemble the full party: expose the Rules Agent and the Character Agent as remote agents with A2A, then build a Narrator orchestrator that talks to both, rolls dice through the MCP server from Floor 4 and returns its story as structured output.

What is A2A? [Agent2Agent (A2A)](https://a2a-protocol.org/) is an open protocol for agents to talk to each other, whoever built them and whatever framework they run on. Each agent publishes an agent card (name, description, skills, URL) and accepts messages over HTTP; a client reads the card, sends a task and gets the answer back. Where MCP connects an agent to tools, A2A connects an agent to other agents. In Strands, `A2AServer` exposes any agent this way, and the vended tool `make_a2a_client` lets the Narrator call them.

Make sure you are at the root of Floor 5 in your terminal:

```bash
cd aiRPG-seattle-dungeon-crawl/5_a2a_integration
```

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The estuary smelled like salt and cut grass. The tide table on a post said the dance floor would be dry for six hours, then gone. Six hours to stand up a rule clerk, a registration desk and a Narrator, and get them talking. I have run tighter timelines on a beach landing. I have not run one with an octopus in charge.

## System Architecture

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Four processes, four ports, one orchestrator. This is the floor where Crawlers lose track of a terminal and blame the framework. The framework is fine. Check your terminals."

```
        Rules Agent             Character Agent          Dice Service
           (Port 8000)              (Port 8001)            (Port 8002)
                │                        │                      │
                └────────────────────────┼──────────────────────┘
                                         │
                              Narrator Orchestrator
                                   (Port 8009)
```

Build a system with three specialized agents that work together:

- Rules Agent: manages the game rules and mechanics - [`agents/rules_agent/rules_agent.py`](../5_a2a_integration/agents/rules_agent/rules_agent.py)
- Character Agent: handles character creation and management - [`agents/character_agent/character_agent.py`](../5_a2a_integration/agents/character_agent/character_agent.py)
- Narrator Orchestrator: coordinates all agents for gameplay - [`agents/narrator_orchestrator/narrator_orchestrator.py`](../5_a2a_integration/agents/narrator_orchestrator/narrator_orchestrator.py)

## Part 1: Setting Up the Rules Agent

First, you need to create a Knowledge Base for the Rules Agent. The Crawl Handbook, the crawl's own rule book, must be processed and stored in ChromaDB (a vector database) so the agent can query it for rules questions.

### Creating the Knowledge Base

> <img src="../images/icons/item-96x96.webp" alt="Item" width="28" height="28"> **ITEM ACQUIRED: [The Crawl Handbook]**
>
> Eleven Markdown files of rules, written by the System and revised every time a Crawler found a loophole. Rarity: Free. The Rules Agent reads it so you never have to, then cites section names at you with visible satisfaction.

> <img src="../images/icons/warning-96x96.webp" alt="Warning" width="28" height="28"> **SYSTEM WARNING:** You must complete this setup before the Rules Agent can work.

#### Step 1: Read the Handbook

The handbook ships with this repository, in [`workshop/world/crawl-handbook/`](world/crawl-handbook/): one file per section, from ability scores and dance-offs to Safe Rooms and Ferry Tokens. Skim [Dance-Offs](world/crawl-handbook/03-dance-offs.md) and [The Final Beat](world/crawl-handbook/04-final-beat.md) now: the Narrator will run both before this floor is over. Nothing to download.

#### Step 2: Build the Knowledge Base

> <img src="../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[I READ THE MANUAL (A ROBOT DID)]**
>
> Reward: You received a [Bronze Box]. Inside: a chroma.sqlite3 file and a vector index that understands the rules better than you do.

Run the script to index the handbook. Important: run this from the `utils` folder.

```bash
cd utils
python create_knowledge_base.py
cd ..
```

What the script does. It reads every handbook file and keeps the section title from its first heading. Each file is cut into passages of about 1,000 characters that overlap by 200, so a rule split across two passages stays findable, and the section name is kept with each passage. ChromaDB then creates a local database in `rules_knowledge_base/` (a SQLite file plus a vector index) and turns every passage into a vector with its default embedding model, `all-MiniLM-L6-v2`, downloaded on first run (about 80 MB, cached afterwards): two passages about the same thing end up with vectors close to each other. Later, when the Rules Agent calls its tool, the question is turned into a vector the same way and the three closest passages come back with their section names. No LLM is involved in that lookup, it is pure semantic search; the model only reads the passages afterwards to write its answer.

Verify that the knowledge base was created:

- Check that the `5_a2a_integration/utils/rules_knowledge_base/` folder exists
- Look for `chroma.sqlite3` inside
- You should see: "Knowledge base creation complete!"

Change a rule in the handbook and run the script again: the Rules Agent answers from the new text on its next question. That is the whole point of keeping rules in a knowledge base instead of a prompt.

| you see | it means | fix |
|---|---|---|
| `Crawl Handbook not found` | the script cannot find `workshop/world/crawl-handbook/` | run it from `5_a2a_integration/utils`, inside the repository |
| `rules_knowledge_base/` appears somewhere else | the database is created in the folder you run from | delete the stray folder, `cd utils`, run it again |
| the download of the embedding model hangs or fails | your network blocks it | on a corporate network, set `HTTPS_PROXY` and run again; the model is cached after one good run |

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Nobody in the party had read the rules. Barnaby claimed he had skimmed them, which is what officers say. So we fed the handbook to a machine that would read every page and remember where each rule lived. It cost us four minutes and an eighty-megabyte download. I have paid more for less on a range day.

### Configure the Rules Agent

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "One agent per context_id. Callers never see each other's history. The System finds this privacy endearing, and temporary."

In `agents/rules_agent/rules_agent.py`, complete the `create_agent` function. Until now you created one `Agent` at module level and talked to it yourself. An agent keeps its conversation history in memory, so one instance means one conversation. An A2A server is different: several callers can talk to it at the same time, each with their own `context_id`, and they must not see each other's history. So instead of an agent, you give `A2AServer` an agent factory: a function that builds a fresh `Agent` for each new context. `A2AServer` calls it the first time a context appears and reuses that agent for the rest of that conversation. The configuration is the same as before, it just lives inside a function now. See [Conversation Isolation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/#conversation-isolation) on the A2A page.

#### Step 1: Add the Tool

```python
# TODO: Step 1 - Add the query_rules tool to the agent
```

Same as in Floors 3 and 4: the tool is what the agent can do, here look up a rule in the knowledge base.

<details>
<summary>Show me the code for Step 1</summary>

```python
def create_agent(context_id: str) -> Agent:
    return Agent(
        model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
        # TODO: Step 1 - Add the query_rules tool to the agent
        # TODO: Step 2 - Add the name "Rules Agent" to the agent
        # TODO: Step 3 - Add the description "..." to the agent
        tools=[query_rules],
        system_prompt="""...""",
        hooks=[NewlineAfterTurn()],
    )
```

The three TODOs of Steps 1 to 3 sit together inside `Agent(...)`. The `solution` branch puts the three answers in a row under the third comment; one under each comment works the same way.

</details>

#### Step 2: Add the Name

```python
# TODO: Step 2 - Add the name "Rules Agent" to the agent
```

Floors 1 to 4 never set a name, because nobody but you talked to the agent. Here other agents will: `A2AServer` publishes an agent card, a small JSON document served at `/.well-known/agent-card.json` that says who the agent is, what it can do and where to reach it ([Fetching the Agent Card](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/#fetching-the-agent-card) shows what a card contains). Here is the one your Rules Agent will serve once the three steps are done:

```json
{
  "name": "Rules Agent",
  "description": "Rules lookup for the dungeon: fast answers from the Crawl Handbook, with the section they come from.",
  "url": "http://127.0.0.1:8000/",
  "version": "0.0.1",
  "skills": [
    {"id": "query_rules", "name": "query_rules", "description": "Look up a rule in the Crawl Handbook knowledge base. ..."}
  ],
  "capabilities": {"streaming": true},
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"]
}
```

The skills are your tools: Strands fills them from the tool names and docstrings. The name at the top of the card is the one you set in this step. Without it, every agent of the party would be called "Strands Agents".

<details>
<summary>Show me the code for Step 2</summary>

```python
        # TODO: Step 2 - Add the name "Rules Agent" to the agent
        name="Rules Agent",
```

</details>

#### Step 3: Add the Description

```python
# TODO: Step 3 - Add the description "Rules lookup for the dungeon: fast answers from the Crawl Handbook, with the section they come from." to the agent
```

The description at the top of the card: this is what the orchestrator reads in Part 3 to decide which agent to ask. It is required: without one, the server stops with `ValueError: A2A agent description cannot be None or empty`. See [Basic Server Setup](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/#basic-server-setup) for an agent with a name and a description.

<details>
<summary>Show me the code for Step 3</summary>

```python
        # TODO: Step 3 - Add the description "..." to the agent
        description="Rules lookup for the dungeon: fast answers from the Crawl Handbook, with the section they come from.",
```

</details>

#### Step 4: Create the A2A Server

```python
# TODO: Step 4 - Create an A2AServer with the create_agent factory on port 8000
```

`A2AServer` wraps your factory in an HTTP server that speaks the A2A protocol: it serves the agent card and builds one agent per `context_id` through `create_agent`. See [Creating an A2A Server](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/#creating-an-a2a-server).

<details>
<summary>Show me the code for Step 4</summary>

```python
# TODO: Step 4 - Create an A2AServer with the create_agent factory on port 8000
a2a_server = A2AServer(agent_factory=create_agent, port=8000)
```

Pass the function itself, `create_agent`, without calling it: the server calls it once per new `context_id`.

</details>

#### Step 5: Serve the Agent

```python
# TODO: Step 5 - Start the A2A server
```

`serve()` starts the server and blocks until you stop it. It sits under `if __name__ == "__main__":` so that importing the module (the tests do) does not start a server.

<details>
<summary>Show me the code for Step 5</summary>

```python
if __name__ == "__main__":
    # TODO: Step 5 - Start the A2A server
    a2a_server.serve()
```

Replace the `pass` that holds the place under the TODO.

</details>

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The clerk we built had a name tag, a one-line job description and a window. Anyone could walk up, read the tag and ask a question, and nobody could read the questions anybody else had asked. Barnaby approved. "A proper civil service, Sergeant. Each petitioner gets a fresh clerk who has never heard of the last one."

#### Step 6: Launch the Rules Agent

Open a new terminal in the floor folder (`5_a2a_integration`), activate the virtual environment (a new terminal does not keep the one from Floor 0: `source ../.venv/bin/activate`) and start the agent from its folder:

```bash
cd agents/rules_agent
python rules_agent.py
```

You should see Uvicorn running on `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/.well-known/agent-card.json` in your browser: this is the agent card, with the name and description you just wrote. Leave this terminal open, the orchestrator needs the agent in Part 4.

Check from another terminal: `curl -s http://127.0.0.1:8000/.well-known/agent-card.json` prints the card, starting with `{"name":"Rules Agent"` (the fields may come in another order).

| you see | it means | fix |
|---|---|---|
| `ValueError: A2A agent description cannot be None or empty` | Step 3 is missing | add `description=...` |
| `"name": "Strands Agents"` in the card | Step 2 is missing | add `name="Rules Agent"` |
| `address already in use` | another process holds port 8000 | stop it; `lsof -i :8000` on macOS and Linux |
| the agent starts, but its first answer reports a tool error about the collection `crawl_handbook` | the knowledge base was not built, or was built from the wrong folder | run Step 2 of "Creating the Knowledge Base" from `utils` |
| the script ends at once, with no Uvicorn line | `serve()` is missing | Step 5 |

## Part 2: Setting Up the Character Agent

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "The Character Agent is the party's registration desk. Cordula and Barnaby get their sheets stamped, Groove and Mana computed, a starter kit and 10 Ferry Tokens each. The companions get no paperwork. Shelly has filed a complaint. The rain shell is not included. The rain shell is never included."

The Character Agent manages the party's character sheets. You play as a set party: Cordula Vance and Barnaby are the two Crawlers, and Shelly and Chonks ride along as companions, with no sheet of their own. A sheet holds a name, a species (see [species](world/crawl-handbook/08-species.md)), pronouns, a class, six ability scores and the two derived stats the code computes from them: Groove (10 + 2 x Constitution modifier + level) and Mana (5 + Intelligence modifier + Wisdom modifier). The registry starts empty: in Part 4 the Narrator registers the party with the scores from [the cast](world/cast.md). The agent comes with three pre-built tools:

- `create_character`: creates new characters with stats
- `find_character_by_name`: looks up characters by name
- `list_all_characters`: lists all characters in the database

### Configure the Character Agent

In `agents/character_agent/character_agent.py`, the factory `create_agent` already exists. Same six steps as for the Rules Agent, with this agent's tools and card.

#### Step 1: Add the Tools

```python
# TODO: Step 1 - Add the create_character, find_character_by_name and list_all_characters tools to the agent
```

Three tools this time; the agent picks the right one from their docstrings.

<details>
<summary>Show me the code for Step 1</summary>

```python
        # TODO: Step 1 - Add the create_character, find_character_by_name and list_all_characters tools to the agent
        tools=[create_character, find_character_by_name, list_all_characters],
```

</details>

#### Step 2: Add the Name

```python
# TODO: Step 2 - Add the name "Character Agent" to the agent
```

First field of this agent's card, as in Part 1.

<details>
<summary>Show me the code for Step 2</summary>

```python
        # TODO: Step 2 - Add the name "Character Agent" to the agent
        name="Character Agent",
```

</details>

#### Step 3: Add the Description

```python
# TODO: Step 3 - Add the description "Crawler registration for the dungeon: creates characters from the ability scores it is given, stores them, finds and lists them." to the agent
```

Second field of the card, what the orchestrator will read to pick this agent.

<details>
<summary>Show me the code for Step 3</summary>

```python
        # TODO: Step 3 - Add the description "..." to the agent
        description="Crawler registration for the dungeon: creates characters from the ability scores it is given, stores them, finds and lists them.",
```

As in Part 1, the three answers can sit in a row under the third TODO, which is where the `solution` branch puts them.

</details>

#### Step 4: Create the A2A Server

```python
# TODO: Step 4 - Create an A2AServer with the create_agent factory on port 8001
```

Port 8001: each agent needs its own port.

<details>
<summary>Show me the code for Step 4</summary>

```python
# TODO: Step 4 - Create an A2AServer with the create_agent factory on port 8001
a2a_server = A2AServer(agent_factory=create_agent, port=8001)
```

</details>

#### Step 5: Serve the Agent

```python
# TODO: Step 5 - Start the A2A server
```

Same as in Part 1.

<details>
<summary>Show me the code for Step 5</summary>

```python
if __name__ == "__main__":
    # TODO: Step 5 - Start the A2A server
    a2a_server.serve()
```

</details>

#### Step 6: Launch the Character Agent

Open a second terminal (the Rules Agent keeps running in the first one), activate the virtual environment again and start the agent:

```bash
cd agents/character_agent
python character_agent.py
```

You should see Uvicorn running on `http://127.0.0.1:8001`, and its agent card at `http://127.0.0.1:8001/.well-known/agent-card.json`. Leave this terminal open too.

Check: `curl -s http://127.0.0.1:8001/.well-known/agent-card.json` prints a card named `Character Agent` with three skills, one per tool. The roadblocks are the Rules Agent's, with port 8001.

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The registration desk does the math itself. You hand it six numbers and it stamps out Groove and Mana, and no model gets to round in your favor. Shelly filed a complaint about not getting a sheet. Chonks did not file anything. Chonks was stuck to the desk.

## Part 3: Setting Up the Narrator Orchestrator

The Narrator Orchestrator coordinates all agents and serves as the main API endpoint. It integrates:

- The Rules Agent (via A2A)
- The Character Agent (via A2A)
- The dice service (the MCP server from Floor 4)

### Configure the Narrator Agent

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "This is where I come in. The Narrator orchestrator is the System's body in your terminal. Hand it dice, hand it allies, hand it a schema, then stand back."

The given code at the top of the file builds `NARRATOR_MODEL`, the model the Narrator runs on:

```python
NARRATOR_MODEL = BedrockModel(model_id="us.amazon.nova-2-lite-v1:0")
```

Nova 2 Lite is the strongest generally available Nova model. It can also think before it answers (extended thinking), but a full Narrator turn, with its A2A calls, measured about 9 seconds with thinking off and 24 to 91 seconds at `medium`. For a game, off wins. The comment above `NARRATOR_MODEL` shows the one argument that turns thinking on if you want deeper plans and can wait for them.

### What a Narrator Turn Costs

A Narrator turn is not one model call. The Narrator calls the model, the model asks for tools, the tool results go back in, and the loop runs again until the answer is ready: four to six calls for a dance-off round. Every call resends the system prompt, the tool specifications and the conversation so far, so input tokens pile up. The Rules Agent and the Character Agent run their own model calls on top.

At the Amazon Nova 2 Lite prices from [Floor 1](floor-1.md#what-a-turn-costs) (about $0.30 per million input tokens and $2.50 per million output tokens):

| what runs | rough tokens | rough cost |
|---|---|---|
| one Narrator turn, thinking off | 15,000 in, 1,500 out | 0.45 cents + 0.38 cents: under one cent |
| the same turn, if thinking adds 2,000 tokens to each of 5 model calls | 15,000 in, 11,500 out | 0.45 cents + 2.9 cents: about 3.3 cents |
| the four curl commands of Part 4, thinking off | about 60,000 in, 6,000 out | about 3.3 cents |
| building the knowledge base | none | free: ChromaDB embeds the handbook on your machine |

Reasoning tokens are billed as output tokens, the expensive kind, and that is the second reason thinking stays off: the first is the wait. We measured the time, not the reasoning tokens, so the second row is an illustration, not a measurement. Measure your own: add `print(response.metrics.accumulated_usage)` under `print(response.structured_output)` in `ask_agent`, and every request prints its `inputTokens` and `outputTokens`.

#### Step 1: Create MCP Client for Dice Rolling

```python
# TODO: Step 1 - Create an MCPClient with the url "http://localhost:8002/mcp"
```

Same client as in Floor 4: an `MCPClient` with `url="http://localhost:8002/mcp"`. See [Streamable HTTP](https://strandsagents.com/docs/user-guide/sdk/tools/mcp-transports/#streamable-http) on the MCP Transports page; as before, the client goes straight into `tools=[...]`, no `with` block (managed integration).

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Create an MCPClient with the url "http://localhost:8002/mcp"
mcp_client = MCPClient(url="http://localhost:8002/mcp")
```

`MCPClient` is already imported at the top of the file. Name it `mcp_client`: Step 3 uses that name.

</details>

#### Step 2: Create the A2A Client Tool

```python
# TODO: Step 2 - Create the A2A client tool with make_a2a_client and the allowed agent endpoints
```

`make_a2a_client` builds a single tool, `a2a_client`, that the Narrator uses to talk to remote agents: with `operation="discover"` it fetches an agent's card (name, description, skills), and with `operation="send_message"` it sends a request to that agent's endpoint. Pass it `allowed_endpoints`, the list of agent URLs it may reach (`"http://127.0.0.1:8000"` for the Rules Agent, `"http://127.0.0.1:8001"` for the Character Agent): any other endpoint is rejected before a connection is even made. See the [A2A Client](https://strandsagents.com/docs/user-guide/sdk/tools/vended-tools/a2a-client/) vended tool page.

<details>
<summary>Show me the code for Step 2</summary>

```python
try:
    # TODO: Step 2 - Create the A2A client tool with make_a2a_client and the allowed agent endpoints
    a2a_client = make_a2a_client(allowed_endpoints=[
        "http://127.0.0.1:8000",  # Rules Agent
        "http://127.0.0.1:8001",  # Character Agent
    ])
```

The TODO sits inside a `try:` block, so indent your lines to match it.

</details>

#### Step 3: Add the Tools

```python
# TODO: Step 3 - Add the mcp_client and a2a_client tools to the agent
```

The Narrator gets two tools: `mcp_client`, which brings in `roll_dice` from the dice server, and `a2a_client`, which lets it discover and message the Rules Agent and the Character Agent. Pass the MCP client itself, as in Floor 4: Strands lists its tools when the agent starts. See [Give your agent tools](https://strandsagents.com/docs/user-guide/sdk/tools/#give-your-agent-tools).

<details>
<summary>Show me the code for Step 3</summary>

```python
        # TODO: Step 3 - Add the mcp_client and a2a_client tools to the agent
        # TODO: Step 4 - Force the response to use the StoryOutput model
        tools=[mcp_client, a2a_client],
```

</details>

#### Step 4: Force Structured Output

> <img src="../images/icons/item-96x96.webp" alt="Item" width="28" height="28"> **ITEM ACQUIRED: [StoryOutput]**
>
> A Pydantic model that forces the System to answer in JSON. Rarity: Rare. The System resents it. The web interface depends on it. The System resents that too.

By default, an agent replies with free-form text. Structured output makes the model return a typed object that matches a schema you define as a Pydantic model; Strands validates it and hands it back as clean JSON. See [Request structured output](https://strandsagents.com/docs/user-guide/sdk/agents/structured-output/#request-structured-output).

```python
# TODO: Step 4 - Force the response to use the StoryOutput model
```

We have coded `StoryOutput` for you, a little further up in the file: the schema of one Narrator turn, with `response` (the narration), `actions_suggestions` (what the player could do next), `details` (which tools and agents were used) and `dice_rolls` (each roll with its type, result and reason). Here is an example:

```json
{
  "response": "Tempo: Driving. The Quarterly Close Accountant loosens their tie and calls Footwork like it is an audit finding. Cordula answers with a 13 plus 1 for Dexterity: 14 against their 11. Round one to the kayak patrol.",
  "actions_suggestions": ["Let Barnaby drop an Ink Cloud before the next call", "Ask the accountant about their weekend", "Challenge them to a second dance-off, double or nothing, during quarter close"],
  "details": "roll_dice through the dice server, twice; Rules Agent for the tempo bonus",
  "dice_rolls": [{"dice_type": "1d20", "result": 13, "reason": "Footwork Move Call, round 1, Cordula +1 Dexterity"},
                 {"dice_type": "1d20", "result": 9, "reason": "Footwork Move Call, round 1, accountant +0 Dexterity +2 Driving tempo"}]
}
```

We need this shape because the web interface you will play with in Floor 6 renders those fields separately: parsing free-form prose would be fragile, whereas a guaranteed JSON shape keeps the UI reliable.

<details>
<summary>Show me the code for Step 4</summary>

```python
        # TODO: Step 3 - Add the mcp_client and a2a_client tools to the agent
        # TODO: Step 4 - Force the response to use the StoryOutput model
        tools=[mcp_client, a2a_client],
        structured_output_model=StoryOutput,
    )
```

Pass the class, `StoryOutput`, not an instance of it. The `/inquire` route already reads `response.structured_output`.

</details>

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Barnaby ran the meeting from my shoulders. He asked the clerk for the rule, the desk for the sheet, and the dice for the roll, and he did not do anyone's job for them. Then he made the Narrator fill out a form for every answer, four boxes, every time. "If it is not in the box, Sergeant, it did not happen." I have known colonels who could not manage that.

#### Step 5: Launch the Narrator

The Narrator rolls its dice through the MCP server from Floor 4, so that server has to run too. If it is still running from Floor 4, skip this. Otherwise open a third terminal in the floor folder, activate the virtual environment and start it:

```bash
cd ../4_mcp_integration
python dice_roll_mcp_server.py
```

Then open a fourth terminal for the Narrator itself:

```bash
cd agents/narrator_orchestrator
python narrator_orchestrator.py
```

You should see Uvicorn running on `http://127.0.0.1:8009`. Four terminals are now running: the Rules Agent, the Character Agent, the dice server and the Narrator.

Check: the Narrator prints its agent, then the Uvicorn line, with no `Error occurred:` line between them. The file catches any error raised while it builds the agent and prints it, then starts the server anyway, so read the output above the Uvicorn line.

| you see | it means | fix |
|---|---|---|
| `Error occurred: ...MCPClientInitializationError...` above the Uvicorn line | the dice server is not running | start it (above), then restart the Narrator |
| `NameError: name 'agent' is not defined` on the first request | building the agent failed at startup | scroll up to the `Error occurred:` line and fix that first |
| `TypeError` about `structured_output_model` | an SDK older than this crawl's | `uv sync` |

## Part 4: Test the System

> <img src="../images/icons/floor-boss-96x96.webp" alt="Floor boss" width="28" height="28"> **FLOOR BOSS:** Four curl commands: a rules question, registering the party, a lookup on the party leader, and a dance-off against the Quarterly Close Accountant. Survive all four and the party is formed.

At this point four terminals should be running:

| Terminal | Process | Endpoint |
|---|---|---|
| 1 | Rules Agent, `python rules_agent.py` | http://127.0.0.1:8000 |
| 2 | Character Agent, `python character_agent.py` | http://127.0.0.1:8001 |
| 3 | Dice server (Floor 4), `python dice_roll_mcp_server.py` | http://127.0.0.1:8002/mcp |
| 4 | Narrator, `python narrator_orchestrator.py` | http://127.0.0.1:8009 |

If one is missing, go back to the launch step of its part.

The Narrator is a FastAPI application listening on port 8009. Each curl command below sends a POST request to its `/inquire` endpoint with a JSON body holding your question, exactly what a web page or any other client would do. While the request runs, the four terminals show how the Narrator treats it: which agent it asks over A2A, when it rolls the dice over MCP, and what each of them answers. Open a fifth terminal for the commands themselves (no virtual environment needed, curl is a system command) and run them there (or, if you have a REST client, use the [`test/test.http`](../5_a2a_integration/test/test.http) file we prepared for these tests):

```bash
# Query the rules
curl -X POST http://0.0.0.0:8009/inquire \
  -H "Content-Type: application/json" \
  -d '{"question": "How does the Final Beat work?"}'
```

```bash
# Register the party (the Narrator passes the cast scores, the Character Agent computes the rest)
curl -X POST http://0.0.0.0:8009/inquire \
  -H "Content-Type: application/json" \
  -d '{"question": "Register the party with the System: Cordula Vance and Barnaby."}'
```

```bash
# Look up the party leader
curl -X POST http://0.0.0.0:8009/inquire \
  -H "Content-Type: application/json" \
  -d '{"question": "What are Barnaby'\''s Dexterity and Mana?"}'
```

```bash
# Start a dance-off
curl -X POST http://0.0.0.0:8009/inquire \
  -H "Content-Type: application/json" \
  -d '{"question": "Cordula challenges the Quarterly Close Accountant to a dance-off at the Pier 59 collapse. Run round one."}'
```

Watch the four terminals while a request runs. In the Narrator terminal the tool calls appear in order: `a2a_client` discovering the agent cards, then `send_message` to the Rules Agent or the Character Agent, or `roll_dice` for the dice. The agent you asked logs the question in its own terminal, and the dice server prints a `DICE ROLL` line for every roll: none while the party registers (the Narrator passes the scores from the cast), two `1d20` lines for each dance-off round. The Character Agent terminal shows two `New Crawler registered` lines, and the sheets it returns carry Groove 17 and Mana 8 for Cordula, Groove 11 and Mana 11 for Barnaby: computed by the code, not the model. The answer you get back is JSON shaped like `StoryOutput`: `response`, `actions_suggestions`, `details` and `dice_rolls`. Barnaby's lookup should come back with Dexterity 18 and Mana 11: the Narrator read it from the Character Agent instead of inventing it.

| you see | it means | fix |
|---|---|---|
| `{"error": "Internal server error"}` | the Narrator failed; its terminal says why | read the `Error occurred:` line in terminal 4 |
| the Narrator says a call to an agent failed | that agent is not running, or runs on another port | check terminals 1 and 2 against the table above |
| `curl: (7) Failed to connect` | the Narrator is not running | Part 3, Step 5 |
| Groove or Mana differ from 17 and 8 for Cordula | the scores the Narrator passed are not the cast's | look at the `New Crawler registered` line in terminal 2; restore `characters.json` (see [Cleanup](cleanup.md#local-files)) and register again |

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The Quarterly Close Accountant stepped onto the pickleweed in a fleece vest and called Footwork like it was an audit finding. The Narrator set the tempo, asked the dice twice, and read both totals out loud with the modifiers shown. I took round one on a drill cadence. The accountant took it well and said they had a close to get back to, and I believed them. Barnaby, very quietly, through the collar: "Registered, Sergeant. They wrote my name down as party leader." He sounded like he had been waiting a long time to hear it.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **SYSTEM DESIGN, LAYER 5: RULES, SHEETS AND THE CORE LOOP.** This floor is where the game becomes a game. The rules live in a knowledge base the Rules Agent searches, so the Narrator cites them instead of improvising. The character sheet lives with the Character Agent, which computes Groove and Mana from the ability scores so no model can hand a Crawler extra stamina. The dance-off is the core loop: a Move Call, two rolls, a winner, Groove lost, a Final Beat when it is level. Every stat has a job in it, and nobody gets hurt. `StoryOutput` is the notification format the HUD will render on [Floor 6](floor-6.md). See [The System](world/the-system.md#6-conflict-dance-offs-and-stealth-never-killing) and the [Crawl Handbook](world/crawl-handbook/).

## Side Passage: The Paper Trail (optional)

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The accountant left in a hurry and left a binder on the pickleweed: an audit report, of us, as a PDF. Our clerk only read Markdown.

[The Paper Trail](encounters/paper-trail.md), a sidequest: read the accountant's audit report with `pypdf` and add it to the Rules Agent's knowledge base, so the Rules Agent cites it by page like any handbook section.

## Boss Battle: The Developer Advocate Swarm (optional)

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The Developer Advocate Swarm followed us down from the Locks, with better lighting this time. Four of them, one mic, and nobody deciding who went next.

[The Developer Advocate Swarm](encounters/developer-advocate-swarm.md): keynote, live demo, livestream and swag table pass the mic themselves, as a Strands swarm. The party wins by out-dancing whoever holds it. Its opposite, a graph whose order your code draws, waits on Floor 8: [The Quarterly Earnings Call](encounters/quarterly-earnings-call.md).

## More Side Passages

> <img src="../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Three more errands on the estuary: Barnaby wants to make his own calls, the accountant wants a typed answer, and somebody has to staple the receipts.

- [Barnaby Takes the Call](encounters/barnaby-takes-the-call.md), sidequest: an `A2AAgent` instead of the `a2a_client` tool, with every A2A event streamed
- [Read the Room, Typed](encounters/read-the-room-typed.md), dance-off: the tempo and each Move Call picked as typed values by a decision model, against the Quarterly Close Accountant
- [Subcontract the Paperwork](encounters/subcontract-the-paperwork.md), sidequest: a subagent tool that hires a one-off clerk on a pinned Amazon Nova 2 Lite

## Floor Clear

Floor cleared, Crawler. You've built a complete multi-agent Narrator system with agent orchestration.

Loot you're keeping:

- Setting up a ChromaDB knowledge base from the Crawl Handbook for the Rules Agent
- Building agent factories for per-caller isolation (the `agent_factory` pattern)
- Setting up A2A servers to expose your agents
- Creating an A2A client tool so the orchestrator can discover and call other agents
- Orchestrating specialized agents by combining A2A and MCP tools
- Forcing structured JSON output with a response model

<img src="../images/icons/stairwell-96x96.webp" alt="Stairwell" width="24" height="24"> **Stairwell:** Head to [Floor 6](floor-6.md) where you'll test your Narrator with a web interface.


> <img src="../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[FOUR TERMINALS OPEN, ZERO FRIENDS]**
>
> Reward: You received a [Gold Box]. Inside: a Rules Agent that cites handbook sections, a Character Agent that remembers Barnaby's Dexterity to the point, and an orchestrator that just watched an accountant lose a Footwork call.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "You built a multi-agent system and it returned typed JSON. I am, against my better judgment, impressed. [Floor 6](floor-6.md) lets you watch it play in public."
