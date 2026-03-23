# Go Quick Reference

## Language: Go 1.22+
**Paradigm:** Concurrent, procedural, structural typing  
**Typing:** Static, strong, inferred  
**Compiled:** Single binary, cross-compilation built in  

## Syntax Essentials

```go
package main

import (
    "fmt"
    "errors"
)

// Variables
var name string = "Piddy"
count := 42                    // short declaration
const MaxRetries = 3

// Functions — multiple return values
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// Closures
adder := func(x int) func(int) int {
    return func(y int) int { return x + y }
}
```

## Structs & Interfaces

```go
type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email,omitempty"`
}

func (u User) String() string {
    return fmt.Sprintf("%s <%s>", u.Name, u.Email)
}

// Interfaces — implicit satisfaction
type Reader interface {
    Read(p []byte) (n int, err error)
}
```

## Generics (1.18+)

```go
func Map[T, U any](s []T, f func(T) U) []U {
    result := make([]U, len(s))
    for i, v := range s {
        result[i] = f(v)
    }
    return result
}

type Number interface {
    ~int | ~float64 | ~int64
}
```

## Concurrency

```go
// Goroutines
go processItem(item)

// Channels
ch := make(chan string)
ch := make(chan int, 100)     // buffered

// Select
select {
case msg := <-msgCh:
    handle(msg)
case <-time.After(5 * time.Second):
    fmt.Println("timeout")
case <-ctx.Done():
    return ctx.Err()
}

// errgroup (structured concurrency)
g, ctx := errgroup.WithContext(ctx)
for _, url := range urls {
    url := url
    g.Go(func() error { return fetch(ctx, url) })
}
if err := g.Wait(); err != nil { /* handle */ }
```

## Error Handling

```go
var ErrNotFound = errors.New("not found")

// Wrapping
if err != nil {
    return fmt.Errorf("loading config: %w", err)
}

// Checking
if errors.Is(err, ErrNotFound) { /* ... */ }
var valErr *ValidationError
if errors.As(err, &valErr) { /* use valErr.Field */ }
```

## Tooling

```bash
go build ./...
go test ./... -v -race
go mod init module-name
go mod tidy
go vet ./...
golangci-lint run
```
