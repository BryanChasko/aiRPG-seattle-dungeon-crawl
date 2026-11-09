"""Floor 7 encounter, Keyword versus Vector: two ways to search the Crawl Handbook, judged on the Final Beat.

Both searchers get the same passages, the ones Floor 5 cut from the Crawl Handbook. The keyword searcher
is the Strands BM25 strategy, a SQLite full-text index on local disk. The vector searcher is a local
ChromaDB collection, as on Floor 5. Each round is a question; the judge is code: it finds the Final Beat
passage in each ranked list and gives the round to the searcher that put it higher. No model is called.

Run it from this folder, with the workshop environment active:
    python keyword_versus_vector.py
"""

import asyncio
import shutil
import sys
import tempfile
from pathlib import Path

import chromadb

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "5_a2a_integration" / "utils"))  # Floor 5's passage cutter
from create_knowledge_base import HANDBOOK_DIR, extract_chunks
from strands.storage import LocalFileStorage
# TODO: Step 1 - Import Bm25SearchStrategy from strands.storage.search.bm25
from strands.storage.search.bm25 import Bm25SearchStrategy

FINAL_BEAT = "04-final-beat"  # the handbook file the right answer lives in
TOP = 5  # how many passages each searcher gets to hand back
ROUNDS = [
    "what happens when we tie?",
    "tie",
    "tiebreaker",
    "closest to 20 without going over",
    "who wins when it is level",
]


def section_of(key: str) -> str:
    """The handbook file a passage came from: '04-final-beat_offset_0.md' -> '04-final-beat'."""
    return key.removesuffix(".md").split("_offset_")[0]


def rank_of(keys: list[str]) -> int | None:
    """Where the Final Beat passage sits in a ranked list, 1 for first; None when the searcher missed it."""
    for place, key in enumerate(keys, start=1):
        if section_of(key) == FINAL_BEAT:
            return place
    return None


def keyword_arena(folder: str, chunks: list[dict]) -> LocalFileStorage:
    """A folder of passages with a BM25 index over them. Writing a file indexes it."""
    # TODO: Step 2 - Create a LocalFileStorage at folder whose search_strategy is a Bm25SearchStrategy()
    storage = LocalFileStorage(folder, search_strategy=Bm25SearchStrategy())

    async def write_all() -> None:
        for chunk in chunks:
            await storage.write(f"{chunk['id']}.md", chunk["text"].encode("utf-8"))

    asyncio.run(write_all())
    return storage


def keyword_search(storage: LocalFileStorage, query: str) -> list[str]:
    """The keys of the passages BM25 found, best first. Every word of the question has to be in a passage."""
    # TODO: Step 3 - Run storage.search(query) with asyncio.run and return the key of each of the first TOP results, in order
    return [result.key for result in asyncio.run(storage.search(query))[:TOP]]


def vector_arena(chunks: list[dict]):
    """A ChromaDB collection in memory. Chroma embeds each passage on this machine with its built-in embedder."""
    collection = chromadb.EphemeralClient().get_or_create_collection("keyword_versus_vector")
    collection.add(ids=[c["id"] for c in chunks], documents=[c["text"] for c in chunks])
    return collection


def vector_search(collection, query: str) -> list[str]:
    """The ids of the TOP passages nearest to the question in meaning, closest first."""
    # TODO: Step 4 - Query the collection with query_texts=[query] and n_results=TOP, and return the first list under "ids"
    return collection.query(query_texts=[query], n_results=TOP)["ids"][0]


def judge(keyword_rank: int | None, vector_rank: int | None) -> str:
    """The searcher that put the Final Beat higher takes the round. A miss loses to anything."""
    worst = TOP + 1
    keyword, vector = keyword_rank or worst, vector_rank or worst
    return "keyword" if keyword < vector else "vector" if vector < keyword else "draw"


def show(rank: int | None) -> str:
    return f"{rank}" if rank else "missed"


if __name__ == "__main__":
    chunks = extract_chunks(HANDBOOK_DIR)
    workbench = tempfile.mkdtemp(prefix="keyword-versus-vector-")  # the BM25 index file lands beside the passages folder
    print(f"{len(chunks)} passages from the Crawl Handbook, the Final Beat is in {FINAL_BEAT}\n")

    storage = keyword_arena(str(Path(workbench) / "passages"), chunks)
    collection = vector_arena(chunks)

    wins = {"keyword": 0, "vector": 0, "draw": 0}
    for number, query in enumerate(ROUNDS, start=1):
        keyword_rank = rank_of(keyword_search(storage, query))
        vector_rank = rank_of(vector_search(collection, query))
        winner = judge(keyword_rank, vector_rank)
        wins[winner] += 1
        print(f"ROUND {number}: {query!r}")
        print(f"  keyword put the Final Beat: {show(keyword_rank)}    vector put the Final Beat: {show(vector_rank)}    -> {winner}")

    print(f"\nkeyword {wins['keyword']}, vector {wins['vector']}, draws {wins['draw']}")
    shutil.rmtree(workbench, ignore_errors=True)
