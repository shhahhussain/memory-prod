# Dedupe Key Builder (Code-Ready Reference)

> For Claude Code: Port the POC's `SVC - Util - Dedupe Key Builder` service.

## Purpose

Generates deterministic `customId` and `conflict_group` for Supermemory documents to enable deduplication and conflict detection.

## Implementation

```python
import hashlib
import re

def normalize_for_key(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", text.lower().strip())

def build_conflict_group(content: str, metadata: dict) -> str:
    entity_type = metadata.get("entity_type", "fact")
    client = metadata.get("client", "general")
    department = metadata.get("department", "general")

    normalized = normalize_for_key(content)
    words = [w for w in normalized.split() if len(w) > 2][:5]
    slug = "_".join(words) if words else "unknown"

    return f"{entity_type}_{client}_{department}_{slug}"

def build_custom_id(content: str, metadata: dict) -> str:
    group = build_conflict_group(content, metadata)
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    return f"{group}_{content_hash}"

def enrich_write_payload(payload: dict) -> dict:
    content = payload.get("content", "")
    metadata = payload.get("metadata", {})

    if not payload.get("custom_id"):
        payload["custom_id"] = build_custom_id(content, metadata)

    if not metadata.get("conflict_group"):
        metadata["conflict_group"] = build_conflict_group(content, metadata)
        payload["metadata"] = metadata

    return payload
```

## IMPORTANT NOTES
1. `customId` = `conflict_group` + content hash (8 chars)
2. Same content → same customId → Supermemory deduplicates
3. Same topic, different content → same conflict_group, different customId → triggers conflict resolution
4. Always call `enrich_write_payload()` before writing to Supermemory
