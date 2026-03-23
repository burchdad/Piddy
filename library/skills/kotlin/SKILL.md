---
name: kotlin
description: Kotlin programming for Android, backend (Ktor, Spring), multiplatform, and coroutines
---

# Kotlin Development

## Core Language
- Null safety: String vs String?, safe call ?., elvis ?:, non-null assertion !!
- Type inference, val (immutable) vs var (mutable)
- Data classes: auto-generated equals, hashCode, toString, copy, componentN
- Sealed classes/interfaces: restricted hierarchies, exhaustive when
- Object declarations: singleton, companion object, object expressions
- Extension functions and properties
- Scope functions: let, run, with, apply, also
- Lambdas: { params -> body }, trailing lambda, it parameter
- Collections: listOf, mutableListOf, map, filter, flatMap, groupBy, associate
- Sequences: lazy evaluation, asSequence() for large collections
- Destructuring: val (name, age) = person
- Inline functions, reified type parameters
- Delegation: by keyword, property delegates (lazy, observable, vetoable)
- Operator overloading, infix functions
- Type aliases: typealias StringMap = Map<String, String>
- Value classes: @JvmInline value class for type-safe wrappers
- Context receivers (experimental)

## Coroutines
- suspend functions: suspending without blocking threads
- CoroutineScope, launch, async/await
- Dispatchers: Main, IO, Default, Unconfined
- Structured concurrency: parent-child relationships, cancellation propagation
- Flow: cold asynchronous streams, collect, map, filter, combine
- StateFlow: hot state holder, MutableStateFlow
- SharedFlow: hot event stream, replay
- Channel: for communication between coroutines
- Exception handling: CoroutineExceptionHandler, SupervisorJob
- withContext for dispatcher switching
- coroutineScope, supervisorScope builders

## Android (Jetpack Compose)
- @Composable functions: UI as functions of state
- State: remember, mutableStateOf, derivedStateOf
- State hoisting: stateless composables receive state as params
- Layout: Column, Row, Box, LazyColumn, LazyRow
- Material 3: MaterialTheme, Surface, Card, TopAppBar, NavigationBar
- Navigation: NavHost, NavController, composable routes, type-safe nav (2.8+)
- ViewModel: viewModel(), SavedStateHandle, ViewModelScope
- Room database: @Entity, @Dao, @Database, Flow queries
- Hilt: @HiltViewModel, @Inject, @Module, @Provides
- Retrofit: interface with suspend functions, converter factories
- Coil for image loading: AsyncImage composable
- Lifecycle: LaunchedEffect, DisposableEffect, SideEffect

## Backend (Ktor / Spring Boot)
- Ktor: routing, plugins (ContentNegotiation, Authentication, CORS), client
- Spring Boot with Kotlin: data classes for DTOs, null-safety integration
- Exposed: Kotlin SQL framework, DSL and DAO approaches
- kotlinx.serialization: @Serializable, Json.encodeToString/decodeFromString

## Kotlin Multiplatform (KMP)
- Shared code: commonMain, androidMain, iosMain, jvmMain
- expect/actual declarations
- Compose Multiplatform for shared UI

## Testing
- JUnit 5 with Kotlin
- MockK: every, verify, coEvery/coVerify for coroutines, mockk/spyk/relaxed
- Turbine: testing Flows
- Kotest: property-based testing, matchers, spec styles
- Compose testing: ComposeTestRule, onNodeWithText, performClick

## Best Practices
- Use val over var, immutable collections by default
- Use sealed classes for state modeling
- Never use !! in production — handle nullability properly
- Use data class for DTOs, regular class for domain entities with behavior
- Collect Flows in lifecycle-aware scope (repeatOnLifecycle)
- Use Kotlin idioms: scope functions, destructuring, when expressions
- Follow Kotlin coding conventions (ktlint)
