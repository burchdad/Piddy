# HTML & CSS Quick Reference

## Language: HTML5 / CSS3+
**Paradigm:** Document structure (HTML), Presentation (CSS)  
**Standard:** WHATWG Living Standard / CSS Modules Level 3-5  

## HTML Semantic Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title</title>
</head>
<body>
  <header><nav aria-label="Main"><ul><li><a href="/">Home</a></li></ul></nav></header>
  <main>
    <article><h1>Title</h1><p>Content.</p></article>
    <aside>Sidebar</aside>
  </main>
  <footer><p>&copy; 2024</p></footer>
</body>
</html>
```

## CSS Layout

```css
/* Flexbox */
.flex { display: flex; justify-content: center; align-items: center; gap: 1rem; }
.flex-item { flex: 1 1 200px; }

/* Grid */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}
```

## CSS Modern Features

```css
/* Custom properties */
:root { --color-primary: #3b82f6; --spacing: 1rem; }
.card { padding: var(--spacing); }

/* Container queries */
.card-container { container-type: inline-size; }
@container (min-width: 400px) { .card { flex-direction: row; } }

/* :has() parent selector */
form:has(:invalid) button { opacity: 0.5; }

/* Nesting (native) */
.card {
  padding: 1rem;
  & .title { font-size: 1.5rem; }
  &:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
}
```

## Responsive Design

```css
@media (min-width: 768px) { /* tablet+ */ }
h1 { font-size: clamp(1.5rem, 4vw, 3rem); }
.video { aspect-ratio: 16 / 9; }
@media (prefers-color-scheme: dark) {
  :root { --color-bg: #0f172a; }
}
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; }
}
```
