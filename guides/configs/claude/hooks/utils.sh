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
