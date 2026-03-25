# Topic: TASKR Agent — Asana Integration & Multi-Turn State

**Time:** 20-30 min
**Goal:** Port TASKR's task creation and pending-state handling

---

## What to Search
- "Asana API Python create task"
- "pip install asana"
- "Asana API project tasks"

## Install
```bash
pip install asana
```

## What TASKR Does (from POC)
1. Receives task creation request from MINDY
2. Parses natural language → title, owner, due date, project, priority
3. If required fields missing → stores pending state, asks MINDY to clarify
4. Searches Supermemory for execution context
5. Creates task in Asana (or returns mock if Asana unavailable)
6. Returns: task object, next steps, PM link, confidence

## Asana API
```python
import asana

asana_client = asana.Client.access_token(settings.asana_api_key)

async def create_asana_task(title: str, project_id: str, assignee: str = None, due_on: str = None, notes: str = "") -> dict:
    try:
        result = asana_client.tasks.create_task({
            "name": title,
            "projects": [project_id],
            "assignee": assignee,
            "due_on": due_on,  # "2026-04-15"
            "notes": notes,
        })
        return {
            "ok": True,
            "task_id": result["gid"],
            "url": f"https://app.asana.com/0/{project_id}/{result['gid']}",
        }
    except Exception as e:
        # Mock fallback
        return {
            "ok": False,
            "mock": True,
            "task_id": f"mock_{hash(title) & 0xFFFF}",
            "error": str(e),
        }
```

## Multi-Turn Pending State
When user says "create a task for the Nike campaign" but doesn't specify assignee/due:

```python
from pydantic import BaseModel

class PendingTask(BaseModel):
    title: str | None = None
    owner: str | None = None
    due_date: str | None = None
    project: str | None = None
    priority: str | None = None

    @property
    def is_complete(self) -> bool:
        return bool(self.title)  # Title is the only hard requirement

    @property
    def missing_fields(self) -> list[str]:
        fields = []
        if not self.title: fields.append("title")
        if not self.owner: fields.append("owner/assignee")
        if not self.due_date: fields.append("due date")
        return fields
```

Store pending state in thread context so follow-up messages can fill in missing fields.

## What to Understand
- [ ] Asana client is synchronous — may need `asyncio.to_thread()` wrapper
- [ ] Mock fallback when Asana is unavailable (POC pattern)
- [ ] Multi-turn: if fields missing, ask for clarification via MINDY
- [ ] Pending task state persists in thread context (not global)
- [ ] POC stored `awaiting_details` flag in agent context
