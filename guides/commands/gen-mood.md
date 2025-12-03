---
name: Gen Mood
description: Help the user curate images that capture an aesthetic
argument-hint: [name] [nmore int] [brief...]
---

NAME=$ARGUMENTS[0]
NMORE=$ARGUMENTS[1]
BRIEF=$ARGUMENTS[2:]

WORK=$STYLE_/$NAME
OUT=$MOODS/$NAME.css

# Output

```text
$WORK/                 # working directory (local)
  *.jpg                # reference images
  *.spec.yaml          # extracted data per image
  mood.yaml            # creative brief
  mood.css             # design tokens + element styles

$MOODS/$NAME.css       # exported style (global)
```

gen-comm consumes the exported CSS.

# Workflow

## 1. Discover

Use AskUserQuestion to explore direction before searching.

## 2. Search

Find $NMORE images matching $BRIEF.

Display images inline. Never list URLs with descriptions.

Sources: Film Grab, Unsplash, Fonts In Use, Dribbble, Cinema Palettes.

After each round, ask: More like which? Less of what? What's missing?

## 3. Collect

Download selected images to $WORK.

Name: `{nn}-{slug}.{ext}`

## 4. Extract

For each image, generate `{nn}-{slug}.spec.yaml`:

```yaml
source: "01-rain-soaked-neon.jpg"
extracted_at: "2025-12-02T10:30:00Z"

palette:
  dominant:
    - { hex: "#0a0a0a", weight: 0.6, name: "void" }
  accent:
    - { hex: "#ff2a6d", weight: 0.1, name: "neon" }

composition:
  balance: -0.2
  density: 0.3
  focal_points: [[0.3, 0.5, 0.9]]

texture:
  grain: 0.7
  organic: 0.2

affect:
  temperature: -0.6
  weight: 0.7
  energy: 0.2

influences: ["film noir", "Blade Runner"]
anti_patterns: ["flat lighting", "pastels"]
intent: "Tension through negative space and isolated light."
```

## 5. Compose

Read all specs. Write $WORK/mood.yaml:

```yaml
_meta:
  sources: [01-rain-soaked-neon.spec.yaml, ...]
  composed_at: "2025-12-02T10:45:00Z"

intent: |
  Cinematic tension. Deep shadows punctuated by artificial light.

mood: "nocturnal urban solitude"

palette:
  dominant:
    - { hex: "#0a0a0a", name: "void" }
  accent:
    - { hex: "#ff2a6d", name: "neon" }
  semantic:
    surface: "#0a0a0a"
    text: "#e8e8e8"
    text-muted: "#6a6a6a"
    accent: "#ff2a6d"

typography:
  families: ["Inter", "JetBrains Mono"]
  scale: { base: "1rem", ratio: 1.25 }

spacing:
  base: 8

influences:
  - "film noir cinematography"
  - "Blade Runner production design"

anti_patterns:
  - "flat even lighting"
  - "pastel colors"
```

Directives: `# LOCKED` (preserved exactly), `# IMPORTANT` (wins conflicts)

## 6. Express

Transform mood.yaml into $WORK/mood.css.

Required:
- Tokens: `--color-*`, `--space-*`, `--fs-*`, `--ff-*`
- Elements: section, h1, h2, main, aside, footer, figure
- Utilities: .accent, .muted

Integration point:

```css
section {
  inline-size: var(--comm-width, 100%);
  block-size: var(--comm-height, auto);
}
```

## 7. Export

Copy $WORK/mood.css to $OUT.

# Output

```text
Mood "$NAME" complete.

Working: $WORK/
Exported: $OUT

Test: /guide:gen-comm $NAME deck "Quick test"
```
