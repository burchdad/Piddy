---
name: rust
description: Systems programming in Rust with ownership, lifetimes, traits, async, and the ecosystem (Cargo, Tokio, Serde)
---

# Rust Development

## Core Language
- Ownership: each value has exactly one owner, ownership moves on assignment
- Borrowing: &T (shared/immutable), &mut T (exclusive/mutable) — can't have both simultaneously
- Lifetimes: 'a annotations, lifetime elision rules, 'static
- Variables: let (immutable by default), let mut, shadowing
- Types: i8-i128, u8-u128, f32, f64, bool, char, str, String
- Tuples: (T1, T2), destructuring, unit type ()
- Enums: variants with data, Option<T> (Some/None), Result<T, E> (Ok/Err)
- Pattern matching: match (exhaustive), if let, while let, let-else
- Structs: named fields, tuple structs, unit structs, impl blocks
- Traits: define shared behavior, default methods, supertraits
- Generics: <T>, trait bounds (T: Display + Clone), where clauses
- Closures: |args| body, Fn/FnMut/FnOnce traits, move closures
- Iterators: iter(), into_iter(), iter_mut(), adaptor chains, collect()
- Error handling: Result with ? operator, thiserror for libraries, anyhow for applications

## Ownership Deep Dive
- Stack vs heap: Copy types (primitives) vs Move types (String, Vec)
- Clone: explicit deep copy via .clone()
- Drop: automatic cleanup when owner goes out of scope
- Rc<T>: reference counting for shared ownership (single-thread)
- Arc<T>: atomic reference counting (multi-thread)
- Box<T>: heap allocation, trait objects (Box<dyn Trait>)
- Cow<'a, T>: clone-on-write for flexible borrowing

## Collections
- Vec<T>: growable array, push, pop, indexing, slicing
- HashMap<K, V>: entry API (or_insert, or_insert_with)
- HashSet<T>: unique values, set operations
- BTreeMap, BTreeSet: ordered variants
- VecDeque: double-ended queue
- String: owned UTF-8, &str: borrowed UTF-8 slice

## Traits and Generics
- Common traits: Display, Debug, Clone, Copy, PartialEq, Eq, Hash, Default, From/Into
- Derive macros: #[derive(Debug, Clone, PartialEq)]
- Trait objects: dyn Trait for dynamic dispatch
- Associated types vs generic parameters
- Blanket implementations
- Operator overloading via std::ops traits

## Async Rust
- async fn, .await syntax
- Futures: poll-based, lazy execution
- Tokio runtime: #[tokio::main], spawn, JoinHandle
- async channels: tokio::sync::mpsc, broadcast, watch
- Select: tokio::select! for multiplexing futures
- Streams: async iterators (futures::Stream)
- Pin and Unpin for self-referential futures
- Avoid holding locks across await points

## Cargo and Ecosystem
- Cargo.toml: dependencies, features, workspace
- Commands: cargo build, run, test, check, clippy, fmt, doc
- Features: conditional compilation, optional dependencies
- Workspaces: multi-crate projects
- Key crates: serde (serialization), tokio (async), reqwest (HTTP), sqlx (database), axum/actix-web (web), clap (CLI), tracing (logging)

## Web Development
- Axum: Router, handlers, extractors, State, middleware
- Actix-web: App, web::Data, handlers, middleware
- Serde: Serialize/Deserialize, #[serde(rename_all = "camelCase")]
- SQLx: compile-time checked queries, migrations, connection pools
- Tower: middleware layers, Service trait

## Testing
- Unit tests: #[cfg(test)] mod tests, #[test] fn
- Integration tests: tests/ directory, each file is separate crate
- assert!, assert_eq!, assert_ne!
- #[should_panic] for expected failures
- Property testing: proptest crate
- Mocking: mockall crate

## Unsafe Rust
- Unsafe blocks: dereference raw pointers, call unsafe functions, access mutable statics
- FFI: extern "C", #[no_mangle], bindgen for C headers
- Minimize unsafe scope — encapsulate in safe abstractions

## Best Practices
- Prefer &str over String in function parameters
- Use iterators over manual loops — they optimize to the same code
- Leverage the type system: newtype pattern, enums for state machines
- Handle all errors — don't unwrap() in production code
- Run clippy and fix all warnings
- Use #[must_use] on types/functions where ignoring results is a bug
- Prefer compile-time guarantees over runtime checks
