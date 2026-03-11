# Personal Assistant Kit

An AI-powered system for aligning daily work with long-term goals — built on Claude Code and
Gemini CLI, powered by your own context. Not a productivity hack. A strategic thinking partner.

**Ready to set up?** Open [`docs/quickstart.md`](docs/quickstart.md) and paste the Phase 0
bootstrap prompt into Claude Code. The assistant will guide you from there.

---

## A Day in the Life

> It's 4:45 PM on a Thursday. You have a 1:1 with your manager tomorrow morning and a
> deliverable that slipped this week.

You open Claude Code and say **"reflect"**. The assistant already knows your goals, your
active projects, and that you tend to under-communicate when things are behind. It asks
what you worked on today, flags that the slipped deliverable hasn't come up in your last
three reflections, and asks if you want to draft an update to your manager before the 1:1.

You say **"draft email"**. It pulls the thread from your Gmail, writes a concise update in
your voice — direct, no hedging, a clear ask — and flags one sentence it flagged as
potentially too casual for your manager relationship. You adjust one word and save the draft.

Then: **"prep for 1:1"**. The assistant surfaces the last three things your manager raised,
the two projects where you're the blocker, and a coaching note you wrote about yourself six
weeks ago — that you tend to avoid surfacing bad news until it's urgent. It suggests you
lead with the slip, not bury it.

You walk into Friday's 1:1 prepared. Your manager already has your update. You lead with
the hard thing. The meeting is useful instead of awkward.

That's the system working. None of it required you to remember context, re-explain your
situation, or think about which tool to use. You just talked to it.

---

## What This Is

Most productivity systems optimize small things. This one targets the decisions that matter:
are you spending time on the right problems, developing as a person, and building institutional
memory that compounds over time?

The Personal Assistant Kit gives your AI assistant deep, persistent context about who you are
and what you're trying to accomplish. The result: every interaction — drafting an email,
preparing for a meeting, doing a weekly review — draws on a coherent picture of your goals,
patterns, and relationships rather than starting from scratch.

---

## What It Does

| Pillar | What the system does |
|--------|---------------------|
| **Monitor time allocation** | Surfaces whether your work reflects your priorities, or whether you're drifting toward low-value tasks |
| **Develop personally** | Regularly surfaces blind spots, recurring patterns, and growth opportunities you'd otherwise miss |
| **Elevate meeting quality** | Loads prior context automatically so you never walk into a meeting cold or waste time reviewing old notes |
| **See patterns across time** | Daily → weekly → monthly synthesis reveals what's invisible day to day |

---

## Time Investment

**Setup: 2–3 hours.** The system's value directly reflects how much context you provide. The
initial setup is an interview process — your AI assistant will ask about your goals, decision
patterns, current projects, writing style, and key relationships. Take your time with it.

**Daily use: 10–15 minutes.** A short reflection after work. A few minutes to process each
meeting. The compound effect builds over weeks.

