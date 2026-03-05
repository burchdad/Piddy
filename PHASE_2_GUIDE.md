# Phase 2 Implementation Guide

## Overview

Phase 2 introduces advanced capabilities that transform Piddy from a basic code generator into a comprehensive backend development assistant with memory, quality control, and version management.

## Components Built

### 1. ✅ Advanced Code Analysis & Review (`src/tools/code_analyzer.py`)

**Features:**
- Security vulnerability detection (exec, eval, SQL injection, hardcoded secrets)
- Performance issue identification (N+1 queries, inefficient loops)
- Best practice enforcement (exception handling, type hints)
- Error handling analysis
- Type safety checks

**Usage in Agent:**
```python
from src.tools.code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()
result = analyzer.analyze(code, language="python")
# Returns: {
#   "issues": [CodeIssue],
#   "score": 72,  # 0-100
#   "recommendations": [...]
# }
```

**Slack Integration:**
When code is reviewed, Piddy will show:
```
📊 Code Quality: 72/100
🔴 CRITICAL: Hardcoded password detected
   💡 Use environment variables
🟡 MEDIUM: Bare except clause
   💡 Catch specific exceptions
```

---

### 2. ✅ Git Integration Module (`src/tools/git_manager.py`)

**Features:**
- Commit generation with automatic staging
- Branch creation and management
- Push/pull operations
- Status checking
- Diff viewing
- Commit history
- PR information generation

**Usage in Agent:**
```python
from src.tools.git_manager import get_git_manager

git = get_git_manager("/workspaces/Piddy")
result = git.commit(
    message="Add authentication endpoints",
    files=["src/auth/routes.py", "src/auth/models.py"]
)
# Returns: {"success": True, "commit_hash": "abc123", ...}
```

**Workflow:**
1. Agent generates code
2. Writes to appropriate file location
3. Stages the files in Git
4. Creates meaningful commit message
5. Pushes to branch

---

### 3. ✅ Memory & Context Persistence (`src/utils/memory.py`)

**Features:**
- SQLite-backed conversation history
- Artifact storage (generated code, configs)
- User preferences
- Context caching
- Full conversation retrieval

**Tables:**
- `conversations` - Chat threads with project context
- `messages` - Full message history with roles
- `artifacts` - Generated files/code
- `preferences` - User settings
- `context_cache` - Quick lookup cache

**Usage in Agent:**
```python
from src.utils.memory import get_memory

memory = get_memory()

# Save context
memory.create_conversation(
    conversation_id="slack_thread_123",
    user_id="U0123",
    channel_id="C0123",
    project_context="Piddy Backend",
    title="User Authentication Implementation"
)

# Add messages
memory.add_message(
    conversation_id="slack_thread_123",
    user_id="U0123",
    content="Generate FastAPI auth endpoints",
    role="user"
)

# Save artifacts
memory.save_artifact(
    conversation_id="slack_thread_123",
    artifact_type="code",
    content=generated_code,
    filename="auth_routes.py",
    file_path="src/auth/routes.py",
    language="python"
)

# Retrieve history
history = memory.get_conversation_history("slack_thread_123", limit=50)
```

**Benefits:**
- Agents learn from past interactions
- Can reference previous work
- Track project artifacts
- User preferences for customization

---

### 4. ✅ Advanced Error Handling (`src/utils/error_handler.py`)

**Features:**
- Error categorization (Security, External Service, Permission, etc.)
- Automatic severity detection
- Recovery suggestions
- Retry with exponential backoff
- Safe execution with fallbacks
- Graceful degradation

**Error Categories:**
- ✅ Validation errors
- ✅ External service failures
- ✅ Resource not found
- ✅ Permission denied
- ✅ Configuration issues
- ✅ Internal errors

**Usage in Agent:**
```python
from src.utils.error_handler import ErrorHandler

# Automatic retry with backoff
@ErrorHandler.retry_with_backoff(max_attempts=3, backoff_factor=2.0)
def call_external_api():
    ...

# Safe execution with fallback
result = ErrorHandler.safe_execute(
    risky_function,
    fallback="default_value",
    on_error=lambda e: logger.error(e.message)
)

# Error handling in Slack
error_info = ErrorHandler.categorize_error(exception)
slack_msg = error_info.to_slack_message()
# Shows user-friendly message with recovery steps
```

**Slack Error Messages:**
```
❌ ERROR | External Service
Connection timeout reaching OpenAI API

*Details:* Connection refused: 10.0.0.1:443

*Try:*
• Check service status
• Verify network connection
• Retry after a delay
```

