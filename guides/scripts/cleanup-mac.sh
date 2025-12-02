#!/bin/bash
set -euo pipefail

# Mac Cleanup Script - Comprehensive Edition
# Intelligently cleans caches, logs, temp files, and development artifacts
# Safe to run regularly - only touches regenerable caches and temp files

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

TOTAL_SAVED=0

# Output functions
print_section() { echo -e "\n${BLUE}==>${NC} ${1}"; }
print_success() { echo -e "${GREEN}✓${NC} ${1}"; }
print_warning() { echo -e "${YELLOW}!${NC} ${1}"; }
print_info() { echo -e "${CYAN}ℹ${NC} ${1}"; }

# Get size in KB
get_size() {
    if [ -e "$1" ]; then
        du -sk "$1" 2>/dev/null | cut -f1 || echo "0"
    else
        echo "0"
    fi
}

# Format size for display
format_size() {
    local size=$1
    if [ $size -ge 1048576 ]; then
        local gb=$((size * 100 / 1048576))
        echo "$((gb / 100)).$((gb % 100)) GB"
    elif [ $size -ge 1024 ]; then
        local mb=$((size * 100 / 1024))
        echo "$((mb / 100)).$((mb % 100)) MB"
    else
        echo "${size} KB"
    fi
}

# Clean directory - only if it exists and has meaningful size
clean_dir() {
    local path=$1
    local desc=$2
    local min_kb=${3:-1024}  # Skip if less than 1MB by default

    [ ! -e "$path" ] && return

    local before=$(get_size "$path")
    [ -z "$before" ] && before=0
    [ $before -lt $min_kb ] && return

    # Safety check: ensure path is not empty, root, or home
    if [[ -z "$path" || "$path" == "/" || "$path" == "$HOME" ]]; then
        return
    fi

    if [ -d "$path" ]; then
        # Use find for safer deletion
        find "$path" -mindepth 1 -delete 2>/dev/null || true
    elif [ -f "$path" ]; then
        rm -f "$path" 2>/dev/null || true
    fi

    local after=$(get_size "$path")
    local saved=$((before - after))
    TOTAL_SAVED=$((TOTAL_SAVED + saved))

    [ $saved -gt 0 ] && print_success "$desc: $(format_size $saved)"
}

# Clean with command
clean_cmd() {
    local cmd=$1
    local desc=$2
    if eval "$cmd" 2>/dev/null; then
        print_success "$desc"
    fi
}

echo "======================================"
echo "  Mac Cleanup - Running..."
echo "======================================"

# ==================================================
# SYSTEM CACHES & LOGS
# ==================================================
print_section "System Caches & Logs"