---

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/claude-code) **or** [Gemini CLI](https://github.com/google-gemini/gemini-cli) installed
- MCP servers configured (see `mcp/README.md` for Gmail and Outlook setup)
- For Gemini CLI: `skill-porter` installed (`pip install skill-porter`) — see `docs/stitch-setup.md`

---

## Quick Start

Open `docs/quickstart.md` and paste the **Phase 0 bootstrap prompt** into Claude Code (or Gemini
CLI). The assistant will guide you through the remaining phases conversationally. The interview
takes 2–3 hours and can be paused and resumed at any point — progress is saved to `handoffs/`.

```bash
# Open the quickstart guide
cat docs/quickstart.md
```

For Gemini CLI, see the Stitch setup section at the bottom of `docs/quickstart.md`.

---

## Architecture

```
personal-assistant-kit/
├── AGENTS.md                      ← Universal agent instructions (all platforms)
├── CLAUDE.md                      ← Claude Code-specific overrides and skill index
├── GEMINI.md                      ← Gemini CLI-specific overrides
│
├── .claude/
│   ├── settings.json              ← MCP server declarations
│   │
│   ├── context/                   ← Your personal context (fill in during setup)
│   │   ├── goals.md               ← Long-term goals and current priorities
│   │   ├── decision-patterns.md   ← How you make decisions; recurring failure modes
│   │   ├── projects.md            ← Active projects, stakeholders, blockers
│   │   ├── meetings.md            ← Recurring meetings, key relationships, standing context
│   │   ├── context.md             ← Role, organization, background, communication prefs
│   │   ├── writing-style.md       ← Tone, voice, sign-offs, phrases to use/avoid
│   │   ├── response-framework.md  ← Email response structure and conventions
│   │   └── email-goals.md         ← Communication goals and recurring scenarios
│   │
│   └── skills/                    ← One skill per agent; each loads only what it needs
│       ├── resume/                ← Reload prior session context
│       ├── handoff/               ← Write session handoff (quick)
│       ├── reflect/               ← Daily reflection + handoff (conversational)
│       ├── weekly-report/         ← Weekly synthesis against goals
│       ├── week-plan/             ← Plan the week ahead
│       ├── meeting/               ← Process a completed meeting
│       ├── coaching-prep/         ← Prepare for a 1:1
│       ├── follow-up-meeting/     ← Draft a calendar invite
│       ├── follow-up-email/       ← Draft an email reply
│       ├── stakeholder-update/    ← Draft a project status update
│       ├── review-doc/            ← Review a document
│       └── decision/              ← Structure a hard decision
│
├── handoffs/                      ← Session continuity notes (AI-written, you own)
│   ├── session-handoff.md         ← Current session state; updated by reflect and handoff
│   ├── weekly-[date].md           ← Weekly synthesis; written by weekly-report
│   ├── week-plan-[date].md        ← Weekly plan; written by week-plan
│   ├── meeting-[date]-[name].md   ← Meeting records; written by meeting
│   └── decision-[topic].md        ← Decision frames; written by decision (optional)
│
├── mcp/
│   └── README.md                  ← MCP server setup guide (Gmail + Outlook)
│
└── docs/
    ├── quickstart.md              ← Phased setup prompts — start here
    └── stitch-setup.md            ← Gemini CLI / Stitch interoperability guide
```

---

## Agent Catalog

Each agent is a Claude Code skill invoked by natural language. They load only the context
files they need — `writing-style.md`, for example, loads only in `follow-up-email` and
`stakeholder-update`.

### Session Management

| Agent | Trigger phrases | What it does |
|-------|----------------|--------------|
| `resume` | "resume", "good morning", "start session" | Loads prior handoff and orients you to current state |
| `handoff` | "end session", "write handoff", "I'm done for today" | Writes session handoff with a single summary question |

### Reflection & Synthesis

| Agent | Trigger phrases | What it does |
|-------|----------------|--------------|
| `reflect` | "daily reflection", "end of day", "reflect" | Conversational EOD check-in; writes session handoff; surfaces patterns from your decision history |
| `weekly-report` | "weekly review", "end of week", "weekly synthesis" | Synthesizes the week against goals; writes dated weekly report |
| `week-plan` | "plan my week", "weekly planning", "Monday planning" | Reviews goals, projects, and meetings; produces a focused weekly priority list |

### Meeting Workflow

| Agent | Trigger phrases | What it does |
|-------|----------------|--------------|
| `meeting` | "process meeting", "I just had a meeting", "meeting notes for" | Captures decisions, action items, and relationship notes; writes meeting record |
| `coaching-prep` | "prep for 1:1", "1:1 with [person]", "coaching prep" | Builds a prep sheet for a 1:1 using relationship and project context |
| `follow-up-meeting` | "draft calendar invite", "schedule follow-up" | Drafts a calendar invite with agenda; never sends automatically |

### Communication

| Agent | Trigger phrases | What it does |
|-------|----------------|--------------|
| `follow-up-email` | "draft email", "help me reply to", "compose a reply" | Reads inbox via MCP, applies writing style, presents draft for review; never sends automatically |
| `stakeholder-update` | "draft status update", "project update for [person]" | Drafts a concise project status update in the appropriate format (email, Slack, brief) |

### Thinking & Review

| Agent | Trigger phrases | What it does |
|-------|----------------|--------------|
| `review-doc` | "review this doc", "give me feedback on", "critique this" | Structured document feedback using your thinking style and org context |
| `decision` | "help me decide", "thinking through a decision" | Frames the choice, applies your decision patterns, surfaces blind spots, gives a direct recommendation |

---

## Context Load Matrix

Each skill loads only the context files it needs. `writing-style.md` loads in two skills only.

| Agent | goals | projects | meetings | context | decision-patterns | writing-style | email-goals | response-framework |
|-------|:-----:|:--------:|:--------:|:-------:|:-----------------:|:-------------:|:-----------:|:-----------------:|
| resume | ✓ | ✓ | | | | | | |
| handoff | ✓ | ✓ | | | | | | |
| reflect | ✓ | ✓ | | | ✓ | | | |
| weekly-report | ✓ | ✓ | | | ✓ | | | |
| week-plan | ✓ | ✓ | ✓ | | | | | |
| meeting | | ✓ | ✓ | ✓ | | | | |
| coaching-prep | ✓ | ✓ | ✓ | | ✓ | | | |
| follow-up-meeting | | | ✓ | ✓ | | | | |
| follow-up-email | | | | ✓ | | ✓ | ✓ | ✓ |
| stakeholder-update | | ✓ | | ✓ | | ✓ | | |
| review-doc | | | | ✓ | ✓ | | | |
| decision | ✓ | | | | ✓ | | | |

---

## Cross-Platform Support

| Platform | Config file | How skills load |
|----------|-------------|-----------------|
| Claude Code | `CLAUDE.md` + `.claude/skills/` | Semantic skill matching |
| Gemini CLI | `GEMINI.md` | Context file + Stitch extension |
| Cursor / Copilot | `AGENTS.md` | Instruction following |

See `docs/stitch-setup.md` for Gemini CLI installation and skill-porter conversion.

---

## Privacy

**Never commit filled-in context files to a public repository.**

The `.gitignore` excludes `.env` and `credentials/`. Context files ship with `[PLACEHOLDER]`
sections that are safe to commit. Once filled in with personal data, treat them as private —
add to `.gitignore` or use a private fork.

The `handoffs/` directory contains personal reflection notes. Add it to `.gitignore` or keep
the repository private.

No email content is ever stored or logged by any agent in this kit.

---

## Verification Checklist

- [ ] `claude mcp list` shows `gmail` and/or `outlook` as connected
- [ ] `docs/quickstart.md` Phase 0 completes without errors
- [ ] All context files exist and are filled in after setup (`.claude/context/`)
- [ ] `handoffs/session-handoff.md` was written at the end of the interview
- [ ] Trigger phrase "reflect" activates the daily reflection skill
- [ ] Trigger phrase "draft email" activates the follow-up-email skill
- [ ] `git diff --cached` shows no credentials before any commit
- [ ] Gemini CLI extension activates (if using Stitch)
