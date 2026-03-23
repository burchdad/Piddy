---
name: php
description: Modern PHP programming with Laravel, Symfony, Composer, type system, and best practices
---

# PHP Development

## Modern PHP (8.1+)
- Type system: scalar types, union types (string|int), intersection types (A&B), nullable (?string)
- Enums: enum Suit: string { case Hearts = 'H'; }, backed enums, methods on enums
- Readonly properties and readonly classes
- Fibers: lightweight concurrency primitives
- Named arguments: function(name: 'value', age: 25)
- Match expression: match($x) { 1 => 'one', default => 'other' }
- Null-safe operator: $user?->getAddress()?->getCity()
- First-class callable syntax: $fn = strlen(...)
- Attributes: #[Route('/path')] replacing docblock annotations
- Constructor property promotion: public function __construct(private string $name)
- Array destructuring: [$a, $b] = [1, 2]; ['key' => $val] = $arr
- String functions: str_contains, str_starts_with, str_ends_with
- Typed class constants (PHP 8.3)

## Laravel
- Artisan CLI: make:model, make:controller, make:migration, tinker
- Eloquent ORM: models, relationships (hasMany, belongsTo, morphTo), scopes, casts
- Query Builder: DB::table()->where()->get(), chunking, lazy collections
- Migrations: Schema::create, Blueprint methods, seeding
- Routing: Route::get/post/resource, middleware, route model binding
- Controllers: resource controllers, form requests for validation
- Blade templates: @if, @foreach, @extends, @section, @component
- Authentication: Sanctum (API tokens, SPA), Breeze, Jetstream
- Authorization: Gates, Policies
- Queues: dispatch jobs, queue workers, failed job handling
- Events and listeners, observers
- Collections: map, filter, reduce, pluck, groupBy, pipe
- Testing: Feature tests, Unit tests, RefreshDatabase, actingAs
- API Resources: JsonResource, ResourceCollection for API responses

## Symfony
- Bundle system, service container, autowiring
- Doctrine ORM: entities, repositories, DQL, migrations
- Routing: attributes/annotations, YAML/XML configuration
- Twig templates: extends, block, include, macros
- Form component: form types, validation constraints
- Security component: firewalls, voters, access control
- Console: commands, input/output, progress bars
- Messenger: message bus, handlers, transports

## Composer
- composer.json: require, require-dev, autoload (PSR-4)
- Commands: install, update, require, dump-autoload
- Packagist: package discovery and versioning (semver)
- composer.lock: reproducible installs

## Testing
- PHPUnit: TestCase, assertions, data providers, mocking
- Pest: expressive syntax, describe/it blocks, expectations
- Laravel-specific: assertStatus, assertJson, assertDatabaseHas
- Mockery: mock, shouldReceive, expectations
- Static analysis: PHPStan (level 0-9), Psalm

## Best Practices
- Use strict types: declare(strict_types=1) in every file
- Follow PSR-12 coding standard, PSR-4 autoloading
- Type everything: parameters, return types, properties
- Use enums over string/int constants
- Validate at boundaries with form requests
- Never trust user input — parameterized queries, htmlspecialchars
- Run PHPStan at level 6+ in CI
