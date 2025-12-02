# Style System

Moodboards as agent-readable YAML. Minimal code, maximal impact.

## Structure

```text
style/
  commands/                        # symlinked to ~/.claude/commands/guide/
    gen-moodboard-exemplars.md     # find and collect images
    analyze.md                     # image → spec
    compose.md                     # specs → style
    export.md                      # style → tokens
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

| Directive      | Behavior                               |
|----------------|----------------------------------------|
| `# LOCKED`     | Frozen. Composition preserves exactly. |
| `# IMPORTANT`  | Wins conflicts during merge.           |

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

| Context            | Approach                      |
|--------------------|-------------------------------|
| Public onboarding  | Familiar, guided, forgiving   |
| Expert tool        | Dense, learned, efficient     |
| Creative platform  | Expressive, surprising, deep  |
| Safety-critical    | Clear, redundant, deliberate  |

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
