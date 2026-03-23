---
name: javascript-typescript
description: Write modern JavaScript and TypeScript for Node.js, React, and browser environments
---

# JavaScript & TypeScript Development

## TypeScript Patterns
- Use strict mode (`"strict": true` in tsconfig)
- Prefer `interface` for object shapes, `type` for unions & intersections
- Use `const` assertions for literal types
- Avoid `any` — use `unknown` when the type is truly unknown
- Use discriminated unions for state machines

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'viewer';
}

type Result<T> = { ok: true; data: T } | { ok: false; error: string };

function handleResult<T>(result: Result<T>): T {
  if (!result.ok) throw new Error(result.error);
  return result.data;
}
```

## React Patterns
- Use functional components with hooks
- Keep components small and focused (< 150 lines)
- Lift state to the lowest common ancestor
- Use `useCallback` for functions passed to children
- Use `useMemo` for expensive computations only when needed
- Prefer controlled components for forms

```tsx
function SearchInput({ onSearch }: { onSearch: (q: string) => void }) {
  const [value, setValue] = useState('');
  const debouncedSearch = useMemo(
    () => debounce((q: string) => onSearch(q), 300),
    [onSearch]
  );
  return (
    <input value={value} onChange={e => {
      setValue(e.target.value);
      debouncedSearch(e.target.value);
    }} />
  );
}
```

## Node.js Best Practices
- Use ES modules (`import/export`) over CommonJS
- Handle async errors with try/catch (never unhandled promises)
- Use `AbortController` for cancellation
- Stream large data instead of buffering in memory
- Use environment variables for configuration (never hardcode)

## Package Management
- Pin exact versions in production (`--save-exact`)
- Use `npm audit` regularly
- Avoid unnecessary dependencies — prefer native APIs
- Use `package-lock.json` for reproducible builds

## Error Handling
```typescript
class AppError extends Error {
  constructor(
    message: string,
    public statusCode: number = 500,
    public code: string = 'INTERNAL_ERROR'
  ) {
    super(message);
    this.name = 'AppError';
  }
}
```
