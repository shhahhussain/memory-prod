# Sprint 1 — Edge Cases & Known Pitfalls

> **Scope:** Agent Framework install, M365 SDK echo bot, Azure Bot registration, ngrok/dev tunnel, Supermemory SDK, pydantic-settings, project structure

---

## EC-S1.1 — Supermemory SDK smoke test timeout

**Scenario:** `AsyncSupermemory` client has no default timeout. Your smoke test calls `client.search(query="test")` — if Supermemory's API is slow (cold start), the call hangs for 60+ seconds with no error.

**Why dangerous:** During project setup, you think the SDK is broken and waste hours debugging. In production, a hung search blocks the entire agent.

```python
# WRONG — no timeout
client = AsyncSupermemory(api_key=key)
results = await client.search(query="test")  # Hangs forever if API is slow

# CORRECT — always set timeout at the session level
import aiohttp

timeout = aiohttp.ClientTimeout(total=15, connect=5)
session = aiohttp.ClientSession(timeout=timeout)
client = AsyncSupermemory(api_key=key, session=session)

try:
    results = await asyncio.wait_for(client.search(query="test"), timeout=10)
except asyncio.TimeoutError:
    print("Supermemory API not responding — check API key and network")
```

---

## EC-S1.2 — pydantic-settings `env_prefix` silently ignoring vars

**Scenario:** You set `env_prefix="ORGMIND_"` but your `.env` has `ANTHROPIC_API_KEY=sk-...` (no prefix). Settings loads with `anthropic_api_key=None`. No error at startup — crashes at first LLM call.

**Why dangerous:** Silent `None` propagation. You only discover it when a real user triggers an LLM call 10 minutes into testing.

```python
class OrgMindSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ORGMIND_")
    anthropic_api_key: SecretStr  # Requires ORGMIND_ANTHROPIC_API_KEY in .env

    @model_validator(mode='after')
    def validate_required_keys(self) -> 'OrgMindSettings':
        # Fail FAST at startup, not at first LLM call
        if not self.anthropic_api_key.get_secret_value():
            raise ValueError(
                "ORGMIND_ANTHROPIC_API_KEY is empty. "
                "Check your .env file uses the ORGMIND_ prefix."
            )
        return self
```

---

## EC-S1.3 — Azure Bot Registration: empty APP_ID/APP_PASSWORD in dev

**Scenario:** During dev, you leave `MicrosoftAppId` and `MicrosoftAppPassword` empty for local testing. This disables authentication entirely. If you accidentally deploy this config to production, **any HTTP client can send fake Teams activities to your bot endpoint** — no JWT validation.

**Why dangerous:** Full bot impersonation. Attacker sends crafted activities, triggers agent orchestration, exfiltrates memory data.

```python
# In your startup validation:
def validate_bot_config(settings: OrgMindSettings):
    if settings.environment == "production":
        if not settings.microsoft_app_id or not settings.microsoft_app_password:
            raise ConfigurationError(
                "FATAL: MicrosoftAppId/Password cannot be empty in production. "
                "This disables Bot Framework authentication entirely."
            )
```

---

## EC-S1.4 — ngrok/dev tunnel URL changes on restart

**Scenario:** You start ngrok, get `https://abc123.ngrok.io`. Configure it in Azure Bot registration as the messaging endpoint. Stop ngrok. Next day, restart — new URL `https://xyz789.ngrok.io`. Bot Framework sends activities to the old URL. Your bot receives nothing. Teams shows no error to the user — messages silently vanish.

**Why dangerous:** You waste hours thinking your code is broken when it's just a stale URL in Azure.

```bash
# FIX: Use a stable ngrok subdomain (paid) or Azure Dev Tunnels with persistent ID
# For dev tunnels:
devtunnel create --allow-anonymous
devtunnel port create -p 3978
devtunnel host
# Save the tunnel ID — reuse it across sessions

# OR: Use teamsapptester (no tunnel needed for initial dev)
# pip install teamsapptester
```

---

## EC-S1.5 — pyproject.toml dependency conflicts with `--pre` packages

**Scenario:** `agent-framework` is `1.0.0rc5` (pre-release). Your `pyproject.toml` has `agent-framework>=1.0.0`. `pip install .` skips `1.0.0rc5` because pip ignores pre-releases by default. You get `PackageNotFoundError`.

```toml
# WRONG
[project]
dependencies = [
    "agent-framework>=1.0.0",  # Skips 1.0.0rc5
]

# CORRECT — pin the exact pre-release version
[project]
dependencies = [
    "agent-framework==1.0.0rc5",
    "agent-framework-anthropic==1.0.0rc5",
]
```

---

## EC-S1.6 — Agent Framework `AnthropicClient` using wrong model ID format

**Scenario:** You pass `model_id="claude-sonnet"` instead of the full `"claude-sonnet-4-5-20250929"`. The SDK passes it to Anthropic's API as-is. API returns `400 Bad Request: Invalid model`. Error message is unclear about what model IDs are valid.

```python
# WRONG
client = AnthropicClient(model_id="claude-sonnet")

# CORRECT — use full model identifier
client = AnthropicClient(
    model_id="claude-sonnet-4-5-20250929",
    api_key=settings.anthropic_api_key.get_secret_value(),
)

# Validate at startup:
VALID_MODELS = {"claude-sonnet-4-5-20250929", "claude-haiku-3-5-20241022"}
if model_id not in VALID_MODELS:
    raise ConfigurationError(f"Invalid model_id: {model_id}. Valid: {VALID_MODELS}")
```