# User caches - only clean large ones
for cache in "$HOME/Library/Caches"/*; do
    [ -d "$cache" ] && clean_dir "$cache" "$(basename "$cache")" 102400  # >100MB
done

clean_dir "$HOME/Library/Logs" "System logs"
clean_dir "$HOME/Library/Logs/DiagnosticReports" "Crash reports"
clean_dir "$HOME/Library/Application Support/CrashReporter" "Crash reporter"

# Temp files older than 3 days
if [ -d "/tmp" ]; then
    before=$(get_size "/tmp")
    find /tmp -type f -atime +3 -delete 2>/dev/null || true
    after=$(get_size "/tmp")
    saved=$((before - after))
    [ $saved -gt 0 ] && { TOTAL_SAVED=$((TOTAL_SAVED + saved)); print_success "Temp files: $(format_size $saved)"; }
fi

# Trash
clean_dir "$HOME/.Trash" "Trash" 0

# ==================================================
# PACKAGE MANAGERS
# ==================================================
print_section "Package Managers"

# Homebrew (required)
if command -v brew &> /dev/null; then
    clean_cmd "brew cleanup -s && brew autoremove" "Homebrew"
    clean_dir "$(brew --cache)" "Homebrew cache"
fi

# npm
command -v npm &> /dev/null && clean_cmd "npm cache clean --force" "npm"

# yarn
if command -v yarn &> /dev/null; then
    clean_dir "$(yarn cache dir 2>/dev/null)" "yarn"
fi

# pnpm
command -v pnpm &> /dev/null && clean_cmd "pnpm store prune" "pnpm"

# pip
command -v pip3 &> /dev/null && clean_cmd "pip3 cache purge" "pip"

# Cargo (Rust)
if [ -d "$HOME/.cargo" ]; then
    clean_dir "$HOME/.cargo/registry/cache" "Cargo cache"
    clean_dir "$HOME/.cargo/git/checkouts" "Cargo checkouts"
fi

# Go
command -v go &> /dev/null && clean_cmd "go clean -cache -modcache -testcache" "Go"

# Ruby gems
command -v gem &> /dev/null && clean_cmd "gem cleanup" "Ruby gems"

# Composer (PHP)
command -v composer &> /dev/null && clean_cmd "composer clear-cache" "Composer"

# ==================================================
# DEVELOPMENT TOOLS
# ==================================================
print_section "Development Tools"

# Docker (less aggressive - keeps tagged images)
if command -v docker &> /dev/null && docker info &> /dev/null 2>&1; then
    clean_cmd "docker system prune --volumes -f" "Docker"
fi

# Xcode
clean_dir "$HOME/Library/Developer/Xcode/DerivedData" "Xcode DerivedData"
clean_dir "$HOME/Library/Developer/Xcode/Archives" "Xcode Archives" 1048576  # >1GB
clean_dir "$HOME/Library/Caches/CocoaPods" "CocoaPods"

# iOS Simulators - delete unavailable
if command -v xcrun &> /dev/null; then
    clean_cmd "xcrun simctl delete unavailable" "Old simulators"
fi

# Old iOS backups (>30 days)
if [ -d "$HOME/Library/Application Support/MobileSync/Backup" ]; then
    before=$(get_size "$HOME/Library/Application Support/MobileSync/Backup")
    find "$HOME/Library/Application Support/MobileSync/Backup" -type d -mindepth 1 -maxdepth 1 -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
    after=$(get_size "$HOME/Library/Application Support/MobileSync/Backup")
    saved=$((before - after))
    [ $saved -gt 0 ] && { TOTAL_SAVED=$((TOTAL_SAVED + saved)); print_success "iOS backups: $(format_size $saved)"; }
fi

# iOS Software Updates
clean_dir "$HOME/Library/iTunes/iPhone Software Updates" "iOS updates"
clean_dir "$HOME/Library/iTunes/iPad Software Updates" "iPad updates"

# Gradle & Maven
clean_dir "$HOME/.gradle/caches" "Gradle"
clean_dir "$HOME/.m2/repository" "Maven" 512000  # >500MB

# ==================================================
# BROWSERS
# ==================================================
print_section "Browsers"

clean_dir "$HOME/Library/Caches/com.apple.Safari" "Safari"
clean_dir "$HOME/Library/Caches/Google/Chrome" "Chrome"
clean_dir "$HOME/Library/Caches/Firefox" "Firefox"
clean_dir "$HOME/Library/Caches/Microsoft Edge" "Edge"
clean_dir "$HOME/Library/Caches/BraveSoftware/Brave-Browser" "Brave"
clean_dir "$HOME/Library/Caches/com.operasoftware.Opera" "Opera"

# Browser service workers
clean_dir "$HOME/Library/Application Support/Google/Chrome/Default/Service Worker" "Chrome workers"

# ==================================================
# APPLICATIONS
# ==================================================
print_section "Applications"

# Mail
clean_dir "$HOME/Library/Caches/com.apple.mail" "Mail"
for envelope in "$HOME/Library/Mail/V*/MailData/Envelope Index"*; do
    [ -e "$envelope" ] && rm -rf "$envelope" 2>/dev/null || true
done

# Adobe (notorious space hog)
clean_dir "$HOME/Library/Application Support/Adobe/Common/Media Cache Files" "Adobe media"
clean_dir "$HOME/Library/Caches/Adobe" "Adobe"

# Communication apps
clean_dir "$HOME/Library/Application Support/Slack/Cache" "Slack"
clean_dir "$HOME/Library/Application Support/Slack/Service Worker" "Slack workers"
clean_dir "$HOME/Library/Application Support/discord/Cache" "Discord"
clean_dir "$HOME/Library/Caches/com.spotify.client" "Spotify"

# System caches
clean_dir "$HOME/Library/Caches/com.apple.QuickLookDaemon" "QuickLook"
clean_dir "$HOME/Library/Application Support/com.apple.documentVersions" "Document versions"

# ==================================================
# SYSTEM MAINTENANCE
# ==================================================
print_section "System Maintenance"

# Font cache
clean_cmd "atsutil databases -removeUser" "Font cache"

# DNS cache
clean_cmd "dscacheutil -flushcache && killall -HUP mDNSResponder" "DNS cache"

# .DS_Store files
find ~ -name ".DS_Store" -delete 2>/dev/null || true
print_success "Removed .DS_Store files"

# Purge memory (requires sudo in some macOS versions)
if command -v purge &> /dev/null; then
    if purge 2>/dev/null; then
        print_success "Memory purge"
    else
        print_warning "Memory purge (skipped - requires elevated privileges)"
    fi
fi

# ==================================================
# SUMMARY
# ==================================================
echo ""
echo "======================================"
print_success "Cleanup Complete!"
echo "======================================"
echo -e "Space freed: ${GREEN}$(format_size $TOTAL_SAVED)${NC}"
echo ""
print_info "Next steps:"
echo "  • brew install ncdu && ncdu ~  ${CYAN}# Visual disk analyzer${NC}"
echo "  • du -sh ~/* | sort -hr | head -20  ${CYAN}# Find large dirs${NC}"
echo "  • System Settings → Storage  ${CYAN}# macOS storage manager${NC}"
echo ""
