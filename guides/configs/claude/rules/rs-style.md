---
description: Rust Style Guide
paths:
  - "**/*.rs"
---

Declarative, robust, self-explanatory Rust. No comments.

```rust
use std::collections::HashMap;

const BUFFER_SIZE: usize = 4096;

pub struct Handler {
    state: State,
    cache: HashMap<Key, Value>,
}

impl Handler {
    pub fn new() -> Self { ... }
    pub fn process(&mut self, input: Input) -> Result<Output> { ... }
}
```

# Control Flow

for-loops > iterator chains

```rust
let mut results = Vec::new();
for item in items {
    if item.valid {
        results.push(item.transform());
    }
}
```

let-else for early returns; guards at top

```rust
let Some(user) = users.get(&id) else {
    return Err(Error::NotFound);
};
```

# Shadowing

shadow freely; reuse names when purpose unchanged

```rust
let config = load_raw_config()?;
let config = parse_config(config)?;
let config = validate_config(config)?;
```

# Newtypes

newtypes for domain concepts; primitives leak meaning

```rust
pub struct UserId(pub i64);
pub struct Timestamp(pub i64);
pub struct Bytes(pub Vec<u8>);

fn fetch_user(id: UserId) -> Result<User> { ... }
```

# Matching

exhaustive match; let compiler catch missing cases

```rust
enum Command { Start, Stop, Restart }

match cmd {
    Command::Start => start(),
    Command::Stop => stop(),
    Command::Restart => restart(),
}
```

discriminated enums for state machines

```rust
enum Connection {
    Disconnected,
    Connecting { attempt: u32 },
    Connected { socket: Socket },
    Failed { reason: String },
}
```

# Errors

propagate with `?`; handle at boundaries

```rust
fn load_config(path: &Path) -> Result<Config> {
    let content = fs::read_to_string(path)?;
    let config = toml::from_str(&content)?;
    Ok(config)
}
```

custom error types; context matters

```rust
#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("io: {0}")]
    Io(#[from] std::io::Error),
    #[error("parse: {0}")]
    Parse(#[from] toml::de::Error),
    #[error("not found: {0}")]
    NotFound(String),
}
```

invs:
  ¬ tautological comments
  ¬ unsafe without justification
  ¬ unwrap in library code
