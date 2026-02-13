#!/usr/bin/env bash
set -euo pipefail

# PostToolUse auto-formatter: mirrors VSCode format-on-save behavior.
# Runs the appropriate formatter based on file extension after Edit/Write.
# Always exits 0 — formatting is best-effort, never blocks.

# Resolve config directory (biome.json, .markdownlint.json live here)
CONFIG_DIR="${CLAUDE_PROJECT_DIR:-.}/guides/configs"

# Read hook data from stdin
hook_data=$(cat)

# Extract file path
file_path=$(echo "$hook_data" | jq -r '.tool_input.file_path // empty')

# No file path or file doesn't exist — nothing to format
if [[ -z "$file_path" || ! -f "$file_path" ]]; then
  exit 0
fi

ext="${file_path##*.}"

case "$ext" in
  # Biome: JS/TS, HTML, CSS, GraphQL, Vue, Svelte, Astro, JSON
  ts | tsx | js | jsx | mjs | cjs | html | css | graphql | vue | svelte | astro | json | jsonc)
    command -v biome > /dev/null 2>&1 \
      && biome format --write --config-path="$CONFIG_DIR" "$file_path" 2> /dev/null
    ;;
  # Ruff: Python (auto-discovers ruff.toml / pyproject.toml)
  py)
    command -v ruff > /dev/null 2>&1 \
      && ruff format "$file_path" 2> /dev/null
    ;;
  # markdownlint: Markdown
  md | markdown)
    command -v markdownlint > /dev/null 2>&1 \
      && markdownlint --fix -c "$CONFIG_DIR/.markdownlint.json" "$file_path" 2> /dev/null
    ;;
  # shfmt: Shell scripts (flags mirror VSCode shellformat.flag)
  sh | bash)
    command -v shfmt > /dev/null 2>&1 \
      && shfmt -i 2 -ci -bn -sr -w "$file_path" 2> /dev/null
    ;;
  # sql-formatter: SQL (PostgreSQL dialect)
  sql)
    command -v sql-formatter > /dev/null 2>&1 \
      && sql-formatter -l postgresql --fix "$file_path" 2> /dev/null
    ;;
esac

exit 0
