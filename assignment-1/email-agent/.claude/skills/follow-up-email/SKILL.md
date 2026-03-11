---
name: follow-up-email
description: >
  Draft a reply to an email. Triggered by "draft email", "follow-up email",
  "help me reply to [email]", "write a response to", "email response",
  "compose a reply", "draft a reply".
  Reads Gmail and Outlook inboxes via MCP, applies personal writing style,
  and presents a draft for user review. Never sends automatically.
allowed-tools: mcp__gmail__*, mcp__outlook__*, Read
context: fork
---

## Activation

This skill activates on any of the following trigger phrases:

- `draft email`
- `follow-up email`
- `help me reply to [email description or paste]`
- `write a response to [email]`
- `email response`
- `compose a reply`
- `draft a reply`

The match is semantic — variations in phrasing or additional context words are fine.

Examples that activate this skill:
> "Can you draft email replies for my inbox?"
> "Help me reply to the email from my advisor"
> "Draft a response to the meeting request I just got"
> "Write a response to this: [pasted email]"

---

## Context Files

This skill reads the following files before drafting:

- `.claude/context/writing-style.md` — tone, voice, sign-offs, phrases to use/avoid
- `.claude/context/context.md` — role, org, sender relationships
- `.claude/context/response-framework.md` — structure, length, opening/closing conventions
- `.claude/context/email-goals.md` — communication goals, recurring scenarios, response expectations

If any file has unfilled `[PLACEHOLDER]` sections, note this and use reasonable defaults.

---

## Workflow

### Step 1 — Identify Target Email

Ask the user which email to reply to, or infer from pasted content.

If no email is specified:
- Ask: "Which email would you like to reply to? You can describe it (sender, subject, topic)
  or paste the content directly."
- If the user says "my most recent" or "the latest", use `list_messages` to fetch the inbox
  and identify the most recent unread thread.

### Step 2 — Fetch Email Thread

Use the appropriate MCP server based on the user's email provider.

**Gmail:**
```
mcp__gmail__search_messages(query="from:[sender] subject:[subject]")
mcp__gmail__get_message(id=[message_id])
```

**Outlook:**
```
mcp__outlook__list_messages(filter="[relevant filter]")
mcp__outlook__get_message(id=[message_id])
```

Read the full thread, not just the most recent message, to preserve context.

### Step 3 — Load Context

Read the four context files listed above before drafting.

### Step 4 — Draft Reply

Compose the reply using:
- The email content from Step 2
- The writing style from `writing-style.md`
- The structural framework from `response-framework.md`
- The relationship context from `context.md`
- The communication goals from `email-goals.md`

If the email is ambiguous about what response is needed, include one clarifying question
in the draft body rather than guessing.

### Step 5 — Present for Review

Output the draft in the labeled format below and offer a revision loop.

**NEVER** call `send_message` or any send tool. Save as draft only if the user explicitly
requests it (using `create_draft`).

---

## Output Format

```
---
DRAFT EMAIL REPLY
---

To: [recipient email]
Subject: Re: [original subject]

[Opening line referencing their email]

[Body — 1-3 paragraphs following response-framework.md structure]

[Closing with clear next step or call-to-action]

[Sign-off],
[Name]

---
Review this draft and let me know if you'd like changes:
- "revise tone" — adjust formality
- "make shorter" — condense
- "make longer" — expand with detail
- "add [point]" — insert a specific item
- "change sign-off" — try a different closing
- "save draft" — save to Gmail/Outlook without sending
---
```

---

## Constraints

- **NEVER** call any send tool (`send_message`, `send_email`, `SendMail`, etc.)
- **NEVER** log, store, or write email content to any file
- **NEVER** include email thread content in memory or session notes
- Always present the draft and wait for the user to review
- If uncertain about tone or content, flag it and offer alternatives in the revision prompt
- Respect the privacy of all parties mentioned in the email thread
