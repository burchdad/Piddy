"""
Piddy Local Code Engine — Pure offline code intelligence.

Handles code_review, code_generation, debugging, and analysis
WITHOUT any external LLM calls. Uses:
  - Pattern-based code analysis (security, performance, quality)
  - Template-based code generation (REST endpoints, design patterns)
  - KB semantic search (learned knowledge, programming books)
  - AST analysis and call graph data
  - Experience recorder (learns from past fixes)
"""

import logging
import re
import ast
import os
from typing import Dict, Any, Optional, List

from src.models.command import Command, CommandResponse, CommandType

logger = logging.getLogger(__name__)


class LocalCodeEngine:
    """
    Pure offline code engine for Piddy.
    No API keys, no network — works entirely from local tools and knowledge.
    """

    def __init__(self):
        self._analyzer = None
        self._retriever = None
        self._experiences = None

    @property
    def analyzer(self):
        if self._analyzer is None:
            try:
                from src.tools.code_analyzer import get_code_analyzer
                self._analyzer = get_code_analyzer()
            except Exception as e:
                logger.debug(f"Code analyzer unavailable: {e}")
        return self._analyzer

    @property
    def retriever(self):
        if self._retriever is None:
            try:
                from src.knowledge_base.retriever import KnowledgeRetriever
                self._retriever = KnowledgeRetriever()
            except Exception as e:
                logger.debug(f"KB retriever unavailable: {e}")
        return self._retriever

    @property
    def experiences(self):
        if self._experiences is None:
            try:
                from src.kb.experience_recorder import KBExperienceRecorder
                self._experiences = KBExperienceRecorder()
            except Exception as e:
                logger.debug(f"Experience recorder unavailable: {e}")
        return self._experiences

    async def process(self, command: Command) -> Optional[CommandResponse]:
        """
        Process a command using local-only tools.
        Returns None if this command type can't be handled locally.
        """
        # Map command types to handlers
        handlers = {
            CommandType.CODE_REVIEW: self._handle_code_review,
            CommandType.CODE_GENERATION: self._handle_code_generation,
            CommandType.DEBUGGING: self._handle_debugging,
            CommandType.API_DESIGN: self._handle_code_generation,
            CommandType.DATABASE_SCHEMA: self._handle_code_generation,
            CommandType.INFRASTRUCTURE: self._handle_architecture,
            CommandType.DOCUMENTATION: self._handle_code_generation,
        }

        handler = handlers.get(command.command_type)

        # For unmatched types, try keyword-based routing from description
        if handler is None:
            desc = command.description.lower()
            if any(k in desc for k in ["security", "audit", "vulnerability"]):
                handler = self._handle_security_audit
            elif any(k in desc for k in ["performance", "optimize", "speed", "slow"]):
                handler = self._handle_performance
            elif any(k in desc for k in ["architecture", "design", "pattern"]):
                handler = self._handle_architecture

        if handler is None:
            # Fall back to code generation as a generic scaffold
            handler = self._handle_code_generation

        try:
            result = await handler(command)
            if result:
                return CommandResponse(
                    success=True,
                    command_type=command.command_type,
                    result=result,
                    execution_time=0.0,
                    metadata={
                        "source": command.source,
                        "engine": "local",
                        "offline_capable": True,
                    }
                )
        except Exception as e:
            logger.error(f"Local engine error for {command.command_type}: {e}")

        return None

    # ------------------------------------------------------------------
    # CODE REVIEW — pattern-based analysis
    # ------------------------------------------------------------------

    async def _handle_code_review(self, command: Command) -> Optional[str]:
        code = command.description
        context = command.context or {}

        # Extract code from the description if it's wrapped in a request
        code_block = self._extract_code(code)
        if not code_block:
            code_block = code

        results = []

        # 1) Static analysis via CodeAnalyzer
        if self.analyzer:
            try:
                analysis = self.analyzer.analyze(code_block)
                results.append(self._format_analysis(analysis))
            except Exception as e:
                logger.debug(f"Analyzer error: {e}")

        # 2) AST-based checks
        ast_issues = self._ast_check(code_block)
        if ast_issues:
            results.append("## AST Analysis\n" + "\n".join(f"- {i}" for i in ast_issues))

        # 3) Pattern-based security scan
        sec = self._security_scan(code_block)
        if sec:
            results.append("## Security Scan\n" + "\n".join(f"- ⚠️ {s}" for s in sec))

        # 4) KB knowledge lookup
        kb_info = self._search_kb(f"code review best practices {context.get('language', 'python')}")
        if kb_info:
            results.append("## Relevant Knowledge\n" + kb_info)

        if not results:
            return None

        score = self._calculate_quality_score(code_block, ast_issues, sec)
        header = f"## Local Code Review (Score: {score}/100)\n\n"
        return header + "\n\n".join(results)

    # ------------------------------------------------------------------
    # CODE GENERATION — template + pattern library
    # ------------------------------------------------------------------

    async def _handle_code_generation(self, command: Command) -> Optional[str]:
        desc = command.description.lower()
        context = command.context or {}
        language = context.get("language", "python")
        framework = context.get("framework", "")

        results = []

        # Detect what kind of code to generate
        if any(k in desc for k in ["endpoint", "api", "route", "rest"]):
            results.append(self._generate_endpoint(desc, language, framework))
        elif any(k in desc for k in ["pattern", "singleton", "factory", "observer", "strategy"]):
            results.append(self._generate_pattern(desc, language))
        elif any(k in desc for k in ["model", "schema", "database", "table"]):
            results.append(self._generate_model(desc, language))
        elif any(k in desc for k in ["test", "unittest", "pytest"]):
            results.append(self._generate_test(desc, language))
        elif any(k in desc for k in ["class", "service", "module"]):
            results.append(self._generate_class(desc, language))
        elif any(k in desc for k in ["function", "method", "helper", "utility"]):
            results.append(self._generate_function(desc, language))

        # KB lookup for relevant examples
        kb_info = self._search_kb(command.description)
        if kb_info:
            results.append(f"\n## Reference Knowledge\n{kb_info}")

        if not results or all(r is None for r in results):
            # Fallback: generate a basic scaffold
            results = [self._generate_scaffold(command.description, language)]

        return "\n\n".join(r for r in results if r)

    # ------------------------------------------------------------------
    # DEBUGGING — pattern matching + AST
    # ------------------------------------------------------------------

    async def _handle_debugging(self, command: Command) -> Optional[str]:
        desc = command.description
        code_block = self._extract_code(desc) or desc
        results = []

        # Common error patterns
        error_fixes = self._detect_common_errors(code_block)
        if error_fixes:
            results.append("## Detected Issues & Fixes\n" + "\n".join(f"- {f}" for f in error_fixes))

        # AST analysis for structural issues
        ast_issues = self._ast_check(code_block)
        if ast_issues:
            results.append("## Structural Issues\n" + "\n".join(f"- {i}" for i in ast_issues))

        # KB lookup for similar errors
        kb_info = self._search_kb(f"debug fix error {desc[:100]}")
        if kb_info:
            results.append(f"## Related Solutions\n{kb_info}")

        # Experience lookup
        if self.experiences:
            try:
                similar = self.experiences.search_experiences(desc[:100], top_k=3)
                if similar:
                    exp_text = "\n".join(
                        f"- **{e.get('tags', ['fix'])[0]}**: {e.get('description', '')[:200]}"
                        for e in similar
                    )
                    results.append(f"## Past Fixes\n{exp_text}")
            except Exception:
                pass

        if not results:
            return None

        return "## Local Debug Analysis\n\n" + "\n\n".join(results)

    # ------------------------------------------------------------------
    # SECURITY AUDIT
    # ------------------------------------------------------------------

    async def _handle_security_audit(self, command: Command) -> Optional[str]:
        code = self._extract_code(command.description) or command.description
        issues = self._security_scan(code)

        if not issues:
            return "## Security Audit: ✅ No issues detected\n\nNo common security vulnerabilities found in the provided code."

        report = "## Security Audit Report\n\n"
        critical = [i for i in issues if "CRITICAL" in i]
        high = [i for i in issues if "HIGH" in i]
        other = [i for i in issues if "CRITICAL" not in i and "HIGH" not in i]

        if critical:
            report += "### 🔴 Critical\n" + "\n".join(f"- {i}" for i in critical) + "\n\n"
        if high:
            report += "### 🟠 High\n" + "\n".join(f"- {i}" for i in high) + "\n\n"
        if other:
            report += "### 🟡 Other\n" + "\n".join(f"- {i}" for i in other) + "\n\n"

        report += f"\n**Total issues: {len(issues)}** | Critical: {len(critical)} | High: {len(high)}"
        return report

    # ------------------------------------------------------------------
    # PERFORMANCE
    # ------------------------------------------------------------------

    async def _handle_performance(self, command: Command) -> Optional[str]:
        code = self._extract_code(command.description) or command.description
        issues = self._performance_scan(code)
        kb_info = self._search_kb(f"performance optimization {command.description[:80]}")

        results = []
        if issues:
            results.append("## Performance Issues\n" + "\n".join(f"- {i}" for i in issues))
        if kb_info:
            results.append(f"## Optimization Knowledge\n{kb_info}")

        return "\n\n".join(results) if results else None

    # ------------------------------------------------------------------
    # ARCHITECTURE
    # ------------------------------------------------------------------

    async def _handle_architecture(self, command: Command) -> Optional[str]:
        desc = command.description.lower()
        results = []

        # Generate relevant design patterns
        try:
            from src.tools.design_patterns import get_design_pattern, DesignPattern
            patterns_to_suggest = []

            pattern_keywords = {
                DesignPattern.SINGLETON: ["singleton", "single instance", "shared state"],
                DesignPattern.FACTORY: ["factory", "create objects", "instantiate"],
                DesignPattern.STRATEGY: ["strategy", "algorithm", "interchangeable"],
                DesignPattern.OBSERVER: ["observer", "event", "pubsub", "subscribe", "notify"],
                DesignPattern.REPOSITORY: ["repository", "data access", "crud"],
                DesignPattern.DEPENDENCY_INJECTION: ["dependency", "injection", "di", "ioc"],
                DesignPattern.MIDDLEWARE: ["middleware", "pipeline", "chain"],
            }

            for pattern, keywords in pattern_keywords.items():
                if any(kw in desc for kw in keywords):
                    patterns_to_suggest.append(pattern)

            if not patterns_to_suggest:
                patterns_to_suggest = [DesignPattern.REPOSITORY, DesignPattern.FACTORY]

            for pattern in patterns_to_suggest[:3]:
                info = get_design_pattern(pattern, "python")
                results.append(f"### {pattern.value} Pattern\n```python\n{info.get('code', '')}\n```")

        except Exception as e:
            logger.debug(f"Design patterns unavailable: {e}")

        kb_info = self._search_kb(f"architecture design {desc[:100]}")
        if kb_info:
            results.append(f"## Architecture References\n{kb_info}")

        return "## Architecture Suggestions\n\n" + "\n\n".join(results) if results else None

    # ==================================================================
    # INTERNAL HELPERS
    # ==================================================================

    def _extract_code(self, text: str) -> Optional[str]:
        """Extract code block from text."""
        # Try markdown code blocks
        match = re.search(r'```(?:\w+)?\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Try indented code (4+ spaces)
        lines = text.split('\n')
        code_lines = [l for l in lines if l.startswith('    ') or l.startswith('\t')]
        if len(code_lines) > 2:
            return '\n'.join(code_lines)

        # If it looks like code (has def/class/import), use the whole thing
        if any(kw in text for kw in ['def ', 'class ', 'import ', 'from ', 'async def']):
            return text

        return None

    def _ast_check(self, code: str) -> List[str]:
        """Run AST-based checks on Python code."""
        issues = []
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [f"**Syntax Error** at line {e.lineno}: {e.msg}"]

        for node in ast.walk(tree):
            # Bare except
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append(f"Line {node.lineno}: Bare `except:` clause — specify exception types")

            # Mutable default arguments
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for default in node.args.defaults + node.args.kw_defaults:
                    if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append(
                            f"Line {node.lineno}: Mutable default argument in `{node.name}()` "
                            f"— use `None` and initialize inside"
                        )

                # Missing return type annotation
                if not node.returns:
                    issues.append(f"Line {node.lineno}: `{node.name}()` missing return type annotation")

            # Global variable usage
            if isinstance(node, ast.Global):
                issues.append(f"Line {node.lineno}: `global` statement — consider passing as parameter")

            # Star imports
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == '*':
                        issues.append(f"Line {node.lineno}: `from {node.module} import *` — import explicitly")

        return issues

    def _security_scan(self, code: str) -> List[str]:
        """Pattern-based security vulnerability scan."""
        issues = []
        patterns = [
            (r'exec\s*\(', "CRITICAL: `exec()` call — allows arbitrary code execution"),
            (r'eval\s*\(', "CRITICAL: `eval()` call — allows arbitrary code execution"),
            (r'pickle\.loads?\s*\(', "HIGH: Unsafe pickle deserialization — use `json` instead"),
            (r'subprocess\.call\s*\(.*shell\s*=\s*True', "HIGH: Shell injection risk — use `shell=False`"),
            (r'os\.system\s*\(', "HIGH: `os.system()` — use `subprocess.run()` with `shell=False`"),
            (r'password\s*=\s*["\'][^"\']+["\']', "HIGH: Hardcoded password — use environment variables"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "HIGH: Hardcoded secret — use environment variables"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "HIGH: Hardcoded API key — use environment variables"),
            (r'\.format\s*\(.*\)\s*$.*SELECT|INSERT|UPDATE|DELETE', "HIGH: SQL injection risk — use parameterized queries"),
            (r'f["\'].*SELECT.*\{', "HIGH: f-string in SQL — use parameterized queries"),
            (r'verify\s*=\s*False', "MEDIUM: SSL verification disabled"),
            (r'DEBUG\s*=\s*True', "MEDIUM: Debug mode enabled — disable in production"),
            (r'CORS.*allow_origins.*\*', "MEDIUM: CORS allows all origins"),
        ]
        for pattern, message in patterns:
            if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
                issues.append(message)
        return issues

    def _performance_scan(self, code: str) -> List[str]:
        """Pattern-based performance issue detection."""
        issues = []
        patterns = [
            (r'for.*in.*\.query\(', "N+1 query pattern — batch your database queries"),
            (r're\.compile\(.*\)\s*$.*for ', "Regex compiled inside loop — compile once outside"),
            (r'\+= .*\+.*(?:str|join)', "String concatenation in loop — use `str.join()` or list"),
            (r'time\.sleep\(', "Blocking `sleep()` — consider `asyncio.sleep()` in async code"),
            (r'\.readlines\(\)', "`.readlines()` loads entire file — iterate line by line instead"),
            (r'list\(.*range\(.*\d{6}', "Large list in memory — use generator with `range()` directly"),
            (r'import \*', "Wildcard import — increases memory and load time"),
        ]
        for pattern, message in patterns:
            if re.search(pattern, code, re.MULTILINE):
                issues.append(message)
        return issues

    def _detect_common_errors(self, code: str) -> List[str]:
        """Detect common Python errors and suggest fixes."""
        fixes = []

        # Indentation issues
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if line and not line[0].isspace() and line[0] != '#' and line[0] != '\n':
                if i > 1 and lines[i-2].rstrip().endswith(':'):
                    fixes.append(f"Line {i}: Expected indentation after block statement")

        # Common typos/mistakes
        typo_patterns = [
            (r'retrun\b', "Typo: `retrun` → `return`"),
            (r'pritn\b', "Typo: `pritn` → `print`"),
            (r'slef\b', "Typo: `slef` → `self`"),
            (r'improt\b', "Typo: `improt` → `import`"),
            (r'ture\b', "Typo: `ture` → `True`"),
            (r'flase\b', "Typo: `flase` → `False`"),
            (r'defualt\b', "Typo: `defualt` → `default`"),
            (r'== None\b', "Use `is None` instead of `== None`"),
            (r'!= None\b', "Use `is not None` instead of `!= None`"),
            (r'except:\s*$', "Bare except — catch specific exceptions"),
            (r'from .* import \*', "Wildcard import — import specific names"),
        ]
        for pattern, message in typo_patterns:
            if re.search(pattern, code):
                fixes.append(message)

        # Try AST parse for syntax errors
        try:
            ast.parse(code)
        except SyntaxError as e:
            fixes.append(f"**Syntax Error** at line {e.lineno}: {e.msg}")

        return fixes

    def _calculate_quality_score(self, code: str, ast_issues: List, sec_issues: List) -> int:
        """Calculate a quality score 0-100."""
        score = 100
        score -= len(ast_issues) * 3
        score -= len(sec_issues) * 5

        # Bonus for good practices
        if 'def ' in code and '->' in code:
            score += 2  # type hints
        if '"""' in code or "'''" in code:
            score += 2  # docstrings

        return max(0, min(100, score))

    def _search_kb(self, query: str) -> Optional[str]:
        """Search knowledge base for relevant info."""
        if not self.retriever:
            return None
        try:
            results = self.retriever.search(query, top_k=3, threshold=0.3)
            if results:
                snippets = []
                for r in results[:3]:
                    content = r.content[:300].strip()
                    snippets.append(f"> **{r.filename}** (relevance: {r.relevance_score:.0%})\n> {content}...")
                return "\n\n".join(snippets)
        except Exception as e:
            logger.debug(f"KB search error: {e}")
        return None

    # ------------------------------------------------------------------
    # Code generation helpers
    # ------------------------------------------------------------------

    def _generate_endpoint(self, desc: str, language: str, framework: str) -> str:
        """Generate a REST endpoint using template library."""
        try:
            from src.tools.advanced_codegen import generate_rest_endpoint, Language

            # Parse endpoint details from description
            method = "POST" if any(w in desc for w in ["create", "add", "post"]) else \
                     "PUT" if any(w in desc for w in ["update", "edit", "put"]) else \
                     "DELETE" if any(w in desc for w in ["delete", "remove"]) else "GET"

            # Extract name from description
            name_match = re.search(r'(?:for|named?|called?)\s+(\w+)', desc)
            name = name_match.group(1) if name_match else "resource"

            # Pluralize name for path (simple heuristic)
            path_name = name if name.endswith('s') else f"{name}s"

            fw = framework or ("fastapi" if language == "python" else
                              "express" if language in ("javascript", "typescript") else "fastapi")

            lang_map = {"python": Language.PYTHON, "javascript": Language.NODEJS,
                       "typescript": Language.NODEJS, "java": Language.JAVA,
                       "go": Language.GO, "rust": Language.RUST,
                       "nodejs": Language.NODEJS}

            code = generate_rest_endpoint(
                endpoint_name=name,
                http_method=method,
                path=f"/{path_name}",
                language=lang_map.get(language, Language.PYTHON),
                framework=fw,
                auth_required="auth" in desc,
            )
            return f"## Generated {method} /{name}s Endpoint ({fw})\n\n```{language}\n{code}\n```"
        except Exception as e:
            logger.debug(f"Codegen error: {e}")
            return self._generate_scaffold(desc, language)

    def _generate_pattern(self, desc: str, language: str) -> str:
        """Generate a design pattern from the template library."""
        try:
            from src.tools.design_patterns import get_design_pattern, DesignPattern

            pattern_map = {
                "singleton": DesignPattern.SINGLETON,
                "factory": DesignPattern.FACTORY,
                "strategy": DesignPattern.STRATEGY,
                "observer": DesignPattern.OBSERVER,
                "decorator": DesignPattern.DECORATOR,
                "repository": DesignPattern.REPOSITORY,
                "middleware": DesignPattern.MIDDLEWARE,
            }

            pattern = None
            for keyword, dp in pattern_map.items():
                if keyword in desc:
                    pattern = dp
                    break

            if pattern:
                info = get_design_pattern(pattern, language)
                return f"## {pattern.value} Pattern\n\n```{language}\n{info.get('code', '')}\n```\n\n{info.get('description', '')}"

        except Exception as e:
            logger.debug(f"Pattern gen error: {e}")

        return self._generate_scaffold(desc, language)

    def _generate_model(self, desc: str, language: str) -> str:
        """Generate a database model scaffold."""
        name_match = re.search(r'(?:model|schema|table)\s+(?:for\s+)?(\w+)', desc, re.IGNORECASE)
        name = name_match.group(1).title() if name_match else "Resource"

        if language == "python":
            return f"""## Generated Model: {name}

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class {name}(Base):
    __tablename__ = "{name.lower()}s"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<{name}(id={{self.id}}, name={{self.name}})>"
```"""
        return self._generate_scaffold(desc, language)

    def _generate_test(self, desc: str, language: str) -> str:
        """Generate a test scaffold."""
        name_match = re.search(r'(?:test|for)\s+(\w+)', desc, re.IGNORECASE)
        name = name_match.group(1) if name_match else "function"

        return f"""## Generated Tests for `{name}`

```python
import pytest

class Test{name.title()}:
    \"\"\"Tests for {name} functionality.\"\"\"

    def test_{name}_success(self):
        \"\"\"Test {name} with valid input.\"\"\"
        result = {name}()
        assert result is not None

    def test_{name}_invalid_input(self):
        \"\"\"Test {name} with invalid input.\"\"\"
        with pytest.raises(ValueError):
            {name}(None)

    def test_{name}_edge_case(self):
        \"\"\"Test {name} boundary conditions.\"\"\"
        result = {name}("")
        assert result is not None

    @pytest.mark.asyncio
    async def test_{name}_async(self):
        \"\"\"Test async variant if applicable.\"\"\"
        result = await {name}()
        assert result is not None
```"""

    def _generate_class(self, desc: str, language: str) -> str:
        """Generate a class scaffold."""
        name_match = re.search(r'(?:class|service|module)\s+(?:for\s+|named?\s+|called?\s+)?(\w+)', desc, re.IGNORECASE)
        name = name_match.group(1).title() if name_match else "Service"

        return f"""## Generated Class: {name}

```python
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class {name}:
    \"\"\"Service for {name.lower()} operations.\"\"\"

    def __init__(self):
        self._data: Dict = {{}}
        logger.info(f"{name} initialized")

    def create(self, data: Dict) -> Dict:
        \"\"\"Create a new resource.\"\"\"
        resource_id = str(len(self._data) + 1)
        self._data[resource_id] = data
        return {{"id": resource_id, **data}}

    def get(self, resource_id: str) -> Optional[Dict]:
        \"\"\"Get a resource by ID.\"\"\"
        return self._data.get(resource_id)

    def list_all(self) -> List[Dict]:
        \"\"\"List all resources.\"\"\"
        return [{{"id": k, **v}} for k, v in self._data.items()]

    def update(self, resource_id: str, data: Dict) -> Optional[Dict]:
        \"\"\"Update a resource.\"\"\"
        if resource_id in self._data:
            self._data[resource_id].update(data)
            return {{"id": resource_id, **self._data[resource_id]}}
        return None

    def delete(self, resource_id: str) -> bool:
        \"\"\"Delete a resource.\"\"\"
        return self._data.pop(resource_id, None) is not None
```"""

    def _generate_function(self, desc: str, language: str) -> str:
        """Generate a function scaffold."""
        name_match = re.search(r'(?:function|method|helper|utility)\s+(?:for\s+|named?\s+|to\s+)?(\w+)', desc, re.IGNORECASE)
        name = name_match.group(1) if name_match else "process"

        return f"""## Generated Function: `{name}`

```python
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

def {name}(data: Any, *, strict: bool = False) -> Optional[Any]:
    \"\"\"
    {desc[:100]}

    Args:
        data: Input data to process
        strict: If True, raise on invalid input

    Returns:
        Processed result or None
    \"\"\"
    if data is None:
        if strict:
            raise ValueError("{name}: data cannot be None")
        return None

    try:
        result = data  # Transform as needed
        logger.info(f"{name} processed successfully")
        return result
    except Exception as e:
        logger.error(f"{name} failed: {{e}}")
        if strict:
            raise
        return None
```"""

    def _generate_scaffold(self, desc: str, language: str) -> str:
        """Generic fallback scaffold when no specific template matches."""
        return f"""## Generated Code Scaffold

Based on your request: *{desc[:200]}*

```{language}
# Piddy Local Engine — Generated scaffold
# Customize this template for your needs

# TODO: Implement the following based on the description above
# The local engine generated this scaffold without external APIs.
# For more sophisticated generation, ensure Ollama is running locally
# or cloud LLMs are available.

def main():
    \"\"\"Entry point.\"\"\"
    pass

if __name__ == "__main__":
    main()
```

> 💡 **Tip**: For more detailed code generation, install and run Ollama locally:
> `ollama pull codellama:13b && ollama serve`"""
