# Stitch / Gemini CLI Interoperability Guide

How to use the email-draft agent with Gemini CLI via the Stitch interoperability layer and
the Agent Skills open standard.

---

## Overview

This agent is built on the **Agent Skills open standard** — a common format for defining
AI agent capabilities that works across Claude Code, Gemini CLI, Cursor, and other runtimes.

**Stitch** is the interoperability protocol that allows skills written for one platform to run
on another. The `skill-porter` tool converts Claude Code skills into Gemini CLI Extensions.

---

## Architecture

```
AGENTS.md                          ← Single source of truth (all platforms)
├── CLAUDE.md                      ← Claude Code thin wrapper
├── GEMINI.md                      ← Gemini CLI thin wrapper
└── .claude/skills/draft-emails/   ← Claude skill definition
    └── SKILL.md                   → skill-porter → Gemini CLI Extension
```

---

## Prerequisites

- Gemini CLI installed: `pip install gemini-cli` or follow [Gemini CLI docs](https://github.com/google-gemini/gemini-cli)
- `skill-porter` installed: `pip install skill-porter`
- Node.js 18+ (for MCP servers)
- `.env` configured with Gmail and/or Outlook credentials (see `mcp/README.md`)

---

## Installation Steps

### Step 1 — Convert the Skill

From the `email-agent/` directory, run:

```bash
skill-porter convert \
  .claude/skills/draft-emails/SKILL.md \
  --output ./gemini-extensions/draft-emails/
```

This generates a Gemini CLI Extension manifest from the SKILL.md definition.

### Step 2 — Register the Extension

```bash
gemini extension install ./gemini-extensions/draft-emails/
```

Verify it appears in your extension list:

```bash
gemini extension list
```

### Step 3 — Configure MCP in Gemini Context

Add the MCP server configuration to your Gemini CLI settings. Gemini CLI reads context
from `GEMINI.md` in the project directory.

The MCP environment variables must be available in your shell:

```bash
source .env
gemini chat
```

### Step 4 — Test the Trigger

In a Gemini CLI session (from the `email-agent/` directory):

```
draft email
```

The extension should activate and begin the draft-email workflow.

---

## How GEMINI.md Works

`GEMINI.md` is loaded by Gemini CLI as a project context file (equivalent to Claude's
`CLAUDE.md`). It:

1. Points Gemini to the `./steering/` files for writing style context
2. Declares the same trigger phrases as the Claude skill
3. References `AGENTS.md` for the full workflow and constraints

Gemini CLI does not have a native "skill" concept — the extension (from skill-porter) handles
trigger matching, and GEMINI.md provides the behavioral context.

---

## Keeping Skills in Sync

When you update `SKILL.md` or `AGENTS.md`, re-run the skill-porter conversion:

```bash
skill-porter convert \
  .claude/skills/draft-emails/SKILL.md \
  --output ./gemini-extensions/draft-emails/ \
  --overwrite

gemini extension install ./gemini-extensions/draft-emails/ --force
```

---

## Differences Between Platforms

| Feature | Claude Code | Gemini CLI |
|---------|-------------|------------|
| Skill loading | SKILL.md + `.claude/` | skill-porter extension |
| Context file | CLAUDE.md | GEMINI.md |
| Trigger matching | Semantic (built-in) | Extension manifest |
| MCP support | Native | Via extension bridge |
| Steering files | Auto-loaded by skill | Loaded via GEMINI.md context |

---

## Troubleshooting

### Extension not activating

- Check `gemini extension list` — confirm it's installed
- Ensure you're running from the `email-agent/` directory (GEMINI.md must be present)
- Try an explicit trigger: `@draft-emails draft email` if direct activation fails

### MCP tools not available

- Confirm `.env` is sourced: `source .env && gemini chat`
- Verify MCP servers connect in Claude Code first: `claude mcp list`
- MCP bridge in Gemini CLI may require extension configuration — check skill-porter docs

### skill-porter not found

```bash
pip install skill-porter
# or
pipx install skill-porter
```

---

## Resources

- [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [skill-porter tool](https://github.com/jduncan-rva/skill-porter)
- [Agent Skills open standard](https://agentskills.dev) — shared format for AGENTS.md
- [Stitch protocol docs](https://stitch.agentskills.dev) — cross-platform interoperability
