# Rust Quick Reference

## Language: Rust (2024 Edition)
**Paradigm:** Systems, functional, concurrent  
**Typing:** Static, strong, affine (ownership)  
**Compiled:** LLVM backend, no runtime/GC  

## Ownership & Borrowing

```rust
// Ownership rules:
// 1. Each value has exactly one owner
// 2. When owner goes out of scope, value is dropped
// 3. Value can be moved or borrowed

let s1 = String::from("hello");
let s2 = s1;              // s1 MOVED

// Borrowing (immutable — multiple allowed)
fn len(s: &str) -> usize { s.len() }

// Mutable borrow (exclusive — only one at a time)
fn push(v: &mut Vec<i32>, val: i32) { v.push(val); }

// Lifetimes
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

## Enums & Structs

```rust
// Enum (algebraic data type)
enum Command {
    Quit,
    Move { x: i32, y: i32 },
    Say(String),
}

#[derive(Debug, Clone, PartialEq)]
struct User {
    name: String,
    age: u32,
    active: bool,
}

impl User {
    fn new(name: impl Into<String>) -> Self {
        Self { name: name.into(), age: 0, active: true }
    }
}
```

## Traits

```rust
trait Summary {
    fn summarize(&self) -> String;
    fn preview(&self) -> String {
        format!("{}...", &self.summarize()[..50])
    }
}

fn notify(item: &impl Summary) { println!("{}", item.summarize()); }
fn process<T>(item: T) where T: Summary + Clone + Send { /* ... */ }
```

## Error Handling

```rust
use thiserror::Error;

#[derive(Error, Debug)]
enum AppError {
    #[error("not found: {0}")]
    NotFound(String),
    #[error("io error")]
    Io(#[from] std::io::Error),
}

// ? operator propagates errors
fn load_config(path: &str) -> Result<Config, AppError> {
    let content = std::fs::read_to_string(path)?;
    let config = serde_json::from_str(&content)?;
    Ok(config)
}
```

## Async

```rust
#[tokio::main]
async fn main() {
    let result = fetch_data("url").await;
}

// Concurrent tasks
let (a, b) = tokio::join!(task_a(), task_b());

let handle = tokio::spawn(async { heavy_computation().await });
let result = handle.await?;
```

## Tooling

```bash
cargo new project-name
cargo build --release
cargo test
cargo clippy              # lints
cargo fmt                 # format
cargo add serde tokio
```
