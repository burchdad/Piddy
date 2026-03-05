"""Security analysis and best practices tools."""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class SecurityLevel(str, Enum):
    """Security threat levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityFinding:
    """Represents a security finding."""
    level: SecurityLevel
    category: str
    title: str
    description: str
    recommendation: str
    code_example: str = ""


def analyze_security(code: str, language: str = "python") -> Dict[str, Any]:
    """Comprehensive security analysis of code."""
    
    findings = []
    score = 100
    
    # Check for common vulnerabilities
    findings.extend(_check_injection_vulnerabilities(code, language))
    findings.extend(_check_authentication_issues(code, language))
    findings.extend(_check_data_exposure(code, language))
    findings.extend(_check_dependency_issues(code, language))
    findings.extend(_check_input_validation(code, language))
    
    # Calculate security score
    for finding in findings:
        if finding.level == SecurityLevel.CRITICAL:
            score -= 25
        elif finding.level == SecurityLevel.HIGH:
            score -= 10
        elif finding.level == SecurityLevel.MEDIUM:
            score -= 5
        elif finding.level == SecurityLevel.LOW:
            score -= 2
    
    score = max(0, score)
    
    return {
        "language": language,
        "findings": [
            {
                "level": f.level.value,
                "category": f.category,
                "title": f.title,
                "description": f.description,
                "recommendation": f.recommendation,
                "example": f.code_example,
            }
            for f in findings
        ],
        "security_score": score,
        "grade": _get_security_grade(score),
        "total_findings": len(findings),
    }


def _check_injection_vulnerabilities(code: str, language: str) -> List[SecurityFinding]:
    """Check for SQL injection and other injection attacks."""
    findings = []
    
    if language == "python":
        if ".format(" in code and "select" in code.lower():
            findings.append(SecurityFinding(
                level=SecurityLevel.CRITICAL,
                category="SQL Injection",
                title="Potential SQL Injection via string formatting",
                description="Using .format() or f-strings with SQL queries is vulnerable to injection",
                recommendation="Use parameterized queries with ? placeholders",
                code_example="""# VULNERABLE
query = f"SELECT * FROM users WHERE id = {user_id}"

# SAFE
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
"""
            ))
        
        if "os.system(" in code or "subprocess.call(" in code:
            findings.append(SecurityFinding(
                level=SecurityLevel.CRITICAL,
                category="Command Injection",
                title="Command injection vulnerability detected",
                description="Using os.system() or similar with user input is dangerous",
                recommendation="Use subprocess with list arguments or safer alternatives",
                code_example="""# VULNERABLE
os.system(f"rm {filename}")

# SAFE
subprocess.run(["rm", filename])
"""
            ))
    
    elif language in ["javascript", "typescript"]:
        if ".innerHTML =" in code or "innerHTML =" in code:
            findings.append(SecurityFinding(
                level=SecurityLevel.HIGH,
                category="XSS (Cross-Site Scripting)",
                title="Direct innerHTML assignment detected",
                description="Using innerHTML with unsanitized content can lead to XSS attacks",
                recommendation="Use textContent or sanitize HTML properly",
                code_example="""// VULNERABLE
element.innerHTML = userInput;

// SAFE
element.textContent = userInput;
// or use DOMPurify for HTML content
element.innerHTML = DOMPurify.sanitize(userInput);
"""
            ))
        
        if "eval(" in code:
            findings.append(SecurityFinding(
                level=SecurityLevel.CRITICAL,
                category="Code Injection",
                title="eval() usage detected",
                description="eval() is dangerous and can execute arbitrary code",
                recommendation="Avoid eval(). Use safer parsing methods",
                code_example="""// VULNERABLE
const result = eval(userCode);

// SAFE
const result = JSON.parse(userCode);  // for JSON
"""
            ))
    
    return findings


def _check_authentication_issues(code: str, language: str) -> List[SecurityFinding]:
    """Check for authentication and authorization issues."""
    findings = []
    
    if "password" in code.lower() and "md5" in code.lower():
        findings.append(SecurityFinding(
            level=SecurityLevel.CRITICAL,
            category="Weak Hashing",
            title="MD5 used for password hashing (VULNERABLE)",
            description="MD5 is cryptographically broken and unsuitable for password hashing",
            recommendation="Use bcrypt, scrypt, or PBKDF2",
            code_example="""# VULNERABLE
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()

# SAFE
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
"""
        ))
    
    if "password" in code.lower() and ("==" in code or "=" in code) and "secret" not in code.lower():
        if "hardcode" not in code.lower() and "TODO" not in code:
            findings.append(SecurityFinding(
                level=SecurityLevel.HIGH,
                category="Hardcoded Credentials",
                title="Potential hardcoded credentials detected",
                description="Credentials should not be hardcoded in source code",
                recommendation="Use environment variables or secure vaults",
                code_example="""# VULNERABLE