---

### 5. ✅ File Writing System (`src/utils/file_writer.py`)

**Features:**
- Project-aware path resolution
- Safe file writing (no overwrite without consent)
- File type categorization
- Path validation
- Directory structure preview

**Usage in Agent:**
```python
from src.utils.file_writer import write_generated_file, FileType

result = write_generated_file(
    filename="auth_router.py",
    content=generated_code,
    file_type=FileType.ROUTE,
    subdir="auth"
)
# Result: {
#   "success": True,
#   "path": "src/api/routes/auth/auth_router.py",
#   "message": "✅ File written to: src/api/routes/auth/auth_router.py"
# }
```

---

## Integration Points

### Adding Code Review to Agent

```python
# In src/integrations/slack_handler.py
from src.tools.code_analyzer import CodeAnalyzer

async def handle_code_review_request(code: str, user_id: str):
    analyzer = CodeAnalyzer()
    result = analyzer.analyze(code)
    
    # Format for Slack
    review_blocks = {
        "score": result["score"],
        "issues": result["issues"][:10],
        "recommendations": result["recommendations"]
    }
    
    await slack_client.send_message(
        text=f"Code Review: {result['score']}/100",
        blocks=review_blocks
    )
```

### Auto-Commit Generated Code

```python
# After file writing
git = get_git_manager()

# Create branch
git.create_branch(f"feature/user-auth-{timestamp}")

# Commit generated code
git.commit(
    message=f"Add authentication: {description}",
    files=file_paths
)

# Push
git.push()
```

### Learning from History

```python
# Before generating code
memory = get_memory()
history = memory.get_conversation_history(conversation_id)

# Include context in prompt
system_prompt = f"""
Previous context:
- Task: {history[0].content}
- Previous attempts: {len(history)}
- Generated artifacts: {memory.get_artifacts(conversation_id)}
"""
```

---

## Phase 2 Roadmap Status

- ✅ Advanced code analysis and review
- ✅ Git integration (version control)
- ✅ Memory/context persistence
- ✅ Advanced error handling
- ✅ Safe file writing

**Remaining for Phase 2:**
- ⏳ Code execution environment (sandbox)
- ⏳ Integration with all agent commands
- ⏳ User preference system

---

## Phase 3 Preview

Once Phase 2 is complete, Phase 3 will focus on:

- **Multi-language Support**: Expand analyzer and tools to JavaScript, TypeScript, Go, Rust
- **Performance Optimization**: Caching, async operations, resource pooling
- **Security Hardening**: Encryption, rate limiting, audit logging
- **Monitoring & Analytics**: Metrics, dashboards, performance tracking
- **Self-Improvement**: Learning from successful patterns, continuous refinement

---

## Testing Phase 2

### Test Code Review
```python
test_code = """
def process_user(user_id):
    import pickle
    user_data = pickle.loads(get_data(user_id))
    exec(user_data['code'])
"""

analyzer = CodeAnalyzer()
result = analyzer.analyze(test_code)
assert result['score'] < 30
assert len(result['issues']) > 5
```

### Test Memory
```python
memory = get_memory()
memory.create_conversation("test_conv", "test_user", "test_channel")
memory.add_message("test_conv", "test_user", "Hello", role="user")
history = memory.get_conversation_history("test_conv")
assert len(history) == 1
```

### Test Git Integration
```python
git = get_git_manager()
status = git.get_status()
assert status['success']
assert 'branch' in status
```

---

## Next Steps

1. **Integrate into agent**: Add Phase 2 tools to BackendDeveloperAgent
2. **Update Slack commands**: New `/piddy review` and `/piddy commit` commands
3. **Test end-to-end**: Generate code → Review → Commit → Remember
4. **Document**: Update user guides and API documentation
5. **Migrate existing code**: Apply analyzer to existing Piddy codebase first

---

## Configuration

All Phase 2 systems use sensible defaults. Configure with environment variables:

```env
# Memory
PIDDY_MEMORY_DB=/workspaces/Piddy/.piddy_memory.db

# Git
PIDDY_GIT_USER_NAME=Piddy Agent
PIDDY_GIT_USER_EMAIL=piddy@agent.local

# File writing
PIDDY_PROJECT_ROOT=/workspaces/Piddy

# Error handling
PIDDY_MAX_RETRIES=3
PIDDY_RETRY_DELAY=1.0
```

---

This Phase 2 implementation provides the foundation for Piddy to be a true productivity multiplier for backend teams! 🚀
