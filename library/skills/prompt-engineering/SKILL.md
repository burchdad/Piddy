---
name: prompt-engineering
description: Write effective LLM prompts — system instructions, few-shot examples, chain-of-thought, and output formatting
---

# Prompt Engineering

Write effective prompts for LLMs — clear instructions, structured output, and reliable results.

## Core Principles

1. **Be specific** — "Summarize in 3 bullet points" not "Summarize this"
2. **Show, don't describe** — Give examples of desired output
3. **Set constraints** — Length, format, tone, what NOT to include
4. **Assign a role** — "You are a senior Python developer" focuses the response
5. **Structure the output** — JSON, markdown, specific format

## System Prompt Structure

```
[ROLE] Who you are and your expertise
[TASK] What you're doing
[CONSTRAINTS] Rules and boundaries
[FORMAT] How to structure the output
[EXAMPLES] (Optional) Show desired input→output pairs
```

### Example System Prompt

```
You are a senior code reviewer specializing in Python.

When reviewing code:
1. Check for bugs and logic errors first
2. Then security issues
3. Then performance
4. Then style/readability

Output format:
- List issues as: [SEVERITY] Line X: Description → Fix
- Severities: CRITICAL, WARNING, INFO
- End with a summary: "X issues found (Y critical, Z warnings)"
- If the code is clean, say "No issues found"

Do NOT:
- Rewrite the entire code
- Suggest style changes unless they affect readability
- Comment on things that are correct
```

## Few-Shot Prompting

Provide 2-3 examples to establish the pattern:

```
Convert these natural language descriptions to SQL:

Input: "Show me all users who signed up last month"
Output: SELECT * FROM users WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') AND created_at < DATE_TRUNC('month', CURRENT_DATE);

Input: "Count orders by status"
Output: SELECT status, COUNT(*) as count FROM orders GROUP BY status ORDER BY count DESC;

Input: "Find the top 5 customers by total spend"
Output:
```

## Chain-of-Thought

For complex reasoning, ask the model to think step-by-step:

```
Analyze this code for potential race conditions.

Think through it step by step:
1. Identify all shared state (variables accessed by multiple threads)
2. For each shared variable, check if access is synchronized
3. Look for read-modify-write patterns without locks
4. Check for ordering dependencies between operations
5. State your conclusion with specific line references

Code:
[paste code]
```

## Output Formatting

### JSON Output

```
Extract the following information as JSON:
{
  "name": "string",
  "email": "string",
  "topics": ["string"],
  "sentiment": "positive" | "negative" | "neutral"
}

Respond with ONLY the JSON, no other text.
```

### Structured Analysis

```
Analyze this error using the following template:

## Error Analysis
**Error**: [exact error message]
**Root Cause**: [one sentence]
**Fix**: [specific code change]
**Prevention**: [how to avoid this in future]
```

## Prompt Patterns

### Constraint Prompting
```
Write a function that:
- Takes a list of integers
- Returns the second largest unique value
- Handles edge cases (empty list, all same values)
- Uses no built-in sort functions
- Is O(n) time complexity
```

### Negative Prompting
```
Explain OAuth 2.0.

Do NOT:
- Use jargon without defining it
- Include code examples
- Exceed 200 words
- Use bullet points (prose only)
```

### Iterative Refinement
```
Step 1: "Write a basic Flask API endpoint for user registration"
Step 2: "Add input validation and error handling"
Step 3: "Add rate limiting and logging"
Step 4: "Add tests for the endpoint"
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Vague instructions | Be specific about format, length, content |
| Too many tasks at once | Break into sequential prompts |
| No examples | Add 1-3 few-shot examples |
| Assuming context | State all relevant background |
| Not testing edge cases | Try adversarial inputs |
| Ignoring model strengths | Use code models for code, general for prose |

## Temperature Guide

| Task | Temperature | Why |
|------|-------------|-----|
| Code generation | 0.0 - 0.2 | Deterministic, correct output |
| Code review | 0.1 - 0.3 | Mostly analytical |
| Technical writing | 0.3 - 0.5 | Some creativity needed |
| Creative writing | 0.7 - 0.9 | More varied output |
| Brainstorming | 0.8 - 1.0 | Maximum diversity |
