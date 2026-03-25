# Teams App Manifest & Sideload (Code-Ready Reference)

> For Claude Code: See Sprint 1 result `05-azure-bot-registration.md` for the full manifest.

## Quick Reference

```bash
# Package
zip -j orgmind-teams-app.zip manifest.json color.png outline.png

# Sideload
# Teams → Apps → Manage your apps → Upload a custom app
```

## Key Fields

- `id` = MicrosoftAppId
- `bots[0].botId` = MicrosoftAppId
- `bots[0].scopes` = ["personal", "team", "groupChat"]
- Icons: `color.png` (192x192), `outline.png` (32x32)

## IMPORTANT NOTES
1. Full manifest template is in `sprint-1/results/05-azure-bot-registration.md`
2. Sideloading requires admin to enable "Upload custom apps" in Teams admin center
3. For org-wide deployment, publish to org app catalog
