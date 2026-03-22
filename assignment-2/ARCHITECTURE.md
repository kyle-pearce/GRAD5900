# System Architecture Design Document

**Course:** Applied Generative AI (GRAD 5900)
**Author:** Kyle
**Date:** 2026-03-22
**Scope:** Assignment 1 (Personal Assistant Kit) and Assignment 2 (RAG-Augmented Knowledge Layer)

---

## 1. Overview

These two assignments form a layered personal AI assistant system. Assignment 1 establishes
the **interface layer**: a set of skills, context files, and workflow agents that give an AI
assistant persistent knowledge of the user's goals, relationships, and working patterns.
Assignment 2 establishes the **knowledge layer**: a retrieval-augmented generation (RAG)
pipeline that grounds assistant responses in private documents rather than relying on the
model's parametric knowledge alone.

The two systems share a common LLM backbone (Anthropic Claude) and a conceptual dependency:
Assignment 1's context files are natural input documents for Assignment 2's ingestion
pipeline. Phase 3 or a future integration would connect them so that retrieval augments
skills directly at inference time.

---

## 2. Assignment 1 — Personal Assistant Kit

### 2.1 Purpose

Provide the AI assistant with deep, persistent, user-specific context so that every
skill interaction — drafting an email, preparing for a meeting, doing a weekly review —
draws on a coherent picture of the user's goals, patterns, and relationships.

### 2.2 Runtime Model

Assignment 1 has **no application code**. Its runtime is Claude Code itself. Skills are
loaded as instruction files; the model is the engine. Configuration drives all behavior.

```
User utterance
      │
      ▼
Claude Code (claude-sonnet-4-6)
      │
      ├── Semantic skill match (CLAUDE.md skill index)
      │         │
      │         ▼
      │   .claude/skills/<name>/SKILL.md   ← loaded as system instructions
      │
      ├── Context file reads (per skill's context load matrix)
      │         │
      │         ▼
      │   .claude/context/*.md             ← user-filled personal data
      │
      └── External tool calls (when skill permits)
                │
                ├── mcp__gmail__*          ← Gmail via MCP server
                └── mcp__outlook__*        ← Outlook via MCP server
```

### 2.3 Components

#### Context Files (`.claude/context/`)

Static markdown files filled in once during setup. They encode who the user is so the
model never starts from scratch.

| File | What it encodes |
|------|----------------|
| `goals.md` | Long-term goals, annual priorities, tension points |
| `projects.md` | Active projects, stakeholders, blockers |
| `meetings.md` | Recurring meetings, key relationships |
| `context.md` | Role, org, sender relationships, timezone |
| `decision-patterns.md` | Decision process, failure modes, blind spots |
| `writing-style.md` | Tone, voice, sign-offs, phrases to avoid |
| `email-goals.md` | Communication goals, recurring scenarios |
| `response-framework.md` | Email structure, length guidelines |

#### Skills (`.claude/skills/`)

Each skill is a markdown instruction file with a declared context load matrix. Skills
load only the context files they need — `follow-up-email` loads writing style; `decision`
loads decision patterns; `resume` loads goals and projects.

| Skill category | Skills |
|----------------|--------|
| Session management | `resume`, `handoff` |
| Reflection | `reflect`, `weekly-report`, `week-plan` |
| Meetings | `meeting`, `coaching-prep`, `follow-up-meeting` |
| Communication | `follow-up-email`, `stakeholder-update` |
| Thinking | `review-doc`, `decision` |

#### MCP Servers (`.claude/settings.json`)

Two external tool bridges are declared as MCP servers. Both are Node.js processes
launched by Claude Code on demand, authenticated via OAuth tokens in `.env`.

```
gmail   → npx @shinzolabs/gmail-mcp    (Google OAuth2)
outlook → npx ms-365-mcp-server        (Microsoft OAuth2)
```

Skills that read or draft email invoke these tools via `mcp__gmail__*` /
`mcp__outlook__*` calls. No email content is ever written to disk.

