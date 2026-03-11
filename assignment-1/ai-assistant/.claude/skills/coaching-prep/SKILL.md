---
name: coaching-prep
description: >
  Prepare for a 1:1 meeting. Triggered by "prep for 1:1", "1:1 with [person]",
  "coaching prep", "prepare for my 1:1". Surfaces relevant relationship context,
  open items, and talking points for a manager or direct report 1:1.
allowed-tools: Read, Write
---

## Activation

Trigger phrases:

- `prep for 1:1`
- `1:1 with [person]`
- `coaching prep`
- `prepare for my 1:1`
- `I have a 1:1 with [person]`

---

## Context Files

- `.claude/context/meetings.md` — recurring meetings and key relationships
- `.claude/context/goals.md` — long-term goals and priorities
- `.claude/context/projects.md` — active projects, blockers, stakeholder map
- `.claude/context/decision-patterns.md` — coaching notes and blind spots

---

## Workflow

### Step 1 — Load Context

Read all four context files.

### Step 2 — Identify the 1:1

Ask:

> "Who's this 1:1 with, and is it with your manager, a direct report, or a peer?"

Use their answer to look up the person in `meetings.md` and retrieve standing
relationship context.

### Step 3 — Ask About This Specific Meeting

Ask:

> "Is there anything in particular you want to get out of this 1:1, or any issues
> you're going in with?"

Take their answer at face value. Do not ask follow-ups unless something is genuinely ambiguous.

### Step 4 — Build the Prep Sheet

Construct a prep sheet based on the relationship type:

**For a 1:1 with your manager:**
- Surface open blockers from `projects.md` that need escalation or a decision
- Pull any goals from `goals.md` where you need alignment or visibility
- Identify anything you want to proactively share (progress, risks, asks)
- Flag topics to handle carefully based on relationship notes in `meetings.md`

**For a 1:1 with a direct report:**
- Surface what the person cares about (from `meetings.md`)
- Pull any active items they own from `projects.md`
- Identify coaching moments from `decision-patterns.md` that might apply
- Note anything you committed to last time that needs follow-through

**For a peer 1:1:**
- Identify shared projects or dependencies from `projects.md`
- Pull relationship notes from `meetings.md`
- Flag any asks or coordination needed

### Step 5 — Present the Prep Sheet

```
---
1:1 PREP — [Person Name]
[Date] | [Manager / Direct Report / Peer]
---

Context to Recall
- [Key relationship notes from meetings.md]
- [Anything important about this person's current state]

Agenda Topics
1. [Most important thing to cover — one sentence]
2. [Second topic]
3. [Third topic, if applicable]

Things to Listen For
- [What this person tends to care about or need]
- [Any dynamic to pay attention to]

Your Asks / Decisions Needed
- [Blocker or escalation requiring their input]

Carry-Forward from Last Time
- [Anything you committed to or they raised last time, from meetings.md]

Coaching Note
[One sentence from decision-patterns.md that might be relevant to how you show
up in this 1:1. Omit if nothing applies.]

---
Anything to add before the meeting?
---
```

### Step 6 — Save if Requested

If the user wants to save the prep:

> "Want me to save this to `handoffs/1on1-prep-[person]-[date].md`?"

Write the file only if confirmed.
