---
name: dart-flutter
description: Dart language and Flutter framework for cross-platform mobile, web, and desktop applications
---

# Dart and Flutter Development

## Dart Language
- Sound null safety: String vs String?, late, required keyword
- Type system: strong static typing, var, final, const, dynamic
- Classes: constructors (named, factory, const), mixins, abstract, sealed
- Extensions: add methods to existing types
- Enums: enhanced enums with fields, methods, interfaces
- Patterns (Dart 3): switch expressions, if-case, destructuring, guards
- Records: (int, String) for lightweight data tuples
- Futures: Future<T>, async/await, Future.wait, Future.delayed
- Streams: Stream<T>, async*, yield, StreamController, StreamBuilder
- Isolates: true parallelism, Isolate.run for heavy computation
- Collections: List, Map, Set, spread operator (...), collection if/for
- Generics, typedefs, extension types

## Flutter Core
- Widget tree: StatelessWidget, StatefulWidget, build() method
- Layout: Column, Row, Stack, Center, Padding, SizedBox, Expanded, Flexible
- Container: decoration, padding, margin, constraints
- Scrolling: ListView, GridView, CustomScrollView, Slivers
- Navigation: Navigator 2.0, GoRouter, named routes
- Material 3: MaterialApp, Scaffold, AppBar, BottomNavigationBar, FloatingActionButton
- Cupertino: iOS-style widgets, CupertinoApp, CupertinoNavigationBar
- Theming: ThemeData, ColorScheme, TextTheme, dark/light mode

## State Management
- setState: simple local state for StatefulWidget
- Provider: ChangeNotifierProvider, Consumer, context.watch/read
- Riverpod: Provider, StateNotifier, FutureProvider, auto-dispose
- Bloc/Cubit: BlocProvider, BlocBuilder, BlocListener, event-driven
- GetX: reactive state, dependency injection, route management

## Common Patterns
- Key: ValueKey, GlobalKey for widget identity
- InheritedWidget: data down the tree (underlying Provider)
- Builder pattern: LayoutBuilder, MediaQuery, FutureBuilder, StreamBuilder
- Platform-specific code: Platform.isIOS, kIsWeb
- Responsive design: MediaQuery, LayoutBuilder, breakpoints
- Animations: AnimationController, Tween, AnimatedBuilder, Hero, implicit animations

## Networking and Data
- http/dio packages for REST APIs
- JSON serialization: json_serializable, freezed, manual fromJson/toJson
- SQLite: sqflite, drift (formerly moor) for local database
- SharedPreferences: simple key-value storage
- Firebase: Authentication, Firestore, Cloud Functions, FCM

## Testing
- Unit tests: test package, expect, group, setUp/tearDown
- Widget tests: testWidgets, WidgetTester, find, pumpWidget
- Integration tests: integration_test package, patrol
- Mocking: mockito, mocktail
- Golden tests: visual regression with matchesGoldenFile

## Best Practices
- const constructors everywhere possible (performance)
- Prefer StatelessWidget, extract state to providers/blocs
- Use const widgets to prevent unnecessary rebuilds
- Key everything in lists with unique data-based keys
- Avoid deep nesting: extract widgets into methods or sub-widgets
- Use build_runner for code generation (freezed, json_serializable)
- Flutter analyze and dart fix for code quality
