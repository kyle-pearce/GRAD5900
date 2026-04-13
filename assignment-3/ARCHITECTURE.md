# System Architecture Design Document

**Course:** Applied Generative AI (GRAD 5900)
**Author:** Kyle Pearce
**Date:** 2026-04-13
**Scope:** Assignment 3 — Agentic Orchestration Layer with MCP Integration

---

## 1. Overview

Assignment 3 is **Phase 3 of 4** in the Personal Assistant Kit project. It builds a three-layer system on top of Assignments 1 and 2, preparing the foundation for the final user-facing phase:

| Phase | Layer | Purpose |
|-------|-------|---------|
| 1 | **Skills** | Specialized atomic capabilities in Claude Code |
| 2 | **Memory** | Standalone RAG knowledge base for long-term storage |
| **3 (Current)** | **Orchestration** | The "brain" — connects skills and memory via MCP with multi-agent workflows |
| 4 (Future) | **UI / App** | The "face" — a user-friendly desktop application for non-technical users |

Each layer builds on the one below it. MCP tools work standalone. The orchestrator uses
MCP tools. The approval layer wraps the orchestrator.

The result is a system where a single natural-language request like *"I just had my 1:1
with Sarah"* triggers a coordinated workflow: a meeting capture agent and a knowledge
retrieval agent run in parallel, their outputs feed a follow-up email agent and a calendar
invite agent (also in parallel), the orchestrator detects that an action item from the
last meeting was never completed, escalates that conflict to the user, and presents all
drafts as a single reviewable package — one approval gate, zero manual coordination.

---

## 2. The Problem Being Solved

### 2.1 State After Assignment 2

Assignment 1 built 12 specialized skills that operate on static context files. Assignment 2
added a searchable knowledge base with a filesystem watcher that auto-ingests handoff files
the moment A1 writes them. Data flows *into* the knowledge base — but there is no protocol
connecting Claude Code back to it for reads. The knowledge base is write-only from the
assistant's perspective: skills produce data that becomes searchable, but only via a
separate terminal (`python main.py query`), never from within the skills that produced it.

| Gap | Impact |
|-----|--------|
| One-way data flow: A1 writes into the knowledge base but cannot read from it | `coaching-prep` cannot search past meeting notes; `reflect` cannot compare today's patterns against last month's — even though that data is already ingested and searchable from the CLI |
| Skills run in isolation | "End of day" requires the user to manually invoke reflect, handoff, and ingest in sequence |
| No safety guardrails on actions | Nothing distinguishes a read (safe) from an external write (risky) |
| No conflict detection | `week-plan` and `reflect` can produce contradictory guidance with no one noticing |

### 2.2 What Changes for the User

| Workflow | Before (A1 + A2) | After (A3) |
|----------|-------------------|------------|
| "End of day" | Manually run reflect, then switch terminals to ingest the handoff | Say "end of day" — orchestrator runs reflect, auto-ingests, surfaces patterns from past weeks |
| "Prep for my 1:1 with Sarah" | Generic prep from static context | Orchestrator queries past meeting notes with Sarah, checks calendar for the 1:1 time, finds open action items, generates enriched prep |
| "Process meeting and schedule follow-up" | Two separate manual invocations, no shared state | Orchestrator chains meeting and follow-up, detects uncompleted action items from last time, pauses for approval before creating the calendar event |
| "Draft status update" | Drafts from static project context | Queries knowledge base for recent progress, drafts update, pauses for tone/content approval before saving |

---

## 3. Skill Clusters

The 12 A1 skills form natural clusters based on shared context and data flow. These
clusters determine which skills the orchestrator chains together.

```
Cluster 1: Reflection & Memory           Cluster 2: Meeting Lifecycle
(highest overlap)                         (high overlap)

reflect ──► handoff                       coaching-prep
    │                                         │
    ▼                                         ▼
weekly-report ──► week-plan               meeting ──► follow-up-meeting
                                                  ──► follow-up-email
Shared: goals.md, projects.md
Write to: handoffs/                       Shared: meetings.md, context.md
All query knowledge base                  All query knowledge base + calendar


Cluster 3: Communication                  Cluster 4: Strategic Thinking
(moderate overlap)                        (independent)

follow-up-email ↔ stakeholder-update      review-doc    decision

Shared: writing-style.md, context.md      Shared: decision-patterns.md
Both produce drafts requiring approval    Rarely interact with other clusters
```

Cluster 4 skills are on-demand — the orchestrator augments them with knowledge-search
but does not chain them automatically.

---

## 4. Layer 1 — MCP Tools (Weeks 8-9)

### 4.1 Purpose

Expose the A2 RAG pipeline and external services as MCP tools that any agent can call
natively. MCP is the "USB for AI" — one protocol, works with Claude Code, Gemini CLI,
Cursor, or any future client.

### 4.2 Servers and Tools

| Server | Tool | Tier | Purpose |
|--------|------|------|---------|
| `knowledge-base` | `query_knowledge` | 0 (read) | Search the knowledge base using the self-correcting hybrid retriever |
| `knowledge-base` | `ingest_documents` | 1 (local write) | Ingest all `.md`/`.txt` files from a directory into ChromaDB |
| `knowledge-base` | `ingest_single_file` | 1 (local write) | Ingest one file on demand |
| `knowledge-base` | `corpus_stats` | 0 (read) | Document count, collection name, last-modified time |
| `google-calendar` | `list_events` | 0 (read) | List upcoming calendar events |
| `google-calendar` | `check_availability` | 0 (read) | Check free/busy slots for a given date |
| `google-calendar` | `create_event` | 2 (external write) | Create a calendar event (attendees NOT auto-notified) |

