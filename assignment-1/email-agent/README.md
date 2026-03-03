# Email Draft Agent

An AI agent skill that auto-drafts email replies using Gmail and Outlook inboxes, powered by
personal writing-style steering files. Works with Claude Code and Gemini CLI via the Agent
Skills open standard and Stitch interoperability.

**This agent never sends email. It only drafts.**

---

## Quick Start

### 1. Clone and enter the directory

```bash
cd assignment-1/email-agent
```

### 2. Set up credentials

```bash
cp .env.example .env
# Edit .env and fill in your OAuth2 credentials
```

See `mcp/README.md` for step-by-step OAuth setup for Gmail and Outlook.

### 3. Verify MCP connections

```bash
claude mcp list
```

Both `gmail` and `outlook` servers should appear as connected.

### 4. Trigger the agent

In Claude Code, type any of:

- `draft email`
- `draft emails`
- `help me reply to [paste email or describe it]`
- `write a response to [email]`

---

## Architecture

```
email-agent/
├── AGENTS.md              ← Universal agent instructions (all platforms)
├── CLAUDE.md              ← Claude Code-specific overrides
├── GEMINI.md              ← Gemini CLI-specific overrides
│
├── .claude/
│   ├── settings.json      ← MCP server declarations (credentials injected at runtime)
│   └── skills/
│       └── draft-emails/
│           └── SKILL.md   ← Skill trigger, workflow, tool permissions
│
├── steering/              ← Personal writing-style context (fill in placeholders)
│   ├── writing-style.md
│   ├── context.md
│   ├── response-framework.md
│   └── email-goals.md
│
├── mcp/
│   └── README.md          ← MCP server setup guide
│
└── docs/
    └── stitch-setup.md    ← Gemini CLI / Stitch interoperability guide
```

### How It Works

1. User types a trigger phrase (e.g., "draft email")
2. Agent asks which email to reply to (or infers from context)
3. Agent fetches the email thread via Gmail or Outlook MCP
4. Agent loads all `steering/` files for writing style and context
5. Agent drafts a reply and presents it with a revision prompt
6. User reviews, requests revisions, or copies the draft manually

---

## Steering Files

The `steering/` directory contains template files with `[PLACEHOLDER]` sections. Fill these in
with your personal information to customize the agent's writing style.

| File | What to fill in |
|------|----------------|
| `writing-style.md` | Your preferred tone, sign-offs, phrases to use/avoid |
| `context.md` | Your role, organization, common sender relationships |
| `response-framework.md` | Fixed how-to guide — no personal data needed |
| `email-goals.md` | Your communication goals and recurring email scenarios |

---

## Cross-Platform Support

| Platform | Config file | Trigger method |
|----------|-------------|----------------|
| Claude Code | `CLAUDE.md` + `.claude/skills/` | Semantic skill matching |
| Gemini CLI | `GEMINI.md` | Context file + Stitch extension |
| Cursor / Copilot | `AGENTS.md` | Instruction following |

See `docs/stitch-setup.md` for Gemini CLI installation.

---

## Privacy

**Never commit filled-in steering files to a public repository.**

The `.gitignore` excludes `.env` and `credentials/`. Steering files contain `[PLACEHOLDER]`
sections — these are safe to commit. Once you fill them in with personal data, treat them as
private (add to `.gitignore` or use a private fork).

No email content is ever stored or logged by this agent.

---

## Verification Checklist

- [ ] `claude mcp list` shows `gmail` and `outlook` as connected
- [ ] Trigger phrase "draft email" activates the skill
- [ ] Agent lists recent emails via MCP (no auto-send)
- [ ] Draft output matches the labeled format in `AGENTS.md`
- [ ] `git diff --cached` shows no credentials before any commit
- [ ] Gemini CLI extension activates (if using Stitch)
