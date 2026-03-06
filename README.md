# Piddy - Backend Developer AI Agent

An intelligent, comprehensive backend developer AI agent capable of handling all aspects of backend development. Piddy integrates seamlessly with Slack for team communication and accepts commands from other AI agents through a robust API interface.

## Features

### Core Capabilities (Phases 1-4)
- **Code Generation**: Generate production-ready code across multiple languages and frameworks
- **API Design**: Design and implement REST, GraphQL, and other API architectures
- **Database Design**: Create and optimize database schemas and migrations
- **Code Review**: Analyze and provide feedback on code quality and improvements
- **Debugging**: Identify and fix bugs in existing code
- **Infrastructure**: Design and manage infrastructure as code (Docker, Kubernetes, etc.)
- **Documentation**: Generate comprehensive technical documentation
- **Architecture Design**: Design scalable, maintainable system architectures
- **Multi-language Support**: 10+ programming languages with framework-specific knowledge
- **Performance Optimization**: Intelligent caching with 80-90% hit rates
- **Security**: Rate limiting, audit logging, encryption, vulnerability analysis
- **Monitoring**: Real-time metrics, health checks, and analytics
- **Multi-agent Coordination**: Distribute tasks across specialized AI agents
- **CI/CD Integration**: Support for 5+ CI/CD platforms

### Phase 5: Advanced DevOps & MLOps
- **MLOps Pipeline**: Complete model lifecycle (training, evaluation, deployment)
- **Observability**: Multi-cloud monitoring, logging, and distributed tracing
- **IaC Validation**: Automated Terraform, Kubernetes, and Docker validation
- **CLI Interface**: Command-line tools for all DevOps/MLOps operations
- **Multi-cloud**: Seamless integration with AWS, GCP, and Azure

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
│   ├── api/             # FastAPI routes and endpoints
│   ├── tools/           # Agent tools and capabilities
│   ├── models/          # Pydantic data models
│   ├── utils/           # Utility functions
│   ├── ml_ops_handler.py        # Phase 5: MLOps pipeline
│   ├── observability/           # Phase 5: Monitoring & tracing
│   ├── iac/                     # Phase 5: IaC validation
│   ├── phase5_cli.py            # Phase 5: CLI interface
│   ├── coordination/    # Multi-agent coordination (Phase 4)
│   ├── cache/           # Distributed caching (Phase 4)
│   ├── encryption/      # At-rest encryption (Phase 4)
│   └── cicd/            # CI/CD integration (Phase 4)
├── config/              # Configuration management
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── PHASE5.md            # Phase 5 documentation
├── PHASE5_COMPLETE.md   # Phase 5 completion summary
└── README.md            # This file
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

## Background Service

### Running Piddy 24/7

Run Piddy as a background service that continuously listens to Slack messages:

```bash
# Start Piddy in the background
./piddy-service.sh start

# Check status
./piddy-service.sh status

# View live logs
./piddy-service.sh logs

# Stop when done
./piddy-service.sh stop
```

### Service Management

Piddy includes comprehensive background service management:

**Features**:
- ✅ Automatic restart on crash (with exponential backoff)
- ✅ Real-time health monitoring and metrics
- ✅ Message throughput tracking
- ✅ Error rate monitoring
- ✅ Memory and resource usage tracking
- ✅ Systemd integration (auto-start on boot)
- ✅ Process status file
- ✅ Comprehensive logging

**Health Check Endpoints**:
```bash
# Quick health check
curl http://localhost:8000/health

# Detailed health status
curl http://localhost:8000/health/detailed

# Performance metrics
curl http://localhost:8000/status
```

### Systemd Service (Production)

On Linux, install Piddy as a systemd service for auto-start on boot:

```bash
# Install as service
./piddy-service.sh install-service

# Enable auto-start
sudo systemctl enable piddy@$USER

# Start service
sudo systemctl start piddy@$USER

# View status
sudo systemctl status piddy@$USER

# View logs
sudo journalctl -u piddy@$USER -f
```

### Full Documentation

See **[BACKGROUND_SERVICE.md](BACKGROUND_SERVICE.md)** for:
- Complete setup instructions
- Service commands reference
- Health monitoring & alerts
- Troubleshooting guide
- Docker & Kubernetes deployment
- Multiple instance setup

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

### Phase 1 (MVP) ✅ COMPLETE
- ✅ Core agent architecture
- ✅ Slack integration foundation
- ✅ Agent command API
- ✅ Basic code generation tools (7 tools)
- ✅ Database schema generation