The Tier column maps to the approval layer in Section 7.

### 4.3 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Claude Code (A1)                        │
│                                                           │
│  MCP Clients:                                             │
│    ├── gmail (existing)                                   │
│    ├── outlook (existing)                                 │
│    ├── knowledge-base (NEW) ──┐                           │
│    └── google-calendar (NEW) ─┤                           │
└───────────────────────────────┼───────────────────────────┘
                                │  MCP Protocol (stdio)
                ┌───────────────┼───────────────┐
                ▼                               ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  Knowledge Base Server   │  │  Google Calendar Server   │
│                          │  │                           │
│  Imports A2 modules:     │  │  google-api-python-client │
│  ├── retriever.py        │  │  ├── list_events          │
│  └── ingest.py           │  │  ├── check_availability   │
│         │                │  │  └── create_event         │
│         ▼                │  │         │                 │
│  ┌────────────┐          │  │  Google Calendar API      │
│  │ ChromaDB   │          │  │                           │
│  │ (.chroma/) │          │  │  sendUpdates="none"       │
│  └────────────┘          │  │  (never auto-notifies)    │
└──────────────────────────┘  └───────────────────────────┘
```

### 4.4 Key Design Decisions

- **Thin wrapper, not a rewrite.** The knowledge server imports A2's existing modules
  via `sys.path`. No code duplication. Improvements to A2's retrieval logic are picked
  up automatically.
- **stdio transport.** Claude Code spawns MCP servers as child processes. No ports, no
  HTTP, no auth tokens. Server starts with Claude Code and dies when it exits.
- **Shared ChromaDB instance.** The MCP server and A2's CLI/watcher share the same
  `.chroma/` directory. SQLite WAL mode handles concurrent access.
- **Self-correcting retriever by default.** `query_knowledge` always uses
  `SelfCorrectingRetriever` — every query gets relevance judgment and automatic query
  expansion when needed.
- **Calendar safety.** `create_event` uses `sendUpdates="none"` — attendees are never
  notified until the user manually sends from Google Calendar. Consistent with A1's
  "never send automatically" constraint.

### 4.5 What This Means for Data ETL

Before A3, getting knowledge into and out of the RAG pipeline required manual shell
commands in a separate terminal. After A3:

- **Retrieval** happens automatically whenever an agent needs historical context — no
  manual query
- **Ingestion** happens automatically at the end of every workflow — the orchestrator
  calls `ingest_single_file` after writing any new handoff file, so the corpus stays
  current without human intervention
- **The A2 watcher remains active** as a parallel sync path — any file written outside
  of an orchestrated workflow is still picked up within seconds

---

## 5. Layer 2 — Multi-Agent Orchestration (Week 10)

### 5.1 Design

The orchestrator is a Claude Code skill defined in `AGENTS.md` and
`.claude/skills/orchestrate/`. It is not a separate process — it runs inside Claude Code
and uses the same conversational back-and-forth that all A1 skills use. When the user
speaks, the orchestrator:

1. **Classifies intent** — maps to one or more skills
2. **Resolves dependencies** — determines parallel vs. sequential execution
3. **Routes context** — each agent gets only what it needs (per the A1 context load matrix)
4. **Detects conflicts** — compares agent outputs for contradictions
5. **Synthesizes results** — combines outputs into a coherent package
6. **Presents for approval** — tiered pause points based on action severity

### 5.2 Sub-Agent Mapping

Each sub-agent is dispatched by the orchestrator with a scoped task, the relevant context
files, and access to MCP tools. Sub-agents do not communicate with each other directly —
they receive inputs from the orchestrator and return outputs to the orchestrator. The
orchestrator is the only entity that holds the full picture.

| Sub-Agent | Source Skill | Output Type | Can Run In Parallel With |
|-----------|-------------|-------------|--------------------------|
| `session-resume` | `resume` | orientation summary | `knowledge-search` |
| `session-close` | `reflect` + `handoff` | session-handoff.md | `knowledge-search` |
| `week-planner` | `week-plan` | week plan doc | — (needs resume + search outputs) |
| `weekly-synthesizer` | `weekly-report` | weekly report doc | — (needs session-close output) |
| `meeting-capture` | `meeting` | meeting record + action items | `knowledge-search` |
| `prep-1on1` | `coaching-prep` | 1:1 prep sheet | other `prep-1on1` instances |
| `email-drafter` | `follow-up-email` | email draft | `invite-drafter` |
| `invite-drafter` | `follow-up-meeting` | calendar invite draft | `email-drafter` |
| `status-updater` | `stakeholder-update` | status update draft | other `status-updater` instances |
| `doc-reviewer` | `review-doc` | structured feedback | — (on-demand) |
| `decision-framer` | `decision` | decision analysis | `knowledge-search` |
| `knowledge-search` | A2 RAG (MCP) | retrieved context chunks | most other sub-agents |

`session-close` subsumes `handoff` — both write `session-handoff.md` at different depths.
The orchestrator uses `session-close` (the deeper version) unless the user explicitly
requests speed.

### 5.3 Dependency Graph

```
knowledge-search ──────────────────────────────────► (feeds all agents that need history)
                                                        │
                 ┌──────────────────────────────────────┤
                 │                                      │
                 ▼                                      ▼
          meeting-capture ─────────────────────► email-drafter  ┐
                 │                                       │      │── parallel
                 │                            invite-drafter  ──┘
                 │
          prep-1on1 ───────────────────────► (standalone output)

