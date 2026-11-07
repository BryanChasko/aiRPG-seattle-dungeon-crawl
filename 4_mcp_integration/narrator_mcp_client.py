from strands import Agent
# TODO: Step 1 - Import MCPClient from strands.tools.mcp

# TODO: Step 1 - Create an MCPClient with the url "http://localhost:8002/mcp"

narrator = Agent(
    model="us.amazon.nova-2-lite-v1:0",  # Amazon Nova 2 Lite, US cross-Region inference profile
    system_prompt="""You are Lady Luck, the System's croupier subroutine and keeper of every die in this dungeon.
    You announce each roll like an arena announcer, mock low rolls with delight, and greet high rolls with visible disappointment.
    Your dice now live on a server across the room: always use the tool for every roll and report the total it returns. Plain text only, no emoji."""
    # TODO: Step 2 - Add the MCP tool to the narrator agent
)

narrator("Help me create a new fantasy character! Roll the strength, wisdom, charisma and intelligence abilities scores using 4d6 drop lowest method.")
