# Personal Assistant Kit — Overview

An AI-powered system for aligning daily work with long-term goals, built on Claude Code
and Gemini CLI, powered by your own context.

## Primary Goal

The primary goal is to give the AI assistant deep, persistent context about who the user
is and what they are trying to accomplish. Every interaction — drafting an email, preparing
for a meeting, doing a weekly review — draws on a coherent picture of goals, patterns, and
relationships rather than starting from scratch.

## Skills

### Session Management

- **resume**: Reload prior session context and orient to current state. Trigger phrases:
  "resume", "good morning", "start session", "pick up where we left off".
- **handoff**: Write a session handoff without a full reflection dialogue. Trigger phrases:
  "end session", "write handoff", "I'm done for today".

### Reflection & Synthesis

- **reflect**: Daily end-of-day conversational check-in. Surfaces patterns from decision
  history and writes a session handoff note. Trigger phrases: "daily reflection", "end of
  day", "reflect".
- **weekly-report**: Weekly synthesis against goals and patterns; writes a dated weekly
  report file. Trigger phrases: "weekly review", "end of week", "weekly synthesis".
- **week-plan**: Plan the week ahead using goals, projects, and meetings; produces a
  focused weekly priority list. Trigger phrases: "plan my week", "weekly planning".

### Meeting Workflow

- **meeting**: Process a completed meeting — extracts decisions, action items, and
  relationship notes; writes a meeting record file.
- **coaching-prep**: Prepare for a 1:1 with a manager or direct report using relationship
  and project context.
- **follow-up-meeting**: Draft a calendar invite for a follow-up meeting. Never sends
  automatically.

### Communication

- **follow-up-email**: Draft an email reply using personal writing style and email goals.
  Reads inbox via MCP. Never sends automatically.
- **stakeholder-update**: Draft a concise project status update for a stakeholder.

### Thinking & Review

- **review-doc**: Review a document and provide structured feedback using the user's
  thinking style and organizational context.
- **decision**: Frame a hard decision using the user's known decision patterns; surface
  blind spots; give a direct recommendation.

## Context Files

Personal context lives in `.claude/context/`. Each file is filled in during the quickstart
interview and referenced only by the skills that need it.

| File                  | Purpose                                                  |
|-----------------------|----------------------------------------------------------|
| goals.md              | Long-term goals, annual priorities, tension points       |
| projects.md           | Active projects, stakeholders, blockers, priority map    |
| meetings.md           | Recurring meetings, key relationships, standing context  |
| context.md            | Role, org, sender relationships, communication prefs     |
| decision-patterns.md  | Decision process, failure modes, strengths, blind spots  |
| writing-style.md      | Tone, voice, sign-offs, phrases to use/avoid             |
| email-goals.md        | Communication goals, response norms, recurring scenarios |
| response-framework.md | Email structure, length guidelines, scenario patterns    |

## Context Load Matrix

Each skill loads only the context files it needs.

| Skill              | goals | projects | meetings | context | decision-patterns | writing-style | email-goals | response-framework |
|--------------------|:-----:|:--------:|:--------:|:-------:|:-----------------:|:-------------:|:-----------:|:-----------------:|
| resume             |  ✓   |    ✓    |          |         |                   |               |             |                   |
| handoff            |  ✓   |    ✓    |          |         |                   |               |             |                   |
| reflect            |  ✓   |    ✓    |          |         |         ✓        |               |             |                   |
| weekly-report      |  ✓   |    ✓    |          |         |         ✓        |               |             |                   |
| week-plan          |  ✓   |    ✓    |    ✓    |         |                   |               |             |                   |
| meeting            |       |    ✓    |    ✓    |    ✓   |                   |               |             |                   |
| coaching-prep      |  ✓   |    ✓    |    ✓    |         |         ✓        |               |             |                   |
| follow-up-meeting  |       |          |    ✓    |    ✓   |                   |               |             |                   |
| follow-up-email    |       |          |          |    ✓   |                   |       ✓      |      ✓     |         ✓        |
| stakeholder-update |       |    ✓    |          |    ✓   |                   |       ✓      |             |                   |
| review-doc         |       |          |          |    ✓   |         ✓        |               |             |                   |
| decision           |  ✓   |          |          |         |         ✓        |               |             |                   |

## Platforms

| Platform        | Config file | How skills load              |
|-----------------|-------------|------------------------------|
| Claude Code     | CLAUDE.md   | Semantic skill matching       |
| Gemini CLI      | GEMINI.md   | Context file + Stitch extension |
| Cursor / Copilot | AGENTS.md  | Instruction following         |

## Universal Constraints

- **NEVER** send email or calendar invites automatically.
- **NEVER** store email thread content to disk.
- **NEVER** include personal data from emails in memory or session files.
- Always present drafts and wait for explicit user approval before saving.
- Credentials are injected via environment variables — never appear in committed files.

## Handoff Files

Agents that produce persistent output write to `handoffs/`. Files are owned by the user
and are never sent or shared automatically.

| File                            | Written by      |
|---------------------------------|-----------------|
| handoffs/session-handoff.md     | reflect, handoff |
| handoffs/weekly-[date].md       | weekly-report   |
| handoffs/week-plan-[date].md    | week-plan       |
| handoffs/meeting-[date]-[name].md | meeting       |
| handoffs/decision-[topic].md    | decision        |
