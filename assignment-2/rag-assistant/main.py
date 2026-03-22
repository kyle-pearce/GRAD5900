"""
RAG Personal Assistant — Phase 2 demo CLI.

Commands:
  python main.py ingest <doc_dir>   Chunk, embed, and store all .txt/.md files
  python main.py query  "<question>" Ask a question against the knowledge base
  python main.py eval               Run RAGAS evaluation across all configurations
"""

import argparse
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()


def do_ingest(doc_dir: str) -> None:
    from knowledge.ingest import ingest_directory
    print(f"Ingesting documents from: {doc_dir}")
    ingest_directory(doc_dir)


def do_query(question: str) -> None:
    from knowledge.retriever import SelfCorrectingRetriever

    retriever = SelfCorrectingRetriever()
    chunks, meta = retriever.retrieve(question)

    score = meta["relevance_score"]
    tag = ""
    if meta["corrected"]:
        tag = f" → self-corrected (expanded: \"{meta['expanded_query'][:60]}...\")"

    print(f"\n[Retrieval] relevance={score:.2f}{tag}")
    print(f"[Context]  {len(chunks)} chunk(s) retrieved\n")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    context_text = "\n\n---\n\n".join(chunks)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Answer this question using only the provided context. "
                    f"Be direct and concise. Cite the relevant passage when helpful.\n\n"
                    f"Context:\n{context_text}\n\n"
                    f"Question: {question}"
                ),
            }
        ],
    )
    print(f"Answer: {response.content[0].text.strip()}\n")


def do_eval() -> None:
    from eval.evaluate import main as run_eval
    run_eval()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RAG Personal Assistant (Phase 2 — Week 5 + Week 7)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    ingest_p = sub.add_parser("ingest", help="Ingest documents into the knowledge base")
    ingest_p.add_argument("doc_dir", help="Directory containing .txt / .md files")

    query_p = sub.add_parser("query", help="Ask a question")
    query_p.add_argument("question", help="The question to answer")

    sub.add_parser("eval", help="Run RAGAS evaluation across retriever configurations")

    args = parser.parse_args()

    if args.cmd == "ingest":
        do_ingest(args.doc_dir)
    elif args.cmd == "query":
        do_query(args.question)
    elif args.cmd == "eval":
        do_eval()


if __name__ == "__main__":
    main()
