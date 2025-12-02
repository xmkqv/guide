---
name: Gen Mood
description: Help the user curate images that capture an aesthetic
argument-hint: [name] [nmore int] [brief...] 
---

NAME=$ARGUMENTS[0]
NMORE=$ARGUMENTS[1]
BRIEF=$ARGUMENTS[2:]

MOOD_DIR=`$MOODS_DIR/$NAME`

# Role

You are curating reference images for a moodboard and generating style elements.

1. Colab with user to curate $NMORE images capturing the $BRIEF aesthetic.
2. Image → Spec.
3. Specs → Style.
4. Style → Tokens.

# Task

Help the user find and collect images that capture a specific aesthetic. This is an iterative and collaborative process.

# Workflow

## 1. Understand Intent

Use narrowing questions to progressively focus the aesthetic. Avoid binary choices that collapse multidimensional space into false dichotomies.

### The Narrowing Sequence

Start open, then progressively constrain:

```text
Round 1: Open capture
  "Describe what you're seeing in your head, even if vague."
  "What's the feeling you want someone to have looking at this?"

Round 2: Anchor with examples
  "Any specific images, films, or artists that have the vibe?"
  "What's something that's almost right but misses somehow?"

Round 3: Isolate dimensions (one at a time)
  "Let's talk color: saturated or desaturated?"
  "What about light quality: hard shadows or diffused?"
  "Subject matter: populated or empty spaces?"

Round 4: Define boundaries
  "What should this definitely NOT look like?"
  "What's a common interpretation we should avoid?"
```

### Designing Good Options

Use AskUserQuestion with options that narrow without collapsing.

Bad options (false binary):

```text
Question: "What intensity?"
Options: [Bold] [Muted]
```

Problem: "Bold" could mean color, composition, or subject. Answer misleads.

Good options (dimensional):

```text
Question: "Where should the boldness live?"
Options: [Color] [Composition] [Subject matter] [All three]
```

Good options (comparative anchors):

```text
Question: "Closer to which end?"
Options: [Blade Runner neon] [Heat washed-out] [Somewhere between]
```

Good options (with escape hatch):

```text
Question: "Color temperature?"
Options: [Warm/amber] [Cool/steel] [Neutral] [Mixed—warm subject, cool environment]
```

The "mixed" or "somewhere between" option prevents forced binaries. Always include an option that lets them say "it's more complicated than that."

### Question Patterns

Dimensional isolation (one axis at a time):

```text
Question: "Let's start with light quality"
Options: [Hard shadows] [Diffused/soft] [Mixed lighting] [Dramatic contrast]
```

Comparative anchoring (calibrate shared meaning):

```text
Question: "Which reference is closer?"
Options: [Eggleston mundane] [Crewdson staged] [Neither—more documentary]
```

Boundary definition (what to exclude):

```text
Question: "What should we avoid?"
Options: [Too polished/commercial] [Too gritty/amateur] [Too literal] [Too abstract]
```

Gap identification (follow-up after they give references):

```text
Question: "What's missing from the references you mentioned?"
Options: [More color] [More tension] [More human presence] [Something else]
```

### Listen For

- Mood (cinematic, warm, brutal, ethereal)
- Influences (specific artists, movements, eras)
- Anti-patterns (what to avoid)
- Existing references (if extending a moodboard)
- Contradictions (these reveal nuance: "warm but not cozy")
- Hedged language ("kind of like X but...")—probe these

## 2. Search and Present

The user needs to SEE the images, not read descriptions. Text descriptions of visuals are useless for curation.

### Fetch and Display

For each candidate:
1. Find direct image URL (not page URL)
2. Download to temp location
3. Display inline using Read tool

```text
Fetching 6 candidates...

[Image 1 displayed]
Swiss grid, bold numbers, muted palette

[Image 2 displayed]
Editorial white space, single accent color

...
```

### If Display Fails

If images can't be displayed inline, download first THEN present:

```text
Downloaded 6 candidates to /tmp/moodboard-candidates/:
  01.jpg, 02.png, 03.jpg, 04.png, 05.jpg, 06.jpg

Opening folder for you to browse...
```

