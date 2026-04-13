# Assignment 3: Agentic Personal Assistant

**Course:** Applied Generative AI (GRAD 5900)
**Author:** Kyle Pearce
**Date:** April 2026

## Overview

This project implements **Phase 3 of 4** of the Personal Assistant Kit. It transforms a collection of isolated skills (Assignment 1) and a standalone knowledge base (Assignment 2) into a unified, proactive agentic system.

While this phase provides the sophisticated orchestration and integration logic, the ultimate goal is to make this assistant accessible to everyone—not just technical users. **Phase 4** will focus on creating a user-friendly UI and desktop application to simplify installation and daily use for non-technical individuals.

By integrating **Model Context Protocol (MCP)** servers with **Claude Code orchestration**, the assistant can now:
1. **Search and Update Memory:** Natively query and ingest data into your RAG pipeline.
2. **Interact with the World:** Check availability and schedule meetings via Google Calendar.
3. **Run Compound Workflows:** Execute multi-step processes like "Monday Morning Kickoff" or "Meeting Lifecycle" with conflict detection.
4. **Safety First:** Utilize a 4-tier approval system to ensure you are always in control of external writes and high-stakes decisions.

---

## Prerequisites

- **Directory Structure:** Ensure all assignments are in the same parent directory:
  ```
  grad5900/
  ├── assignment-1/ai-assistant/
  ├── assignment-2/rag-assistant/
  └── assignment-3/
  ```
- **Python:** 3.12+
- **Claude Code:** Installed and authenticated.
- **Google Cloud Project:** With Gmail (from A1) and Calendar (new) APIs enabled.

---

## Installation & Setup

### 1. Knowledge Base MCP Server
Connects Claude Code to your Assignment 2 RAG pipeline.

```bash
cd assignment-3/mcp-servers/knowledge-server
pip install -r requirements.txt
# Ensure assignment-2/rag-assistant/.env has your API keys
```

### 2. Google Calendar MCP Server
Provides real-time schedule awareness.

1. **Enable API:** Go to Google Cloud Console and enable the **Google Calendar API**.
2. **Auth:** Run the auth helper (see `LOW_LEVEL_DESIGN.md` Section 3) to get a `GOOGLE_CALENDAR_REFRESH_TOKEN` with the `calendar` scope.
3. **Environment:** Create `.env` in `mcp-servers/calendar-server/` with your Client ID, Secret, and the new Refresh Token.
4. **Install:**
   ```bash
   cd assignment-3/mcp-servers/calendar-server
   pip install -r requirements.txt
   ```

### 3. Claude Code Integration
Register the servers in your Claude Code settings.

1. Copy the configuration from `assignment-3/claude-settings.json`.
2. Apply it to `assignment-1/ai-assistant/.claude/settings.json`.

### 4. Orchestrator Deployment
Install the "brain" of the system.

```bash
# Create the skill directory
mkdir -p ../assignment-1/ai-assistant/.claude/skills/orchestrate

# Copy the orchestrator skill
cp orchestrator/SKILL.md ../assignment-1/ai-assistant/.claude/skills/orchestrate/SKILL.md
```

---

## Usage: Compound Workflows

The orchestrator automatically detects when to run a workflow based on your intent. Use these trigger phrases in Claude Code:

| Workflow | Trigger Phrases | Key Actions |
|----------|-----------------|-------------|
| **Monday Kickoff** | "plan my week", "good morning" | Resume context + Calendar check + Week Plan + 1:1 Prep sheets |
| **End of Day** | "end of day", "EOD" | Reflection + Auto-ingest + Pattern discovery |
| **Meeting Prep** | "prep for my 1:1 with [Name]" | Calendar lookup + Past notes search + Stale action item check |
| **Meeting Lifecycle** | "process meeting with [Name]" | Capture notes + Auto-ingest + Conflict check + Schedule follow-up |
| **Week Close** | "end of week", "weekly review" | Reflection + Weekly Report + Stakeholder update drafts |

---

## The Human-in-the-Loop (HITL) Process

The system follows the **Tiered Approval Layer** defined in `approval/tiers.md`:

- **Tier 0/1 (Read/Local Write):** Claude proceeds automatically and logs the action.
- **Tier 2 (External Write):** Claude will **PAUSE** and show you a draft (e.g., a calendar invite). You must say "yes", "no", or "edit".
- **Tier 3 (Conflict):** If Claude detects a contradiction (e.g., you are double-booked or a tone mismatch), it will **ESCALATE** and ask you for a decision.

Check `handoffs/action-log.md` in your Assignment 1 directory to see the persistent audit trail of all automated actions.
