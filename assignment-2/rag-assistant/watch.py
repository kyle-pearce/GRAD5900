"""
Filesystem watcher: automatically re-ingests handoff files as they are written.

Instead of manually running `python main.py ingest` on a schedule, this script
watches one or more directories and triggers ingest for each file as it is
created or modified. Uses the same upsert logic as the manual pipeline, so
re-processing a file is always safe — no duplicates.

Usage:
    # Watch the default A1 handoffs directory
    python watch.py

    # Watch a custom directory
    python watch.py path/to/handoffs/

    # Watch multiple directories
    python watch.py path/to/handoffs/ ~/notes/grad5900/
"""

import argparse
import logging
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from knowledge.ingest import CHUNK_OVERLAP, CHUNK_SIZE, get_collection, ingest_file

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [watcher] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Default: the A1 handoffs directory relative to this file's location
DEFAULT_WATCH_PATH = (
    Path(__file__).parent.parent.parent
    / "assignment-1"
    / "ai-assistant"
    / "handoffs"
)


class HandoffHandler(FileSystemEventHandler):
    """Re-ingests any .md or .txt file that is created, modified, or moved in."""

    def __init__(self, persist_dir: str = ".chroma"):
        self.collection = get_collection(persist_dir)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

    def _ingest(self, path: str) -> None:
        fp = Path(path)
        if fp.suffix not in {".md", ".txt"} or not fp.is_file():
            return
        count = ingest_file(fp, self.collection, self.splitter)
        log.info(f"Ingested {fp.name}  ({count} chunks)")

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._ingest(event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._ingest(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        # Catches files moved/renamed into the watched directory
        if not event.is_directory:
            self._ingest(event.dest_path)


def watch(directories: list[Path], persist_dir: str = ".chroma") -> None:
    handler = HandoffHandler(persist_dir=persist_dir)
    observer = Observer()

    watched = 0
    for d in directories:
        if not d.exists():
            log.warning(f"Directory does not exist, skipping: {d}")
            continue
        observer.schedule(handler, str(d), recursive=True)
        log.info(f"Watching: {d}")
        watched += 1

    if watched == 0:
        log.error("No valid directories to watch. Exiting.")
        return

    observer.start()
    log.info("Watcher running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        log.info("Stopped.")

    observer.join()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Watch directories and auto-ingest new/modified files into ChromaDB"
    )
    parser.add_argument(
        "dirs",
        nargs="*",
        help=f"Directories to watch (default: {DEFAULT_WATCH_PATH})",
    )
    args = parser.parse_args()

    directories = [Path(d) for d in args.dirs] if args.dirs else [DEFAULT_WATCH_PATH]
    watch(directories)


if __name__ == "__main__":
    main()
