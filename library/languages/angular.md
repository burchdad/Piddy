# Angular Quick Reference

## Language: Angular 17+
**Paradigm:** Full-featured application framework  
**Typing:** TypeScript  
**Architecture:** Component-based, dependency injection, RxJS  

## Standalone Components

```typescript
import { Component, signal, computed } from '@angular/core';

@Component({
  selector: 'app-counter',
  standalone: true,
  template: `
    <p>Count: {{ count() }}</p>
    <p>Double: {{ double() }}</p>
    <button (click)="increment()">+</button>
  `
})
export class CounterComponent {
  count = signal(0);
  double = computed(() => this.count() * 2);
  increment() { this.count.update(n => n + 1); }
}
```

## Template Syntax (Angular 17+)

```html
@if (user) {
  <user-profile [user]="user" />
} @else {
  <login-form />
}

@for (item of items; track item.id) {
  <div>{{ item.name }}</div>
} @empty {
  <p>No items</p>
}

@defer (on viewport) {
  <heavy-component />
} @loading {
  <spinner />
}
```

## Services & DI

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
  getUsers() { return this.http.get<User[]>('/api/users'); }
}
```

## Tooling

```bash
ng new project-name --standalone
ng serve
ng build
ng test
ng generate component users/user-list
```
