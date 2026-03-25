# Retry & Circuit Breaker (Code-Ready Reference)

> For Claude Code: Resilience patterns for external API calls.

## Installation

```bash
pip install tenacity
```

## Retry with Exponential Backoff

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
)
async def call_supermemory_search(query: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post("https://api.supermemory.ai/v4/search", ...)
        response.raise_for_status()
        return response.json()
```

## Simple Circuit Breaker

```python
import time

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed=normal, open=blocking, half_open=testing

    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "open"
            raise
```

## IMPORTANT NOTES
1. Use `tenacity` for retry logic — don't write your own
2. Circuit breaker prevents cascading failures
3. Apply to: Supermemory API, LLM calls, NocoDB calls
4. Don't retry on 4xx errors (client errors) — only 5xx and timeouts
