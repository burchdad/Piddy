# Swift & Kotlin Coding Standards

## Scope: Mobile development conventions for iOS and Android
**Authority:** Swift API Design Guidelines, Kotlin Coding Conventions  
**Tools:** SwiftLint, ktlint, detekt  

## Swift Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Type / Protocol | `PascalCase` | `UserProfile`, `Drawable` |
| Method / Property | `camelCase` | `makeNoise()`, `isActive` |
| Factory method | `make` prefix | `makeIterator()` |
| Boolean | `is/has/should` prefix | `isEmpty`, `canEdit` |
| Protocol (capability) | `-able/-ible` suffix | `Codable`, `Hashable` |

**Swift API Design Guidelines:**
- Clarity at the point of use
- Prefer method names that read as English phrases
- `func move(from start: Point, to end: Point)` — label all arguments

## Kotlin Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Class / Object | `PascalCase` | `UserViewModel` |
| Function / Property | `camelCase` | `fetchUser()`, `isActive` |
| Constant | `UPPER_SNAKE` or `camelCase` | Top: `MAX_COUNT`, local: `maxCount` |
| Package | `lowercase.dotted` | `com.example.feature.user` |
| Backing property | `_prefix` | `private val _users = MutableStateFlow(...)` |
| Flow / LiveData | no `get` prefix | `val users: StateFlow<List<User>>` |

## Shared Mobile Patterns

| Pattern | Do | Don't |
|---------|-----|-------|
| Nullability | Use platform null safety (`?`, `!!` sparingly) | Force unwrap everywhere |
| Immutability | `val`/`let` by default | `var` unless mutation needed |
| Error handling | Result types, sealed classes | Generic catch-all |
| Dependency injection | Constructor injection | Service locator |
| Architecture | MVVM / MVI with clean layers | God Activity / ViewController |
| Async | Coroutines (Kotlin) / async-await (Swift) | Callback pyramids |
