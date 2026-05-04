# Design — Local-First Personal Assistant

## Overview

Fully local AI personal assistant. No external API calls at runtime — all inference runs through Ollama on the host. FastAPI backend, React frontend, ChromaDB vector store.

---

## System Architecture

```mermaid
graph TD
    subgraph Frontend ["Frontend (React + Vite, :5173)"]
        UI[Chat / Onboard / Knowledge UI]
    end

    subgraph Backend ["Backend (FastAPI, :8000)"]
        API[REST + SSE API]
        Router[Skill Router]
        Skills[Skill Classes]
        RAG[RAG Pipeline]
        Approval[Approval Store]
    end

    subgraph Storage ["Local Storage"]
        Context[context/*.md]
        Defaults[context/defaults/*.md]
        Chroma[.chroma/ — ChromaDB]
        Handoffs[handoffs/]
    end

    Ollama[Ollama :11434\nllama3.2:3b · nomic-embed-text]

    UI -->|POST /api/chat/send| API
    UI -->|GET /api/chat/stream SSE| API
    UI -->|POST /api/approval/:id/respond| API
    UI -->|GET/POST /api/onboarding/*| API
    UI -->|GET/POST /api/knowledge/*| API

    API --> Router --> Skills
    Skills -->|load_context| Context
    Skills -->|stream_chat| Ollama
    Skills --> RAG
    Skills --> Approval

    RAG -->|vector query| Chroma
    RAG -->|embed query| Ollama
    RAG -->|relevance judge / expand| Ollama

    Approval -->|write on approve| Handoffs
    Skills -->|write summaries| Handoffs
```

---

## Chat Request Flow

Two-phase design: `POST /send` starts the work and returns immediately; `GET /stream` opens the SSE connection and drains the queue as tokens arrive. This avoids holding an HTTP connection open during inference.

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as FastAPI
    participant Q as asyncio.Queue
    participant T as ThreadPoolExecutor
    participant Ollama

    FE->>API: POST /api/chat/send {skill, message}
    API->>Q: create queue[session_id]
    API->>T: run_in_executor(run_skill)
    API-->>FE: {session_id}

    FE->>API: GET /api/chat/stream?session_id=...
    Note over API: SSE connection open

    T->>Ollama: stream_chat(messages)
    loop token stream
        Ollama-->>T: token
        T->>Q: queue.put_nowait({event: token})
        Q-->>API: await queue.get()
        API-->>FE: event: token\ndata: <token>
    end

    T->>Q: queue.put_nowait({event: done})
    Q-->>API: await queue.get()
    API-->>FE: event: done
    Note over API: SSE connection closed
