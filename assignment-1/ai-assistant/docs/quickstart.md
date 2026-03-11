# Personal Assistant Kit — Quickstart

This file contains six phased prompts. Paste the **Phase 0 bootstrap** into **Claude Code** (or
Gemini CLI — see the Gemini section at the bottom) to begin. The assistant will guide you through
the remaining phases conversationally. You can pause at any point and resume later — the system
writes progress to `handoffs/` so nothing is lost.

**Before you begin:**
- Confirm MCP servers are connected: `claude mcp list`
- Budget 2–3 hours total; phases can be split across multiple sessions
- Be specific. Vague answers produce vague context. The system's value reflects what you put in.

---

## Phase 0 — Bootstrap

> Paste this first. It sets up the working files and prepares the assistant for the interview.

---

```
I'm setting up the Personal Assistant Kit. Your job for this session is to conduct a deep
interview across five phases and build my personal context files.

First, create the following working files in handoffs/ (create the directory if it doesn't exist):
  - handoffs/interview-log.md     — Running log of all Q&A; append after every exchange
  - handoffs/setup-handoff.md     — Current phase, completion status, threads to return to

Then, as each phase completes, write the output to its context file:
  Phase 1 → Goals              → writes .claude/context/goals.md
  Phase 2 → Decision patterns  → writes .claude/context/decision-patterns.md
  Phase 3 → Projects & org     → writes .claude/context/projects.md and updates .claude/context/context.md
  Phase 4 → Writing & email    → writes .claude/context/writing-style.md and .claude/context/email-goals.md
  Phase 5 → Meetings & people  → writes .claude/context/meetings.md

Persistence rules:
- After each exchange, append a brief summary to handoffs/interview-log.md
- After each phase completes, update handoffs/setup-handoff.md with: phase status, key
  learnings, and any threads I want to return to
- If I say "pause", write a full summary of where we are before stopping
- If I return and say "resume", read handoffs/interview-log.md and handoffs/setup-handoff.md
  to restore context, then confirm what we've covered before asking new questions

Ground rules for the interview:
- Ask one or a few questions at a time — not a wall of questions
- If an answer is thin, ask a follow-up before moving on
- If I'm vague, reflect it back and ask me to be more specific
- At natural breaks, check in: "We can go deeper here or move on — your call"
- Don't summarize after every answer; move forward naturally
- When I say "write it", commit the current phase's output to its context file
- When you write the context files, use my words where possible. Be concrete, not generic.

When you're ready, confirm you understand the plan, create the handoffs/ working files,
and move into Phase 1.
```

---

## Phase 1 — Goals

> The assistant will guide you through this phase automatically after Phase 0. Paste this prompt
> to skip ahead, restart this phase, or re-run it with more detail.

---

```
Phase 1: Goals.

I want you to understand what I'm actually trying to accomplish — not just my job description,
but what I'm optimizing for at a deeper level.

Ask me about:
- What I want to be true in 1–3 years that isn't true today (professionally and personally)
- What "winning" looks like for me this year — specifically, not generically
- What I'm trying to get better at personally right now
- What I would work on if I had 20% more time and no constraints
- How I currently track whether I'm making progress (and whether it's working)
- Where I feel pulled in directions that don't serve my goals

After we've talked through it, ask me:
- What do I want this AI system to remind me of when I drift?
- Are there goals I'm not saying out loud that I should be honest about?

When I say "write it", write to .claude/context/goals.md with these sections:
  - Long-term vision (1–3 years)
  - This year's priorities (professional)
  - Personal development goals
  - Quarterly focus (Q1–Q4 if known)
  - Tension points (where my time doesn't match my goals)
  - What to surface when I drift
  - Honest goals I named

Append a summary of this exchange to handoffs/interview-log.md and update
handoffs/setup-handoff.md to mark Phase 1 complete.
```

---

## Phase 2 — Decision Patterns

> The assistant will guide you through this phase automatically. Paste to restart or re-run.

---

```
Phase 2: Decision patterns.

I want to map how I actually make decisions — not the ideal version, but the real one,
including the parts that get me into trouble.

Ask me about:
- How I typically approach a hard decision (my actual process, not the textbook version)
- What I tend to optimize for, even when I shouldn't (speed? consensus? avoiding conflict?)
- A decision I made recently that I'm proud of — what made it good?
- A decision I've regretted — what pattern was I in?
- Where I tend to procrastinate or avoid deciding
- What my strengths are that others rely on me for
- How I typically handle conflict or disagreement

Then go deeper:
- What's a belief I hold that shapes most of my decisions?
- What do people around me see as my blind spots?
- Do I have recent performance feedback I want to incorporate? If so, what themes came up?
- What kinds of problems energize me vs. drain me?
- Who do I rely on when I'm stuck, and why?

When I say "write it", write to .claude/context/decision-patterns.md with these sections:
  - Default decision process
  - What I over-optimize for
  - Recurring failure modes
  - Strengths others rely on
  - Blind spots (named by me or from feedback)
  - How I handle conflict
  - Energy map (what energizes vs. drains)
  - Coaching implications (what to push me on; how I respond best)
  - Who I trust and why

Append to handoffs/interview-log.md and mark Phase 2 complete in handoffs/setup-handoff.md.
```

