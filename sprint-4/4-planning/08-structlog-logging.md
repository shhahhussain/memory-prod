# Topic: Structured Logging with structlog

**Time:** 10 min
**Goal:** Replace print() with proper structured logging

---

## What to Search
- "structlog Python FastAPI setup"
- "structured logging JSON Python"

## Install
```bash
pip install structlog
```

## Setup
```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

logger = structlog.get_logger()
```

## Usage
```python
# Instead of: print(f"Searching memory for {query}")
logger.info("memory_search", query=query, container="orgmind-poc", limit=5)

# Instead of: print(f"Error: {e}")
logger.error("agent_failed", agent="TASKR", error=str(e), conversation_id=conv_id)

# Instead of: print(f"Conflict resolved: {winner}")
logger.info("conflict_resolved", group="acme_budget_q1", winner="fact:abc123", strategy="hierarchy")
```

## Output (JSON, machine-parseable)
```json
{"event": "memory_search", "query": "acme budget", "container": "orgmind-poc", "limit": 5, "level": "info", "timestamp": "2026-03-21T10:30:00Z"}
```

## What to Understand
- [ ] Structured logs are key-value pairs, not free text
- [ ] JSON output is parseable by log aggregators (Datadog/CloudWatch/Azure Monitor)
- [ ] Every log entry should have context (conversation_id, agent, etc.)
- [ ] `structlog` is zero-config compared to Python's logging module
