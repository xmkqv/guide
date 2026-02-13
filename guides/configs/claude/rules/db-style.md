---
paths:
  - "./**/*.sql"
---

Write declarative & self-explanatory SQL. No comments.

Filenames: `{schema-number}{entry-number}_{schema}_{name}.sql`
Format: { lowercase, snake_case }

```form:sql-entry
{table}

{indexes}

{primitives}

{triggers}

{rls} -- ie alter table ... enable row level security;

{policies}
```

```form:sql-migration-file
{entries}
```

# Reminders

Use fully qualified names in function bodies
No tautological comments eg do not use `-- table trace.tx` over `create table trace.tx(...)`
No non-native comments eg do not use `-- ...` over `comment on ...`
