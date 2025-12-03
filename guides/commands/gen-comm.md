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
4. Compose HTML with semantic tags
5. Render with format-appropriate size:

| Format | Size       |
|--------|------------|
| deck   | 1920x1080  |
| doc    | 816x1056   |
| cv     | 816x1056   |
| poster | 1080x1920  |

```bash
decktape generic --size {size} "file://$RESULTS_/{name}.html" "$RESULTS_/{name}.pdf"
```

# Output

```text
$RESULTS_/{name}.html
$RESULTS_/{name}.pdf
```