#### Handoff Files (`handoffs/`)

The only writable outputs. Skills like `reflect` and `meeting` write structured
markdown records here. These persist context across sessions without storing PII in
the model's weights.

### 2.4 Data Flow — Example: `follow-up-email`

```
"draft email" utterance
        │
        ▼
Claude Code matches → follow-up-email skill
        │
        ├── Read: writing-style.md, context.md,
        │         response-framework.md, email-goals.md
        │
        ├── Call: mcp__gmail__search_messages(query=...)
        ├── Call: mcp__gmail__get_message(id=...)
        │
        ▼
Claude composes draft using context + email thread
        │
        ▼
Draft presented to user (never auto-sent)
```

---

## 3. Assignment 2 — RAG Knowledge Layer

### 3.1 Purpose

Ground assistant responses in private, user-owned documents using hybrid retrieval
(vector + keyword) and a self-correcting retrieval loop. Introduce scientific evaluation
of retrieval quality using RAGAS before deployment.

### 3.2 Runtime Model

Assignment 2 is a Python application that calls external APIs directly. There is no
Claude Code runtime — the application manages its own prompt construction, retrieval
logic, and evaluation loop.

```
python main.py <command>
        │
        ├── ingest  → Ingestion Pipeline → ChromaDB (persistent)
        ├── query   → Retrieval Pipeline → Claude Sonnet (answer)
        └── eval    → Evaluation Pipeline → RAGAS → results/latest.json
```

### 3.3 Component Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        main.py (CLI entry point)                    │
│           ingest <dir>    │    query "<q>"    │    eval             │
└────────────┬──────────────┴────────┬──────────┴──────┬─────────────┘
             │                       │                  │
             ▼                       ▼                  ▼
┌────────────────────┐  ┌────────────────────────┐  ┌──────────────────────┐
│  knowledge/        │  │  knowledge/             │  │  eval/               │
│  ingest.py         │  │  retriever.py           │  │  evaluate.py         │
│                    │  │                         │  │                      │
│  RecursiveChar     │  │  HybridRetriever        │  │  load_golden_dataset │
│  TextSplitter      │  │  ├── vector search      │  │  generate_answer     │
│  (512 tok,         │  │  │   (ChromaDB)         │  │  run_evaluation      │
│   64 overlap)      │  │  ├── BM25 keyword       │  │  print_comparison    │
│        │           │  │  │   (rank_bm25)        │  │        │             │
│        ▼           │  │  └── RRF fusion         │  │        ▼             │
│  OpenAI            │  │                         │  │  ragas.evaluate()    │
│  text-embed-3-sm   │  │  SelfCorrectingRetriever│  │  ├── faithfulness    │
│        │           │  │  ├── HybridRetriever    │  │  ├── answer_relevancy│
│        ▼           │  │  ├── _judge_relevance   │  │  ├── context_prec.  │
│  ChromaDB          │  │  │   (Claude Haiku)     │  │  └── context_recall  │
│  PersistentClient  │  │  └── _expand_query      │  │        │             │
│  (.chroma/)        │  │      (Claude Haiku)     │  │        ▼             │
└────────────────────┘  └──────────┬──────────────┘  │  eval/results/      │
             │                      │                  │  latest.json        │
             ▼                      ▼                  └──────────────────────┘
     ┌───────────────┐    ┌──────────────────┐
     │  ChromaDB     │    │  Claude Sonnet   │
     │  (.chroma/)   │◄───│  (answer gen)    │
     │  sqlite-vec   │    └──────────────────┘
     └───────────────┘
```

### 3.4 Ingestion Pipeline (`knowledge/ingest.py`)

Transforms raw documents into a searchable vector store.

```
Document files (.txt, .md)
        │
        ▼
RecursiveCharacterTextSplitter
  chunk_size=512, chunk_overlap=64
        │
        ▼  (chunks[])
OpenAI text-embedding-3-small
  → 1536-dimensional dense vectors
        │
        ▼
