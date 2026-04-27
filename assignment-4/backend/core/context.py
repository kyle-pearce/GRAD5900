"""
Load personal context files into a dict keyed by filename stem.

Each skill declares REQUIRED_CONTEXT = ["goals.md", "projects.md"].
Only the declared files are read — avoids loading unnecessary context.
"""

from pathlib import Path
from .config import settings


def load_context(files: list[str]) -> dict[str, str]:
    """
    Load the requested context files from the configured context directory.
    Returns a dict mapping filename stem → file content.
    Missing files return an empty string (skill degrades gracefully).
    """
    result: dict[str, str] = {}
    for filename in files:
        path = settings.context_dir / filename
        stem = Path(filename).stem
        if path.exists():
            result[stem] = path.read_text(encoding="utf-8").strip()
        else:
            result[stem] = ""
    return result
