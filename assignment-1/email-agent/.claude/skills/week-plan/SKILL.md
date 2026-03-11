---
name: week-plan
description: >
  Plan the week ahead. Triggered by "plan my week", "weekly planning", "Monday planning",
  "what should I focus on this week". Reviews goals, projects, and upcoming meetings
  to produce a focused weekly plan.
allowed-tools: Read, Write
---

## Activation

Trigger phrases:

- `plan my week`
- `weekly planning`
- `Monday planning`
- `what should I focus on this week`
- `help me plan the week`

---

## Context Files

- `.claude/context/goals.md` — long-term goals and current priorities
- `.claude/context/projects.md` — active projects, blockers, priority map
- `.claude/context/meetings.md` — recurring meetings and key relationships
- `handoffs/session-handoff.md` — carry-forward from last session (if exists)

---

## Workflow

### Step 1 — Load Context

Read all four context files. Note carry-forward items from the session handoff.

### Step 2 — Ask One Orienting Question

Ask:

> "Before I draft the week plan — anything from last week that should shape this week?
> (Deadlines, blocked items, commitments made?)"

Take their answer and incorporate it. Do not ask additional questions unless the
answer introduces a critical ambiguity.

### Step 3 — Build the Plan

Using goals, projects, meetings context, and the user's input, construct a weekly plan:

**Priority logic:**
1. Commitments with deadlines this week come first
2. Highest-priority projects (from `projects.md`) come second
3. Goal-aligned work that has no deadline but is important comes third
4. Recurring meeting prep fits around the above

**Meeting load:**
Scan `meetings.md` for recurring meetings likely to fall this week. Flag any that
require prep (1:1s, reviews, presentations) and block time accordingly.

### Step 4 — Present the Plan

Output in this format:

```
---
WEEK PLAN — [week of date]
---

Top 3 Priorities
1. [Most important thing this week — one sentence, outcome-focused]
2. [Second priority]
3. [Third priority]

Meeting Prep Needed
- [Meeting name] on [day] — [what to prepare]
- [Meeting name] on [day] — [what to prepare]

Carry-Forward from Last Session
- [Item from session handoff, if any]

Watch-Out
[One sentence flagging a potential trap this week — a tendency to drift, a
blocked item that needs a decision, or a relationship that needs attention]

---
Does this reflect your actual priorities, or should I adjust?
---
```

### Step 5 — Revise if Needed

If the user requests changes, revise and re-present. Once confirmed, ask:

> "Want me to save this to `handoffs/week-plan-[date].md`?"

Write the file only if the user confirms.
