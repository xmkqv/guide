---
name: Gen Moodboard Exemplars
description: Help the user find and collect images that capture a specific aesthetic for a style moodboard
argument-hint: {name} {jumble}
---

# Role

You are curating reference images for a style moodboard named `$ARGUMENTS[0]`.

Initial brief: `$ARGUMENTS[1:]`

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

1. Download to `$GUIDE_DIR/style/{moodboard}/`
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

| Need | Go to |
|------|-------|
| Cinematic, moody, filmic | Film Grab, Shot Deck |
| Clean photography, stock | Unsplash, Pexels (rotate between them) |
| Editorial, typography | Fonts In Use, Typewolf |
| UI/product design | Dribbble, Mobbin, Behance |
| Data viz, charts | Observable, Information is Beautiful |
| Textures, patterns | Poly Haven, Hero Patterns |
| Color palettes | Cinema Palettes, Coolors |
| Icons | Lucide, Phosphor |

Don't default to Unsplash for everything. A moodboard for "cinematic noir" should pull from Film Grab. A moodboard for "swiss typography" should pull from Fonts In Use.

# Sources

Go directly to sources with downloadable assets. Don't waste time on generic web search.

## Photography

| Source | URL | Notes |
|--------|-----|-------|
| Unsplash | `source.unsplash.com/random/?{query}` | Direct image URL, no API key |
| Unsplash API | `api.unsplash.com/photos/random?query={q}` | JSON response, needs key |
| Pexels API | `api.pexels.com/v1/search?query={q}` | JSON response, needs key |
| Lorem Picsum | `picsum.photos/seed/{seed}/{w}/{h}` | Random but reproducible |
| Wikimedia Commons | `commons.wikimedia.org/wiki/Special:Search/{q}` | Historical, scientific, public domain |

## Icons

| Source | URL | Notes |
|--------|-----|-------|
| Lucide | `lucide.dev/icons/{name}` | Line icons, SVG |
| Heroicons | `heroicons.com` | UI icons, Tailwind ecosystem |
| Simple Icons | `simpleicons.org` | Brand/logo icons |
| Feather | `feathericons.com` | Minimal line icons |
| Phosphor | `phosphoricons.com` | Variable weight icons |

## Illustration

| Source | URL | Notes |
|--------|-----|-------|
| unDraw | `undraw.co/illustrations` | Flat vector, customizable color |
| Humaaans | `humaaans.com` | Mix-and-match people |
| Open Peeps | `openpeeps.com` | Hand-drawn people |
| Blush | `blush.design` | Multiple illustration styles |
| Storyset | `storyset.com` | Animated illustrations |

## Data Viz

| Source | URL | Notes |
|--------|-----|-------|
| Observable | `observablehq.com` | D3 examples, interactive |
| Datawrapper | `datawrapper.de` | Clean chart examples |
| RAWGraphs | `rawgraphs.io` | Unusual chart types |
| Information is Beautiful | `informationisbeautiful.net` | Award-winning viz |

## Textures / Patterns

| Source | URL | Notes |
|--------|-----|-------|
| Subtle Patterns | `subtlepatterns.com` | Tiling backgrounds |
| Hero Patterns | `heropatterns.com` | SVG patterns, customizable |
| Transparent Textures | `transparenttextures.com` | Overlay textures |
| Poly Haven | `polyhaven.com/textures` | PBR textures, free |

## Film / Cinematography

| Source | URL | Notes |
|--------|-----|-------|
| Film Grab | `film-grab.com` | Curated film stills |
| Evan Richards | `evanerichards.com` | Cinematography frames |
| Shot Deck | `shotdeck.com` | Searchable film stills |
| Cinema Palettes | `cinemapalettes.com` | Color palettes from films |

## 3D / Mockups

| Source | URL | Notes |
|--------|-----|-------|
| Poly Haven | `polyhaven.com` | HDRIs, textures, models |
| Sketchfab | `sketchfab.com` | 3D model previews |
| Cleanmock | `cleanmock.com` | Device mockups |
| Mockup World | `mockupworld.co` | Free PSD mockups |

## Typography

| Source | URL | Notes |
|--------|-----|-------|
| Google Fonts | `fonts.google.com` | Font specimens |
| Typewolf | `typewolf.com` | Type in use, pairings |
| Fonts In Use | `fontsinuse.com` | Real-world typography |
| Font Review Journal | `fontreviewjournal.com` | Deep font analysis |

## Design Inspiration

| Source | URL | Notes |
|--------|-----|-------|
| Dribbble | `dribbble.com` | UI/visual design |
| Behance | `behance.net` | Full projects |
| Godly | `godly.website` | Web design |
| Mobbin | `mobbin.com` | Mobile UI patterns |
| Awwwards | `awwwards.com` | Award-winning sites |

## Color

| Source | URL | Notes |
|--------|-----|-------|
| Coolors | `coolors.co` | Palette generator |
| Adobe Color | `color.adobe.com` | Extract from images |
| Realtime Colors | `realtimecolors.com` | Preview on UI |
| Happy Hues | `happyhues.co` | Curated palettes in context |

## API Keys

Available via direnv:

- `$UNSPLASH_ACCESS_KEY`
- `$PEXELS_API_KEY`

Prefer API access for reliable direct URLs.

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
Added to style/{moodboard}/:

  01-noir-alley-rain.jpg
  02-neon-fog-silhouette.png
  03-brutalist-concrete-shadow.jpg

Run style-align?
```
