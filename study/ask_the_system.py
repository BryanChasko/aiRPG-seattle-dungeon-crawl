"""Ask the System: a study companion for the crawl, built with the same SDK you are learning.

Ask it anything about a floor, a TODO, an error message or a Strands API, and it answers in
the System's voice from two sources only: the pages of this repository and the Strands API
reference. It cites both, and says so when it does not know.

    python study/ask_the_system.py                      # chat; type exit to leave
    python study/ask_the_system.py "what is an agent card?"

Strands concepts on show, most of them beyond the base floors:
- @tool functions with docstrings (Floor 3)
- full-text search with strands.storage: LocalFileStorage and Bm25SearchStrategy
- a session that survives restarts with FileSessionManager (Floor 7 does the same through the harness)
- a sliding window so a long study session never overflows the context
"""

from __future__ import annotations

import asyncio
import html
import re
import sys
import urllib.request
from pathlib import Path

from strands import Agent, tool
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from strands.storage import LocalFileStorage
from strands.storage.search.bm25 import Bm25SearchStrategy

ROOT = Path(__file__).resolve().parent.parent
STATE = Path(__file__).resolve().parent / ".state"  # gitignored: the search index and the chat session
PAGES = sorted(
    [*ROOT.glob("README.md"), *ROOT.glob("workshop/*.md"), *ROOT.glob("workshop/world/*.md"),
     *ROOT.glob("workshop/world/crawl-handbook/*.md")]
)
API_PAGE = "https://strandsagents.com/docs/api/python/{module}/"
MODULE_NAME = re.compile(r"^strands(\.[a-z0-9_]+){0,6}$")
MAX_PAGE_CHARS = 6000

_storage = LocalFileStorage(str(STATE / "pages"))


async def _build_index() -> None:
    """Index every page once per run. Keys are repository-relative paths, so answers can cite them."""
    search = Bm25SearchStrategy()
    try:
        for page in PAGES:
            await search.index(_storage, page.relative_to(ROOT).as_posix(), page.read_bytes())
    finally:
        await search.close()


async def _search_pages(query: str):
    # a fresh strategy per call: its lock belongs to one event loop, and the index lives on disk anyway
    search = Bm25SearchStrategy()
    try:
        return await search.search(_storage, query)
    finally:
        await search.close()


def _run(coro):
    return asyncio.run(coro)


def _strip_html(raw: str) -> str:
    parts = re.split(r"<main[^>]*>", raw, maxsplit=1)
    main = parts[-1].split("</main>", 1)[0]
    main = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", main, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", main))).strip()


@tool
def search_workshop(query: str) -> str:
    """Search the pages of this workshop: the floors, the world guide and the Crawl Handbook.

    Use it first for any question about a floor, a TODO, a command, a file or a rule of the
    crawl. The search is BM25 keyword search: every word of the query must appear in a page, so
    use two or three distinctive words ("agent card", "drop_lowest", "Final Beat"), not a
    sentence. If nothing comes back, try fewer or different words.

    Args:
        query: Two or three distinctive words to look for.

    Returns:
        Up to five matching pages, best first, as "path (score)" lines, or a note that nothing matched.
    """
    hits = _run(_search_pages(query))[:5]
    if not hits:
        return f"No page contains all of: {query}. Try fewer or different words."
    return "\n".join(f"{h.key} ({h.score:.2f})" for h in hits)


@tool
def read_workshop_page(path: str, find: str = "") -> str:
    """Read one page of this workshop, by the path search_workshop returned.

    Args:
        path: A repository-relative path such as "workshop/floor-5.md".
        find: Optional word or phrase; when given, the text starts a little before its first
            occurrence instead of at the top of the page.

    Returns:
        Up to 6,000 characters of the page, or an error if the path is not a workshop page.
    """
    allowed = {p.relative_to(ROOT).as_posix(): p for p in PAGES}
    if path not in allowed:
        return f"Not a workshop page: {path}. Use a path from search_workshop."
    text = allowed[path].read_text(encoding="utf-8")
    start = max(0, text.lower().find(find.lower()) - 500) if find and find.lower() in text.lower() else 0
    return text[start:start + MAX_PAGE_CHARS]


@tool
def strands_api_reference(module: str) -> str:
    """Read the Strands Agents SDK API reference page for one Python module.

    Use it to check a class, a function or an argument before you explain it, for example
    "strands.multiagent.a2a.server", "strands.tools.mcp.mcp_client" or
    "strands.agent.conversation_manager.summarizing_conversation_manager".

    Args:
        module: A dotted module path that starts with "strands".

    Returns:
        The page as plain text (first 6,000 characters) followed by its URL, or an error.
    """
    if not MODULE_NAME.match(module):
        return f"Not a Strands module path: {module!r}. Use dotted names such as strands.tools.decorator."
    url = API_PAGE.format(module=module)
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            text = _strip_html(resp.read().decode("utf-8", "replace"))
    except Exception as err:  # noqa: BLE001 - every failure is reported to the model, never hidden
        return f"Could not read {url}: {err}"
    return f"{text[:MAX_PAGE_CHARS]}\n\nSource: {url}"


SYSTEM_PROMPT = """You are the System, the petty, theatrical broadcast AI that runs a dungeon crawl under Seattle, \
working the help desk in the Safe Room. The person typing is a Crawler learning the Strands Agents SDK by \
building you, one floor at a time. Be funny for one sentence, then be exactly right.
How you answer:
- For anything about the workshop (a floor, a TODO, a command, a file, a rule), call search_workshop with two or three \
distinctive words, then read_workshop_page, and answer from what the page says.
- For anything about a Strands class, function or argument, call strands_api_reference before you explain it.
- Cite your sources at the end: the page path (for example workshop/floor-5.md) and the API reference URL.
- Never invent an API, an argument or a file. If the pages and the reference do not say, answer that you do not know \
and say where to look.
- When the Crawler is stuck on a TODO, give a hint first and the answer only if they ask for it. The answers live on \
the solution branch.
- Plain text only: no markdown, no emoji. Short paragraphs. Code goes on its own lines."""


def build_agent(session_id: str = "study") -> Agent:
    return Agent(
        model=BedrockModel(model_id="us.amazon.nova-2-lite-v1:0"),
        system_prompt=SYSTEM_PROMPT,
        tools=[search_workshop, read_workshop_page, strands_api_reference],
        session_manager=FileSessionManager(session_id=session_id, storage_dir=str(STATE / "sessions")),
        conversation_manager=SlidingWindowConversationManager(window_size=30),
    )


def main(argv: list[str]) -> None:
    STATE.mkdir(exist_ok=True)
    _run(_build_index())
    agent = build_agent()
    if len(argv) > 1:
        agent(" ".join(argv[1:]))
        print()
        return
    print("SYSTEM: The help desk is open. Ask about any floor, any TODO, any Strands API. Type exit to leave.")
    while True:
        try:
            question = input("\nCrawler> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() in {"exit", "quit"}:
            break
        if question:
            agent(question)
            print()


if __name__ == "__main__":
    main(sys.argv)
