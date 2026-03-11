---
name: review-doc
description: >
  Review a document and provide structured feedback. Triggered by "review this doc",
  "give me feedback on", "critique this", "review document". Applies the user's
  thinking style and organizational context to produce targeted, useful feedback.
allowed-tools: Read
---

## Activation

Trigger phrases:

- `review this doc`
- `give me feedback on`
- `critique this`
- `review document`
- `review this [proposal / memo / draft / report]`
- `what do you think of this?` (when document content is provided)

---

## Context Files

- `.claude/context/context.md` — role and org context (to understand audience and stakes)
- `.claude/context/decision-patterns.md` — what the user values, how they think, coaching notes

---

## Workflow

### Step 1 — Load Context

Read both context files. Use `decision-patterns.md` to understand what the user
tends to value in documents (e.g., clarity over completeness, directness over hedging)
and what they tend to miss.

### Step 2 — Identify the Document and Review Goal

Ask (if not already clear from the trigger):

> "What am I reviewing, and what kind of feedback is most useful? For example:
> - Is the argument clear and persuasive?
> - Does the structure work?
> - Is the tone right for the audience?
> - Should I look at everything or focus on a specific section?"

If the user pastes the document directly, proceed to Step 3. If they reference a file,
use the Read tool to load it.

### Step 3 — Review the Document

Read the document thoroughly. Evaluate across these dimensions:

**Clarity** — Is it easy to understand? Would the target audience follow it?
**Structure** — Does the organization serve the argument? Are sections in the right order?
**Argument / Logic** — Is the reasoning sound? Are claims supported?
**Tone** — Is it appropriately calibrated for the audience and stakes?
**Concision** — Is anything over-explained, redundant, or filler?
**Gaps** — What's missing that the audience will ask for?

Also apply the user's personal lens from `decision-patterns.md`:
- Do they tend to under-qualify claims? Flag over-hedging.
- Do they tend to bury the lead? Flag if the structure does this.
- Do they have known blind spots? Check for them.

### Step 4 — Present Feedback

Structure feedback as follows:

```
---
DOCUMENT REVIEW
---

Document: [Title or description]
Overall: [One sentence verdict — e.g., "Strong argument, structure needs work"]

---

What's Working
- [Specific strength 1]
- [Specific strength 2]

Issues to Address
1. [Most important issue — be specific, not generic]
   → Suggestion: [Concrete fix or reframe]

2. [Second issue]
   → Suggestion: [Concrete fix]

3. [Third issue, if applicable]
   → Suggestion: [Concrete fix]

Gaps / Missing Pieces
- [Something the audience will ask for that isn't addressed]

Tone Check
[One sentence on whether the tone is right for the audience. Flag if it should
be more direct, more diplomatic, more formal, etc.]

Personal Pattern Note
[If a known pattern from decision-patterns.md appears in this document — e.g.,
burying the lead, over-hedging, avoiding a hard conclusion — name it directly.
Omit if nothing applies.]

---
Want to work through any of these? I can help you revise specific sections.
---
```

### Step 5 — Revision Support

If the user wants to revise a section, work through it together inline.
Do not rewrite the entire document unprompted — offer to revise specific sections on request.
