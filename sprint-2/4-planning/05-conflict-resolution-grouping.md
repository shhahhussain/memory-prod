# Topic: Conflict Resolution — Grouping & Detection

**Time:** 20-30 min
**Goal:** Understand how memories are grouped into conflict sets

---

## What to Search
- "conflict group detection algorithm"
- "metadata grouping Python defaultdict"
- "semantic deduplication content normalization"

## Two Grouping Methods

### Method 1: Explicit Groups (primary)
Memories have `metadata.conflict_group` set explicitly (e.g., `"acme_budget_q1"`).
All memories with the same conflict_group are candidates.

### Method 2: Lazy Detection (fallback)
When no explicit group, derive from content:
- Extract: memory_type + client + subject tokens
- Build a lazy group key like: `lazy_conflict_fact_acme_budget`

## Code Pattern
```python
from collections import defaultdict

def group_conflicts(memories: list[Memory]) -> dict[str, list[Memory]]:
    groups = defaultdict(list)

    for mem in memories:
        # Explicit group
        group = mem.metadata.get("conflict_group", "")
        if group:
            groups[group].append(mem)
        else:
            # Lazy detection
            lazy_key = build_lazy_key(mem)
            if lazy_key:
                groups[lazy_key].append(mem)

    # Only return groups with 2+ candidates (single = no conflict)
    return {k: v for k, v in groups.items() if len(v) >= 2}

def build_lazy_key(mem: Memory) -> str:
    """Derive conflict group from content when not explicitly set."""
    parts = [
        mem.metadata.get("memory_type", "unknown"),
        mem.metadata.get("client", "general"),
        # Extract subject tokens from content (first 3-4 meaningful words)
        "_".join(extract_subject_tokens(mem.content)[:4]),
    ]
    return f"lazy_conflict_{'_'.join(parts)}"
```

## Value-Signature Dedup
If all candidates in a group have the **same normalized content**, it's NOT a real conflict:

```python
def is_meaningful_conflict(candidates: list[Memory]) -> bool:
    signatures = {normalize_content(c.content) for c in candidates}
    return len(signatures) > 1  # If all same → not a conflict

def normalize_content(text: str) -> str:
    """Strip formatting, lowercase, collapse whitespace."""
    return " ".join(text.lower().split())
```

## What to Understand
- [ ] Explicit `conflict_group` metadata is the primary grouping mechanism
- [ ] Lazy detection is a fallback for untagged memories
- [ ] Single-member groups are not conflicts (need 2+)
- [ ] Same content but different metadata = not a meaningful conflict
- [ ] This runs AFTER Supermemory search, BEFORE context pack assembly
