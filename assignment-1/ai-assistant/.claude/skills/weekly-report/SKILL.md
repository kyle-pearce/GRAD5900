---
name: weekly-report
description: >
  Weekly synthesis and review. Triggered by "weekly review", "end of week",
  "weekly synthesis", "weekly report". Reads goals, projects, and session history
  to surface patterns and produce a written synthesis.
allowed-tools: Read, Write
---

## Activation

Trigger phrases:

- `weekly review`
- `end of week`
- `weekly synthesis`
- `weekly report`
- `let's do the weekly`

---

## Context Files

- `.claude/context/goals.md` — long-term goals and annual priorities
- `.claude/context/projects.md` — active projects and blockers
- `.claude/context/decision-patterns.md` — known failure modes and coaching notes
- `handoffs/session-handoff.md` — most recent session state

---

## Workflow

### Step 1 — Load Context

Read all four context files listed above.

### Step 2 — Ask for the Week's Raw Input

Ask the user two questions (together, not separately):

> "Before I synthesize the week, give me the raw picture:
> 1. What were the 3-5 most significant things that happened this week?
> 2. On a scale of 1-10, how well did the week reflect your actual priorities?"

Wait for both answers before proceeding.

### Step 3 — Synthesize

Analyze the user's input against their goals and decision patterns. Look for:
- **Goal alignment** — Did their work this week match their stated annual and quarterly priorities?
- **Drift** — What got attention that shouldn't have? What got neglected?
- **Patterns** — Do any of this week's themes match known failure modes from `decision-patterns.md`?
- **Progress** — What moved? What's stuck?
- **Energy signals** — What energized vs. drained them (if mentioned)?

### Step 4 — Write the Weekly Report

Write `handoffs/weekly-[YYYY-MM-DD].md` using today's date:

```markdown
# Weekly Synthesis

**Week of:** [date range]
**Written:** [today's date]

---

## What Happened

[3-5 sentence summary of the week's significant events, in the user's words]

## Goal Alignment

**This week's rating:** [their 1-10 score]

[2-3 sentences on how well the week reflected stated goals. Be specific — name
the goals from goals.md that were served or neglected.]

## What Moved

- [Project or thread that advanced]
- [Project or thread that advanced]

## What's Stuck

- [Thing that didn't move and why, if known]

## Patterns Observed

[If a known failure mode from decision-patterns.md appeared this week, name it
and describe how it showed up. If none, write "No notable patterns this week."]

## Next Week's Focus

[Top 2-3 things to prioritize next week based on goals and open items. Frame
as intentions, not a task list.]

## One Honest Observation

[One direct sentence about something worth paying attention to — a tension,
a pattern, or a blind spot. This is the coaching note for the week.]
```

### Step 5 — Present and Invite Feedback

After writing, share the key findings inline (summary, not the full report):

> "Weekly report written to `handoffs/weekly-[date].md`. Here are the key takeaways:
>
> [3 bullet points from the synthesis]
>
> Anything you'd add or correct before I close this out?"

Incorporate any corrections, then confirm the file is finalized.
