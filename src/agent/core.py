"""Core Piddy backend developer agent."""

import logging
import time
import asyncio
from typing import Any, Dict, List, Optional, Union
from langchain.agents import AgentExecutor, create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.base_language import BaseLanguageModel

from config.settings import get_settings
from src.models.command import Command, CommandResponse, CommandType
from src.tools import get_all_tools
from src.agent.conversational_prompt import CONVERSATIONAL_SYSTEM_PROMPT
from src.services.rate_limiter import get_rate_limiter, Provider
from src.skills.loader import get_skill_registry


logger = logging.getLogger(__name__)

# Rate limit tracking
_llm_rate_limits = {
    "claude": {"last_error": None, "error_count": 0, "backoff_until": 0},
    "gpt-4o": {"last_error": None, "error_count": 0, "backoff_until": 0},
}


def _is_rate_limited(llm_name: str) -> bool:
    """
    Check if an LLM is currently in backoff period.
    Uses both legacy local tracking and new global rate limiter.
    """
    # Check global rate limiter
    limiter = get_rate_limiter()
    provider = Provider.ANTHROPIC if llm_name == "claude" else Provider.OPENAI
    
    if not limiter.can_make_request(provider):
        logger.warning(f"{llm_name} is rate limited (global limiter)")
        return True
    
    # Fall back to legacy tracking
    if llm_name not in _llm_rate_limits:
        return False
    
    limit_info = _llm_rate_limits[llm_name]
    if limit_info["backoff_until"] > time.time():
        logger.warning(f"{llm_name} is in backoff until {limit_info['backoff_until']}")
        return True
    return False


def _record_rate_limit_error(llm_name: str, error_msg: str = ""):
    """
    Record a rate limit error for an LLM.
    Reports to both legacy tracking and new global rate limiter.
    """
    # Update global rate limiter
    limiter = get_rate_limiter()
    provider = Provider.ANTHROPIC if llm_name == "claude" else Provider.OPENAI
    limiter.record_rate_limit_error(provider, error_msg)
    
    # Keep legacy tracking for backward compatibility
    if llm_name not in _llm_rate_limits:
        _llm_rate_limits[llm_name] = {"last_error": None, "error_count": 0, "backoff_until": 0}
    
    limit_info = _llm_rate_limits[llm_name]
    limit_info["error_count"] += 1
    limit_info["last_error"] = error_msg
    
    # Exponential backoff: 30s, 60s, 120s, etc.
    backoff_seconds = min(30 * (2 ** (limit_info["error_count"] - 1)), 600)  # Max 10 minutes
    limit_info["backoff_until"] = time.time() + backoff_seconds
    
    logger.warning(
        f"{llm_name} hit rate limit. Backing off for {backoff_seconds}s. "
        f"Error count: {limit_info['error_count']}"
    )


def _clear_rate_limit(llm_name: str):
    """
    Clear rate limit tracking for an LLM.
    Clears both legacy and new global tracking.
    """
    # Clear global rate limiter
    limiter = get_rate_limiter()
    provider = Provider.ANTHROPIC if llm_name == "claude" else Provider.OPENAI
    limiter.reset_metrics(provider)
    
    # Clear legacy tracking
    if llm_name in _llm_rate_limits:
        _llm_rate_limits[llm_name] = {"last_error": None, "error_count": 0, "backoff_until": 0}