ChromaDB.upsert(documents, ids, metadatas)
  IDs are deterministic: "{stem}_{chunk_index}"
  → allows re-ingestion without duplicates
        │
        ▼
Persisted in .chroma/ (SQLite + sqlite-vec)
```

**Design decisions:**
- `upsert` (not `add`) enables idempotent re-ingestion as source files change.
- `chunk_overlap=64` preserves sentence context at chunk boundaries.
- Chunk IDs encode filename + position, making source attribution trivial.

### 3.5 Retrieval Pipeline (`knowledge/retriever.py`)

#### HybridRetriever — Vector + BM25 via Reciprocal Rank Fusion

```
Query string
     │
     ├──────────────────────┬────────────────────────────
     │                      │
     ▼                      ▼
ChromaDB.query()        BM25Okapi.get_scores()
(semantic similarity)   (lexical keyword match)
     │                      │
     │  ranked list A        │  ranked list B
     └──────────┬────────────┘
                ▼
         _rrf_fuse(A, B, k=60)
         score(d) = Σ 1/(k + rank(d))
                ▼
         top_k fused results
```

RRF is rank-based, so it tolerates the incompatible score scales of cosine similarity
(vector) and BM25 TF-IDF scores. Documents appearing in both lists are boosted.

#### SelfCorrectingRetriever — LLM Judge Loop

```
Query
  │
  ▼
HybridRetriever.retrieve(query)        ← first pass
  │
  ▼
_judge_relevance(query, chunks[:3])
  │  Prompt: "Rate relevance 0.0–1.0"
  │  Model: claude-haiku-4-5 (cheap, fast)
  │
  ├── score >= 0.5 ──► return chunks, meta{corrected=False}
  │
  └── score < 0.5
        │
        ▼
      _expand_query(query)
        │  Prompt: "Rewrite with synonyms/related terms"
        │  Model: claude-haiku-4-5
        │
        ▼
      HybridRetriever.retrieve(expanded_query)  ← second pass
        │
        ▼
      return chunks, meta{corrected=True, expanded_query=...}
```

The judge uses Claude Haiku (fast, low cost) as the relevance scorer, reserving
Claude Sonnet for the final answer generation step.

### 3.6 Evaluation Pipeline (`eval/evaluate.py`)

Implements the RAGAS evaluation framework (Week 7: LLM-as-a-Judge).

```
golden_dataset.json
  [{question, ground_truth}, ...]
        │
        ▼  for each item × each retriever config
  retriever.retrieve(question)
        │
        ▼
  generate_answer(question, chunks)   ← Claude Haiku
        │
        ▼
  HuggingFace Dataset {
    question, answer, contexts, ground_truth
  }
        │
        ▼
  ragas.evaluate(dataset, metrics=[
    faithfulness,       ← answer grounded in context?
    answer_relevancy,   ← answer addresses the question?
    context_precision,  ← retrieved chunks were relevant?
    context_recall,     ← needed chunks were retrieved?
  ])
        │
        ▼
  Comparison table (stdout) + eval/results/latest.json
```

**Retriever configurations compared:**

| Config | Retrieval method |
|--------|-----------------|
| Hybrid (vector + BM25) | `HybridRetriever` — no correction loop |
| Self-correcting | `SelfCorrectingRetriever` — hybrid + judge loop |

The comparison directly shows whether the self-correction step improves measurable
retrieval quality, which satisfies the Week 7 requirement to "scientifically score
performance before deployment."

### 3.7 Corpus Sync: Filesystem Watcher (`watch.py`)

The ingestion pipeline is triggered either manually (`python main.py ingest <dir>`) or
automatically via a `watchdog`-based filesystem observer. The watcher is the preferred
method for keeping the knowledge layer current as A1 writes new handoff files.

```
Assignment 1 runtime                    watch.py (background process)
──────────────────────────              ──────────────────────────────────
reflect skill writes                    watchdog.Observer monitors
  handoffs/session-handoff.md   ──►     handoffs/ for fs events
                                                  │
                                         on_created / on_modified / on_moved
                                                  │
                                                  ▼
                                         ingest_file(fp, collection, splitter)
                                         (upsert — safe to re-run)
                                                  │
                                                  ▼
                                         .chroma/ updated within seconds