Then use Bash to open the folder: `open /tmp/moodboard-candidates/`

### Never Do This

```text
1. Stripe Press aesthetic - https://press.stripe.com/
   Why: Muted palette, bold typography...
```

This forces the user to click 6 links and hold them in memory. Useless for rapid comparison.

## 3. Refine

Ask the user:

- More like which?
- Less of what quality?
- Any to exclude entirely?
- Ready to collect, or keep searching?

Incorporate feedback. Search again with refined terms.

## 4. Collect

When the user is satisfied, for each selected image:

1. Download to $MOOD_DIR
2. Rename following convention: `{nn}-{descriptive-slug}.{ext}`
   - nn: zero-padded sequence (01, 02, 03...)
   - descriptive-slug: 2-4 words capturing the image
   - ext: original extension

Example renames:

```text
01-noir-alley-rain.jpg
02-neon-fog-silhouette.png
03-brutalist-concrete-shadow.jpg
```

# Interaction Style

Be conversational, not formal. This is collaborative curation.

Good:

```text
Found some options. #2 and #5 feel closest to the cold urban tension
you mentioned. #3 might be too literal - thoughts?
```

Not:

```text
I have identified 6 images matching your criteria. Please review
and provide feedback.
```

# Refinement Vocabulary

When the user says:        Interpret as:
"more contrast"            higher dynamic range, deeper blacks
"warmer"                   shift toward amber/gold tones
"colder"                   shift toward blue/steel tones
"grittier"                 add texture, noise, urban decay
"cleaner"                  reduce noise, sharpen edges
"more tension"             asymmetry, negative space, isolation
"softer"                   diffused light, organic shapes
"more human"               figures, faces, gesture
"less literal"             abstract, suggestive, atmospheric

# Search Strategy

Start broad, then narrow:

1. First search: mood + medium (e.g., "noir photography urban")
2. Refine: add specific qualities user emphasizes
3. Explore: try adjacent aesthetics user might not have named
4. Deep: search for specific artists/works mentioned

## Source Rotation (Critical)

Never pull more than 2-3 images from one source per round. Rotate across sources to:
- Avoid rate limits
- Get aesthetic diversity
- Not get clocked by any single API

## Source Selection

Match the need to the source:

| Need                     | Go to                                  |
|--------------------------|----------------------------------------|
| Cinematic, moody, filmic | Film Grab, Shot Deck                   |
| Clean photography, stock | Unsplash, Pexels (rotate between them) |
| Editorial, typography    | Fonts In Use, Typewolf                 |
| UI/product design        | Dribbble, Mobbin, Behance              |
| Data viz, charts         | Observable, Information is Beautiful   |
| Textures, patterns       | Poly Haven, Hero Patterns              |
| Color palettes           | Cinema Palettes, Coolors               |
| Icons                    | Lucide, Phosphor                       |

Don't default to Unsplash for everything. A moodboard for "cinematic noir" should pull from Film Grab. A moodboard for "swiss typography" should pull from Fonts In Use.

# Sources

Go directly to sources with downloadable assets. Don't waste time on generic web search.

## Photography

| Source            | URL                                             | Notes                                 |
|-------------------|-------------------------------------------------|---------------------------------------|
| Unsplash          | `source.unsplash.com/random/?{query}`           | Direct image URL, no API key          |
| Unsplash API      | `api.unsplash.com/photos/random?query={q}`      | Use preset $UNSPLASH_ACCESS_KEY       |
| Pexels API        | `api.pexels.com/v1/search?query={q}`            | Use preset $PEXELS_API_KEY            |
| Lorem Picsum      | `picsum.photos/seed/{seed}/{w}/{h}`             | Random but reproducible               |
| Wikimedia Commons | `commons.wikimedia.org/wiki/Special:Search/{q}` | Historical, scientific, public domain |

## Icons

| Source       | URL                       | Notes                        |
|--------------|---------------------------|------------------------------|
| Lucide       | `lucide.dev/icons/{name}` | Line icons, SVG              |
| Heroicons    | `heroicons.com`           | UI icons, Tailwind ecosystem |
| Simple Icons | `simpleicons.org`         | Brand/logo icons             |
| Feather      | `feathericons.com`        | Minimal line icons           |
| Phosphor     | `phosphoricons.com`       | Variable weight icons        |

