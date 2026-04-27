# Assignment 4 Plan: Local-First Personal Assistant (Ollama + FastAPI + React)

## Context

Assignment 4 is Phase 4 of the Personal Assistant Kit. It delivers the core skills from A1–A3
through a fully local stack — Ollama (llama3.2:3b) for inference, nomic-embed-text for embeddings,
ChromaDB for vector storage — wrapped in a FastAPI backend and React frontend.

First-time users are guided through an onboarding flow that configures their personal context
files. They can use Kyle's default context (pre-loaded from the Windows host via WSL2 mount) or
build their own context interactively with LLM assistance.

---

## The 6 Skills

| Button label | Skill file    | What it does                                                |
|--------------|---------------|-------------------------------------------------------------|
| Standup      | standup.py    | Daily EOD check-in (5 questions, writes session summary)   |
| Sync         | sync.py       | Meeting capture (decisions, action items, notes)           |
| Refinement   | refinement.py | Weekly planning (goals + projects → priority list)         |
| 1:1          | one_on_one.py | 1:1 prep for a named person                                |
| Email        | email.py      | Draft a reply (user pastes thread; never auto-sends)       |
| Close        | close.py      | End session → write handoff → auto-ingest into ChromaDB    |

### How Close works

1. User clicks "Close Session" in the sidebar
2. close skill generates a structured summary from the full chat history
3. Writes summary to handoffs/session-handoff.md on disk
4. Auto-ingests the file into ChromaDB (Tier 1 — logged, no approval needed)
5. Displays the summary in chat for review

### Approval gate for Email

The only Tier 2 action: saving an email draft. When email produces a draft, the backend emits
`approval_required`. The frontend renders an `ApprovalGate` card inline with
**Save Draft / Edit / Cancel**. The draft is not written to disk until the user approves.

---

## Onboarding Flow

### First-run detection

The backend checks for `context/.onboarded` at startup. If absent, `/api/onboarding/status`
returns `{ onboarded: false }`. The React app checks this on mount and redirects to `/onboard`
before rendering the main chat.

### Onboarding screen (React route: `/onboard`)

Two paths:

