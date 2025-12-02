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
