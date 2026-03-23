---
name: java
description: Complete Java programming from core language to enterprise frameworks (Spring Boot, Jakarta EE), build tools, and JVM internals
---

# Java Development

## Core Language
- Strong static typing, primitives vs wrapper types (int vs Integer)
- OOP: classes, interfaces, abstract classes, enums, records (Java 16+)
- Generics with type erasure, bounded wildcards (<? extends T>, <? super T>)
- Exception handling: checked vs unchecked, try-with-resources
- Collections Framework: List, Set, Map, Queue, Deque implementations
- Streams API: map, filter, reduce, collect, parallel streams
- Optional for null safety
- Lambda expressions and functional interfaces (Predicate, Function, Consumer, Supplier)
- Pattern matching (instanceof, switch expressions Java 17+)
- Sealed classes and interfaces (Java 17+)
- Virtual threads (Java 21+ Project Loom)
- String templates (Java 21+)

## JVM Internals
- Memory model: heap, stack, metaspace, string pool
- Garbage collectors: G1, ZGC, Shenandoah — tuning flags
- ClassLoader hierarchy: bootstrap, platform, application
- JIT compilation: C1, C2, Graal compiler
- Profiling: JFR (Java Flight Recorder), async-profiler
- Bytecode basics: javap disassembly for debugging

## Build Tools
- Maven: pom.xml, dependency management, lifecycle phases, multi-module projects, BOM imports
- Gradle: build.gradle.kts (Kotlin DSL preferred), task configuration avoidance, dependency configurations (api vs implementation)
- Dependency management: version catalogs, exclusions, conflict resolution

## Spring Boot
- Auto-configuration, starters, application.yml/properties
- Dependency injection: @Component, @Service, @Repository, @Configuration, @Bean
- Web: @RestController, @RequestMapping, @PathVariable, @RequestBody
- Data: Spring Data JPA, repositories, query methods, @Query, Specifications
- Security: Spring Security 6, SecurityFilterChain, JWT, OAuth2
- Testing: @SpringBootTest, @WebMvcTest, @DataJpaTest, MockMvc, @MockBean
- Actuator: health checks, metrics, custom endpoints
- Profiles: @Profile, environment-specific configuration
- Reactive: WebFlux, Mono, Flux for non-blocking IO

## Jakarta EE (formerly Java EE)
- CDI (Contexts & Dependency Injection)
- JPA (Java Persistence API): entities, relationships, JPQL, criteria queries
- JAX-RS for RESTful services
- Bean Validation: @NotNull, @Size, custom validators
- JMS for messaging

## Testing
- JUnit 5: @Test, @ParameterizedTest, @Nested, lifecycle callbacks
- Mockito: mock, when/thenReturn, verify, argument captors
- AssertJ for fluent assertions
- Testcontainers for integration tests with real databases
- ArchUnit for architecture testing
- JMH for microbenchmarks

## Design Patterns in Java
- Singleton (enum-based), Factory, Builder, Strategy, Observer
- Repository pattern, Service layer pattern
- DTO/Entity separation with MapStruct
- Event-driven with ApplicationEventPublisher

## Best Practices
- Prefer composition over inheritance
- Program to interfaces, not implementations
- Immutable objects where possible (records, unmodifiable collections)
- Avoid raw types — always parameterize generics
- Use try-with-resources for all AutoCloseable resources
- Validate at boundaries, trust internal code
- Use SLF4J + Logback for logging, never System.out.println in production
