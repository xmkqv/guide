# Special Agents

Task-specific Claude agents with isolated MCP configurations.

## Structure

```txt
specials/{name}/
  .mcp.json                      # MCP server config
  .claude/agents/{name}.md       # Subagent definition
  ...                            # Agent-specific files
```

## Invocation

```bash
just agent {name} "{task}" [workdir]
```

- `name`: Agent directory name
- `task`: Natural language task description
- `workdir`: Project directory for context (default: current dir)

## Subagent Definition

File: `.claude/agents/{name}.md`

```yaml
---
name: {name}
description: Brief description of agent purpose
tools: mcp__{server}           # MCP server name (no wildcards)
permissionMode: acceptEdits    # Or: default, bypassPermissions
---

Instructions for the agent...
```

## MCP Configuration

File: `.mcp.json`

```json
{
  "mcpServers": {
    "{server}": {
      "command": "npx",
      "args": ["-y", "@scope/mcp-package"],
      "env": {}
    }
  }
}
```

## Permission Modes

- `default`: Prompt for each tool use
- `acceptEdits`: Auto-approve file edits
- `bypassPermissions`: Auto-approve all tools

## Tool Permissions

Use MCP server name only (no wildcards):

```yaml
tools: mcp__likec4           # All tools from likec4 server
tools: mcp__github           # All tools from github server
tools: Read, Write, mcp__x   # Multiple tools
```

Omit `tools` to inherit all available tools.

## Example

```bash
just agent gen-diagram "diagram the system in README.md"
```

Runs the gen-diagram agent with access to LikeC4 MCP tools.
