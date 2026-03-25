# Topic: ngrok / Dev Tunnel for Local Development

**Time:** 15-20 min
**Goal:** Get a public HTTPS URL pointing to localhost so Teams can reach your bot

---

## What to Search
- "ngrok Teams bot local development"
- "Azure dev tunnels Python bot"
- "ngrok setup localhost 3978 https"

## Why This is Needed
Teams → Azure Bot Service → **your messaging endpoint**. During local dev, your endpoint is `localhost:3978` which Teams can't reach. ngrok creates a public tunnel.

## Option A: ngrok
```bash
# Install
brew install ngrok  # or download from ngrok.com

# Start tunnel
ngrok http 3978

# Output shows something like:
# https://abc123.ngrok-free.app → http://localhost:3978
```

Then update Azure Bot Configuration → Messaging endpoint to:
`https://abc123.ngrok-free.app/api/messages`

## Option B: Azure Dev Tunnels
```bash
# Install
brew install azure-dev-tunnels  # or via VS Code extension

# Create tunnel
devtunnel create --allow-anonymous
devtunnel port create -p 3978
devtunnel host
```

## What to Understand
- [ ] How to start ngrok tunnel
- [ ] How to update the Azure Bot messaging endpoint URL
- [ ] That you need to update the URL every time ngrok restarts (free tier)
- [ ] That Dev Tunnels can give you a persistent URL
