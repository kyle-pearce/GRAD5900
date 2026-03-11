---
name: handoff
description: >
  Write a session handoff note. Triggered by "end session", "write handoff",
  "I'm done for today", "close out session". Synthesizes current context into
  a structured handoff without a full reflection dialogue.
allowed-tools: Read, Write
---

## Activation

Trigger phrases:

- `end session`
- `write handoff`
- `I'm done for today`
- `close out session`

Use `reflect` instead if you want a conversational end-of-day check-in before writing the handoff.

---

## Context Files

- `.claude/context/goals.md` — long-term goals and priorities
- `.claude/context/projects.md` — active projects and blockers
- `handoffs/session-handoff.md` — prior session state (read before overwriting)

---

## Workflow

### Step 1 — Load Context

Read `.claude/context/goals.md`, `.claude/context/projects.md`, and the current
`handoffs/session-handoff.md` if it exists.

### Step 2 — Ask for a Quick Summary

Ask the user one focused question:

> "Quick summary before I write the handoff: What did you work on this session,
> and is there anything carry-forward I should flag?"

Wait for the response. Do not ask follow-up questions — take what they give you.

### Step 3 — Write the Handoff

Write `handoffs/session-handoff.md` with this structure:

```markdown
# Session Handoff

**Date:** [today's date]
**Written by:** handoff skill

---

## What Was Worked On

[Summary of what the user described, in plain language]

## Open Items

- [Anything unfinished, flagged, or carry-forward]

## Decisions Made

- [Any decisions made this session, if mentioned]

## Next Session Starting Point

[One sentence: where to pick up next time]

## Goal Alignment Note

[One sentence: does today's work connect to stated goals? Flag if there's drift.]
```

### Step 4 — Confirm

After writing, confirm:

> "Handoff written to `handoffs/session-handoff.md`. Use `resume` at the start of
> your next session to reload this context."
