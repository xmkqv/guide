# Claude Code Hooks

PostToolUse auto-formatter — mirrors VSCode format-on-save.

## on-change.sh

Formats files after Edit/Write operations. Always exits 0 (best-effort, never blocks).

### Formatter Map

| Extensions | Tool | Command |
|---|---|---|
| ts tsx js jsx mjs cjs html css graphql vue svelte astro json jsonc | Biome | `biome format --write` |
| py | Ruff | `ruff format` |
| md markdown | markdownlint | `markdownlint --fix` |
| sh bash | shfmt | `shfmt -i 2 -ci -bn -sr -w` |
| sql | sql-formatter | `sql-formatter -l postgresql --fix` |

### Config resolution

- Biome: `--config-path="$CLAUDE_PROJECT_DIR/guides/configs"` (explicit)
- Ruff: auto-discovers ruff.toml / pyproject.toml (walks up)
- markdownlint: `-c "$CLAUDE_PROJECT_DIR/guides/configs/.markdownlint.json"` (explicit)
- shfmt: flags inline (mirrors VSCode `shellformat.flag`)
- sql-formatter: dialect flag inline

### Behavior

- Skips silently if formatter not installed
- Suppresses stderr (no noise in transcript)
- Skips if file_path missing or file doesn't exist

### Hook registration

In `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/guides/configs/claude/hooks/on-change.sh"
          }
        ]
      }
    ]
  }
}
```

### Dependencies

- Required: jq
- Formatters: biome, ruff, markdownlint, shfmt, sql-formatter (each optional)

## utils.sh

Shared utilities.

- `load_env(path)` — loads .env file (default: ~/guide/.env)
- `require_command(cmd)` — checks command exists, returns 1 if missing