```

Three filesystem events are handled:

| Event | Trigger | Example |
|-------|---------|---------|
| `on_created` | New file appears | `reflect` skill writes a new `session-handoff.md` |
| `on_modified` | Existing file saved | `session-handoff.md` overwritten with updated content |
| `on_moved` | File renamed into watched dir | Editor writes to temp file then renames on save |

**Design decisions:**
- Calls `ingest_file()` directly (not `ingest_directory`) — only the changed file is
  re-embedded, not the entire corpus.
- `upsert` semantics mean firing twice on the same file is harmless.
- Accepts multiple watch paths as CLI args, so handoffs and course notes can be watched
  simultaneously with a single process.

```bash
# Watch A1 handoffs (default)
python watch.py

# Watch handoffs + course notes simultaneously
python watch.py ../../assignment-1/ai-assistant/handoffs/ ~/notes/grad5900/
```

---

## 4. Cross-Assignment Relationship

### 4.1 Conceptual Dependency

Assignment 1 is the **interface**; Assignment 2 is the **knowledge layer**. They address
different failure modes of the same underlying system:

| Problem | Assignment 1 solves | Assignment 2 solves |
|---------|--------------------|--------------------|
| Model has no user context | Context files encode goals, style, relationships | — |
| Context is static (written once) | Handoff files allow session-to-session accumulation | — |
| Model cannot access private documents | — | Ingestion + hybrid retrieval grounds answers in docs |
| No way to measure retrieval quality | — | RAGAS golden dataset + metrics |
| Model uses stale parametric knowledge | — | Retrieved chunks inject up-to-date information |

### 4.2 Data Flow Between Assignments

Assignment 1's context files are the natural first corpus for Assignment 2's ingestion
pipeline. The relationship is one-directional today: A1 produces documents; A2 ingests
and queries them.

```
Assignment 1                          Assignment 2
─────────────────────────────         ────────────────────────────────────
.claude/context/goals.md   ──────►   knowledge/ingest.py
.claude/context/projects.md ─────►   (chunk → embed → ChromaDB)
.claude/context/meetings.md ─────►
handoffs/session-handoff.md ─────►
handoffs/weekly-*.md        ─────►
handoffs/meeting-*.md       ─────►
                                             │
                                             ▼
                                      .chroma/ (vector store)
                                             │
                                             ▼
                                      knowledge/retriever.py
                                      (hybrid + self-correcting)
                                             │
                                             ▼
                                      Claude Sonnet answer
```

### 4.3 Shared Infrastructure

| Resource | Assignment 1 | Assignment 2 |
|----------|-------------|-------------|
| LLM provider | Anthropic (via Claude Code runtime) | Anthropic (direct SDK calls) |
| Primary model | claude-sonnet-4-6 | claude-sonnet-4-6 (answers), claude-haiku-4-5 (judge/expand) |
| Embeddings | None (not needed) | OpenAI text-embedding-3-small |
| Vector store | None | ChromaDB (local SQLite + sqlite-vec) |
| External services | Gmail MCP, Outlook MCP | None (fully local except LLM/embed APIs) |
| Credential pattern | OAuth tokens in `.env` | API keys in `.env` |
| Privacy constraint | No email content written to disk | No external transmission of ingested docs |

### 4.4 Integration Path (Future — Phase 3)

The logical next step is to expose `SelfCorrectingRetriever` as a tool that Assignment 1
skills can call at inference time. This would close the loop: a skill like `coaching-prep`
could retrieve relevant meeting notes dynamically rather than reading a static context file.

```
Future state (not yet implemented):

