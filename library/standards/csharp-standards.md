# C# Coding Standards

## Scope: Naming, patterns, modern C# 10-12 idioms
**Authority:** Microsoft .NET Framework Design Guidelines, Roslyn analyzers  
**Tools:** dotnet format, Roslynator, SonarAnalyzer  

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Class / Struct / Record | `PascalCase` | `UserService` |
| Interface | `IPascalCase` | `IUserRepository` |
| Method / Property | `PascalCase` | `GetUser()`, `IsActive` |
| Local variable / parameter | `camelCase` | `userName`, `retryCount` |
| Private field | `_camelCase` | `_logger`, `_cache` |
| Constant | `PascalCase` | `MaxRetries` |
| Enum | `PascalCase` (singular) | `Color.Red` |
| Namespace | `Company.Product.Area` | `Piddy.Core.Services` |
| Async method | `...Async` suffix | `GetUserAsync()` |

## Modern Idioms (C# 10-12)

```csharp
// Use file-scoped namespaces
namespace MyApp.Services;

// Use records for immutable data
record UserDto(string Name, string Email);

// Use primary constructors for DI (C# 12)
class UserService(IRepository repo, ILogger<UserService> logger)
{
    public User? Find(int id) => repo.GetById(id);
}

// Use pattern matching over type checks
if (shape is Circle { Radius: > 10 } c)
    Console.WriteLine($"Big circle: {c.Radius}");

// Use collection expressions (C# 12)
int[] primes = [2, 3, 5, 7, 11];
```

## Async Best Practices

```csharp
// ALWAYS await async calls (no fire-and-forget)
await SendEmailAsync(user);

// ALWAYS pass CancellationToken
async Task<User> GetUserAsync(int id, CancellationToken ct = default)
{
    return await repo.FindAsync(id, ct);
}

// NEVER use .Result or .Wait() (deadlock risk)
// NEVER return async void (except event handlers)
// ALWAYS use ConfigureAwait(false) in libraries
```

## Error Handling

```csharp
// Throw specific exceptions with context
throw new InvalidOperationException($"User {id} not found");

// Use exception filters
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
{
    return null;
}

// Prefer Result<T> pattern for expected failures
record Result<T>(T? Value, string? Error)
{
    public bool IsSuccess => Error is null;
}
```
