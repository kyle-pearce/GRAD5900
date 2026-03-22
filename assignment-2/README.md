# Assignment 2 — RAG-Augmented Personal Assistant

**Course:** Applied Generative AI (GRAD 5900)
**Topics:** Week 5 (RAG 2.0, Hybrid Search) · Week 7 (RAGAS Evaluation)

---

## What This Does

This project adds a **knowledge augmentation layer** to the personal AI assistant built
in Assignment 1. Where Assignment 1 gave the assistant a static picture of the user's
goals and context, Assignment 2 gives it a searchable, always-current memory of private
documents — grounded answers instead of hallucinated ones.

Three capabilities are implemented:

| Capability | Week | What it demonstrates |
|-----------|------|----------------------|
| **Hybrid retrieval** (vector + BM25, fused via RRF) | 5 | Semantic and keyword search combined; rank-based fusion tolerates incompatible score scales |
| **Self-correcting retrieval loop** | 5 | LLM judges retrieved context quality; if below threshold, rewrites the query and retrieves again |
| **RAGAS evaluation harness** | 7 | Scientifically scores retrieval quality (faithfulness, answer relevancy, context precision, context recall) across configurations before deployment |

A fourth utility — a **filesystem watcher** — keeps the knowledge base current automatically
by re-ingesting documents the moment they are written to disk.

---

## How It Works

```
Documents (.md, .txt)
       │
       ▼  knowledge/ingest.py
  Chunk (512 tok, 64 overlap)
  Embed (OpenAI text-embedding-3-small)
  Store (ChromaDB, local SQLite)
       │
       ▼  knowledge/retriever.py
  HybridRetriever
  ├── Vector search  (ChromaDB)   ─┐
  └── BM25 keyword search          ├── Reciprocal Rank Fusion
                                  ─┘
       │
  SelfCorrectingRetriever
  ├── Judge relevance  (Claude Haiku, 0.0–1.0)
  └── If score < 0.5 → expand query → retrieve again
       │
       ▼  Claude Sonnet
  Grounded answer
       │
       ▼  eval/evaluate.py  (optional)
  RAGAS scores across configs → eval/results/latest.json
```

The **filesystem watcher** (`watch.py`) runs as a background process. It monitors the
Assignment 1 `handoffs/` directory and re-ingests any file within seconds of it being
written — so every daily reflection, meeting note, and weekly report is automatically
searchable without any manual step.

---

## Installation

Requires Python 3.12+ and API keys for Anthropic and OpenAI.

> **No additional software to install.** ChromaDB (the vector store) is a Python
> package — it installs via pip and runs entirely inside the Python process. There
> is no separate server, no service to start, and no system-level setup. When the
> application first ingests a document, it creates a `.chroma/` folder in the
> project directory and reads/writes to it as a local SQLite file. The only external
> services required are the Anthropic and OpenAI APIs, which are standard HTTPS calls.
> To reset the knowledge base at any time: `rm -rf .chroma/`

```bash
cd assignment-2/rag-assistant

# Install dependencies (includes chromadb, watchdog, ragas, and all others)
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and add:
#   ANTHROPIC_API_KEY=...
#   OPENAI_API_KEY=...
```

---

## Testing the Features

### 1. Ingest documents

```bash
# Ingest the included sample document
python main.py ingest docs/sample/

# Or ingest the Assignment 1 handoff files
python main.py ingest ../../assignment-1/ai-assistant/handoffs/
```

### 2. Query the knowledge base

```bash
python main.py query "What does the reflect skill do?"
```

Expected output shows the retrieval relevance score, whether self-correction triggered,
and a grounded answer from Claude Sonnet:

```
[Retrieval] relevance=0.87  (no correction)
[Context]   4 chunk(s) retrieved

Answer: The reflect skill is a daily end-of-day conversational check-in...
```

To see self-correction trigger, ask about something not well-represented in the corpus:

```bash
python main.py query "epistemological foundations of Bayesian inference"
```

```
[Retrieval] relevance=0.21 → self-corrected (expanded: "Bayesian probability
  theory statistical inference prior posterior...")
[Context]   4 chunk(s) retrieved
```

### 3. Run RAGAS evaluation

```bash
python main.py eval
```

Runs both retriever configurations against the golden dataset and prints a comparison:

```
================================================================
RAGAS Evaluation Results
================================================================
Configuration               faithfulness          answer_relevancy      context_precision     context_recall
────────────────────────────────────────────────────────────────
Hybrid (vector + BM25)      0.8821                0.9134                0.7650                0.8210
Self-correcting             0.9103                0.9287                0.8012                0.8544
================================================================
```

Results are saved to `eval/results/latest.json`.

> **Note:** The golden dataset (`eval/golden_dataset.json`) ships with 10 examples
> derived from the Assignment 1 sample document. Replace these with Q&A pairs from your
> own ingested documents for meaningful scores.

### 4. Run the filesystem watcher

