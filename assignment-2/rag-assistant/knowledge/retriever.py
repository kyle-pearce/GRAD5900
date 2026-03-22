"""
Hybrid retriever (vector + BM25) with a self-correcting retrieval loop.

Week 5 concepts implemented here:
  - Hybrid search: vector similarity (semantic) fused with BM25 (lexical/keyword)
  - Reciprocal Rank Fusion (RRF): rank-based fusion that is robust to score scale differences
  - Self-correcting loop: LLM judges retrieved context quality; if below threshold,
    the query is expanded and retrieval runs a second time
"""

import os
from typing import List, Tuple

import anthropic
from rank_bm25 import BM25Okapi

from .ingest import get_collection

# RRF constant — higher k reduces the impact of top-ranked documents
RRF_K = 60

# Minimum acceptable relevance score (0.0–1.0) before triggering self-correction
RELEVANCE_THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# Reciprocal Rank Fusion
# ---------------------------------------------------------------------------

def _rrf_fuse(
    vector_docs: List[str],
    bm25_docs: List[Tuple[str, float]],
    k: int = RRF_K,
) -> List[str]:
    """
    Merge two ranked lists using Reciprocal Rank Fusion.

    RRF score for a document d = sum over each list of 1 / (k + rank(d)).
    Documents appearing in both lists get a double boost.
    """
    scores: dict[str, float] = {}

    for rank, doc in enumerate(vector_docs):
        scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + rank + 1)

    for rank, (doc, _) in enumerate(bm25_docs):
        scores[doc] = scores.get(doc, 0.0) + 1.0 / (k + rank + 1)

    return [doc for doc, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]


# ---------------------------------------------------------------------------
# Hybrid Retriever
# ---------------------------------------------------------------------------

class HybridRetriever:
    """
    Combines ChromaDB vector search with BM25 keyword search, fused via RRF.

    Why hybrid?
      - Vector search captures semantic similarity but can miss exact keyword matches.
      - BM25 is strong on rare terms and proper nouns but ignores meaning.
      - RRF fusion gets the best of both without needing to tune score scales.
    """

    def __init__(self, persist_dir: str = ".chroma", top_k: int = 5):
        self.collection = get_collection(persist_dir)
        self.top_k = top_k
        self._corpus_cache: List[str] | None = None

    def _load_corpus(self) -> List[str]:
        """Lazily load all documents from ChromaDB for BM25 indexing."""
        if self._corpus_cache is None:
            result = self.collection.get()
            self._corpus_cache = result.get("documents") or []
        return self._corpus_cache

    def retrieve(self, query: str) -> List[str]:
        # --- Vector search via ChromaDB ---
        vec_result = self.collection.query(query_texts=[query], n_results=self.top_k)
        vec_docs: List[str] = vec_result["documents"][0] if vec_result["documents"] else []

        # --- BM25 keyword search over full corpus ---
        corpus = self._load_corpus()
        if not corpus:
            return vec_docs

        tokenized = [doc.lower().split() for doc in corpus]
        bm25 = BM25Okapi(tokenized)
        raw_scores = bm25.get_scores(query.lower().split())
        bm25_ranked = sorted(zip(corpus, raw_scores), key=lambda x: x[1], reverse=True)[: self.top_k]

        # --- Fuse and return top_k ---
        fused = _rrf_fuse(vec_docs, bm25_ranked, k=RRF_K)
        return fused[: self.top_k]


# ---------------------------------------------------------------------------
# Self-Correcting Retriever
# ---------------------------------------------------------------------------

class SelfCorrectingRetriever:
    """
    Wraps HybridRetriever with an LLM-as-judge self-correction loop.

    Flow:
      1. Retrieve with HybridRetriever.
      2. Ask a fast LLM (Haiku) to score how relevant the context is (0.0–1.0).
      3. If score < RELEVANCE_THRESHOLD, expand the query and retrieve again.
      4. Return final chunks plus metadata about whether correction occurred.

    This implements the "self-correcting retrieval loop" from RAG 2.0 (Week 5).
    """

    def __init__(self, persist_dir: str = ".chroma", top_k: int = 5):
        self.hybrid = HybridRetriever(persist_dir=persist_dir, top_k=top_k)
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def _judge_relevance(self, query: str, chunks: List[str]) -> float:
        """
        Ask the LLM to rate context relevance on a 0.0–1.0 scale.
        Uses only the top 3 chunks to keep the prompt short.
        """
        context_text = "\n\n---\n\n".join(chunks[:3])
        prompt = (
            f"Rate how relevant the following context is for answering this question.\n"
            f"Respond with ONLY a decimal number between 0.0 (irrelevant) and 1.0 (perfect).\n\n"
            f"Question: {query}\n\n"
            f"Context:\n{context_text}\n\n"
            f"Relevance score:"
        )
        response = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}],
        )
        try:
            return float(response.content[0].text.strip())
        except ValueError:
            return 0.5  # assume marginal if parse fails

    def _expand_query(self, query: str) -> str:
        """
        Ask the LLM to rewrite the query with additional terms and synonyms
        to improve recall on a second retrieval pass.
        """
        response = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=80,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Rewrite the following search query to include related terms and synonyms "
                        f"that would help retrieve more relevant documents. "
                        f"Return only the rewritten query, nothing else.\n\nOriginal: {query}"
                    ),
                }
            ],
        )
        return response.content[0].text.strip()

    def retrieve(self, query: str) -> Tuple[List[str], dict]:
        """
        Retrieve with self-correction.

        Returns:
            chunks: List of retrieved text chunks
            meta: {
                "relevance_score": float,   # LLM judge score after initial retrieval
                "corrected": bool,          # True if a second retrieval pass ran
                "expanded_query": str|None  # The rewritten query if correction occurred
            }
        """
        chunks = self.hybrid.retrieve(query)
        score = self._judge_relevance(query, chunks)

        meta = {"relevance_score": score, "corrected": False, "expanded_query": None}

        if score < RELEVANCE_THRESHOLD:
            expanded = self._expand_query(query)
            meta["expanded_query"] = expanded
            chunks = self.hybrid.retrieve(expanded)
            meta["corrected"] = True

        return chunks, meta
