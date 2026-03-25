# Topic: Azure App Service — Production Deployment

**Time:** 15 min
**Goal:** Deploy the bot to Azure App Service

---

## What to Search
- "Azure App Service Python deploy"
- "Azure App Service startup command FastAPI"
- "az webapp deploy zip Python"

## Create Resources
```bash
az group create --name orgmind-rg --location eastus
az appservice plan create --name orgmind-plan --resource-group orgmind-rg --sku B1 --is-linux
az webapp create --name orgmind-bot --resource-group orgmind-rg --plan orgmind-plan --runtime "PYTHON:3.11"
```

## Set Environment Variables
```bash
az webapp config appsettings set --name orgmind-bot --resource-group orgmind-rg --settings \
  MicrosoftAppId="<id>" \
  MicrosoftAppPassword="<secret>" \
  SUPERMEMORY_API_KEY="sm_..." \
  ANTHROPIC_API_KEY="sk-ant-..." \
  POSTGRES_URL="postgresql://..." \
```

## Startup Command
```bash
az webapp config set --name orgmind-bot --resource-group orgmind-rg \
  --startup-file "gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"
```

## Deploy
```bash
zip -r deploy.zip . -x ".git/*" "__pycache__/*" ".env" "tests/*"
az webapp deploy --name orgmind-bot --resource-group orgmind-rg --src-path deploy.zip --type zip
```

## Update Azure Bot Messaging Endpoint
Azure Portal → Azure Bot → Configuration → Messaging endpoint:
`https://orgmind-bot.azurewebsites.net/api/messages`

## What to Understand
- [ ] B1 SKU ($13/mo) is fine for initial prod
- [ ] `--is-linux` for Python (Windows doesn't support Python well)
- [ ] Startup command tells Azure how to run your FastAPI app
- [ ] Update Azure Bot endpoint from ngrok URL to Azure URL
- [ ] Use slots for zero-downtime deployments later
