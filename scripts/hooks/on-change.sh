#!/usr/bin/env bash
set -euo pipefail

# Source utility functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./utils.sh
source "$SCRIPT_DIR/utils.sh"

# Check for required tools
require_command jq || exit 2

# Read hook data from stdin
hook_data=$(cat)

# Extract file path and tool name
file_path=$(echo "$hook_data" | jq -r '.tool_input.file_path // empty')
tool_name=$(echo "$hook_data" | jq -r '.tool_name // empty')

# If no file path, allow operation
if [[ -z "$file_path" ]]; then
    exit 0
fi

# Get file extension and filename
ext="${file_path##*.}"
filename=$(basename "$file_path")

# Track if any errors/warnings found
has_issues=0

# Extract Claude's changes based on tool type
claude_changes=""
full_content=""

if [[ "$tool_name" == "Edit" ]]; then
    # For Edit: only check the new_string (Claude's change)
    claude_changes=$(echo "$hook_data" | jq -r '.tool_input.new_string // empty')
    # For linters, we need to read the current file and apply the edit
    # For now, skip linter validation on Edit operations
    full_content=""
elif [[ "$tool_name" == "Write" ]]; then
    # For Write: check the full content being written
    full_content=$(echo "$hook_data" | jq -r '.tool_input.content // empty')
    claude_changes="$full_content"
fi

# Check for markdown bold text in Claude's changes
if ! check_markdown_bold "$file_path" "$claude_changes"; then
    has_issues=1
fi

# Skip linter validation if we don't have full content (Edit operations)
if [[ -z "$full_content" ]]; then
    if [[ $has_issues -eq 1 ]]; then
        exit 2
    fi
    exit 0
fi

# Create temp file for linter validation (Write operations only)
temp_file=$(mktemp "/tmp/${filename}.XXXXXX")
trap 'rm -f "$temp_file"' EXIT

# Write content to temp file with error checking
if ! echo "$full_content" > "$temp_file"; then
    echo "Error: Failed to write temp file" >&2
    exit 2
fi

# JavaScript/TypeScript files - use biome
if [[ "$ext" =~ ^(js|jsx|ts|tsx|mjs|cjs)$ ]]; then
    if [[ -n "${BIOME_CONFIG_PATH:-}" ]]; then
        biome check --config-path="$BIOME_CONFIG_PATH" "$temp_file" || has_issues=1
    else
        biome check "$temp_file" || has_issues=1
    fi
fi

# Python files - use ruff and pyright
if [[ "$ext" == "py" ]]; then
    if [[ -n "${RUFF_CONFIG_PATH:-}" && -f "$RUFF_CONFIG_PATH" ]]; then
        ruff check --config="$RUFF_CONFIG_PATH" "$temp_file" || has_issues=1
    else
        ruff check "$temp_file" || has_issues=1
    fi

    if [[ -n "${PYRIGHT_CONFIG_PATH:-}" && -f "$PYRIGHT_CONFIG_PATH" ]]; then
        pyright --project="$(dirname "$PYRIGHT_CONFIG_PATH")" "$temp_file" || has_issues=1
    else
        pyright "$temp_file" || has_issues=1
    fi
fi

# Markdown files - use markdownlint
if [[ "$ext" =~ ^(md|markdown)$ ]]; then
    if [[ -n "${MARKDOWNLINT_CONFIG_PATH:-}" && -f "$MARKDOWNLINT_CONFIG_PATH" ]]; then
        markdownlint -c "$MARKDOWNLINT_CONFIG_PATH" "$temp_file" || has_issues=1
    else
        markdownlint "$temp_file" || has_issues=1
    fi
fi

# Shell scripts - use shellcheck
if [[ "$ext" == "sh" ]]; then
    shellcheck "$temp_file" || has_issues=1
fi

# If issues found, block the operation
if [[ $has_issues -eq 1 ]]; then
    echo "" >&2
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
    echo "❌ File save blocked due to linting errors above." >&2
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
    exit 2
fi

# All checks passed
exit 0
