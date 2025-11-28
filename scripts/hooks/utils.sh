#!/usr/bin/env bash

# Utility functions for Claude Code hooks

# Load .env file if it exists
load_env() {
    local env_file="${1:-$HOME/guide/.env}"
    if [[ -f "$env_file" ]]; then
        # shellcheck disable=SC1090
        set -a
        source "$env_file"
        set +a
    fi
}

# Load environment on source
load_env

# Check if a command exists
require_command() {
    local cmd="$1"
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: $cmd is required but not installed" >&2
        return 1
    fi
    return 0
}

# Check for bold text in markdown content
# Usage: check_markdown_bold "$file_path" "$content"
# Returns: 1 if bold text found, 0 otherwise
check_markdown_bold() {
    local file_path="$1"
    local content="$2"

    # Only check markdown files
    if [[ ! "$file_path" =~ \.(md|markdown)$ ]]; then
        return 0
    fi

    # Skip check if no content provided
    if [[ -z "$content" ]]; then
        return 0
    fi

    # Check for bold text (**text** or __text__)
    # More robust: handles multiple occurrences and line breaks
    if echo "$content" | grep -E '\*\*[^*\n]+\*\*|__[^_\n]+__' >/dev/null 2>&1; then
        echo "❌ Bold text (**text** or __text__) is not allowed in markdown files" >&2
        # Show line numbers where bold text was found
        echo "$content" | grep -nE '\*\*[^*\n]+\*\*|__[^_\n]+__' | head -5 >&2
        return 1
    fi

    return 0
}

# Format error message with nice borders
format_error() {
    local title="$1"
    local message="$2"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
    echo "🚫 $title" >&2
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
    if [[ -n "$message" ]]; then
        echo "$message" >&2
    fi
}

# Format success message
format_success() {
    echo "✓ $1"
}

# Format warning message
format_warning() {
    echo "⚠ $1" >&2
}
