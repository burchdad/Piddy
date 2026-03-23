---
name: c-cpp
description: Systems programming with C and modern C++ (C++17/20/23), memory management, STL, and build systems
---

# C and C++ Development

## C Language
- Data types: int, char, float, double, size_t, stdint types (uint8_t, int32_t)
- Pointers: declaration, dereferencing, pointer arithmetic, void*, function pointers
- Arrays and strings: stack arrays, C-strings (null-terminated), string.h functions
- Dynamic memory: malloc, calloc, realloc, free — always check return values
- Structs, unions, enums, typedef
- Preprocessor: #define, #include guards, #ifdef, variadic macros
- File I/O: fopen, fread, fwrite, fclose, fprintf, fscanf
- Standard library: stdlib.h, string.h, stdio.h, math.h, assert.h
- Undefined behavior: buffer overflows, use-after-free, signed overflow, null dereference
- Bit manipulation: &, |, ^, ~, <<, >> for flags and masks

## Modern C++ (C++17/20/23)
- RAII: resource acquisition is initialization — constructors acquire, destructors release
- Smart pointers: unique_ptr (sole ownership), shared_ptr (shared), weak_ptr (observe)
- Move semantics: rvalue references (&&), std::move, move constructors/assignment
- Templates: function, class, variable templates, SFINAE, concepts (C++20)
- Concepts: requires clauses, named concepts for template constraints
- Ranges (C++20): views, adaptors, pipelines (views::filter, views::transform)
- Coroutines (C++20): co_await, co_yield, co_return
- Modules (C++20): import/export replacing headers
- std::optional, std::variant, std::any for type-safe unions
- Structured bindings: auto [x, y] = pair; auto& [key, value] : map
- constexpr and consteval for compile-time computation
- Lambda expressions: capture lists, generic lambdas, mutable
- std::string_view for non-owning string references
- std::span for non-owning contiguous views (C++20)
- std::format (C++20) and std::print (C++23) replacing printf/iostream formatting

## STL Containers and Algorithms
- Sequence: vector, deque, list, array, forward_list
- Associative: map, set, multimap, multiset (ordered, tree-based)
- Unordered: unordered_map, unordered_set (hash-based, O(1) average)
- Adaptors: stack, queue, priority_queue
- Algorithms: sort, find, transform, accumulate, partition, binary_search
- Iterators: input, output, forward, bidirectional, random access

## Memory Management
- Stack vs heap allocation — prefer stack when possible
- RAII over manual new/delete — use smart pointers
- Rule of 0/3/5: prefer Rule of 0 (no custom special members)
- Placement new for memory pools
- Custom allocators: std::pmr::polymorphic_allocator
- Memory debugging: Valgrind, AddressSanitizer (-fsanitize=address)
- Memory order for atomics: relaxed, acquire, release, seq_cst

## Build Systems
- CMake (standard): CMakeLists.txt, targets, find_package, FetchContent
- Modern CMake: target_link_libraries, target_include_directories (per-target, not global)
- Compiler flags: -Wall -Wextra -Werror -pedantic, /W4 (MSVC)
- Sanitizers: -fsanitize=address,undefined,thread
- Package managers: vcpkg, Conan

## Concurrency
- std::thread, std::jthread (C++20, auto-joining)
- std::mutex, std::lock_guard, std::unique_lock, std::scoped_lock
- std::condition_variable for signaling
- std::atomic for lock-free operations
- std::async, std::future, std::promise
- Thread pools (not in std, use BS::thread_pool or custom)

## Best Practices
- Const correctness: const references, const methods, constexpr
- Prefer references over pointers when null is not valid
- Never return references/pointers to local variables
- Initialize all variables at declaration
- Use override keyword on virtual function overrides
- Prefer std::array over C arrays, std::string over char*
- Check bounds: at() in debug, operator[] in release
- Compile with all warnings and sanitizers enabled
