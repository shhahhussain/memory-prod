# Topic: Teams App Manifest & Sideloading

**Time:** 15 min
**Goal:** Package your bot as a Teams app and install it

---

## What to Search
- "Teams app manifest sideload bot"
- "Teams Developer Portal create app"
- "Teams manifest.json schema v1.17"

## Manifest (manifest.json)
```json
{
  "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.17/MicrosoftTeams.schema.json",
  "manifestVersion": "1.17",
  "version": "1.0.0",
  "id": "<your-azure-bot-app-id>",
  "developer": {
    "name": "OrgMind",
    "websiteUrl": "https://orgmind.example.com",
    "privacyUrl": "https://orgmind.example.com/privacy",
    "termsOfUseUrl": "https://orgmind.example.com/terms"
  },
  "name": {"short": "MINDY", "full": "MINDY - OrgMind AI Assistant"},
  "description": {"short": "AI memory assistant", "full": "OrgMind organizational memory agent"},
  "icons": {"color": "color.png", "outline": "outline.png"},
  "accentColor": "#4F6BED",
  "bots": [{
    "botId": "<your-azure-bot-app-id>",
    "scopes": ["personal", "team", "groupChat"],
    "supportsFiles": false,
    "isNotificationOnly": false
  }]
}
```

## Package
```bash
# Create icons (required)
# color.png — 192x192
# outline.png — 32x32

# Zip it
zip orgmind-bot.zip manifest.json color.png outline.png
```

## Sideload
1. Teams → Apps → Manage your apps → Upload a custom app
2. Select `orgmind-bot.zip`
3. Add to a group chat or team

## Visual Editor Alternative
https://dev.teams.microsoft.com/ — create + package the app visually

## What to Understand
- [ ] `id` and `botId` must match your Azure Bot's App ID
- [ ] `scopes` controls where the bot appears (personal chat, team channels, group chats)
- [ ] You need both icon sizes or upload will fail
- [ ] Sideloading must be enabled in the Teams admin center
