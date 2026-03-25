# Agent Framework — Concurrent Fan-Out (Code-Ready Reference)

> For Claude Code: Use this when building MINDY's parallel dispatch to FINDR/TASKR/CAMPA.

## Import

```python
from agent_framework.orchestrations import ConcurrentBuilder
from agent_framework import Message, WorkflowEvent, AgentExecutorResponse
from agent_framework.anthropic import AnthropicClient
```

## Basic Concurrent Workflow

All agents run in **parallel** on the same input. Results are aggregated.

```python
from typing import cast
from agent_framework.orchestrations import ConcurrentBuilder
from agent_framework.anthropic import AnthropicClient
from agent_framework import Message

client = AnthropicClient()

researcher = client.as_agent(
    instructions="You're an expert market researcher. Provide concise, factual insights.",
    name="researcher",
)

marketer = client.as_agent(
    instructions="You're a creative marketing strategist. Craft compelling messaging.",
    name="marketer",
)

legal = client.as_agent(
    instructions="You're a cautious legal reviewer. Highlight constraints and concerns.",
    name="legal",
)

# All 3 agents run simultaneously
workflow = ConcurrentBuilder(participants=[researcher, marketer, legal]).build()

output_data: list[Message] | None = None
async for event in workflow.run("Launch a new budget-friendly electric bike.", stream=True):
    if event.type == "output":
        output_data = event.data

if output_data:
    messages: list[Message] = cast(list[Message], output_data)
    for msg in messages:
        name = msg.author_name or "user"
        print(f"[{name}]: {msg.text}")
```

## Custom Aggregator (THIS IS KEY FOR MINDY)

By default, concurrent just collects all responses. With a custom aggregator, MINDY can **synthesize** results from multiple agents:

```python
from agent_framework import AgentExecutorResponse
from agent_framework.anthropic import AnthropicClient

client = AnthropicClient()

# Summarizer agent for aggregation
summarizer_agent = client.as_agent(
    instructions=(
        "You consolidate multiple domain expert outputs into one cohesive, "
        "concise summary with clear takeaways. Keep it under 200 words."
    ),
    name="summarizer",
)

async def summarize_results(results: list[AgentExecutorResponse]) -> str:
    """Custom aggregator — synthesize all agent outputs into one response."""
    expert_sections: list[str] = []
    for r in results:
        try:
            messages = getattr(r.agent_response, "messages", [])
            final_text = messages[-1].text if messages and hasattr(messages[-1], "text") else "(no content)"
            expert_sections.append(f"{r.executor_id}:\n{final_text}")
        except Exception as e:
            expert_sections.append(f"{r.executor_id}: (error: {type(e).__name__}: {e})")

    prompt = "\n\n".join(expert_sections)
    response = await summarizer_agent.run(prompt)
    return response.messages[-1].text if response.messages else ""

# Build with custom aggregator
workflow = (
    ConcurrentBuilder(participants=[researcher, marketer, legal])
    .with_aggregator(summarize_results)
    .build()
)

output = None
async for event in workflow.run("Launch a new electric bike.", stream=True):
    if event.type == "output":
        output = event.data

if output:
    print(output)  # Single synthesized response
```

## Custom Agent Executors (Advanced)

Wrap agents with custom pre/post processing logic:

```python
from agent_framework import (
    AgentExecutorRequest,
    AgentExecutorResponse,
    Executor,
    WorkflowContext,
    handler,
)

class ResearcherExec(Executor):
    def __init__(self, chat_client: AnthropicClient, id: str = "researcher"):
        self.agent = chat_client.as_agent(
            instructions="You're an expert researcher. Provide concise, factual insights.",
            name=id,
        )
        super().__init__(id=id)

    @handler
    async def run(self, request: AgentExecutorRequest, ctx: WorkflowContext[AgentExecutorResponse]) -> None:
        response = await self.agent.run(request.messages)
        full_conversation = list(request.messages) + list(response.messages)
        await ctx.send_message(AgentExecutorResponse(self.id, response, full_conversation=full_conversation))
```

## ConcurrentBuilder API

```python
ConcurrentBuilder(
    participants: list[Agent | Executor],
)
    .with_aggregator(callable)          # custom result synthesis function
    .register_aggregator(factory)       # factory pattern
    .with_checkpointing(storage)        # persist state
    .build() -> Workflow
```

## OrgMind Application — MINDY Fan-Out Pattern

```python
client = AnthropicClient()

# Specialist agents
findr = client.as_agent(name="FINDR", instructions="You are a research specialist...")
taskr = client.as_agent(name="TASKR", instructions="You are a task management specialist...")
campa = client.as_agent(name="CAMPA", instructions="You are a campaign drafting specialist...")

# MINDY synthesizes the results
async def mindy_aggregator(results: list[AgentExecutorResponse]) -> str:
    """Synthesize results — tolerates partial failures."""
    sections = []
    for r in results:
        try:
            text = r.agent_response.messages[-1].text
            sections.append(f"[{r.executor_id}]: {text}")
        except Exception:
            continue  # Skip failed agents, use what we have

    synthesizer = client.as_agent(
        name="MINDY",
        instructions="Synthesize these agent results into a coherent response for the user.",
    )
    response = await synthesizer.run("\n\n".join(sections))
    return response.messages[-1].text

workflow = (
    ConcurrentBuilder(participants=[findr, taskr, campa])
    .with_aggregator(mindy_aggregator)
    .build()
)
```

## Key Concepts

- **Parallel Execution**: All agents run simultaneously on the same input
- **Default Aggregation**: Collects all responses into `list[Message]`
- **Custom Aggregator**: Override to synthesize/filter results (CRITICAL for MINDY)
- **Partial Failure Tolerance**: Handle individual agent failures in aggregator
- **Flexible Participants**: Mix agents and custom executors
