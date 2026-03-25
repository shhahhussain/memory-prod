# Agent Framework — Sequential Workflows (Code-Ready Reference)

> For Claude Code: Use this when building MINDY's sequential processing chains.

## Import

```python
from agent_framework.orchestrations import SequentialBuilder
from agent_framework import Message, WorkflowEvent
from agent_framework.anthropic import AnthropicClient
```

## Basic Sequential Workflow

Agents run in order. Each agent sees the FULL conversation history from all previous agents.

```python
import os
from typing import cast
from agent_framework.orchestrations import SequentialBuilder
from agent_framework.anthropic import AnthropicClient
from agent_framework import Message, WorkflowEvent

client = AnthropicClient()

writer = client.as_agent(
    instructions="You are a concise copywriter. Provide a single, punchy marketing sentence.",
    name="writer",
)

reviewer = client.as_agent(
    instructions="You are a thoughtful reviewer. Give brief feedback on the previous assistant message.",
    name="reviewer",
)

# Build: writer -> reviewer
workflow = SequentialBuilder(participants=[writer, reviewer]).build()

# Run with streaming
outputs: list[list[Message]] = []
async for event in workflow.run("Write a tagline for a budget-friendly eBike.", stream=True):
    if event.type == "output":
        outputs.append(cast(list[Message], event.data))

# Access final conversation
if outputs:
    messages: list[Message] = outputs[-1]
    for msg in messages:
        name = msg.author_name or msg.role
        print(f"[{name}]: {msg.text}")
```

## Custom Executor in Sequential Pipeline

When you need custom logic (not LLM) between agents:

```python
from agent_framework import (
    AgentExecutorResponse,
    Executor,
    WorkflowContext,
    handler,
    Message,
)

class Summarizer(Executor):
    """Custom non-LLM executor that processes conversation."""

    @handler
    async def summarize(
        self,
        agent_response: AgentExecutorResponse,
        ctx: WorkflowContext[list[Message]]
    ) -> None:
        if not agent_response.full_conversation:
            await ctx.send_message([Message("assistant", ["No conversation to summarize."])])
            return

        users = sum(1 for m in agent_response.full_conversation if m.role == "user")
        assistants = sum(1 for m in agent_response.full_conversation if m.role == "assistant")
        summary = Message("assistant", [f"Summary -> users:{users} assistants:{assistants}"])
        await ctx.send_message(list(agent_response.full_conversation) + [summary])

# Build: content_agent -> summarizer
summarizer = Summarizer(id="summarizer")
workflow = SequentialBuilder(participants=[content_agent, summarizer]).build()
```

## Function-Based Executor (Simpler)

```python
from agent_framework import executor, WorkflowContext

@executor(id="formatter")
async def format_output(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.send_message(text.upper())
```

## SequentialBuilder API

```python
SequentialBuilder(
    participants: list[Agent | Executor],  # ordered list
)
    .with_checkpointing(storage)          # optional — persist state
    .with_request_info(agents=[...])      # optional
    .build() -> Workflow
```

## Workflow.run() API

```python
# Non-streaming
result = await workflow.run(
    message: str | WorkflowStartMessage,
    checkpoint_id: str | None = None,
    checkpoint_storage: CheckpointStorage | None = None,
) -> WorkflowRunResult

# Streaming
async for event in workflow.run(message, stream=True):
    event.type   # "output", "started", "status", "failed", etc.
    event.data   # event payload
```

## Key Concepts

- **Shared Context**: Full conversation history passed to each next agent
- **Order Matters**: Agents execute strictly in `participants` list order
- **Mixed Participants**: Can combine agents and custom `Executor` subclasses
- **Streaming**: Use `stream=True` in `.run()` for real-time events

## OrgMind Application

Use sequential for:
- Intent classification -> agent dispatch -> response synthesis
- FINDR search -> conflict check -> response formatting
- Draft generation (CAMPA) -> review -> final output
