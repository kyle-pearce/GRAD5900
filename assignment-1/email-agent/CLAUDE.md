# Claude Code — Email Draft Agent

This file extends AGENTS.md with Claude Code-specific configuration.

---

## Skill Loading

Use the `draft-emails` skill defined in `.claude/skills/draft-emails/SKILL.md`.

Load all steering files from `./steering/` at the start of every draft-email session:
- `./steering/writing-style.md`
- `./steering/context.md`
- `./steering/response-framework.md`
- `./steering/email-goals.md`

---

## MCP Configuration

MCP servers are declared in `.claude/settings.json`. Credentials are read from the local
`.env` file (never committed). Run `claude mcp list` to verify connections before drafting.

---

## Inherited Instructions

All trigger phrases, workflow steps, output format, and constraints are defined in `AGENTS.md`.
This file only adds Claude-specific overrides; `AGENTS.md` governs behavior.
