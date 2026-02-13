---
name: Gen Comm
description: Generate a styled artifact from a moodboard's design tokens
argument-hint: [mood] [format] [brief...]
---

MOOD=$ARGUMENTS[0]
FORMAT=$ARGUMENTS[1]
BRIEF=$ARGUMENTS[2:]

MOOD_CSS=$MOODS/$MOOD.css
COMM_CSS=$COMMS/$FORMAT.css

# Layers

```text
comm × mood × brief → artifact
```

| Layer    | Owns                         |
|----------|------------------------------|
| comm.css | Frame geometry (size, @page) |
| mood.css | Tokens, element styles       |
| artifact | Content, composition         |

## CSS Architecture

**Critical**: Include CSS from source files verbatim. Do not recreate or modify styles manually.

```html
<style>
/* Contents of $COMM_CSS (e.g., doc.css) */
/* Contents of $MOOD_CSS (e.g., brief.css) */
</style>
```

**Warning**: CSS variables (`var()`) do not work inside `@page` rules. Chrome ignores them. Use literal values for margins.

## Margin Strategy

Documents (doc, cv) use a two-layer margin system:

| Context | Mechanism | Source |
|---------|-----------|--------|
| Screen  | `section { padding }` | mood.css |
| Print   | `@page { margin }` | comm.css |

The pattern:
- `@page { margin: 0.6in }` handles print margins (comm.css)
- `body { margin: 0; padding: 0 }` has zero spacing (comm.css)
- `section { padding: var(--space-8) }` provides screen margins (mood.css)
- `@media print { section { padding: 0 } }` removes section padding for print (mood.css)

**Failure mode**: If section padding is omitted, content touches edges on screen. The @page margin only applies during print/PDF export.

Decks/posters use viewport-based sizing (no @page).

# Comm

| Comm   | Canvas     |
|--------|------------|
| deck   | 1920×1080  |
| doc    | 8.5in×11in |
| cv     | 8.5in×11in |
| poster | 1080×1920  |

# Structure

| Tag     | Role       |
|---------|------------|
| section | Page/slide |
| h1      | Primary    |
| h2      | Secondary  |
| main    | Content    |
| aside   | Tangential |
| footer  | Metadata   |
| figure  | Visual     |

Utilities: .accent, .muted

Multiple `<section>` for multi-page artifacts.

# Generation

1. Validate $MOOD_CSS and $COMM_CSS exist
2. Read $STYLE_/$MOOD/mood.yaml if available: intent, influences, anti_patterns
3. Generate a reasonable output name from the brief
4. Compose HTML:
   - Concatenate $COMM_CSS then $MOOD_CSS into single `<style>` block
   - Do not modify, subset, or recreate CSS properties
   - Use semantic tags per Structure table
5. Verify before render:
   - [ ] section has `padding` property (screen margins)
   - [ ] @page has literal margin value (not var())
   - [ ] @media print section padding is 0
6. Render with format-appropriate tool:

## Rendering

| Format | Tool       | Rationale                        |
|--------|------------|----------------------------------|
| doc    | weasyprint | CSS Paged Media, proper @page    |
| cv     | weasyprint | CSS Paged Media, proper @page    |
| deck   | decktape   | Viewport-based slide capture     |
| poster | decktape   | Viewport-based, fixed dimensions |

## WeasyPrint (doc, cv)

CSS Paged Media renderer. Respects @page rules, handles pagination, no browser overhead.

```bash
weasyprint "$RESULTS_/{name}.html" "$RESULTS_/{name}.pdf"
```

Install: `brew install weasyprint`

## Decktape (deck, poster)

Viewport-based rendering for fixed-dimension canvases.

```bash
decktape generic --size {width}x{height} \
  "file://$RESULTS_/{name}.html" \
  "$RESULTS_/{name}.pdf"
```

| Format | Size      |
|--------|-----------|
| deck   | 1920x1080 |
| poster | 1080x1920 |

# Output

```text
$RESULTS_/{name}.html
$RESULTS_/{name}.pdf
```