class BackendDeveloperAgent:
    """
    Piddy: AI Backend Developer Agent
    Capable of handling comprehensive backend development tasks.
    """
    
    def __init__(self):
        """Initialize the backend developer agent.
        
        Failover priority (free first, paid last):
          1. Local Engine  — pattern-based + KB, always works, zero cost
          2. Ollama         — local LLM, free, requires ollama serve
          3. Anthropic      — Claude, paid cloud API
          4. OpenAI         — GPT, paid cloud API (last resort)
        """
        self.settings = get_settings()
        self.local_engine = self._create_local_engine()
        self.local_llm = self._create_local_llm()       # Ollama (free)
        self.anthropic_llm = self._create_anthropic_llm() # Claude (paid)
        self.openai_llm = self._create_openai_llm()       # GPT (paid)
        
        # Legacy aliases for backward compatibility
        self.primary_llm = self.anthropic_llm
        self.fallback_llm = self.openai_llm
        
        # Set active LLM: prefer local, then cloud
        self.llm = self.local_llm or self.anthropic_llm or self.openai_llm
        self.tools = self._initialize_tools()
        self.executor = self._create_executor() if self.llm else None
        self.conversation_executor = self._create_conversation_executor() if self.llm else None
        
        if self.local_llm:
            mode = "local-llm"
        elif self.anthropic_llm:
            mode = "cloud-anthropic"
        elif self.openai_llm:
            mode = "cloud-openai"
        else:
            mode = "offline"
        logger.info(f"BackendDeveloperAgent initialized — mode={mode}, primary={self.settings.agent_model}")
    
    def _create_anthropic_llm(self) -> Optional[BaseLanguageModel]:
        """Create Anthropic Claude LLM (Tier 3 — paid cloud)."""
        if not self.settings.anthropic_api_key:
            logger.info("Anthropic API key not configured — skipping")
            return None
        try:
            return ChatAnthropic(
                model=self.settings.agent_model,
                temperature=self.settings.agent_temperature,
                max_tokens=self.settings.agent_max_tokens,
                api_key=self.settings.anthropic_api_key,
            )
        except Exception as e:
            logger.warning(f"Anthropic LLM init failed: {e}")
            return None
    
    # Legacy aliases
    _create_primary_llm = _create_anthropic_llm
    
    def _create_openai_llm(self) -> Optional[BaseLanguageModel]:
        """Create OpenAI GPT LLM (Tier 4 — paid cloud, last resort)."""
        if not self.settings.openai_api_key:
            logger.info("OpenAI API key not configured — skipping")
            return None
        try:
            return ChatOpenAI(
                model=self.settings.openai_model,
                temperature=self.settings.agent_temperature,
                max_tokens=self.settings.agent_max_tokens,
                api_key=self.settings.openai_api_key,
            )
        except Exception as e:
            logger.warning(f"OpenAI LLM init failed: {e}")
            return None
    
    # Legacy alias
    _create_fallback_llm = _create_openai_llm
    
    def _create_local_llm(self) -> Optional[BaseLanguageModel]:
        """Create local Ollama LLM for offline operation."""
        if not self.settings.ollama_enabled:
            return None
        try:
            from langchain_community.llms import Ollama
            llm = Ollama(
                base_url=self.settings.ollama_base_url,
                model=self.settings.ollama_model,
                temperature=self.settings.agent_temperature,
            )
            # Quick connectivity check — don't fail init if Ollama isn't running yet
            logger.info(f"🏠 Ollama configured: {self.settings.ollama_model} @ {self.settings.ollama_base_url}")
            return llm
        except ImportError:
            logger.info("Ollama integration not available (langchain-community)")
            return None
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return None
    
    def _create_local_engine(self):
        """Create pure offline code engine (no LLM required)."""
        try:
            from src.agent.local_engine import LocalCodeEngine
            engine = LocalCodeEngine()
            logger.info("🔧 Local code engine ready (pattern-based, KB-augmented)")
            return engine
        except Exception as e:
            logger.warning(f"Local engine unavailable: {e}")
            return None
    
    def _switch_to_fallback(self) -> bool:
        """Switch to fallback LLM if available."""
        if self.fallback_llm and self.llm != self.fallback_llm:
            logger.warning(f"Switching from {self.settings.agent_model} to {self.settings.openai_model}")
            self.llm = self.fallback_llm
            self.executor = self._create_executor()
            self.conversation_executor = self._create_conversation_executor()
            return True
        return False
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize all available tools for the agent."""
        return get_all_tools()
    
    def _create_conversation_executor(self) -> AgentExecutor:
        """Create the agent executor for conversational mode."""
        # Create a simple ReAct prompt with string placeholders
        prompt_template = """Answer the following question as helpfully as possible. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
{agent_scratchpad}"""
        
        prompt = PromptTemplate.from_template(prompt_template)
        agent = create_react_agent(self.llm, self.tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.settings.debug,
            handle_parsing_errors=True,
            max_iterations=25,  # Increased for complex multi-step tasks
        )
        return executor
    
    def _create_executor(self) -> AgentExecutor:
        """Create the agent executor."""
        system_prompt = """You are Piddy, an expert backend developer AI agent. 