session-resume ──► week-planner ──► prep-1on1 (for each flagged 1:1)

session-close ──► weekly-synthesizer ──► status-updater ──► email-drafter

decision-framer ──► (optional) status-updater
```

### 5.4 Conflict Detection

The orchestrator does not just route — it watches for contradictions between agent outputs
and escalates them to the user rather than silently choosing one.

| Type | Example | Detection |
|------|---------|-----------|
| **Priority conflict** | `week-plan` schedules deep work Tuesday, but meeting notes show a Tuesday deliverable | Compare agent outputs against `goals.md` priorities and calendar events |
| **Pattern contradiction** | `reflect` says "improving at delegation" but `weekly-report` shows 3 new tasks taken on | Compare self-assessment language against quantitative signals in retrieved context |
| **Tone mismatch** | Email draft is casual but `query_knowledge` shows prior formal communication to same person | Compare draft tone against historical communication style |
| **Stale action items** | `meeting` produces new action items, but `query_knowledge` reveals unresolved items from the previous meeting with the same person | Compare new meeting record against retrieved history |

When a conflict is detected, the orchestrator does not resolve it — it escalates to the
human via a Tier 3 pause (see Section 7). Conflicts always require human judgment.

---

## 6. The Five Compound Workflows

### 6.1 Workflow 1 — Monday Morning Kickoff

**Trigger:** "good morning" / "start my week" / "plan my week"

**Skills involved:** `resume`, `week-plan`, `coaching-prep` (xN for flagged 1:1s)

```
User: "plan my week"
        │
        ▼
Orchestrator → MONDAY_KICKOFF workflow
        │
        ├── Parallel (Step 1):
        │   ├── session-resume agent
        │   │     reads: session-handoff.md, goals.md, projects.md
        │   │     returns: prior context summary
        │   │
        │   ├── knowledge-search agent
        │   │     query: "carry-forward items open decisions this week"
        │   │     returns: relevant chunks from recent handoffs
        │   │
        │   └── list_events (MCP — Tier 0, auto)
        │         query: this week's calendar
        │         returns: scheduled meetings with times
        │
        ├── Sequential (Step 2, after Step 1):
        │   └── week-planner agent
        │         reads: goals.md, projects.md, meetings.md
        │         input: context summary + retrieved chunks + calendar events
        │         returns: week plan with flagged 1:1s
        │
        │   ⚠️  CONFLICT CHECK: compare week plan priorities against calendar
        │       density and known deadlines from retrieved context
        │       → if conflict detected, escalate (Tier 3)
        │
        ├── Parallel (Step 3, one per flagged 1:1):
        │   ├── prep-1on1 agent (person: Sarah)
        │   │     reads: meetings.md, goals.md, projects.md
        │   │     calls: query_knowledge("1:1 Sarah action items")
        │   │     returns: 1:1 prep sheet
        │   │
        │   └── prep-1on1 agent (person: John)
        │         reads: meetings.md, goals.md, projects.md
        │         calls: query_knowledge("1:1 John decisions blockers")
        │         returns: 1:1 prep sheet
        │
        ├── Sequential (Step 4):
        │   └── ingest_single_file(week plan path) — Tier 1, auto + log
        │
        └── Orchestrator composes package:
              ┌─────────────────────────────────────┐
              │  MONDAY KICKOFF PACKAGE              │
              │                                      │
              │  Week Plan             (saved ✓)    │
              │  - Top 3 priorities                  │
              │  - Meeting prep needed               │
              │  - Watch-out                         │
              │                                      │
              │  1:1 Prep — Sarah      [save? Y/N]  │
              │  1:1 Prep — John       [save? Y/N]  │
              └─────────────────────────────────────┘
              → Approval gate
```

---

### 6.2 Workflow 2 — End of Day

**Trigger:** "end of day" / "EOD" / "daily wrap-up"

**Skills involved:** `reflect`

This is the lightweight daily workflow. It runs a single skill but extends it with
automatic ingestion and a pattern-surfacing step that the standalone `reflect` skill
cannot do on its own. For the heavier end-of-week version that adds `weekly-report`
and `stakeholder-update`, see Workflow 5 (Week Close).

```
User: "end of day"
        │
        ▼
Orchestrator → END_OF_DAY workflow
        │
        ├── Sequential (Step 1 — requires conversation):
        │   └── session-close agent
        │         reads: goals.md, projects.md, decision-patterns.md, prior handoff
        │         runs: reflection dialogue with user (5 questions)
        │         writes: handoffs/session-handoff.md
        │         returns: session handoff content
        │
        ├── Sequential (Step 2, after Step 1):
        │   └── ingest_single_file(session handoff) — Tier 1, auto + log
        │         handoff is now immediately searchable
        │
        ├── Sequential (Step 3, after Step 2):
        │   └── query_knowledge — Tier 0, auto
        │         query: "recurring patterns and themes from the last 4 weekly reflections"
        │         returns: historical pattern context
        │
        └── Orchestrator presents:
              ┌──────────────────────────────────────────────┐
              │  END OF DAY                                    │
              │                                               │
              │  Session Handoff        (saved ✓)            │
              │  Knowledge Base         (ingested ✓)         │
              │                                               │
              │  Patterns Surfaced:                           │
              │  "Over the last 3 weeks, you've mentioned     │
              │   feeling behind on the API doc. This is the  │
              │   4th time it's come up in reflections."       │
              └──────────────────────────────────────────────┘

