# Kotlin Quick Reference

## Language: Kotlin 2.0+
**Paradigm:** OOP, functional, concurrent  
**Typing:** Static, strong, inferred, null-safe  
**Targets:** JVM, Android, Kotlin/Native, Kotlin/JS, Kotlin/Wasm  

## Syntax Essentials

```kotlin
val name = "Piddy"          // immutable
var count = 0                // mutable

// Null safety
var email: String? = null
val len = email?.length ?: 0

// When expression
val label = when (status) {
    200 -> "OK"
    in 400..499 -> "Client error"
    else -> "Unknown"
}

// Scope functions
user.let { println(it.name) }
user.apply { name = "New" }
```

## Data Classes & Sealed Types

```kotlin
data class User(val id: Int, val name: String, val email: String? = null)
val u2 = user.copy(name = "Updated")

sealed interface Result<out T> {
    data class Success<T>(val data: T) : Result<T>
    data class Error(val message: String) : Result<Nothing>
    data object Loading : Result<Nothing>
}

fun <T> handle(result: Result<T>) = when (result) {
    is Result.Success -> process(result.data)
    is Result.Error -> showError(result.message)
    Result.Loading -> showSpinner()
}
```

## Coroutines

```kotlin
import kotlinx.coroutines.*

suspend fun fetchUser(id: Int): User {
    return httpClient.get("/users/$id").body()
}

coroutineScope {
    val user = async { fetchUser(1) }
    val posts = async { fetchPosts(1) }
    Result(user.await(), posts.await())
}

// Flow
fun numbers(): Flow<Int> = flow {
    for (i in 1..10) { delay(100); emit(i) }
}

numbers().filter { it % 2 == 0 }.map { it * 2 }.collect { println(it) }
```

## Tooling

```bash
gradle build
gradle test
gradle run
kotlin script.main.kts
```
