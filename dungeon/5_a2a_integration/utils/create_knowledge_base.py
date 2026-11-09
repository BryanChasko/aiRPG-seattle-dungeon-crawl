"""Build the Rules Agent knowledge base: a local ChromaDB collection of Crawl Handbook passages.

The Crawl Handbook is the crawl's own rule book, one Markdown file per section in
workshop/world/crawl-handbook/. Run this once from this folder:
    python create_knowledge_base.py
"""

import os
import sys
from pathlib import Path

import chromadb

HANDBOOK_DIR = Path(__file__).resolve().parent.parent.parent / "workshop" / "world" / "crawl-handbook"
DB_PATH = "./rules_knowledge_base"
COLLECTION = "crawl_handbook"
CHUNK_SIZE = 1000    # characters per passage
CHUNK_OVERLAP = 200  # characters shared by two consecutive passages, so a rule cut in two stays findable


def section_title(path: Path) -> str:
    """The section's first heading, e.g. "Dance-Offs" for 03-dance-offs.md."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def extract_chunks(handbook_dir: Path) -> list[dict]:
    """Read each handbook section and cut it into overlapping passages."""
    chunks = []
    for path in sorted(handbook_dir.glob("*.md")):
        section = section_title(path)
        text = path.read_text(encoding="utf-8").strip()
        start = 0
        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            if end < len(text):  # cut on a line break or a space, not in the middle of a word
                cut = max(text.rfind("\n", start + CHUNK_SIZE // 2, end), text.rfind(" ", start + CHUNK_SIZE // 2, end))
                if cut != -1:
                    end = cut
            passage = text[start:end].strip()
            if len(passage) > 50:
                chunks.append({
                    "id": f"{path.stem}_offset_{start}",
                    "text": passage,
                    "metadata": {"section": section, "source": path.name},
                })
            if end == len(text):
                break
            start = end - CHUNK_OVERLAP
    return chunks


def create_knowledge_base() -> None:
    print(f"Reading the Crawl Handbook from {HANDBOOK_DIR}...")
    chunks = extract_chunks(HANDBOOK_DIR)
    print(f"{len(chunks)} passages extracted")

    client = chromadb.PersistentClient(path=DB_PATH)
    if COLLECTION in [c.name for c in client.list_collections()]:
        print(f"Collection '{COLLECTION}' already exists, rebuilding it")
        client.delete_collection(COLLECTION)
    collection = client.create_collection(COLLECTION)

    print("Embedding passages into ChromaDB (the embedding model is downloaded on first run)...")
    batch = 100
    for i in range(0, len(chunks), batch):
        part = chunks[i:i + batch]
        collection.add(
            ids=[c["id"] for c in part],
            documents=[c["text"] for c in part],
            metadatas=[c["metadata"] for c in part],
        )
        print(f"  {min(i + batch, len(chunks))}/{len(chunks)}")

    print(f"Knowledge base created at {DB_PATH} ({collection.count()} passages in '{COLLECTION}')")


if __name__ == "__main__":
    if not HANDBOOK_DIR.is_dir():
        sys.exit(f"Crawl Handbook not found at {HANDBOOK_DIR}. Run this script from inside the repository.")
    create_knowledge_base()
    print("Knowledge base creation complete!")
