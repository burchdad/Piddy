# React Quick Reference

## Language: React 18.2+ (with Hooks)
**Paradigm:** UI component library  
**Typing:** JavaScript/TypeScript + JSX  
**Rendering:** Virtual DOM, concurrent features  

## Components

```jsx
function Greeting({ name, excited = false }) {
  return <h1>Hello {name}{excited ? "!" : "."}</h1>;
}

function Layout({ children }) {
  return <div className="layout"><main>{children}</main></div>;
}

function UserList({ users }) {
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

## Hooks

```jsx
const [count, setCount] = useState(0);
setCount(prev => prev + 1);

useEffect(() => {
  const ctrl = new AbortController();
  fetch(url, { signal: ctrl.signal }).then(r => r.json()).then(setData);
  return () => ctrl.abort();
}, [url]);

const sorted = useMemo(() => items.sort(compare), [items]);
const handler = useCallback((id) => setSelected(id), []);
const inputRef = useRef(null);

// Custom hook
function useLocalStorage(key, initial) {
  const [val, setVal] = useState(() => {
    const s = localStorage.getItem(key);
    return s ? JSON.parse(s) : initial;
  });
  useEffect(() => localStorage.setItem(key, JSON.stringify(val)), [key, val]);
  return [val, setVal];
}
```

## Patterns

```jsx
// Lazy loading
const Dashboard = React.lazy(() => import('./Dashboard'));
<Suspense fallback={<Spinner />}><Dashboard /></Suspense>

// Context
const ThemeCtx = createContext('light');
const theme = useContext(ThemeCtx);

// useTransition (non-urgent updates)
const [isPending, startTransition] = useTransition();
startTransition(() => setItems(filter(items, query)));
```

## Tooling

```bash
npm create vite@latest app -- --template react-ts
npm run dev
npm run build
```
