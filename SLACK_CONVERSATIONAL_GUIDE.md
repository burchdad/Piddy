# Piddy Slack Conversational Mode Guide

## Overview

Piddy now supports **full conversational mode on Slack**! You can chat with Piddy just like you chat with GitHub Copilot here, while also retaining the ability to give it commands and instructions.

## Features

### 1. Natural Conversations
- Chat naturally about development topics
- Ask questions and get helpful answers
- Have discussions about architecture, debugging, best practices
- Context is maintained throughout the conversation

### 2. Smart Mode Detection
Piddy automatically detects whether you're:
- **Having a conversation** → Responds naturally and conversationally
- **Giving a command** → Responds with structured, detailed technical output

### 3. Conversation Memory
- Piddy remembers what you've discussed in the current conversation
- Uses this context to provide better answers
- Different channels and threads have separate conversation histories

### 4. Hybrid Support
- Give commands like you normally would: "generate a FastAPI endpoint"
- Have natural conversations: "what's the best way to handle authentication?"
- Mix both freely throughout the conversation

## How It Works

### Command Detection

Commands are automatically detected when your message contains action verbs like:
- `generate`, `create`, `write`, `code`
- `review`, `analyze`, `check`, `audit`
- `design`, `schema`, `database`
- `debug`, `fix`, `error`, `issue`
- `secure`, `security`, `vulnerability`
- `docker`, `kubernetes`, `deploy`
- `commit`, `git`, `status`
- And many more...

### Conversation Detection

Non-command messages are treated as conversational, such as:
- "How do I handle errors in async code?"
- "What's the difference between these two approaches?"
- "Should I use Redis or Memcached?"
- "Tell me about design patterns"
- "How does this code work?"

## Usage Examples

### Example 1: Conversational Question

**You:** "Hey, what's the best way to handle database migrations in a production environment?"

**Piddy:** "Good question! In production, you'll want to:
1. Use a migration tool like Alembic (Python) or Liquibase
2. Run migrations before deploying new code
3. Always have a rollback plan
4. Test in staging first
5. Monitor for issues during execution

What type of database are you using?"

**You:** "PostgreSQL"

**Piddy:** "Nice! For PostgreSQL, Alembic is the standard choice in Python, or Flyway/Liquibase if you prefer language-agnostic tools. They both handle versioning and provide rollback capabilities..."

### Example 2: Command Mode

**You:** "Generate a FastAPI endpoint for creating users with proper validation and error handling"

**Piddy:** [Provides structured code with:
- Full implementation
- Error handling
- Validation
- Type hints
- Best practices documented]

### Example 3: Hybrid Conversation

**You:** "I'm having trouble with concurrency. How should I approach this?"

**Piddy:** "Can you share more details? Are you working with async code, multiprocessing, or threading?"

**You:** "async/await with FastAPI"

**Piddy:** "Got it! For FastAPI, most concurrency issues come from... The best approach is usually... [explanation]"

**You:** "Can you show me an example?"

**Piddy:** [Generates code example with locks, semaphores, or appropriate patterns]

## Features in Detail

### 1. Context Awareness

Piddy maintains context per:
- **Channel** - Separate conversations for different team channels
- **User** - Tracks individual users
- **Thread** - Separate history for threaded messages

### 2. Conversation History

The last several messages in your conversation are automatically included when Piddy processes your message, allowing it to:
- Reference previous discussions
- Build on earlier explanations
- Provide more relevant answers

View conversation stats:
- Each channel has its own conversation context
- Old conversations auto-expire after 60 minutes of inactivity
- Maximum of 100 active conversations (automatic cleanup)

### 3. Smart Responses

**Conversation Mode:**
- Natural, friendly tone
- Concise answers
- No unnecessary headers or footers
- Slack-formatted for readability

**Command Mode:**
- Structured output
- Code blocks with proper syntax highlighting
- Headers and metadata
- Detailed explanations

