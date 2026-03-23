# Java Quick Reference

## Language: Java 21+ (LTS)
**Paradigm:** OOP, functional elements  
**Typing:** Static, strong, nominal  
**Runtime:** JVM (HotSpot, GraalVM)  

## Modern Syntax (Java 17-21)

```java
// Records — immutable data classes
record Point(double x, double y) {
    Point {
        if (x < 0 || y < 0) throw new IllegalArgumentException();
    }
}

// Sealed classes — restricted hierarchy
sealed interface Shape permits Circle, Rectangle {}
record Circle(double radius) implements Shape {}
record Rectangle(double w, double h) implements Shape {}

// Pattern matching (switch)
String describe(Shape s) {
    return switch (s) {
        case Circle c when c.radius() > 10   -> "big circle";
        case Circle c                         -> "circle r=" + c.radius();
        case Rectangle r                      -> "rect " + r.w() + "x" + r.h();
    };
}

// Text blocks
String json = """
    {
        "name": "%s",
        "port": %d
    }
    """.formatted(name, port);

// Virtual threads (Project Loom)
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i ->
        executor.submit(() -> doWork(i))
    );
}
```

## Collections & Streams

```java
// Immutable collections
var list = List.of("a", "b", "c");
var set = Set.of(1, 2, 3);
var map = Map.of("k1", "v1", "k2", "v2");

// Streams
var names = users.stream()
    .filter(u -> u.isActive())
    .map(User::name)
    .sorted()
    .distinct()
    .toList();  // Java 16+

// Collectors
var grouped = items.stream()
    .collect(Collectors.groupingBy(Item::category));

// Optional
Optional<User> user = findById(id);
String name = user.map(User::name).orElse("anonymous");
user.ifPresent(u -> process(u));
```

## Concurrency

```java
// CompletableFuture
CompletableFuture.supplyAsync(() -> fetchData())
    .thenApply(data -> transform(data))
    .thenAccept(result -> save(result))
    .exceptionally(ex -> { log(ex); return null; });

// Structured concurrency (preview)
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    var user  = scope.fork(() -> findUser(id));
    var order = scope.fork(() -> findOrder(id));
    scope.join().throwIfFailed();
    return new Response(user.get(), order.get());
}
```

## Build Tools

```bash
# Maven
mvn clean package
mvn dependency:tree

# Gradle (Kotlin DSL)
./gradlew build
./gradlew test
```
