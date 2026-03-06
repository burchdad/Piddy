"""
Multi-language support system for code analysis and generation.

Extends Piddy to work seamlessly across multiple programming languages
with specialized analysis and generation for each.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    KOTLIN = "kotlin"


@dataclass
class LanguageConfig:
    """Configuration for a language."""
    name: str
    file_extensions: List[str]
    frameworks: List[str]
    orms: List[str]
    type_safe: bool  # Whether language has strong typing
    async_native: bool  # Native async/await support
    package_managers: List[str]
    testing_frameworks: List[str]


# Language configurations
LANGUAGE_CONFIGS: Dict[Language, LanguageConfig] = {
    Language.PYTHON: LanguageConfig(
        name="Python",
        file_extensions=[".py"],
        frameworks=["FastAPI", "Django", "Flask", "Starlette"],
        orms=["SQLAlchemy", "Django ORM", "Tortoise", "Peewee"],
        type_safe=False,
        async_native=True,
        package_managers=["pip", "poetry", "pipenv"],
        testing_frameworks=["pytest", "unittest", "nose"]
    ),
    Language.JAVASCRIPT: LanguageConfig(
        name="JavaScript",
        file_extensions=[".js", ".mjs"],
        frameworks=["Express", "Fastify", "Koa", "Hapi"],
        orms=["Sequelize", "TypeORM", "Prisma", "Knex"],
        type_safe=False,
        async_native=True,
        package_managers=["npm", "yarn", "pnpm"],
        testing_frameworks=["jest", "mocha", "vitest"]
    ),
    Language.TYPESCRIPT: LanguageConfig(
        name="TypeScript",
        file_extensions=[".ts"],
        frameworks=["NestJS", "Express", "Fastify", "Koa"],
        orms=["TypeORM", "Prisma", "Sequelize", "Knex"],
        type_safe=True,
        async_native=True,
        package_managers=["npm", "yarn", "pnpm"],
        testing_frameworks=["jest", "mocha", "vitest"]
    ),
    Language.JAVA: LanguageConfig(
        name="Java",
        file_extensions=[".java"],
        frameworks=["Spring Boot", "Quarkus", "Micronaut", "Vert.x"],
        orms=["Hibernate", "JPA", "Sqlc", "jOOQ"],
        type_safe=True,
        async_native=False,
        package_managers=["maven", "gradle"],
        testing_frameworks=["JUnit", "Testng", "Spock"]
    ),
    Language.GO: LanguageConfig(
        name="Go",
        file_extensions=[".go"],
        frameworks=["Gin", "Echo", "Fiber", "Gorilla"],
        orms=["GORM", "sqlc", "ent", "sqlx"],
        type_safe=True,
        async_native=True,
        package_managers=["go mod"],
        testing_frameworks=["testing", "testify", "ginkgo"]
    ),
    Language.RUST: LanguageConfig(
        name="Rust",
        file_extensions=[".rs"],
        frameworks=["Actix", "Tokio", "Axum", "Rocket"],
        orms=["Diesel", "SQLx", "SeaORM", "sqlx"],
        type_safe=True,
        async_native=True,
        package_managers=["cargo"],
        testing_frameworks=["built-in", "criterion", "proptest"]
    ),
    Language.CSHARP: LanguageConfig(
        name="C#",
        file_extensions=[".cs"],
        frameworks=["ASP.NET Core", "ServiceStack", "Nancy"],
        orms=["Entity Framework Core", "Dapper", "NHibernate"],
        type_safe=True,
        async_native=True,
        package_managers=["NuGet"],
        testing_frameworks=["xUnit", "NUnit", "MSTest"]
    ),
    Language.PHP: LanguageConfig(
        name="PHP",
        file_extensions=[".php"],
        frameworks=["Laravel", "Symfony", "Slim", "Fat-Free"],
        orms=["Eloquent", "Doctrine", "Propel"],
        type_safe=False,
        async_native=False,
        package_managers=["composer"],
        testing_frameworks=["PHPUnit", "Codeception"]
    ),
    Language.RUBY: LanguageConfig(
        name="Ruby",
        file_extensions=[".rb"],
        frameworks=["Rails", "Sinatra", "Hanami", "Roda"],
        orms=["ActiveRecord", "ROM", "Sequel"],
        type_safe=False,
        async_native=False,
        package_managers=["bundler", "gem"],
        testing_frameworks=["RSpec", "Minitest", "Cucumber"]
    ),
    Language.KOTLIN: LanguageConfig(
        name="Kotlin",
        file_extensions=[".kt"],
        frameworks=["Spring Boot", "Ktor", "Quarkus"],
        orms=["Exposed", "Hibernate", "Room"],
        type_safe=True,
        async_native=True,
        package_managers=["maven", "gradle"],
        testing_frameworks=["JUnit", "Kotest", "Mockk"]
    ),
}


class LanguageSwitcher:
    """
    Intelligently switch analysis and generation strategies by language.
    """

    # Language-specific security patterns
    SECURITY_PATTERNS: Dict[Language, Dict[str, Tuple[str, str]]] = {
        Language.PYTHON: {
            r"exec\s*\(": ("exec() unsafe", "Use ast.literal_eval() or safer alternative"),
            r"pickle\.loads": ("Unsafe deserialization", "Use json instead"),
            r"os\.system": ("Shell injection risk", "Use subprocess.run() with shell=False"),
        },
        Language.JAVASCRIPT: {
            r"eval\s*\(": ("eval() unsafe", "Use safer JSON.parse or Function constructor"),
            r"innerHTML\s*=": ("XSS vulnerability", "Use textContent or DOM APIs"),
            r"Math\.random.*crypto": ("Weak RNG", "Use crypto.getRandomValues()"),
        },
        Language.JAVA: {
            r"Runtime\.getRuntime\(\)\.exec": ("Command injection", "Use ProcessBuilder"),
            r"SQL.*\+.*user": ("SQL injection", "Use prepared statements"),
            r"ObjectInputStream": ("Unsafe deserialization", "Use safer JSON libraries"),
        },
        Language.GO: {
            r"sql\.Open.*eval": ("SQL injection", "Use parameterized queries"),
            r"exec\.Command": ("Command injection", "Avoid using user input directly"),
            r"pickle": ("Unsafe serialization", "Use JSON"),
        },
        Language.RUST: {
            r"unsafe\s*\{": ("Unsafe code", "Minimize unsafe blocks"),
            r"unwrap\(\)": ("Panic risk", "Use Result handling"),
            r"format!\s*\{.*user": ("Format injection", "Use proper formatting"),
        },
    }

    # Language-specific performance patterns
    PERFORMANCE_PATTERNS: Dict[Language, Dict[str, Tuple[str, str]]] = {
        Language.PYTHON: {
            r"for.*in.*\.query": ("N+1 query", "Use JOIN or select_related"),
            r"\[.*for.*in.*\]\[0\]": ("Inefficient", "Use next(iter(...))"),
            r"\.copy\(\)": ("Unnecessary copy", "Use views/references"),
        },
        Language.JAVASCRIPT: {
            r"for\s*\(\s*let.*Array": ("Use forEach/map", "Modern iteration"),
            r"\.then\(\)\.then\(\)": ("Promise chains", "Consider async/await"),
            r"JSON\.stringify.*deep": ("Expensive serialization", "Consider streaming"),
        },
        Language.JAVA: {
            r"new.*String\(": ("Inefficient string", "Use literals or StringBuilder"),
            r"\.clone\(\)": ("Expensive clone", "Consider other approaches"),
            r"synchronized": ("Lock contention", "Consider better concurrency"),
        },
    }

    @staticmethod
    def detect_language(code: str, filename: str = "") -> Language:
        """
        Detect programming language from code content or filename.
        """
        import re
        
        # Check filename first
        if filename:
            ext = filename.lower().split('.')[-1]
            ext_map = {
                'py': Language.PYTHON,
                'js': Language.JAVASCRIPT,
                'ts': Language.TYPESCRIPT,
                'java': Language.JAVA,
                'go': Language.GO,
                'rs': Language.RUST,
                'cs': Language.CSHARP,
                'php': Language.PHP,
                'rb': Language.RUBY,
                'kt': Language.KOTLIN,
            }
            if ext in ext_map:
                return ext_map[ext]

        # Detect from language-specific keywords/patterns
        patterns = {
            Language.PYTHON: r'(^import |^from |def |class |@|\.py$)',
            Language.JAVASCRIPT: r'(const |let |var |=>|async |function \()',
            Language.TYPESCRIPT: r'(interface |type .*=|:\s*\w+\s*[=;,)])',
            Language.JAVA: r'(public class |package |import java\.)',
            Language.GO: r'(^package |^import \(|func \(.*\) \{)',
            Language.RUST: r'(fn |impl |trait |async fn|unsafe \{)',
        }
        
        for lang, pattern in patterns.items():
            if re.search(pattern, code, re.MULTILINE):
                return lang
        
        return Language.PYTHON  # Default
    
    @staticmethod
    def get_language_config(language: Language) -> LanguageConfig:
        """Get configuration for specific language."""
        return LANGUAGE_CONFIGS.get(language, LANGUAGE_CONFIGS[Language.PYTHON])
    
    @classmethod
    def analyze_with_patterns(
        cls, 
        code: str, 
        language: Language, 
        pattern_type: str = "security"
    ) -> Dict[str, Any]:
        """
        Analyze code using language-specific patterns.
        """
        import re
        
        patterns = cls.SECURITY_PATTERNS if pattern_type == "security" else cls.PERFORMANCE_PATTERNS
        
        if language not in patterns:
            return {"issues": [], "message": f"No {pattern_type} patterns for {language.value}"}
        
        issues = []
        lang_patterns = patterns[language]
        
        for pattern, (issue_name, suggestion) in lang_patterns.items():
            matches = list(re.finditer(pattern, code, re.MULTILINE))
            if matches:
                for match in matches:
                    line_no = code[:match.start()].count('\n') + 1
                    issues.append({
                        "type": issue_name,
                        "suggestion": suggestion,
                        "line": line_no,
                        "pattern": pattern,
                    })
        
        return {
            "issues": issues,
            "total": len(issues),
            "severity": "HIGH" if len(issues) > 3 else ("MEDIUM" if len(issues) > 0 else "LOW"),
        }


class MultiLanguageAnalyzer:
    """
    Universal code analyzer that adapts to different languages.
    """
    
    def __init__(self):
        self.switcher = LanguageSwitcher()
        self.cache = {}
    
    def analyze(
        self, 
        code: str, 
        language: Optional[Language] = None,
        filename: str = "",
    ) -> Dict[str, Any]:
        """
        Analyze code across multiple languages.
        """
        # Auto-detect language if not provided
        if not language:
            language = self.switcher.detect_language(code, filename)
        
        config = self.switcher.get_language_config(language)
        
        # Run multi-level analysis
        security_issues = self.switcher.analyze_with_patterns(code, language, "security")
        performance_issues = self.switcher.analyze_with_patterns(code, language, "performance")
        
        # Combine results
        all_issues = security_issues["issues"] + performance_issues["issues"]
        
        # Calculate quality score (0-100)
        issue_count = len(all_issues)
        lines_of_code = len(code.split('\n'))
        quality_score = max(0, 100 - (issue_count * 5) - (lines_of_code // 10))
        
        return {
            "language": language.value,
            "config": {
                "type_safe": config.type_safe,
                "async_native": config.async_native,
                "frameworks": config.frameworks[:3],
                "testing_frameworks": config.testing_frameworks[:2],
            },
            "quality_score": quality_score,
            "total_issues": issue_count,
            "security_issues": security_issues["issues"],
            "performance_issues": performance_issues["issues"],
            "recommendations": {
                "use_typing": not config.type_safe,
                "use_async": config.async_native,
                "suggested_frameworks": config.frameworks[:2],
            }
        }
    
    def generate_boilerplate(
        self,
        language: Language,
        project_type: str = "api",
    ) -> str:
        """
        Generate boilerplate code for a language and project type.
        """
        boilerplate_templates = {
            (Language.PYTHON, "api"): '''# FastAPI Project Boilerplate
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/items/")
async def create_item(item: Item):
    return item
''',
            (Language.JAVASCRIPT, "api"): '''// Express.js Project Boilerplate
import express from 'express';

const app = express();
app.use(express.json());

app.get('/', (req, res) => {
  res.json({ message: 'Hello World' });
});

app.post('/items', (req, res) => {
  const item = req.body;
  res.json(item);
});

app.listen(3000, () => console.log('Server ready'));
''',
            (Language.TYPESCRIPT, "api"): '''// NestJS Project Boilerplate
import { Controller, Get, Post, Body } from '@nestjs/common';

interface Item {
  name: string;
  description?: string;
}

@Controller()
export class AppController {
  @Get()
  getHello(): { message: string } {
    return { message: 'Hello World' };
  }

  @Post('items')
  createItem(@Body() item: Item): Item {
    return item;
  }
}
''',
            (Language.GO, "api"): '''// Gin Project Boilerplate
package main

import (
\t"github.com/gin-gonic/gin"
)

type Item struct {
\tName        string `json:"name"`
\tDescription string `json:"description"`
}

func main() {
\trouter := gin.Default()

\trouter.GET("/", func(c *gin.Context) {
\t\tc.JSON(200, gin.H{"message": "Hello World"})
\t})

\trouter.POST("/items", func(c *gin.Context) {
\t\tvar item Item
\t\tc.BindJSON(&item)
\t\tc.JSON(200, item)
\t})

\trouter.Run(":3000")
}
''',
            (Language.RUST, "api"): '''// Actix-web Project Boilerplate
use actix_web::{web, App, HttpServer, HttpResponse};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct Item {
    pub name: String,
    pub description: Option<String>,
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/", web::get().to(hello))
            .route("/items", web::post().to(create_item))
    })
    .bind("127.0.0.1:3000")?
    .run()
    .await
}

async fn hello() -> HttpResponse {
    HttpResponse::Ok().json(serde_json::json!({"message": "Hello World"}))
}

async fn create_item(item: web::Json<Item>) -> HttpResponse {
    HttpResponse::Ok().json(item.into_inner())
}
''',
        }
        
        config = self.switcher.get_language_config(language)
        template_key = (language, project_type)
        
        if template_key in boilerplate_templates:
            return boilerplate_templates[template_key]
        
        return f"# {config.name} {project_type.title()} Project Boilerplate\n# Frameworks: {', '.join(config.frameworks[:3])}"

    @staticmethod
    def get_language_config(language: Language) -> LanguageConfig:
        """Get configuration for a language."""
        return LANGUAGE_CONFIGS.get(language)

    @staticmethod
    def suggest_framework(language: Language) -> str:
        """Suggest best framework for language."""
        config = LANGUAGE_CONFIGS.get(language)
        if config:
            return config.frameworks[0]
        return ""

    @staticmethod
    def get_security_patterns(language: Language) -> Dict[str, Tuple[str, str]]:
        """Get security patterns for a language."""
        return LanguageSwitcher.SECURITY_PATTERNS.get(language, {})

    @staticmethod
    def get_performance_patterns(language: Language) -> Dict[str, Tuple[str, str]]:
        """Get performance patterns for a language."""
        return LanguageSwitcher.PERFORMANCE_PATTERNS.get(language, {})

    @staticmethod
    def analyze_language_specific(code: str, language: Language) -> Dict[str, Any]:
        """
        Perform language-specific analysis.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Language-specific insights
        """
        config = LANGUAGE_CONFIGS.get(language)
        if not config:
            return {"language": str(language), "insights": []}

        insights = {
            "language": config.name,
            "type_safe": config.type_safe,
            "async_native": config.async_native,
            "recommended_frameworks": config.frameworks,
            "recommended_orms": config.orms,
            "insights": []
        }

        # Check for type hints/annotations
        if config.type_safe and language == Language.PYTHON:
            if ":" not in code or "->" not in code:
                insights["insights"].append("Consider adding type hints for better IDE support")
        elif config.type_safe and language in (Language.TYPESCRIPT, Language.JAVA, Language.GO):
            if "any" in code.lower():
                insights["insights"].append("Avoid 'any' type - use specific types")

        # Check async patterns
        if config.async_native:
            if language in (Language.PYTHON, Language.JAVASCRIPT):
                if "sleep" in code and "async" not in code:
                    insights["insights"].append("Consider async/await for better concurrency")

        return insights


def get_language_switcher() -> LanguageSwitcher:
    """Get language switcher instance."""
    return LanguageSwitcher()
