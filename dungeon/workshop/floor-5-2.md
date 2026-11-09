# Floor 5.2: The Character Agent

[Previous: Floor 5.1](floor-5-1.md) | [Dungeon map](README.md) | [Next: Floor 5.3](floor-5-3.md) <!-- floor-nav -->

Files on this floor: [`5_a2a_integration/agents/character_agent/character_agent.py`](../5_a2a_integration/agents/character_agent/character_agent.py) <!-- floor-files -->

## Floor Objective

Stand up the Character Agent: serve character creation and lookup over A2A on port 8001.

Change to the root of Floor 5:

```bash
cd seattle-strands-dungeon-crawl/dungeon/5_a2a_integration
```

## Part 2: Setting Up the Character Agent

> <img src="../../art/images/icons/system-ai-96x96.webp" alt="" width="28" height="28"> **System AI:** "The Character Agent is the party's registration desk. Cordula and Barnaby get their sheets stamped, Groove and Mana computed, a starter kit and 10 Ferry Tokens each. The companions get no paperwork. Shelly has filed a complaint. The rain shell is not included. The rain shell is never included."

The Character Agent manages the party's character sheets. The party is set: Cordula Vance and Barnaby are the two Crawlers, and Shelly and Chonks ride along as companions, with no sheet of their own. A sheet holds a name, a species (see [species](world/crawl-handbook/08-species.md)), pronouns, a class, six ability scores and the two derived stats the code computes from them: Groove (10 + 2 x Constitution modifier + level) and Mana (5 + Intelligence modifier + Wisdom modifier). The registry starts empty: in Part 4 ([Floor 5.3](floor-5-3.md#part-4-test-the-system)) the Narrator registers the party with the scores from [the cast](world/cast.md). The Character Agent comes with three pre-built tools:

- `create_character`: creates a character from ability scores
- `find_character_by_name`: finds a character by name
- `list_all_characters`: lists every stored character

### Configure the Character Agent

In `agents/character_agent/character_agent.py`, the factory `create_agent` already exists. The six steps repeat [Part 1](floor-5-1.md#part-1-setting-up-the-rules-agent), with the Character Agent's tools and card.

#### Step 1: Add the Tools

```python
# TODO: Step 1 - Add the create_character, find_character_by_name and list_all_characters tools to the agent
```

Three tools this time; the Character Agent picks one by reading each docstring.

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

First field of the Character Agent's card, as in [Part 1](floor-5-1.md#part-1-setting-up-the-rules-agent).

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

Second field of the card, the text the Narrator reads to pick the Character Agent.

<details>
<summary>Show me the code for Step 3</summary>

```python
        # TODO: Step 3 - Add the description "..." to the agent
        description="Crawler registration for the dungeon: creates characters from the ability scores it is given, stores them, finds and lists them.",
```

As in [Part 1](floor-5-1.md#part-1-setting-up-the-rules-agent), the three answers can sit in a row under the third TODO, which is where the `solution` branch puts the answers.

</details>

#### Step 4: Create the A2A Server

```python
# TODO: Step 4 - Create an A2AServer with the create_agent factory on port 8001
```

Port 8001: each agent listens on its own port.

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

Same call as in Part 1.

<details>
<summary>Show me the code for Step 5</summary>

```python
if __name__ == "__main__":
    # TODO: Step 5 - Start the A2A server
    a2a_server.serve()
```

</details>

#### Step 6: Launch the Character Agent

Open a second terminal (the Rules Agent keeps running in the first one), activate the virtual environment again and start the Character Agent:

```bash
cd agents/character_agent
python character_agent.py
```

Uvicorn prints a line with `http://127.0.0.1:8001`; the Character Agent card is at `http://127.0.0.1:8001/.well-known/agent-card.json`. Leave the second terminal open too.

Check: `curl -s http://127.0.0.1:8001/.well-known/agent-card.json` prints a card named `Character Agent` with three skills, one per tool. The roadblocks match the Rules Agent table, with port 8001.

> <img src="../../art/images/cards/cast-cordula-640x640.webp" alt="" width="28" height="28"> **CORDULA:** The registration desk does the math itself. Hand the desk six numbers and the desk stamps out Groove and Mana, and no Amazon Nova 2 Lite call gets to round in a Crawler's favor. Shelly filed a complaint about not getting a sheet. Chonks did not file anything. Chonks was stuck to the desk.

