---
name: gen-limn
description: Generate architecture diagrams using LikeC4
argument-hint: [path]
---

PATH=$ARGUMENTS[0]
LIMN_=$RESULTS_/limn

# Output

```text
$LIMN_/
  model.c4    # LikeC4 model
  *.png       # rendered views
```

# Process

1. Read $PATH to understand the system
2. Write $LIMN_/model.c4
3. Run: `bunx likec4 export png -o $LIMN_ $LIMN_/`
4. List generated images

# Modeling

Capture full system complexity:

- Actors and external systems
- Containers and components
- Relationships and data flows
- Technology annotations
- Multiple views at different abstraction levels
- Tags for status (deprecated, external, planned)

# LikeC4

```likec4
element actor { style { shape person } }
element database { style { shape storage } }
element queue { style { shape queue } }

element external { style { color gray } }
element deprecated { style { color amber; opacity 50% } }

views {
  view index { title "System Overview"; include * }
  view containers of system { include system.* }
}

user -> api "REST" { style { color green } }
api -> db "SQL" { style { line dashed } }
```

# Output

```text
$LIMN_/model.c4
$LIMN_/index.png
$LIMN_/containers.png
...
```
