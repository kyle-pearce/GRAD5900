"""
RAGAS evaluation harness — Week 7: LLM-as-a-Judge.

This script:
  1. Loads a golden Q&A dataset (ground-truth question/answer pairs).
  2. Runs each question through two retriever configurations:
       - HybridRetriever (vector + BM25, no correction)
       - SelfCorrectingRetriever (hybrid + LLM judge loop)
  3. Generates answers using Claude for each retrieved context.
  4. Scores every (question, answer, context, ground_truth) tuple with RAGAS:
       - Faithfulness:        Does the answer stay grounded in the retrieved context?
       - Answer Relevancy:    Does the answer address the question?
       - Context Precision:   Were the retrieved chunks actually relevant?
       - Context Recall:      Did retrieval surface the chunks needed for a correct answer?
  5. Prints a side-by-side comparison table and saves results to eval/results/.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

import anthropic
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)

# Allow running from the project root: python -m eval.evaluate
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge.retriever import HybridRetriever, SelfCorrectingRetriever

GOLDEN_DATASET_PATH = Path(__file__).parent / "golden_dataset.json"
RESULTS_DIR = Path(__file__).parent / "results"
METRICS = [faithfulness, answer_relevancy, context_precision, context_recall]
METRIC_NAMES = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_golden_dataset() -> list[dict]:
    with open(GOLDEN_DATASET_PATH) as f:
        data = json.load(f)
    # Strip metadata-only entries
    return [item for item in data if "question" in item and "_comment" not in item]


def generate_answer(question: str, context_chunks: list[str]) -> str:
    """Generate a grounded answer from retrieved context using Claude."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    context_text = "\n\n---\n\n".join(context_chunks)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Answer the following question using only the provided context. "
                    f"Be concise and direct. If the context is insufficient, say so.\n\n"
                    f"Context:\n{context_text}\n\n"
                    f"Question: {question}"
                ),
            }
        ],
    )
    return response.content[0].text.strip()


# ---------------------------------------------------------------------------
# Evaluation runner
# ---------------------------------------------------------------------------

def run_evaluation(
    name: str,
    retriever,
    dataset: list[dict],
) -> dict[str, Any]:
    """
    Run one retriever config against the full golden dataset.
    Returns a dict of RAGAS metric name -> score.
    """
    print(f"\n{'─' * 50}")
    print(f"Running: {name}")
    print(f"{'─' * 50}")

    questions, answers, contexts, ground_truths = [], [], [], []

    for item in dataset:
        question = item["question"]
        ground_truth = item["ground_truth"]

        # Retrieve — handle both retriever signatures
        if isinstance(retriever, SelfCorrectingRetriever):
            chunks, meta = retriever.retrieve(question)
            tag = " [corrected]" if meta["corrected"] else ""
            print(f"  Q: {question[:55]}...{tag}")
        else:
            chunks = retriever.retrieve(question)
            print(f"  Q: {question[:55]}...")

        answer = generate_answer(question, chunks)

        questions.append(question)
        answers.append(answer)
        contexts.append(chunks)          # RAGAS expects List[List[str]]
        ground_truths.append(ground_truth)

    ragas_dataset = Dataset.from_dict(
        {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        }
    )

    result = evaluate(ragas_dataset, metrics=METRICS)
    return dict(result)


# ---------------------------------------------------------------------------
# Comparison report
# ---------------------------------------------------------------------------

def print_comparison(results: dict[str, dict[str, Any]]) -> None:
    col_w = 22
    name_w = 28
    header = f"{'Configuration':<{name_w}}" + "".join(f"{m:<{col_w}}" for m in METRIC_NAMES)
    divider = "─" * len(header)

    print(f"\n{'=' * len(header)}")
    print("RAGAS Evaluation Results")
    print(f"{'=' * len(header)}")
    print(header)
    print(divider)

    for config_name, scores in results.items():
        row = f"{config_name:<{name_w}}" + "".join(
            f"{scores.get(m, float('nan')):<{col_w}.4f}" for m in METRIC_NAMES
        )
        print(row)

    print(f"{'=' * len(header)}")


def save_results(results: dict[str, Any]) -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    output = RESULTS_DIR / "latest.json"
    with open(output, "w") as f:
        json.dump(results, f, indent=2)
    return output


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(persist_dir: str = ".chroma") -> None:
    dataset = load_golden_dataset()
    print(f"Loaded {len(dataset)} golden examples.")

    configs = {
        "Hybrid (vector + BM25)": HybridRetriever(persist_dir=persist_dir),
        "Self-correcting": SelfCorrectingRetriever(persist_dir=persist_dir),
    }

    results = {}
    for name, retriever in configs.items():
        results[name] = run_evaluation(name, retriever, dataset)

    print_comparison(results)

    output_path = save_results(results)
    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
