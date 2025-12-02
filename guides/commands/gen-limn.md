---
name: gen-diagram
description: Generate architecture diagrams using LikeC4
tools: Bash, Read, Edit, Write
permissionMode: acceptEdits
argument-hint: [path]
---

PATH=$ARGUMENTS[0]

# gen-diagram

Generate LikeC4 architecture diagrams from source.

## Input

- `$PATH`: Target directory for architecture model and output
- Project context via `--add-dir`

## Process

1. Read input file(s) to understand the system
2. Create `$PATH/architecture/` directory
3. Write `$PATH/architecture/model.c4` with rich modeling
4. Run: `bunx likec4 export png -o $PATH/output $PATH/architecture/`
5. List all generated images

## Modeling Depth

Capture full system complexity:

- All actors and external systems
- Every container and component mentioned
- All relationships and data flows
- Technology annotations where specified
- Multiple views at different abstraction levels
- Tags for status (deprecated, external, planned)

## LikeC4 Techniques

### Element Shapes

```likec4
element actor { style { shape person } }
element system { style { shape rectangle } }
element database { style { shape storage } }
element queue { style { shape queue } }
element browser { style { shape browser } }
element mobile { style { shape mobile } }
```

### Colors and Themes

```likec4
element external { style { color gray } }
element core { style { color blue } }
element deprecated { style { color amber; opacity 50% } }
```

### Rich Views

Create multiple views for different audiences:

```likec4
views {
  view index { title "System Overview"; include * }
  view containers of system { title "Containers"; include system.* }
  view detail of component { title "Component Detail"; include component, component.* }
}
```

### Relationship Styles

```likec4
user -> api "REST" { style { color green } }
api -> db "SQL" { style { line dashed } }
legacy -> new "deprecated" { style { color red; line dotted } }
```

## Output Format

One sentence describing what the diagrams show.

Then list ALL generated images:

```txt
model: $PATH/architecture/model.c4
images:
  $PATH/output/index.png
  $PATH/output/containers.png
  ...
```

## Rules

- One sentence description
- List every PNG generated
- No markdown formatting in output