You are a comprehensive backend development specialist with expertise across:
- Code generation for multiple languages (Python, JavaScript, TypeScript, Java, Go, Rust, C#, PHP, Ruby, Kotlin)
- Backend frameworks (FastAPI, Django, Flask, Express, NestJS, Spring Boot, Gin, Actix, and more)
- API design and implementation (REST, GraphQL, gRPC)
- Database design, optimization, and migrations
- Infrastructure and DevOps (Docker, Kubernetes, CI/CD)
- Code review and quality analysis
- Security analysis and best practices
- Design patterns and architecture
- Performance optimization
- Testing and debugging

## Your Capabilities

You have access to tools for:
1. **Code Generation**: Create production-ready code across frameworks and languages
2. **Code Analysis**: Review code for quality, security, and performance issues
3. **Advanced Code Review**: Comprehensive multi-dimensional analysis with violation detection
4. **Design Patterns**: Generate templates and implementations of design patterns
5. **Architecture Design**: Create blueprints for system architectures
6. **Database Tools**: Generate models, migrations, and indexing strategies
7. **Security Analysis**: Comprehensive security vulnerability detection
8. **Git Integration**: Commit, push, and manage version control
9. **Memory & Context**: Store conversation history and artifacts
10. **File Management**: Write generated code to appropriate project locations

## Phase 2: Advanced Features

Enhanced core capabilities:
- **Code Quality Scoring**: Automated scoring (0-100) with specific issue categorization
- **Version Control**: Automatically commit and push generated code
- **Conversation Memory**: Store and retrieve context from interactions
- **Safe File Writing**: Intelligent path resolution
- **Error Recovery**: Graceful degradation with automatic retry

## Phase 3: Multi-Language Support & Optimization (NEW!)

### Multi-Language Analysis
- **Universal Code Analyzer**: Analyze code in 10+ programming languages
- Language-Specific Rules: Security patterns, performance patterns, best practices per language
- Auto-Detection: Intelligently detect language from code or filename
- Boilerplate Generation: Quick-start code for any supported language and project type

Supported Languages: Python, JavaScript, TypeScript, Java, Go, Rust, C#, PHP, Ruby, Kotlin

### Performance Optimization
- **Intelligent Caching**: LRU cache for analysis results with TTL control
- **Cache Statistics**: Monitor hit rates, evictions, memory usage
- **Result Reuse**: Automatic caching of analysis findings
- **Memory Management**: Efficient resource utilization

### Security Hardening
- **Rate Limiting**: Per-user and global request throttling (60/min, 500/hour defaults)
- **Audit Logging**: Comprehensive event tracking for compliance
- **Security Policies**: Input validation, dangerous pattern detection
- **Incident Tracking**: Recent security incidents and patterns

### Monitoring & Analytics
- **System Health**: Real-time health status with warnings
- **Performance Metrics**: Track tool execution times and success rates
- **Error Tracking**: Monitor and analyze error patterns
- **Metrics Dashboard**: View performance summaries

### Self-Improvement & Learning
- **Pattern Learning**: Learn from successful code generation patterns
- **Quality Trends**: Track code quality improvements over time
- **Failure Analysis**: Analyze failures to prevent recurrence
- **Recommendations**: AI-driven suggestions based on learned patterns
- **Evolution Tracking**: Monitor how code quality evolves

## Guidelines

When given a development task:
1. **Clarify Requirements**: Ask questions if requirements are ambiguous
2. **Suggest Best Practices**: Recommend architecture and design patterns
3. **Provide Production-Ready Code**: Always include error handling, validation, logging
4. **Security First**: Always consider security implications
5. **Performance Conscious**: Think about scalability and optimization
6. **Well-Documented**: Include comments and docstrings
7. **Testing**: Suggest and help with test strategies
8. **Multi-Language Support**: Offer solutions in multiple languages when relevant
9. **Learn & Improve**: Leverage learned patterns for better recommendations

## Response Format

When generating code or solutions:
- Provide complete, working implementations
- Include necessary imports and dependencies
- Add error handling and validation
- Document complex logic
- Suggest testing approaches
- Point out security considerations
- Mention language-specific best practices
- Recommend next steps or improvements

## Supported Technologies

### Languages (Phase 3 Support)
- Python (3.11+)
- JavaScript/TypeScript (ES2020+)
- Go (1.20+)
- Java (17+)
- Rust (1.70+)
- C# (.NET 6+)
- Ruby (3.0+)
- PHP (8.1+)
- Kotlin (1.8+)
- Java (17+)

### Frameworks
- Python: FastAPI, Django, Flask, Starlette
- JavaScript: Express, Fastify, Koa
- TypeScript: NestJS, Fastify, Koa
- Go: Gin, Echo, Fiber
- Java: Spring Boot, Quarkus, Micronaut
- Rust: Actix, Tokio, Axum
- C#: ASP.NET Core, ServiceStack
- Ruby: Rails, Sinatra, Hanami
- PHP: Laravel, Symfony, Slim
- Kotlin: Spring Boot, Ktor

### Databases
- PostgreSQL, MySQL, MongoDB, Redis
- DynamoDB, Elasticsearch, Cassandra
- Firestore, BigQuery, Snowflake

### Performance Features
- Intelligent result caching with hit rate monitoring
- Multi-language pattern analysis
- Async operation support where available
- Resource pooling and cleanup

Always prioritize code quality, security, maintainability, performance, and user experience."""
        
        # Create a simple ReAct prompt with string placeholders
        prompt_template = """You are Piddy, an expert backend developer AI agent.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
{agent_scratchpad}"""
        
        prompt = PromptTemplate.from_template(prompt_template)
        agent = create_react_agent(self.llm, self.tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.settings.debug,
            handle_parsing_errors=True,
            max_iterations=25,  # Increased for complex multi-step tasks
        )
        return executor
    
    async def process_command(self, command: Command) -> CommandResponse:
        """
        Process a backend development command.
        
        Four-tier failover chain (free first, paid last):
          1. Local Engine  — pattern + KB based, always works, zero cost
          2. Ollama        — local LLM, free, runs on your machine
          3. Anthropic     — Claude cloud API, paid
          4. OpenAI        — GPT cloud API, paid (last resort)
        
        Args:
            command: Command to execute
            
        Returns:
            CommandResponse with results
        """
        logger.info(f"🤖 Processing command: {command.command_type.value} - {command.description[:50]}...")
        
        is_conversation = command.metadata.get("is_conversation", False)
        prompt = self._format_command_prompt(command)
        
        # ── TIER 1: Local Engine (free, instant, always works) ─────────
        local_result = await self._try_local_engine(command)
        if local_result:
            return local_result
        
        # ── TIER 2: Ollama (free, local LLM) ──────────────────────────
        ollama_result = await self._try_local_llm(command, prompt, is_conversation)
        if ollama_result:
            return ollama_result
        
        # ── LOCAL-ONLY MODE: stop here if configured ──────────────
        if self.settings.local_only:
            logger.info("Local-only mode enabled — skipping cloud APIs")
            return CommandResponse(
                success=False,
                command_type=command.command_type,
                result=None,
                error="Local-only mode: Ollama is not responding. "
                      "Ensure Ollama is running (runtime/ollama/ollama.exe serve) "
                      "or disable local_only mode to allow cloud API fallback.",
                metadata={"source": command.source, "tiers_attempted": ["local", "ollama"], "local_only": True}
            )
        
        # ── TIER 3: Anthropic Claude (paid cloud) ─────────────────────
        anthropic_result = await self._try_anthropic(command, prompt, is_conversation)
        if anthropic_result:
            return anthropic_result
        
        # ── TIER 4: OpenAI GPT (paid cloud, last resort) ─────────────
        openai_result = await self._try_openai(command, prompt, is_conversation)
        if openai_result:
            return openai_result
        
        # All tiers exhausted
        logger.error("All processing tiers exhausted (local, ollama, anthropic, openai)")
        return CommandResponse(
            success=False,
            command_type=command.command_type,
            result=None,
            error="All processing tiers exhausted. Install Ollama (free) from ollama.com "
                  "or configure API keys in Settings for cloud providers.",
            metadata={"source": command.source, "tiers_attempted": ["local", "ollama", "anthropic", "openai"]}
        )
    
    async def _try_cloud_llm(self, command, prompt, is_conversation, llm, llm_name, tier_label) -> Optional[CommandResponse]:
        """Try a single cloud LLM provider."""
        if llm is None:
            return None
        
        if _is_rate_limited(llm_name):
            logger.warning(f"Skipping {llm_name}: rate limited")
            return None
        
        try:
            logger.info(f"☁️  {tier_label} — {llm_name}")
            
            if llm != self.llm:
                self.llm = llm
                self.executor = self._create_executor()
                self.conversation_executor = self._create_conversation_executor()
            
            executor = self.conversation_executor if is_conversation else self.executor
            result = executor.invoke({"input": prompt})
            _clear_rate_limit(llm_name)
            
            # Record success in global rate limiter for metrics tracking
            limiter = get_rate_limiter()
            provider = Provider.ANTHROPIC if llm_name == "claude" else Provider.OPENAI
            limiter.record_success(provider)
            
            return CommandResponse(
                success=True,
                command_type=command.command_type,
                result=result.get("output", ""),
                execution_time=0.0,
                metadata={
                    "source": command.source,
                    "is_conversation": is_conversation,
                    "engine": "cloud",
                    "llm_used": llm_name,
                }
            )
        
        except Exception as llm_e:
            error_str = str(llm_e).lower()
            logger.warning(f"{llm_name} failed: {str(llm_e)[:150]}")
            
            rate_limit_phrases = [
                "rate_limit", "429", "rate limit", "quota exceeded",
                "too many requests", "ratelimit"
            ]
            if any(p in error_str for p in rate_limit_phrases):
                _record_rate_limit_error(llm_name, str(llm_e))
            
            return None
    
    async def _try_anthropic(self, command, prompt, is_conversation) -> Optional[CommandResponse]:
        """Tier 3: Anthropic Claude (paid cloud)."""
        return await self._try_cloud_llm(
            command, prompt, is_conversation,
            self.anthropic_llm, "claude", "Tier 3"
        )
    
    async def _try_openai(self, command, prompt, is_conversation) -> Optional[CommandResponse]:
        """Tier 4: OpenAI GPT (paid cloud, last resort)."""
        return await self._try_cloud_llm(
            command, prompt, is_conversation,
            self.openai_llm, "gpt-4o", "Tier 4"
        )
    
    # Legacy alias for backward compatibility
    async def _try_cloud_llms(self, command, prompt, is_conversation) -> Optional[CommandResponse]:
        result = await self._try_anthropic(command, prompt, is_conversation)
        if result:
            return result
        return await self._try_openai(command, prompt, is_conversation)
    
    async def _try_local_llm(self, command, prompt, is_conversation) -> Optional[CommandResponse]:
        """Tier 2: Local LLM via Ollama (free, runs locally)."""
        if not self.local_llm:
            return None
        
        try:
            logger.info(f"🏠 Tier 2 — Local LLM: {self.settings.ollama_model}")
            
            from src.agent.action_parser import AGENTIC_PROMPT_ADDON
            from src.agent.build_learnings import build_lessons_prompt
            
            # Build a full prompt with system identity + agentic capabilities
            system_intro = (
                "You are Piddy, an expert AI developer assistant. "
                "You don't just explain code — you BUILD things. "
                "When asked to create or build something, you produce actual files.\n\n"
            )
            lessons = build_lessons_prompt()
            full_prompt = system_intro + AGENTIC_PROMPT_ADDON + lessons + "\n\n" + prompt
            
            response = self.local_llm.invoke(full_prompt)
            
            # Ollama returns a string directly
            result_text = response if isinstance(response, str) else str(response)
            
            return CommandResponse(
                success=True,
                command_type=command.command_type,
                result=result_text,
                execution_time=0.0,
                metadata={
                    "source": command.source,
                    "is_conversation": is_conversation,
                    "engine": "ollama",
                    "llm_used": self.settings.ollama_model,
                    "offline": True,
                }
            )
        except Exception as e:
            logger.warning(f"Ollama unavailable: {str(e)[:150]}")
            return None
    
    async def _try_local_engine(self, command) -> Optional[CommandResponse]:
        """Tier 1: Pure local engine — pattern-based + KB, no LLM needed (free, instant)."""
        if not self.local_engine:
            return None
        
        try:
            logger.info(f"🔧 Tier 1 — Local engine (patterns + KB)")
            result = await self.local_engine.process(command)
            if result:
                logger.info("✅ Local engine handled command successfully")
            return result
        except Exception as e:
            logger.error(f"Local engine error: {e}")
            return None
    
    def _format_command_prompt(self, command: Command) -> str:
        """Format a command into a natural language prompt with skill injection."""
        prompt = f"Task: {command.description}\n\n"
        
        # Inject matching skill context into the prompt
        try:
            registry = get_skill_registry()
            skill_context = registry.get_context_for_query(command.description)
            if skill_context:
                prompt += f"## Relevant Knowledge\n{skill_context}\n\n"
                logger.debug(f"Injected skill context for: {command.description[:50]}")
        except Exception as e:
            logger.debug(f"Skill injection skipped: {e}")
        
        if command.context:
            prompt += "Context:\n"
            for key, value in command.context.items():
                prompt += f"- {key}: {value}\n"
        
        if command.metadata:
            prompt += "\nAdditional Requirements:\n"
            for key, value in command.metadata.items():
                prompt += f"- {key}: {value}\n"
        
        return prompt
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health status including all tiers."""
        claude_info = _llm_rate_limits.get("claude", {})
        gpt_info = _llm_rate_limits.get("gpt-4o", {})
        
        claude_limited = _is_rate_limited("claude")
        gpt_limited = _is_rate_limited("gpt-4o")
        
        # Determine overall mode
        if not (claude_limited and gpt_limited):
            mode = "online"
        elif self.local_llm:
            mode = "local-llm"
        elif self.local_engine:
            mode = "offline"
        else:
            mode = "degraded"
        
        return {
            "status": "healthy" if mode != "degraded" else "degraded",
            "mode": mode,
            "model": self.settings.agent_model,
            "tools_available": len(self.tools),
            "tiers": {
                "cloud": {
                    "claude": {
                        "configured": bool(self.primary_llm),
                        "rate_limited": claude_limited,
                        "error_count": claude_info.get("error_count", 0),
                        "last_error": claude_info.get("last_error", ""),
                    },
                    "gpt-4o": {
                        "configured": bool(self.fallback_llm),
                        "rate_limited": gpt_limited,
                        "error_count": gpt_info.get("error_count", 0),
                        "last_error": gpt_info.get("last_error", ""),
                    }
                },
                "local_llm": {
                    "configured": bool(self.local_llm),
                    "model": self.settings.ollama_model if self.local_llm else None,
                    "url": self.settings.ollama_base_url if self.local_llm else None,
                },
                "local_engine": {
                    "available": bool(self.local_engine),
                    "capabilities": ["code_review", "code_generation", "debugging",
                                     "security_audit", "performance", "architecture"]
                                    if self.local_engine else [],
                }
            },
            "fallback_available": bool(self.fallback_llm),
            "offline_capable": bool(self.local_llm or self.local_engine),
        }
