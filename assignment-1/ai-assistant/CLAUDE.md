# Claude Code — Personal Assistant Kit

This file extends AGENTS.md with Claude Code-specific configuration.

---

## Skills

Skills are defined in `.claude/skills/`. Each skill loads only the context files it needs.
Context files live in `.claude/context/` and are filled in during the quickstart interview.

Available skills and their trigger phrases:

| Skill | Trigger phrases |
|-------|----------------|
| `resume` | "resume", "good morning", "start session", "pick up where we left off" |
| `handoff` | "end session", "write handoff", "I'm done for today" |
| `reflect` | "daily reflection", "end of day", "reflect" |
| `weekly-report` | "weekly review", "end of week", "weekly synthesis" |
| `week-plan` | "plan my week", "weekly planning", "Monday planning" |
| `meeting` | "process meeting", "I just had a meeting", "meeting notes for" |
| `coaching-prep` | "prep for 1:1", "1:1 with [person]", "coaching prep" |
| `follow-up-meeting` | "draft calendar invite", "schedule follow-up", "book a meeting after" |
| `follow-up-email` | "draft email", "help me reply to", "compose a reply", "follow-up email" |
| `stakeholder-update` | "draft status update", "project update for [person]", "stakeholder update" |
| `review-doc` | "review this doc", "give me feedback on", "critique this" |
| `decision` | "help me decide", "thinking through a decision", "I have a hard call to make" |

---

## MCP Configuration

MCP servers are declared in `.claude/settings.json`. Credentials are read from the local
`.env` file (never committed). Run `claude mcp list` to verify connections before drafting.

---

## Subagent Model

Always launch Opus subagents unless specified otherwise.

---

## Inherited Instructions

All trigger phrases, workflow steps, output format, and constraints are defined per-skill
in `.claude/skills/<name>/SKILL.md`. `AGENTS.md` governs universal behavior and constraints.
