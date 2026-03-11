---
name: meeting
description: >
  Process a completed meeting. Triggered by "process meeting", "I just had a meeting",
  "meeting notes for [person/topic]", "capture meeting". Extracts decisions, action
  items, and relationship notes, then writes a structured meeting record.
allowed-tools: Read, Write
---

## Activation

Trigger phrases:

- `process meeting`
- `I just had a meeting`
- `meeting notes for [person or topic]`
- `capture meeting`
- `log meeting with [person]`

---

## Context Files

- `.claude/context/meetings.md` — recurring meetings and key relationships
- `.claude/context/projects.md` — active projects (to link action items)
- `.claude/context/context.md` — org context and key people

---

## Workflow

### Step 1 — Load Context

Read the three context files. Use `meetings.md` to recognize standing meetings and
key people; use `projects.md` to link action items to existing threads.

### Step 2 — Identify the Meeting

Ask:

> "Which meeting are we capturing? Give me the basics: who was in the room,
> what it was about, and roughly how long it ran."

If it matches a recurring meeting in `meetings.md`, note that and apply any standing
context from the record.

### Step 3 — Extract Raw Notes

Ask:

> "Go ahead and dump your notes or tell me what happened. Raw is fine —
> I'll structure it."

Accept freeform input: bullet points, stream-of-consciousness, partial sentences.
Do not ask for structure from the user.

### Step 4 — Ask for the Critical Pieces

After the raw dump, ask one clarifying question only if needed:

> "Two quick checks:
> 1. Any explicit decisions made that should be on record?
> 2. Any action items with owners and deadlines?"

If the user already covered these, skip this step.

### Step 5 — Write the Meeting Record

Write `handoffs/meeting-[YYYY-MM-DD]-[name-or-topic].md`:

```markdown
# Meeting: [Meeting Name or Topic]

**Date:** [date]
**Attendees:** [list]
**Duration:** [approx]

---

## Summary

[2-4 sentence plain-language summary of what the meeting was about and what happened]

## Decisions Made

- [Decision 1 — include who made it if relevant]
- [Decision 2]
- _(None recorded)_ if applicable

## Action Items

| Action | Owner | Due |
|--------|-------|-----|
| [Task] | [Who] | [When or "TBD"] |

## Relationship Notes

[Any observations about dynamics, relationship context, or things to remember
for future interactions with attendees. Omit if nothing notable.]

## Open Questions / Follow-ups

- [Anything unresolved that needs a follow-up]

## Connection to Projects

- [Link to relevant project from projects.md, if applicable]
```

### Step 6 — Confirm and Offer Next Step

After writing:

> "Meeting captured to `handoffs/meeting-[date]-[name].md`.
>
> Want to draft a follow-up email or calendar invite from this?"

If yes, hand off to `follow-up-email` or `follow-up-meeting` skill.
