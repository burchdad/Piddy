"""
Local Self-Healing Engine for Piddy
Autonomous fix system with NO external AI dependencies
Uses pattern-based analysis and rule-based fixing
"""

import logging
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import asyncio
import datetime

logger = logging.getLogger(__name__)


@dataclass
class CodeIssue:
    """Represents a code issue to be fixed."""
    file_path: str
    line_number: int
    issue_type: str
    severity: str
    description: str
    pattern: str
    replacement: str


class LocalFixEngine:
    """Self-contained fix engine with NO external AI calls."""
    
    def __init__(self):
        """Initialize the fix engine."""
        self.issues_fixed = 0
        self.files_modified = []
        
    async def analyze_and_fix_codebase(self) -> Dict[str, Any]:
        """
        Analyze AND fix codebase without external AI.
        Uses deterministic pattern matching and rules.
        """
        logger.info("🔧 Local Self-Healing Engine Started (NO AI CALLS)")
        
        results = {
            "issues_fixed": 0,
            "files_modified": [],
            "fixes": []
        }
        
        # Scan Python files
        python_files = list(Path(".").rglob("*.py"))
        python_files = [f for f in python_files if not str(f).startswith("./venv")]
        
        logger.info(f"📁 Scanning {len(python_files)} Python files...")
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply all fixes
                original_content = content
                
                # Fix 1: Print statements → logging
                content, print_fixes = self._fix_print_statements(str(file_path), content)
                results["fixes"].extend(print_fixes)
                
                # Fix 2: Broad exceptions
                content, except_fixes = self._fix_broad_exceptions(str(file_path), content)
                results["fixes"].extend(except_fixes)
                
                # Fix 3: Mock data removal
                content, mock_fixes = self._remove_mock_data(str(file_path), content)
                results["fixes"].extend(mock_fixes)
                
                # Fix 4: Hardcoded values
                content, hardcode_fixes = self._fix_hardcoded_values(str(file_path), content)
                results["fixes"].extend(hardcode_fixes)
                
                # Fix 5: Missing imports
                content, import_fixes = self._fix_missing_imports(str(file_path), content)
                results["fixes"].extend(import_fixes)
                
                # If content changed, write it back
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    results["files_modified"].append(str(file_path))
                    results["issues_fixed"] += len(print_fixes) + len(except_fixes) + len(mock_fixes) + len(hardcode_fixes) + len(import_fixes)
                    
                    logger.info(f"  ✅ Fixed {str(file_path)}")
                    
            except Exception as e:
                logger.error(f"  ❌ Error processing {file_path}: {e}")
        
        logger.info(f"\n🎉 Self-Healing Complete!")
        logger.info(f"   Files Modified: {len(results['files_modified'])}")
        logger.info(f"   Total Fixes: {results['issues_fixed']}")
        
        return results
    
    def _fix_print_statements(self, file_path: str, content: str) -> Tuple[str, List[Dict]]:
        """Replace print() with logging.info()."""
        fixes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Match print statements (but not in strings/comments)
            if re.search(r'^\s*print\s*\(', line) and not line.strip().startswith('#'):
                # Extract print content
                original = line
                match = re.search(r'print\s*\((.*)\)', line)
                
                if match:
                    print_args = match.group(1)
                    
                    # Convert to logging
                    indent = len(line) - len(line.lstrip())
                    new_line = ' ' * indent + f'logger.info({print_args})'
                    lines[i] = new_line
                    
                    fixes.append({
                        "file": file_path,
                        "line": i + 1,
                        "type": "replace_print",
                        "before": original.strip(),
                        "after": new_line.strip()
                    })
        
        return '\n'.join(lines), fixes
    
    def _fix_broad_exceptions(self, file_path: str, content: str) -> Tuple[str, List[Dict]]:
        """Fix overly broad exception handlers."""
        fixes = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            except (ValueError, TypeError, RuntimeError, HTTPError) as e:
            if re.search(r'except\s*:\s*$', line) or re.search(r'except\s+Exception\s*:\s*', line):
                original = line
                indent = len(line) - len(line.lstrip())
                
                # Replace with specific exceptions
                new_line = ' ' * indent + 'except (ValueError, TypeError, RuntimeError, HTTPError) as e:'
                lines[i] = new_line
                
                fixes.append({
                    "file": file_path,
                    "line": i + 1,
                    "type": "specific_exception",
                    "before": original.strip(),
                    "after": new_line.strip()
                })
        
        return '\n'.join(lines), fixes
    
    def _remove_mock_data(self, file_path: str, content: str) -> Tuple[str, List[Dict]]:
        """Remove hardcoded mock data."""
        fixes = []
        
        # Pattern 1: Remove MockDataGenerator usage
        if 'MockDataGenerator' in content:
            original = content
            content = content.replace('', '')
            content = re.sub(r'MockDataGenerator\.\w+\(\)', 'get_from_database()', content)
            
            fixes.append({
                "file": file_path,
                "type": "remove_mock_generator",
                "description": "Removed MockDataGenerator - will use live database"
            })
        
        # Pattern 2: Remove hardcoded status
        if '"decisions_pending": get_pending_count()' in content:
            content = content.replace('"decisions_pending": get_pending_count()', '"decisions_pending": get_pending_count()')
            fixes.append({
                "file": file_path,
                "type": "remove_hardcoded_count",
                "description": "Made decisions_pending dynamic"
            })
        
        # Pattern 3: Remove mock return statements
        mock_patterns = [
            (r'return \[\s*{\s*"[\w_]+"\s*:\s*"[\w\s]+"\s*,', 'return get_from_database()'),
            (r'MissionReplayData\(\)', 'get_mission_replay_from_db()'),
            (r'DependencyGraph\(\)', 'get_dependency_graph_from_db()'),
        ]
        
        for pattern, replacement in mock_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                fixes.append({
                    "file": file_path,
                    "type": "remove_mock_pattern",
                    "description": f"Replaced mock pattern: {pattern}"
                })
        
        return content, fixes
    
    def _fix_hardcoded_values(self, file_path: str, content: str) -> Tuple[str, List[Dict]]:
        """Fix hardcoded configuration values."""
        fixes = []
        
        # Pattern: Replace hardcoded URLs with environment variables
        url_pattern = r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)'
        urls = re.findall(url_pattern, content)
        
        for url in urls:
            if 'localhost' in url or '127.0.0.1' in url:
                # Replace with config
                content = content.replace(
                    url,
                    f'get_config().{url.replace("http://", "").replace("https://", "").split("/")[0]}'
                )
                fixes.append({
                    "file": file_path,
                    "type": "hardcoded_url",
                    "before": url,
                    "after": "get_config().api_url"
                })
        
        # Pattern: Replace hardcoded API keys/tokens
        secret_patterns = [
            (r'api_key\s*=\s*["\'][\w\-]+["\']', 'api_key = get_config().api_key'),
            (r'token\s*=\s*["\'][\w\-]+["\']', 'token = get_config().token'),
            (r'password\s*=\s*["\'][\w\-]+["\']', 'password = get_config().password'),
        ]
        
        for pattern, replacement in secret_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                fixes.append({
                    "file": file_path,
                    "type": "hardcoded_secret",
                    "description": "Moved secret to config"
                })
        
        return content, fixes
    
    def _fix_missing_imports(self, file_path: str, content: str) -> Tuple[str, List[Dict]]:
        """Add missing imports."""
        fixes = []
        
        # Check if logging is used but not imported
        if 'logger.' in content and 'import logging' not in content:
            lines = content.split('\n')
            # Find the right place to add import (after other imports)
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_pos = i + 1
            
            lines.insert(insert_pos, 'import logging')
            lines.insert(insert_pos + 1, 'logger = logging.getLogger(__name__)')
            content = '\n'.join(lines)
            
            fixes.append({
                "file": file_path,
                "type": "add_logging_import",
                "description": "Added missing logging import"
            })
        
        # Check for other missing imports
        missing_imports = {
            'asyncio': r'async\s+def|await\s+',
            'json': r'json\.',
            'os': r'os\.',
            'sys': r'sys\.',
            'datetime': r'datetime\.|timedelta',
        }
        
        for module, pattern in missing_imports.items():
            if re.search(pattern, content) and f'import {module}' not in content:
                lines = content.split('\n')
                # Add import at top of other imports
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_pos = i + 1
                
                lines.insert(insert_pos, f'import {module}')
                content = '\n'.join(lines)
                
                fixes.append({
                    "file": file_path,
                    "type": "add_import",
                    "module": module
                })
        
        return content, fixes


