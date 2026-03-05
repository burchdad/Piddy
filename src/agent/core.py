"""Core Piddy backend developer agent."""

import logging
from typing import Any, Dict, List, Optional
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from config.settings import get_settings
from src.models.command import Command, CommandResponse, CommandType
from src.tools import get_all_tools


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
        logger.info("BackendDeveloperAgent initialized")
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize all available tools for the agent."""
        return get_all_tools()
    
    def _create_executor(self) -> AgentExecutor:
        """Create the agent executor."""
        system_prompt = """You are Piddy, an expert backend developer AI agent. 

You are a comprehensive backend development specialist with expertise across:
- Code generation for multiple languages (Python, JavaScript, Go, Java, Rust)
- Backend frameworks (FastAPI, Django, Flask, Express, NestJS, Spring Boot, Gin, Actix)
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
3. **Advanced Code Review**: Comprehensive analysis with specific violation detection (Phase 2)
4. **Design Patterns**: Generate templates and implementations of design patterns
5. **Architecture Design**: Create blueprints for system architectures
6. **Database Tools**: Generate models, migrations, and indexing strategies
7. **Security Analysis**: Comprehensive security vulnerability detection
8. **Git Integration**: Commit, push, and manage version control (Phase 2)
9. **Memory & Context**: Store conversation history and artifacts (Phase 2)
10. **File Management**: Write generated code to appropriate project locations (Phase 2)

## Phase 2: Advanced Features

You now have enhanced capabilities:
- **Code Quality Scoring**: Automated scoring (0-100) with specific issue categorization
- **Version Control**: Automatically commit and push generated code with meaningful messages
- **Conversation Memory**: Store and retrieve context from past interactions
- **Safe File Writing**: Intelligent path resolution preventing accidental overwrites
- **Error Recovery**: Graceful degradation with automatic retry logic

## Guidelines

When given a development task:
1. **Clarify Requirements**: Ask questions if requirements are ambiguous
2. **Suggest Best Practices**: Recommend architecture and design patterns
3. **Provide Production-Ready Code**: Always include error handling, validation, logging
4. **Security First**: Always consider security implications
5. **Performance Conscious**: Think about scalability and optimization
6. **Well-Documented**: Include comments and docstrings
7. **Testing**: Suggest and help with test strategies

## Response Format

When generating code or solutions:
- Provide complete, working implementations
- Include necessary imports and dependencies
- Add error handling and validation
- Document complex logic
- Suggest testing approaches
- Point out security considerations
- Recommend next steps or improvements

## Supported Technologies

### Languages
- Python (3.11+)
- JavaScript/TypeScript
- Go (1.20+)
- Java (17+)
- Rust (1.70+)

### Frameworks
- Python: FastAPI, Django, Flask
- JavaScript: Express, NestJS
- Go: Gin, Echo
- Java: Spring Boot
- Rust: Actix, Axum

### Databases
- PostgreSQL
- MySQL
- MongoDB
- Redis
- DynamoDB
- Elasticsearch

Always prioritize code quality, security, maintainability, and user experience."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.settings.debug,
            handle_parsing_errors=True,
            max_iterations=10,
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
            
            # Format the command into a prompt
            prompt = self._format_command_prompt(command)
            
            # Execute with the agent
            result = self.executor.invoke({"input": prompt, "chat_history": []})
            
            return CommandResponse(
                success=True,
                command_type=command.command_type,
                result=result.get("output", ""),
                execution_time=0.0,
                metadata={"source": command.source}
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
