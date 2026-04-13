#!/bin/bash
set -euo pipefail

# Mac Cleanup Script
# Cleans caches, logs, temp files, and development artifacts
# Safe to run regularly - only touches regenerable caches

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

TOTAL_SAVED=0
DRY_RUN=false

[[ "${1:-}" == "-n" || "${1:-}" == "--dry-run" ]] && DRY_RUN=true

print_section() { echo -e "\n${BLUE}==>${NC} ${1}"; }
print_success() { echo -e "${GREEN}✓${NC} ${1}"; }
print_warning() { echo -e "${YELLOW}!${NC} ${1}"; }

get_size() {
  [[ -e "$1" ]] && du -sk "$1" 2> /dev/null | cut -f1 || echo "0"
}

format_size() {
  local size=$1
  if [[ $size -ge 1048576 ]]; then
    echo "$((size / 1048576)).$((size % 1048576 * 100 / 1048576)) GB"
  elif [[ $size -ge 1024 ]]; then
    echo "$((size / 1024)).$((size % 1024 * 100 / 1024)) MB"
  else
    echo "${size} KB"
  fi
}

is_running() {
  pgrep -xq "$1" 2> /dev/null
}

clean_dir() {
  local path=$1
  local desc=$2
  local min_kb=${3:-1024}

  [[ ! -e "$path" ]] && return 0
  [[ -z "$path" || "$path" == "/" || "$path" == "$HOME" ]] && return 0

  local before
  before=$(get_size "$path")
  [[ $before -lt $min_kb ]] && return 0

  if $DRY_RUN; then
    print_success "[DRY] $desc: $(format_size "$before")"
    TOTAL_SAVED=$((TOTAL_SAVED + before))
    return 0
  fi

  if [[ -d "$path" ]]; then
    find "$path" -mindepth 1 -delete 2> /dev/null || true
  else
    rm -f "$path" 2> /dev/null || true
  fi

  local after
  after=$(get_size "$path")
  local saved=$((before - after))
  TOTAL_SAVED=$((TOTAL_SAVED + saved))
  [[ $saved -gt 0 ]] && print_success "$desc: $(format_size $saved)" || true
}

clean_cmd() {
  local cmd=$1
  local desc=$2

  if $DRY_RUN; then
    print_success "[DRY] $desc"
    return 0
  fi

  if eval "$cmd" 2> /dev/null; then
    print_success "$desc"
  fi
}

echo "======================================"
$DRY_RUN && echo "  Mac Cleanup - DRY RUN" || echo "  Mac Cleanup - Running..."
echo "======================================"

# ==================================================
# SYSTEM CACHES & LOGS
# ==================================================
print_section "System Caches & Logs"

