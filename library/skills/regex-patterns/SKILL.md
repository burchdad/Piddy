---
name: regex-patterns
description: Common regex recipes for validation, extraction, search-and-replace, and text processing
---

# Regex Patterns

Ready-to-use regex recipes for common tasks — validation, extraction, and text processing.

## Validation Patterns

```python
import re

# Email (simplified, covers 99% of real addresses)
EMAIL = r'^[\w.-]+@[\w.-]+\.\w{2,}$'

# URL
URL = r'^https?://[\w.-]+(?:\.[\w.-]+)+(?:/[\w._~:/?#\[\]@!$&\'()*+,;=-]*)?$'

# IPv4
IPV4 = r'^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$'

# Phone (US, flexible format)
PHONE_US = r'^\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'

# Date (YYYY-MM-DD)
DATE_ISO = r'^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$'

# Time (HH:MM or HH:MM:SS, 24h)
TIME_24H = r'^(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?$'

# UUID v4
UUID = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'

# Semantic Version
SEMVER = r'^\d+\.\d+\.\d+(?:-[\w.]+)?(?:\+[\w.]+)?$'

# Hex Color
HEX_COLOR = r'^#(?:[0-9a-fA-F]{3}){1,2}$'

# Strong Password (8+ chars, upper, lower, digit, special)
STRONG_PASSWORD = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

# Slug (URL-friendly)
SLUG = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
```

## Extraction Patterns

```python
# Extract all email addresses from text
emails = re.findall(r'[\w.-]+@[\w.-]+\.\w{2,}', text)

# Extract all URLs from text
urls = re.findall(r'https?://[^\s<>"]+', text)

# Extract numbers (integer and decimal)
numbers = re.findall(r'-?\d+\.?\d*', text)

# Extract hashtags
hashtags = re.findall(r'#(\w+)', text)

# Extract quoted strings
quoted = re.findall(r'"([^"]*)"', text)

# Extract HTML tags
tags = re.findall(r'<(\w+)[^>]*>', html)

# Extract key=value pairs
pairs = re.findall(r'(\w+)=(["\']?)(\S+?)\2(?:\s|$)', text)

# Extract IP addresses from logs
ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', log_text)
```

## Search and Replace

```python
# Remove HTML tags
clean = re.sub(r'<[^>]+>', '', html)

# Normalize whitespace
clean = re.sub(r'\s+', ' ', text).strip()

# Convert camelCase to snake_case
snake = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_case).lower()

# Convert snake_case to camelCase
def to_camel(name):
    parts = name.split('_')
    return parts[0] + ''.join(w.capitalize() for w in parts[1:])

# Remove comments from code
no_comments = re.sub(r'#.*$', '', code, flags=re.MULTILINE)

# Mask sensitive data
masked = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '****-****-****-****', text)

# Fix double spaces
fixed = re.sub(r'  +', ' ', text)

# Add thousand separators
formatted = re.sub(r'(\d)(?=(\d{3})+(?!\d))', r'\1,', str(number))
```

## Log Parsing

```python
# Parse common log format
LOG_PATTERN = r'(?P<ip>[\d.]+) - - \[(?P<date>[^\]]+)\] "(?P<method>\w+) (?P<path>\S+) HTTP/[\d.]+" (?P<status>\d+) (?P<size>\d+)'

for match in re.finditer(LOG_PATTERN, log_content):
    print(match.group('ip'), match.group('status'), match.group('path'))

# Parse key-value log lines
KV_PATTERN = r'(\w+)="?([^"\s]+)"?'
for line in log_lines:
    data = dict(re.findall(KV_PATTERN, line))
```

## Regex Cheat Sheet

### Character Classes

| Pattern | Matches |
|---------|---------|
| `.` | Any character (except newline) |
| `\d` | Digit [0-9] |
| `\w` | Word char [a-zA-Z0-9_] |
| `\s` | Whitespace |
| `\b` | Word boundary |
| `[abc]` | a, b, or c |
| `[^abc]` | NOT a, b, or c |
| `[a-z]` | Range a through z |

### Quantifiers

| Pattern | Matches |
|---------|---------|
| `*` | 0 or more |
| `+` | 1 or more |
| `?` | 0 or 1 |
| `{3}` | Exactly 3 |
| `{2,5}` | 2 to 5 |
| `{3,}` | 3 or more |
| `*?` | 0+ (lazy/non-greedy) |

### Groups and Lookaround

| Pattern | Meaning |
|---------|---------|
| `(abc)` | Capture group |
| `(?:abc)` | Non-capturing group |
| `(?P<name>abc)` | Named group |
| `(?=abc)` | Lookahead (followed by abc) |
| `(?!abc)` | Negative lookahead |
| `(?<=abc)` | Lookbehind (preceded by abc) |
| `\1` | Back-reference to group 1 |

### Flags

```python
re.IGNORECASE  # Case-insensitive matching
re.MULTILINE   # ^ and $ match line start/end
re.DOTALL      # . matches newline too
re.VERBOSE     # Allow comments and whitespace in pattern
```

## Performance Tips

1. **Compile repeated patterns**: `pattern = re.compile(r'...')` then `pattern.findall(text)`
2. **Prefer non-greedy** `.*?` when matching between delimiters
3. **Avoid catastrophic backtracking**: Don't nest quantifiers like `(a+)+`
4. **Use `re.findall`** for simple extraction, `re.finditer` for large texts
5. **Anchor patterns** with `^` and `$` when validating full strings
