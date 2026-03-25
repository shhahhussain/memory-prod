# Guardrails — Pydantic Validation (Code-Ready Reference)

> For Claude Code: Port the POC's `SVC - Util - Guardrails` service.

## POC Behavior

Before writing to Supermemory, validate content and metadata:
- For `fact` or `rule` types: if `source_id` or `as_of` missing → set `status=draft`
- Always ensure required metadata fields exist

## Implementation

```python
from datetime import date
from pydantic import BaseModel, Field, field_validator, model_validator

class MemoryMetadata(BaseModel):
    memory_type: str = "fact"          # fact | rule | agent | vector
    source_type: str = "chat"          # chat | human | email | doc | api | seed
    created_by: str = ""
    source_id: str = ""
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    as_of: str = ""                    # ISO date
    project: str = "orgmind"
    schema_version: str = "v2"
    entity_type: str = "fact"
    client: str = "general"
    department: str = "general"
    source_authority: int = Field(default=5, ge=1, le=10)
    status: str = "active"             # active | draft | deprecated
    conflict_group: str = ""
    is_current: bool = True

    @field_validator("memory_type")
    @classmethod
    def validate_memory_type(cls, v):
        if v not in ("fact", "rule", "agent", "vector"):
            return "fact"
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in ("active", "draft", "deprecated"):
            return "active"
        return v

class WritePayload(BaseModel):
    content: str = Field(min_length=1, max_length=50000)
    container_tag: str = "orgmind"
    custom_id: str = ""
    metadata: MemoryMetadata = MemoryMetadata()

class GuardrailResult(BaseModel):
    ok: bool = True
    write_allowed: bool = True
    payload: WritePayload
    guardrail_flags: list[str] = []
    effective_status: str = "active"

def apply_guardrails(payload: WritePayload) -> GuardrailResult:
    flags = []
    meta = payload.metadata

    # Rule: facts/rules without source_id or as_of → draft
    if meta.memory_type in ("fact", "rule"):
        if not meta.source_id or not meta.as_of:
            meta.status = "draft"
            flags.append("missing_source_id_or_as_of")

    # Ensure as_of has a value (default to today)
    if not meta.as_of:
        meta.as_of = date.today().isoformat()

    # Content length check
    if len(payload.content.strip()) < 10:
        flags.append("content_too_short")

    return GuardrailResult(
        ok=True,
        write_allowed=True,
        payload=payload,
        guardrail_flags=flags,
        effective_status=meta.status,
    )
```

## IMPORTANT NOTES
1. Mirrors POC's `SVC - Util - Guardrails` exactly
2. Missing source_id/as_of on facts → status becomes "draft"
3. Pydantic handles type coercion and validation automatically
4. `source_authority`: 1 = highest (human-reviewed), 10 = lowest
