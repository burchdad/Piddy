# C# Quick Reference

## Language: C# 12 / .NET 8+
**Paradigm:** OOP, functional elements, concurrent  
**Typing:** Static, strong, nominal  
**Runtime:** .NET CLR (cross-platform)  

## Modern Syntax

```csharp
// Top-level statements
Console.WriteLine("Hello Piddy");

// Records
record Person(string Name, int Age);
record struct Point(double X, double Y);

// Primary constructors (C# 12)
class UserService(IRepository repo, ILogger<UserService> logger)
{
    public User? Find(int id) => repo.GetById(id);
}

// Pattern matching
string Classify(object obj) => obj switch
{
    int n when n > 0   => "positive",
    int n when n < 0   => "negative",
    int                => "zero",
    string s           => $"string: {s}",
    null               => "null",
    _                  => "unknown"
};

// Collection expressions (C# 12)
int[] nums = [1, 2, 3, 4, 5];
List<string> names = ["Alice", "Bob"];

// Nullable reference types
string? nullable = null;
string nonNull = nullable ?? "default";
```

## LINQ

```csharp
var result = users
    .Where(u => u.IsActive)
    .OrderBy(u => u.Name)
    .Select(u => new { u.Name, u.Email })
    .ToList();

var grouped = orders.GroupBy(o => o.Category)
    .Select(g => new { Category = g.Key, Total = g.Sum(o => o.Amount) });
```

## Async/Await

```csharp
async Task<User> GetUserAsync(int id, CancellationToken ct = default)
{
    var response = await httpClient.GetAsync($"/api/users/{id}", ct);
    response.EnsureSuccessStatusCode();
    return await response.Content.ReadFromJsonAsync<User>(ct)
        ?? throw new InvalidOperationException("User not found");
}

// Parallel async
var tasks = ids.Select(id => GetUserAsync(id));
var users = await Task.WhenAll(tasks);
```

## Dependency Injection

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddSingleton<ICacheService, RedisCacheService>();

var app = builder.Build();
app.MapGet("/users/{id}", async (int id, IUserService svc) =>
    await svc.GetAsync(id) is { } user ? Results.Ok(user) : Results.NotFound());
app.Run();
```

## CLI

```bash
dotnet new webapi -n MyApi
dotnet build
dotnet run
dotnet test
dotnet publish -c Release
```
