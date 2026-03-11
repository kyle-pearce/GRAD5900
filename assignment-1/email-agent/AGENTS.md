# Personal Assistant Kit

Universal agent instructions — readable by Claude Code, Gemini CLI, Cursor, Copilot, and any
agent runtime that follows the Agent Skills open standard.

---

## Purpose

An AI-powered personal assistant that aligns daily work with long-term goals. It handles
reflection, meeting processing, communication drafting, and strategic thinking — drawing on
persistent context about who you are and what you're trying to accomplish.

---

## Context Files

Personal context lives in `.claude/context/`. These files are filled in during the quickstart
interview and referenced by individual skills. Each skill loads only what it needs.

| File | Purpose |
|------|---------|
| `goals.md` | Long-term goals, annual priorities, tension points |
| `projects.md` | Active projects, stakeholders, blockers, priority map |
| `meetings.md` | Recurring meetings, key relationships, standing context |
| `context.md` | Role, org, sender relationships, timezone, communication preferences |
| `decision-patterns.md` | Decision process, failure modes, strengths, blind spots |
| `writing-style.md` | Tone, voice, sign-offs, phrases to use/avoid |
| `email-goals.md` | Communication goals, response norms, recurring scenarios |
| `response-framework.md` | Email structure, length guidelines, scenario-specific patterns |

> **Note:** Fill in the `[PLACEHOLDER]` sections in each file. Do NOT commit filled-in
> context files to a public repository — they contain personal information.

---

## Skills

### Session Management
- `resume` — Load prior session context and orient to current state
- `handoff` — Write a session handoff without a full reflection dialogue

### Reflection & Synthesis
- `reflect` — Daily end-of-day reflection; writes session handoff
- `weekly-report` — Weekly synthesis against goals and patterns
- `week-plan` — Plan the week ahead using goals, projects, and meetings

### Meeting Workflow
- `meeting` — Process a completed meeting: decisions, actions, relationship notes
- `coaching-prep` — Prepare for a 1:1 (with manager or direct report)
- `follow-up-meeting` — Draft a calendar invite for a follow-up meeting

### Communication
- `follow-up-email` — Draft an email reply using personal writing style and email goals
- `stakeholder-update` — Draft a project status update for a stakeholder

### Thinking & Review
- `review-doc` — Review a document; provide structured feedback
- `decision` — Structure a hard decision using the user's known decision patterns

---

## Handoff Files

Agents that produce persistent output write to `handoffs/`. These files are owned by the
user and are never sent or shared automatically.

| File | Written by |
|------|-----------|
| `handoffs/session-handoff.md` | `reflect`, `handoff` |
| `handoffs/weekly-[date].md` | `weekly-report` |
| `handoffs/week-plan-[date].md` | `week-plan` |
| `handoffs/meeting-[date]-[name].md` | `meeting` |
| `handoffs/decision-[topic].md` | `decision` (optional) |

---

## Universal Constraints

- **NEVER** send email or calendar invites automatically
- **NEVER** store email thread content to disk
- **NEVER** include personal data from emails in memory or session files
- Always present drafts and wait for explicit user approval before saving
- If uncertain about tone or content, surface the ambiguity and offer alternatives
- Credentials are injected via environment variables — never appear in committed files

---

## Security

- Credentials are injected via environment variables at runtime
- No API keys, tokens, or OAuth credentials appear in any committed file
- See `.env.example` for required environment variable names
- See `mcp/README.md` for MCP server setup instructions