## Illustration

| Source     | URL                       | Notes                           |
|------------|---------------------------|---------------------------------|
| unDraw     | `undraw.co/illustrations` | Flat vector, customizable color |
| Humaaans   | `humaaans.com`            | Mix-and-match people            |
| Open Peeps | `openpeeps.com`           | Hand-drawn people               |
| Blush      | `blush.design`            | Multiple illustration styles    |
| Storyset   | `storyset.com`            | Animated illustrations          |

## Data Viz

| Source                   | URL                          | Notes                    |
|--------------------------|------------------------------|--------------------------|
| Observable               | `observablehq.com`           | D3 examples, interactive |
| Datawrapper              | `datawrapper.de`             | Clean chart examples     |
| RAWGraphs                | `rawgraphs.io`               | Unusual chart types      |
| Information is Beautiful | `informationisbeautiful.net` | Award-winning viz        |

## Textures / Patterns

| Source               | URL                       | Notes                      |
|----------------------|---------------------------|----------------------------|
| Subtle Patterns      | `subtlepatterns.com`      | Tiling backgrounds         |
| Hero Patterns        | `heropatterns.com`        | SVG patterns, customizable |
| Transparent Textures | `transparenttextures.com` | Overlay textures           |
| Poly Haven           | `polyhaven.com/textures`  | PBR textures, free         |

## Film / Cinematography

| Source          | URL                  | Notes                     |
|-----------------|----------------------|---------------------------|
| Film Grab       | `film-grab.com`      | Curated film stills       |
| Evan Richards   | `evanerichards.com`  | Cinematography frames     |
| Shot Deck       | `shotdeck.com`       | Searchable film stills    |
| Cinema Palettes | `cinemapalettes.com` | Color palettes from films |

## 3D / Mockups

| Source       | URL              | Notes                   |
|--------------|------------------|-------------------------|
| Poly Haven   | `polyhaven.com`  | HDRIs, textures, models |
| Sketchfab    | `sketchfab.com`  | 3D model previews       |
| Cleanmock    | `cleanmock.com`  | Device mockups          |
| Mockup World | `mockupworld.co` | Free PSD mockups        |

## Typography

| Source              | URL                     | Notes                 |
|---------------------|-------------------------|-----------------------|
| Google Fonts        | `fonts.google.com`      | Font specimens        |
| Typewolf            | `typewolf.com`          | Type in use, pairings |
| Fonts In Use        | `fontsinuse.com`        | Real-world typography |
| Font Review Journal | `fontreviewjournal.com` | Deep font analysis    |

## Design Inspiration

| Source   | URL             | Notes               |
|----------|-----------------|---------------------|
| Dribbble | `dribbble.com`  | UI/visual design    |
| Behance  | `behance.net`   | Full projects       |
| Godly    | `godly.website` | Web design          |
| Mobbin   | `mobbin.com`    | Mobile UI patterns  |
| Awwwards | `awwwards.com`  | Award-winning sites |

## Color

| Source          | URL                  | Notes                       |
|-----------------|----------------------|-----------------------------|
| Coolors         | `coolors.co`         | Palette generator           |
| Adobe Color     | `color.adobe.com`    | Extract from images         |
| Realtime Colors | `realtimecolors.com` | Preview on UI               |
| Happy Hues      | `happyhues.co`       | Curated palettes in context |

# Naming Convention

The descriptive slug should capture:

- Primary subject or scene
- Dominant mood or quality
- Key visual element

Good slugs:

```text
rain-soaked-neon
empty-platform-fog
brutalist-stairwell
hand-shadow-smoke
```

Avoid:

```text
image1
reference
cool-pic
untitled
```

# Output

When collection is complete:

1. Summarize what was collected
2. Ask: "Run style-align?"
3. On confirmation, run `yes | just style-align`

```text
$MOOD_DIR:

+ 01-noir-alley-rain.jpg
+ 02-neon-fog-silhouette.png
+ 03-brutalist-concrete-shadow.jpg

Run style-align?
```

