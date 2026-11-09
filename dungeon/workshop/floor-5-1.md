# Floor 5.1: The Rules Agent and the Knowledge Base

[Previous: Floor 5](floor-5.md) | [Dungeon map](README.md) | [Next: Floor 5.2](floor-5-2.md) <!-- floor-nav -->

Files on this floor: [`5_a2a_integration/agents/rules_agent/rules_agent.py`](../5_a2a_integration/agents/rules_agent/rules_agent.py), [`5_a2a_integration/utils/create_knowledge_base.py`](../5_a2a_integration/utils/create_knowledge_base.py) <!-- floor-files -->

## Floor Objective

Stand up the Rules Agent: index the Crawl Handbook into a ChromaDB knowledge base, then serve the agent over A2A on port 8000.

Change to the root of Floor 5:

```bash
cd seattle-strands-dungeon-crawl/dungeon/5_a2a_integration
```

## Part 1: Setting Up the Rules Agent

First, create the Knowledge Base for the Rules Agent. The Crawl Handbook, the crawl's own rule book, must be processed and stored in ChromaDB (a vector database) so the Rules Agent can query it for rules questions.

### Creating the Knowledge Base

> <img src="../../art/images/icons/item-96x96.webp" alt="" width="28" height="28"> **ITEM ACQUIRED: [The Crawl Handbook]**
>
> Eleven Markdown files of rules, written by the Narrator and revised every time a Crawler found a loophole. Rarity: Free. The Rules Agent reads it so you never have to, then cites section names at you with visible satisfaction.

> <img src="../../art/images/icons/warning-96x96.webp" alt="" width="28" height="28"> **SYSTEM WARNING:** Complete this setup before the Rules Agent can work.

#### Step 1: Read the Handbook

The handbook ships with the repository, in [`workshop/world/crawl-handbook/`](world/crawl-handbook/): one file per section, from ability scores and dance-offs to Safe Rooms and Ferry Tokens. Skim [Dance-Offs](world/crawl-handbook/03-dance-offs.md) and [The Final Beat](world/crawl-handbook/04-final-beat.md) now: the Narrator will run both before Floor 5 ends. Nothing to download.

#### Step 2: Build the Knowledge Base

> <img src="../../art/images/icons/achievement-96x96.webp" alt="" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[I READ THE MANUAL (A ROBOT DID)]**
>
> Reward: a [Bronze Box]. Inside: a chroma.sqlite3 file and a vector index that understands the rules better than you do.

Run the script to index the handbook. Important: run the script from the `utils` folder.

```bash
cd utils
python create_knowledge_base.py
cd ..
```

What `create_knowledge_base.py` does. The script reads every handbook file and keeps the section title from the file's first heading. Each file is cut into passages of about 1,000 characters that overlap by 200, so a rule split across two passages stays findable, and the section name is kept with each passage. ChromaDB then creates a local database in `rules_knowledge_base/` (a SQLite file plus a vector index) and turns every passage into a vector with ChromaDB's default embedding model, `all-MiniLM-L6-v2`, downloaded on first run (about 80 MB, cached afterwards): two passages about the same thing end up with vectors close to each other. Later, when the Rules Agent calls its tool, the question is turned into a vector with the same embedding model and the three closest passages come back with their section names. No LLM runs in that lookup: it is pure semantic search. Amazon Nova 2 Lite only reads the passages afterwards to write its answer.

Check the knowledge base exists:

- Find the `5_a2a_integration/utils/rules_knowledge_base/` folder
- Look for `chroma.sqlite3` inside
- The script prints: "Knowledge base creation complete!"

Change a rule in the handbook and run the script again: the Rules Agent answers from the new text on its next question. That is the point of keeping rules in a knowledge base instead of a system prompt.

| you see | it means | fix |
|---|---|---|
| `Crawl Handbook not found` | the script cannot find `workshop/world/crawl-handbook/` | run the script from `5_a2a_integration/utils`, inside the repository |
| `rules_knowledge_base/` appears somewhere else | the database is created in the folder you run from | delete the stray folder, `cd utils`, run the script again |
| the download of the embedding model hangs or fails | the network blocks the download | on a corporate network, set `HTTPS_PROXY` and run again; the embedding model is cached after one good run |

> <img src="../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** Nobody in the party had read the rules. Barnaby claimed he had skimmed them, which is what officers say. So we fed the handbook to a machine that would read every page and remember where each rule lived. The feeding cost us four minutes and an eighty-megabyte download. I have paid more for less on a range day.

### Configure the Rules Agent

> <img src="../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "One agent per context_id. Callers never see each other's history. The System AI finds this privacy endearing, and temporary."

