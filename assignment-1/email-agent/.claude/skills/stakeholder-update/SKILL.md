---
name: stakeholder-update
description: >
  Draft a project status update for a stakeholder. Triggered by "draft status update",
  "project update for [person]", "stakeholder update", "write a project update".
  Uses project state and personal writing style to draft a concise status communication.
allowed-tools: Read
---

## Activation

Trigger phrases:

- `draft status update`
- `project update for [person]`
- `stakeholder update`
- `write a project update`
- `update [person] on [project]`

---

## Context Files

- `.claude/context/projects.md` — active projects, blockers, status
- `.claude/context/context.md` — role, org, sender relationships
- `.claude/context/writing-style.md` — tone and voice for written communications

---

## Workflow

### Step 1 — Load Context

Read the three context files. Note the user's role and relationship to the stakeholder.

### Step 2 — Identify the Project and Audience

Ask:

> "Which project and which stakeholder? And how formal should this be —
> email update, Slack message, or a longer written brief?"

Use their answer to calibrate length, format, and tone.

### Step 3 — Pull Project Status

From `projects.md`, identify:
- Current status of the named project
- What has moved since a reasonable last-update point
- Current blockers
- Next milestone or expected completion

If the project isn't in `projects.md`, ask the user to give a quick status summary.

### Step 4 — Draft the Update

Apply the user's writing style from `writing-style.md` to produce a concise update
in the appropriate format.

**For email:**
```
---
DRAFT STATUS UPDATE
---

To: [Stakeholder name/email]
Subject: [Project Name] — Status Update [date]

[Opening — one sentence referencing the project and purpose of the update]

Status: [On track / At risk / Delayed / Complete]

What's happened:
- [Key progress point 1]
- [Key progress point 2]

What's next:
- [Next milestone and expected date]

Blockers (if any):
- [Blocker and what's needed to resolve]

[Closing — clear next step or ask, if any]

[Sign-off],
[Name]
---
```

**For Slack or informal update:**
```
---
DRAFT SLACK UPDATE
---

Quick update on [Project]:

✅ [What's done]
🔄 [What's in progress]
⚠️ [Blocker, if any]
📅 Next milestone: [date and what]

[Tag stakeholder if relevant] — happy to discuss further.
---
```

### Step 5 — Present and Offer Revisions

After presenting the draft:

> "Review this update. Options:
> - 'more detail' — expand any section
> - 'shorter' — trim to essentials
> - 'adjust tone' — more formal or more casual
> - 'add [item]' — include something specific"
