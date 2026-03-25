# Topic: Conflict Resolution — Multi-Dimension Scoring Algorithm

**Time:** 30-45 min
**Goal:** Understand and port the POC's conflict winner selection logic

---

## What to Search
- "multi-dimension scoring algorithm Python"
- "deterministic tie-breaking sort Python"
- "tuple comparison Python sorting"

## POC Scoring Dimensions (in priority order)
1. **Type rank** — `unknown` gets penalized (ranked last)
2. **Recency** — `as_of` date, descending (newer wins)
3. **Confidence** — float 0-1, descending (higher wins)
4. **Source authority** — integer, ascending (lower number = higher authority)
5. **Stable fallback** — original index (for deterministic ties)

## Code Pattern
```python
from dataclasses import dataclass
from datetime import date

@dataclass
class ConflictCandidate:
    id: str
    content: str
    memory_type: str
    as_of: date | None
    confidence: float
    source_authority: int
    original_index: int

    @property
    def type_rank(self) -> int:
        """Lower = better. Unknown types get penalty."""
        ranks = {"fact": 1, "rule": 2, "agent": 3, "vector": 4}
        return ranks.get(self.memory_type, 99)

    @property
    def sort_key(self) -> tuple:
        """Python sorts tuples element by element. Negate for descending."""
        return (
            self.type_rank,                              # asc (lower = better)
            -(self.as_of.toordinal() if self.as_of else 0),  # desc (newer = better)
            -self.confidence,                             # desc (higher = better)
            self.source_authority,                        # asc (lower = better)
            self.original_index,                         # stable fallback
        )

def pick_winner(candidates: list[ConflictCandidate]) -> ConflictCandidate:
    sorted_candidates = sorted(candidates, key=lambda c: c.sort_key)
    return sorted_candidates[0]
```

## What to Understand
- [ ] Python tuple comparison goes element by element (perfect for multi-dimension)
- [ ] Negate numeric values for descending sort within ascending tuple
- [ ] `original_index` ensures deterministic results even on perfect ties
- [ ] This is the core of `Code - Detect & Resolve Conflicts` in the POC ORCH
