# PHP Quick Reference

## Language: PHP 8.3+
**Paradigm:** OOP, procedural, functional elements  
**Typing:** Gradual typing (dynamic to static annotations)  
**Runtime:** Zend Engine, also Swoole for async  

## Modern Syntax (PHP 8.x)

```php
<?php
declare(strict_types=1);

// Named arguments
str_contains(haystack: $text, needle: "search");

// Match expression
$label = match($status) {
    200 => 'OK',
    404 => 'Not Found',
    500, 503 => 'Server Error',
    default => 'Unknown',
};

// Null handling
$city = $user?->address?->city;
$name = $input ?? 'default';

// Enums (8.1+)
enum Status: string {
    case Active = 'active';
    case Inactive = 'inactive';
    case Pending = 'pending';
}
```

## Classes

```php
// Readonly classes & constructor promotion (8.2+)
readonly class Point {
    public function __construct(
        public float $x,
        public float $y,
    ) {}
}

// Traits
trait HasTimestamps {
    public DateTime $createdAt;
    public DateTime $updatedAt;
}

class User implements Cacheable, JsonSerializable {
    use HasTimestamps;

    public function __construct(
        private readonly int $id,
        private string $name,
    ) {}
}

// Intersection & union types
function process(Countable&Iterator $items): int|false { }
```

## Arrays & Functional

```php
$names = array_map(fn($u) => $u['name'], $users);
$adults = array_filter($users, fn($u) => $u['age'] >= 18);
$total = array_reduce($items, fn($sum, $i) => $sum + $i['price'], 0);

// Spread
$merged = [...$defaults, ...$overrides];

// Arrow functions (auto-capture)
$multiplier = 3;
$result = array_map(fn($n) => $n * $multiplier, $nums);
```

## Tooling

```bash
composer init
composer require package/name
phpunit
phpstan analyse
php-cs-fixer fix
```