Tier classification:
- Step 1: conversation (no tier)
- Step 2: Tier 1 (local write — auto, log it)
- Step 3: Tier 0 (read — auto)
```

This workflow is entirely automatic after the conversation — no Tier 2 or Tier 3
actions, so no approval gate is needed. The value is in the pattern surfacing step,
which gives the user longitudinal insight that a single reflection cannot.

---

### 6.3 Workflow 3 — Meeting Prep

**Trigger:** "prep for 1:1 with [person]" / "prep for meeting with [person]" / "get ready for [meeting]"

**Skills involved:** `coaching-prep`

Like End of Day, this wraps a single skill with MCP enrichment. The standalone
`coaching-prep` reads static context files; this workflow first gathers real calendar
data and historical context, then feeds enriched inputs to the prep agent.

```
User: "prep for my 1:1 with Sarah tomorrow"
        │
        ▼
Orchestrator → MEETING_PREP workflow
        │
        ├── Parallel (Step 1 — all Tier 0, auto):
        │   ├── list_events (MCP)
        │   │     query: next 3 days
        │   │     returns: Sarah 1:1 confirmed Thu 2:00pm
        │   │
        │   ├── query_knowledge (MCP)
        │   │     query: "past meeting notes with Sarah"
        │   │     returns: chunks from meeting-*-sarah.md handoffs
        │   │
        │   └── query_knowledge (MCP)
        │         query: "open action items involving Sarah"
        │         returns: unresolved items from past meetings
        │
        │   ⚠️  CONFLICT CHECK: if open action items found from prior meetings
        │       that were never resolved, escalate (Tier 3):
        │       "Action item 'migrate auth module' from March 30 meeting
        │        with Sarah was never completed.
        │        (a) Include in prep talking points
        │        (b) Mark as dropped
        │        (c) Ignore"
        │
        ├── Sequential (Step 2, after Step 1):
        │   └── prep-1on1 agent
        │         reads: meetings.md, goals.md, projects.md, decision-patterns.md
        │         input: calendar data + retrieved history + conflict resolution
        │         returns: enriched 1:1 prep sheet
        │
        └── Orchestrator presents:
              ┌──────────────────────────────────────────────┐
              │  MEETING PREP — 1:1 with Sarah                │
              │  Thursday April 16, 2:00pm (from calendar)    │
              │                                               │
              │  Prep Sheet             [save? Y/N]          │
              │  - Context to recall                         │
              │  - Agenda topics (informed by past meetings)  │
              │  - Open items from last time                  │
              │  - Your asks / decisions needed               │
              └──────────────────────────────────────────────┘

Tier classification:
- Step 1: Tier 0 (reads — auto)
- Conflict check: Tier 3 (if triggered)
- Step 2: presentation (no tier)
```

Meeting Prep is distinct from the Monday Kickoff's `prep-1on1` step: Monday Kickoff
generates prep sheets for *all* flagged 1:1s in bulk as part of weekly planning.
Meeting Prep is an on-demand, single-person deep dive that the user triggers before
a specific meeting.

---

### 6.4 Workflow 4 — Meeting Lifecycle

**Trigger:** "I just had a meeting with [person]" / "process meeting and schedule follow-up"

**Skills involved:** `meeting`, `follow-up-email`, `follow-up-meeting`

```
User: "I just had my 1:1 with Sarah"
        │
        ▼
