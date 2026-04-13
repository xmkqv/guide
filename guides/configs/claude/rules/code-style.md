---
description: Code Style Guide
---


# Code Style

## Self-Explanatory Code

Code names carry intent. Comments that restate what the name already says are noise.

∴ Inline comments that redeclare function/mechanic intent are prohibited.

Bad:

```sql
-- resolve_ptr_type: look up the table (regclass) for a given ptr id
create function graph.resolve_ptr_type (p_id uuid)
```

Good:

```sql
create function graph.resolve_ptr_type (p_id uuid)
```

Comments are for **why**, not **what**. If the name doesn't convey intent, rename it.
