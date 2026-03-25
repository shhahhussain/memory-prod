# Conflict Resolution — Scoring (Code-Ready Reference)

> For Claude Code: Port the POC's `Code - Detect & Resolve Conflicts` node.

## POC Algorithm (from n8n)

Groups results by `metadata.conflict_group`, then for each group with 2+ candidates:

**Sort order (priority):**
1. `as_of` descending (most recent wins)
2. `confidence` descending (higher confidence wins)
3. `source_authority` ascending (lower number = higher authority)

Keep winner, drop losers. Annotate winner with resolution reason.

## Production Implementation

```python
from datetime import date
from pydantic import BaseModel

class MemoryCandidate(BaseModel):
    id: str
    content: str
    similarity: float
    metadata: dict

    @property
    def as_of(self) -> str:
        return self.metadata.get("as_of", "1970-01-01")

    @property
    def confidence(self) -> float:
        return float(self.metadata.get("confidence", 0.0))

    @property
    def source_authority(self) -> int:
        return int(self.metadata.get("source_authority", 99))

    @property
    def conflict_group(self) -> str:
        return self.metadata.get("conflict_group", "")

class ResolutionResult(BaseModel):
    winner: MemoryCandidate
    losers: list[MemoryCandidate]
    reason: str  # "recency" | "confidence" | "source_authority" | "tie"
    group: str

def resolve_conflict_group(candidates: list[MemoryCandidate]) -> ResolutionResult:
    if len(candidates) == 1:
        return ResolutionResult(winner=candidates[0], losers=[], reason="only_candidate", group=candidates[0].conflict_group)

    # Sort: as_of DESC, confidence DESC, source_authority ASC
    sorted_candidates = sorted(
        candidates,
        key=lambda c: (c.as_of, c.confidence, -c.source_authority),
        reverse=True,
    )

    winner = sorted_candidates[0]
    losers = sorted_candidates[1:]

    # Determine reason
    if winner.as_of > losers[0].as_of:
        reason = "recency"
    elif winner.confidence > losers[0].confidence:
        reason = "confidence"
    elif winner.source_authority < losers[0].source_authority:
        reason = "source_authority"
    else:
        reason = "tie"

    return ResolutionResult(winner=winner, losers=losers, reason=reason, group=winner.conflict_group)

def resolve_conflicts(results: list[MemoryCandidate]) -> list[MemoryCandidate]:
    from collections import defaultdict
    groups: dict[str, list[MemoryCandidate]] = defaultdict(list)

    resolved = []
    for r in results:
        if r.conflict_group:
            groups[r.conflict_group].append(r)
        else:
            resolved.append(r)  # No conflict group → pass through

    for group_key, candidates in groups.items():
        resolution = resolve_conflict_group(candidates)
        # Annotate winner
        resolution.winner.metadata["_resolution"] = {
            "reason": resolution.reason,
            "losers_dropped": len(resolution.losers),
            "group": group_key,
        }
        resolved.append(resolution.winner)

    return resolved
```

## IMPORTANT NOTES
1. Matches POC's `Code - Detect & Resolve Conflicts` exactly
2. Sort: as_of DESC → confidence DESC → source_authority ASC
3. Results without `conflict_group` pass through unchanged
4. Winner gets `_resolution` annotation for audit trail
