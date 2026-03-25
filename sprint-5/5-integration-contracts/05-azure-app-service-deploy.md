# Azure App Service Deploy (Code-Ready Reference)

> For Claude Code: Production deployment to Azure.

## Create Resources

```bash
az group create --name orgmind-rg --location eastus

az appservice plan create \
  --name orgmind-plan \
  --resource-group orgmind-rg \
  --sku B1 --is-linux

az webapp create \
  --name orgmind-bot \
  --resource-group orgmind-rg \
  --plan orgmind-plan \
  --runtime "PYTHON:3.11"
```

## Configure

```bash
az webapp config appsettings set --name orgmind-bot --resource-group orgmind-rg --settings \
  MicrosoftAppId="<id>" \
  MicrosoftAppPassword="<secret>" \
  ANTHROPIC_API_KEY="<key>" \
  SUPERMEMORY_API_KEY="<key>" \
  PORT=3978

# Startup command
az webapp config set --name orgmind-bot --resource-group orgmind-rg \
  --startup-file "python -m orgmind.app"
```

## Deploy

```bash
zip -r deploy.zip . -x ".git/*" "__pycache__/*" ".env" "tests/*"
az webapp deploy --name orgmind-bot --resource-group orgmind-rg --src-path deploy.zip --type zip
```

## Update Bot Endpoint

```bash
az bot update --resource-group orgmind-rg --name orgmind-bot \
  --endpoint "https://orgmind-bot.azurewebsites.net/api/messages"
```

## IMPORTANT NOTES
1. Use B1 SKU minimum (free tier doesn't support always-on)
2. Store secrets in Azure App Service app settings (env vars)
3. Set startup command to your Python entry point
4. Update bot messaging endpoint after deploy