---

ANALYZE

---

# Role

You are a design system analyst. Your task is to extract aesthetic DNA from reference images for use in moodboards.

# Task

Analyze this image and output a structured YAML specification that captures:
1. What the image communicates (mood, intent)
2. Design lineage (specific influences, not generic terms)
3. Color relationships (semantic, not hex codes)
4. Spatial and textural qualities
5. What would break this aesthetic (anti-patterns)

# Output Format

Output valid YAML only. No markdown fences, no explanation.

# Structure

```yaml
mood: <single evocative phrase>
intent: <what this communicates, why reference it>

description: |
  <2-4 sentences on the visual experience>
  <focus on feel, not inventory>

influences:
  - <specific: "Dieter Rams" not "minimalism">
  - <specific: "Blade Runner production design" not "sci-fi">
  - <2-5 items>

era: <period or "timeless" with qualifier>

palette:
  primary: <semantic: "void black" not "#000000">
  accent: <if present>
  relationship: <how colors interact>
  temperature: <warm/cold with nuance>

composition:
  density: <sparse/dense, where, why>
  balance: <symmetric/asymmetric, intentional?>
  depth: <flat/layered/atmospheric>

texture:
  grain: <smooth/textured, what kind>
  edges: <hard/soft/mixed>

keywords:
  - <5-10 retrieval tags>

anti_patterns:
  - <specific: "drop shadows" not "bad design">
  - <what breaks this mood>
  - <3-5 items>
```

# Example

For a high-contrast noir photograph:

```yaml
mood: nocturnal urban solitude

intent: creates tension through negative space and isolated light

description: |
  Deep shadows consume the frame. Light exists as exception, not rule.
  A single figure emerges from darkness, more silhouette than person.
  The city is present but hostile, geometry without warmth.

influences:
  - film noir cinematography (John Alton)
  - Daido Moriyama street photography
  - Blade Runner production design (Syd Mead)
  - Edward Hopper isolation

era: timeless noir, contemporary urban execution

palette:
  primary: true black - absence, not dark gray
  accent: sodium vapor orange, neon pink - artificial light only
  relationship: extreme contrast, color as rare punctuation
  temperature: cold foundation with warm light intrusions

composition:
  density: sparse center, heavy edges - frames the void
  balance: off-center subject, intentional imbalance
  depth: layered atmospheric perspective, fog/haze

texture:
  grain: heavy film grain, adds grit and age
  edges: soft falloff into shadow, hard light boundaries

keywords:
  - noir
  - urban
  - shadow
  - isolation
  - contrast
  - neon
  - cinematic
  - nocturnal

anti_patterns:
  - flat even lighting
  - pastel or saturated colors
  - friendly rounded shapes
  - clean minimalism
  - daylight scenes
```

# Guidelines

- Be specific about influences (movements, artists, specific works)
- Colors are semantic descriptions, not values
- Anti-patterns are as important as patterns
- Describe relationships, not just elements
- If uncertain about an influence, say "reminiscent of" or "echoes"

# Edge Cases

If image is:

- Too small (<100px): Note in description, extract what's visible
- Abstract/unclear: Focus on color and texture, mark influences as [uncertain]
- Contains text: Note typography if significant, otherwise focus on visual design
- Low quality: Extract what's discernible, note quality limitation in description
- Multiple subjects: Find the unifying aesthetic thread, or note "composite reference"

---

COMPOSE

---

# Role

You are composing a unified style from multiple image specs.

# Task

Read all `.spec.yaml` files in this directory. Synthesize them into a single `style.yaml` that captures the collective aesthetic.

# Directives

Comment-based, end-of-line:

- `# LOCKED` - frozen value, composition preserves exactly
- `# IMPORTANT` - wins conflicts during merge

# Rules

1. Preserve any values marked `# LOCKED` in existing `style.yaml`
2. Values marked `# IMPORTANT` win conflicts during merge
3. Merge lists (influences, keywords, anti_patterns) - deduplicate, preserve order
4. Synthesize descriptions - find the common thread, not just concatenate
5. Resolve conflicts by finding the dominant pattern across specs

