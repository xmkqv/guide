---
description: SQL Style Guide
paths:
  - "**/*.sql"
---

# Case

- all lowercase: keywords, types, functions, identifiers
- snake_case ∀ names
- fully qualified names in function bodies: `schema.object`

# Layout

- 2-space indentation
- commas at end of line
- no trailing empty line
- `select` on own line, expression indented below
- `from`, `where`, `join`, `on` each on own line
- `perform` on own line, expression indented below

# DDL

- `create function` in migrations (forward-only; `create or replace` only in test helpers)
- explicit `volatile` | `stable` | `immutable` on every function
- `returns`, `language`, volatility, `set search_path = ''` each on own line
- `references schema.table (col)` inline > separate constraints
- `primary key`, `not null`, `default` inline with column

# Naming

filenames: `{schema-number}{entry-number}_{schema}_{name}.sql`

# Structure

```form:entry
{table}
{indexes}
{primitives}
{triggers}
{rls}
{policies}
```

```form:migration
{entries}
```

# Comments

invs:
  ¬ tautological comments over self-explanatory DDL
  ¬ meta-commentary
  ¬ driftable references to spec/other modules
  ¬ commented-out SQL

# Elimination

- remove unused functions, triggers, policies
- collapse duplicate grants
- merge redundant `revoke` / `grant` statements
