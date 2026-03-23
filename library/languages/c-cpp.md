# C / C++ Quick Reference

## Language: C17 / C++23
**Paradigm:** Procedural (C), Multi-paradigm (C++)  
**Typing:** Static, strong (with implicit conversions)  
**Compiled:** GCC, Clang, MSVC  

## C Essentials

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

// Fixed-width integers
int32_t x = 42;
uint8_t byte = 0xFF;
size_t len = strlen(str);

// Pointers
int val = 10;
int *ptr = &val;
int deref = *ptr;

// Dynamic memory
int *buf = malloc(n * sizeof(int));
if (!buf) { /* handle OOM */ }
free(buf);
buf = NULL;

// Structs
typedef struct {
    char name[64];
    int age;
} Person;

Person p = {.name = "Piddy", .age = 1};  // designated init (C99)

// Function pointers
typedef int (*Comparator)(const void*, const void*);
qsort(arr, n, sizeof(int), compare_ints);
```

## C++ Modern (C++17/20/23)

```cpp
#include <string>
#include <vector>
#include <memory>
#include <optional>
#include <variant>
#include <ranges>
#include <span>
#include <expected>   // C++23

// Auto & structured bindings
auto [key, value] = *map.begin();

// Smart pointers
auto ptr = std::make_unique<Widget>(args...);
auto shared = std::make_shared<Config>();

// std::optional
std::optional<int> find(const std::string& key) {
    if (auto it = map.find(key); it != map.end())
        return it->second;
    return std::nullopt;
}

// Ranges (C++20)
auto evens = numbers | std::views::filter([](int n){ return n%2==0; })
                     | std::views::transform([](int n){ return n*2; })
                     | std::views::take(10);

// Concepts (C++20)
template<typename T>
concept Hashable = requires(T a) {
    { std::hash<T>{}(a) } -> std::convertible_to<std::size_t>;
};

// Lambdas
auto add = [](int a, int b) { return a + b; };

// std::format (C++20)
auto msg = std::format("Hello {}, port={}", name, port);
```

## Containers

| Container | Access | Insert | Find | Notes |
|-----------|--------|--------|------|-------|
| `vector` | O(1) | O(1)* | O(n) | Default choice |
| `array` | O(1) | - | O(n) | Fixed size |
| `deque` | O(1) | O(1)* | O(n) | Front/back insert |
| `unordered_map` | O(1) | O(1) | O(1) | Hash map |
| `map` | O(log n) | O(log n) | O(log n) | Red-black tree |
| `unordered_set` | - | O(1) | O(1) | Hash set |
| `span` | O(1) | - | - | Non-owning view |

## Build Tools

```bash
# CMake (standard)
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)

# Compiler flags
g++ -std=c++23 -O2 -Wall -Wextra -Wpedantic main.cpp -o main

# Package managers
vcpkg install fmt spdlog
conan install . --build=missing
```

## Memory Safety Patterns

```cpp
// RAII — resources tied to scope
{
    std::lock_guard lock(mutex);
    // mutex released when lock goes out of scope
}

// Rule of 0: use smart pointers, no manual resource mgmt
class Widget {
    std::unique_ptr<Impl> pImpl;
public:
    Widget();
    ~Widget() = default;
};

// span for safe array views
void process(std::span<const int> data) {
    for (int x : data) { /* bounds-safe iteration */ }
}
```
