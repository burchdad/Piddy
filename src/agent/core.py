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
        """Initialize the backend developer agent."""
        self.settings = get_settings()
        self.primary_llm = self._create_primary_llm()
        self.fallback_llm = self._create_fallback_llm()
        self.llm = self.primary_llm  # Start with primary
        self.tools = self._initialize_tools()
        self.executor = self._create_executor()
        self.conversation_executor = self._create_conversation_executor()
        logger.info(f"BackendDeveloperAgent initialized with primary={self.settings.agent_model}")
    
    def _create_primary_llm(self) -> BaseLanguageModel:
        """Create primary Claude LLM."""
        return ChatAnthropic(
            model=self.settings.agent_model,
            temperature=self.settings.agent_temperature,
            max_tokens=self.settings.agent_max_tokens,
            api_key=self.settings.anthropic_api_key,
        )
    
    def _create_fallback_llm(self) -> Optional[BaseLanguageModel]:
        """Create fallback OpenAI LLM if configured."""
        if not self.settings.openai_api_key:
            logger.warning("OpenAI API key not configured - no fallback available")
            return None
        
        return ChatOpenAI(
            model=self.settings.openai_model,
            temperature=self.settings.agent_temperature,
            max_tokens=self.settings.agent_max_tokens,
            api_key=self.settings.openai_api_key,
        )
    
    def _switch_to_fallback(self) -> bool:
        """Switch to fallback LLM if available."""
        if self.fallback_llm and self.llm != self.fallback_llm:
            logger.warning(f"Switching from {self.settings.agent_model} to {self.settings.openai_model}")
            self.llm = self.fallback_llm
            # Recreate executors with new LLM
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
        Process a backend development command with intelligent fallback and rate limit handling.
        
        Args:
            command: Command to execute
            
        Returns:
            CommandResponse with results
        """
        is_conversation = command.metadata.get("is_conversation", False)
        prompt = self._format_command_prompt(command)
        
        # Determine which LLM to try first
        primary_name = self.settings.agent_model.split("-")[0]  # "claude" or "gpt"
        fallback_name = "gpt-4o" if primary_name == "claude" else "claude"
        
        # List of LLMs to try in order
        llm_strategies = [
            ("primary", self.primary_llm, primary_name),
            ("fallback", self.fallback_llm, fallback_name),
        ]
        
        last_error = None
        
        for strategy_name, llm, llm_name in llm_strategies:
            if llm is None:
                logger.warning(f"Skipping {strategy_name} ({llm_name}): not configured")
                continue
            
            # Check if this LLM is in rate limit backoff
            if _is_rate_limited(llm_name):
                logger.warning(f"Skipping {strategy_name} ({llm_name}): currently rate limited")
                continue
            
            try:
                logger.info(f"Attempting {strategy_name} LLM: {llm_name}")
                
                # Switch to this LLM if it's not the current one
                if llm != self.llm:
                    logger.info(f"Switching to {llm_name}")
                    self.llm = llm
                    self.executor = self._create_executor()
                    self.conversation_executor = self._create_conversation_executor()
                
                executor = self.conversation_executor if is_conversation else self.executor
                result = executor.invoke({"input": prompt})
                
                # Success! Clear any rate limit tracking for this LLM
                _clear_rate_limit(llm_name)
                
                return CommandResponse(
                    success=True,
                    command_type=command.command_type,
                    result=result.get("output", ""),
                    execution_time=0.0,
                    metadata={
                        "source": command.source,
                        "is_conversation": is_conversation,
                        "llm_used": llm_name
                    }
                )
            
            except Exception as e:
                error_str = str(e).lower()
                last_error = str(e)
                
                logger.error(f"Error with {llm_name}: {str(e)}")
                
                # Check if this is a rate limit or service error
                rate_limit_phrases = [
                    "rate_limit", "429", "rate limit", "quota exceeded",
                    "too many requests", "ratelimit"
                ]
                service_error_phrases = [
                    "overloaded", "unavailable", "temporarily unavailable",
                    "service unavailable", "502", "503", "timeout"
                ]
                token_error_phrases = [
                    "token", "credit", "balance", "insufficient",
                    "quota", "too low", "exceed", "limit"
                ]
                
                if any(phrase in error_str for phrase in rate_limit_phrases):
                    logger.warning(f"{llm_name} hit rate limit - recording backoff")
                    _record_rate_limit_error(llm_name, str(e))
                
                if any(phrase in error_str for phrase in (rate_limit_phrases + service_error_phrases + token_error_phrases)):
                    logger.info(f"Service error detected with {llm_name}, trying next LLM...")
                    continue
                else:
                    # Non-service error, don't try other LLMs
                    logger.error(f"Non-service error, not retrying: {str(e)}")
                    return CommandResponse(
                        success=False,
                        command_type=command.command_type,
                        result=None,
                        error=str(e),
                        metadata={"source": command.source, "llm_attempted": llm_name}
                    )
        
        # If we get here, all LLMs failed
        logger.error("All LLM strategies exhausted")
        
        # Check rate limit status for better error message
        claude_limited = _is_rate_limited("claude")
        gpt_limited = _is_rate_limited("gpt-4o")
        
        if claude_limited or gpt_limited:
            limited_llms = []
            if claude_limited:
                limited_llms.append("Claude (rate limited)")
            if gpt_limited:
                limited_llms.append("GPT-4o (rate limited)")
            
            error_msg = f"""🚫 Both LLM providers are currently rate limited:
{', '.join(limited_llms)}

**What's happening**:
Both Claude and OpenAI APIs are experiencing high load.

**What to do**:
1. Wait a few minutes and try again
2. The system will automatically retry with exponential backoff
3. Check rate limits: https://platform.openai.com/account/rate-limits

Last error: {last_error[:100]}"""
        else:
            error_msg = f"""❌ LLM Service Error - All providers failed

Unable to process request with any available LLM provider.
Primary: {primary_name}
Fallback: {fallback_name}

Last error: {last_error[:150]}"""
        
        return CommandResponse(
            success=False,
            command_type=command.command_type,
            result=None,
            error=error_msg,
            metadata={
                "source": command.source,
                "claude_rate_limited": claude_limited,
                "gpt_rate_limited": gpt_limited,
                "last_error": last_error
            }
        )
    
    def _format_command_prompt(self, command: Command) -> str:
        """Format a command into a natural language prompt."""
        prompt = f"Task: {command.description}\n\n"
        
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
        """Check agent health status including LLM rate limits."""
        claude_info = _llm_rate_limits.get("claude", {})
        gpt_info = _llm_rate_limits.get("gpt-4o", {})
        
        claude_limited = _is_rate_limited("claude")
        gpt_limited = _is_rate_limited("gpt-4o")
        
        return {
            "status": "healthy" if not (claude_limited and gpt_limited) else "degraded",
            "model": self.settings.agent_model,
            "tools_available": len(self.tools),
            "llm_status": {
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
            "fallback_available": bool(self.fallback_llm),
        }
