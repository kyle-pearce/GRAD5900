"""
Hybrid retriever (vector + BM25 + RRF) with self-correcting loop.

Ported from Assignment 2. Key change: Claude Haiku replaced by llama3.2:3b
(via core.ollama_client) for relevance judging and query expansion.
"""

from typing import List, Tuple
from rank_bm25 import BM25Okapi

from .ingest import get_collection
from ..core.ollama_client import chat

RRF_K = 60
RELEVANCE_THRESHOLD = 0.5


def _rrf_fuse(vector_docs: List[str], bm25_docs: List[Tuple[str, float]], k: int = RRF_K) -> List[str]:
    scores: dict[str, float] = {}
    for rank, doc in enumerate(vector_docs):
        scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + rank + 1)
    for rank, (doc, _) in enumerate(bm25_docs):
        scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + rank + 1)
    return [doc for doc, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]


class HybridRetriever:
    def __init__(self, persist_dir: str | None = None, top_k: int = 5):
        self.collection = get_collection(persist_dir)
        self.top_k = top_k
        self._corpus_cache: List[str] | None = None

    def _load_corpus(self) -> List[str]:
        if self._corpus_cache is None:
            result = self.collection.get()
            self._corpus_cache = result.get("documents") or []
        return self._corpus_cache

    def retrieve(self, query: str) -> List[str]:
        vec_result = self.collection.query(query_texts=[query], n_results=self.top_k)
        vec_docs: List[str] = vec_result["documents"][0] if vec_result["documents"] else []

        corpus = self._load_corpus()
        if not corpus:
            return vec_docs

        tokenized = [doc.lower().split() for doc in corpus]
        bm25 = BM25Okapi(tokenized)
        raw_scores = bm25.get_scores(query.lower().split())
        bm25_ranked = sorted(zip(corpus, raw_scores), key=lambda x: x[1], reverse=True)[: self.top_k]

        fused = _rrf_fuse(vec_docs, bm25_ranked, k=RRF_K)
        return fused[: self.top_k]


class SelfCorrectingRetriever:
    def __init__(self, persist_dir: str | None = None, top_k: int = 5):
        self.hybrid = HybridRetriever(persist_dir=persist_dir, top_k=top_k)

    def _judge_relevance(self, query: str, chunks: List[str]) -> float:
        context_text = "\n\n---\n\n".join(chunks[:3])
        prompt = (
            f"Rate how relevant the following context is for answering this question.\n"
            f"Respond with ONLY a decimal number between 0.0 (irrelevant) and 1.0 (perfect).\n\n"
            f"Question: {query}\n\nContext:\n{context_text}\n\nRelevance score:"
        )
        try:
            result = chat([{"role": "user", "content": prompt}])
            return float(result.strip().split()[0])
        except (ValueError, IndexError):
            return 0.5

    def _expand_query(self, query: str) -> str:
        result = chat([{
            "role": "user",
            "content": (
                f"Rewrite the following search query to include related terms and synonyms "
                f"that would help retrieve more relevant documents. "
                f"Return only the rewritten query, nothing else.\n\nOriginal: {query}"
            ),
        }])
        return result.strip()

    def retrieve(self, query: str) -> Tuple[List[str], dict]:
        chunks = self.hybrid.retrieve(query)
        score = self._judge_relevance(query, chunks)
        meta = {"relevance_score": score, "corrected": False, "expanded_query": None}

        if score < RELEVANCE_THRESHOLD:
            expanded = self._expand_query(query)
            meta["expanded_query"] = expanded
            chunks = self.hybrid.retrieve(expanded)
            meta["corrected"] = True

        return chunks, meta


def query_knowledge(question: str) -> dict:
    """Top-level helper used by the API and skills."""
    retriever = SelfCorrectingRetriever()
    chunks, meta = retriever.retrieve(question)
    return {"chunks": chunks, "meta": meta}
