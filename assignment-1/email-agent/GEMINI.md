# Gemini CLI — Email Draft Agent

This file extends AGENTS.md with Gemini CLI-specific configuration.
It mirrors the structure of CLAUDE.md for cross-ecosystem compatibility via Stitch.

---

## Context Loading

At the start of every draft-email session, load all steering files from `./steering/`:
- `./steering/writing-style.md`
- `./steering/context.md`
- `./steering/response-framework.md`
- `./steering/email-goals.md`

---

## Extension Setup

This agent is packaged as a Gemini CLI Extension via the Stitch interoperability layer.
See `docs/stitch-setup.md` for installation instructions using the skill-porter converter.

---

## Trigger Phrases

Same as AGENTS.md:
- `draft email`, `draft emails`
- `help me reply to [email]`
- `write a response to [email]`
- `email response`, `compose a reply`, `draft a reply`

---

## MCP Tools

Gemini CLI accesses Gmail and Outlook through the same MCP servers declared for Claude Code.
Credentials must be set in the local `.env` file before activating the extension.

See `mcp/README.md` for MCP server setup.
See `docs/stitch-setup.md` for Gemini CLI extension installation.

---

## Inherited Instructions

All workflow steps, output format, and constraints are defined in `AGENTS.md`.
This file only adds Gemini CLI-specific overrides.
