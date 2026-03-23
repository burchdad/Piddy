# Testing Standards & Best Practices

## Scope: Unit, integration, E2E testing patterns
**Authority:** xUnit Patterns, Testing Trophy (Kent C. Dodds), Google Testing Blog  
**Tools:** pytest, Jest/Vitest, JUnit, xUnit, Playwright, Cypress  

## Test Naming

```python
# Python: descriptive snake_case
def test_create_user_returns_201_with_valid_input():
def test_create_user_raises_validation_error_for_missing_email():

# JavaScript/TypeScript: describe + it
describe('UserService', () => {
  it('should return user when valid ID provided', () => {});
  it('should throw NotFoundError for missing user', () => {});
});

# Java: methodName_condition_expectedResult
void createUser_validInput_returns201()
void createUser_missingEmail_throwsValidationException()
```

## Test Structure (AAA / Given-When-Then)

```python
def test_apply_discount_reduces_total():
    # Arrange (Given)
    cart = Cart(items=[Item("Widget", price=100)])
    discount = Discount(percent=20)

    # Act (When)
    cart.apply_discount(discount)

    # Assert (Then)
    assert cart.total == 80
    assert cart.discount_applied is True
```

**Rules:**
- One logical assertion per test (related assertions OK)
- Test behavior, not implementation
- Tests should be independent (no shared mutable state)

## Testing Pyramid / Trophy

```
       /  E2E  \          Few: critical user paths
      /----------\
     / Integration \      More: API, DB, service boundaries
    /----------------\
   /   Unit (logic)    \  Most: pure functions, business rules
  /--------------------\
 /   Static Analysis    \  Baseline: types, lints
/========================\
```

| Level | Speed | Scope | When |
|-------|-------|-------|------|
| Static | Instant | Types, lints | Every save |
| Unit | ms | Single function/class | Every commit |
| Integration | seconds | Service boundaries | Every PR |
| E2E | minutes | Full user flows | Pre-deploy |

## Test Doubles

| Type | Purpose | Example |
|------|---------|---------|
| **Stub** | Return fixed data | `stub_repo.get_user = lambda id: User("test")` |
| **Mock** | Verify interactions | `mock_email.send.assert_called_once()` |
| **Fake** | Working implementation (simplified) | In-memory database |
| **Spy** | Record calls, delegate to real | Wrap real service, check call count |

**Prefer fakes over mocks** for complex dependencies.
**Never mock what you don't own** — wrap third-party APIs in your own interface.

## Anti-Patterns to Avoid

| Anti-Pattern | Better |
|-------------|--------|
| Testing implementation details | Test observable behavior |
| Flaky tests (time, network) | Use clocks, stubs, deterministic data |
| Shared mutable test state | Fresh fixtures per test |
| Giant test setup | Builder/factory patterns |
| No assertions (test runs = passes) | Always assert expected outcomes |
| Testing trivial code (getters) | Focus on logic with branches |
| Copy-paste test code | Extract helpers / parameterize |
