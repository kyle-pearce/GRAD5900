"""
Document ingestion pipeline: chunk, embed (via Ollama nomic-embed-text), store in ChromaDB.

Ported from Assignment 2. Key change: OllamaEmbeddingFunction replaces
OpenAI text-embedding-3-small. The .chroma/ database in A4 is separate
from A2's (incompatible vector dimensions: 768 vs 1536).
"""

from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .embeddings import OllamaEmbeddingFunction
from ..core.config import settings

CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
COLLECTION_NAME = "personal_assistant_docs"


def get_collection(persist_dir: str | None = None) -> chromadb.Collection:
    persist_dir = persist_dir or str(settings.chroma_dir)
    client = chromadb.PersistentClient(path=persist_dir)
    ef = OllamaEmbeddingFunction()
    return client.get_or_create_collection(COLLECTION_NAME, embedding_function=ef)


def ingest_file(fp: Path, collection: chromadb.Collection, splitter: RecursiveCharacterTextSplitter) -> int:
    text = fp.read_text(encoding="utf-8", errors="ignore")
    chunks = splitter.split_text(text)
    if not chunks:
        return 0
    ids = [f"{fp.stem}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": str(fp), "chunk_index": i} for i in range(len(chunks))]
    collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)
    return len(chunks)


def ingest_directory(doc_dir: str, persist_dir: str | None = None) -> int:
    collection = get_collection(persist_dir)
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    total = 0
    for fp in Path(doc_dir).rglob("*"):
        if fp.suffix not in {".txt", ".md"}:
            continue
        total += ingest_file(fp, collection, splitter)
    return total


def ingest_single(file_path: str, persist_dir: str | None = None) -> int:
    fp = Path(file_path)
    if not fp.exists() or fp.suffix not in {".txt", ".md"}:
        return 0
    collection = get_collection(persist_dir)
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return ingest_file(fp, collection, splitter)
