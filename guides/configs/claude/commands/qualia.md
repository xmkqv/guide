---
description: Run one qualia dispatcher cycle against Linear — pick one assigned issue, read its thread, dispatch a fresh-context sub-agent to act
---

Run one cycle of the qualia loop. See docs/qualia.md for the underlying concept.

## 1. Find an issue to work

Query Linear via MCP:

- assignee: me
- workflow state ∈ {Todo, In Review}
- order by updatedAt desc
- limit 10, then pick the **single oldest-updated** from that set (round-robin feel)

If no issues match, report `no work` and exit.

## 2. Read the thread

For the picked issue, fetch:

- title, body, workflow state, labels
- full comment thread, oldest first

## 3. Classify

From the thread, determine the cycle stage:

| Stage | Signal |
|---|---|
| **start** | no agent comments (no comment starts with `[propose]`, `[progress]`, `[blocked]`, `[done]`) |
| **iterate** | the newest comment is from a human (untagged) and is newer than the newest agent comment |
| **wait** | the newest comment is an agent comment with tag `[propose]` or `[blocked]` and no newer human comment |
| **finish** | state is `In Review` and thread ends with `[done]` — move to Done and exit |

If **wait**, report `waiting for human on issue <id>` and exit (no work to do).

## 4. Dispatch sub-agent (fresh context)

Spawn a Task sub-agent with `subagent_type: general-purpose`. The sub-agent prompt must include:

- the issue title + body + full comment thread (verbatim)
- the classified stage (`start` | `iterate` | `finish`)
- this instruction block:

> You have one issue to process. Read the title, body, and thread above.
>
> - **start**: read the request, plan the approach, do bounded work (~20 min of agent time), post a comment starting with `[propose]` describing what you did and what you need decided, then stop. Do NOT transition state.
> - **iterate**: the human left feedback in the newest comment. Act on it. Post a `[progress]` comment summarising what changed, or `[blocked]` if you need more info, or `[done]` if feedback says ship it — in which case also transition the issue to `In Review`.
> - **finish**: post a `[done]` comment and transition the issue to `Done`.
>
> Every comment you post MUST start with exactly one tag: `[propose]`, `[progress]`, `[blocked]`, or `[done]`.
>
> Use the Linear MCP to read the issue, post the comment, and update state. Do not touch other issues.

## 5. Report

After the sub-agent returns, report:

- which issue was processed (id + title)
- what stage it was in
- what the sub-agent did (one line)

## Conventions reference

**Agent comment tags** (first token of comment body):

- `[propose]` — proposed approach, awaiting human direction
- `[progress]` — checkpoint, still working (rare — usually one shot per cycle)
- `[blocked]` — need human input
- `[done]` — work complete for this issue

**Human comments** — untagged, free-form. Treated as hints/direction.

**Workflow states**:

- `Todo` → agent picks up
- `In Progress` → agent working (cycle in flight)
- `In Review` → human action expected
- `Done` → closed

**Scheduled invocation**: this command is designed to be run every 30 min via `/schedule`. Each run processes one issue. Set up the cron once the command is validated manually.
