# ngrok / Dev Tunnels — Local Development (Code-Ready Reference)

> For Claude Code: Use this when setting up local development tunneling for Teams bot testing.

## Why You Need a Tunnel

Teams/Bot Service sends messages to an HTTPS endpoint. During development, your bot runs on `localhost:3978`. A tunnel exposes it as a public HTTPS URL.

## Option 1: ngrok (Recommended for Quick Start)

### Install

```bash
# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

### Basic Usage

```bash
# Tunnel localhost:3978 to a public URL
ngrok http 3978
```

Output:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:3978
```

### Static Domain (Free Tier)

Free accounts get ONE static domain:

```bash
# First, claim your domain at https://dashboard.ngrok.com/domains
# Then use it:
ngrok http 3978 --domain=your-name.ngrok-free.app
```

This avoids updating the bot endpoint every time you restart ngrok.

### ngrok Config File

```yaml
# ~/.ngrok2/ngrok.yml
version: "2"
authtoken: your_auth_token_here
tunnels:
  orgmind:
    addr: 3978
    proto: http
    domain: your-name.ngrok-free.app
```

```bash
# Start named tunnel
ngrok start orgmind
```

### Update Bot Endpoint

After starting ngrok, update your Azure Bot messaging endpoint:

```bash
az bot update \
  --resource-group orgmind-rg \
  --name orgmind-bot \
  --endpoint "https://your-name.ngrok-free.app/api/messages"
```

## Option 2: Azure Dev Tunnels (Microsoft's Alternative)

### Install

```bash
# macOS
brew install microsoft/dev-tunnels/devtunnel

# Or download from https://aka.ms/devtunnels/download
```

### Login

```bash
devtunnel user login
```

### Basic Usage

```bash
# Create and host a tunnel
devtunnel host -p 3978 --allow-anonymous
```

Output includes the tunnel URL like:
```
Connect via browser: https://abc123-3978.usw2.devtunnels.ms
```

### Persistent Tunnel (Reusable URL)

```bash
# Create a named tunnel
devtunnel create orgmind-tunnel
devtunnel port create orgmind-tunnel -p 3978

# Set anonymous access (required for Bot Service)
devtunnel access create orgmind-tunnel -p 3978 --anonymous

# Host it
devtunnel host orgmind-tunnel
```

## Option 3: Agents Playground (No Tunnel Needed!)

Microsoft provides a local test tool that connects directly — NO ngrok needed:

```bash
# Install
npm install -g @microsoft/teams-app-test-tool

# Run (connects to localhost:3978 automatically)
teamsapptester
```

Opens a browser at `http://localhost:56150` with a Teams-like chat UI. Perfect for testing bot logic without Azure registration.

## Development Workflow

```
┌─────────────────────────────────────────────────┐
│  LOCAL DEV (no tunnel needed)                    │
│  python app.py → teamsapptester                  │
│  Fast iteration, no Azure setup                  │
└─────────────────────────────────────────────────┘
           ↓ when ready for real Teams
┌─────────────────────────────────────────────────┐
│  TUNNEL DEV (ngrok or devtunnel)                 │
│  python app.py → ngrok → Azure Bot → Teams       │
│  Test with real Teams, @mentions, group chats     │
└─────────────────────────────────────────────────┘
           ↓ when ready for deployment
┌─────────────────────────────────────────────────┐
│  PRODUCTION                                      │
│  Azure App Service → Azure Bot → Teams           │
│  No tunnel, direct HTTPS                         │
└─────────────────────────────────────────────────┘
```

## IMPORTANT NOTES FOR CODE GENERATION

1. **Default port is 3978** — both M365 SDK and test tools expect this
2. **Use `teamsapptester` first** — no ngrok needed for initial development
3. **ngrok free tier**: 1 static domain, sessions expire after ~2 hours
4. **Always use HTTPS** — Bot Service requires it
5. **Update Azure Bot endpoint** every time your tunnel URL changes (unless static domain)
6. For production, deploy to Azure App Service — no tunnel needed
