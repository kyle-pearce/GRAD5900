from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_host: str = "http://localhost:11434"
    chat_model: str = "llama3.2:3b"
    embed_model: str = "nomic-embed-text"

    # Paths anchored to assignment-4/ (parents[2] from backend/core/config.py)
    context_dir: Path = Path(__file__).resolve().parents[2] / "context"
    chroma_dir: Path = Path(__file__).resolve().parents[2] / ".chroma"
    handoffs_dir: Path = Path(__file__).resolve().parents[2] / "handoffs"
    defaults_dir: Path = Path(__file__).resolve().parents[2] / "context" / "defaults"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
