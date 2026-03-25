# Topic: Azure Bot Registration (Step by Step)

**Time:** 30-45 min
**Goal:** Register a bot in Azure so Teams can talk to it

---

## What to Search
- "Azure bot registration step by step 2026"
- "Azure Entra ID app registration bot"
- "Azure Bot Service create Python"

## Docs to Read
- https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-registration
- https://learn.microsoft.com/en-us/azure/bot-service/abs-quickstart

## Steps
1. Azure Portal → **Microsoft Entra ID** → App registrations → New registration
2. Name: `OrgMind-Bot`
3. Account type: **Multitenant** (REQUIRED for Teams)
4. Note the **Application (client) ID** → this is `MicrosoftAppId`
5. Go to **Certificates & secrets** → New client secret → save as `MicrosoftAppPassword`
6. Azure Portal → search **Azure Bot** → Create
7. Paste your App ID
8. Pricing: **F0** (free for dev)
9. Go to **Channels** → Enable **Microsoft Teams**
10. Go to **Configuration** → Messaging endpoint: `https://your-domain/api/messages`

## What to Understand
- [ ] What is `MicrosoftAppId` (the client ID from Entra)
- [ ] What is `MicrosoftAppPassword` (the client secret)
- [ ] Why Multitenant is required for Teams
- [ ] What the messaging endpoint URL does
- [ ] How to test with a temporary ngrok URL

## Environment Variables Needed
```
MicrosoftAppId=<from step 4>
MicrosoftAppPassword=<from step 5>
```
