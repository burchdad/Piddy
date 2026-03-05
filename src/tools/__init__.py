"""Agent tools initialization and management."""

import json
import logging
from langchain.tools import Tool
from typing import List, Dict, Any
from src.tools.advanced_codegen import generate_rest_endpoint, Language, APIStyle
from src.tools.code_review import analyze_code_quality, suggest_refactoring
from src.tools.design_patterns import get_design_pattern, get_architecture_blueprint, DesignPattern, ArchitecturePattern
from src.tools.database_tools import generate_database_models, generate_migration, generate_index_strategy, DatabaseType
from src.tools.security_analysis import analyze_security, get_security_recommendations
from src.tools.code_analyzer import CodeAnalyzer
from src.tools.git_manager import get_git_manager
from src.utils.memory import get_memory
from src.utils.file_writer import write_generated_file, FileType
from src.utils.error_handler import ErrorHandler

logger = logging.getLogger(__name__)


def _tool_generate_rest_endpoint(description: str) -> str:
    """Wrapper for REST endpoint generation."""
    try:
        params = json.loads(description)
        result = generate_rest_endpoint(
            endpoint_name=params.get("endpoint_name", "endpoint"),
            http_method=params.get("method", "GET"),
            path=params.get("path", "/"),
            language=Language(params.get("language", "python")),
            framework=params.get("framework", "fastapi"),
        )
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_analyze_code(code: str) -> str:
    """Wrapper for code quality analysis."""
    try:
        result = analyze_code_quality(code, language="python")
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_suggest_refactoring(code: str) -> str:
    """Wrapper for refactoring suggestions."""
    try:
        result = suggest_refactoring(code)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_get_design_pattern(pattern_name: str) -> str:
    """Wrapper for design pattern generation."""
    try:
        pattern = DesignPattern(pattern_name.lower())
        result = get_design_pattern(pattern, language="python")
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_get_architecture(arch_name: str) -> str:
    """Wrapper for architecture blueprint."""
    try:
        architecture = ArchitecturePattern(arch_name.lower())
        result = get_architecture_blueprint(architecture)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_generate_database_model(description: str) -> str:
    """Wrapper for database model generation."""
    try:
        params = json.loads(description)
        result = generate_database_models(
            entity_name=params.get("entity_name", "Entity"),
            fields=params.get("fields", {}),
            language=params.get("language", "python"),
            framework=params.get("framework", "sqlalchemy"),
        )
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_generate_migration(description: str) -> str:
    """Wrapper for migration generation."""
    try:
        params = json.loads(description)
        result = generate_migration(
            operation=params.get("operation", "create_table"),
            entity_name=params.get("entity_name", "Entity"),
            fields=params.get("fields"),
            language=params.get("language", "python"),
        )
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_security_analysis(code: str) -> str:
    """Wrapper for security analysis."""
    try:
        result = analyze_security(code, language="python")
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {str(e)}"


def _tool_security_recommendations(tech_stack: str) -> str:
    """Wrapper for security recommendations."""
    try:
        result = get_security_recommendations(tech_stack)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"


# Phase 2: Advanced Code Review
def _tool_advanced_code_review(code: str) -> str:
    """Wrapper for advanced code analysis and review."""
    try:
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(code, language="python")
        
        # Format for agent consumption
        formatted = {
            "score": result["score"],
            "total_issues": result["summary"]["total"],
            "critical": result["summary"]["critical"],
            "high": result["summary"]["high"],
            "medium": result["summary"]["medium"],
            "low": result["summary"]["low"],
            "issues": [
                {
                    "severity": issue.severity.value,
                    "category": issue.category.value,
                    "line": issue.line,
                    "message": issue.message,
                    "suggestion": issue.suggestion
                }
                for issue in result["issues"][:10]  # Top 10 issues
            ],
            "recommendations": result["recommendations"]
        }
        
        return json.dumps(formatted, indent=2)
    except Exception as e:
        logger.error(f"Code review error: {e}")
        return f"Error: {str(e)}"


# Phase 2: Git Integration
def _tool_git_commit(description: str) -> str:
    """Wrapper for Git commit operations."""
    try:
        params = json.loads(description)
        git = get_git_manager()
        
        if git is None:
            return json.dumps({"success": False, "error": "Git manager not available"})
        
        result = git.commit(
            message=params.get("message", "Auto-commit from Piddy"),
            files=params.get("files"),
            auto_stage=params.get("auto_stage", True)
        )
        
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Git commit error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_git_push(description: str) -> str:
    """Wrapper for Git push operations."""
    try:
        params = json.loads(description)
        git = get_git_manager()
        
        if git is None:
            return json.dumps({"success": False, "error": "Git manager not available"})
        
        result = git.push(
            branch=params.get("branch"),
            force=params.get("force", False)
        )
        
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Git push error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_git_status() -> str:
    """Wrapper for checking Git status."""
    try:
        git = get_git_manager()
        
        if git is None:
            return json.dumps({"success": False, "error": "Git manager not available"})
        
        result = git.get_status()
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Git status error: {e}")
        return json.dumps({"success": False, "error": str(e)})


