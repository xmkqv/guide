#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

# Check dependencies
command -v claude >/dev/null 2>&1 || { echo "Error: claude not found in PATH"; exit 1; }

# Collect unspecced images
find_unspecced() {
    local unspecced=()
    shopt -s nullglob
    for img in style/*/*.png style/*/*.jpg style/*/*.jpeg style/*/*.webp; do
        [ -f "$img" ] || continue
        spec="${img%.*}.spec.yaml"
        [ -f "$spec" ] || unspecced+=("$img")
    done
    shopt -u nullglob
    printf '%s\n' "${unspecced[@]}"
}

# Unique directories from file list
unique_dirs() {
    while read -r f; do
        [ -n "$f" ] && dirname "$f"
    done | sort -u
}

# Step 1: Analyze images → specs
analyze() {
    local img="$1"
    local spec="${img%.*}.spec.yaml"
    echo "→ analyze: $img"
    claude style/commands/analyze.md "$img" > "$spec"
}

# Step 2: Compose specs → style
compose() {
    local dir="$1"
    echo "→ compose: $dir"
    claude style/commands/compose.md "$dir/" > "$dir/style.yaml"
}

# Step 3: Export style → tokens
export_tokens() {
    local dir="$1"
    echo "→ export: $dir"
    claude style/commands/export.md "$dir/" > "$dir/tokens.css"
}

# Main
unspecced=$(find_unspecced)

if [ -z "$unspecced" ]; then
    echo "All images have specs."
    exit 0
fi

echo "Unspecced images:"
echo "$unspecced" | sed 's/^/  /'
echo ""
read -p "Proceed? [y/N] " -n 1 -r
echo ""

[[ $REPLY =~ ^[Yy]$ ]] || exit 0

dirs=$(echo "$unspecced" | unique_dirs)

# Analyze
echo "$unspecced" | while read -r img; do
    [ -n "$img" ] && analyze "$img"
done

# Compose + Export
echo "$dirs" | while read -r dir; do
    [ -n "$dir" ] && compose "$dir" && export_tokens "$dir"
done

echo "Done."
