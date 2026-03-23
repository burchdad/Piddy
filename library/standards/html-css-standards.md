# HTML & CSS Standards

## Scope: Semantic HTML, accessibility, CSS architecture, responsive design
**Authority:** WCAG 2.2, BEM methodology, CUBE CSS, MDN best practices  
**Tools:** axe, Lighthouse, Stylelint, PurgeCSS  

## Semantic HTML

```html
<!-- Use semantic elements, not div soup -->
<header>          <!-- not <div class="header"> -->
<nav>             <!-- not <div class="nav"> -->
<main>            <!-- one per page, main content -->
<article>         <!-- self-contained content -->
<section>         <!-- thematic grouping with heading -->
<aside>           <!-- tangentially related -->
<footer>          <!-- not <div class="footer"> -->

<!-- Headings: proper hierarchy (never skip levels) -->
<h1>Page Title</h1>
  <h2>Section</h2>
    <h3>Subsection</h3>
```

## Accessibility (a11y) Essentials

| Rule | Implementation |
|------|---------------|
| Alt text on images | `<img alt="User profile photo">` (decorative: `alt=""`) |
| Labels on inputs | `<label for="email">` or `aria-label` |
| Keyboard navigation | All interactive elements focusable, logical tab order |
| Color contrast | 4.5:1 for text, 3:1 for large text (WCAG AA) |
| ARIA sparingly | Prefer semantic HTML; ARIA only when HTML isn't enough |
| Skip link | First focusable element skips to `<main>` |
| `lang` attribute | `<html lang="en">` |

## CSS Naming (BEM)

```css
/* Block: standalone component */
.card { }

/* Element: part of a block */
.card__title { }
.card__body { }
.card__footer { }

/* Modifier: variation of block/element */
.card--featured { }
.card__title--large { }
```

**Rules:**
- One component per file
- Prefer custom properties over magic numbers
- Mobile-first: `min-width` media queries

## CSS Custom Properties

```css
:root {
  /* Spacing scale */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 2rem;

  /* Colors */
  --color-primary: #3b82f6;
  --color-text: #1e293b;
  --color-bg: #ffffff;

  /* Typography */
  --font-sans: system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-text: #e2e8f0;
    --color-bg: #0f172a;
  }
}
```
