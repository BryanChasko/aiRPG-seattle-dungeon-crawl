# Floor 3: The Crafting Table

![Floor 3: The Crafting Table](../images/floors/floor-3-1200x675.webp)

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Floor 3. Craft your own gear, Crawler. The model never reads your code, only the docstring you write for it. Write a lazy one and watch your agent dance to the wrong song."

## Floor Objective

Learn how to create custom tools by building a Dice Rolling Tool - an essential capability for any Narrator.

Make sure you are at the root of Floor 3 in your terminal:

```bash
cd aiRPG-seattle-dungeon-crawl/3_custom_tools
```

Open and modify the `agent_with_dice_roll_tool.py` file to create an agent capable of rolling dice using a custom tool.

## How Custom Tools Work

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "On this floor you stop borrowing gear and forge your own. The model never sees your code. It sees a name, a docstring and a schema. That is your entire sales pitch."

In Strands, a custom tool is a Python function decorated with special attributes:

- The `@tool` Decorator: marks a function as an agent tool
- Function Docstring: describes the tool and guides the agent on when and how to use it

## Step 1: Turn Your Function into a Tool

Open `agent_with_dice_roll_tool.py`: it already contains a plain Python function, `roll_dice`, that rolls `count` dice with `faces` faces each, drops the `drop_lowest` lowest ones and returns every die, the dice kept and their total. Your goal is to turn that function into a tool your agent can call.

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
 'inputSchema': {'json': {'properties': {
     'faces': {'default': 6, 'description': 'Parameter faces', 'type': 'integer'},  # only the parameter names
     'count': {'default': 1, 'description': 'Parameter count', 'type': 'integer'},
     'drop_lowest': {'default': 0, 'description': 'Parameter drop_lowest', 'type': 'integer'}},
   'type': 'object'}}}
```

Look at `description`: it contains only the function name, `roll_dice`, and the three parameters are described as nothing more than `Parameter faces`, `Parameter count` and `Parameter drop_lowest`. That is all the model will ever know about your tool: it never reads the function's code, it only receives what Strands builds from the name, the docstring and the typed parameters.

```python
# TODO: Step 2 - Write a docstring with the description, an Args section and the return value
```

Now write the docstring: a first paragraph saying what the tool does and how to call it for 4d6 drop lowest, an `Args:` section describing `faces`, `count` and `drop_lowest`, and what it returns, as in the documentation best practices.

Tip: LLMs are good at writing tool docstrings. Give them the function and an example of best practices, and let them generate a docstring for you.

Run the script again and compare the printed specification. You should see:

```
{'name': 'roll_dice',
 'description': '...',  # the docstring you added
 'inputSchema': {'json': {'properties': {
     'faces': {'default': 6, 'description': '...', 'type': 'integer'},  # the Args section of your docstring
     'count': {'default': 1, 'description': '...', 'type': 'integer'},
     'drop_lowest': {'default': 0, 'description': '...', 'type': 'integer'}},
   'type': 'object'}}}
```

The `Args:` section became the description of each parameter, the rest became the description of the tool.

Would it work without a docstring? Not reliably. `faces` is guessable, but nothing in `count` or `drop_lowest` tells the model that 4d6 drop lowest is a single call with `count=4, drop_lowest=1`, or that it should report the `total` instead of adding the dice itself. On Amazon Nova 2 Lite, an earlier design of this tool that rolled one die per call left the model to plan sixteen calls and do the arithmetic, and it skipped rolls and miscounted. Moving the work into the tool and documenting it fixed both.

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

> <img src="../images/icons/floor-boss-96x96.webp" alt="Floor boss" width="28" height="28"> **FLOOR BOSS:** Four abilities, four dice each, drop the lowest. Four calls, sixteen dice, zero arithmetic by the model. Lady Luck runs the table, and Lady Luck does not do favors.

Once TODOs are completed, run your script:

```bash
python agent_with_dice_roll_tool.py
```

The system prompt in the file turns the agent into Lady Luck, the System's croupier subroutine, who rolls every die on the broadcast. The script asks her to show the audience how the System rolled Cordula's sheet on day one: four ability scores (strength, wisdom, charisma and intelligence) with the 4d6-drop-lowest method: for each ability, roll four six-sided dice and keep the three highest. That is four tool calls, one per ability, each with `faces=6, count=4, drop_lowest=1`: sixteen dice in total, all rolled by your tool, which also drops the lowest and adds up the rest.

Watch the agent in action:

- Analyze the character creation request
- Plan one roll per ability (4d6 drop lowest each)
- Call your tool four times with `faces=6, count=4, drop_lowest=1`
- Report the four totals the tool returned
- Return the results

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **SYSTEM DESIGN, LAYER 3: HARD MATH.** Readers forgive a System for being cruel, never for being inconsistent. Ability scores, modifiers and dice are the math every later rule stands on, so they live in code, not in the model's head. In this crawl each of the six scores also maps to a dance-off Move Call: Strength is Power, Dexterity is Footwork, Constitution is Endurance, Intelligence is Choreography, Wisdom is Read the Room and Charisma is Presence. A score of 16 gives a +3 modifier: (score - 10) / 2, rounded down. See [ability scores](world/crawl-handbook/01-ability-scores.md) and [The System](world/the-system.md#2-stat-design).

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
> Reward: You received a [Silver Box]. Inside: a roll_dice tool that actually works, and sixteen dice that rolled exactly where the docstring told the model to roll them.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "You forged a tool. A real one. Floor 4 is where it leaves the house."
