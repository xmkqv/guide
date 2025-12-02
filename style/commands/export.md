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
