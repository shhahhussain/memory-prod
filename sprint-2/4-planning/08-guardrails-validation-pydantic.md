# Topic: Guardrails — Write Validation with Pydantic

**Time:** 20-30 min
**Goal:** Port n8n guardrail code nodes to Pydantic validators

---

## What to Search
- "pydantic validator model_validator Python"
- "pydantic field_validator custom"
- "pydantic enum validation"

## POC Validation Rules
1. `memory_type` must be one of: fact, rule, agent, vector
2. `source_type` must be one of: slack, chat, email, doc, api, human, seed
3. `content` must be non-empty
4. `as_of` must be valid date format if present

## POC Guardrail Rules
- If `memory_type` is "fact" or "rule" (strict types):
  - AND `source_id` is missing OR `as_of` is missing
  - → Demote to `status = "draft"`
  - → Set `guardrail_reason = "missing_source_id_or_as_of"`

## Code Pattern
```python
from pydantic import BaseModel, field_validator, model_validator
from enum import Enum
from datetime import date

class MemoryType(str, Enum):
    FACT = "fact"
    RULE = "rule"
    AGENT = "agent"
    VECTOR = "vector"

class SourceType(str, Enum):
    SLACK = "slack"
    CHAT = "chat"
    EMAIL = "email"
    DOC = "doc"
    API = "api"
    HUMAN = "human"
    SEED = "seed"
    TEAMS = "teams"  # NEW for prod

class MemoryMetadata(BaseModel):
    memory_type: MemoryType
    source_type: SourceType
    source_id: str | None = None
    as_of: date | None = None
    confidence: float = 0.5
    source_authority: int = 5
    conflict_group: str = ""
    status: str = "active"
    guardrail_reason: str | None = None

    @model_validator(mode="after")
    def apply_guardrails(self):
        """Demote to draft if strict type is missing provenance."""
        strict_types = {MemoryType.FACT, MemoryType.RULE}
        if self.memory_type in strict_types:
            if not self.source_id or not self.as_of:
                self.status = "draft"
                self.guardrail_reason = "missing_source_id_or_as_of"
        return self

class WritePayload(BaseModel):
    content: str
    container_tag: str = "orgmind-poc"
    custom_id: str | None = None
    metadata: MemoryMetadata

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v.strip()
```

## What to Understand
- [ ] `field_validator` — validates individual fields
- [ ] `model_validator(mode="after")` — runs after all fields are set (can access self)
- [ ] Enum types automatically reject invalid values
- [ ] Guardrail logic lives IN the model, not in separate code
- [ ] This replaces 2 separate n8n workflows: `SVC - Util - Guardrails` + validation in `SVC - SM - Write`
