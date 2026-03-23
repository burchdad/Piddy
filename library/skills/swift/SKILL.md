---
name: swift
description: Swift programming for iOS, macOS, and server-side with SwiftUI, UIKit, Combine, and Swift concurrency
---

# Swift Development

## Core Language
- Strong static typing with type inference
- Optionals: String?, unwrapping (if let, guard let, ??), optional chaining
- Value types (struct, enum, tuple) vs reference types (class)
- Struct: value semantics, copy-on-write for collections
- Enums: associated values, raw values, CaseIterable, recursive (indirect)
- Protocols: like interfaces, protocol extensions, protocol-oriented programming
- Generics: type parameters, associated types, where clauses, opaque types (some Protocol)
- Closures: { (params) -> Return in body }, trailing closure syntax, @escaping
- Error handling: throws/try/catch, Result<T, Error>, typed throws (Swift 6)
- Property wrappers: @State, @Published, @AppStorage, custom wrappers
- Extensions: add methods/computed properties/protocol conformance to existing types
- Access control: open, public, internal, fileprivate, private
- Actors: reference types with built-in data isolation
- Sendable protocol: thread-safety marker

## Swift Concurrency (async/await)
- async/await: structured concurrency model
- Task: Task { }, Task.detached, cancellation
- TaskGroup: withTaskGroup for parallel work
- AsyncSequence: for await in
- Actors: actor keyword, isolated state, nonisolated
- @MainActor: main thread isolation for UI code
- Continuations: withCheckedContinuation/withCheckedThrowingContinuation for bridging callback APIs
- Strict concurrency checking (Swift 6)

## SwiftUI
- Declarative UI: View protocol, body computed property
- Layout: VStack, HStack, ZStack, Grid, LazyVGrid
- State management: @State, @Binding, @StateObject, @ObservedObject, @EnvironmentObject
- Observable macro (iOS 17+): @Observable class, not ObservableObject
- Navigation: NavigationStack, NavigationLink, navigationDestination
- Lists: List, ForEach, onDelete, onMove
- Modifiers: .padding(), .font(), .foregroundStyle(), .frame()
- Animations: withAnimation, .animation, .transition, matched geometry
- Data flow: @Environment, custom EnvironmentKey
- SwiftData (iOS 17+): @Model, @Query, ModelContext

## UIKit (still relevant)
- UIViewController lifecycle: viewDidLoad, viewWillAppear, viewDidAppear
- Auto Layout: NSLayoutConstraint, anchors (translatesAutoresizingMaskIntoConstraints = false)
- UITableView/UICollectionView: diffable data sources, compositional layout
- Storyboards vs programmatic UI
- Delegation pattern, target-action pattern
- Combine with UIKit: assign(to:), sink

## Combine Framework
- Publishers, Subscribers, Operators
- map, filter, flatMap, combineLatest, merge, zip
- Just, Future, PassthroughSubject, CurrentValueSubject
- sink, assign for subscription
- AnyCancellable, store(in: &cancellables)

## Networking
- URLSession: async data(for:), download(for:)
- Codable: Encodable + Decodable, CodingKeys, custom coding
- JSONDecoder/JSONEncoder: keyDecodingStrategy, dateDecodingStrategy

## Testing
- XCTest: XCTestCase, setUp/tearDown, test methods
- Assertions: XCTAssertEqual, XCTAssertTrue, XCTAssertThrowsError
- Async testing: async test methods, XCTestExpectation
- UI testing: XCUIApplication, XCUIElement, queries

## Best Practices
- Prefer structs over classes (value semantics by default)
- Protocol-oriented programming: compose behavior via protocols
- Use guard for early returns
- Never force-unwrap (!) in production code — use if let/guard let
- Mark @MainActor for all UI-related code
- Use Swift concurrency over GCD/completion handlers in new code