### 4. Message Reactions

Piddy uses emoji reactions to show what's happening:
- 🤔 **Thinking** - Processing your message
- 💭 **Thought bubble** - In conversation mode
- ✅ **Check mark** - Command completed successfully
- 😊 **Smile** - Conversation complete
- ❌ **X mark** - Error occurred
- 😕 **Confused** - Couldn't understand

## Tips & Best Practices

### 1. Be Natural
- You can be casual in conversations
- Ask clarifying questions
- Refer back to earlier points

### 2. Mix Modes Freely
- Start with a question, get a conceptual answer
- Ask for code, get implementation
- Go back to discussing

### 3. Use Threads
- Keep conversations organized in threads
- Piddy maintains separate context per thread
- Great for focused discussions

### 4. Give Commands When You Need Them
- "Generate a complete test suite for..."
- "Analyze this code for security issues"
- "Review the architecture"

### 5. For Complex Tasks
- Start with a question to discuss approach
- Ask for specific implementation
- Iterate on the response

## Conversation Tips

### Good Questions for Conversation Mode
- "What are the pros and cons of...?"
- "How does...work?"
- "Should I use...or...?"
- "What's the best practice for...?"
- "Can you explain...?"
- "Walk me through...?"

### Good Commands for Command Mode
- "Generate a FastAPI endpoint that..."
- "Create a database schema for..."
- "Review this code: [code]"
- "Analyze this for security issues"
- "Write a test for this function"

## Troubleshooting

### Piddy Not Responding to Messages
- Ensure the Slack bot is invited to the channel
- Check that Slack events are being received
- Verify webhook URL is correct

### Getting Command Responses When You Want Conversation
- Commands are triggered by action keywords
- If Piddy isn't detecting it as a command, it will treat it as conversation
- Use explicit keywords to trigger command mode

### Conversation Context Not Showing Up
- Context is accumulated within a conversation
- New threads start fresh contexts
- Old conversations expire after 60 minutes

## Architecture

The conversational system consists of:

1. **Slack Conversation Manager** (`slack_conversation.py`)
   - Maintains per-channel/user/thread context
   - Stores message history
   - Auto-cleanup of old conversations

2. **Enhanced Message Processor** (`slack_handler.py`)
   - Detects command vs. conversation mode
   - Routes to appropriate handler
   - Maintains conversation history

3. **Dual Executor Agent** (`agent/core.py`)
   - Command executor: Full technical responses
   - Conversation executor: Natural, friendly responses
   - Shared tools for both

4. **Slack API Integration** (`slack_commands.py`)
   - Receives events from Slack
   - Verifies webhook signatures
   - Routes to message processor

## What's Stored

Piddy stores per-conversation:
- User ID
- Channel ID
- Message history (last ~10 exchanges)
- Timestamps
- Metadata (command types, etc.)

**Note:** Message history expires after 60 minutes of inactivity.

## Advanced Usage

### Thread Usage
```
Main channel: "What's the best practice for error handling?"
  └─ Thread: Piddy explains general principles
  └─ You: "Show me an example code"
  └─ Piddy: [Remembers the context, provides relevant code]
```

### Channel Separation
- Different team channels have separate conversation contexts
- Allows for context-specific discussions
- You can chat about the same topic differently in different channels

### Multi-Turn Conversations
```
You: "I need to build an auth system"
Piddy: "What authentication method? OAuth, JWT, sessions?"
You: "JWT with refresh tokens"
Piddy: "Good choice. Here's how to implement that..." [continues with context]
```

## Coming Soon

- Conversation search and retrieval
- Conversation exports
- Conversation analytics
- Custom personality modes
- Team-wide context sharing

## Questions?

For issues or questions about Piddy's conversational mode:
1. Check the logs (typically in dashboard)
2. Try a simple test message
3. File an issue with the message and response

Enjoy chatting with Piddy!