async def run_local_self_healing() -> Dict[str, Any]:
    """
    Run complete local self-healing WITHOUT external AI.
    This is the core autonomous self-fixing engine.
    """
    logger.info("=" * 60)
    logger.info("🤖 PIDDY LOCAL SELF-HEALING ENGINE")
    logger.info("   NO External AI • NO API Calls • Offline Capable")
    logger.info("=" * 60)
    
    engine = LocalFixEngine()
    
    try:
        # Analyze and fix
        results = await engine.analyze_and_fix_codebase()
        
        # Compile summary
        summary = {
            "status": "success",
            "engine": "local_self_healing",
            "uses_external_ai": False,
            "offline_capable": True,
            "files_scanned": len(list(Path(".").rglob("*.py"))),
            "files_modified": len(results["files_modified"]),
            "total_fixes": results["issues_fixed"],
            "fixes_by_type": {
                "print_to_logging": sum(1 for f in results["fixes"] if f.get("type") == "replace_print"),
                "exception_handling": sum(1 for f in results["fixes"] if f.get("type") == "specific_exception"),
                "mock_data_removal": sum(1 for f in results["fixes"] if f.get("type") == "remove_mock_generator"),
                "hardcoded_values": sum(1 for f in results["fixes"] if f.get("type") == "hardcoded_url"),
                "missing_imports": sum(1 for f in results["fixes"] if f.get("type") == "add_import"),
            },
            "modified_files": results["files_modified"],
            "all_fixes": results["fixes"],
            "next_step": "Commit changes and deploy"
        }
        
        logger.info("\n✅ LOCAL SELF-HEALING COMPLETE")
        logger.info(f"   Files Modified: {summary['files_modified']}")
        logger.info(f"   Total Fixes Applied: {summary['total_fixes']}")
        logger.info(f"   Print→Logging: {summary['fixes_by_type']['print_to_logging']}")
        logger.info(f"   Exception handlers: {summary['fixes_by_type']['exception_handling']}")
        logger.info(f"   Mock data removed: {summary['fixes_by_type']['mock_data_removal']}")
        logger.info(f"   Hardcoded values: {summary['fixes_by_type']['hardcoded_values']}")
        logger.info(f"   Missing imports: {summary['fixes_by_type']['missing_imports']}")
        
        return summary
        
    except Exception as e:
        logger.error(f"❌ Error during self-healing: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# For backwards compatibility
async def local_self_heal() -> Dict[str, Any]:
    """Alias for run_local_self_healing()."""
    return await run_local_self_healing()
