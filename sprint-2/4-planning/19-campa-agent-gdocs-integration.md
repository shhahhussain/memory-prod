# Topic: CAMPA Agent — Google Docs Integration

**Time:** 20 min
**Goal:** Port CAMPA's campaign brief creation

---

## What to Search
- "Google Docs API Python create document"
- "google-api-python-client docs quickstart"
- "Google Drive API Python service account"

## Install
```bash
pip install google-api-python-client google-auth
```

## What CAMPA Does (from POC)
1. Receives campaign brief request from MINDY
2. Parses: campaign objective, client, type
3. Searches Supermemory for campaign context
4. Builds brief structure: objective, pillars, channels, CTA
5. Creates Google Doc (or returns mock link)
6. Returns: doc link, brief structure, confidence

## Google Docs API
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file("service-account.json", scopes=SCOPES)

docs_service = build("docs", "v1", credentials=creds)
drive_service = build("drive", "v3", credentials=creds)

async def create_campaign_doc(title: str, content: str) -> dict:
    try:
        # Create doc
        doc = docs_service.documents().create(body={"title": title}).execute()
        doc_id = doc["documentId"]

        # Add content
        docs_service.documents().batchUpdate(documentId=doc_id, body={
            "requests": [{
                "insertText": {
                    "location": {"index": 1},
                    "text": content,
                }
            }]
        }).execute()

        return {
            "ok": True,
            "doc_id": doc_id,
            "url": f"https://docs.google.com/document/d/{doc_id}/edit",
        }
    except Exception as e:
        return {"ok": False, "mock": True, "url": f"https://mock-doc.example.com/{title}", "error": str(e)}
```

## Brief Structure (from POC)
```python
class CampaignBrief(BaseModel):
    objective: str
    client: str
    campaign_type: str
    key_pillars: list[str]
    channels: list[str]
    cta: str
    budget_context: str | None = None

    def to_doc_content(self) -> str:
        return f"""Campaign Brief: {self.client}

Objective: {self.objective}
Type: {self.campaign_type}

Key Pillars:
{chr(10).join(f"- {p}" for p in self.key_pillars)}

Channels:
{chr(10).join(f"- {c}" for c in self.channels)}

Call to Action: {self.cta}

Budget Context: {self.budget_context or "TBD"}
"""
```

## What to Understand
- [ ] Google API client is synchronous — wrap with `asyncio.to_thread()`
- [ ] Service account auth for server-to-server (no OAuth consent screen)
- [ ] Mock fallback when GDocs unavailable (same as POC)
- [ ] CAMPA's LLM call generates the brief structure, then formats it for the doc
