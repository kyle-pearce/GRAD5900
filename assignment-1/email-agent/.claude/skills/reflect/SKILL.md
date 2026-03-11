---
name: reflect
description: >
  Daily end-of-day reflection. Triggered by "daily reflection", "end of day",
  "reflect", "EOD check-in". Runs a structured conversational check-in, then
  writes a session handoff. Use this for depth; use handoff for speed.
allowed-tools: Read, Write
---

## Activation

Trigger phrases:

- `daily reflection`
- `end of day`
- `reflect`
- `EOD check-in`
- `let's reflect`

---

## Context Files

- `.claude/context/goals.md` — long-term goals and current priorities
- `.claude/context/projects.md` — active projects, blockers, priority map
- `.claude/context/decision-patterns.md` — known failure modes and coaching notes
- `handoffs/session-handoff.md` — prior session state (if it exists)

---

## Workflow

### Step 1 — Load Context

Read the four files listed above. Use the goals and decision-patterns to calibrate
what to listen for during the conversation.

### Step 2 — Open the Reflection

Greet the user and frame the session:

> "Let's do a quick end-of-day reflection. I'll ask a few questions — answer as much
> or as little as feels useful. Ready?"

Then ask the questions below **one at a time**. Wait for a real answer before moving on.
If an answer is thin or vague, ask one follow-up before proceeding.

### Step 3 — Reflection Questions

Ask these questions in order. Do not ask all at once.

1. "What did you actually work on today?"
2. "Did today reflect your priorities, or did you drift toward something else?"
3. "Any decisions made today — big or small — that are worth noting?"
4. "Anything stuck, blocked, or unresolved that you're carrying forward?"
5. "What's the most important thing to pick up tomorrow?"

After the five questions, check in:

> "Anything else worth capturing before I write this up?"

### Step 4 — Surface a Pattern (if relevant)

After the user's answers, check them against `decision-patterns.md`. If you notice
a known failure mode appearing (e.g., "avoiding a hard decision", "drifting toward
low-value work"), name it gently:

> "I noticed [observation]. That sounds like [pattern from decision-patterns.md].
> Worth flagging — you can ignore it if it doesn't fit."

Only do this if the connection is clear. Don't force it.

### Step 5 — Write the Handoff

Write `handoffs/session-handoff.md` with this structure:

```markdown
# Session Handoff

**Date:** [today's date]
**Written by:** reflect skill

---

## What Was Worked On

[Summary from the conversation, in the user's words where possible]

## Goal Alignment

[One sentence: did today's work reflect stated priorities? Flag drift if observed.]

## Decisions Made

- [Any decisions surfaced during reflection]

## Open Items / Carry-Forward

- [Anything unresolved or explicitly flagged for tomorrow]

## Pattern Note

[If a pattern from decision-patterns.md was surfaced, note it here. Omit if none.]

## Next Session Starting Point

[One sentence: where to pick up tomorrow]
```

### Step 6 — Close

After writing:

> "Handoff written. Good work today — see you tomorrow."

Do not summarize or add commentary beyond this. Let the user close the session.
