---
name: follow-up-meeting
description: >
  Draft a calendar invite for a follow-up meeting. Triggered by "draft calendar invite",
  "schedule follow-up", "book a meeting after", "send a calendar invite". Produces
  a complete invite draft with attendees, agenda, and logistics. Never sends automatically.
allowed-tools: mcp__gmail__*, mcp__outlook__*, Read
context: fork
---

## Activation

Trigger phrases:

- `draft calendar invite`
- `schedule follow-up`
- `book a meeting after`
- `send a calendar invite`
- `follow-up meeting with [person]`
- `set up a meeting with [person]`

---

## Context Files

- `.claude/context/context.md` — timezone, meeting preferences, scheduling conventions
- `.claude/context/meetings.md` — key relationships and standing context about people

---

## Workflow

### Step 1 — Load Context

Read `.claude/context/context.md` and `.claude/context/meetings.md`.

Note the user's timezone, preferred meeting lengths, and preferred days/times from `context.md`.

### Step 2 — Gather the Basics

Ask:

> "A few quick questions for the invite:
> 1. Who's this meeting with?
> 2. What's it for — what do you want to accomplish?
> 3. How long? (Default from your preferences: [length from context.md])"

If this follows a processed meeting (i.e., the user says "follow up on the meeting we just
captured"), reference the meeting record for attendees and purpose.

### Step 3 — Propose Time Options

Ask:

> "Do you have specific times in mind, or should I suggest options based on your
> preferences?"

If no times specified, propose 2-3 options using the preferred days/times from `context.md`.

### Step 4 — Draft the Invite

Compose the calendar invite:

```
---
DRAFT CALENDAR INVITE
---

Title: [Clear, action-oriented title — e.g., "Follow-up: Q3 Planning / Kyle + [Name]"]

To: [Attendee emails]
When: [Proposed time options, or confirmed time]
Duration: [Length]
Location/Link: [TBD — add video link or room before sending]

---
AGENDA
---

Purpose: [One sentence on why we're meeting]

1. [Agenda item 1] — [5-10 min]
2. [Agenda item 2] — [5-10 min]
3. [Wrap / next steps] — [5 min]

Pre-read (if any): [Link or description]

---

[Optional note to attendees — e.g., "Looking forward to continuing the conversation from [context]."]

---
Review this invite draft. To save or send:
- "save draft" — save to calendar app without sending
- "send" — only use if you explicitly want to send now
- "adjust [detail]" — modify any field
---
```

**NEVER** call any send or create tool without explicit user instruction.

### Step 5 — Revision Loop

Offer to adjust any element. If the user says "send" or "save draft", use the
appropriate MCP tool (`create_event` or equivalent). Confirm before executing.
