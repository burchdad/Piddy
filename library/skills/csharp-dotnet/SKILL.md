---
name: csharp-dotnet
description: Complete C# programming with .NET platform, ASP.NET Core, Entity Framework, and modern patterns
---

# C# and .NET Development

## Core Language (C# 12+)
- Strong static typing with type inference (var, target-typed new)
- Value types vs reference types, structs vs classes
- Nullable reference types (NRT): enable in project, use ?, null-forgiving !
- Pattern matching: is, switch expressions, relational/logical patterns, list patterns
- Records: record class (reference), record struct (value) for immutable data
- Primary constructors (C# 12)
- Collection expressions: [1, 2, 3] syntax (C# 12)
- LINQ: query syntax and method syntax, deferred execution
- Async/await: Task, ValueTask, ConfigureAwait, IAsyncEnumerable
- Span<T>, Memory<T> for high-performance slicing
- Generics with constraints (where T : class, new(), IComparable<T>)
- Delegates, events, Func<>, Action<>, lambdas
- Extension methods, implicit/explicit operators
- Disposable pattern: IDisposable, IAsyncDisposable, using declarations

## .NET Platform
- .NET 8+ (LTS): cross-platform runtime
- SDK: dotnet new, dotnet build, dotnet run, dotnet publish
- Project files: .csproj with SDK-style format
- NuGet package management
- Configuration: appsettings.json, environment variables, user secrets
- Dependency injection: built-in DI container, service lifetimes (Singleton, Scoped, Transient)
- Logging: ILogger<T>, structured logging with Serilog
- Host builder: WebApplication.CreateBuilder pattern

## ASP.NET Core
- Minimal APIs: app.MapGet/Post/Put/Delete with route handlers
- Controllers: [ApiController], [Route], model binding, validation
- Middleware pipeline: Use, Map, Run ordering
- Authentication: JWT Bearer, Cookie, Identity, OAuth2/OIDC
- Authorization: policies, roles, claims, resource-based
- Filters: action, exception, result, authorization filters
- SignalR for real-time WebSocket communication
- Rate limiting, output caching (built-in .NET 7+)
- Health checks: AddHealthChecks, custom health check implementations
- Blazor: Server-side, WebAssembly, Auto render modes (.NET 8)

## Entity Framework Core
- DbContext: OnModelCreating, connection strings
- Code-first migrations: Add-Migration, Update-Database
- Fluent API configuration vs data annotations
- Relationships: one-to-one, one-to-many, many-to-many
- Query: LINQ to Entities, eager/explicit/lazy loading, AsNoTracking
- Raw SQL: FromSqlRaw, ExecuteSqlRaw (parameterized only)
- Change tracker, SaveChanges, concurrency tokens
- Global query filters (soft delete, multi-tenancy)

## Testing
- xUnit: [Fact], [Theory], [InlineData], IClassFixture
- NUnit: [Test], [TestCase], [SetUp], [TearDown]
- Moq: Mock<T>, Setup, Verify, It.IsAny
- FluentAssertions for readable assertions
- WebApplicationFactory for integration testing
- Testcontainers for database integration tests
- BenchmarkDotNet for performance benchmarks

## Patterns
- Repository + Unit of Work
- CQRS with MediatR: IRequest, IRequestHandler, INotification
- Clean Architecture: Domain, Application, Infrastructure, Presentation layers
- Options pattern: IOptions<T>, IOptionsSnapshot<T>
- Result pattern for error handling (no exceptions for control flow)
- Decorator pattern via DI registration

## Best Practices
- Enable nullable reference types project-wide
- Use records for DTOs, classes for entities with behavior
- Async all the way — never .Result or .Wait() (deadlock risk)
- Validate at API boundaries with FluentValidation or DataAnnotations
- Use cancellation tokens in async methods
- Prefer IReadOnlyList/IReadOnlyCollection in return types
- Seal classes not designed for inheritance
