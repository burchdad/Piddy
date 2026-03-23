# TypeScript Coding Standards

## Scope: Type safety, strict config, interface patterns
**Authority:** TypeScript Handbook, Google TS Style, ts-reset  
**Tools:** tsc --strict, ESLint + typescript-eslint, Biome  

## Strict Configuration

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,
    "verbatimModuleSyntax": true
  }
}
```

**Never disable strict checks** — they catch real bugs.

## Types vs Interfaces

```typescript
// Use `type` for unions, intersections, mapped types, primitives
type Status = 'active' | 'inactive' | 'pending';
type Result<T> = { ok: true; data: T } | { ok: false; error: string };
type UserMap = Map<string, User>;

// Use `interface` for object shapes (especially public APIs)
interface UserService {
  getUser(id: number): Promise<User>;
  createUser(data: CreateUserInput): Promise<User>;
}

// interfaces are extendable / mergeable:
interface Config { host: string; }
interface Config { port: number; }  // declaration merging
```

## Avoid Type Escape Hatches

```typescript
// NEVER use `any` — use `unknown` and narrow
function parse(input: unknown): Config {
  if (typeof input !== 'object' || input === null) {
    throw new Error('Expected object');
  }
  // ... validate and narrow
}

// AVOID non-null assertions (!) — guard instead
// Bad:  const name = user!.name;
// Good: if (!user) throw new Error('No user');
//       const name = user.name;

// AVOID type assertions unless truly necessary
// Bad:  const data = response as UserData;
// Good: const data = schema.parse(response);  // runtime validation
```

## Function Signatures

```typescript
// Return types on public functions (inference for private/internal)
export function calculateTotal(items: LineItem[]): number { }

// Use discriminated unions over optional fields
// Bad:
type Response = { data?: User; error?: string; };
// Good:
type Response = { ok: true; data: User } | { ok: false; error: string };

// Generics: name descriptively when >1
function merge<TBase, TOverride>(base: TBase, over: TOverride): TBase & TOverride { }
```

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Type / Interface | `PascalCase` | `UserProfile`, `ApiResponse` |
| Type parameter | `T` prefix or descriptive | `T`, `TKey`, `TValue` |
| Enum | `PascalCase` (members too) | `Direction.North` |
| File | `camelCase` or `kebab-case` | `userService.ts` |
| No `I` prefix | ~~`IUserService`~~ | `UserService` |
| No `Enum` suffix | ~~`StatusEnum`~~ | `Status` |
