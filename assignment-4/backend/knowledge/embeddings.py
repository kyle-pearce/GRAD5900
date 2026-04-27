"""
ChromaDB-compatible embedding function backed by Ollama's nomic-embed-text model.

nomic-embed-text produces 768-dimensional vectors.
This replaces the OpenAI text-embedding-3-small used in Assignment 2.
"""

from chromadb import EmbeddingFunction, Documents, Embeddings
import ollama
from ..core.config import settings


class OllamaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model: str | None = None):
        self.model = model or settings.embed_model

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            response = ollama.embeddings(model=self.model, prompt=text)
            embeddings.append(response["embedding"])
        return embeddings
