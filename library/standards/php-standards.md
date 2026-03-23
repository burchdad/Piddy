# PHP Coding Standards

## Scope: PSR standards, modern PHP 8.x patterns
**Authority:** PSR-1, PSR-4, PSR-12, PHP-FIG  
**Tools:** PHP-CS-Fixer, PHPStan, Psalm, Rector  

## PSR Standards Summary

| PSR | Name | Key Points |
|-----|------|-----------|
| PSR-1 | Basic Coding | UTF-8, `<?php` tags, PascalCase classes |
| PSR-4 | Autoloading | Namespace = directory structure |
| PSR-12 | Extended Coding | Indentation, braces, line length |
| PSR-7 | HTTP Messages | Request/Response interfaces |
| PSR-11 | Container | Dependency injection interface |
| PSR-15 | HTTP Handlers | Middleware interface |

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Class | `PascalCase` | `UserService` |
| Method | `camelCase` | `getUserById()` |
| Property | `camelCase` | `$userName` |
| Constant | `UPPER_SNAKE` | `MAX_RETRIES` |
| Namespace | `PascalCase` | `App\Services` |
| File | `PascalCase` (matches class) | `UserService.php` |

## Modern PHP Patterns

```php
<?php
declare(strict_types=1);   // ALWAYS at top of every file

// Readonly classes (8.2+) for DTOs
readonly class UserDTO {
    public function __construct(
        public string $name,
        public string $email,
    ) {}
}

// Enums (8.1+) instead of class constants
enum Status: string {
    case Active = 'active';
    case Inactive = 'inactive';
}

// Named arguments for clarity
str_contains(haystack: $text, needle: 'search');

// Null-safe operator
$city = $user?->address?->city;
```