Claude Code skill execution
        │
        ├── Read: context files (static, as today)
        │
        └── Tool call: retriever_search(query)   ← A2 retriever as MCP tool
                 │
                 ▼
           .chroma/ vector store
           (populated from A1 handoff files + docs)
                 │
                 ▼
           Retrieved chunks injected into prompt
```

---

## 5. Technology Stack Summary

### Assignment 1

| Layer | Technology | Role |
|-------|-----------|------|
| Runtime | Claude Code | Skill execution, tool calling |
| LLM | claude-sonnet-4-6 | All inference |
| Skills | Markdown instruction files | Behavior definition |
| External tools | Gmail MCP, Outlook MCP (Node.js) | Email read/draft |
| Persistence | Markdown files (`handoffs/`) | Session continuity |

### Assignment 2

| Layer | Technology | Role |
|-------|-----------|------|
| Application | Python 3.12, argparse | CLI entry point |
| Chunking | langchain-text-splitters | RecursiveCharacterTextSplitter |
| Embeddings | OpenAI text-embedding-3-small | Dense vector representation |
| Vector store | ChromaDB (PersistentClient) | Semantic similarity search |
| Keyword search | rank_bm25 (BM25Okapi) | Lexical/exact-match search |
| Fusion | Reciprocal Rank Fusion (custom) | Merges vector + BM25 rankings |
| LLM judge | claude-haiku-4-5 | Relevance scoring, query expansion |
| LLM answer | claude-sonnet-4-6 | Final answer generation |
| Evaluation | RAGAS + HuggingFace datasets | Faithfulness, relevancy, precision, recall |
| Corpus sync | watchdog (filesystem observer) | Auto-ingest on file create/modify/move |

---

## 6. Directory Structure

```
grad5900/
├── assignment-1/
│   └── ai-assistant/
│       ├── AGENTS.md                  ← Universal agent instructions
│       ├── CLAUDE.md                  ← Claude Code config + skill index
│       ├── GEMINI.md                  ← Gemini CLI config
│       ├── .claude/
│       │   ├── settings.json          ← MCP server declarations
│       │   ├── context/               ← User-filled personal context (8 files)
│       │   └── skills/                ← 12 skill instruction files
│       ├── handoffs/                  ← AI-written session records (gitignored)
│       ├── mcp/README.md              ← MCP setup guide
│       └── docs/quickstart.md         ← Setup interview prompts
│
└── assignment-2/
    ├── ARCHITECTURE.md                ← This document
    └── rag-assistant/
        ├── main.py                    ← CLI: ingest / query / eval
        ├── watch.py                   ← Filesystem watcher: auto-ingest on file changes
        ├── requirements.txt
        ├── .env.example
        ├── knowledge/
        │   ├── ingest.py              ← Chunking + embedding + ChromaDB storage
        │   └── retriever.py           ← HybridRetriever + SelfCorrectingRetriever
        ├── eval/
        │   ├── golden_dataset.json    ← Ground-truth Q&A pairs
        │   ├── evaluate.py            ← RAGAS runner + comparison report
        │   └── results/               ← Evaluation run outputs (gitignored)
        └── docs/sample/               ← Sample documents for initial testing
