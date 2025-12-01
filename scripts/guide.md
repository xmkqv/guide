---
model: opus
---

# Guide System Initialization

Read and internalize the guide system:

@/Users/m/guide/README.md
@/Users/m/guide/exemplar.md

## Directive

You are initializing or managing a project under the guide system. The system operates via:

```text
∆Design → ∆Code → ∆Signal
    ↑                  ↓
    └──── ∇Loss ───────┘
```

Core concepts:
- mission.yaml defines project identity, design tree, and signal tree
- Specs: Ideas (aspect_id: null) ground tenets; Directives (aspect_id: S*) decompose into testable invariants
- Signals link test results to specs, providing gradient for iteration
- Anti-fragile: Flaws reveal hidden assumptions, each failure strengthens

## Task

$ARGUMENTS

If no arguments provided: Analyze current directory for existing mission.yaml or create initial scaffold.