```

**Thread boundary:** Ollama's Python client is synchronous. Skills run in a `ThreadPoolExecutor` (max 10 workers). Tokens cross the thread boundary via `loop.call_soon_threadsafe(queue.put_nowait, event)`.

**Session state:** Conversation history is stored in-memory (`_sessions: dict[str, list[dict]]`). Not persisted across restarts.

---

## Skill System

```mermaid
graph TD
    Msg[User message or skill button] --> Resolve[resolve_skill]
    Resolve -->|explicit skill name| Map[SKILL_MAP lookup]
    Resolve -->|free text| KW[Keyword match]
    KW -->|no match| Default[StandupSkill fallback]
    Map & KW & Default --> Skill[Skill instance]

    Skill --> BuildSys[_build_system]
    BuildSys -->|load_context REQUIRED_CONTEXT| Files[context/*.md]
    BuildSys --> SysPrompt[system prompt + context block]

    SysPrompt --> Messages["[system] + history + [user]"]
    Messages --> Ollama[stream_chat → Ollama]
    Ollama --> Tokens[yield token events]
```

Each skill declares `REQUIRED_CONTEXT` — only the files it needs are read from disk. Context is loaded fresh per request (no caching needed at this scale).

| Skill | Context loaded | Special behavior |
|---|---|---|
| Standup | goals, projects, mental-model | — |
| Sync | goals, projects | — |
| Refinement | goals, projects, mental-model | — |
| One-on-One | goals, projects, mental-model | RAG query over handoffs |
| Email | writing-style, email-goals | Tier 2 approval gate |
| Close | goals, projects | Writes handoff file, triggers ingestion |

---

## RAG Pipeline

Used by skills that need long-term memory (1:1 prep, close session). All embedding and inference is local via Ollama.

```mermaid
flowchart TD
    Q[Query] --> VS[Vector search\nChromaDB top-5]
    Q --> BM25[BM25 keyword search\nfull corpus top-5]
    VS & BM25 --> RRF[RRF Fusion\nscore = Σ 1 / 60+rank]
    RRF --> Top5[Fused top-5 chunks]
    Top5 --> Judge[LLM relevance judge\n0.0 – 1.0]
    Judge -->|score ≥ 0.5| Return[Return chunks]
    Judge -->|score < 0.5| Expand[LLM query expansion]
    Expand --> VS2[Re-run hybrid retrieval]
    VS2 --> Return
```

**Why hybrid:** Vector search handles semantic similarity; BM25 handles exact keyword matches (names, dates, acronyms). RRF fuses both without requiring score normalization.

**Self-correction:** If the relevance judge scores below 0.5, the query is expanded with synonyms and the full retrieval runs again. `meta.corrected` is returned to the caller so the UI (or logs) can surface when this happened.

**Storage:** ChromaDB with a `PersistentClient` backed by SQLite at `.chroma/`. Embeddings are 768-dimensional (`nomic-embed-text`). Chunking: 512 tokens, 64-token overlap.

---

## Approval Gate (Email Skill)

Non-blocking design — the skill does not await the user's decision. The SSE stream ends immediately after emitting `approval_required`; the frontend holds state and makes a separate call when the user responds.

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant Email as EmailSkill
    participant Store as Approval Store (in-memory)
    participant Disk as handoffs/

    Email->>FE: stream draft tokens
    Email->>Store: store_pending_draft(uuid, draft)
    Email->>FE: event: approval_required {id, tier, action}
    Email->>FE: event: done

    Note over FE: Shows Save Draft / Cancel UI

    alt User approves
        FE->>+API: POST /api/approval/{id}/respond {outcome: approved}
        API->>Store: pop_pending_draft(id)
        API->>Disk: write handoffs/email-draft.md
        API-->>-FE: {outcome: approved}
    else User cancels
        FE->>API: POST /api/approval/{id}/respond {outcome: cancelled}
        API->>Store: pop_pending_draft(id) — discard
        API-->>FE: {outcome: cancelled}
    end
```

**Trade-off:** In-memory approval store means a server restart between draft generation and user response loses the draft. Acceptable for a local-first single-user app.

---

## Onboarding Flow

```mermaid
flowchart TD
    Load[App load] --> Status[GET /api/onboarding/status]
    Status -->|.onboarded exists| Chat[Chat UI]
    Status -->|not onboarded| OnboardUI[Onboarding UI]

    OnboardUI --> Choice{User choice}

    Choice -->|Use defaults| Defaults[POST /api/onboarding/use-defaults]
    Defaults --> Copy[Copy context/defaults/*.md → context/*.md]
    Copy --> Marker[touch context/.onboarded]
    Marker --> Chat

    Choice -->|Build your own| Form[5-question form]
    Form --> SaveCustom[POST /api/onboarding/save-custom]
    SaveCustom --> Generate[LLM generates each context file\nfrom user answers]
    Generate --> Marker
```

`context/defaults/` ships with the repo as portable starter templates. `context/` is the live working directory written by onboarding and read by skills at runtime.

---

## Storage Layout

```
assignment-4/
├── context/
│   ├── defaults/          ← repo-committed starter templates (read-only source)
│   │   ├── writing-style.md
│   │   ├── email-goals.md
│   │   ├── mental-model.md
│   │   ├── goals.md
│   │   └── projects.md
│   ├── writing-style.md   ← live copies (written by onboarding, read by skills)
│   ├── email-goals.md
│   ├── mental-model.md
│   ├── goals.md
│   ├── projects.md
│   └── .onboarded         ← presence = onboarding complete
├── .chroma/               ← ChromaDB SQLite store (gitignored)
└── handoffs/              ← session summaries + email drafts (gitignored)
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Streaming transport | SSE over WebSockets | Unidirectional stream; simpler; no upgrade handshake |
| Inference thread model | `ThreadPoolExecutor` | Ollama client is sync; executor bridges to async event loop |
| Approval gate | Non-blocking event | Skill stream ends immediately; no server-side await on user |
| Retrieval | Hybrid BM25 + vector + RRF | BM25 covers exact matches; vector covers semantics; RRF fuses without normalization |
| Context loading | Per-request, no cache | File system reads are fast; simplicity > premature optimization |
| Session state | In-memory dict | Local single-user app; persistence not worth the complexity |
| Embedding model | `nomic-embed-text` (768-dim) | Fully local; strong retrieval quality for its size |