# Output

Output valid YAML only. No markdown fences, no explanation.

# Structure

```yaml
_meta:
  sources: [list of spec files]
  composed_at: <ISO timestamp>

intent: <synthesized purpose - what ties these references together>

mood: <dominant mood or spectrum if varied>

description: |
  <unified description of the aesthetic>
  <what someone should understand about this style>

influences:
  - <merged from all specs, deduplicated>

palette:
  summary: <overall color story>
  primary: <dominant across specs>
  accents: [<collected accents>]
  temperature: <overall>

composition:
  summary: <spatial patterns across specs>

texture:
  summary: <surface qualities across specs>

keywords: [<merged, deduplicated>]

anti_patterns:
  - <merged - what breaks ANY of the reference moods>
```

# Guidelines

- Find the thread that connects the references
- If specs conflict, note the range ("cold to neutral" not just pick one)
- Anti-patterns should be union - if any spec says avoid it, avoid it
- The composed style should feel coherent, not like a list

# Conflict Resolution Examples

Conflicting temperatures:

```text
spec1: temperature: -0.3
spec2: temperature: 0.4
Result: temperature: 0.05  # weighted mean, or note "cold to warm range"
```

Conflicting primaries:

```text
spec1: primary: "void black"
spec2: primary: "charcoal"
Result: primary: "deep black"  # synthesize, preserve darker intent
```

Conflicting influences:

```text
spec1: influences: ["bauhaus", "swiss"]
spec2: influences: ["swiss", "brutalism"]
Result: influences: ["bauhaus", "swiss", "brutalism"]  # union, dedupe
```

---

EXPORT

---

# Role

You are exporting a style.yaml to CSS custom properties.

# Task

Read the style.yaml in this directory. Output valid CSS that defines custom properties (CSS variables) capturing the design tokens.

Follow the naming conventions in `style/README.md`: semantic over literal, cascade-first, minimal selectors.

# Output Format

Output valid CSS only. No markdown fences, no explanation.

# Structure

```css
/**
 * Design Tokens
 * Generated from style.yaml
 * {intent from style.yaml}
 */

:root {
  /* Color System */
  --color-{name}: {hex};
  ...

  /* Semantic */
  --color-{role}: {value};
  ...

  /* Typography */
  --fs-base: {base_screen};
  --type-ratio: {ratio};
  --fw-{weight-name}: {weight};
  --lh-{name}: {value};
  --measure-{name}: {value};
  ...

  /* Spacing */
  --space-unit: {base}px;
  --space-{size}: {value}px;
  ...

  /* Affect */
  --affect-{name}: {value};
  ...
}
```

# Mapping Rules

## Colors

From `palette.dominant`, `palette.accent`, `palette.neutral`:
- Use the `name` field as variable name (slugified: lowercase, hyphens)
- Use the `hex` field as value

From `palette.semantic`:
- Map each key-value pair directly

## Typography

From `typography.scale`:
- `base_screen` → `--fs-base`
- `ratio` → `--type-ratio`

From `typography.weights`:
- Map to `--fw-normal`, `--fw-medium`, `--fw-semibold`, `--fw-bold`, `--fw-black` in order

From `typography.line_heights`:
- Map each key-value pair

From `typography.measure`:
- Map each key-value pair

## Spacing

From `spacing`:
- `base` → `--space-unit`
- `scale` array → `--space-3xs`, `--space-2xs`, `--space-xs`, `--space-sm`, `--space-md`, `--space-lg`, `--space-xl`, `--space-2xl`, `--space-3xl`

## Affect

From `affect`:
- Map each key-value pair as `--affect-{key}: {value}`

# Guidelines

