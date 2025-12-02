---
name: Gen Art
description: Generate a styled artifact from a moodboard's design tokens
argument-hint: [mood] [type] [name] [brief...]
---

MOOD=$ARGUMENTS[0]
TYPE=$ARGUMENTS[1]
NAME=$ARGUMENTS[2]
BRIEF="${ARGUMENTS[@]:3}"

MOOD_DIR=$MOODS_DIR/$MOOD
STYLE_YAML=$MOOD_DIR/style.yaml
TOKENS_CSS=$MOOD_DIR/tokens.css

# Role

Generate an artifact in style $MOOD. The style (style.yaml + tokens.css) is the canonical visual language. TYPE and BRIEF guide how to apply it.

# Task

1. Read $STYLE_YAML and $TOKENS_CSS
2. Generate HTML embodying the style for $BRIEF
3. Convert to PDF using decktape

# Type Guidance

TYPE is flexible. Use judgment based on the word and BRIEF:

- Presentation types (deck, slides, pitch): Sparse, large type, 1-2 elements per page, 16:9
- Document types (report, doc, brief, paper): Dense, smaller type, flowing prose, letter/A4
- Single-page types (poster, one-pager, flyer): Everything on one page, portrait or landscape
- Other: Infer from context

# Frameworks

For documents, use the existing CSS framework:

```html
<link rel="stylesheet" href="../docs/report.css">
<script src="../docs/nav.js"></script>
```

This provides:
- Document typography from `style/tokens.css`
- Page structure from `style/docs/base.css`
- Report components from `style/docs/report.css`
- Navigation for decktape from `style/docs/nav.js`

For moodboard-specific styles, inline tokens from $TOKENS_CSS.

# Page Structure

All artifacts use discrete pages for decktape:

```html
<section class="page">...</section>
<section class="page">...</section>
```

The difference is content density and typography, not navigation mechanism.

# HTML Entities

Technical content often contains `<` and `>` symbols. These MUST be escaped:

- `<` becomes `&lt;`
- `>` becomes `&gt;`
- `&` becomes `&amp;`

Example: `latency < 0.08ms` must be written as `latency &lt; 0.08ms`

Unescaped angle brackets are interpreted as HTML tags and will silently disappear.

# Decktape

```bash
decktape generic --size {WxH} "file://path/to/file.html" output.pdf
```

Common sizes:
- 1920x1080: 16:9 presentations
- 816x1056: US Letter documents
- 794x1123: A4 documents
- 1080x1920: Portrait posters

# Content

For documents: Write dense, flowing prose. Use the components from base.css (callouts, stat boxes, tables). Fill each page with substantial content.

For presentations: Sparse. One idea per page. Large type. Negative space.

# Output

```text
Generated style/$MOOD/$NAME.pdf

  $NAME.html  (source)
  $NAME.pdf   (output)
```
