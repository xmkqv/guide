---
paths:
  - "./**/*.rs"
---

Write declarative, robust, & self-explanatory Rust. No comments.

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

Prefer for-loops over iterator chains. Explicit control flow reads cleaner.

```rust
let mut results = Vec::new();
for item in items {
    if item.valid {
        results.push(item.transform());
    }
}
```

Use let-else for early returns. Guards belong at the top.

```rust
let Some(user) = users.get(&id) else {
    return Err(Error::NotFound);
};

let Ok(parsed) = input.parse::<u64>() else {
    return Err(Error::InvalidInput);
};
```

Shadow variables freely. Reuse names when the purpose stays the same.

```rust
let config = load_raw_config()?;
let config = parse_config(config)?;
let config = validate_config(config)?;
```

Use newtypes for domain concepts. Primitives leak meaning.

```rust
pub struct UserId(pub i64);
pub struct Timestamp(pub i64);
pub struct Bytes(pub Vec<u8>);

fn fetch_user(id: UserId) -> Result<User> { ... }
```

Match exhaustively. Let the compiler catch missing cases.

```rust
enum Command {
    Start,
    Stop,
    Restart,
}

match cmd {
    Command::Start => start(),
    Command::Stop => stop(),
    Command::Restart => restart(),
}
```

Use discriminated enums for state machines.

```rust
enum Connection {
    Disconnected,
    Connecting { attempt: u32 },
    Connected { socket: Socket },
    Failed { reason: String },
}
```

Propagate errors with `?`. Handle them at boundaries.

```rust
fn load_config(path: &Path) -> Result<Config> {
    let content = fs::read_to_string(path)?;
    let config = toml::from_str(&content)?;
    Ok(config)
}
```

Define custom error types. Context matters.

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

# Reminders

No tautological comments
No unsafe without justification
No unwrap in library code
