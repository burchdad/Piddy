# WebAssembly Quick Reference

## Language: WebAssembly (Wasm)
**Paradigm:** Binary instruction format for stack-based VM  
**Standard:** W3C standard  
**Targets:** Browsers, Node.js, edge compute, embedded (WASI)  

## Source Languages to Wasm

| Language | Toolchain | Output |
|----------|-----------|--------|
| C/C++ | Emscripten (`emcc`) | .wasm + JS glue |
| Rust | `wasm-pack` + `wasm-bindgen` | .wasm + TS bindings |
| Go | `GOOS=js GOARCH=wasm` | .wasm + `wasm_exec.js` |
| AssemblyScript | `asc` compiler | .wasm (TS-like syntax) |

## Rust to Wasm (Most Common)

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn fibonacci(n: u32) -> u64 {
    let (mut a, mut b) = (0u64, 1u64);
    for _ in 2..=n { let t = a + b; a = b; b = t; }
    b
}
```

## JavaScript Integration

```javascript
import init, { fibonacci } from './pkg/my_wasm.js';
await init();
const result = fibonacci(40);  // near-native speed

// Low-level
const { instance } = await WebAssembly.instantiate(bytes, imports);
instance.exports.main();
```

## Build Commands

```bash
# Rust
wasm-pack build --target web

# C/C++
emcc main.c -o output.js -s WASM=1 -O2

# AssemblyScript
asc assembly/index.ts --outFile build/output.wasm --optimize
```

## Use Cases

| Use Case | Example |
|----------|---------|
| Image/video processing | Filters, codecs, format conversion |
| Cryptography | Hashing, encryption in browser |
| Scientific computing | Physics simulation, ML inference |
| Gaming | Game engines (Unity, Unreal) |
| Code execution | Sandboxed language runtimes |