**Path A — Use defaults (Kyle's context)**
- Button: "Use default context (quick start)"
- Backend reads from WSL2-mounted Windows paths and copies to `context/`:
  - `/mnt/c/Users/kyle/Downloads/writing-style-draft.md` → `context/writing-style.md`
  - `/mnt/c/Users/kyle/Downloads/email-style-draft.md`   → `context/email-goals.md`
  - `/mnt/c/Users/kyle/Downloads/mental-model-draft.md`  → `context/mental-model.md`
- Placeholder files used for `goals.md` and `projects.md` (not covered by the defaults)
- Writes `context/.onboarded`, redirects to `/`

**Path B — Customize your context**
- A guided multi-step form with 5 short questions:
  - a. What is your role and what are you trying to accomplish? (→ goals.md)
  - b. What are your active projects right now? (→ projects.md)
  - c. How would you describe your writing and communication style? (→ writing-style.md)
  - d. What are your email habits and preferences? (→ email-goals.md)
  - e. How do you tend to make decisions? What are your known blind spots? (→ mental-model.md)
- After submission: backend calls llama3.2:3b to generate a well-structured context file from
  each answer, then writes it to `context/`
- Writes `context/.onboarded`, redirects to `/`

Users can re-run onboarding later via a "Reset context" option in settings.

---

## Context File Schema

| File             | Used by skills                  | Source (default)       |
|------------------|---------------------------------|------------------------|
| goals.md         | standup, refinement, one_on_one | placeholder            |
| projects.md      | refinement, one_on_one, sync    | placeholder            |
| writing-style.md | email                           | writing-style-draft.md |
| email-goals.md   | email                           | email-style-draft.md   |
| mental-model.md  | standup, one_on_one             | mental-model-draft.md  |

---

## Architecture

```
assignment-4/
│
├── backend/
│   ├── main.py                       ← FastAPI app; mounts all routers
│   ├── requirements.txt
│   ├── .env.example                  ← No API keys needed (Gmail OAuth optional)
│   │
│   ├── core/
│   │   ├── config.py                 ← Pydantic Settings: model name, paths, chroma dir
│   │   ├── ollama_client.py          ← stream_chat(), chat(), embed()
│   │   └── context.py                ← Loads context .md files per skill's declared needs
│   │
│   ├── knowledge/
│   │   ├── embeddings.py             ← OllamaEmbeddingFunction for ChromaDB
│   │   ├── ingest.py                 ← Ported from A2; uses Ollama embeddings
│   │   └── retriever.py              ← Ported from A2; judge/expand use llama3.2:3b
│   │
│   ├── skills/
│   │   ├── base.py                   ← BaseSkill: REQUIRED_CONTEXT + stream()
│   │   ├── standup.py
│   │   ├── sync.py
│   │   ├── refinement.py
│   │   ├── one_on_one.py
│   │   ├── email.py
│   │   └── close.py
│   │
│   ├── router.py                     ← Maps skill name → skill class
│   ├── approval.py                   ← asyncio.Event approval gate (email Tier 2)
│   │
│   └── api/
│       ├── chat.py                   ← POST /api/chat/send + GET /api/chat/stream (SSE)
│       ├── approval.py               ← POST /api/approval/{id}/respond
│       ├── knowledge.py              ← GET /api/knowledge/query + /stats; POST /ingest
│       └── onboarding.py             ← GET /api/onboarding/status
│                                         POST /api/onboarding/use-defaults
│                                         POST /api/onboarding/save-custom
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── src/
│       ├── App.tsx                   ← Checks onboarding status; routes to /onboard if needed
│       ├── main.tsx
│       │
│       ├── pages/
│       │   ├── Chat.tsx              ← Main chat page (two-column layout)
│       │   └── Onboard.tsx           ← Onboarding page: Path A or Path B
│       │
│       ├── components/
│       │   ├── Sidebar.tsx           ← Skill buttons + Close Session
│       │   ├── Chat/
│       │   │   ├── ChatWindow.tsx    ← Message list, auto-scroll
│       │   │   └── ChatMessage.tsx   ← User / assistant bubble (streaming)
│       │   ├── Approval/
│       │   │   └── ApprovalGate.tsx  ← Save Draft / Edit / Cancel
│       │   ├── Knowledge/
│       │   │   └── KnowledgePanel.tsx ← Search, ingest, corpus stats
│       │   └── Onboarding/
│       │       ├── PathSelector.tsx  ← "Use defaults" vs "Customize" choice cards
│       │       └── ContextForm.tsx   ← 5-question guided form (Path B)
│       │
│       ├── hooks/
│       │   ├── useChat.ts            ← EventSource consumer; streams tokens
│       │   └── useApproval.ts        ← Handles approval_required; POSTs response
│       │
│       └── api/
│           └── client.ts             ← Typed fetch wrappers
│
├── context/                          ← Runtime context files (written by onboarding)
│   ├── .onboarded                    ← Marker file; presence = onboarding complete
│   ├── goals.md                      ← Placeholder until user fills in
│   ├── projects.md                   ← Placeholder until user fills in
│   ├── writing-style.md              ← Written by onboarding
│   ├── email-goals.md                ← Written by onboarding
│   └── mental-model.md               ← Written by onboarding
│
├── handoffs/                         ← Session summaries written by close skill
│
└── README.md
```

---

## Key Technical Decisions

### Ollama Inference

- Python SDK: `ollama.chat(model="llama3.2:3b", stream=True, messages=[...])`
- `core/ollama_client.py` wraps `stream_chat()`, `chat()`, `embed()`
- Model name from `config.py`

### Embeddings (nomic-embed-text)

- `knowledge/embeddings.py` implements ChromaDB's `EmbeddingFunction` interface
- `ollama.embeddings(model="nomic-embed-text", prompt=text)` → 768-dim vectors
- Fresh `.chroma/` db in A4 (incompatible with A2's OpenAI-based db)

### Streaming (SSE)

- `GET /api/chat/stream?session_id=<id>` via `sse-starlette`
- Event types: `token`, `approval_required`, `done`
- `useChat` wraps `EventSource`; appends tokens to the active message bubble

### Approval Gate (Email only)

- `approval.py` holds `_pending: dict[str, asyncio.Event]`
- email skill emits `approval_required` before writing draft to disk
- User clicks Save / Edit / Cancel → `POST /api/approval/{id}/respond` → skill resumes

### Onboarding — Path A (defaults)

- `api/onboarding.py` reads from `/mnt/c/Users/kyle/Downloads/` (WSL2 mount of Windows host)
- Copies and renames files to `context/` directory
- Creates `context/.onboarded`

### Onboarding — Path B (custom)

- Frontend collects 5 free-text answers
- Backend sends each answer to llama3.2:3b with a prompt like:
  `"Generate a concise personal context file for [purpose] based on this description: [answer]"`
- Writes the LLM-generated markdown to the corresponding `context/*.md` file

### No MCP Servers

- FastAPI backend directly imports `knowledge/ingest.py` and `knowledge/retriever.py`
- REST endpoints replace the MCP protocol

---

## Implementation Phases

### Phase A — Backend scaffolding + Ollama

1. `core/config.py`, `core/ollama_client.py`
2. `main.py` + basic `api/chat.py` (non-streaming POST first)
3. Verify: `curl POST /api/chat/send` → llama3.2:3b response

### Phase B — RAG pipeline

1. `knowledge/embeddings.py` — OllamaEmbeddingFunction
2. `knowledge/ingest.py`, `knowledge/retriever.py` — port from A2
3. `api/knowledge.py`
4. Verify: ingest a doc, query it, self-correction triggers

### Phase C — Onboarding API + context files

1. `api/onboarding.py` — status, use-defaults, save-custom endpoints
2. Path A: copy from `/mnt/c/Users/kyle/Downloads/*.md`
3. Path B: LLM-generated context files from form answers
4. Placeholder `context/*.md` files for goals + projects
5. Verify: both paths write correct files, `.onboarded` created

### Phase D — Skill engine

1. `skills/base.py`, all 6 skill classes
2. `core/context.py` — load context per skill's `REQUIRED_CONTEXT`
3. `router.py`, SSE streaming in `api/chat.py`
4. Verify: trigger standup via API → streaming 5-question check-in

### Phase E — Approval gate

1. `approval.py` — asyncio.Event pattern
2. `api/approval.py` — respond endpoint
3. email skill Tier 2 behavior
4. Verify: email draft → approval_required fires → yes/cancel both work

### Phase F — React frontend: onboarding

1. Vite + React + TypeScript + Tailwind scaffold
2. `Onboard.tsx` — PathSelector + ContextForm
3. `App.tsx` checks `/api/onboarding/status` on mount; redirects to `/onboard` if needed
4. Verify: cold start → onboarding page; Path A completes in one click; Path B form submits

### Phase G — React frontend: main chat

1. `Chat.tsx` layout + `Sidebar.tsx` with skill buttons + Close Session
2. `ChatWindow` + `ChatMessage` + `useChat` SSE hook
3. `ApprovalGate.tsx` inline in chat
4. Verify: click Standup → streams check-in; email approval card renders correctly

### Phase H — Knowledge panel + Close Session

1. `KnowledgePanel.tsx`
2. Close Session → `POST /api/chat/close` → close skill → writes handoff → ingests
3. Verify: session → close → query knowledge → today's work in results

### Phase I — Polish + README

1. Error states (Ollama not running, ChromaDB empty, onboarding files missing)
2. "Reset context" link in sidebar → clears `.onboarded` → redirects to `/onboard`
3. README: prerequisites, ollama pull commands, install steps, start commands
4. Verify: cold start from README instructions works end-to-end

---

## Verification Checklist

- [ ] `ollama pull llama3.2:3b && ollama pull nomic-embed-text`
- [ ] Cold start → redirected to `/onboard` automatically
- [ ] Path A (defaults): one click → context files written from WSL2 mount → main chat loads
- [ ] Path B (custom): fill form → LLM generates context files → main chat loads
- [ ] Click Standup → 5-question check-in streams in chat
- [ ] Click Email, paste thread → draft appears → ApprovalGate renders → Save / Cancel works
- [ ] Click Close Session → handoff summary shown → ingested into ChromaDB
- [ ] Knowledge panel: ingest a .md file, query it, grounded answer returned
- [ ] "Reset context" → back to onboarding
- [ ] Zero Anthropic / OpenAI API keys required

---

## External Requirements

- Ollama installed and running (`ollama serve`)
- Python 3.12+, Node 20+
- Windows host files at `C:\Users\kyle\Downloads\` (for Path A defaults via WSL2 mount)
- Gmail OAuth (optional — email skill drafts without inbox access)