Orchestrator → MEETING_LIFECYCLE workflow
        │
        ├── Parallel (Step 1):
        │   ├── meeting-capture agent
        │   │     reads: meetings.md, projects.md, context.md
        │   │     asks user: attendees, what happened, decisions, action items
        │   │     returns: structured meeting record
        │   │
        │   └── knowledge-search agent
        │         query: "Sarah past meetings action items open decisions"
        │         returns: relevant history chunks
        │
        │   ⚠️  CONFLICT CHECK: compare new action items against unresolved
        │       items from retrieved history
        │       → if stale items found, escalate (Tier 3):
        │         "Open item from last time was never completed.
        │          (a) Add to follow-up agenda  (b) Mark dropped  (c) Ignore"
        │
        ├── Parallel (Step 2, after Step 1):
        │   ├── email-drafter agent
        │   │     reads: writing-style.md, response-framework.md
        │   │     input: meeting record + action items + conflict resolution
        │   │     calls: mcp__gmail__* (fetch Sarah's email for threading)
        │   │     returns: follow-up email draft
        │   │
        │   ├── invite-drafter agent
        │   │     reads: context.md, meetings.md
        │   │     input: meeting record + follow-up items
        │   │     calls: check_availability(next week)
        │   │     returns: calendar invite draft with real available times
        │   │
        │   └── ingest_single_file(meeting record) — Tier 1, auto + log
        │
        └── Orchestrator composes package:
              ┌──────────────────────────────────────────────┐
              │  MEETING LIFECYCLE PACKAGE                    │
              │                                               │
              │  Meeting Record          (saved ✓)           │
              │  handoffs/meeting-2026-04-13-sarah.md         │
              │                                               │
              │  Follow-up Email Draft   [send? Y/N]         │
              │  To: sarah@company.com                        │
              │  Re: 1:1 follow-up — action items             │
              │  [draft body...]                              │
              │                                               │
              │  Calendar Invite Draft   [send? Y/N]         │
              │  Title: Follow-up / Kyle + Sarah              │
              │  When: Thu Apr 16 2:00pm (confirmed free)     │
              │  [agenda...]                                  │
              └──────────────────────────────────────────────┘
              → Approval gate
```

---

### 6.5 Workflow 5 — Week Close

**Trigger:** "end of week" / "weekly review" / "weekly synthesis"

**Skills involved:** `reflect`, `weekly-report`, `stakeholder-update`, `follow-up-email`

This is the heavier counterpart to End of Day. It includes the reflection conversation
but extends it with a weekly synthesis, stakeholder updates, and email drafts.

```
User: "end of week"
        │
        ▼
Orchestrator → WEEK_CLOSE workflow
        │
        ├── Sequential (Step 1 — requires conversation):
        │   └── session-close agent
        │         reads: goals.md, projects.md, decision-patterns.md, prior handoff
        │         runs: reflection dialogue with user (5 questions)
        │         returns: session handoff content
        │
        ├── Parallel (Step 2, after Step 1):
        │   ├── knowledge-search agent
        │   │     query: "this week decisions blockers completed work"
        │   │     returns: chunks from this week's handoffs and meeting records
        │   │
        │   └── ingest_single_file(session handoff) — Tier 1, auto + log
        │
        ├── Sequential (Step 3, after Step 2):
        │   └── weekly-synthesizer agent
        │         reads: goals.md, projects.md
        │         input: session handoff + all retrieved week context
        │         returns: weekly report (patterns, goal alignment, carry-forward)
        │
        │   ⚠️  CONFLICT CHECK: compare reflect self-assessment against
        │       quantitative patterns in weekly report
        │       → if pattern contradiction found, escalate (Tier 3):
        │         "You said you're getting better at delegation, but this
        │          week you took on 3 new tasks from others."
        │
        ├── Parallel (Step 4, one per relevant stakeholder):
        │   ├── status-updater agent (stakeholder: manager)
        │   │     reads: projects.md, writing-style.md
        │   │     input: weekly report highlights
        │   │     returns: status update draft
        │   │
        │   └── email-drafter agent
        │         reads: writing-style.md, response-framework.md
        │         input: status update content
        │         calls: query_knowledge("[manager] prior updates tone")
        │         returns: formatted email draft
        │
        │   ⚠️  CONFLICT CHECK: compare draft tone against retrieved prior
        │       communication tone with this recipient
        │
        ├── Sequential (Step 5):
        │   └── ingest_documents(weekly report) — Tier 1, auto + log
        │
        └── Orchestrator composes package:
              ┌──────────────────────────────────────────────┐
              │  WEEK CLOSE PACKAGE                           │
              │                                               │
              │  Session Handoff        (saved ✓)            │
              │  Weekly Report          (saved ✓)            │
              │                                               │
              │  Manager Status Update  [send? Y/N]          │
              │  To: manager@company.com                      │
              │  Subject: Week of Apr 13 — Status Update      │
              │  [draft body...]                              │
              └──────────────────────────────────────────────┘
              → Approval gate
```

---

## 7. Layer 3 — Human-in-the-Loop Approval (Week 11)

### 7.1 Tier Definitions

The approval layer classifies every action by its reversibility and blast radius.
The principle: **reads are free, writes require awareness, external actions require
consent, conflicts require judgment.**

```
┌──────────┬──────────────┬──────────────────────────────────────────────┐
│ Tier     │ Behavior     │ Actions                                      │
├──────────┼──────────────┼──────────────────────────────────────────────┤
│ 0: Read  │ Auto         │ query_knowledge, list_events,                │
│          │              │ check_availability, corpus_stats              │
├──────────┼──────────────┼──────────────────────────────────────────────┤
│ 1: Local │ Auto + Log   │ ingest_single_file, ingest_documents,        │
│   Write  │              │ write handoff, save meeting notes             │
├──────────┼──────────────┼──────────────────────────────────────────────┤
│ 2: Ext.  │ Pause +      │ create_event, save email draft to Gmail,     │
│   Write  │ Approve      │ stakeholder update send                      │
├──────────┼──────────────┼──────────────────────────────────────────────┤
│ 3: Con-  │ Pause +      │ Orchestrator-detected conflicts between      │
│   flict  │ Escalate     │ agent outputs (priority, pattern, tone,      │
│          │              │ stale action items)                           │
└──────────┴──────────────┴──────────────────────────────────────────────┘
```

### 7.2 How Pause Points Work

When the orchestrator hits a Tier 2 or Tier 3 action:

1. **Pause** — workflow state is held (which agents ran, what is pending)
2. **Present** — show the user what it wants to do and why
3. **Wait** — user approves, edits, or rejects
4. **Resume** — continue the workflow or re-route based on feedback

This is not a separate system — it is behavior encoded in the orchestrator skill's
instructions. Claude Code already supports conversational back-and-forth, so "pausing"
means the orchestrator asks a question and waits for the user's response before proceeding.

### 7.3 Approval UX

**Tier 2 — External write:**
```
APPROVAL NEEDED — Create calendar event:
   "1:1 Kyle + Sarah"
   Thursday April 16, 2:00-2:30 PM
   Agenda: Review API doc draft, follow up on auth migration

   Create this event? (yes / edit / no)
```

**Tier 3 — Conflict escalation:**
```
CONFLICT: Your week plan has deep work blocked for Tuesday,
   but Sarah's meeting notes indicate she expects the API doc
   by Tuesday EOD.

   (a) Move deep work to Wednesday, prioritize API doc
   (b) Keep the plan — I'll update Sarah on the timeline
   (c) Ignore — I'll handle it manually
```

### 7.4 Edit Flow

At the approval gate, `edit` re-enters the relevant sub-agent with the user's revision
instruction. The sub-agent rewrites only the affected output. The orchestrator does not
re-run the entire workflow.

```
User: "edit" → "make the email shorter and reference the infra blocker"
                        │
                        ▼
            email-drafter agent (revision pass)
            input: original draft + revision instruction + meeting record
            returns: revised draft
                        │
                        ▼
            Approval gate re-presented for revised draft only
```

### 7.5 Audit Trail

All Tier 1+ actions are logged to `handoffs/action-log.md` with timestamp, action, tier,
and outcome (auto / approved / rejected / escalated). This gives the user a persistent
record of everything the system did and every decision they made.

```markdown
## Action Log

| Time | Workflow | Action | Tier | Outcome |
|------|----------|--------|------|---------|
| 2026-04-13 17:02 | WEEK_CLOSE | write session-handoff.md | 1 | auto |
| 2026-04-13 17:02 | WEEK_CLOSE | ingest session-handoff.md | 1 | auto |
| 2026-04-13 17:03 | WEEK_CLOSE | pattern contradiction detected | 3 | escalated → user chose (a) |
| 2026-04-13 17:04 | WEEK_CLOSE | write weekly-report.md | 1 | auto |
| 2026-04-13 17:05 | WEEK_CLOSE | send manager status update | 2 | approved |
```

---

## 8. Unified Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                        Claude Code                            │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                  Orchestrator Skill                     │   │
│  │                                                        │   │
│  │  Intent ──► Workflow ──► Agent Dispatch ──► Synthesis   │   │
│  │                              │                         │   │
│  │              ┌───────────────┼───────────────┐         │   │
│  │              ▼               ▼               ▼         │   │
│  │        ┌──────────┐   ┌──────────┐   ┌──────────┐     │   │
│  │        │ Reflect  │   │ Meeting  │   │ Coaching │     │   │
│  │        │ Agent    │   │ Agent    │   │ Prep     │     │   │
│  │        └────┬─────┘   └────┬─────┘   └────┬─────┘     │   │
│  │             │              │              │            │   │
│  │  ┌──────────▼──────────────▼──────────────▼─────────┐  │   │
│  │  │            Approval Layer (HITL)                  │  │   │
│  │  │                                                  │  │   │
│  │  │  Tier 0: pass    Tier 1: log                     │  │   │
│  │  │  Tier 2: pause + approve    Tier 3: escalate     │  │   │
│  │  └──────────┬──────────────┬──────────────┬─────────┘  │   │
│  └─────────────┼──────────────┼──────────────┼────────────┘   │
│                │              │              │                 │
│           MCP Tools           │              │                 │
│  ┌─────────────▼──┐  ┌───────▼────┐  ┌──────▼───┐            │
│  │ knowledge-base │  │  calendar  │  │  gmail   │            │
│  │                │  │            │  │          │            │
│  │ query_knowledge│  │ list_events│  │ (exist.) │            │
│  │ ingest_*       │  │ check_avl. │  │          │            │
│  │ corpus_stats   │  │ create_evt │  │          │            │
│  └───────┬────────┘  └──────┬─────┘  └──────────┘            │
│          │                  │                                 │
│          ▼                  ▼                                 │
│    ┌──────────┐      Google Calendar                          │
│    │ ChromaDB │      API                                      │
│    └──────────┘                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 9. Skill Coverage

The five workflows cover 10 of 12 skills in orchestrated context. Two remain on-demand.

| Skill | Coverage | Workflow(s) |
|-------|---------|-------------|
| `resume` | Orchestrated | Workflow 1 (Monday Kickoff) |
| `handoff` / `reflect` | Orchestrated | Workflow 2 (End of Day), Workflow 5 (Week Close) |
| `week-plan` | Orchestrated | Workflow 1 (Monday Kickoff) |
| `weekly-report` | Orchestrated | Workflow 5 (Week Close) |
| `coaching-prep` | Orchestrated | Workflow 1 (Monday Kickoff), Workflow 3 (Meeting Prep) |
| `meeting` | Orchestrated | Workflow 4 (Meeting Lifecycle) |
| `follow-up-email` | Orchestrated | Workflow 4 (Meeting Lifecycle), Workflow 5 (Week Close) |
| `follow-up-meeting` | Orchestrated | Workflow 4 (Meeting Lifecycle) |
| `stakeholder-update` | Orchestrated | Workflow 5 (Week Close) |
| `decision` | **On-demand** | Orchestrator chains `knowledge-search`; optionally chains `status-updater` |
| `review-doc` | **On-demand** | Orchestrator augments with knowledge-search; no automatic chaining |

---

## 10. Implementation Plan

### Phase A — MCP Servers

- Create `knowledge-server/server.py` using FastMCP (Python `mcp` SDK)
- Implement tools: `query_knowledge`, `ingest_documents`, `ingest_single_file`, `corpus_stats`
- Import `SelfCorrectingRetriever` and ingestion pipeline from A2 via `sys.path`
- Create `calendar-server/server.py` using FastMCP
- Implement tools: `list_events`, `check_availability`, `create_event`
- Wire `create_event` with `sendUpdates="none"`
- Register both servers in `assignment-1/ai-assistant/.claude/settings.json`
- Verify with `claude mcp list`

### Phase B — Orchestrator Skill

- Create `.claude/skills/orchestrate/SKILL.md` with workflow definitions
- Define intent classifier logic (maps user utterance to workflow)
- Define dependency graphs for all three workflows
- Define conflict detection rules
- Wire MCP tool access for knowledge-search and calendar lookups

### Phase C — Approval Layer

- Define tier classification for all tools and actions in orchestrator skill
- Implement Tier 2 pause-and-present pattern (conversational approval)
- Implement Tier 3 conflict escalation pattern (choices presented to user)
- Create `handoffs/action-log.md` template and logging behavior

### Phase D — Workflow Integration

- Implement MONDAY_KICKOFF workflow (Workflow 1)
- Implement END_OF_DAY workflow (Workflow 2)
- Implement MEETING_PREP workflow (Workflow 3)
- Implement MEETING_LIFECYCLE workflow (Workflow 4)
- Implement WEEK_CLOSE workflow (Workflow 5)
- Implement ON_DEMAND fallback for `decision` and `review-doc`

### Phase E — End-to-End Validation

- Run END_OF_DAY: verify reflect runs, handoff auto-ingested, patterns surfaced from
  historical context
- Run MEETING_PREP: verify calendar lookup returns real meeting time, knowledge queries
  return past meeting history, stale action item conflict detected if applicable
- Run MEETING_LIFECYCLE: capture a meeting, verify conflict detection triggers on
  stale action items, verify email + invite drafts surface at approval gate, verify
  meeting record auto-ingested into ChromaDB
- Run MONDAY_KICKOFF: verify calendar events appear in week plan, verify 1:1 prep
  sheets generated for each flagged meeting
- Run WEEK_CLOSE: verify weekly report compares against retrieved week context,
  verify pattern contradiction detection works, verify status update held for approval
- Verify edit loop: revise email draft at approval gate, confirm only email-drafter
  re-runs
- Verify audit trail: confirm `handoffs/action-log.md` reflects all actions
- Confirm A2 watcher still functions as parallel ingest path

---

## 11. Directory Structure

```
grad5900/
├── assignment-1/
│   └── ai-assistant/
│       └── .claude/
│           ├── settings.json              ← ADD: knowledge + calendar MCP entries
│           └── skills/
│               └── orchestrate/SKILL.md   ← NEW: orchestrator skill definition
│
├── assignment-2/
│   └── rag-assistant/
│       └── knowledge/
│           ├── ingest.py                  ← imported by A3 (no changes)
│           └── retriever.py               ← imported by A3 (no changes)
│
└── assignment-3/
    ├── ARCHITECTURE.md                    ← This document
    │
    ├── mcp-servers/
    │   ├── knowledge-server/
    │   │   ├── server.py                  ← FastMCP: query, ingest, stats
    │   │   ├── requirements.txt
    │   │   └── README.md
    │   │
    │   └── calendar-server/
    │       ├── server.py                  ← FastMCP: list, availability, create
    │       ├── requirements.txt
    │       └── README.md
    │
    ├── orchestrator/
    │   ├── ORCHESTRATOR.md                ← Skill definition for orchestrator agent
    │   ├── workflows.md                   ← Workflow dependency graphs + step definitions
    │   └── conflicts.md                   ← Conflict detection rules and escalation patterns
    │
    ├── approval/
    │   ├── tiers.md                       ← Tier classification for all tools/actions
    │   └── action-log-template.md         ← Template for the audit trail
    │
    └── README.md                          ← Setup, testing, and demo instructions
```

---

## 12. Design Decisions

### Why a Claude Code skill instead of a separate Python orchestrator?

Claude Code already supports conversational back-and-forth, skill dispatch, and MCP tool
access. Building the orchestrator as a skill means:
- "Pausing" at a Tier 2 action is just asking a question and waiting for the answer —
  no custom terminal UI needed
- Sub-agent dispatch uses Claude Code's existing capabilities — no second runtime
- Conflict escalation is a natural part of the conversation, not a mode switch
- The orchestrator composes skills that are already defined and tested in A1

A separate Python orchestrator with `asyncio` + `AsyncAnthropic` would make the
architecture more explicit and inspectable, but would add significant scaffolding for
a capability Claude Code already provides. The real parallelism bottleneck is always
LLM response time, not Python async coordination.

### Why two MCP servers instead of one?

The knowledge base and Google Calendar have entirely different dependencies, auth models,
and failure modes. A single server would couple them: a ChromaDB issue would take down
calendar access. Separate servers mean independent startup, independent failure, and
cleaner dependency trees.

### Why a Google Calendar MCP server?

Three skills materially improve with real calendar data:
- `coaching-prep` can see actual 1:1 times instead of guessing from static `meetings.md`
- `follow-up-meeting` can check real availability with `check_availability` instead of
  proposing hypothetical time slots
- `week-plan` can see what is actually scheduled and detect conflicts between planned
  priorities and calendar density

Calendar safety: `create_event` uses `sendUpdates="none"` so attendees are never notified
until the user manually sends from Google Calendar — consistent with A1's "never send
automatically" constraint.

### Why auto-ingest after every workflow?

Keeping ChromaDB current is a prerequisite for retrieval being useful. If the orchestrator
writes a meeting record but does not ingest it, the next workflow's knowledge-search will
miss it. Auto-ingesting at workflow completion (Tier 1, logged) makes the corpus
self-maintaining.

### Why detect conflicts instead of resolving them?

The orchestrator flags contradictions but never picks a winner. Conflict resolution
requires human judgment about priorities, trade-offs, and context the model does not have.
Auto-resolving would create a false sense of coherence while potentially making the wrong
call. Escalating to Tier 3 keeps the human in the loop where it matters most.

### Why are `decision` and `review-doc` on-demand rather than chained?

Both skills require freeform conversation that does not fit cleanly into a pre-defined
workflow. Forcing them into compound workflows would require predicting what decision or
document comes next, which is not possible without user input. The orchestrator handles
them as direct invocations with knowledge-search augmentation.

### Graceful degradation

If the knowledge MCP server is unavailable, agents fall back to static context file reads.
If the calendar server is unavailable, `invite-drafter` proposes times from `meetings.md`
preferences instead of checking real availability. If a sub-agent errors, the orchestrator
surfaces the failure at the approval gate with remaining outputs intact — a single failure
does not abort the workflow.

---

## 13. Scope and Risks

### In Scope

- Knowledge Base MCP server (4 tools)
- Google Calendar MCP server (3 tools)
- Orchestrator skill with workflow definitions for 3 key workflows
- Tiered approval system (Tier 0-3)
- Conflict detection for priority, pattern, tone, and stale action item mismatches
- Action audit log
- End-to-end demo: user says "I just had my 1:1 with Sarah" — orchestrator captures
  meeting, detects stale action items, drafts email + invite, pauses for approval

### Out of Scope

- Modifying A1 skill internals (orchestrator composes them, does not rewrite them)
- Automated conflict resolution (conflicts always escalate to human)
- Persistent workflow state across sessions (workflows complete within a single session)
- Additional MCP servers beyond knowledge and calendar

### Risks

| Risk | Mitigation |
|------|------------|
| ChromaDB concurrent writes from watcher + MCP server | SQLite WAL mode serializes writes. Ingestion is infrequent and fast. |
| `sys.path` import of A2 modules is fragile | Document in README. Future: package A2 as an installable module. |
| Orchestrator over-triggers on simple requests | Intent classifier defaults to single-skill execution. Multi-agent workflows only activate on compound intents ("process meeting AND schedule follow-up"). |
| Approval fatigue — too many Tier 2 pauses | Only external writes pause. Reads and local writes are silent or log-only. User can downgrade specific actions in `tiers.md`. |
| Google Calendar OAuth scope creep | Request only `calendar` scope. `create_event` uses `sendUpdates="none"`. No delete capability exposed. |

---

## 14. Course Topic Coverage

| Phase | Week | Topic | Where in Assignment 3 |
|-------|------|-------|----------------------|
| 3 | 8 | MCP Foundations — "USB for AI" | `knowledge-server/` + `calendar-server/` — MCP protocol, tool registration, stdio transport |
| 3 | 9 | Building MCP Servers — Lab | Two custom Python MCP servers: one bridging Claude Code to a private RAG knowledge base, one to Google Calendar |
| 3 | 10 | Multi-Agent Workflows — manager/worker | Orchestrator skill + 12 sub-agents; skill clusters; dependency graphs; conflict detection; three compound workflows |
| 3 | 11 | Human-in-the-Loop & Memory | 4-tier approval system; conflict escalation; audit trail; auto-ingest keeps ChromaDB as persistent long-term memory |

---

## 15. The Complete Three-Assignment Arc

```
Assignment 1              Assignment 2              Assignment 3
─────────────────         ─────────────────         ─────────────────────────
Interface layer           Knowledge layer           Orchestration + Bridge

12 skills as              RAG pipeline:             MCP servers: knowledge
static instruction        hybrid retrieval,         and calendar are live
files in Claude Code      self-correction,          infrastructure callable
                          RAGAS evaluation          by any agent at any time

User manages each         User queries via          Orchestrator: high-level
skill manually,           Python CLI in a           intent decomposes into
one at a time             second terminal           coordinated agents

Static context:           Queryable memory:         Seamless ETL: ingestion
read once per session     search all past docs      automatic after every
                                                    workflow

No safety tiers           No safety tiers           4-tier approval: reads
                                                    auto, local writes log,
                                                    external writes pause,
                                                    conflicts escalate

No conflict awareness     No conflict awareness     Orchestrator detects
                                                    contradictions between
                                                    agent outputs and
                                                    escalates to human

Output: handoff  ──►  Input: same files  ──►  Output: multi-draft package
        files           auto-ingested              surfaced for human review
```

The three assignments together implement a complete personal AI assistant with:
- A **persistent identity** (A1 context files — who you are, how you work)
- A **searchable episodic memory** (A2 ChromaDB — everything you have done)
- A **native knowledge interface** (A3 MCP servers — memory and calendar available to all agents)
- A **coordinated action layer** (A3 orchestrator — agents work in parallel, conflicts detected)
- A **human safety net** (A3 approval layer — tiered consent, nothing irreversible without you)
