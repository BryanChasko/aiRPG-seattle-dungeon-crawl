# Floor 6: The Arena (Web Interface)

![Floor 6: The Arena (Web Interface)](../images/floors/floor-6-1200x675.webp)

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Floor 6. Time to show the audience what you built. Fill in your character, point it at port 8009, and press Start. No pressure. Only billions of viewers."

## Floor Objective

You've built a Narrator with custom tools, an MCP server and A2A agents. Test it in real life with our basic web interface.

## Web Interface

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "The arena is a public HTTPS page that calls your localhost. The browser allows it because 127.0.0.1 is you. Nobody else is invited. Yet."

Once all your agents and MCP servers are running, use the web interface at https://bryanchasko.github.io/strands-dungeon-crawl/.

The interface lives in this repository under `web/` (Vue 3 + Vite). To run it on your own machine instead, with Node.js 20 or later:

```bash
cd strands-dungeon-crawl/web
npm ci
npm run dev
```

### Connect Your Narrator

> <img src="../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[OPENING NIGHT JITTERS]**
>
> Reward: You received a [Bronze Box]. Inside: one character sheet, one Start button, and a stage light pointed directly at you.

In the web interface:

- Fill in your character: name, gender, race and class
- In Server URL, enter the URL shown in your Narrator Orchestrator terminal: `http://127.0.0.1:8009`
- Click Start

The web interface runs in your browser and talks to the Narrator running on the same machine. Browsers let this HTTPS page reach `http://127.0.0.1:8009` because it is localhost.

Monitor performance: watch your terminal logs to see how your Narrator processes requests:

```
Processing request...
Tool #1: a2a_client
Tool #2: roll_dice
response='...' actions_suggestions=[...] details='...' dice_rolls=[...]
INFO:     127.0.0.1:53210 - "POST /inquire HTTP/1.1" 200 OK
```

Customization ideas:

- Modify system prompts to change your Narrator's personality
- Add new custom tools for different mechanics
- Integrate additional MCP servers for new capabilities

## Troubleshooting

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Safari has not been tested. The System does not test Safari. Chrome or Firefox, Crawler."

Browser:

- Do not run this in Safari: it has not been tested
- Use Google Chrome or Mozilla Firefox, both work

"Connection Refused" error:

- Verify your Narrator is running on port 8009
- Check that no firewall is blocking the connection

"Invalid Server URL" message:

- Make sure the URL is exactly `http://127.0.0.1:8009`, with no space or path after the port
- Check for typos in the URL entry

Slow response times:

- Monitor your local machine's resource usage
- Check your internet connection stability
- Consider optimizing your agent's model configuration

## Floor Clear

Floor cleared, Crawler. You've connected your Narrator to a web interface and tested it end to end.

Loot you're keeping:

- Connecting your local Narrator to the web interface
- Testing your agent's responses through the web interface
- Following your agent's tool calls in the terminal

<img src="../images/icons/stairwell-96x96.webp" alt="Stairwell" width="24" height="24"> **Stairwell:** Explore [Floor 7](floor-7.md) for advanced enhancements you can add to your system.


> <img src="../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[OPENING NIGHT]**
>
> Reward: You received a [Bronze Box]. Inside: a browser tab, a character sheet, and the faint smell of stage fright.

> <img src="../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "It works end to end. Do not tell the sponsors it was easy."
