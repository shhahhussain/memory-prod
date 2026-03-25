# Agent Framework — Install & Hello World (Code-Ready Reference)

> For Claude Code: Use this as the authoritative reference when generating Agent Framework code for OrgMind.

## Installation

```bash
# Full install (includes all providers)
pip install agent-framework --pre

# Anthropic-specific (REQUIRED for OrgMind — we use Claude, not Azure OpenAI)
pip install agent-framework-anthropic --pre
```

**Package:** `agent-framework` v1.0.0rc5 (as of March 2026)
**Python:** >=3.10 (recommend 3.11+)
**Status:** Release Candidate (Beta)

## Sub-packages Available

| Package | Purpose |
|---------|---------|
| `agent-framework` | Full install — all providers |
| `agent-framework-core` | Core only (Azure OpenAI + OpenAI default) |
| `agent-framework-anthropic` | Anthropic/Claude provider |
| `agent-framework-azure-ai` | Azure AI provider |
| `agent-framework-copilotstudio` | Copilot Studio integration |
| `agent-framework-a2a` | Agent-to-Agent protocol |
| `agent-framework-devui` | Debug UI with OpenAI-compatible API server |

## Core Imports

```python
# Agent Framework core
from agent_framework import (
    Message,
    WorkflowEvent,
    TextReasoningContent,
    UsageContent,
)

# Anthropic provider (OrgMind uses this)
from agent_framework.anthropic import AnthropicClient

# Tools
from agent_framework import tool

# Workflows
from agent_framework.orchestrations import SequentialBuilder, ConcurrentBuilder
```

## Creating an Agent with Claude

### Basic (env vars)

```python
import asyncio
from agent_framework.anthropic import AnthropicClient

async def main():
    # Reads ANTHROPIC_API_KEY and ANTHROPIC_CHAT_MODEL_ID from env
    agent = AnthropicClient().as_agent(
        name="HelpfulAssistant",
        instructions="You are a helpful assistant.",
    )

    result = await agent.run("Hello, how can you help me?")
    print(result.text)

asyncio.run(main())
```

### Explicit Config

```python
agent = AnthropicClient(
    model_id="claude-sonnet-4-5-20250929",
    api_key="your-api-key-here",
).as_agent(
    name="HelpfulAssistant",
    instructions="You are a helpful assistant.",
)
```

### Environment Variables

```bash
ANTHROPIC_API_KEY="sk-ant-..."
ANTHROPIC_CHAT_MODEL_ID="claude-sonnet-4-5-20250929"
```

## Streaming Responses

```python
async for chunk in agent.run("Tell me a fun fact.", stream=True):
    if chunk.text:
        print(chunk.text, end="", flush=True)
```

## Extended Thinking (Reasoning)

```python
agent = AnthropicClient().as_agent(
    name="ReasoningAgent",
    instructions="You are a helpful agent.",
    default_options={
        "max_tokens": 20000,
        "thinking": {"type": "enabled", "budget_tokens": 10000}
    },
)
```

## Key API Surface

### `AnthropicClient`
```python
AnthropicClient(
    model_id: str | None = None,           # defaults to ANTHROPIC_CHAT_MODEL_ID env
    api_key: str | None = None,            # defaults to ANTHROPIC_API_KEY env
    anthropic_client: AsyncAnthropic | None = None,  # pass custom client
    additional_beta_flags: list[str] | None = None,
)
```

### `.as_agent()` method
```python
client.as_agent(
    name: str,
    instructions: str,
    tools: callable | list | None = None,
    max_tokens: int | None = None,
    default_options: dict | None = None,
) -> Agent
```

### `Agent.run()` method
```python
# Non-streaming
result = await agent.run("prompt") -> AgentRunResponse
result.text       # final text
result.messages   # list[ChatMessage]

# Streaming
async for chunk in agent.run("prompt", stream=True):
    chunk.text      # text delta
    chunk.contents  # list[Content]
```

## Adding Tools to an Agent

```python
from typing import Annotated
from agent_framework import tool

@tool(approval_mode="never_require")
def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is sunny."

agent = AnthropicClient().as_agent(
    name="WeatherAgent",
    instructions="You are a helpful weather assistant.",
    tools=get_weather,  # single tool
    # tools=[get_weather, another_tool],  # multiple tools
)
```

## MCP Tools (Supermemory integration path)

```python
client = AnthropicClient()
agent = client.as_agent(
    name="MemoryAgent",
    instructions="You are a helpful agent with memory.",
    tools=[
        client.get_mcp_tool(
            name="Supermemory MCP",
            url="https://mcp.supermemory.ai/mcp",
        ),
        client.get_web_search_tool(),
    ],
    max_tokens=20000,
)
```

## IMPORTANT NOTES FOR CODE GENERATION

1. **Agent Framework does NOT auto-load `.env` files.** You must call `load_dotenv()` manually.
2. **OrgMind uses Claude (Anthropic), NOT Azure OpenAI.** Always use `agent_framework.anthropic.AnthropicClient`.
3. **All agent operations are async.** Use `asyncio.run(main())` as entrypoint.
4. The `as_agent()` pattern is the canonical way to create agents — no class inheritance needed.
5. Model IDs: `claude-sonnet-4-5-20250929`, `claude-haiku-4-5`
6. Tools use `@tool` decorator with `Annotated` type hints for parameters.