# Phase 2: Memory & Context
def _tool_save_conversation_context(description: str) -> str:
    """Wrapper for saving conversation context."""
    try:
        params = json.loads(description)
        memory = get_memory()
        
        success = memory.create_conversation(
            conversation_id=params.get("conversation_id", ""),
            user_id=params.get("user_id", ""),
            channel_id=params.get("channel_id", ""),
            project_context=params.get("project_context", ""),
            title=params.get("title", "")
        )
        
        return json.dumps({
            "success": success,
            "message": "Context saved" if success else "Context already exists"
        })
    except Exception as e:
        logger.error(f"Save context error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def _tool_save_generated_artifact(description: str) -> str:
    """Wrapper for saving generated artifacts."""
    try:
        params = json.loads(description)
        memory = get_memory()
        
        success = memory.save_artifact(
            conversation_id=params.get("conversation_id", ""),
            artifact_type=params.get("artifact_type", "code"),
            content=params.get("content", ""),
            filename=params.get("filename", ""),
            file_path=params.get("file_path", ""),
            language=params.get("language", "python")
        )
        
        return json.dumps({
            "success": success,
            "message": "Artifact saved" if success else "Error saving artifact"
        })
    except Exception as e:
        logger.error(f"Save artifact error: {e}")
        return json.dumps({"success": False, "error": str(e)})


# Phase 2: File Writing
def _tool_write_generated_code(description: str) -> str:
    """Wrapper for writing generated code to files."""
    try:
        params = json.loads(description)
        
        file_type = FileType[params.get("file_type", "OTHER").upper()]
        
        result = write_generated_file(
            filename=params.get("filename", "generated.py"),
            content=params.get("content", ""),
            file_type=file_type,
            subdir=params.get("subdir")
        )
        
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Write file error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def get_all_tools() -> List[Tool]:
    """Get all available tools for the agent."""
    tools = []
    
    # Code Generation Tools
    tools.extend([
        Tool(
            name="generate_rest_endpoint",
            func=_tool_generate_rest_endpoint,
            description="Generate complete REST API endpoints in FastAPI, Django, Flask, Express, NestJS, Spring Boot, Gin, or Actix. Pass JSON with: endpoint_name, method (GET/POST/PUT/DELETE), path, language, framework"
        ),
        Tool(
            name="generate_graphql_endpoint",
            func=lambda x: "GraphQL endpoint generation - pass query/mutation definition",
            description="Generate GraphQL endpoints and resolver functions"
        ),
    ])
    
    # Code Analysis & Review Tools
    tools.extend([
        Tool(
            name="analyze_code_quality",
            func=_tool_analyze_code,
            description="Analyze code for quality issues, performance problems, security issues, and best practice violations"
        ),
        Tool(
            name="suggest_refactoring",
            func=_tool_suggest_refactoring,
            description="Get refactoring suggestions to improve code quality, performance, and maintainability"
        ),
    ])
    
    # Design Pattern Tools
    tools.extend([
        Tool(
            name="get_design_pattern",
            func=_tool_get_design_pattern,
            description="Get implementation template for design patterns: singleton, factory, strategy, observer, decorator, adapter, builder, repository, middleware, or dependency_injection"
        ),
        Tool(
            name="get_architecture_pattern",
            func=_tool_get_architecture,
            description="Get architecture blueprint: layered, microservices, event_driven, or hexagonal"
        ),
    ])
    
    # Database Tools
    tools.extend([
        Tool(
            name="generate_database_models",
            func=_tool_generate_database_model,
            description="Generate database models for SQLAlchemy, Django ORM, Pydantic, Mongoose, TypeORM, or JPA. Pass JSON with: entity_name, fields dict, language, framework"
        ),
        Tool(
            name="generate_database_migration",
            func=_tool_generate_migration,
            description="Generate database migration scripts for Alembic or Knex. Pass JSON with: operation (create_table/add_column), entity_name, fields"
        ),
    ])
    
    # Security Tools
    tools.extend([
        Tool(
            name="security_analysis",
            func=_tool_security_analysis,
            description="Comprehensive security analysis checking for vulnerabilities, injection attacks, hardcoded credentials, and best practice violations"
        ),
        Tool(
            name="security_recommendations",
            func=_tool_security_recommendations,
            description="Get security best practices and recommendations for your tech stack"
        ),
    ])
    
    # Phase 2: Advanced Code Review
    tools.extend([
        Tool(
            name="advanced_code_review",
            func=_tool_advanced_code_review,
            description="Perform advanced code review analyzing security vulnerabilities, performance issues, best practices, error handling, and type safety. Pass the code to review."
        ),
    ])
    
    # Phase 2: Git Integration
    tools.extend([
        Tool(
            name="git_commit",
            func=_tool_git_commit,
            description="Create a Git commit with generated code. Pass JSON with: message (commit message), files (optional list), auto_stage (true to stage all)."
        ),
        Tool(
            name="git_push",
            func=_tool_git_push,
            description="Push commits to remote repository. Pass JSON with: branch (optional, current branch used if not specified), force (false by default)."
        ),
        Tool(
            name="git_status",
            func=_tool_git_status,
            description="Check current Git repository status including staged, unstaged, and untracked files."
        ),
    ])
    
    # Phase 2: Memory & Context
    tools.extend([
        Tool(
            name="save_conversation_context",
            func=_tool_save_conversation_context,
            description="Save conversation context for future reference. Pass JSON with: conversation_id, user_id, channel_id, project_context, title."
        ),
        Tool(
            name="save_generated_artifact",
            func=_tool_save_generated_artifact,
            description="Save generated code/artifacts to memory. Pass JSON with: conversation_id, artifact_type (code/schema/config), content, filename, file_path, language."
        ),
    ])
    
    # Phase 2: File Writing
    tools.extend([
        Tool(
            name="write_generated_code",
            func=_tool_write_generated_code,
            description="Write generated code to appropriate project location. Pass JSON with: filename, content, file_type (MODEL/ROUTE/UTILITY/SERVICE/SCHEMA/TEST/CONFIG), subdir (optional)."
        ),
    ])
    
    return tools
