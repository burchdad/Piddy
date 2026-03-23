---
name: go
description: Complete Go programming including concurrency, web services, modules, testing, and cloud-native patterns
---

# Go Development

## Core Language
- Static typing with type inference (:= short declaration)
- Basic types: int, float64, string, bool, byte, rune
- Composite types: arrays, slices, maps, structs
- Slices: make, append, copy, slicing syntax [low:high:max]
- Maps: make(map[K]V), delete, comma-ok idiom (val, ok := m[key])
- Pointers: &, *, no pointer arithmetic
- Structs: field tags (`json:"name"`), embedding for composition
- Interfaces: implicit implementation, empty interface (any), type assertions, type switches
- Functions: multiple return values, named returns, variadic (...args)
- Error handling: error interface, errors.New, fmt.Errorf with %w wrapping
- Defer: LIFO execution, common for cleanup (file.Close, mutex.Unlock)
- Init functions: package-level initialization

## Generics (Go 1.18+)
- Type parameters: func Foo[T any](x T) T
- Type constraints: comparable, ordered, custom interfaces
- Type sets in interfaces: int | float64 | string
- Constraint packages: golang.org/x/exp/constraints

## Concurrency
- Goroutines: go func() for lightweight concurrent execution
- Channels: make(chan T), buffered channels make(chan T, size)
- Channel operations: send (<-), receive (<-), close, range over channel
- Select statement: multiplexing channel operations, default for non-blocking
- sync package: Mutex, RWMutex, WaitGroup, Once, Pool
- Context: context.Background(), WithCancel, WithTimeout, WithValue
- errgroup for coordinated goroutine error handling
- Patterns: fan-in, fan-out, pipeline, worker pool, semaphore

## Standard Library
- net/http: HTTP server (http.ListenAndServe, Handler, HandlerFunc, ServeMux)
- encoding/json: Marshal, Unmarshal, json.Decoder for streaming
- io: Reader, Writer interfaces — composability
- os: file operations, environment variables, signals
- fmt: Stringer interface, format verbs (%v, %+v, %#v, %w)
- testing: Test, Benchmark, Fuzz functions
- log/slog: structured logging (Go 1.21+)
- database/sql: DB, Tx, Rows, prepared statements, connection pool

## Web Frameworks and Libraries
- Standard library net/http for simple services
- Chi: lightweight router with middleware support
- Gin: high-performance HTTP framework
- Echo: minimalist web framework
- gRPC: Protocol Buffers, service definitions, interceptors
- sqlx: database extensions, named queries, struct scanning
- GORM: ORM with auto-migration, associations, hooks

## Modules and Packages
- go.mod: module path, Go version, dependencies
- go.sum: cryptographic checksums
- Commands: go mod init, go mod tidy, go get, go mod vendor
- Package design: small focused packages, avoid circular imports
- Internal packages for private code
- Exported (PascalCase) vs unexported (camelCase)

## Testing
- Table-driven tests: []struct with name, input, expected
- Subtests: t.Run("name", func(t *testing.T) {...})
- Test helpers: t.Helper() for clean stack traces
- Benchmarks: func BenchmarkX(b *testing.B) { for i := 0; i < b.N; i++ {...} }
- Fuzz tests (Go 1.18+): func FuzzX(f *testing.F)
- Testify: assert, require, mock, suite
- httptest: NewRecorder, NewServer for HTTP testing
- Race detector: go test -race

## Project Structure
```
project/
  cmd/           # Main applications
    server/
      main.go
  internal/      # Private application code
    handler/
    service/
    repository/
  pkg/           # Public library code
  api/           # API definitions (proto, openapi)
  go.mod
  go.sum
```

## Best Practices
- Accept interfaces, return structs
- Handle every error — never use _ for error returns in production
- Use context for cancellation propagation
- Prefer composition over inheritance (embed structs/interfaces)
- Keep goroutine lifetimes clear — always ensure goroutines can exit
- Use defer for cleanup immediately after resource acquisition
- Run go vet, staticcheck, and golangci-lint
- Format with gofmt/goimports (non-negotiable in Go)
