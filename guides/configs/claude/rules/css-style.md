---
description: CSS Style Guide
paths:
  - "**/*.css"
---

# Layout

- `flex`, `grid` > floats, positioning hacks
- logical properties (`inline`, `block`) > physical (`left`, `right`)
- `gap` > margin-based sibling spacing
- intrinsic sizing (`min-content`, `max-content`, `fit-content`) > fixed widths
- `clamp()` for fluid sizing; `@media` only for layout structure changes

# Selectors

- class > element, ID
- flat > deep nesting (max 2 levels)
- `:where()` for zero-specificity defaults; `:is()` for grouping
- `!important` ∉ allowed (exception: utility overrides)
- kebab-case ∀ class names

# Values

- custom properties ∀ repeated values
- `rem` for font-size; `em` for component-relative spacing
- `dvh` / `svh` > `vh`; `cqi` / `vw` in `clamp()`
- `oklch` for color; `color-mix()` for derived; `light-dark()` for themes
- unitless `line-height`
- `0` > `0px`

# Structure

- one declaration block per concern
- order: positioning > display > box-model > typography > visual > misc
- no vendor prefixes (build tooling)
- no shorthand unless setting all sub-properties

# Composition

- shared properties → base class; specialize via parent context
- `.parent > .base` > `.base.base--variant`
- `>` (direct child) when DOM nesting tight + unambiguous
- native nesting (`& > .base`) to colocate specializations
- no BEM

# Naming

```conventions
size       { sm, md, lg }
speed      { fast, slow }
light      { lit, dim }
dim        dimension
  w        width
  h        height
  d        depth
pad        padding
bdr        border
bg         background
color      color
```

# Modules

- `@scope` | CSS Modules > global sheets
- colocate styles with components
- `@container` > `@media` for component-level responsiveness

invs:
  tokens (css variables) declared in global/root css module
  no accent borders (`border-inline-start` highlight stripe)
  remove unused selectors
  collapse duplicate declarations
  delete commented-out rules
