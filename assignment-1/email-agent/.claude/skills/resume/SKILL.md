---
name: resume
description: >
  Resume a session from a prior handoff. Triggered by "resume", "good morning",
  "start session", "pick up where we left off", "what was I working on".
  Reads the session handoff and current goals/projects to orient the user.
allowed-tools: Read
---

## Activation

Trigger phrases:

- `resume`
- `good morning`
- `start session`
- `pick up where we left off`
- `what was I working on`

---

## Context Files

- `.claude/context/goals.md` — long-term goals and current priorities
- `.claude/context/projects.md` — active projects, blockers, priority map
- `handoffs/session-handoff.md` — prior session state (if it exists)

---

## Workflow

### Step 1 — Load Context

Read `.claude/context/goals.md` and `.claude/context/projects.md`.

Then check for `handoffs/session-handoff.md`:
- If it exists, read it.
- If it does not exist, note that this appears to be a fresh start and skip to Step 3.

### Step 2 — Synthesize Prior State

From the handoff file, identify:
- What was being worked on when the last session ended
- Any open decisions or pending actions
- Anything flagged as time-sensitive or carry-forward

### Step 3 — Orient the User

Present a brief orientation — 3-5 bullet points max:

```
---
RESUMING SESSION
---

Last session: [date from handoff, or "no prior session found"]

Where you left off:
- [Key thread 1]
- [Key thread 2]

Open items:
- [Action or decision still pending]

Today's goal alignment:
- [One sentence on whether the open items connect to stated goals]

What would you like to focus on?
---
```

If there is no handoff file, orient around current goals and projects instead:

```
---
STARTING FRESH
---

No prior session handoff found. Based on your context files:

Current priorities:
- [Top 1-2 from goals.md]

Active projects:
- [Top 1-2 from projects.md]

What would you like to work on?
---
```

### Step 4 — Hand Off to the User

Wait for the user to respond. Do not launch into any other skill automatically.
