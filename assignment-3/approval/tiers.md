# Action Tier Classification

The orchestrator uses these tiers to decide when to pause for approval.

## Tier 0: Read (Auto — no pause, no log)

These actions only read data. They never modify anything.

- `query_knowledge` — search the knowledge base
- `corpus_stats` — check knowledge base status
- `list_events` — list calendar events
- `check_availability` — check free/busy slots
- Reading context files (goals.md, projects.md, etc.)

## Tier 1: Local Write (Auto — proceed, but log)

These actions write to the local filesystem. They don't affect
external systems. The orchestrator proceeds automatically but
records the action in the audit log.

- `ingest_single_file` — add a file to the knowledge base
- `ingest_documents` — add a directory to the knowledge base
- Writing handoff files to `handoffs/`
- Writing meeting notes to `handoffs/`

Log format:
```
[YYYY-MM-DD HH:MM] TIER 1 | AUTO | ingest_single_file | handoffs/session-handoff.md | 3 chunks
```

## Tier 2: External Write (Pause — show draft, wait for approval)

These actions affect external systems (calendar, email). The
orchestrator MUST pause, show what it wants to do, and wait for
explicit user confirmation.

- `create_event` — create a calendar event
- Saving an email draft via Gmail MCP
- Saving a stakeholder update draft

Pause format:
```
APPROVAL NEEDED — [action description]

   [Details of what will be created/sent]

   Proceed? (yes / edit / no)
```

If the user says "edit", ask what to change, update the draft,
and present it again. If "no", skip the action and continue
the workflow.

## Tier 3: Conflict (Pause — explain conflict, present options)

When the orchestrator detects a conflict between agent outputs
or between an agent's output and existing context, it MUST pause
and escalate.

- Priority conflicts (schedule vs. deliverables)
- Pattern contradictions (self-assessment vs. evidence)
- Tone mismatches (draft vs. prior communications)
- Uncompleted action items from prior meetings

Escalation format:
```
CONFLICT: [one-sentence description]

   [Evidence from source A]
   [Evidence from source B]

   Options:
   (a) [option]
   (b) [option]
   (c) Ignore — I'll handle it manually
```

Always include an "ignore" option. Never force a resolution.
