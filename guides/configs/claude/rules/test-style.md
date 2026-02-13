---
paths:
    - "**/tests/**/*"
---

# Philosophy

Classical TDD (Kent Beck): real collaborators; mocks only at infrastructure boundaries
Sociable tests (Jay Fields): units tested with their real dependencies
Testing Trophy (Kent C. Dodds): integration layer is the widest
Testing Without Mocks (James Shore): real implementations everywhere; Nullables only for infrastructure
Don't Mock What You Don't Own (Steve Freeman, Nat Pryce): only fake boundaries for which you control the contract
Generative testing (QuickCheck, Claessen & Hughes): generators produce inputs; assert invariants not specific values

# Rules

real: Use real implementations; only stub infrastructure boundaries (db, network, wasm, clock, ...)
generators: Use generators for test data; hand-craft only the fields under test
observable: Assert on store state and emissions, not internal call counts
no-mock: Do not mock or spy on internal modules
boundaries: Infrastructure stubs live in tests/data/; one per boundary
