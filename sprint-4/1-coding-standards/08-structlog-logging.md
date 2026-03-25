# structlog — Structured Logging (Code-Ready Reference)

> For Claude Code: JSON-structured logging for OrgMind.

## Installation

```bash
pip install structlog
```

## Setup

```python
import structlog
import logging

def setup_logging(log_level: str = "INFO"):
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if log_level == "DEBUG" else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, log_level)),
    )

logger = structlog.get_logger()
```

## Usage

```python
logger.info("agent_dispatched", agent="FINDR", query="Nike budget", user="Shah")
logger.warning("agent_timeout", agent="TASKR", timeout_seconds=30)
logger.error("supermemory_error", status_code=500, endpoint="/v4/search")
```

Output (JSON):
```json
{"event": "agent_dispatched", "agent": "FINDR", "query": "Nike budget", "user": "Shah", "level": "info", "timestamp": "2026-03-21T10:00:00Z"}
```

## IMPORTANT NOTES
1. Use JSON in production, ConsoleRenderer in development
2. Always include structured context (agent name, query, user)
3. structlog integrates with Python's standard `logging` module
