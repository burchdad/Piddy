# TypeScript Quick Reference

## Language: TypeScript 5.x
**Paradigm:** Multi-paradigm with static type system  
**Typing:** Static, structural  
**Compiled:** JavaScript (any target)  

## Type Basics

```typescript
// Primitives
let name: string = "Piddy";
let age: number = 1;
let active: boolean = true;

// Arrays & tuples
let nums: number[] = [1, 2, 3];
let pair: [string, number] = ["age", 25];
let readonly: readonly number[] = [1, 2, 3];

// Object types
type User = {
  id: number;
  name: string;
  email?: string;           // optional
  readonly createdAt: Date;  // immutable
};

// Union & intersection
type Result = Success | Failure;
type Admin = User & { permissions: string[] };

// Literal types
type Direction = "north" | "south" | "east" | "west";
```

## Generics

```typescript
function identity<T>(value: T): T { return value; }

// Constraints
function getLength<T extends { length: number }>(item: T): number {
  return item.length;
}

// Conditional types
type IsString<T> = T extends string ? true : false;

// Infer
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
```

## Utility Types

```typescript
Partial<T>          // all properties optional
Required<T>         // all properties required
Readonly<T>         // all properties readonly
Pick<T, K>          // select properties
Omit<T, K>          // exclude properties
Record<K, V>        // construct object type
Extract<T, U>       // extract union members
Exclude<T, U>       // remove union members
NonNullable<T>      // remove null/undefined
ReturnType<F>       // function return type
Parameters<F>       // function parameter types
Awaited<T>          // unwrap Promise
```

## Discriminated Unions

```typescript
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rect"; width: number; height: number }
  | { kind: "triangle"; base: number; height: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle":   return Math.PI * s.radius ** 2;
    case "rect":     return s.width * s.height;
    case "triangle": return 0.5 * s.base * s.height;
  }
}
```

## Mapped & Template Literal Types

```typescript
// Mapped type
type Optional<T> = { [K in keyof T]?: T[K] };

// Key remapping
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

// Template literal
type EventName = `on${Capitalize<string>}`;
```

## Key tsconfig Options

```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```
