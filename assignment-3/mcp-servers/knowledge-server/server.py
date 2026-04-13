"""
Knowledge Base MCP Server

Wraps the Assignment 2 RAG pipeline as MCP tools so Claude Code
can query and ingest documents natively.

How it works:
- This file is spawned by Claude Code as a child process
- It communicates over stdin/stdout using the MCP protocol
- It imports A2's existing modules (retriever.py, ingest.py) directly
- It shares the same .chroma/ database that A2 uses

Tools exposed:
- query_knowledge: search the knowledge base
- ingest_documents: ingest a directory of files
- ingest_single_file: ingest one file
- corpus_stats: check knowledge base status
"""

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Path setup: add A2's rag-assistant directory to Python's import path
# so we can import knowledge.retriever and knowledge.ingest directly.
#
# This assumes the repo structure is:
#   assignment-2/rag-assistant/knowledge/retriever.py
#   assignment-2/rag-assistant/knowledge/ingest.py
#   assignment-3/mcp-servers/knowledge-server/server.py  (this file)
# ---------------------------------------------------------------------------
A2_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "assignment-2" / "rag-assistant"
sys.path.insert(0, str(A2_ROOT))

# Load A2's .env file (contains ANTHROPIC_API_KEY and OPENAI_API_KEY)
from dotenv import load_dotenv
load_dotenv(A2_ROOT / ".env")

# Now we can import A2's modules
from knowledge.ingest import ingest_directory, ingest_file, get_collection
from knowledge.retriever import SelfCorrectingRetriever

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------
CHROMA_DIR = str(A2_ROOT / ".chroma")

mcp = FastMCP("knowledge-base")
_retriever = SelfCorrectingRetriever(persist_dir=CHROMA_DIR)


# ---------------------------------------------------------------------------
# Tool 1: query_knowledge
# ---------------------------------------------------------------------------
@mcp.tool()
def query_knowledge(question: str) -> str:
    """Search the personal knowledge base and return relevant context.

    Use this when the user asks about their goals, projects, past
    reflections, meeting notes, or anything from their handoff files.

    Args:
        question: The question to search for.

    Returns:
        Retrieved context chunks with relevance metadata.
    """
    chunks, meta = _retriever.retrieve(question)
    if not chunks:
        return "No relevant documents found in the knowledge base."

    score = meta["relevance_score"]
    corrected = ""
    if meta["corrected"]:
        corrected = f" (self-corrected \u2192 \"{meta['expanded_query'][:60]}\")"

    context = "\n\n---\n\n".join(chunks)
    return (
        f"[Retrieval] relevance={score:.2f}{corrected} | "
        f"{len(chunks)} chunks\n\n{context}"
    )


# ---------------------------------------------------------------------------
# Tool 2: ingest_documents
# ---------------------------------------------------------------------------
@mcp.tool()
def ingest_documents(directory: str) -> str:
    """Ingest all .md and .txt files from a directory into the knowledge base.

    Use this when the user wants to add new documents to their
    searchable memory, e.g. "ingest my meeting notes folder".

    Args:
        directory: Absolute or relative path to the directory.

    Returns:
        Summary of how many chunks were ingested.
    """
    path = Path(directory).expanduser().resolve()
    if not path.is_dir():
        return f"Error: '{directory}' is not a valid directory."
    count = ingest_directory(str(path), persist_dir=CHROMA_DIR)
    return f"Ingested {count} chunks from {path}"


# ---------------------------------------------------------------------------
# Tool 3: ingest_single_file
# ---------------------------------------------------------------------------
@mcp.tool()
def ingest_single_file(file_path: str) -> str:
    """Ingest a single .md or .txt file into the knowledge base.

    Use this after writing a handoff, meeting note, or any file
    that should be immediately searchable.

    Args:
        file_path: Absolute or relative path to the file.

    Returns:
        Summary of how many chunks were ingested from the file.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    fp = Path(file_path).expanduser().resolve()
    if not fp.exists():
        return f"Error: '{file_path}' not found."
    if fp.suffix not in {".md", ".txt"}:
        return f"Error: Only .md and .txt files are supported. Got '{fp.suffix}'."

    collection = get_collection(CHROMA_DIR)
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    count = ingest_file(fp, collection, splitter)
    return f"Ingested {fp.name}: {count} chunks"


# ---------------------------------------------------------------------------
# Tool 4: corpus_stats
# ---------------------------------------------------------------------------
@mcp.tool()
def corpus_stats() -> str:
    """Check the status of the knowledge base.

    Use this to verify the knowledge base is populated before querying,
    or to report how many documents are indexed.

    Returns:
        Collection name, document count, and storage location.
    """
    collection = get_collection(CHROMA_DIR)
    count = collection.count()
    return (
        f"Collection: {collection.name}\n"
        f"Documents indexed: {count} chunks\n"
        f"Storage: {CHROMA_DIR}"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
