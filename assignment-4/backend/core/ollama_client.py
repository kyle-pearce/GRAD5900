"""
Thin wrapper around the Ollama Python SDK.

Exposes three functions used throughout the backend:
  - stream_chat: yields text tokens for SSE streaming
  - chat: blocking single-turn call, returns full response string
  - embed: returns a float vector for a single text input
"""

from typing import Generator
import ollama
from .config import settings


def stream_chat(messages: list[dict], model: str | None = None) -> Generator[str, None, None]:
    """Stream chat tokens from Ollama. Yields one string token at a time."""
    model = model or settings.chat_model
    stream = ollama.chat(model=model, messages=messages, stream=True)
    for chunk in stream:
        token = chunk["message"]["content"]
        if token:
            yield token


def chat(messages: list[dict], model: str | None = None) -> str:
    """Blocking chat call. Returns the full assistant response as a string."""
    model = model or settings.chat_model
    response = ollama.chat(model=model, messages=messages, stream=False)
    return response["message"]["content"]


def embed(text: str, model: str | None = None) -> list[float]:
    """Return a single embedding vector for the given text."""
    model = model or settings.embed_model
    response = ollama.embeddings(model=model, prompt=text)
    return response["embedding"]
