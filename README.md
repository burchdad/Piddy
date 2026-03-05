# Piddy - Backend Developer AI Agent

An intelligent, comprehensive backend developer AI agent capable of handling all aspects of backend development. Piddy integrates seamlessly with Slack for team communication and accepts commands from other AI agents through a robust API interface.

## Features

### Core Capabilities
- **Code Generation**: Generate production-ready code across multiple languages and frameworks
- **API Design**: Design and implement REST, GraphQL, and other API architectures
- **Database Design**: Create and optimize database schemas and migrations
- **Code Review**: Analyze and provide feedback on code quality and improvements
- **Debugging**: Identify and fix bugs in existing code
- **Infrastructure**: Design and manage infrastructure as code (Docker, Kubernetes, etc.)
- **Documentation**: Generate comprehensive technical documentation
- **Architecture Design**: Design scalable, maintainable system architectures

### Integration Channels
- **Slack**: Real-time communication with development teams
- **Agent API**: Accept commands from other AI agents
- **Batch Processing**: Process multiple tasks sequentially or in parallel

## Project Structure

```
Piddy/
├── src/
│   ├── agent/           # Core agent logic
│   ├── integrations/    # External integrations (Slack, etc.)
│   ├── api/            # FastAPI routes and endpoints
│   ├── tools/          # Agent tools and capabilities
│   ├── models/         # Pydantic data models
│   └── utils/          # Utility functions
├── config/             # Configuration management
├── tests/              # Test suite
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # This file
```

## Installation

### Prerequisites
- Python 3.11+
- pip or poetry
- Slack workspace (for Slack integration)
- Anthropic API key (for Claude models)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Piddy
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run the application**
   ```bash
   python -m src.main
   ```

The application will start on `http://localhost:8000`

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_TOKEN=xapp-your-app-token

# Anthropic API
ANTHROPIC_API_KEY=your-api-key

# Agent Configuration
AGENT_MODEL=claude-3-opus-20240229
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=4096

# Database
DATABASE_URL=sqlite:///./piddy.db

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True
```

## Usage

### API Interface (For Other Agents)

Send a POST request to `/api/v1/agent/command`:

```bash
curl -X POST "http://localhost:8000/api/v1/agent/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command_type": "code_generation",
    "description": "Generate a Python FastAPI endpoint for user authentication",
    "context": {
      "framework": "FastAPI",
      "auth_type": "JWT"
    },
    "priority": 8
  }'
```

### Command Types

- `code_generation` - Generate code implementations
- `api_design` - Design and specify APIs
- `database_schema` - Create database schemas
- `code_review` - Review and improve code
- `debugging` - Debug and fix issues
- `infrastructure` - Infrastructure as code
- `documentation` - Generate documentation
- `migration` - Handle database/code migrations
- `custom` - Custom backend development tasks

### Available Endpoints

- `GET /` - Root endpoint with service info
- `GET /docs` - OpenAPI documentation
- `GET /api/v1/agent/health` - Agent health check
- `GET /api/v1/agent/capabilities` - List agent capabilities
- `POST /api/v1/agent/command` - Execute a single command
- `POST /api/v1/agent/command/batch` - Execute multiple commands
- `POST /slack/events` - Slack event webhook

## Slack Integration

### Quick Start (5 Minutes)

1. **Get tokens**: Create Slack app at https://api.slack.com/apps
2. **Configure**: Copy tokens to `.env` (see [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md))
3. **Run**: 
   ```bash
   bash start-slack.sh    # Linux/Mac
   # or
   start-slack.bat       # Windows
   ```
4. **Chat**: Mention `@Piddy` in any channel or send a direct message

### Usage in Slack

Mention Piddy in a channel or DM to request backend development tasks:

```
@Piddy Generate a Python function that validates email addresses

@Piddy Design a database schema for a blog application

@Piddy Review this code for security vulnerabilities
```

### Documentation

- **[SLACK_INDEX.md](SLACK_INDEX.md)** - Complete navigation guide for all Slack docs
- **[SLACK_QUICK_REFERENCE.md](SLACK_QUICK_REFERENCE.md)** - Quick commands and examples (5 min read)
- **[SLACK_INTEGRATION.md](SLACK_INTEGRATION.md)** - Full setup guide with screenshots (10 min read)
- **[SLACK_TROUBLESHOOTING.md](SLACK_TROUBLESHOOTING.md)** - Troubleshooting & FAQ (reference)
- **[start-slack.sh](start-slack.sh)** / **[start-slack.bat](start-slack.bat)** - Automated startup scripts

### Supported Commands

| Area | Examples |
|------|----------|
| **Code Generation** | Generate endpoints, create functions, write implementations |
| **Code Review** | Analyze quality, security audit, refactoring suggestions |
| **Database Design** | Schema design, migrations, indexing strategies |
| **API Design** | REST, GraphQL, or gRPC API architecture |
| **Infrastructure** | Docker, Kubernetes, cloud deployment configs |
| **Security** | Vulnerability analysis, best practices review |
| **Architecture** | Design patterns, system architecture blueprints |
| **Documentation** | Technical specs, API docs, system design docs |

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Check linting
flake8 src/

# Type checking
mypy src/
```

### Adding New Tools

1. Create a new tool file in `src/tools/`
2. Implement tool functions
3. Register tools in `src/tools/__init__.py`
4. Update agent initialization

## Architecture

### Agent Flow

```
Command Input (Slack/API)
    ↓
Command Parser
    ↓
Backend Developer Agent
    ↓
Tool Selection & Execution
    ↓
Result Processing
    ↓
Response Output (Slack/API)
```

### Communication Flow

```
Other AI Agents → API Interface → Command Queue
Development Teams → Slack Interface → Event Handler
                        ↓
                  Backend Developer Agent
                        ↓
                   Tool Execution
                        ↓
              Response to Requestor
```

## Roadmap

### Phase 1 (MVP)
- ✅ Core agent architecture
- ✅ Slack integration foundation
- ✅ Agent command API
- ✅ Basic code generation tools
- ✅ Database schema generation

### Phase 2 (Advanced Features)
- ✅ Advanced code analysis and review
- ✅ Git integration (version control)
- ✅ Memory/context persistence
- ✅ Advanced error handling
- ✅ Safe file writing

**Phase 2 New Capabilities:**
- **Code Quality Scoring**: Automated analysis with issue categorization (Security, Performance, Best Practices)
- **Git Operations**: Automatic commits, branch management, push/pull
- **Conversation Memory**: Store and retrieve context from past interactions
- **Safe File Writing**: Intelligent path resolution for generated code
- **Error Recovery**: Graceful degradation with automatic retry logic

**Phase 2 Slack Commands:**
- `@Piddy review this: [code]` — Advanced code review with quality scoring
- `Piddy commit` — Commit generated code with automatic staging
- `Piddy git status` — Check repository status
- `Piddy remember this` — Save conversation context to memory

### Phase 3
- [ ] Multi-language support expansion
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Monitoring and analytics
- [ ] Self-improvement mechanisms

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request

## License

This project is proprietary and confidential.

## Support

For issues and questions, please create an issue in the repository.
