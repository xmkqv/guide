---
name: Gen Report
description: Generate analytical HTML reports with data visualization
argument-hint: [data-path] [title] [subtitle?]
---

DATA=$ARGUMENTS[0]
TITLE=$ARGUMENTS[1]
SUBTITLE=$ARGUMENTS[2]

# Output Structure

Multi-file report. One HTML file per tab.

```
$RESULTS_/{slug}/
  index.html              # Home/landing page
  {tab}.html              # One per tab
  {tab}.{subtab}.html     # Subtabs (optional)
  report.css              # Shared styles
```

# Design Tokens

```css
:root {
  --accent: #2d8a7a; --surface: #f8f7f4; --border: #dcdad6;
  --text: #1a1a18; --text-muted: #5a6268;
}
```

Chart palette: `#2d8a7a`, `#c4854a`, `#2d7a4a`, `#6a7a8a`, `#247a6a`

# Writing Style

Prohibited:
- Emdash: use comma, colon, or period
- "I'd be happy to..." / "Certainly!" / "Great question!"
- Unnecessary hedging ("perhaps", "it seems")

# Navigation

Each file is complete HTML. Navigation via links, not JavaScript.

## Tabs

```html
<nav class="tabs">
  <a class="tab" href="index.html">Home</a>
  <a class="tab active" href="overview.html">Overview</a>
  <a class="tab" href="technical.html">Technical</a>
</nav>
```

Current page gets `active` class.

## Subtabs

When a tab has subtabs, include secondary nav:

```html
<nav class="tabs">
  <a class="tab" href="index.html">Home</a>
  <a class="tab active" href="technical.html">Technical</a>
</nav>
<nav class="subtabs">
  <a class="subtab active" href="technical.pipeline.html">Pipeline</a>
  <a class="subtab" href="technical.validation.html">Validation</a>
</nav>
```

Parent tab stays active. Current subtab gets `active`.

## CSS

```css
.tabs { display: flex; border-bottom: 2px solid var(--border); margin-bottom: 1rem; }
.tab { padding: 0.75rem 1.5rem; text-decoration: none;
       font-weight: 600; color: var(--text-muted); border-bottom: 2px solid transparent; margin-bottom: -2px; }
.tab:hover { color: var(--text); }
.tab.active { color: var(--accent); border-bottom-color: var(--accent); }

.subtabs { display: flex; gap: 0.5rem; margin-bottom: 2rem; }
.subtab { padding: 0.5rem 1rem; text-decoration: none; font-size: 0.875rem;
          color: var(--text-muted); background: var(--surface); border-radius: 4px; }
.subtab:hover { color: var(--text); }
.subtab.active { color: #fff; background: var(--accent); }
```

# Page Template

Every HTML file follows this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{Page Title} - {Report Title}</title>
  <link rel="stylesheet" href="report.css">
</head>
<body>
  <header>
    <h1>{Report Title}</h1>
    <p class="subtitle">{Subtitle}</p>
  </header>

  <nav class="tabs">...</nav>
  <!-- <nav class="subtabs">...</nav> if applicable -->

  <main>
    <!-- Page content -->
  </main>

  <footer>
    <p class="text-xs">{Footer text}</p>
  </footer>
</body>
</html>
```

# Components

## Card

```html
<div class="card">Content</div>
```

## Stat Card

```html
<div class="card stat">
  <div class="stat-label">LABEL</div>
  <div class="stat-value">VALUE</div>
  <div class="stat-desc">description</div>
</div>
```

## Table

```html
<div class="card"><table>
  <thead><tr><th>Col</th></tr></thead>
  <tbody><tr><td>Data</td></tr></tbody>
</table></div>
```

## Badge

```html
<span class="badge badge-primary">TEXT</span>
```

# Charts

Plotly with template:

```javascript
{ colorway: ["#2d8a7a", "#c4854a", "#2d7a4a", "#6a7a8a", "#247a6a"],
  font: { family: "Source Sans 3", color: "#1a1a18" },
  paper_bgcolor: "#f8f7f4", plot_bgcolor: "#ffffff" }
```

# Generation

1. Read $DATA, plan tab structure
2. Create output directory: `$RESULTS_/{slug}/`
3. Generate `report.css` with all styles
4. Generate each tab file with correct nav active states
5. Verify: no emdashes, nav links valid
