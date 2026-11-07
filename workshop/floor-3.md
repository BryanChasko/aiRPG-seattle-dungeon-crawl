# Floor 3: The Crafting Table

![Floor 3: The Crafting Table](../images/floors/floor-3-1200x675.webp)

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Floor 3. Craft your own weapon, Crawler. The model never reads your code, only the docstring you write for it. Write a lazy one and watch your agent swing at air."

## Floor Objective

Learn how to create custom tools by building a Dice Rolling Tool - an essential capability for any Narrator.

Make sure you are at the root of Floor 3 in your terminal:

```bash
cd strands-dungeon-crawl/3_custom_tools
```

Open and modify the `agent_with_dice_roll_tool.py` file to create an agent capable of rolling dice using a custom tool.

## How Custom Tools Work

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "On this floor you stop borrowing weapons and forge your own. The model never sees your code. It sees a name, a docstring and a schema. That is your entire sales pitch."

In Strands, a custom tool is a Python function decorated with special attributes:

- The `@tool` Decorator: marks a function as an agent tool
- Function Docstring: describes the tool and guides the agent on when and how to use it

## Step 1: Turn Your Function into a Tool

Open `agent_with_dice_roll_tool.py`: it already contains a plain Python function, `roll_dice`, that rolls a die with a given number of faces. Your goal is to turn that function into a tool your agent can call.

```python
# TODO: Step 1 - Import tool from strands
```

```python
# TODO: Step 1 - Add the decorator to transform your function into a tool
```

Import the `@tool` decorator from Strands, then put it on `roll_dice`: the decorator turns an ordinary Python function into a tool that your agent can automatically discover and use. See this example in the documentation.

## Step 2: Write a Clear Docstring

> <img src="../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[THE SPEC SHEET OF SHAME]**
>
> Reward: You received a [Cracked Mirror]. It shows your tool_spec before the docstring: description 'roll_dice', and nothing else. The audience laughed for eleven seconds.

Right now `roll_dice` has no docstring at all. Before writing one, look at what the model will be told about your tool: right after the function, the script prints `roll_dice.tool_spec`, the exact specification Strands sends to the model. Run the script (Step 1 must be done). You should see:

```
{'name': 'roll_dice',
 'description': 'roll_dice',  # only the function name
 'inputSchema': {'json': {'properties': {'faces': {'default': 6, 'description': 'Parameter faces',  # only the parameter name
 'type': 'integer'}}, 'type': 'object'}}}
```

Look at `description`: it contains only the function name, `roll_dice`, and the parameter is described as nothing more than `Parameter faces`. That is all the model will ever know about your tool: it never reads the function's code, it only receives what Strands builds from the name, the docstring and the typed parameters.

```python
# TODO: Step 2 - Write a docstring with the description, an Args section and the return value
```

Now write the docstring: a first paragraph saying what the tool does, an `Args:` section describing `faces`, and what it returns, as in the documentation best practices.

Tip: LLMs are good at writing tool docstrings. Give them the function and an example of best practices, and let them generate a docstring for you.

Run the script again and compare the printed specification. You should see:

```
{'name': 'roll_dice',
 'description': '...',  # the docstring you added
 'inputSchema': {'json': {'properties': {'faces': {'default': 6, 'description': '...',  # the Args section of your docstring
 'type': 'integer'}}, 'type': 'object'}}}
```

The `Args:` section became the description of `faces`, the rest became the description of the tool.

Would it work without a docstring? Here, yes: with a name as explicit as `roll_dice` and a single parameter called `faces`, the model manages either way. With a vaguer name or several parameters it would have nothing else to go on, so make the docstring a habit.

## Step 3: Add the Tool to Your Agent

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "A tool that is not in tools=[] does not exist. The System checks. The System always checks."

```python
# TODO: Step 3 - Add the tool to the agent
```

Pass your tool to your agent. See the documentation from step 1 for how to do this.

Why this matters:

- The agent can only use tools that are explicitly provided in the `tools=[]` list
- Without this step, your tool cannot be discovered by the agent
- The agent automatically learns how to use all provided tools

## Step 4: Testing Your Tool

> <img src="../images/icons/floor-boss-96x96.webp" alt="Floor boss" width="28" height="28"> **FLOOR BOSS:** Sixteen rolls. Four abilities, four dice each, drop the lowest. Lady Luck runs the table, and Lady Luck does not do favors.

Once TODOs are completed, run your script:

```bash
python agent_with_dice_roll_tool.py
```

The system prompt in the file turns the agent into Lady Luck, the System's croupier subroutine, who helps players create characters for a fantasy role-playing game. The script asks her to roll four ability scores (strength, wisdom, charisma and intelligence) for a new character with the 4d6-drop-lowest method: for each ability, roll four six-sided dice and keep the three highest. That is always 16 rolls (4 abilities x 4 dice), and every single one must go through your tool.

Watch the agent in action:

- Analyze the character creation request
- Plan necessary rolls (4 abilities x 4d6 each)
- Execute dice rolls using your custom tool
- Calculate final scores (keep the best 3 dice)
- Return the results

## Floor Clear

Floor cleared, Crawler. You've created your own custom tool, and your agent can now use a capability you built specifically for it.

Loot you're keeping:

- How to turn a Python function into a tool with the `@tool` decorator
- How to write a docstring that guides the agent's use of the tool
- How to add your custom tool to an agent

<img src="../images/icons/stairwell-96x96.webp" alt="Stairwell" width="24" height="24"> **Stairwell:** Head to [Floor 4](floor-4.md) where you'll learn about the Model Context Protocol (MCP) to connect your agents to external services.


> <img src="../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[I MADE THIS (SO TO SPEAK)]**
>
> Reward: You received a [Silver Box]. Inside: a roll_dice tool that actually works, and the knowledge that sixteen rolls were required to prove it.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "You forged a tool. A real one. Floor 4 is where it leaves the house."