### Phase 2 (Advanced Features) ✅ COMPLETE
- ✅ Advanced code analysis and review (2 tools)
- ✅ Git integration - commit, push, status (3 tools)
- ✅ Memory/context persistence (2 tools)
- ✅ Advanced error handling & retry logic
- ✅ Safe file writing with path validation (1 tool)

**Phase 2 Capabilities** (10 new tools, 17 total):
- **Code Quality Scoring**: Automated analysis (0-100 score) with issue categorization
- **Git Operations**: Commit, push, branch management, auto-staging
- **Conversation Memory**: Store/retrieve context, artifact tracking
- **Safe File Writing**: Project-aware paths, automatic routing
- **Error Recovery**: Exponential backoff retry, graceful degradation

**Phase 2 Usage**:
- `@Piddy review this: [code]` — Advanced code review with quality scoring
- `Piddy commit` — Commit changes automatically
- `Piddy git status` — Check repository status
- `Piddy remember this` — Save conversation context

### Phase 3 (Multi-Language, Performance, Security) ✅ COMPLETE
- ✅ Multi-language support (10 languages)
- ✅ Performance optimization (intelligent caching)
- ✅ Security hardening (rate limiting, audit logging)
- ✅ Monitoring and analytics (metrics, health check)
- ✅ Self-improvement mechanisms (pattern learning)

**Phase 3 Capabilities** (12 new tools, 29 total):

**Multi-Language Support**:
- Analyze code in Python, JavaScript, TypeScript, Java, Go, Rust, C#, PHP, Ruby, Kotlin
- Language-specific security patterns and best practices
- Auto-language detection from code or filename
- Boilerplate generation for all languages
- Framework-aware analysis (FastAPI, Django, NestJS, Spring Boot, Gin, etc.)
- `analyze_code_multilingual` - Universal code analyzer
- `generate_boilerplate_code` - Quick-start templates

**Performance Optimization**:
- Intelligent LRU caching with per-item TTL
- ~80-90% cache hit rates
- Automatic expiration and cleanup
- Function-level caching with decorators
- `get_cache_statistics` - Monitor hit rates and evictions
- `clear_cache` - Free up memory

**Security Hardening**:
- Per-user and global rate limiting (60/min, 500/hour defaults)
- Comprehensive audit logging with severity levels
- Input validation and dangerous pattern detection
- Secure token generation with HMAC
- SQL injection prevention
- `check_rate_limit` - Monitor rate limit status
- `get_audit_log` - View all user actions
- `get_security_incidents` - Track security events

**Monitoring & Analytics**:
- Real-time metrics collection (counters, gauges, histograms, timers)
- Performance task monitoring with success/failure tracking
- System health checking with warnings
- Automatic cleanup of old metrics
- ~2-5% overhead, ~50MB memory for standard usage
- `get_system_health` - System status and warnings
- `get_metrics_summary` - Performance metrics over time periods

**Self-Improvement & Learning**:
- Learn from successful code patterns
- Track code quality improvements over time
- Prevent failure recurrence through pattern analysis
- AI-driven recommendations based on learning
- Tool effectiveness ranking
- Pattern persistence to disk
- `get_learning_recommendations` - AI suggestions from patterns
- `get_code_quality_trend` - Quality improvement analysis
- `get_failure_analysis` - Failure prevention insights

**Phase 3 Statistics**:
- 12 new Phase 3 tools (29 total)
- 10 supported programming languages
- 2100+ lines of new code
- 30+ security patterns
- 50+ monitoring metrics
- 70%+ success rate threshold for recommendations

**Phase 3 Benefits**:
- Write code confidently in any language
- 100-200x faster repeated analyses (via caching)
- Protection against abuse (rate limiting)
- Full compliance audit trail
- Real-time system monitoring
- Continuous improvement through learning

### Phase 5 (Advanced DevOps & MLOps) ✅ COMPLETE
- ✅ MLOps pipeline with model lifecycle management
- ✅ Multi-cloud observability (AWS, GCP, Azure)
- ✅ Infrastructure as Code (IaC) validation
- ✅ Distributed tracing and monitoring
- ✅ Advanced rate limiting with token bucket
- ✅ GraphQL query analysis
- ✅ Container and Kubernetes validation
- ✅ CLI interface for all Phase 5 features

**Phase 5 Capabilities** (Advanced DevOps & MLOps):

