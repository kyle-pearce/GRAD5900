# MCP Server Setup

Step-by-step guide to configuring Gmail and Outlook MCP servers for the email-draft agent.

---

## Prerequisites

- Node.js 18+ installed (`node --version`)
- A Google account (for Gmail) and/or a Microsoft account (for Outlook)
- Claude Code CLI installed and running

---

## Gmail MCP Setup

### Package
`@shinzolabs/gmail-mcp` — well-maintained, OAuth2-based, draft-first safe.

### Step 1 — Create a Google Cloud OAuth2 App

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable the **Gmail API**:
   - APIs & Services → Library → search "Gmail API" → Enable
4. Create OAuth2 credentials:
   - APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Application type: **Desktop app**
   - Download the credentials JSON

### Step 2 — Get a Refresh Token

```bash
npx @shinzolabs/gmail-mcp auth
```

Follow the browser prompts to authorize your Google account. The tool will output:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`

### Step 3 — Add to .env

```bash
GOOGLE_CLIENT_ID=<paste value here>
GOOGLE_CLIENT_SECRET=<paste value here>
GOOGLE_REFRESH_TOKEN=<paste value here>
```

### Step 4 — Verify

```bash
claude mcp list
```

`gmail` should appear as connected. If not, check that `.env` is loaded in your shell:

```bash
source .env
claude mcp list
```

---

## Outlook MCP Setup

### Package
`ms-365-mcp-server` — Microsoft 365 MCP server with OAuth2 support.

Alternative: Microsoft's official MCP preview (check Microsoft's GitHub for latest).

### Step 1 — Register an Azure App

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** → **App registrations** → **New registration**
3. Name: `email-draft-agent` (or any name)
4. Supported account types: **Accounts in any organizational directory and personal accounts**
5. Redirect URI: `http://localhost` (Desktop/mobile app)
6. Click **Register**

### Step 2 — Configure API Permissions

In your app registration:
1. **API permissions** → **Add a permission** → **Microsoft Graph**
2. Add **Delegated permissions**:
   - `Mail.Read`
   - `Mail.ReadWrite` (needed for draft creation)
   - `Mail.Send` — **do NOT add this** (agent should never send)
3. Click **Grant admin consent** (if available)

### Step 3 — Get Client Secret

1. **Certificates & secrets** → **New client secret**
2. Copy the secret value immediately (shown only once)

### Step 4 — Get a Refresh Token

```bash
npx ms-365-mcp-server auth \
  --client-id <MS_CLIENT_ID> \
  --client-secret <MS_CLIENT_SECRET>
```

Follow browser prompts. Copy the refresh token from output.

### Step 5 — Add to .env

```bash
MS_CLIENT_ID=<paste value here>
MS_CLIENT_SECRET=<paste value here>
MS_REFRESH_TOKEN=<paste value here>
```

### Step 6 — Verify

```bash
claude mcp list
```

`outlook` should appear as connected.

---

## Troubleshooting

### "MCP server failed to start"

- Check Node.js version: `node --version` (need 18+)
- Ensure `.env` is sourced: `source .env`
- Try running the MCP server directly to see errors:
  ```bash
  GOOGLE_CLIENT_ID=... GOOGLE_CLIENT_SECRET=... GOOGLE_REFRESH_TOKEN=... \
    npx @shinzolabs/gmail-mcp
  ```

### "Authentication failed" / token expired

Refresh tokens expire. Re-run the auth command for the relevant provider:
```bash
npx @shinzolabs/gmail-mcp auth       # Gmail
npx ms-365-mcp-server auth ...       # Outlook
```

### Only one inbox needed

If you only use Gmail or only Outlook, you can omit the other server's credentials.
The agent will use whichever server is connected.

---

## Security Notes

- `.env` is in `.gitignore` — never commit it
- Refresh tokens grant long-lived access — treat them like passwords
- Revoke tokens at any time:
  - Gmail: [Google Account Permissions](https://myaccount.google.com/permissions)
  - Outlook: [Microsoft App Permissions](https://myaccount.microsoft.com/permissions)
- The `Mail.Send` scope is intentionally NOT requested — the agent can only create drafts
