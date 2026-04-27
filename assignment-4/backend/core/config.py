from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_host: str = "http://localhost:11434"
    chat_model: str = "llama3.2:3b"
    embed_model: str = "nomic-embed-text"

    # Paths (relative to repo root — backend resolves absolute at startup)
    context_dir: Path = Path(__file__).resolve().parents[3] / "context"
    chroma_dir: Path = Path(__file__).resolve().parents[3] / ".chroma"
    handoffs_dir: Path = Path(__file__).resolve().parents[3] / "handoffs"

    # WSL2 mount paths for Kyle's default context files
    default_writing_style_src: Path = Path("/mnt/c/Users/kyle/Downloads/writing-style-draft.md")
    default_email_style_src: Path = Path("/mnt/c/Users/kyle/Downloads/email-style-draft.md")
    default_mental_model_src: Path = Path("/mnt/c/Users/kyle/Downloads/mental-model-draft.md")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