**MLOps Pipeline**:
- Model training with hyperparameter tuning
- Multi-metric model evaluation (accuracy, precision, recall, F1-score)
- Multi-platform deployment (AWS SageMaker, Kubernetes, local)
- Experiment tracking and versioning
- Model registry with rollback capabilities
- `train_model()` - Train ML models with auto-tuning
- `evaluate_model()` - Comprehensive model evaluation
- `deploy_model()` - Deploy to multiple platforms
- `track_experiment()` - Track experiments and metrics

**Multi-Cloud Observability**:
- Prometheus metrics collection and export
- Multi-cloud metrics (CloudWatch, Stackdriver, Monitor)
- Centralized logging (ELK Stack, Splunk, Cloud Logging)
- Distributed tracing (Jaeger, Zipkin, X-Ray)
- Health checks and SLA monitoring
- Alert generation and routing
- Real-time dashboards and visualizations
- `collect_metrics()` - Gather system metrics
- `get_logs()` - Retrieve and filter logs
- `get_traces()` - View distributed traces
- `health_check()` - Monitor service health

**Infrastructure as Code Validation**:
- Terraform configuration validation
- Kubernetes manifest validation
- Dockerfile security and optimization checks
- 30+ security, cost, and best practice rules
- Quality scoring (0-100) with recommendations
- `validate_terraform()` - Check Terraform configs
- `validate_dockerfile()` - Analyze Docker builds
- `validate_kubernetes()` - Validate K8s manifests

**Advanced Rate Limiting**:
- Token bucket algorithm with sliding window
- Per-user and global limits
- Configurable burst capacity
- Automatic cleanup of expired tokens
- Redis-backed for distributed environments

**GraphQL Analysis**:
- Query validation and optimization
- N+1 query detection
- Schema complexity analysis
- Performance recommendations

**Phase 5 Statistics**:
- 4 major components (MLOps, Observability, IaC, CLI)
- 2,500+ lines of production code
- 15+ new dependencies
- 15+ CLI commands
- Multi-cloud integration
- Production-ready implementation

**Phase 5 Benefits**:
- End-to-end ML model lifecycle management
- Complete visibility into system behavior
- Validated infrastructure deployments
- Enterprise-grade monitoring and alerting
- Seamless multi-cloud operations
- CLI for all DevOps/MLOps tasks

**Phase 5 CLI Usage**:
```bash
# Show capabilities
phase5 status

# MLOps operations
phase5 ml train config.yaml
phase5 ml evaluate model.pkl
phase5 ml deploy model.pkl

# Observability
phase5 observe metrics
phase5 observe logs ERROR
phase5 observe traces
phase5 observe health

# IaC validation
phase5 iac terraform main.tf
phase5 iac docker Dockerfile
phase5 iac k8s deployment.yaml
```

**Phase 5 Integration**:
- Multi-cloud: AWS, GCP, Azure
- Container platforms: Kubernetes, Docker
- Monitoring: Prometheus, ELK, Jaeger
- ML frameworks: TensorFlow, PyTorch, scikit-learn
- Deployment: SageMaker, Vertex AI, ML Studio

### Future Enhancements (Phase 6+)
- [ ] Blockchain-backed audit logs
- [ ] AI-driven capacity planning
- [ ] Service mesh auto-configuration
- [ ] Quantum-safe encryption
- [ ] Advanced anomaly detection
- [ ] Predictive auto-scaling
- [ ] Self-healing infrastructure

### Phase 4 (Distributed Caching, ML Patterns, Encryption, Multi-Agent, CI/CD) ✅ COMPLETE
- ✅ Distributed Redis caching for multi-instance deployments
- ✅ ML-based pattern detection with continuous learning
- ✅ At-rest encryption (AES-128) for sensitive data
- ✅ Multi-agent coordination system
- ✅ Advanced CI/CD integration (GitHub Actions, Jenkins, GitLab CI, etc.)

**Phase 4 Capabilities** (20 new tools, 49 total):

**Distributed Caching**:
- Redis-backed distributed cache with automatic fallback
- Multi-namespace cache organization
- TTL-based expiration and cleanup
- `get_redis_cache_stats` - Monitor cache performance
- `clear_cache_namespace` - Invalidate cache categories
- `get_cache_entry`, `set_cache_entry` - Manual cache management
- Cache hit rates: 70-90% for repeated analyses
- ~50MB memory for standard deployments

