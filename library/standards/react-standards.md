# React Coding Standards

## Scope: Component patterns, hooks rules, state management, performance
**Authority:** React docs, React Compiler requirements, Airbnb React guide  
**Tools:** eslint-plugin-react, eslint-plugin-react-hooks, React DevTools  

## Component Rules

```jsx
// One component per file (name matches filename)
// UserProfile.tsx → export default function UserProfile()

// Props: destructure with defaults
function Button({ label, variant = 'primary', onClick }) {
  return <button className={variant} onClick={onClick}>{label}</button>;
}

// NEVER mutate props or state directly
// Bad:  props.items.push(newItem);
// Good: setItems(prev => [...prev, newItem]);

// Prefer composition over prop drilling
<Layout>
  <Sidebar />
  <Main>{children}</Main>
</Layout>
```

## Hooks Rules

```jsx
// 1. ONLY call hooks at the top level (never inside conditions/loops)
// 2. ONLY call hooks from React components or custom hooks
// 3. Custom hooks MUST start with "use"

// useEffect: always clean up side effects
useEffect(() => {
  const controller = new AbortController();
  fetchData(url, { signal: controller.signal }).then(setData);
  return () => controller.abort();
}, [url]);

// Correct dependencies — never lie about deps
// If a function is a dependency, memoize it:
const handleUpdate = useCallback((id) => {
  setItems(prev => prev.filter(i => i.id !== id));
}, []);  // stable reference
```

## Performance Patterns

```jsx
// Memoize expensive computations
const sorted = useMemo(() => items.sort(compare), [items]);

// Lazy load heavy components
const Dashboard = React.lazy(() => import('./Dashboard'));

// Use key prop correctly (NEVER use array index for dynamic lists)
{items.map(item => <Card key={item.id} {...item} />)}

// Avoid creating objects/functions in render
// Bad:  <Comp style={{color: 'red'}} />  (new object every render)
// Good: const style = useMemo(() => ({color: 'red'}), []);
```

## File Structure

```
src/
├── components/
│   ├── ui/              # Reusable primitives (Button, Input, Modal)
│   └── features/        # Feature-specific (UserCard, OrderTable)
├── hooks/               # Custom hooks
├── pages/               # Route-level components
├── services/            # API calls
├── utils/               # Pure helper functions
└── types/               # Shared TypeScript types
```
