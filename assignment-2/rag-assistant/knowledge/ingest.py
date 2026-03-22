"""
Document ingestion pipeline: chunk, embed, and store in ChromaDB.

Week 5 concept: chunks are the retrieval unit. Overlap preserves context
across chunk boundaries. Embedding model maps text to a shared vector space
so semantically similar chunks are geometrically close.
"""

import os
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 512       # tokens (~400 words) — balances specificity vs. context
CHUNK_OVERLAP = 64     # overlap preserves context at chunk boundaries
COLLECTION_NAME = "personal_assistant_docs"


def get_collection(persist_dir: str = ".chroma") -> chromadb.Collection:
    """Return (or create) the ChromaDB collection backed by OpenAI embeddings."""
    client = chromadb.PersistentClient(path=persist_dir)
    ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ["OPENAI_API_KEY"],
        model_name="text-embedding-3-small",
    )
    return client.get_or_create_collection(COLLECTION_NAME, embedding_function=ef)


def ingest_file(fp: Path, collection: chromadb.Collection, splitter: RecursiveCharacterTextSplitter) -> int:
    """Chunk a single file and upsert its chunks into the collection."""
    text = fp.read_text(encoding="utf-8", errors="ignore")
    chunks = splitter.split_text(text)
    if not chunks:
        return 0

    # Deterministic IDs let us re-ingest files without creating duplicates
    ids = [f"{fp.stem}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": str(fp), "chunk_index": i} for i in range(len(chunks))]
    collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)
    return len(chunks)


def ingest_directory(doc_dir: str, persist_dir: str = ".chroma") -> int:
    """
    Chunk and embed all .txt and .md files in doc_dir (recursively).
    Returns the total number of chunks stored.
    """
    collection = get_collection(persist_dir)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    total = 0
    for fp in Path(doc_dir).rglob("*"):
        if fp.suffix not in {".txt", ".md"}:
            continue
        count = ingest_file(fp, collection, splitter)
        print(f"  {fp.name}: {count} chunks")
        total += count

    print(f"\nDone. Total chunks stored: {total}")
    return total
