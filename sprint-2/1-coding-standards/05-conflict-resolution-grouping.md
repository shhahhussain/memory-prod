# Conflict Resolution — Grouping (Code-Ready Reference)

> For Claude Code: How conflict_group is assigned and used.

## What is conflict_group?

A metadata field on Supermemory documents that identifies which memories can conflict. Memories in the same group are about the same fact and may contradict each other.

Example: Two memories about Acme's Q1 budget:
- `"Acme Q1 budget is $35K"` → `conflict_group: "client_acme_budget_q1"`
- `"Acme Q1 budget is $50K"` → `conflict_group: "client_acme_budget_q1"`

## How Groups Are Built (from POC Dedupe Key Builder)

The POC's `SVC - Util - Dedupe Key Builder` generates deterministic keys:

```python
import hashlib
import re

def build_conflict_group(content: str, metadata: dict) -> str:
    entity_type = metadata.get("entity_type", "fact")
    client = metadata.get("client", "general")
    department = metadata.get("department", "general")

    # Normalize content for grouping
    normalized = re.sub(r"[^a-z0-9\s]", "", content.lower().strip())
    # Take first 5 significant words
    words = [w for w in normalized.split() if len(w) > 2][:5]
    slug = "_".join(words)

    return f"{entity_type}_{client}_{department}_{slug}"

def build_custom_id(content: str, metadata: dict) -> str:
    group = build_conflict_group(content, metadata)
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    return f"{group}_{content_hash}"
```

## Grouping in Search Results

```python
from collections import defaultdict

def group_by_conflict(results: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    ungrouped = []

    for r in results:
        group = r.get("metadata", {}).get("conflict_group", "")
        if group:
            groups[group].append(r)
        else:
            ungrouped.append(r)

    return {"groups": dict(groups), "ungrouped": ungrouped}
```

## IMPORTANT NOTES
1. `conflict_group` is assigned at write time by the dedupe key builder
2. Empty `conflict_group` = no conflict possible, pass through
3. Group key format: `{entity_type}_{client}_{department}_{content_slug}`
4. Both `customId` and `conflict_group` come from the same builder
