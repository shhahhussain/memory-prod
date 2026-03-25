# Sprint 4 — Production Hardening Research

**Milestone:** M4 — Production Hardening (20-25h)
**Focus:** Observability, caching, security, error handling, email surface

---

## What to Research

### 1. Security & Auth — Zero Trust

**Azure Bot auth flow:**
```
Teams → Azure Bot Service (validates JWT) → Your endpoint (validates again)
```

**Key items:**
- MSAL auth for bot identity
- Environment variables via Azure App Service config for secrets
- Rate limiting per user/team
- Memory content sanitization (prompt injection defense)

**Search queries:**
- "MSAL Python bot authentication Teams"
- "prompt injection defense LLM Python"
- "FastAPI rate limiting per user"
- "Azure App Service managed identity"

---

### 4. Error Handling & Resilience

**Circuit breaker for external services:**
```python
# When Supermemory/Asana/GDocs is down, fail fast instead of timeout
```

**Retry with exponential backoff:**
```python
import tenacity

@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
    retry=tenacity.retry_if_exception_type(httpx.TimeoutException),
)
async def search_memory(query: str):
    ...
```

**Search queries:**
- "circuit breaker pattern Python async"
- "tenacity retry Python async"
- "resilience patterns microservices Python"
- "graceful degradation AI agent"

---

### 5. Email Surface Port (if in scope)

POC email pipeline:
- Gmail bridge → webhook receiver → client lookup → response agent → confidence routing → approval queue

**Teams/Azure equivalents:**
| POC (n8n) | Prod (Python) |
|-----------|--------------|
| Gmail trigger | Azure Logic Apps / Microsoft Graph API |
| SMTP send | Microsoft Graph API send mail |
| Slack approval post | Teams proactive message with Adaptive Card |
| Webhook receiver | FastAPI endpoint |

**Search queries:**
- "Microsoft Graph API send email Python"
- "Azure Logic Apps email trigger"
- "msgraph-sdk-python mail send"

---

### 6. Database Hardening

**POC tables to migrate:**
- `conflict_override` — needs advisory lock handling in asyncpg
- `conflict_audit_log` + `conflict_audit_snapshot`
- `email_reply_approval_queue`
- `client_email_lookup`
- `slack_thread_context` → `teams_thread_context`
- `slack_agent_context` → `teams_agent_context`
- `slack_event_dedupe` → `teams_event_dedupe`
- `agent_action_log`
- `chat_response_feedback`
- `memory_feedback_review_queue`

**Search queries:**
- "asyncpg advisory lock Python"
- "PostgreSQL migration tool Python alembic"
- "alembic async migration asyncpg"

---

## Checklist
- [ ] Implement retry/circuit breaker for Supermemory calls
- [ ] Plan DB migration from POC tables
- [ ] Set up structlog for structured logging
- [ ] Test Microsoft Graph API email (if in scope)
