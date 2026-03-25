# Pydantic Settings — Environment Config (Code-Ready Reference)

> For Claude Code: Use this for ALL configuration management in OrgMind.

## Installation

```bash
pip install pydantic-settings
```

Requires: `pydantic>=2.0`

## Basic Usage

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore extra vars in .env
    )

    # Required — no default, MUST be in env or .env
    anthropic_api_key: str
    supermemory_api_key: str

    # Required for Teams (but optional for local dev)
    microsoft_app_id: str = ""
    microsoft_app_password: str = ""
    microsoft_app_tenant_id: str = "common"

    # Optional with defaults
    port: int = 3978
    agent_timeout_seconds: float = 30.0
    log_level: str = "INFO"
    postgres_url: str = ""


# Usage
settings = Settings()
print(settings.anthropic_api_key)
```

## Environment Variable Mapping

By default, field names map to UPPERCASE env vars:

| Field | Env Var |
|-------|---------|
| `anthropic_api_key` | `ANTHROPIC_API_KEY` |
| `supermemory_api_key` | `SUPERMEMORY_API_KEY` |
| `microsoft_app_id` | `MICROSOFT_APP_ID` |
| `port` | `PORT` |

### Custom Prefix

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ORGMIND_")

    api_key: str   # reads ORGMIND_API_KEY from env
```

### Custom Field Alias

```python
from pydantic import Field

class Settings(BaseSettings):
    app_id: str = Field(alias="MicrosoftAppId")  # reads MicrosoftAppId exactly
```

## Nested Settings

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    model_id: str = "claude-sonnet-4-5-20250929"
    max_tokens: int = 4096
    temperature: float = 0.7


class MemoryConfig(BaseModel):
    search_limit: int = 10
    threshold: float = 0.5
    rerank: bool = True


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",  # enables LLM__MODEL_ID=xxx
        extra="ignore",
    )

    anthropic_api_key: str
    supermemory_api_key: str

    llm: LLMConfig = LLMConfig()
    memory: MemoryConfig = MemoryConfig()
```

With `env_nested_delimiter="__"`:

```bash
# .env
LLM__MODEL_ID=claude-sonnet-4-5-20250929
LLM__MAX_TOKENS=8192
MEMORY__THRESHOLD=0.6
```

## Multiple .env Files

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),  # .env.local overrides .env
    )
```

## Validation

```python
from pydantic import field_validator

class Settings(BaseSettings):
    anthropic_api_key: str
    port: int = 3978

    @field_validator("anthropic_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v.startswith("sk-ant-"):
            raise ValueError("Invalid Anthropic API key format")
        return v

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1024 <= v <= 65535):
            raise ValueError("Port must be between 1024 and 65535")
        return v
```

## OrgMind Settings Template

```python
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    anthropic_model: str = "claude-sonnet-4-5-20250929"
    gemini_model: str = "gemini-2.0-flash"
    max_tokens: int = 4096
    temperature: float = 0.7
    thinking_budget: int = 10000


class MemoryConfig(BaseModel):
    search_limit: int = 10
    threshold: float = 0.5
    rerank: bool = True
    default_search_mode: str = "hybrid"


class TeamsConfig(BaseModel):
    app_id: str = ""
    app_password: str = ""
    tenant_id: str = "common"
    app_type: str = "MultiTenant"


class OrgMindSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # API Keys
    anthropic_api_key: str
    supermemory_api_key: str
    gemini_api_key: str = ""

    # Infrastructure
    port: int = 3978
    log_level: str = "INFO"
    postgres_url: str = ""

    # Sub-configs
    llm: LLMConfig = LLMConfig()
    memory: MemoryConfig = MemoryConfig()
    teams: TeamsConfig = TeamsConfig()

    # Agent settings
    agent_timeout_seconds: float = 30.0
    max_concurrent_agents: int = 3


# Singleton pattern
_settings: OrgMindSettings | None = None

def get_settings() -> OrgMindSettings:
    global _settings
    if _settings is None:
        _settings = OrgMindSettings()
    return _settings
```

## Corresponding .env File

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
SUPERMEMORY_API_KEY=sm_...
GEMINI_API_KEY=...

PORT=3978
LOG_LEVEL=INFO
POSTGRES_URL=postgresql://user:pass@localhost:5432/orgmind

# Nested config
LLM__ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
LLM__MAX_TOKENS=4096
MEMORY__THRESHOLD=0.5
MEMORY__RERANK=true
TEAMS__APP_ID=12345678-...
TEAMS__APP_PASSWORD=...
TEAMS__TENANT_ID=common
```

## IMPORTANT NOTES FOR CODE GENERATION

1. **Import from `pydantic_settings`**, NOT `pydantic`
2. **`extra="ignore"`** prevents crashes from unrelated env vars
3. **`env_nested_delimiter="__"`** enables `LLM__MODEL_ID` → `settings.llm.model_id`
4. **Defaults are validated** — unlike regular Pydantic BaseModel
5. **No `.env` auto-loading** in Agent Framework — call `Settings()` explicitly
6. Priority: env vars > .env file > defaults
7. **Secrets**: In production, use Azure App Service app settings (env vars) for sensitive values
