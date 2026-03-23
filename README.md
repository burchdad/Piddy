# Piddy -- Portable AI Development Assistant

A fully portable, plug-and-play AI assistant that runs from any directory with zero installation. Piddy ships with embedded runtimes (Python 3.11.9, Node.js 20.19.0, Ollama v0.18.2), a React dashboard, an Electron desktop app, and a 21-agent consensus system.

**Version 5.2.0** -- 60 skills -- 21 agents -- 51 development phases

## Quick Start

```bash
# From the Piddy directory (USB drive, external drive, any folder)
python piddy.py start          # -> Dashboard at http://localhost:8889

# Or launch the Electron desktop app (no ports needed)
python piddy.py desktop

# Check system health
python piddy.py doctor

# See all commands
python piddy.py --help
```

> **No installation required.** Piddy uses embedded runtimes at `runtime/python/`, `runtime/node/`, and `runtime/ollama/`. Just copy the folder and run.

## Table of Contents
- [Quick Start](#quick-start)
- [Features](#features)
- [CLI Commands](#cli-commands)
- [Project Structure](#project-structure)
- [Dashboard](#dashboard)
- [Desktop App](#desktop-app-electron)
- [Integrations](#integrations)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [Development](#development)
- [Contributing](#contributing)

## Features

### Portable Architecture
- **Zero-install**: Embedded Python 3.11.9, Node.js 20.19.0, Ollama v0.18.2
- **Runs anywhere**: USB drive, external drive, any local folder
- **Electron desktop app**: Zero-port stdio RPC -- no network ports opened
- **Web dashboard**: FastAPI + React on port 8889
- **4-tier LLM failover**: Local Engine -> Ollama -> Anthropic Claude -> OpenAI GPT-4o

### AI Agent System
- **21 specialized agents** with reputation-weighted consensus voting
- **60 reference skill packs** covering languages, frameworks, and patterns
- **6-stage mission pipeline**: Planning -> Consensus -> Approval -> Execution -> Commit -> Persist
- **Self-improving**: Learns from every mission outcome (Phase 19)
- **Knowledge graph**: Persistent SQLite (1335+ nodes, 2502+ edges)

### Core Development
- **Code generation**: 10+ languages (Python, JS/TS, Go, Java, Rust, C#, PHP, Ruby, C++, Kotlin)
- **API design**: REST, GraphQL, gRPC with validation and auth
- **Database design**: Schema optimization, migrations, query tuning
- **Code review**: Automated analysis with pylint, autopep8, isort, bandit
- **Testing**: Real pytest with coverage reporting
- **Security**: RBAC, audit logging, encryption, vulnerability scanning

### Integrations
- **Slack**: `/nova` commands with full mission pipeline
- **Discord**: Bot integration (discord.py 2.7.1)
- **Telegram**: Bot integration (python-telegram-bot 22.7)
- **Browser automation**: Playwright 1.58.0 with Chromium
- **Productivity**: Google Calendar, Jira, Notion connectors
- **GitHub**: PR creation, branch management, real commits
- **CI/CD**: GitHub Actions, Jenkins, GitLab CI, CircleCI, Azure Pipelines

### Enterprise (Phases 27-31)
- **PR-based workflow**: Approval gates replace direct commits
- **Sandboxed execution**: Docker isolation with resource limits
- **Multi-agent protocol**: Capability-based routing and orchestration
- **Compliance**: GDPR, HIPAA, SOC2, PCI-DSS policy enforcement
- **Cryptographic audit logs**: HMAC-SHA256 signed, immutable

---

## CLI Commands

```bash
python piddy.py <command>
```

| Command | Description |
|---------|-------------|
| `start` | Start the web dashboard (port 8889) |
| `stop` | Stop running services |
| `status` | Show system status |
| `doctor` | Run 17 health checks |
| `config` | View/edit configuration |
| `export` | Export data or reports |
| `agents` | List or manage agents |
| `skills` | List, reload, or inspect skills |
| `desktop` | Launch the Electron desktop app |
| `scan` | Run security scanning |
| `update` | Check for updates |
| `platform` | Platform diagnostics |
| `discord` | Start Discord bot |
| `telegram` | Start Telegram bot |
| `browse` | Launch browser automation |
| `productivity` | Manage productivity connectors |

---

## Project Structure

```
Piddy/
+-- piddy.py                 # Main CLI entry point
+-- piddy/                   # CLI command modules
|   +-- rpc_endpoints.py     # 45 RPC endpoints + 6 stream functions
|   +-- *.py                 # Command handlers (start, stop, doctor, etc.)
+-- src/
|   +-- agent/               # Core agent logic & spawning
|   +-- api/                 # FastAPI routes and endpoints
|   +-- dashboard_api.py     # Dashboard REST API (port 8889)
|   +-- infrastructure/      # Agent framework & mission config
|   +-- coordination/        # Multi-agent coordination
|   +-- integration/         # Discord, Telegram, browser, productivity
|   +-- integrations/        # Slack integration
|   +-- kb/                  # Knowledge base management
|   +-- models/              # Pydantic data models
|   +-- platform/            # Platform detection & portability
|   +-- reasoning/           # Advanced graph reasoning
|   +-- services/            # Service manager & background tasks
|   +-- skills/              # Skill system engine
|   +-- tools/               # Agent tools and capabilities
|   +-- utils/               # Utility functions
|   +-- phase*.py            # Phase implementations (5-50)
+-- frontend/
|   +-- src/
|   |   +-- App.jsx          # Main app with IPC-aware routing
|   |   +-- components/      # 30 React dashboard components
|   |   +-- utils/           # apiClient.js (Electron IPC + web fetch)
|   |   +-- styles/          # App.css, components.css
|   +-- dist/                # Production build (63 modules)
|   +-- package.json
|   +-- vite.config.js
+-- desktop/
|   +-- main.js              # Electron main process
|   +-- preload.js           # IPC bridge (no raw fetch)
|   +-- stdio-protocol.js    # JSON-RPC over stdin/stdout
|   +-- package.json         # Electron 28.3.3
+-- runtime/
|   +-- python/              # Embedded Python 3.11.9
|   +-- node/                # Embedded Node.js 20.19.0
|   +-- ollama/              # Embedded Ollama v0.18.2
+-- library/
|   +-- skills/              # 60 skill reference packs
|       +-- python/          +-- javascript/
|       +-- react/           +-- fastapi/
|       +-- discord-bot/     +-- telegram-bot/
|       +-- browser-automation/ +-- electron-desktop/
|       +-- ...              # + 52 more
+-- config/                  # Configuration management
+-- data/                    # Runtime data & databases
+-- docs/                    # Documentation (14 active, 177 archived)
+-- scripts/                 # Utility scripts
+-- tests/                   # Test suite
+-- templates/               # Code generation templates
+-- requirements.txt         # Python dependencies
+-- .env.example             # Environment variables template
+-- docker-compose.yml       # Container deployment
```

---

## Dashboard

The web dashboard runs at `http://localhost:8889` with 30 React components:

| Page | Description |
|------|-------------|
| **Overview** | System status, agent health, recent activity |
| **Agents** | 21 agents with reputation scores and vote weights |
| **Missions** | Timeline visualization with 6-stage progression |
| **Mission Replay** | Step-by-step playback with speed controls (0.5x-4x) |
| **Decisions** | AI reasoning chains, confidence scores, factor analysis |
| **Dependency Graph** | Interactive SVG system architecture visualization |
| **Skills** | Browse and inspect 60 skill reference packs |
| **Chat** | Interactive AI chat interface |
| **Live Chat** | Real-time streaming responses |
| **Live Activity** | Real-time system event feed |
| **Sessions** | Conversation session management |
| **Messages** | Message history and search |
| **Logs** | System log viewer with filtering |
| **Tests** | Test execution and coverage reports |
| **Metrics** | Performance counters, gauges, histograms |
| **Security** | Vulnerability scanner, audit trails |
| **Scanner** | Code security scanning interface |
| **Rate Limits** | Token bucket rate limiting status |
| **Database Performance** | Query analysis and optimization |
| **Approvals** | PR-based approval gate management |
| **Phases** | Development phase status tracker |
| **Doctor** | 17 health checks with pass/fail status |
| **Export** | Data export in multiple formats |
| **Integrations** | Slack, Discord, Telegram status |
| **Browser Tool** | Playwright browser automation UI |
| **Productivity** | Google Calendar, Jira, Notion connectors |
| **Setup** | First-run configuration wizard |
| **Updater** | Check for and apply updates |

---

## Desktop App (Electron)

The Electron app provides a native desktop experience with **zero network ports**:

```bash
python piddy.py desktop
```

**How it works:**
1. Electron spawns a Python child process
2. Communication happens over **stdin/stdout JSON-RPC** (no HTTP, no ports)
3. The preload script bridges IPC calls to the renderer
4. The same React UI renders inside the Electron window

**Key files:**
- `desktop/main.js` -- Electron main process, spawns Python backend
- `desktop/preload.js` -- Context bridge exposing `window.piddy.call()`
- `desktop/stdio-protocol.js` -- JSON-RPC message framing and parsing
- `piddy/rpc_endpoints.py` -- 45 RPC endpoints + 6 stream functions

---

## Integrations

### Slack

Mention `@Piddy` in any channel or DM, or use `/nova` slash commands:

```
@Piddy Generate a Python function that validates email addresses
@Piddy Design a database schema for a blog application
/nova review src/main.py
```

See [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md) for full setup.

### Discord

```bash
python piddy.py discord
```

Uses discord.py 2.7.1 with slash commands, embeds, cogs, and event handlers. Set `DISCORD_BOT_TOKEN` in `.env`.

### Telegram

```bash
python piddy.py telegram
```

Uses python-telegram-bot 22.7 with command handlers, inline keyboards, and conversation flows. Set `TELEGRAM_BOT_TOKEN` in `.env`.

### Browser Automation

```bash
python piddy.py browse
```

Playwright 1.58.0 with embedded Chromium for web scraping, testing, and automation tasks.

### Productivity

```bash
python piddy.py productivity
```

Connectors for Google Calendar, Jira, and Notion. Configure API tokens in `.env`.

---

## Configuration

Copy `.env.example` to `.env` and fill in your tokens:

```env
# LLM Providers (4-tier failover: Local -> Ollama -> Anthropic -> OpenAI)
ANTHROPIC_API_KEY=your-key        # Claude models
OPENAI_API_KEY=your-key           # GPT-4o fallback

# Slack Integration
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_SIGNING_SECRET=your-secret
SLACK_APP_TOKEN=xapp-your-token

# Discord & Telegram
DISCORD_BOT_TOKEN=your-token
TELEGRAM_BOT_TOKEN=your-token

# Productivity Connectors
GOOGLE_CALENDAR_TOKEN=your-token
JIRA_API_TOKEN=your-token
NOTION_API_TOKEN=your-token

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8889
```

---

## Architecture

```
+------------------------------------------------------+
|  User Interface                                      |
|  +--------------+  +--------------+                  |
|  | Web Dashboard |  | Electron App |                 |
|  | (React 18.2)  |  | (stdio RPC)  |                |
|  +------+--------+  +------+-------+                 |
|         | HTTP :8889       | stdin/stdout             |
+---------|------------------+-------------------------+
|  Backend (FastAPI + RPC)                             |
|  +----------+  +-----------+  +------------------+   |
|  | Dashboard |  | RPC       |  | Integration      |  |
|  | API       |  | Endpoints |  | Slack/Discord/   |  |
|  | (REST)    |  | (39+6)    |  | Telegram/Browser |  |
|  +----------+  +-----------+  +------------------+   |
+------------------------------------------------------+
|  Agent System                                        |
|  +------------------------------------------------+  |
|  | 21 Agents - Reputation-Weighted Consensus      |  |
|  | 6-Stage Pipeline - Knowledge Graph (SQLite)    |  |
|  +------------------------------------------------+  |
+------------------------------------------------------+
|  LLM Providers (4-tier failover)                     |
|  Local Engine -> Ollama 0.18.2 -> Claude -> GPT-4o   |
+------------------------------------------------------+
|  Embedded Runtimes                                   |
|  Python 3.11.9 - Node.js 20.19.0 - Ollama 0.18.2    |
+------------------------------------------------------+
```

### Agent Roster (21 Agents)

| # | Agent | Domain |
|---|-------|--------|
| 1 | Guardian | Security analysis & threat detection |
| 2 | Validator | Code quality & testing |
| 3 | Analyzer | Code analysis & metrics |
| 4 | Executor | Task execution & automation |
| 5 | Coordinator | Multi-agent orchestration |
| 6 | Learner | Pattern learning & self-improvement |
| 7 | Performance Analyst | Benchmarking & optimization |
| 8 | Tech Debt Hunter | Refactoring & debt tracking |
| 9 | API Compatibility | Contract validation |
| 10 | Database Migration | Schema evolution |
| 11 | Architecture Reviewer | Design patterns & structure |
| 12 | Cost Optimizer | Resource & cost analysis |
| 13 | DevOps Engineer | CI/CD & infrastructure |
| 14 | Documentation Writer | Docs generation & maintenance |
| 15 | UX Reviewer | UI/UX analysis |
| 16 | Compliance Auditor | Regulatory compliance |
| 17 | Incident Responder | Incident triage & resolution |
| 18 | Data Scientist | ML & analytics |
| 19 | Release Manager | Versioning & release planning |
| 20 | Accessibility Expert | a11y compliance |
| 21 | Localization Specialist | i18n & l10n |

### Development Phases

Piddy has progressed through 51 development phases. Key milestones:

| Phases | Focus |
|--------|-------|
| 1-3 | Core agent, Slack integration, multi-language support, security |
| 5 | Dashboard (12 pages), reputation-weighted consensus voting |
| 6-9 | Service ecosystem, security hardening, AI operations |
| 10-17 | Multi-component orchestration, analytics, ML, cost optimization |
| 18-21 | AI developer autonomy, self-improvement, autonomous features |
| 22-26 | Task orchestration, RKG reasoning, refactoring, enterprise |
| 27-31 | PR workflow, persistent graph, sandbox, multi-agent protocol, compliance |
| 32-38 | API contracts, call graph, incremental rebuild, LLM-assisted planning |
| 39-50 | Impact visualization, simulation, multi-repo, continuous refactoring, consensus |
| 51 | Autonomous loop engine, failure memory, dynamic tool selection |

See [CAPABILITIES.md](CAPABILITIES.md) for detailed phase descriptions.

---

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Doctor Checks

```bash
python piddy.py doctor
```

Runs 17 health checks: Python version, Node.js, Ollama, disk space, database integrity, frontend build, skills system, agent status, and more.

### Adding Skills

Create a folder under `library/skills/<skill-name>/` with a `SKILL.md` frontmatter file:

```yaml
---
name: my-skill
category: framework
---
# My Skill
Reference content here...
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT

## Links

| Resource | URL |
|----------|-----|
| Repository | [github.com/burchdad/Piddy](https://github.com/burchdad/Piddy) |
| Capabilities | [CAPABILITIES.md](CAPABILITIES.md) |
| API Reference | [API.md](API.md) |
| Quick Start | [QUICKSTART.md](QUICKSTART.md) |
| Slack Setup | [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |
