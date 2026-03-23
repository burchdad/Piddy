---
name: testing
description: Write effective tests — unit, integration, and end-to-end testing strategies
---

# Testing

## Test Pyramid
- **Unit tests** (70%) — Fast, isolated, test one function/method
- **Integration tests** (20%) — Test modules working together, real DB/API
- **E2E tests** (10%) — Full user flows, slowest but highest confidence

## Unit Test Patterns (Python / pytest)
```python
import pytest

def test_create_user_valid():
    """Test that valid input creates a user."""
    user = create_user(name="Alice", email="alice@example.com")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.id is not None

def test_create_user_empty_name_raises():
    """Test that empty name raises ValueError."""
    with pytest.raises(ValueError, match="name cannot be empty"):
        create_user(name="", email="alice@example.com")

@pytest.fixture
def db_session():
    """Provide a clean database session for each test."""
    session = create_test_session()
    yield session
    session.rollback()
    session.close()
```

## Unit Test Patterns (JavaScript / Jest)
```javascript
describe('UserService', () => {
  it('creates user with valid input', async () => {
    const user = await createUser({ name: 'Alice', email: 'a@b.com' });
    expect(user.name).toBe('Alice');
    expect(user.id).toBeDefined();
  });

  it('throws on empty name', async () => {
    await expect(createUser({ name: '' }))
      .rejects.toThrow('name cannot be empty');
  });
});
```

## What to Test
- **Happy path** — Normal input, expected output
- **Edge cases** — Empty input, boundary values, null/undefined
- **Error cases** — Invalid input, network failures, timeouts
- **State transitions** — Before/after a mutation

## What NOT to Test
- Framework internals (don't test that React renders a div)
- Trivial getters/setters with no logic
- Implementation details (test behavior, not how it's done)
- Third-party library behavior

## Mocking Guidelines
- Mock external dependencies (HTTP, database, file system)
- Don't mock the thing you're testing
- Prefer fakes over mocks when possible (in-memory DB > mocked DB)
- Verify mock calls only if the interaction IS the behavior

## Test Naming Convention
- `test_<what>_<condition>_<expected>` (Python)
- `it('should <expected> when <condition>')` (JavaScript)
