---
name: scala
description: Scala programming with functional and OOP paradigms, Akka, Play Framework, and the JVM ecosystem
---

# Scala Development

## Core Language
- Type inference: val (immutable), var (mutable), def for methods
- Unified types: Any > AnyVal (Int, Double) + AnyRef (classes), Nothing, Null
- Classes: primary constructor in class header, case classes for data
- Case classes: immutable, auto equals/hashCode/toString/copy, pattern matching
- Traits: multiple inheritance of behavior, abstract and concrete members, linearization
- Objects: singleton, companion object (like static in Java)
- Pattern matching: match/case, guards, sealed hierarchies, extractors
- Enums (Scala 3): enum Color { case Red, Green, Blue }, parameterized
- Generics: [T], variance (+T covariant, -T contravariant), bounds (<:, >:)
- Implicits (Scala 2) / Given/Using (Scala 3): type class pattern, context parameters
- Extension methods (Scala 3): extension (s: String) def ...
- Union types (Scala 3): String | Int
- Intersection types (Scala 3): A & B
- Opaque types: type-safe wrappers without runtime overhead

## Functional Programming
- Functions as first-class values: val f = (x: Int) => x + 1
- Higher-order functions: map, filter, flatMap, fold, reduce, collect
- Option[T]: Some/None, map, flatMap, getOrElse, for-comprehensions
- Either[L, R]: Left/Right, error handling without exceptions
- Try[T]: Success/Failure, wrapping exception-throwing code
- Future[T]: async computation, map, flatMap, recover, for-comprehensions
- For-comprehensions: syntactic sugar for flatMap chains
- Immutable collections by default: List, Vector, Map, Set
- Lazy evaluation: lazy val, LazyList (formerly Stream)
- Tail recursion: @tailrec annotation for stack-safe recursion
- Type classes: trait + given instances + extension methods

## Collections
- Immutable: List, Vector (default), Map, Set, LazyList
- Mutable: ArrayBuffer, HashMap, HashSet (import scala.collection.mutable)
- Operations: map, flatMap, filter, fold, groupBy, partition, zip, collect
- Parallel collections: .par for parallel processing
- Views: lazy transformations for efficiency

## Akka
- Actor model: ActorRef, Behavior, message passing
- Akka Typed: typed actors with Behavior[Message]
- Supervision: restart, stop, resume strategies
- Akka Streams: Source, Flow, Sink, backpressure
- Akka HTTP: routes, directives, marshalling/unmarshalling
- Akka Cluster: distributed computing, sharding

## Build Tools
- sbt: build.sbt, libraryDependencies, plugins, multi-project builds
- sbt commands: compile, run, test, console, reload
- Mill: alternative build tool, simpler configuration
- Scala CLI: for scripts and small projects

## Testing
- ScalaTest: FunSuite, FlatSpec, WordSpec, matchers (should/shouldBe)
- MUnit: lightweight testing framework
- ScalaCheck: property-based testing
- Mockito-Scala: mocking in Scala-idiomatic way

## Best Practices
- Prefer immutable data and pure functions
- Use case classes for data, regular classes for services
- Pattern matching over instanceof/isInstanceOf
- For-comprehensions for monadic composition
- Avoid null — use Option, Either, Try
- Use Scala 3 syntax (given/using) over Scala 2 implicits in new code
- Leverage the type system: sealed traits for exhaustive matching
