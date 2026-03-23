# Go Coding Standards

## Scope: Effective Go, naming, error handling, project layout
**Authority:** Effective Go, Go Code Review Comments, Go Proverbs  
**Tools:** gofmt, go vet, golangci-lint, staticcheck  

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Exported | `PascalCase` | `UserService`, `GetUser` |
| Unexported | `camelCase` | `userCache`, `parseConfig` |
| Package | Short, lowercase, no underscores | `http`, `user`, `config` |
| Interface (1 method) | method + `er` | `Reader`, `Writer`, `Stringer` |
| Acronyms | All caps or all lower | `HTTPClient`, `xmlParser` |
| Getter | No `Get` prefix | `Name()` not ~~`GetName()`~~ |
| File | `snake_case.go` | `user_service.go` |

**Go proverb:** "A name's length should be proportional to the distance between declaration and use."

## Error Handling

```go
// ALWAYS check errors — never ignore
result, err := doWork()
if err != nil {
    return fmt.Errorf("doWork failed: %w", err)
}

// Sentinel errors for known conditions
var ErrNotFound = errors.New("not found")

// Check with errors.Is / errors.As
if errors.Is(err, ErrNotFound) { return nil }

// Error types for extra context
type ValidationError struct {
    Field   string
    Message string
}
func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

// NEVER panic in library code
// NEVER use _ to discard errors (except in tests/examples)
```

## Interface Design

```go
// Keep interfaces small (1-3 methods)
type Reader interface { Read(p []byte) (n int, err error) }

// Accept interfaces, return structs
func NewService(repo UserRepository) *UserService { }

// Define interfaces at the consumer, not the implementor
// package handler (consumer)
type UserFinder interface {
    FindByID(ctx context.Context, id int) (*User, error)
}
```

## Project Layout

```
myapp/
├── cmd/
│   └── myapp/
│       └── main.go          # entry point
├── internal/                 # private packages
│   ├── user/
│   │   ├── service.go
│   │   ├── repository.go
│   │   └── service_test.go
│   └── config/
├── pkg/                      # public packages (optional)
├── go.mod
├── go.sum
└── README.md
```

## Concurrency Rules

```go
// ALWAYS pass context.Context as first parameter
func GetUser(ctx context.Context, id int) (*User, error) { }

// Use errgroup for structured concurrency
g, ctx := errgroup.WithContext(ctx)
g.Go(func() error { return fetchA(ctx) })
g.Go(func() error { return fetchB(ctx) })
if err := g.Wait(); err != nil { return err }

// Share by communicating, don't communicate by sharing
// Prefer channels over mutexes where practical
// Keep goroutine lifetimes obvious and bounded
```
