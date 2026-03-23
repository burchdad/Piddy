# Rust Coding Standards

## Scope: Naming, ownership idioms, error handling, API design
**Authority:** Rust API Guidelines, Clippy lints, Rust RFC style  
**Tools:** cargo clippy, cargo fmt, miri, cargo audit  

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Type / Trait / Enum | `PascalCase` | `UserService`, `Display` |
| Function / Method | `snake_case` | `get_user_by_id` |
| Variable / field | `snake_case` | `user_count` |
| Constant | `UPPER_SNAKE` | `MAX_RETRIES` |
| Module / crate | `snake_case` | `user_service`, `my_crate` |
| Type parameter | Short uppercase | `T`, `K`, `V` |
| Lifetime | Short lowercase `'a` | `'a`, `'static` |
| Conversion | `from_*`, `to_*`, `into_*`, `as_*` | `from_str`, `to_string` |
| Fallible | `try_*` | `try_parse` |
| Bool getter | `is_*`, `has_*` | `is_empty`, `has_value` |

## Error Handling

```rust
// Use Result<T, E> for fallible operations (never panic for expected errors)
fn load_config(path: &Path) -> Result<Config, AppError> { }

// Use thiserror for library error types
#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("not found: {0}")]
    NotFound(String),
    #[error("io error")]
    Io(#[from] std::io::Error),
}

// Use anyhow for application-level error handling
fn main() -> anyhow::Result<()> {
    let config = load_config("config.toml")
        .context("Failed to load configuration")?;
    Ok(())
}

// NEVER .unwrap() in production — use .expect("reason") at minimum
// Prefer ? operator over manual match on Result
```

## Ownership Patterns

```rust
// Take ownership only when you need it
fn process(data: Vec<u8>) { }         // takes ownership
fn inspect(data: &[u8]) { }           // borrows (preferred if not consuming)
fn modify(data: &mut Vec<u8>) { }     // mutable borrow

// Prefer &str over &String, &[T] over &Vec<T>
fn greet(name: &str) { }              // accepts String, &str, Cow<str>

// Use Cow<str> for "maybe owned" data
fn normalize(input: &str) -> Cow<str> {
    if input.contains(' ') {
        Cow::Owned(input.replace(' ', "_"))
    } else {
        Cow::Borrowed(input)
    }
}

// Clone is a code smell — justify each .clone()
```

## Derive & Traits

```rust
// Derive common traits on data types
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct UserId(u64);

// Implement Display for user-facing output
impl fmt::Display for UserId {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "user:{}", self.0)
    }
}

// Use From/Into for conversions
impl From<u64> for UserId {
    fn from(id: u64) -> Self { UserId(id) }
}
```