---

## Phase 3 — Projects & Org Context

> The assistant will guide you through this phase automatically. Paste to restart or re-run.

---

```
Phase 3: Projects and org context.

Two sub-sections here. Start with active projects, then move to org structure.

**Part A — Current projects:**

Ask me about:
- The 3–5 things I'm actively working on (name them, describe the goal and current status)
- For each: what does "done" look like? What's blocking it?
- Which projects are most important vs. most urgent?
- Where am I the bottleneck on my own work?
- What's been on my list for too long without moving?
- What context would someone need to get up to speed on my work quickly?

**Part B — Org context:**

Ask me about:
- My role and level
- Who I report to; who my skip-levels are
- Whether I have direct reports — if so, who and what they own
- My key partners (engineering, science, design, ops, etc.)
- My key stakeholders (the people who are customers of my work)
- What programs or product areas I own or contribute to
- My planning and review cadence (weekly syncs, quarterly reviews, planning cycles)

When I say "write it":
  - Write to .claude/context/projects.md with sections for:
      Active projects (name, goal, status, blockers, "done" definition)
      Priority vs. urgency map
      Key stakeholders per project
      Stuck items and why
      What would move the needle most right now
  - Update .claude/context/context.md with:
      Role and level
      Reporting structure (up and down)
      Key partners and stakeholders
      Programs and areas owned
      Planning cadence

Append to handoffs/interview-log.md and mark Phase 3 complete in handoffs/setup-handoff.md.
```

---

## Phase 4 — Writing & Email Style

> The assistant will guide you through this phase automatically. Paste to restart or re-run.

---

```
Phase 4: Writing and email style.

This phase populates the context the system uses when drafting communications on my behalf.
It works best with real samples — not descriptions.

**Part A — Writing style:**

Start by asking me how I want to provide writing samples. Present these options:

  Option 1 — Paste samples: I'll paste 2–3 documents, proposals, or long-form pieces
              directly into the conversation.

  Option 2 — Scan a directory: I approve you to read files from a directory I specify
              (e.g. ~/Documents/writing-samples/ or a project folder). Read up to 5
              files, prioritizing ones I flag as favorites or recent work. Confirm
              which files you read before analyzing.

Whichever option I choose, after reviewing the samples ask me:
- What do I think makes my writing effective?
- What writing habits do I want to reinforce or change?
- Are there writers or communicators whose style I admire and try to emulate?

**Part B — Email style:**

Start by asking me how I want to provide email samples. Present these options:

  Option 1 — Paste emails: I'll paste 2–3 emails directly into the conversation.
              I should choose a mix of contexts: an update, a request, a difficult
              conversation. My own writing only — no forwards or templates.

  Option 2 — Read sent mail via MCP: I approve you to fetch my 10 most recent sent
              emails using the Gmail or Outlook MCP tool. Read them, then present a
              one-line summary of each so I can confirm before you analyze. Skip any
              I flag as not representative (e.g. automated replies, calendar responses).

Whichever option I choose, after reviewing the samples ask me:
- How do I think about email differently than documents?
- How does my tone shift by relationship: boss, peer, direct report, external client, vendor?
- Words or phrases I use naturally that feel like "me"
- Words or phrases I actively avoid (because they feel off, passive-aggressive, or generic)
- My preferred sign-offs by context and subject line habits
- What's a bad email habit I know I have?
- What do I want the assistant to push back on when drafting for me?

When I say "write it":
  - Write to .claude/context/writing-style.md with sections for:
      Voice and tone (from sample analysis, in my words)
      Structure preferences
      Habits to reinforce
      Habits to avoid
      Sample references (note what was shared or read, don't reproduce full content)
  - Write to .claude/context/email-goals.md with sections for:
      Default tone and tone by relationship type
      Phrases to use (my natural voice)
      Phrases to avoid
      Email length conventions
      Sign-off preferences
      Subject line style
      Known bad habits to flag
      What to push back on when drafting

Append to handoffs/interview-log.md and mark Phase 4 complete in handoffs/setup-handoff.md.
```

---

## Phase 5 — Meetings & Relationships

> The assistant will guide you through this phase automatically. Paste to restart or re-run.

---