```bash
# Terminal 1 — start the watcher
python watch.py

# Terminal 2 — simulate A1 writing a new handoff file
echo "## Session notes\nWorked on RAG pipeline today." > ../../assignment-1/ai-assistant/handoffs/test-session.md
```

Terminal 1 will log:
```
14:23:01 [watcher] Watching: .../assignment-1/ai-assistant/handoffs
14:23:01 [watcher] Watcher running. Press Ctrl+C to stop.
14:23:08 [watcher] Ingested test-session.md  (1 chunks)
```

The new file is immediately queryable:
```bash
python main.py query "What did I work on today?"
```

---

## Project Structure

```
assignment-2/
├── README.md                          ← This file
├── ARCHITECTURE.md                    ← Full system design document
└── rag-assistant/
    ├── main.py                        ← CLI: ingest / query / eval
    ├── watch.py                       ← Filesystem watcher (auto-ingest)
    ├── requirements.txt
    ├── .env.example
    ├── knowledge/
    │   ├── ingest.py                  ← Chunking, embedding, ChromaDB storage
    │   └── retriever.py               ← HybridRetriever + SelfCorrectingRetriever
    ├── eval/
    │   ├── golden_dataset.json        ← Ground-truth Q&A pairs
    │   ├── evaluate.py                ← RAGAS runner + comparison report
    │   └── results/                   ← Evaluation outputs (gitignored)
    └── docs/sample/                   ← Sample documents for testing
```

---

## Running Both Assignments Together

This is the intended demo scenario: Assignment 1 drives the assistant interface;
Assignment 2 keeps the knowledge base current in the background.

### Prerequisites

**Assignment 1 — one-time setup**
```bash
cd ~/grad5900/assignment-1/ai-assistant

# Install Claude Code if not already installed
npm install -g @anthropic-ai/claude-code

# Create the handoffs directory (gitignored, does not exist by default)
mkdir -p handoffs

# Fill in context files — reflect won't work well without at minimum:
#   .claude/context/goals.md
#   .claude/context/projects.md
# Replace [PLACEHOLDER] sections with real content
```

**Assignment 2 — one-time setup**
```bash
cd ~/grad5900/assignment-2/rag-assistant

pip install -r requirements.txt
cp .env.example .env
# Edit .env: add ANTHROPIC_API_KEY and OPENAI_API_KEY

# Initial ingest of A1 context files and any existing handoffs
python main.py ingest ../../assignment-1/ai-assistant/.claude/context/
python main.py ingest ../../assignment-1/ai-assistant/handoffs/
```

### Starting the system

Open two terminals.

**Terminal 1 — start the A2 watcher first**
```bash
cd ~/grad5900/assignment-2/rag-assistant
python watch.py ../../assignment-1/ai-assistant/handoffs/
```
```
14:00:01 [watcher] Watching: .../assignment-1/ai-assistant/handoffs
14:00:01 [watcher] Watcher running. Press Ctrl+C to stop.
```

**Terminal 2 — start the A1 assistant**
```bash
cd ~/grad5900/assignment-1/ai-assistant
claude
```

### End-to-end demo

In Terminal 2, trigger a reflection:
```
> reflect
```

Claude Code runs the `reflect` skill, asks about the session, then writes
`handoffs/session-handoff.md`. Terminal 1 immediately logs:

```
14:23:08 [watcher] Ingested session-handoff.md  (3 chunks)
```

That handoff is now in the corpus. Query it from the rag-assistant directory:

```bash
# In a third terminal (or after stopping the assistant)
cd ~/grad5900/assignment-2/rag-assistant
python main.py query "What did I work on today?"
python main.py query "What projects have I been blocked on this month?"
```

The second query searches across *all* past handoffs — something the A1 assistant
alone cannot do, since it only ever sees the most recent session file.

### Sequence diagram

```
Professor (Terminal 2)       A1 Claude Code          A2 watch.py (Terminal 1)
────────────────────         ──────────────          ────────────────────────
"reflect"
                       ──►  reflect skill runs
                             asks questions
                             writes session-handoff.md
                                                ──►  on_created fires
                                                     ingest_file()
                                                     .chroma/ updated ✓

python main.py query   ──►                           SelfCorrectingRetriever
 "blocked last month"                                queries .chroma/
                                                     returns chunks from
                                                     all past handoffs ✓
```

### One gotcha

The watcher must be running **before** `reflect` writes the file. If it was started
after handoffs already exist, run a manual ingest to catch up, then let the watcher
handle everything going forward:

```bash
python main.py ingest ../../assignment-1/ai-assistant/handoffs/
```

---

## Relationship to Assignment 1

Assignment 1 is the **interface layer** — skills, context files, and workflow agents
running inside Claude Code. Assignment 2 is the **knowledge layer** — a Python RAG
pipeline that makes the assistant's memory searchable and measurable.

The watcher closes the loop: every file Assignment 1 writes to `handoffs/` is
automatically ingested into the knowledge base, turning session-by-session reflection
notes into a queryable episodic memory.

Full design documentation: [`ARCHITECTURE.md`](ARCHITECTURE.md)
