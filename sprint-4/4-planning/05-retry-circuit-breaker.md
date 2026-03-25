# Topic: Retry & Circuit Breaker for External Services

**Time:** 15 min
**Goal:** Handle Supermemory/Asana/GDocs being temporarily down

---

## What to Search
- "tenacity retry Python async"
- "circuit breaker pattern Python"

## Install
```bash
pip install tenacity
```

## Retry with Backoff
```python
import tenacity
import httpx

@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
    retry=tenacity.retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    before_sleep=tenacity.before_sleep_log(logger, logging.WARNING),
)
async def search_memory(query: str) -> list:
    return await supermemory.search.documents(q=query, ...)
```

## Simple Circuit Breaker
```python
import time

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failures = 0
        self.threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = 0
        self.state = "closed"  # closed = normal, open = failing

    def can_execute(self) -> bool:
        if self.state == "closed":
            return True
        if time.time() - self.last_failure_time > self.reset_timeout:
            self.state = "half-open"
            return True  # Try one request
        return False

    def record_success(self):
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.threshold:
            self.state = "open"

supermemory_breaker = CircuitBreaker()
asana_breaker = CircuitBreaker()
```

## What to Understand
- [ ] Retry handles transient failures (timeout, connection reset)
- [ ] Exponential backoff: 1s → 2s → 4s between retries
- [ ] Circuit breaker prevents hammering a down service
- [ ] After 5 failures, circuit opens → instant fail for 60s → then try one request
- [ ] POC had mock fallbacks for Asana/GDocs — keep those AND add retry/breaker
