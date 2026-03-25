# TASKR Agent Port (Code-Ready Reference)

> For Claude Code: Port TASKR (task management) from n8n to Python.

## TASKR's Role

TASKR manages tasks and project tracking. In the POC, this was planned but not fully implemented. For production, integrate with the client's project management tool.

## Implementation

```python
from agent_framework.anthropic import AnthropicClient
from agent_framework import tool
from typing import Annotated
import httpx

# NocoDB API for task management (client uses NocoDB)
NOCODB_BASE_URL = "https://nocodb.example.com/api/v2"

@tool(approval_mode="never_require")
async def list_tasks(
    status: Annotated[str, "Filter by status: open, in_progress, done, all"] = "open",
    assignee: Annotated[str, "Filter by assignee name (optional)"] = "",
) -> str:
    # Query NocoDB for tasks
    filters = {}
    if status != "all":
        filters["Status"] = status
    if assignee:
        filters["Assignee"] = assignee

    async with httpx.AsyncClient() as http:
        response = await http.get(
            f"{NOCODB_BASE_URL}/tables/tasks/records",
            headers={"xc-auth": settings.nocodb_api_key},
            params={"where": str(filters)} if filters else {},
        )
        tasks = response.json().get("list", [])

    if not tasks:
        return "No tasks found."

    return "\n".join(f"- [{t['Status']}] {t['Title']} (assigned: {t.get('Assignee', 'unassigned')})" for t in tasks)

@tool(approval_mode="never_require")
async def create_task(
    title: Annotated[str, "Task title"],
    description: Annotated[str, "Task description"] = "",
    assignee: Annotated[str, "Assignee name"] = "",
    priority: Annotated[str, "Priority: low, medium, high"] = "medium",
) -> str:
    async with httpx.AsyncClient() as http:
        response = await http.post(
            f"{NOCODB_BASE_URL}/tables/tasks/records",
            headers={"xc-auth": settings.nocodb_api_key},
            json={"Title": title, "Description": description, "Assignee": assignee, "Priority": priority, "Status": "open"},
        )
        return f"Task created: {title}"

def create_taskr(anthropic_client: AnthropicClient) -> "Agent":
    return anthropic_client.as_agent(
        name="TASKR",
        instructions="""You are TASKR, OrgMind's task management specialist.
Your role: Create, update, list, and manage tasks and action items.
Always confirm task details before creating.""",
        tools=[list_tasks, create_task],
    )
```

## IMPORTANT NOTES
1. Client uses NocoDB (already provisioned) for task management
2. NocoDB has a REST API — authenticate with `xc-auth` header
3. Confirm task details before creating (prevent accidental creation)
4. TASKR tools need the NocoDB API key from settings
