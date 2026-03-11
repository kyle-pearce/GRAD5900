---
name: decision
description: >
  Structure a hard decision. Triggered by "help me decide", "thinking through a decision",
  "I have a hard call to make", "decision support". Uses the user's known decision patterns
  and failure modes to frame the choice and surface blind spots before they decide.
allowed-tools: Read, Write
---

## Activation

Trigger phrases:

- `help me decide`
- `thinking through a decision`
- `I have a hard call to make`
- `decision support`
- `I'm stuck on a decision`
- `help me think through [choice]`

---

## Context Files

- `.claude/context/decision-patterns.md` — decision process, failure modes, blind spots, coaching notes
- `.claude/context/goals.md` — long-term goals and priorities (to test alignment)

---

## Workflow

### Step 1 — Load Context

Read both context files. Note the user's known failure modes (what they over-optimize for,
where they tend to avoid deciding) and their coaching implications. These will shape how
you frame questions and what you flag.

### Step 2 — Get the Decision on the Table

Ask:

> "Tell me about the decision. What are the options you're choosing between, and
> what's making it hard?"

Listen without structuring yet. Let them describe it in their own terms.

### Step 3 — Probe if Needed

If the options aren't clear or the real tension isn't named, ask one follow-up:

> "What would you regret more — choosing [option A] and it not working, or not
> choosing it and missing the opportunity?"

Or, if the decision has a time dimension:

> "Is there a reason this needs to be decided now, or is there more information
> that would help?"

Do not ask multiple follow-up questions at once.

### Step 4 — Frame the Decision

Lay out the decision clearly before offering analysis:

```
---
DECISION FRAME
---

The choice: [State the decision in one sentence]

Options on the table:
1. [Option A] — [one-line description]
2. [Option B] — [one-line description]
(3. [Option C] if applicable)

What's making it hard: [The core tension in 1-2 sentences]
```

Ask: "Does this capture the decision accurately, or am I missing something?"

Adjust before proceeding.

### Step 5 — Apply Decision Lens

Using `decision-patterns.md`, analyze the decision through the user's known lens:

**Check for failure modes:**
- If the user tends to over-optimize for speed: flag if moving fast here would be premature
- If the user tends to avoid conflict: flag if one option avoids a necessary confrontation
- If the user has a known blind spot (e.g., under-weighting people costs): surface it explicitly

**Check for goal alignment:**
- Compare each option against the priorities in `goals.md`
- Note if one option is clearly more aligned and whether that alignment is being weighted appropriately

**Surface the trade-offs:**
- Reversibility — which option is easier to undo?
- Downside asymmetry — which option's failure mode is worse?
- Second-order effects — what does each option make harder or easier next?

### Step 6 — Present the Analysis

```
---
DECISION ANALYSIS
---

Option A: [Name]
+ [Strength]
- [Weakness / risk]
Goal alignment: [High / Medium / Low]

Option B: [Name]
+ [Strength]
- [Weakness / risk]
Goal alignment: [High / Medium / Low]

Tension
[The real trade-off in one sentence — what you're actually giving up with each option]

Pattern Check
[One direct observation about how a known failure mode might be operating here.
E.g.: "This looks like a situation where you might be over-optimizing for consensus
at the expense of speed. That's a pattern worth watching."]

Reversibility
[Which option is more reversible, and does that matter here?]

If I had to recommend
[A direct recommendation, clearly labeled as such, with the main reason.
If you genuinely can't recommend, say so and explain why — don't hedge.]

---
What's your reaction? Does this help clarify the call, or is there something
I'm not seeing?
---
```

### Step 7 — Save if Useful

After the conversation concludes:

> "Want me to save this decision frame to `handoffs/decision-[topic].md`?
> Useful if you want to revisit your reasoning later."

Write the file only if confirmed.
