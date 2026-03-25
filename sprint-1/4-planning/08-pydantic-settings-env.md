# Topic: Pydantic Settings — Config from .env

**Time:** 15-20 min
**Goal:** Set up typed, validated config management (replaces n8n credential nodes)

---

## What to Search
- "pydantic-settings BaseSettings env file Python"
- "pydantic settings nested config"

## Install
```bash
pip install pydantic-settings
```

## Code
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Microsoft
    microsoft_app_id: str
    microsoft_app_password: str

    # LLMs
    anthropic_api_key: str
    gemini_api_key: str

    # Memory
    supermemory_api_key: str

    # Database
    postgres_url: str
    # Agent config
    agent_timeout_seconds: float = 30.0
    max_context_tokens: int = 100000
    summarize_threshold: float = 0.75

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

settings = Settings()
```

## .env file
```
MICROSOFT_APP_ID=abc123
MICROSOFT_APP_PASSWORD=secret
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
SUPERMEMORY_API_KEY=sm_...
POSTGRES_URL=postgresql://user:pass@host:5432/orgmind
```

## What to Understand
- [ ] How `BaseSettings` reads from env vars automatically
- [ ] How `.env` file loading works
- [ ] How nested config works with `__` delimiter
- [ ] How defaults work (e.g., `agent_timeout_seconds` has a default)
- [ ] How validation catches missing required vars at startup