for cache in "$HOME/Library/Caches"/*; do
  [[ -d "$cache" ]] && clean_dir "$cache" "$(basename "$cache")" 51200 || true
done

clean_dir "$HOME/Library/Logs" "System logs"
clean_dir "$HOME/Library/Logs/DiagnosticReports" "Crash reports"
clean_dir "$HOME/Library/Application Support/CrashReporter" "Crash reporter"

if [[ -d "/tmp" ]]; then
  before=$(get_size "/tmp")
  if ! $DRY_RUN; then
    find /tmp -type f -atime +3 -delete 2> /dev/null || true
  fi
  after=$(get_size "/tmp")
  saved=$((before - after))
  if [[ $saved -gt 0 ]]; then
    TOTAL_SAVED=$((TOTAL_SAVED + saved))
    print_success "Temp files: $(format_size $saved)"
  fi
fi

clean_dir "$HOME/.Trash" "Trash" 0

# ==================================================
# XDG CACHES
# ==================================================
print_section "XDG Caches"

# uv (Python package manager)
clean_dir "$HOME/.cache/uv/archive-v0" "uv package archive"
clean_dir "$HOME/.cache/uv/sdists-v9" "uv sdists"
clean_dir "$HOME/.cache/uv/simple-v16" "uv simple cache"
clean_dir "$HOME/.cache/uv/simple-v17" "uv simple cache v17"
clean_dir "$HOME/.cache/uv/wheels-v5" "uv wheels"

# bun
clean_dir "$HOME/.bun/install/cache" "bun install cache"

# Browser automation
clean_dir "$HOME/.cache/puppeteer" "Puppeteer browsers"
clean_dir "$HOME/.cache/ms-playwright" "Playwright browsers"

# Python tools
clean_dir "$HOME/.cache/pre-commit" "pre-commit"
clean_dir "$HOME/.cache/torch" "PyTorch cache"

# Node
clean_dir "$HOME/.cache/node" "Node cache"
clean_dir "$HOME/Library/Caches/node-gyp" "node-gyp"

# ==================================================
# ML CACHES (Warning Only)
# ==================================================
print_section "ML Caches"

if [[ -d "$HOME/.cache/huggingface" ]]; then
  hf_size=$(get_size "$HOME/.cache/huggingface")
  if [[ $hf_size -gt 5242880 ]]; then
    print_warning "Huggingface: $(format_size "$hf_size") - run 'huggingface-cli delete-cache'"
  fi
fi

if [[ -d "$HOME/.ollama/models" ]]; then
  ollama_size=$(get_size "$HOME/.ollama/models")
  if [[ $ollama_size -gt 5242880 ]]; then
    print_warning "Ollama models: $(format_size "$ollama_size") - run 'ollama rm <model>'"
  fi
fi

# ==================================================
# PACKAGE MANAGERS
# ==================================================
print_section "Package Managers"

if command -v brew &> /dev/null; then
  clean_cmd "brew cleanup -s && brew autoremove" "Homebrew"
  brew_cache=$(brew --cache 2> /dev/null)
  [[ -n "$brew_cache" ]] && clean_dir "$brew_cache" "Homebrew cache"
fi

# npm
clean_dir "$HOME/.npm/_cacache" "npm cache"
clean_dir "$HOME/.npm/_logs" "npm logs"

# yarn
if command -v yarn &> /dev/null; then
  yarn_cache=$(yarn cache dir 2> /dev/null)
  [[ -n "$yarn_cache" ]] && clean_dir "$yarn_cache" "yarn cache"
fi

# pnpm
command -v pnpm &> /dev/null && clean_cmd "pnpm store prune" "pnpm"

# pip
command -v pip3 &> /dev/null && clean_cmd "pip3 cache purge" "pip"

# Cargo
clean_dir "$HOME/.cargo/registry/cache" "Cargo registry cache"
clean_dir "$HOME/.cargo/git/checkouts" "Cargo git checkouts"

# Go
command -v go &> /dev/null && clean_cmd "go clean -cache -modcache -testcache" "Go"

# Ruby
command -v gem &> /dev/null && clean_cmd "gem cleanup" "Ruby gems"

# Composer
command -v composer &> /dev/null && clean_cmd "composer clear-cache" "Composer"

# ==================================================
# DEVELOPMENT TOOLS
# ==================================================
print_section "Development Tools"

# Docker
if command -v docker &> /dev/null && docker info &> /dev/null 2>&1; then
  clean_cmd "docker system prune -f" "Docker system"
  clean_cmd "docker builder prune -f" "Docker builder"
  clean_cmd "docker volume prune -f" "Docker dangling volumes"
fi

# Xcode
clean_dir "$HOME/Library/Developer/Xcode/DerivedData" "Xcode DerivedData"
clean_dir "$HOME/Library/Developer/Xcode/Archives" "Xcode Archives" 1048576
clean_dir "$HOME/Library/Caches/CocoaPods" "CocoaPods"

# iOS Simulators
command -v xcrun &> /dev/null && clean_cmd "xcrun simctl delete unavailable" "Old simulators"

# Old iOS backups (>30 days)
if [[ -d "$HOME/Library/Application Support/MobileSync/Backup" ]]; then
  before=$(get_size "$HOME/Library/Application Support/MobileSync/Backup")
  if ! $DRY_RUN; then
    find "$HOME/Library/Application Support/MobileSync/Backup" -type d -mindepth 1 -maxdepth 1 -mtime +30 -exec rm -rf {} \; 2> /dev/null || true
  fi
  after=$(get_size "$HOME/Library/Application Support/MobileSync/Backup")
  saved=$((before - after))
  if [[ $saved -gt 0 ]]; then
    TOTAL_SAVED=$((TOTAL_SAVED + saved))
    print_success "iOS backups: $(format_size $saved)"
  fi
fi

clean_dir "$HOME/Library/iTunes/iPhone Software Updates" "iOS updates"
clean_dir "$HOME/Library/iTunes/iPad Software Updates" "iPad updates"

# Gradle & Maven
clean_dir "$HOME/.gradle/caches" "Gradle caches"
clean_dir "$HOME/.m2/repository" "Maven" 524288

# ==================================================
# EDITORS
# ==================================================
print_section "Editors"

# VS Code
clean_dir "$HOME/Library/Application Support/Code/CachedData" "VS Code cached data"
clean_dir "$HOME/Library/Application Support/Code/CachedExtensionVSIXs" "VS Code extension cache"
clean_dir "$HOME/Library/Application Support/Code/logs" "VS Code logs"
clean_dir "$HOME/Library/Application Support/Code/User/workspaceStorage" "VS Code workspace storage" 102400

# Cursor
clean_dir "$HOME/Library/Application Support/Cursor/CachedData" "Cursor cached data"
clean_dir "$HOME/Library/Application Support/Cursor/CachedExtensionVSIXs" "Cursor extension cache"
clean_dir "$HOME/Library/Application Support/Cursor/logs" "Cursor logs"

# Claude CLI
if [[ -d "$HOME/.local/share/claude" ]]; then
  claude_size=$(get_size "$HOME/.local/share/claude")
  if [[ $claude_size -gt 1048576 ]]; then
    print_warning "Claude CLI: $(format_size "$claude_size") - run 'claude conversation rm' to prune"
  fi
fi

# ==================================================
# BROWSERS (Skip if running)
# ==================================================
print_section "Browsers"

if is_running "Google Chrome"; then
  print_warning "Chrome running - skipped"
else
  clean_dir "$HOME/Library/Caches/Google/Chrome" "Chrome cache"
  clean_dir "$HOME/Library/Application Support/Google/Chrome/Default/Service Worker" "Chrome workers"
fi

if is_running "Safari"; then
  print_warning "Safari running - skipped"
else
  clean_dir "$HOME/Library/Caches/com.apple.Safari" "Safari cache"
fi

if is_running "firefox"; then
  print_warning "Firefox running - skipped"
else
  clean_dir "$HOME/Library/Caches/Firefox" "Firefox cache"
fi

clean_dir "$HOME/Library/Caches/Microsoft Edge" "Edge cache"
clean_dir "$HOME/Library/Caches/BraveSoftware/Brave-Browser" "Brave cache"
clean_dir "$HOME/Library/Caches/com.operasoftware.Opera" "Opera cache"
clean_dir "$HOME/Library/Caches/company.thebrowser.Browser" "Arc cache"

# ==================================================
# APPLICATIONS
# ==================================================
print_section "Applications"

clean_dir "$HOME/Library/Caches/com.apple.mail" "Mail cache"

# Adobe
clean_dir "$HOME/Library/Application Support/Adobe/Common/Media Cache Files" "Adobe media cache"
clean_dir "$HOME/Library/Caches/Adobe" "Adobe cache"

# Communication
if ! is_running "Slack"; then
  clean_dir "$HOME/Library/Application Support/Slack/Cache" "Slack cache"
  clean_dir "$HOME/Library/Application Support/Slack/Service Worker" "Slack workers"
fi

clean_dir "$HOME/Library/Application Support/discord/Cache" "Discord cache"
clean_dir "$HOME/Library/Caches/com.spotify.client" "Spotify cache"
clean_dir "$HOME/Library/Caches/us.zoom.xos" "Zoom cache"

# System
clean_dir "$HOME/Library/Caches/com.apple.QuickLookDaemon" "QuickLook cache"

# ==================================================
# DOWNLOADS (files older than 30 days)
# ==================================================
print_section "Downloads"

if [[ -d "$HOME/Downloads" ]]; then
  before=$(get_size "$HOME/Downloads")
  if ! $DRY_RUN; then
    find "$HOME/Downloads" -mindepth 1 -maxdepth 1 -mtime +30 -exec rm -rf {} \; 2> /dev/null || true
  else
    stale=$(find "$HOME/Downloads" -mindepth 1 -maxdepth 1 -mtime +30 -exec du -sk {} + 2> /dev/null | awk '{s+=$1}END{print s+0}')
    [[ $stale -gt 0 ]] && print_success "[DRY] Downloads >30d: $(format_size $stale)"
    TOTAL_SAVED=$((TOTAL_SAVED + stale))
  fi
  after=$(get_size "$HOME/Downloads")
  saved=$((before - after))
  if [[ $saved -gt 0 ]]; then
    TOTAL_SAVED=$((TOTAL_SAVED + saved))
    print_success "Downloads >30d: $(format_size $saved)"
  fi
fi

# ==================================================
# SYSTEM MAINTENANCE
# ==================================================
print_section "System Maintenance"

if ! $DRY_RUN; then
  clean_cmd "atsutil databases -removeUser" "Font cache"
  clean_cmd "dscacheutil -flushcache && killall -HUP mDNSResponder" "DNS cache"
  find ~ -name ".DS_Store" -delete 2> /dev/null || true
  print_success "Removed .DS_Store files"
fi

# ==================================================
# SUMMARY
# ==================================================
echo ""
echo "======================================"
$DRY_RUN && print_success "Dry Run Complete!" || print_success "Cleanup Complete!"
echo "======================================"
echo -e "Space freed: ${GREEN}$(format_size $TOTAL_SAVED)${NC}"
echo ""
print_warning "Manual review recommended:"
echo -e "  huggingface-cli delete-cache   ${CYAN}# ML models${NC}"
echo -e "  ollama rm <model>              ${CYAN}# LLM models${NC}"
echo -e "  docker volume prune            ${CYAN}# Unused volumes${NC}"
echo ""
