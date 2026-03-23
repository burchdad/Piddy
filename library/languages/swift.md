# Swift Quick Reference

## Language: Swift 5.9+
**Paradigm:** OOP, functional, protocol-oriented  
**Typing:** Static, strong, inferred  
**Platforms:** iOS, macOS, watchOS, tvOS, Linux, Windows  

## Syntax Essentials

```swift
let name = "Piddy"          // constant (preferred)
var count = 0                // mutable

// Optionals
var email: String? = nil
let len = email?.count ?? 0
guard let email = email else { return }

// Closures
let sorted = names.sorted { $0 < $1 }
let mapped = nums.map { $0 * 2 }
```

## Enums & Structs

```swift
enum NetworkError: Error {
    case notFound
    case serverError(code: Int, message: String)
}

struct User: Codable, Hashable {
    let id: Int
    var name: String
    var email: String?
}
```

## Protocols

```swift
protocol Drawable {
    func draw()
}

extension Collection where Element: Numeric {
    var sum: Element { reduce(.zero, +) }
}

func makeShape() -> some Drawable { Circle() }    // opaque
func anyShape() -> any Drawable { shapes.first! }  // existential
```

## Concurrency (async/await)

```swift
func fetchUser(id: Int) async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// Structured concurrency
async let user = fetchUser(id: 1)
async let posts = fetchPosts(userId: 1)
let (u, p) = try await (user, posts)

// Actor (thread-safe state)
actor Counter {
    private var value = 0
    func increment() -> Int { value += 1; return value }
}
```

## Tooling

```bash
swift build
swift test
swift run
swift package init --type executable
```