- Slugify names: lowercase, replace spaces and underscores with hyphens
- Omit sections that don't exist in the source style.yaml
- Preserve numeric precision (don't round floats)
- Group related properties with comments

# Missing Sections

If style.yaml lacks a section (typography, spacing, etc.):

- Omit that section entirely from output
- Do not generate placeholder values
- Document omission in header comment if significant

# Example Output

For a minimal noir style:

```css
/**
 * Design Tokens
 * Generated from style.yaml
 * Cinematic tension. Deep shadows, punctuated light.
 */

:root {
  /* Color System */
  --color-void: #0a0a0a;
  --color-shadow: #1a1a1a;
  --color-danger: #ff4444;
  --color-highlight: #f4f4f4;

  /* Affect */
  --affect-temperature: -0.6;
  --affect-weight: 0.7;
  --affect-energy: 0.2;
}
```

---

---

PREVIOUS README

---

---

# Mood System

Moodboards as agent-readable YAML + tokenized CSS.

gen-mood

 analyze.md                     # image → spec
    compose.md                     # specs → mood

## Structure

```text
style/
  commands/                        # symlinked to ~/.claude/commands/guide/
    gen-mood.md                    # find and collect images
   
  {name}/
    *.png, *.jpg    # reference images
    *.spec.yaml     # per-image specs
    style.yaml      # composed style
    tokens.css      # exported CSS variables
```

## Workflow

### Curate

```text
/guide:gen-moodboard-exemplars noir
```

Interactive image collection:

1. Describe the aesthetic you want
2. Review options, refine (more of X, less of Y)
3. Collect selected images to `style/{name}/`

Images are renamed: `01-noir-alley-rain.jpg`, `02-neon-fog-silhouette.png`

### Align

```bash
just style-align
```

1. Finds images without `.spec.yaml`
2. Shows list, asks to proceed
3. Analyzes each image → spec
4. Composes each touched directory → style
5. Exports each style → tokens.css

## Directives

End-of-line comments control composition behavior:

```yaml
intent: "cinematic tension"  # LOCKED
palette:
  primary: "void black"      # IMPORTANT
```

| Directive     | Behavior                               |
|---------------|----------------------------------------|
| `# LOCKED`    | Frozen. Composition preserves exactly. |
| `# IMPORTANT` | Wins conflicts during merge.           |

## Lexicon

Naming conventions that guide without restricting. Each line cascades effect throughout contained elements.

### Principles

Cascade First: Set once, inherit everywhere.

```css
--color-text        /* sets default, children inherit */
--color-text-muted  /* explicit override when needed */
```

Semantic Over Literal: Names communicate intent, not implementation.

```text
Avoid:  --color-005, --space-32, --gray-400
Prefer: --color-sand, --space-generous, --color-muted
```

Constraint as Liberation: Fewer options, faster decisions.

- 3-5 spacing sizes, not 12
- Role-based colors, not enumerated slots
- Purpose-driven typography, not weight/size matrices

### Naming Pattern

```text
--{category}-{role}-{modifier}
```

| Segment  | Examples                               |
|----------|----------------------------------------|
| category | color, space, type, radius, shadow     |
| role     | text, accent, surface, border, primary |
| modifier | muted, hover, strong, relaxed, tight   |

Omit segments when unnecessary. `--color-text` before `--color-text-default`.

### Tiers

```text
Layer 1: Primitives     --raw-blue-600
Layer 2: Semantics      --color-accent, --space-lg
Layer 3: Variants       --color-accent-hover, --space-lg-relaxed
Layer 4: Components     --button-background, --card-padding
```

Each tier references the one below. Change a primitive, semantics update.

### Color Roles

```css
/* Surface */
--color-surface, --color-surface-raised, --color-surface-sunken

/* Text */
--color-text, --color-text-muted, --color-text-inverted

/* Accent */
--color-accent, --color-accent-hover, --color-accent-muted

/* Semantic */
--color-success, --color-warning, --color-danger

/* Border */
--color-border, --color-border-muted
```

### Space Scale

T-shirt sizes, not pixels:

```css
--space-3xs   /* 4px  */    --space-lg    /* 24px */
--space-2xs   /* 6px  */    --space-xl    /* 32px */
--space-xs    /* 8px  */    --space-2xl   /* 48px */
--space-sm    /* 12px */    --space-3xl   /* 64px */
--space-md    /* 16px */
```

### Typography

Purpose, not metrics:

```css
--type-xs, --type-sm, --type-md, --type-lg, --type-xl, --type-2xl, --type-3xl
--weight-normal, --weight-medium, --weight-semibold, --weight-bold
--leading-tight, --leading-base, --leading-relaxed
--measure-narrow, --measure-base, --measure-wide
```

### Affect

Design feel as variables:

```css
--affect-temperature   /* -1 cold ... 1 warm */
--affect-weight        /* -1 light ... 1 heavy */
--affect-energy        /* -1 calm ... 1 energetic */
```

These guide generation, not direct application.

### Composition

Inheritance chains propagate changes:

```css
:root {
  --color-accent: var(--raw-blue-600);
  --button-background: var(--color-accent);
}
```

Cascading defaults flow to children:

```css
body { color: var(--color-text); }
.caption { color: var(--color-text-muted); }  /* override when needed */
```

### Anti-Patterns

- Hardcoded values bypassing tokens
- Over-specified names (--button-primary-background-hover-desktop-dark)
- Enumerated slots (--color-01 through --color-20)
- Flat structure without semantic tiers

### The Subtle Potential

The lexicon creates latent energy through productive tensions:

| Tension              | Resolution                                            |
|----------------------|-------------------------------------------------------|
| Constraint / Freedom | Core tokens fixed, modifiers enable variation         |
| Specific / General   | Semantics reference roles, roles reference primitives |
| Inherit / Override   | Cascade flows down, explicit declarations interrupt   |

Constraints that whisper, not shout. Names evoke intent. Structure permits local adaptation. The system feels intentional, not mechanical.

## Aesthetic Philosophy

UX laws optimize for novice, task-focused, efficiency-oriented users. This system serves a different context: creative practitioners who value expression, depth, and intentionality.

### When Convention Applies

Follow conventional wisdom when:

- Users are new to the domain
- Tasks are transactional (complete and leave)
- Speed and efficiency are primary goals
- Errors are costly and irreversible

### When to Break Rules

Deliberately violate convention when:

- Expression advances the core purpose
- Audience expertise can be assumed
- Authenticity requires visible constraint
- Intentional friction serves the user
- Depth requires mystery
- Beauty needs complexity

### Permissions

This system explicitly permits:

```text
Density over hand-holding       Expert users want information, not tutorials
Friction for irreversibles      Slow down deletions, commitments, payments
Rawness over polish             Visible craft signals authenticity
Learned affordances             Reward returning users with depth
Asymmetric hierarchy            Break visual consistency for emphasis
Typography as argument          Type can whisper, declare, or challenge
```

### The Carson Principle

"Don't mistake legibility for communication."

A perfectly legible interface that communicates blandness fails. An unconventional interface that communicates intention succeeds. Message comes first. Legibility serves message, not the reverse.

### Productive Friction

Not all friction is bad. Intentional friction:

- Enforces deliberation before irreversible actions
- Creates investment that deepens engagement
- Signals that something matters
- Respects user agency over passive consumption

### Context Determines Everything

The same design choice can be right or wrong depending on:

| Context           | Approach                     |
|-------------------|------------------------------|
| Public onboarding | Familiar, guided, forgiving  |
| Expert tool       | Dense, learned, efficient    |
| Creative platform | Expressive, surprising, deep |
| Safety-critical   | Clear, redundant, deliberate |

Document the assumption: for whom and why this interface exists.

## Behavior

Running `just style-align` is idempotent for unchanged images:

- Images with existing specs are skipped
- Composition and export run on touched directories only
- Manual edits to style.yaml with `# LOCKED` are preserved

## Troubleshooting

Image produces poor spec:

- Add more reference images to dilute influence
- Or manually edit the spec.yaml, add `# LOCKED` to key values

Composition loses important detail:

- Mark critical values with `# IMPORTANT` in style.yaml before running
- Or lock entire sections with `# LOCKED`

Export missing sections:

- Ensure style.yaml has the section defined
- Export only outputs what exists in source

## FAQ

Q: Can I hand-edit style.yaml?

A: Yes. Use `# LOCKED` to preserve edits across recomposition.

Q: What makes a good reference image?

A: Clear aesthetic intent, good resolution, representative of desired mood.

Q: How do I version styles?

A: Commit style.yaml and tokens.css. Specs are derived, can regenerate.
