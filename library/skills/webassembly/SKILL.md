---
name: webassembly
description: WebAssembly for high-performance web applications, WASI, and compilation from Rust, C++, and other languages
---

# WebAssembly Development

## Core Concepts
- Binary instruction format: runs at near-native speed in browsers
- Stack-based virtual machine: portable, sandboxed execution
- Module: compiled unit containing functions, memory, tables, globals
- Linear memory: shared ArrayBuffer between WASM and JavaScript
- Type system: i32, i64, f32, f64, v128 (SIMD), funcref, externref
- WAT (Web Assembly Text): human-readable format for debugging
- Compilation: source language → WASM binary (.wasm file)

## Rust to WASM
- wasm-pack: build tool for Rust-WASM packages
- wasm-bindgen: bridge between Rust and JavaScript
- #[wasm_bindgen]: export Rust functions to JS, import JS functions
- Web-sys: Rust bindings to Web APIs (DOM, fetch, WebGL)
- js-sys: Rust bindings to JavaScript built-in objects
- Cargo.toml: crate-type = ["cdylib"], wasm-opt for optimization
- wasm-pack build --target web/bundler/nodejs

## C/C++ to WASM
- Emscripten: C/C++ to WASM compiler toolchain
- emcc: compiler frontend, -O2/-O3 for optimization, -s flags
- Exported functions: EMSCRIPTEN_KEEPALIVE, EXPORTED_FUNCTIONS
- Memory: emscripten_malloc, passing arrays between C and JS
- File system: Emscripten virtual file system, preloading data
- Pthreads: SharedArrayBuffer for multithreading

## JavaScript Integration
- Instantiation: WebAssembly.instantiate, WebAssembly.instantiateStreaming
- Import object: functions JS provides to WASM module
- Exports: functions WASM provides to JavaScript
- Memory: WebAssembly.Memory, grow(), buffer as typed arrays
- Table: WebAssembly.Table for indirect function calls
- String passing: encode to UTF-8 bytes, write to linear memory, pass pointer+length

## WASI (WebAssembly System Interface)
- Standardized system calls: file I/O, sockets, clocks, random
- Capability-based security: explicit permission grants
- Runtimes: Wasmtime, Wasmer, WasmEdge
- Server-side WASM: portable binaries, sandboxed execution
- Component Model: composable WASM components with typed interfaces

## Use Cases
- Compute-intensive: image/video processing, cryptography, physics simulations
- Porting native code: games (Unity, Unreal), codecs, compilers
- Libraries: SQLite in browser, PDF rendering, compression (zstd, brotli)
- Edge computing: Cloudflare Workers, Fastly Compute, serverless WASM
- Plugin systems: sandboxed extensibility for applications

## Performance
- SIMD: v128 operations for parallel data processing
- Multi-threading: SharedArrayBuffer + Atomics
- Streaming compilation: compile while downloading
- Memory management: explicit allocation, no garbage collector overhead
- Profile: browser DevTools, wasm-opt for binary optimization
- Size: wasm-opt -Oz, tree-shaking unused exports

## Best Practices
- Keep WASM boundary crossings minimal — batch data transfers
- Use typed arrays for efficient memory sharing with JS
- Compile with optimization flags for production
- Use streaming instantiation (instantiateStreaming) for faster load
- WASM for compute, JS for DOM — don't try to do everything in WASM
- Test with multiple runtimes/browsers for compatibility
- Monitor binary size — strip debug info, use wasm-opt
