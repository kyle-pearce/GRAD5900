# Assignment 4 — Local-First Personal Assistant

**Course:** Applied Generative AI (GRAD 5900)
**Phase:** 4 of 4 — User Interface + Local Inference

A fully local AI personal assistant with a React web UI. Powered by Ollama (llama3.2:3b)
for inference and nomic-embed-text for embeddings. No Anthropic or OpenAI API keys required.

---

## Prerequisites

- [Ollama](https://ollama.com) installed and running
- Python 3.12+
- Node 20+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

---

## Setup

### 1. Pull Ollama models

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### 2. Install backend dependencies

```bash
cd assignment-4
uv venv --python 3.12
uv pip install -r backend/requirements.txt
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## Running

Open two terminals from `assignment-4/`.

**Terminal 1 — Backend**
```bash
.venv/bin/uvicorn backend.main:app --reload
```

**Terminal 2 — Frontend**
```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## First Run — Onboarding

On first load you'll be prompted to set up your context:

- **Use default context** — copies Kyle's writing style, email preferences, and mental model
  from the Windows host (`C:\Users\kyle\Downloads\`) via WSL2 mount. Takes one click.
- **Build your own** — answer 5 questions and the assistant generates your context files
  using llama3.2:3b. Takes 2–3 minutes.

After onboarding you're dropped into the main chat. Click **Reset context** in the sidebar
to re-run onboarding at any time.

---

## Skills

Click any button in the sidebar to start a skill:

| Button | What it does |
|--------|-------------|
| **Standup** | Daily EOD check-in — 5 questions, produces a session summary |
| **Sync** | Meeting capture — decisions, action items, notes |
| **Refinement** | Weekly planning — priorities from your goals and projects |
| **1:1** | 1:1 prep — enriched with past meeting history from your knowledge base |
| **Email** | Email draft — paste a thread, get a reply in your voice |
| **Close Session** | Summarises the session, writes a handoff file, auto-ingests it |

You can also type freely — the assistant routes your message to the most relevant skill.

---

## Knowledge Base

Click **Knowledge** in the sidebar to:
- Search your personal knowledge base (handoff files, meeting notes, course notes)
- Ingest a new file or directory path
- Check how many chunks are indexed

The knowledge base uses ChromaDB with Ollama's `nomic-embed-text` embeddings (768-dim,
fully local). Each time you close a session the handoff is automatically ingested.

---

## Approval Gates

The **Email** skill demonstrates the Tier 2 approval gate. After generating a draft,
the assistant pauses and shows a **Save Draft / Cancel** prompt inline in the chat.
The draft is only written to `handoffs/email-draft.md` after you explicitly approve.

---

## Architecture

```
assignment-4/
├── backend/                  ← FastAPI + Python
│   ├── core/                 ← Ollama client, config, context loader
│   ├── knowledge/            ← RAG pipeline (Ollama embeddings + ChromaDB)
│   ├── skills/               ← 6 skill classes (standup, sync, refinement, one_on_one, email, close)
│   ├── api/                  ← REST routes (chat, approval, knowledge, onboarding)
│   ├── router.py             ← Intent → skill dispatch
│   └── approval.py           ← Tier 2 draft store
│
├── frontend/                 ← React + Vite + TypeScript + Tailwind
│   └── src/
│       ├── pages/            ← Chat, Onboard
│       ├── components/       ← Sidebar, ChatWindow, ApprovalGate, KnowledgePanel, Onboarding
│       ├── hooks/            ← useChat (SSE streaming)
│       └── api/              ← Typed fetch wrappers
│
├── context/                  ← Personal context files (written by onboarding)
└── handoffs/                 ← Session summaries + email drafts
```

**Streaming:** Skills run in a background thread and push tokens into an `asyncio.Queue`.
The SSE endpoint reads from the queue in real time — the chat bubble fills as the model generates.

**No MCP servers.** The RAG pipeline is imported directly by the FastAPI backend.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM inference | Ollama `llama3.2:3b` |
| Embeddings | Ollama `nomic-embed-text` (768-dim) |
| Vector store | ChromaDB (local SQLite) |
| Retrieval | Hybrid: vector + BM25 + RRF + self-correcting loop |
| Backend | FastAPI, uvicorn, sse-starlette |
| Frontend | React, Vite, TypeScript, Tailwind CSS |
