# Java Coding Standards

## Scope: Naming, structure, modern idioms (Java 17-21)
**Authority:** Google Java Style, Oracle Code Conventions, Effective Java  
**Tools:** Checkstyle, SpotBugs, Error Prone, google-java-format  

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Package | `lowercase.dotted` | `com.example.service` |
| Class / Interface | `PascalCase` | `UserService` |
| Method | `camelCase` (verb) | `getUserById()` |
| Variable | `camelCase` | `userCount` |
| Constant | `UPPER_SNAKE` | `MAX_CONNECTIONS` |
| Type parameter | Single uppercase / descriptive | `T`, `K`, `V`, `E` |
| Boolean method | `is/has/can` prefix | `isActive()` |
| Enum member | `UPPER_SNAKE` | `Status.ACTIVE` |

## Modern Idioms

```java
// Prefer records for data carriers
record UserDTO(String name, String email) {}

// Prefer sealed hierarchies for known subtypes
sealed interface Shape permits Circle, Rectangle {}

// Prefer var for local variables with obvious types
var users = new ArrayList<User>();
var config = loadConfig();

// Prefer switch expressions over statements
var label = switch (status) {
    case 200 -> "OK";
    case 404 -> "Not Found";
    default -> "Unknown";
};

// Prefer Optional over null returns
Optional<User> findById(int id) { }
// NEVER: Optional as method parameter or field
```

## Error Handling

```java
// Prefer specific exceptions
throw new UserNotFoundException("ID: " + id);

// Catch specific, not generic
try { parseConfig(path); }
catch (IOException e) { logger.error("Config read failed", e); throw; }

// NEVER catch Throwable/Error (except at top-level)
// NEVER swallow exceptions silently
// Use try-with-resources for AutoCloseable
try (var conn = dataSource.getConnection();
     var stmt = conn.prepareStatement(sql)) {
    // ...
}
```

## Project Structure

```
src/main/java/com/example/
├── config/              # Configuration classes
├── controller/          # REST controllers
├── service/             # Business logic
├── repository/          # Data access
├── model/               # Domain objects
│   ├── entity/
│   └── dto/
└── exception/           # Custom exceptions

src/test/java/com/example/
└── (mirrors main structure)
```
