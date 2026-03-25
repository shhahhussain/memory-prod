# Topic: Thread Context Persistence (Slack → Teams Migration)

**Time:** 20 min
**Goal:** Port Slack's thread context tables to Teams conversation IDs

---

## What to Search
- "Teams bot conversation.id threading"
- "Teams conversation state persistence PostgreSQL"
- "M365 Agents SDK conversation reference"

## POC Tables (Slack)
```sql
slack_thread_context    -- shared per-thread JSON
slack_agent_context     -- per-agent per-thread JSON
slack_event_dedupe      -- prevent duplicate event processing
```

## New Tables (Teams)
```sql
CREATE TABLE teams_thread_context (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT NOT NULL UNIQUE,  -- Teams conversation.id
    shared_context JSONB DEFAULT '{}',
    last_user_text TEXT,
    last_intent TEXT,
    last_topic TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE teams_agent_context (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,              -- MINDY, FINDR, TASKR, CAMPA
    agent_context JSONB DEFAULT '{}',
    last_reply_text TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(conversation_id, agent_name)
);

CREATE TABLE teams_event_dedupe (
    id SERIAL PRIMARY KEY,
    activity_id TEXT NOT NULL UNIQUE,      -- Teams activity.id
    processed_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Context Service
```python
class ThreadContextService:
    def __init__(self, db: Database):
        self.db = db

    async def get(self, conversation_id: str) -> dict:
        shared = await self.db.fetchrow(
            "SELECT * FROM teams_thread_context WHERE conversation_id = $1",
            conversation_id
        )
        agents = await self.db.fetch(
            "SELECT * FROM teams_agent_context WHERE conversation_id = $1",
            conversation_id
        )
        return {
            "shared": dict(shared) if shared else {},
            "agents": {a["agent_name"]: dict(a) for a in agents},
        }

    async def upsert(self, conversation_id: str, shared_patch: dict, agent_name: str = None, agent_patch: dict = None):
        await self.db.execute("""
            INSERT INTO teams_thread_context (conversation_id, shared_context, updated_at)
            VALUES ($1, $2, NOW())
            ON CONFLICT (conversation_id) DO UPDATE
            SET shared_context = teams_thread_context.shared_context || $2, updated_at = NOW()
        """, conversation_id, json.dumps(shared_patch))

        if agent_name and agent_patch:
            await self.db.execute("""
                INSERT INTO teams_agent_context (conversation_id, agent_name, agent_context, updated_at)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (conversation_id, agent_name) DO UPDATE
                SET agent_context = teams_agent_context.agent_context || $3, updated_at = NOW()
            """, conversation_id, agent_name, json.dumps(agent_patch))
```

## What to Understand
- [ ] Teams `conversation.id` replaces Slack `team_id + thread_ts`
- [ ] JSONB `||` operator merges patches (PostgreSQL feature)
- [ ] Upsert pattern: INSERT ... ON CONFLICT DO UPDATE
- [ ] Context enables follow-up detection (same conversation = continuation)
- [ ] Event dedupe prevents processing same Teams activity twice
