---
name: typescript-advanced
description: Advanced TypeScript type system, generics, utility types, declaration files, and enterprise patterns
---

# TypeScript Advanced

## Type System Deep Dive
- Literal types: "hello", 42, true as types
- Union types: string | number, discriminated unions with type guards
- Intersection types: A & B, combining types
- Type narrowing: typeof, instanceof, in, discriminant property, user-defined guards
- Type guards: function isString(x: unknown): x is string
- Assertion functions: function assert(x: unknown): asserts x is string
- Never type: exhaustive checks, unreachable code detection
- Unknown vs any: unknown is safe (requires narrowing), any disables checking

## Generics
- Generic functions: function identity<T>(arg: T): T
- Generic constraints: <T extends HasLength>, <T extends keyof U>
- Multiple type parameters: <T, U>, <Input, Output>
- Default type parameters: <T = string>
- Generic classes and interfaces
- Conditional types: T extends U ? X : Y
- Infer keyword: T extends Promise<infer U> ? U : never
- Recursive types: type DeepPartial<T> = { [K in keyof T]?: DeepPartial<T[K]> }

## Utility Types
- Partial<T>, Required<T>: optional/required all properties
- Pick<T, K>, Omit<T, K>: select/exclude properties
- Record<K, V>: construct type with set of properties
- Readonly<T>, ReadonlyArray<T>: immutable variants
- ReturnType<T>, Parameters<T>: extract from function types
- InstanceType<T>: extract instance type of constructor
- Exclude<T, U>, Extract<T, U>: union type filtering
- NonNullable<T>: remove null and undefined
- Awaited<T>: unwrap Promise type
- NoInfer<T>: prevent inference in specific positions (TS 5.4+)
- Satisfies operator: expression satisfies Type for validation without widening

## Mapped Types
- { [K in keyof T]: NewType }: transform all properties
- Key remapping: { [K in keyof T as NewKey]: T[K] }
- Template literal types: `${string}Changed`, `get${Capitalize<string>}`
- Filtering keys: [K in keyof T as T[K] extends Condition ? K : never]

## Declaration Files
- .d.ts files: type declarations without implementation
- declare module 'name' for third-party libraries
- Ambient declarations: declare const, declare function, declare namespace
- Triple-slash references: /// <reference types="..." />
- Module augmentation: extending existing module types

## Patterns
- Discriminated unions: { type: 'a', data: A } | { type: 'b', data: B }
- Builder pattern: method chaining with generic accumulation
- Type-safe event emitter: mapped types + generics
- Branded types: type UserId = string & { __brand: 'UserId' }
- Const assertions: as const for literal types
- Enum alternatives: const object + typeof (tree-shakeable)
- Zod: runtime validation + static type inference (z.infer<typeof schema>)

## Configuration
- tsconfig.json: strict mode, target, module, paths, baseUrl
- Strict flags: strictNullChecks, noImplicitAny, strictFunctionTypes
- Module resolution: node, bundler (TS 5+), paths for aliases
- Project references: composite, references for monorepos
- Declaration maps: declarationMap for go-to-definition in .d.ts

## Best Practices
- Enable strict mode — no exceptions
- Prefer unknown over any, narrow with type guards
- Use discriminated unions for state modeling
- Avoid type assertions (as) — narrow instead
- Export types alongside values
- Use satisfies for validation without type widening
- Template literal types for string patterns
- Keep types close to usage — colocate with code