```
Phase 5: Meetings and key relationships.

This phase gives the system what it needs to help me prepare for and follow up on meetings —
without re-explaining context every time.

Ask me about my recurring meetings:
- What are the standing meetings I attend? (name, cadence, purpose, who's in the room)
- Which of these actually move things forward vs. just consume time?
- For each meaningful one: what's the usual dynamic? What do I want to get out of it?
- What context do I almost always wish I had before a meeting but have to scramble for?

Then ask about key relationships:
- Who are the 5–10 people I interact with most?
- For each: their role, our working relationship, what they care about, anything I should
  always remember when dealing with them
- Are there relationships that are complicated, strained, or need careful handling?
- Where do I tend to under-communicate or over-communicate?

When I say "write it", write to .claude/context/meetings.md with sections for:
  - Recurring meetings (name, cadence, purpose, dynamic, what I want from it)
  - Key relationships (person, role, relationship notes, what they care about)
  - Communication patterns to watch
  - Pre-meeting context I typically need

Append to handoffs/interview-log.md and mark Phase 5 complete in handoffs/setup-handoff.md.
```

---

## Wrap-Up

> Paste this after Phase 5 is done to close the interview and finalize the system.

---

```
The interview is complete.

Step 1 — Synthesize:
Read all of handoffs/interview-log.md and all five context files. Identify:
- The most important things you learned about me
- 3–5 open threads or tensions that didn't fully resolve
- Any context files that feel thin and should be revisited

Step 2 — Confirm what was built:
- List all context files written, with a one-line description of what each covers
- Flag any that feel thin or were rushed
- Ask if any should be revised or expanded before we close out

Step 3 — Write the final handoffs/setup-handoff.md with:
  - Date of completion
  - Summary of most important learnings
  - Open threads to return to
  - Recommended starting point for the first working session
  - Files that need revisiting

Step 4 — Tell me: based on everything I shared, what is the one thing I should be most
intentional about in the next 30 days?

Then confirm setup is complete and give me "first week" guidance for getting started.
```

---

## Resuming a Paused Setup

If you stopped mid-interview, start a new session and paste:

```
I'm resuming the Personal Assistant Kit setup. Read handoffs/interview-log.md and
handoffs/setup-handoff.md to restore context. Confirm what phases we've completed
and what was captured, then pick up from the next incomplete phase.
```

---

## Daily Use

Once setup is complete, the system works through ordinary conversation. Suggested patterns:

**End-of-day reflection** — paste this to close out a session:
```
End of day. Read my context files and handoffs/session-handoff.md, then ask me:
1. What did I actually work on today vs. what I planned?
2. Any decisions made — good or bad?
3. Anything worth capturing about meetings or relationships?

After we talk, update handoffs/session-handoff.md with key context for tomorrow.
```

**Pre-meeting prep** — paste this before any meeting:
```
I have [meeting name] in [X] minutes with [people]. Read .claude/context/meetings.md and
.claude/context/projects.md and tell me: what do I need to remember, what should I pay
attention to, and what do I want to come out of this meeting with?
```

**Weekly synthesis** — paste this at end of week:
```
End of week. Read all my context files and handoffs/session-handoff.md.
Give me a synthesis: Did my week reflect my goals? What patterns showed up?
What should I do differently next week?
```

---

## Iteration

Your first version won't be perfect. Plan to revisit and refine:

- **After 1 week:** What workflows are you actually using? Drop what doesn't fit. Edit context
  files to match your real preferences, not the idealized version from setup.
- **After 1 month:** Update `.claude/context/decision-patterns.md` with new self-observations. What
  patterns did the system surface that turned out to be accurate? What was off?
- **After 1 quarter:** Review `.claude/context/goals.md`. Are the right things getting attention?
  Update quarterly focus and adjust tension points.

The system should evolve with you. The initial setup is a starting point, not a contract.

---

## Troubleshooting

**Steering files feel generic after setup:**
- Go back to the relevant phase prompt and re-run it, this time with more specific answers
  or actual writing/email samples to analyze
- The more concrete your inputs, the more useful the outputs

**Context isn't loading in a new session:**
- Paste the resume prompt above — it reads `handoffs/interview-log.md` explicitly
- If that file is missing, check that Phase 0 completed (it creates the working files)

**Workflows feel too rigid:**
- Edit the context files directly to match your actual preferences
- The phase prompts are starting points, not fixed rules — adjust the questions for your context

**Too much overhead:**
- Start with just end-of-day reflection and pre-meeting prep
- Add weekly synthesis after the first two weeks when the pattern feels natural

**MCP tools not responding:**
- Verify connections: `claude mcp list`
- Check that `.env` is present and credentials are valid (see `mcp/README.md`)

---

## Gemini CLI (via Stitch)

The quickstart prompts work with Gemini CLI after installing the Stitch extension:

```bash
# Convert the skill for Gemini CLI
skill-porter convert \
  .claude/skills/draft-emails/SKILL.md \
  --output ./gemini-extensions/draft-emails/

# Register the extension
gemini extension install ./gemini-extensions/draft-emails/

# Source credentials and start a session
source .env
gemini chat
```

Then paste any phase prompt above exactly as written. Gemini CLI reads `GEMINI.md` for
behavioral context, which mirrors `CLAUDE.md`. The interview prompts are platform-agnostic
and work without modification.

See `docs/stitch-setup.md` for full Gemini CLI setup and troubleshooting.
