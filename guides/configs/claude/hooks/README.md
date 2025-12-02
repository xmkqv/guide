# Claude Code Hooks

PreToolUse hooks for validating files before Edit/Write operations.

## Exit Code Behavior

Claude Code hooks use exit codes to control operation flow:

| Exit Code | Behavior | When to Use |
|-----------|----------|-------------|
| `0` | **Allow** - Tool executes normally | All validations passed |
| `1` | **Warn** - Shows warning but tool still executes | Non-critical issues (not used in this hook) |
| `2` | **Block** - Tool does not execute, operation cancelled | Validation failures or infrastructure errors |

## on-change.sh

Validates files before Claude saves them.

### What it does

- **Markdown validation:** Blocks bold text (`**text**` or `__text__`)
- **JavaScript/TypeScript:** Runs biome linter
- **Python:** Runs ruff and pyright
- **Markdown:** Runs markdownlint
- **Shell scripts:** Runs shellcheck

### Configuration

*_CONFIG_PATH set in .env.

### How it works

1. Hook receives JSON via stdin from Claude Code
2. Extracts file path and tool name (Edit or Write)
3. For Edit operations: Only validates markdown bold text
4. For Write operations: Runs all applicable linters
5. Returns exit code:
   - `exit 0` if all checks pass → Claude saves the file
   - `exit 2` if any issues found → Claude blocks the save

### Blocking behavior

The hook blocks (exit 2) on:

- Markdown bold text detected
- Any linter errors (biome, ruff, pyright, markdownlint, shellcheck)
- Missing jq command
- Failed to create temp file
- Any other infrastructure errors

This ensures validation infrastructure is working before allowing saves.

### Hook data structure

Claude Code passes JSON via stdin:

```json
{
  "session_id": "abc123",
  "hook_event_name": "PreToolUse",
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/path/to/file.js",
    "new_string": "const x = 1",
    "old_string": "var x = 1"
  },
  "tool_use_id": "toolu_01ABC123",
  "cwd": "/Users/m/project"
}
```

For Write operations, `tool_input.content` contains the full file content instead of `old_string`/`new_string`.

### Troubleshooting

If saves are unexpectedly blocked:

1. Check stderr output - linters output directly
2. Verify linter is installed: `which biome ruff pyright markdownlint shellcheck`
3. Check config paths in `~/guide/.env`
4. Verify configs exist at specified paths
5. Run linter manually: `biome check file.js`

### Dependencies

- **Required:** jq
- **Optional:** biome, ruff, pyright, markdownlint, shellcheck

If a linter is not installed, the hook will fail and block the save. Remove linter blocks from `on-change.sh` if you don't want that linter.

## utils.sh

Shared utilities for hooks.

### Functions

- `load_env()` - Loads ~/guide/.env automatically when sourced
- `require_command(cmd)` - Checks if command exists, exits 2 if missing
- `check_markdown_bold(path, content)` - Validates no bold text in markdown
- `format_error(title, message)` - Formats error messages with borders
- `format_success(message)` - Formats success messages
- `format_warning(message)` - Formats warning messages

### Usage

```bash
#!/usr/bin/env bash
set -euo pipefail

# Source utilities (automatically loads .env)
source "$SCRIPT_DIR/utils.sh"

# Check for required commands
require_command jq || exit 2

# Validate markdown
if ! check_markdown_bold "$file_path" "$content"; then
    exit 2
fi
```
