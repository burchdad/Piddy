---
name: html-css
description: Build responsive, accessible UIs with modern HTML and CSS
---

# HTML & CSS

## Semantic HTML
- Use `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`
- Use `<button>` for actions, `<a>` for navigation
- Use `<label>` with `for` attribute for form inputs
- Use heading hierarchy (`h1` > `h2` > `h3`) — never skip levels

## CSS Layout — Flexbox vs Grid
```css
/* Flexbox — 1D layouts (row or column) */
.toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Grid — 2D layouts (rows and columns) */
.dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}
```

## CSS Variables for Theming
```css
:root {
  --color-primary: #6366f1;
  --color-bg: #0f172a;
  --color-text: #f1f5f9;
  --color-border: #334155;
  --radius: 0.5rem;
  --transition: 0.15s ease;
}

.card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  transition: all var(--transition);
}
```

## Responsive Design
- Mobile-first: write base styles for mobile, add breakpoints for larger
- Use `rem` for font sizes, `px` for borders/shadows
- Use `clamp()` for fluid typography: `font-size: clamp(1rem, 2.5vw, 1.5rem)`
- `max-width` on content containers (never full-width text)

```css
@media (min-width: 768px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 1024px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}
```

## Accessibility (a11y)
- Color contrast ratio: 4.5:1 minimum for text
- `tabindex="0"` for custom interactive elements
- `aria-label` for icon-only buttons
- Never use `outline: none` without a replacement focus style
- Respect `prefers-reduced-motion` for animations

## Dark Theme Pattern
- Use CSS variables for all colors
- Toggle a class on `<body>` or `<html>` (e.g., `.dark-theme`)
- Test both themes — don't just invert colors
