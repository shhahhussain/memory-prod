# Azure Bot Registration (Code-Ready Reference)

> For Claude Code: Use this when setting up Azure Bot Service for OrgMind Teams integration.

## Overview

Azure Bot Registration connects your Python bot to Microsoft Teams. It's an Azure resource that acts as the identity and routing layer.

## Step-by-Step Registration

### Step 1: Create App Registration (Entra ID)

```bash
# Create the app registration
az ad app create --display-name "OrgMind-Bot" --sign-in-audience "AzureADMultipleOrgs"

# Note the appId from output — this is your MicrosoftAppId
# Example: "appId": "12345678-abcd-efgh-ijkl-123456789012"

# Create a client secret
az ad app credential reset --id <appId> --years 2

# Note the "password" from output — this is your MicrosoftAppPassword
```

**Account type MUST be `AzureADMultipleOrgs` (Multitenant)** — Teams requires this.

### Step 2: Create Azure Bot Resource

```bash
# Create resource group (if not exists)
az group create --name orgmind-rg --location eastus

# Create the bot
az bot create \
  --resource-group orgmind-rg \
  --name orgmind-bot \
  --app-type MultiTenant \
  --appid <MicrosoftAppId> \
  --password <MicrosoftAppPassword> \
  --sku F0
```

**SKU options:**
- `F0` — Free (dev/test, limited messages)
- `S1` — Standard (production)

### Step 3: Enable Teams Channel

```bash
az bot msteams create --resource-group orgmind-rg --name orgmind-bot
```

Or via Azure Portal: Bot resource → Channels → Microsoft Teams → Enable.

### Step 4: Set Messaging Endpoint

```bash
az bot update \
  --resource-group orgmind-rg \
  --name orgmind-bot \
  --endpoint "https://your-domain.azurewebsites.net/api/messages"
```

For local dev with ngrok: `https://abc123.ngrok-free.app/api/messages`

## Required Environment Variables

```bash
# .env file
MicrosoftAppId=12345678-abcd-efgh-ijkl-123456789012
MicrosoftAppPassword=your-client-secret-here
MicrosoftAppTenantId=common   # "common" for multitenant
MicrosoftAppType=MultiTenant
PORT=3978
```

## Auth Configuration in Code

### Development (Anonymous — No Auth)

```python
# Pass None for auth config
start_server(AGENT_APP, None)
```

### Production (MSAL Auth)

```bash
pip install microsoft-agents-authentication-msal
```

```python
from microsoft_agents.authentication.msal import MsalAuth
from microsoft_agents.hosting.core import AgentAuthConfiguration

auth_config = AgentAuthConfiguration(
    app_id=os.environ["MicrosoftAppId"],
    app_password=os.environ["MicrosoftAppPassword"],
    tenant_id=os.environ.get("MicrosoftAppTenantId", "common"),
)

start_server(AGENT_APP, auth_config)
```

## Teams App Manifest

The manifest is a zip containing 3 files:

### `manifest.json`

```json
{
  "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.17/MicrosoftTeams.schema.json",
  "manifestVersion": "1.17",
  "version": "1.0.0",
  "id": "<MicrosoftAppId>",
  "developer": {
    "name": "GroupM",
    "websiteUrl": "https://www.groupm.com",
    "privacyUrl": "https://www.groupm.com/privacy",
    "termsOfUseUrl": "https://www.groupm.com/terms"
  },
  "name": {
    "short": "OrgMind",
    "full": "OrgMind AI Memory Agent"
  },
  "description": {
    "short": "AI-powered organizational memory",
    "full": "OrgMind helps teams capture, retrieve, and manage organizational knowledge through natural conversation."
  },
  "icons": {
    "color": "color.png",
    "outline": "outline.png"
  },
  "accentColor": "#4F6BED",
  "bots": [
    {
      "botId": "<MicrosoftAppId>",
      "scopes": ["personal", "team", "groupChat"],
      "supportsFiles": false,
      "isNotificationOnly": false,
      "commandLists": [
        {
          "scopes": ["personal", "team", "groupChat"],
          "commands": [
            { "title": "help", "description": "Get help with OrgMind" },
            { "title": "search", "description": "Search organizational memory" },
            { "title": "remember", "description": "Save information to memory" }
          ]
        }
      ]
    }
  ],
  "permissions": ["identity", "messageTeamMembers"],
  "validDomains": []
}
```

### Icons Required
- `color.png` — 192x192 pixels, full color
- `outline.png` — 32x32 pixels, white on transparent

### Package & Sideload

```bash
# Create zip
zip -j orgmind-teams-app.zip manifest.json color.png outline.png

# Sideload in Teams:
# Teams → Apps → Manage your apps → Upload a custom app → Upload for me or my org
```

## Visual Manifest Editor

Use https://dev.teams.microsoft.com/ to create/edit manifests with a GUI.

## IMPORTANT NOTES FOR CODE GENERATION

1. **Multitenant is REQUIRED** for Teams bots — `AzureADMultipleOrgs`
2. **Messaging endpoint must be HTTPS** — use ngrok for local dev
3. **Port 3978** is convention — matches M365 SDK default
4. **F0 (free)** SKU is fine for development
5. Auth is optional for local dev (pass `None`) but required for production
6. The manifest `id` and `bots.botId` must match your `MicrosoftAppId`
