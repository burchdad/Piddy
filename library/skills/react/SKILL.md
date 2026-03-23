---
name: react
description: Complete React with hooks, state management, performance, testing, and Next.js for production applications
---

# React Development

## Core Concepts
- Components: function components (standard), props, children
- JSX: expressions {}, conditional rendering, lists with key prop
- Hooks: useState, useEffect, useRef, useMemo, useCallback, useContext
- useState: [state, setState], functional updates, lazy initialization
- useEffect: dependencies array, cleanup function, empty deps = mount only
- useRef: mutable reference, DOM access, stable across renders
- useMemo: expensive computation caching, referential equality
- useCallback: stable function references for child optimization
- useContext: avoid prop drilling, Provider/Consumer pattern
- Custom hooks: extract reusable logic, use* naming convention
- Event handling: synthetic events, onChange, onSubmit, event.preventDefault()

## State Management
- Local state: useState for component-scoped state
- Context API: createContext, Provider, useContext — for low-frequency updates
- useReducer: complex state logic, dispatch actions
- Zustand: lightweight global state, no providers needed
- Redux Toolkit: createSlice, configureStore, RTK Query for API caching
- Jotai: atomic state model, derived atoms
- TanStack Query (React Query): server state, caching, mutations, invalidation

## Performance
- React.memo: skip re-renders when props unchanged
- useMemo/useCallback: prevent expensive recalculations
- Virtualization: react-window/react-virtuoso for large lists
- Code splitting: React.lazy, Suspense, dynamic imports
- Profiler: React DevTools profiler, identify re-render causes
- Avoid: inline object/array creation in JSX, anonymous functions in render

## Patterns
- Composition over inheritance: children, render props, compound components
- Custom hooks for logic reuse
- Controlled vs uncontrolled components (forms)
- Error boundaries: class component with getDerivedStateFromError
- Portal: createPortal for modals, tooltips, dropdowns
- Suspense: data fetching boundaries, fallback UI
- Optimistic updates: update UI before server confirms

## Forms
- Controlled inputs: value + onChange
- React Hook Form: register, handleSubmit, errors, watch
- Zod + React Hook Form: schema validation with zodResolver
- Formik: alternative form library
- File uploads: input type="file", FormData, preview with URL.createObjectURL

## Routing
- React Router v6: BrowserRouter, Routes, Route, useNavigate, useParams
- Nested routes: Outlet, relative paths
- Protected routes: wrapper component that checks auth
- Loaders and actions (data router pattern)

## Next.js
- App Router (Next.js 13+): app/ directory, layouts, loading, error boundaries
- Server Components: default in app/, data fetching at component level
- Client Components: 'use client' directive for interactivity
- Server Actions: 'use server' for form handling and mutations
- Routing: file-system based, dynamic routes [slug], catch-all [...slug]
- Data fetching: fetch with caching, revalidation strategies
- Middleware: conditional redirects, auth checks, geolocation
- Image optimization: next/image component
- SSR, SSG, ISR: rendering strategies per-route

## Testing
- React Testing Library: render, screen, fireEvent, userEvent, waitFor
- Testing philosophy: test behavior, not implementation
- Mock API: MSW (Mock Service Worker) for intercepting network requests
- Jest: assertions, mocking modules, snapshots (use sparingly)
- Component testing: render → interact → assert on DOM
- Async testing: findBy queries, waitFor, act()

## Best Practices
- One component per file, named exports
- Prefer composition over complex prop drilling
- Lift state up only as far as needed
- Colocate state with the component that uses it
- Use TypeScript with React for prop safety
- Avoid useEffect for derived state — use useMemo or compute during render
- Keys must be stable, unique IDs — never array index for dynamic lists
