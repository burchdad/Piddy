# C / C++ Coding Standards

## Scope: Modern C++ (17/20/23), memory safety, RAII
**Authority:** C++ Core Guidelines (Stroustrup/Sutter), Google C++ Style, MISRA C  
**Tools:** clang-tidy, cppcheck, AddressSanitizer, Valgrind  

## Naming Conventions

**Google C++ Style (most common):**

| Element | Convention | Example |
|---------|-----------|---------|
| Type / Class / Struct | `PascalCase` | `UserManager` |
| Function / Method | `PascalCase` or `camelCase` | `GetUser()` |
| Variable | `snake_case` | `user_count` |
| Member variable | `snake_case_` (trailing) | `cache_size_` |
| Constant | `kPascalCase` | `kMaxRetries` |
| Enum member | `kPascalCase` | `Color::kRed` |
| Macro | `UPPER_SNAKE` | `MY_MACRO` |
| Namespace | `snake_case` | `my_project` |
| File | `snake_case` | `user_service.cpp` |

## Memory Safety Rules

```cpp
// 1. RAII: every resource is owned by an object
auto ptr = std::make_unique<Widget>();        // unique ownership
auto shared = std::make_shared<Config>();     // shared ownership

// 2. NEVER use raw new/delete
// Bad:  Widget* w = new Widget();
// Good: auto w = std::make_unique<Widget>();

// 3. Use span/string_view for non-owning references
void process(std::span<const int> data);
void log(std::string_view message);

// 4. Prefer stack allocation
std::array<int, 100> buffer;     // not: int* buf = new int[100];

// 5. Use AddressSanitizer in CI
// g++ -fsanitize=address -fno-omit-frame-pointer
```

## Modern C++ Idioms

```cpp
// Prefer auto for complex types (readability)
auto result = computeMatrix();
auto it = container.find(key);

// Structured bindings
auto [key, value] = *map.begin();

// constexpr for compile-time computation
constexpr auto factorial(int n) -> int {
    return n <= 1 ? 1 : n * factorial(n - 1);
}

// Concepts for constrained templates
template<typename T>
concept Sortable = std::totally_ordered<T> && std::movable<T>;

template<Sortable T>
void sort(std::vector<T>& v);
```

## Header Hygiene

```cpp
// Use #pragma once (or include guards)
#pragma once

// Forward declare instead of including when possible
class UserService;   // in header
#include "user_service.h"  // in .cpp

// Include order (Google style):
// 1. Related header (foo.h for foo.cpp)
// 2. C system headers
// 3. C++ standard headers
// 4. Third-party library headers
// 5. Project headers
```
