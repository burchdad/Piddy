---
name: angular
description: Angular framework with TypeScript, RxJS, signals, standalone components, and enterprise patterns
---

# Angular Development

## Core Concepts
- Standalone components (default in Angular 17+): no NgModules needed
- Components: @Component decorator, template, styles, selector
- Templates: interpolation {{ }}, property binding [prop], event binding (event), two-way [(ngModel)]
- Directives: *ngIf/*ngFor (legacy), @if/@for (new control flow, Angular 17+)
- Pipes: | date, | async, | json, custom pipes with @Pipe
- Dependency injection: providedIn: 'root', inject() function (preferred over constructor injection)
- Signals (Angular 16+): signal(), computed(), effect() — reactive primitive
- Input/Output: input() and output() functions (signal-based, Angular 17+)
- Lifecycle: ngOnInit, ngOnDestroy, ngOnChanges, afterNextRender

## Routing
- RouterModule or provideRouter (standalone)
- Routes: path, component, children, loadComponent (lazy loading)
- Route guards: canActivate, canDeactivate, resolve
- Route parameters: ActivatedRoute, paramMap, queryParamMap
- Router events: NavigationStart, NavigationEnd

## Forms
- Reactive forms (preferred): FormGroup, FormControl, FormArray, Validators
- Template-driven forms: ngModel, ngForm (simpler use cases)
- Custom validators: sync and async
- Form arrays for dynamic fields

## RxJS
- Observable, Subject, BehaviorSubject, ReplaySubject
- Operators: map, filter, switchMap, mergeMap, concatMap, exhaustMap
- combineLatest, forkJoin, merge, concat
- Error handling: catchError, retry, retryWhen
- takeUntilDestroyed() for automatic cleanup (Angular 16+)
- Signals vs RxJS: use signals for synchronous state, RxJS for async streams

## HTTP
- HttpClient: get, post, put, delete — returns Observables
- Interceptors: functional interceptors (Angular 15+), auth token injection, error handling
- Typed responses: HttpClient.get<Type>(url)
- Error handling: catchError in pipe, centralized error interceptor

## State Management
- Signals for local/component state
- NgRx: Store, Actions, Reducers, Effects, Selectors (Redux pattern)
- NgRx SignalStore (newer): simpler signal-based state
- Component Store: localized state management
- Simple service-based state with BehaviorSubject or signals

## Testing
- Jasmine + Karma (default) or Jest
- TestBed: configureTestingModule, createComponent, inject
- Component testing: fixture, debugElement, ComponentFixture
- Service testing: TestBed.inject, HttpClientTestingModule, HttpTestingController
- Marble testing for RxJS streams
- Cypress/Playwright for E2E

## Build and Tooling
- Angular CLI: ng new, ng generate, ng serve, ng build, ng test
- Schematics: code generation, migrations
- SSR: Angular Universal / @angular/ssr
- Esbuild (Angular 17+): fast builds replacing webpack

## Best Practices
- Use standalone components (no NgModules for new projects)
- Prefer signals over RxJS for synchronous state
- Use inject() function over constructor injection
- OnPush change detection for performance
- Lazy load routes with loadComponent
- Use typed reactive forms
- Keep components smart/dumb separation (container/presentational)
- Use trackBy with @for loops for performance