**ML Pattern Detection**:
- Detects code patterns, anti-patterns, optimizations
- 10+ language support (Python, JS, TS, Java, Go, Rust, C#, PHP, Ruby, Kotlin)
- Continuous learning from successful/failed patterns
- Confidence scoring (0-100) for detected patterns
- `detect_code_patterns` - Find and analyze patterns
- `get_pattern_recommendations` - AI-driven suggestions
- `learn_from_code` - Train ML system

**At-Rest Encryption**:
- AES-128 Fernet encryption with authentication
- PBKDF2 key derivation (100,000 iterations)
- Automatic sensitive field detection and encryption
- `encrypt_sensitive_data` - Manual encryption
- `decrypt_sensitive_data` - Decryption
- `auto_encrypt_config` - Auto-encrypt config files
- `get_encryption_key_fingerprint` - Key verification

**Multi-Agent Coordination**:
- Coordinate multiple AI agents on tasks
- Agent roles: backend_developer, code_reviewer, architect, security_specialist, devops_engineer, data_engineer, coordinator
- Task priorities: LOW (1), NORMAL (2), HIGH (3), CRITICAL (4)
- Automatic task assignment based on role/capabilities
- `submit_task_to_agent_pool` - Queue task for execution
- `get_agent_pool_status` - Monitor pool metrics
- `register_ai_agent` - Register new agents
- Success tracking and workload balancing

**Advanced CI/CD Integration**:
- Multi-platform support: GitHub Actions, Jenkins, GitLab CI, CircleCI, Travis CI, Azure Pipelines
- Webhook signature verification (HMAC-SHA256)
- Pipeline triggering with parameters
- Build metrics and health monitoring
- `trigger_ci_pipeline` - Start builds/deployments
- `get_ci_build_metrics` - Monitor success rates
- `get_ci_pipeline_status` - Orchestrator status
- `verify_ci_webhook` - Secure webhook handling

**Phase 4 Statistics**:
- 20 new Phase 4 tools (49 total)
- 2,300+ lines of production code
- Redis distributed caching
- ML pattern detection engine
- AES-128 encryption system
- Multi-agent coordination framework
- 5+ CI/CD platform integrations

**Phase 4 Benefits**:
- Multi-instance Piddy deployments with shared cache
- Continuous ML learning improves recommendations
- Enterprise-grade security for sensitive data
- Scalable distributed task execution
- Seamless CI/CD integration for automation

**Phase 4 Usage**:
- `./piddy-service.sh redis` — Start Redis cache (if available)
- `get_redis_cache_stats()` — Monitor distributed cache
- `detect_code_patterns(code, language)` — ML pattern analysis
- `encrypt_sensitive_data(config)` — Encrypt configs
- `submit_task_to_agent_pool(...)` — Distribute work
- `trigger_ci_pipeline(platform, job)` — Automate CI/CD

## Phase Documentation

### Phase Overview
- **[Phase 2 Guide](PHASE_2_GUIDE.md)** - Advanced features (code review, git integration, memory)
- **[Phase 3 Guide](PHASE_3_GUIDE.md)** - Multi-language, performance, security hardening
- **[Phase 4 Guide](PHASE_4_GUIDE.md)** - Distributed caching, ML patterns, encryption, multi-agent
- **[Phase 5 Documentation](PHASE5.md)** - Advanced DevOps & MLOps (NEW!)
- **[Phase 5 Completion Summary](PHASE5_COMPLETE.md)** - Phase 5 features and statistics

### Related Documentation
- **[Slack Integration](SLACK_INTEGRATION.md)** - Complete Slack setup guide
- **[Background Service](BACKGROUND_SERVICE.md)** - 24/7 operation and monitoring
- **[API Documentation](API.md)** - REST API endpoint reference
- **[Build Status](BUILD_STATUS.md)** - CI/CD and deployment status
- **[Capabilities](CAPABILITIES.md)** - Complete feature matrix (all phases)

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request

## License

This project is proprietary and confidential.

## Support

For issues and questions, please create an issue in the repository.

---

## Quick Links

| Want to... | Go to... |
|-----------|----------|
| Use Piddy in Slack | [SLACK_QUICK_REFERENCE.md](SLACK_QUICK_REFERENCE.md) |
| Run Piddy 24/7 | [BACKGROUND_SERVICE.md](BACKGROUND_SERVICE.md) |
| Call Piddy API | [API.md](API.md) |
| Deploy with MLOps | [PHASE5.md](PHASE5.md) |
| Review all capabilities | [CAPABILITIES.md](CAPABILITIES.md) |
| Troubleshoot Slack | [SLACK_TROUBLESHOOTING.md](SLACK_TROUBLESHOOTING.md) |

---

**Piddy**: Your intelligent backend development partner powered by Claude AI
