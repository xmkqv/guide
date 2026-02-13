---
name: map-md-to-yaml
description: Transform Markdown documents to structured YAML via schema-guided extraction.
meta: Command is semantic flow-based. If a flow is not defined, mechanics can be inferred from context.
argument-hint: [target_path path] [schema_details path | string] [nline-per-chunk number]
N_MAX_CONCURRENT_AGENT: 3
---

TARGET_PATH=$ARGUMENTS[0]
SCHEMA_PATH=extract-path($ARGUMENTS[1])
NLINE_PER_CHUNK=${ARGUMENTS[2]}
RESULT_DIR=parent($TARGET_PATH)/name($TARGET_PATH)/

```flow:main()
schema = load-or-infer-schema($SCHEMA_PATH)
nlinemap = create-line-map()
map(nlinemap, process-chunk)
```

```flow:create-line-map()
nline = bash`wc -l $TARGET_PATH`
nlinemap = [(start, start + NLINE_PER_CHUNK) for start in range(0, nline, NLINE_PER_CHUNK)]
```

```flow:process-chunk([start_line, end_line], schema)
chunk = bash`sed -n '${start_line},${end_line}p' $TARGET_PATH`
yaml = extract-yaml-from-markdown($schema, chunk)
```

main()

# Reminders

- Yaml must be syntax compliant.
- Yaml must be faithful to the schema.
- Do not hallucinate.
- Directly tell agents: "Do not hallucinate."
