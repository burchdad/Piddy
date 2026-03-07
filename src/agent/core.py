"""Core Piddy backend developer agent."""

import logging
from typing import Any, Dict, List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate

from config.settings import get_settings
from src.models.command import Command, CommandResponse, CommandType
from src.tools import get_all_tools
from src.agent.conversational_prompt import CONVERSATIONAL_SYSTEM_PROMPT


logger = logging.getLogger(__name__)


class BackendDeveloperAgent:
    """
    Piddy: AI Backend Developer Agent
    Capable of handling comprehensive backend development tasks.
    """
    
    def __init__(self):
        """Initialize the backend developer agent."""
        self.settings = get_settings()
        self.llm = ChatAnthropic(
            model=self.settings.agent_model,
            temperature=self.settings.agent_temperature,
            max_tokens=self.settings.agent_max_tokens,
            api_key=self.settings.anthropic_api_key,
        )
        self.tools = self._initialize_tools()
        self.executor = self._create_executor()
        self.conversation_executor = self._create_conversation_executor()
        logger.info("BackendDeveloperAgent initialized")
    
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
        
        Args:
            command: Command to execute
            
        Returns:
            CommandResponse with results
        """
        try:
            logger.info(f"Processing command: {command.command_type}")
            
            # Check if this is a conversation mode request
            is_conversation = command.metadata.get("is_conversation", False)
            executor = self.conversation_executor if is_conversation else self.executor
            
            # Format the command into a prompt
            prompt = self._format_command_prompt(command)
            
            # Execute with the appropriate executor
            # ReAct agents only need 'input', they manage scratchpad internally
            result = executor.invoke({"input": prompt})
            
            return CommandResponse(
                success=True,
                command_type=command.command_type,
                result=result.get("output", ""),
                execution_time=0.0,
                metadata={"source": command.source, "is_conversation": is_conversation}
            )
        
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}", exc_info=True)
            return CommandResponse(
                success=False,
                command_type=command.command_type,
                result=None,
                error=str(e),
                metadata={"source": command.source}
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
        """Check agent health status."""
        return {
            "status": "healthy",
            "model": self.settings.agent_model,
            "tools_available": len(self.tools),
        }