PASSWORD = "mypassword123"

# SAFE
import os
PASSWORD = os.getenv("DB_PASSWORD")
"""
            ))
    
    return findings


def _check_data_exposure(code: str, language: str) -> List[SecurityFinding]:
    """Check for data exposure issues."""
    findings = []
    
    if language == "python":
        if "print(" in code and ("password" in code.lower() or "secret" in code.lower()):
            findings.append(SecurityFinding(
                level=SecurityLevel.HIGH,
                category="Sensitive Data Exposure",
                title="Sensitive data logged or printed",
                description="Passwords, tokens, or secrets are being logged",
                recommendation="Never log sensitive data; use placeholder messages",
                code_example="""# VULNERABLE
print(f"User logged in with password: {password}")

# SAFE
print("User logged in successfully")
logger.debug(f"User {user_id} authenticated")
"""
            ))
    
    elif language in ["javascript", "typescript"]:
        if "console.log" in code and ("password" in code.lower() or "token" in code.lower()):
            findings.append(SecurityFinding(
                level=SecurityLevel.HIGH,
                category="Sensitive Data Exposure",
                title="Sensitive data logged to console",
                description="Tokens or credentials in console output",
                recommendation="Remove console logs with sensitive data",
                code_example="""// VULNERABLE
console.log('Token:', authToken);

// SAFE
console.log('Authentication successful');
"""
            ))
    
    return findings


def _check_dependency_issues(code: str, language: str) -> List[SecurityFinding]:
    """Check for dependency and library issues."""
    findings = []
    
    if language == "javascript":
        if "require(" in code and ("old-library" in code or "mongoose" in code and "mongoose@2" in code):
            findings.append(SecurityFinding(
                level=SecurityLevel.MEDIUM,
                category="Outdated Dependencies",
                title="Potentially outdated dependency detected",
                description="Using old library versions with known vulnerabilities",
                recommendation="Update to latest stable version; use 'npm audit' to check",
                code_example="""# Run to check vulnerabilities
npm audit
npm update

# Or update specific package
npm install package@latest
"""
            ))
    
    return findings


def _check_input_validation(code: str, language: str) -> List[SecurityFinding]:
    """Check for input validation issues."""
    findings = []
    
    if language == "python":
        if "def " in code and "request" in code and ":" not in code.split("request")[1][:5]:
            findings.append(SecurityFinding(
                level=SecurityLevel.MEDIUM,
                category="Missing Input Validation",
                title="Input validation may be missing",
                description="Request parameters should be validated before use",
                recommendation="Validate and sanitize all user inputs",
                code_example="""# VULNERABLE
@app.post("/user")
def create_user(data: dict):
    # Assumes data is valid
    user = User(**data)

# SAFE
from pydantic import BaseModel, validator

class UserCreate(BaseModel):
    email: str
    age: int
    
    @validator('email')
    def email_valid(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
"""
            ))
    
    return findings


def _get_security_grade(score: int) -> str:
    """Convert security score to grade."""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


def get_security_recommendations(technology_stack: str) -> Dict[str, List[str]]:
    """Get security recommendations based on tech stack."""
    
    recommendations = {
        "authentication": [],
        "data_protection": [],
        "api_security": [],
        "infrastructure": [],
        "deployment": [],
    }
    
    if "python" in technology_stack.lower():
        recommendations["authentication"].extend([
            "Use python-jose for JWT handling",
            "Implement OAuth2 with proper scopes",
            "Use argon2 or bcrypt for password hashing",
        ])
    
    if "fastapi" in technology_stack.lower():
        recommendations["api_security"].extend([
            "Enable HTTPS only (no HTTP in production)",
            "Use CORS middleware carefully",
            "Implement rate limiting",
            "Add API key validation",
        ])
    
    if "database" in technology_stack.lower():
        recommendations["data_protection"].extend([
            "Use parameterized queries to prevent SQL injection",
            "Enable database encryption at rest",
            "Implement row-level security where needed",
            "Regular database backups and testing",
        ])
    
    recommendations["infrastructure"].extend([
        "Keep systems patched and updated",
        "Use firewalls and security groups",
        "Implement WAF (Web Application Firewall)",
        "Use secrets management (not environment variables for production)",
    ])
    
    recommendations["deployment"].extend([
        "Use HTTPS/TLS certificates",
        "Implement proper logging and monitoring",
        "Use container security scanning",
        "Regular security audits and penetration testing",
    ])
    
    return recommendations