In `agents/rules_agent/rules_agent.py`, complete the `create_agent` function. Until now each floor created one `Agent` at module level, and you were the only caller. An agent keeps its conversation history in memory, so one `Agent` instance holds one conversation. An A2A server serves many callers at the same time, each with a `context_id` of its own, and callers must not see each other's history. So give `A2AServer` an agent factory instead of an agent: a function that builds a fresh `Agent` for each new context. `A2AServer` calls the factory the first time a `context_id` appears and reuses the resulting agent for the rest of that conversation. The configuration is the same as before; only the location changed: a function. See [Conversation Isolation](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/#conversation-isolation) on the A2A page.

#### Step 1: Add the Tool

```python
# TODO: Step 1 - Add the query_rules tool to the agent
```

As in Floors 3 and 4, a tool is an action the agent can take. Here the action is looking up a rule in the knowledge base.

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

The three TODOs of Steps 1 to 3 sit together inside `Agent(...)`. The `solution` branch puts the three answers in a row under the third comment; placing one answer under each comment works the same.

</details>

#### Step 2: Add the Name

```python
# TODO: Step 2 - Add the name "Rules Agent" to the agent
```

Floors 1 to 4 never set a name, because only the learner talked to the agent. Here other agents will: `A2AServer` publishes an agent card, a small JSON document served at `/.well-known/agent-card.json` that says the agent's name, skills and URL ([Fetching the Agent Card](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/#fetching-the-agent-card) shows what a card contains). Here is the card the Rules Agent serves once Steps 1 to 3 are done:

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

The skills are the agent's tools: Strands fills them from the tool names and docstrings. The name at the top of the card is the `name` set in this step. Without `name`, every agent of the party would be called "Strands Agents".

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

The description at the top of the card: the Narrator reads the description in Part 3 ([Floor 5.3](floor-5-3.md#configure-the-narrator-agent)) to decide which agent to ask. A description is required: without one, the server stops with `ValueError: A2A agent description cannot be None or empty`. See [Basic Server Setup](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/#basic-server-setup) for an agent with a name and a description.

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

`A2AServer` wraps the `create_agent` factory in an HTTP server that speaks the A2A protocol: it serves the agent card and builds one agent per `context_id` through `create_agent`. See [Creating an A2A Server](https://strandsagents.com/docs/user-guide/sdk/multi-agent/agent-to-agent/#creating-an-a2a-server).

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

`serve()` starts the server and blocks until the process is stopped. The call sits under `if __name__ == "__main__":` so importing the module (the tests do) does not start a server.

<details>
<summary>Show me the code for Step 5</summary>

```python
if __name__ == "__main__":
    # TODO: Step 5 - Start the A2A server
    a2a_server.serve()
```

Replace the `pass` placeholder under the TODO.

</details>

> <img src="../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** The clerk we built had a name tag, a one-line job description and a window. Anyone could walk up, read the tag and ask a question, and nobody could read the questions anybody else had asked. Barnaby approved. "A proper civil service, Sergeant. Each petitioner gets a fresh clerk who has never heard of the last one."

#### Step 6: Launch the Rules Agent

Open a new terminal in the floor folder (`5_a2a_integration`), activate the virtual environment (a new terminal does not keep the one from Floor 0: `source ../../.venv/bin/activate` from the floor folder) and start the Rules Agent from the `agents/rules_agent` folder:

```bash
cd agents/rules_agent
python rules_agent.py
```

Uvicorn prints a line with `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/.well-known/agent-card.json` in a browser: the page is the agent card, with the name and description written in Steps 2 and 3. Leave the terminal open: the Narrator calls the Rules Agent in Part 4 ([Floor 5.3](floor-5-3.md#part-4-test-the-system)).

Check from another terminal: `curl -s http://127.0.0.1:8000/.well-known/agent-card.json` prints the card, starting with `{"name":"Rules Agent"` (the fields may come in another order).

| you see | it means | fix |
|---|---|---|
| `ValueError: A2A agent description cannot be None or empty` | Step 3 is missing | add `description=...` |
| `"name": "Strands Agents"` in the card | Step 2 is missing | add `name="Rules Agent"` |
| `address already in use` | another process holds port 8000 | stop it; `lsof -i :8000` on macOS and Linux |
| the agent starts, but its first answer reports a tool error about the collection `crawl_handbook` | the knowledge base was not built, or was built from the wrong folder | run Step 2 of "Creating the Knowledge Base" from `utils` |
| the script ends at once, with no Uvicorn line | `serve()` is missing | Step 5 |


## Side Passage: The Paper Trail (optional)

> <img src="../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** The accountant left in a hurry and left a binder on the pickleweed: an audit report, of us, as a PDF. Our clerk only read Markdown.

[The Paper Trail](encounters/paper-trail.md), a sidequest: read the accountant's audit report with `pypdf` and add the report to the Rules Agent's knowledge base, so the Rules Agent cites the report by page like any handbook section.