```

---

## 7. Knowledge Corpus Design

### 8.1 Guiding Principle

The RAG layer adds value where content is **too voluminous, too specific, or too
time-varying** to fit in a static context file or model weights. If something is small
and stable (like writing tone preferences), load it directly as A1 does. If it's large,
accumulating, or needs to be searched selectively, it belongs in the knowledge layer.

### 8.2 Tier 1 — Highest Value (ingest immediately)

#### Accumulated Handoff Files (`assignment-1/handoffs/`)

This is the most important corpus and the primary reason A2 exists. Over months of daily
use, `handoffs/` becomes a rich episodic memory store — too large for any single context
window, but full of exactly the facts that matter most.

| File type | What becomes retrievable |
|-----------|--------------------------|
| `session-handoff.md` | What was worked on, what was blocked, what was decided |
| `weekly-*.md` | Weekly patterns, goal progress, recurring themes |
| `meeting-*.md` | Decisions from each meeting, action items, relationship notes |
| `decision-*.md` | Past decision frames, trade-offs considered, outcomes |
| `week-plan-*.md` | Past priorities, what got dropped or deferred |

Without RAG, when you ask "remind me what I decided about X three months ago" the
assistant can only see the most recent handoff. With RAG, the entire history is
searchable. This is the episodic memory problem — and it compounds in value the longer
the system runs.

#### Course Materials

As a grad student in Applied GenAI, the primary private knowledge corpus is coursework:

- Lecture notes and slides (exported as text/markdown)
- Paper reading notes and summaries
- Assignment feedback from instructors
- Personal analyses and reflections on readings

The model already knows publicly available papers. What it does not know is your
synthesis of them, the specific framing your instructor used, or which concepts connect
to which assignments. That is private knowledge only RAG can surface.

### 8.3 Tier 2 — High Value (ingest as they accumulate)

**Project documentation** — any project with more than a few documents benefits from
retrieval rather than manual context loading: architecture docs, design decision records,
README files, technical notes.

**Advisor and mentor interaction notes** — notes from meetings with advisors, committee
members, or professors are high-signal private documents the model otherwise has no
access to.

### 8.4 Tier 3 — Selective

**The static A1 context files** — the eight files in `.claude/context/` are already
handled well by A1's direct-load pattern (they are small and always-relevant). However,
if these files are periodically snapshotted and re-ingested as they change, the RAG
layer can answer longitudinal questions like "how have my stated goals changed over
time?" — something the current A1 system has no memory of.

**Exported calendar or email archives** — past commitments add temporal depth but are
low urgency.

### 8.5 What Does Not Belong in the Knowledge Layer

| Data | Reason |
|------|--------|
| Live email content | A1 handles this at query time via MCP. Storing it would violate the `AGENTS.md` privacy constraint: "NEVER store email thread content to disk." |
| Writing style, tone, sign-offs | Must always be in context — a RAG miss here corrupts every drafted communication. |
| Real-time project status | Stale too quickly. Keep `projects.md` updated and re-ingest on a schedule instead. |
| API keys, credentials | Never. |

### 8.6 Recommended Starting Corpus

| Priority | Source | Ingest command |
|----------|--------|----------------|
| 1 | `assignment-1/handoffs/` | `python main.py ingest ../../assignment-1/ai-assistant/handoffs/` |
| 2 | Course notes directory | `python main.py ingest ~/notes/grad5900/` |
| 3 | A1 context files snapshot | `python main.py ingest ../../assignment-1/ai-assistant/.claude/context/` |

For ongoing sync, run `python watch.py` in the background instead of manually
re-running ingest. The watcher picks up new handoff files within seconds of A1 writing
them. The episodic memory use case becomes meaningful after roughly 4–6 weeks of
consistent A1 usage — corpus size is what makes retrieval valuable.

---

## 8. Course Topic Mapping

| Week | Topic | Where implemented |
|------|-------|-------------------|
| 1 | LLM landscape, System 2 thinking | Foundation for both projects |
| 2 | CoT, ReAct prompting patterns | A1 skill instructions use structured reasoning prompts; A2 judge/expand prompts use explicit CoT |
| 3 | Agent architecture (state machines vs. type-safe agents) | A1 = skill-dispatch state machine; A2 = linear pipeline with conditional branch |
| 4 | Embeddings, vector DBs, context management | A2 `ingest.py` — OpenAI embeddings + ChromaDB |
| 5 | RAG 2.0, hybrid search, self-correcting loops | A2 `retriever.py` — HybridRetriever (RRF) + SelfCorrectingRetriever |
| 6 | GraphRAG, knowledge graphs | Not implemented (Phase 3 scope) |
| 7 | RAGAS, LLM-as-a-Judge evaluation | A2 `eval/evaluate.py` — full RAGAS pipeline |
