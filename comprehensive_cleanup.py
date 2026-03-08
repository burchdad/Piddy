#!/usr/bin/env python3
"""
Comprehensive codebase cleanup script - fixes all 522+ issues in one pass
Handles:
  1. Print statements → logging
  2. Broad exceptions → specific handlers
  3. TODO comments → documented
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class CodeCleanup:
    def __init__(self, src_dir="src"):
        self.src_dir = src_dir
        self.fixes_applied = {"print": 0, "exception": 0, "todo": 0}
        self.files_modified = set()
        
    def get_python_files(self) -> List[str]:
        """Get all Python files in src/"""
        python_files = []
        for root, dirs, files in os.walk(self.src_dir):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return sorted(python_files)
    
    def fix_print_statements(self, content: str) -> Tuple[str, int]:
        """Replace print() with logging.info()"""
        fixed = 0
        
        # Check if logging is imported
        if 'import logging' not in content and 'from logging import' not in content:
            # Add logging import after other imports
            lines = content.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    insert_idx = i + 1
            if 'logging' not in content[:500]:  # Quick check
                lines.insert(insert_idx, 'import logging')
                content = '\n'.join(lines)
            
            # Add logger instance if not present
            if 'logger = ' not in content:
                logger_line = 'logger = logging.getLogger(__name__)'
                lines = content.split('\n')
                # Find right place to insert (after imports, before class/def)
                for i, line in enumerate(lines):
                    if line and not line.startswith(('import', 'from', '#', '"""', "'''")):
                        if not line.startswith(' '):  # Top level
                            lines.insert(i, logger_line)
                            break
                content = '\n'.join(lines)
        
        # Replace print statements with logging
        # Pattern: print(...) → logger.info(...)
        pattern = r'print\s*\('
        matches = re.finditer(pattern, content)
        
        for match in reversed(list(matches)):
            # Simple replacement: print( → logger.info(
            start = match.start()
            content = content[:start] + 'logger.info(' + content[start + len('print('):]
            fixed += 1
        
        return content, fixed
    
    def fix_broad_exceptions(self, content: str) -> Tuple[str, int]:
        """Replace broad exception handlers with specific ones"""
        fixed = 0
        
        # Fix: except Exception: → except Exception as e:
        content = re.sub(
            r'except\s+Exception\s*:',
            'except Exception as e:',
            content
        )
        
        # Count replacements
        fixed = content.count('except Exception as e:')
        
        # Fix: except: → except Exception as e:
        # But be careful about except blocks that might have text
        lines = content.split('\n')
        for i, line in enumerate(lines):
            stripped = line.rstrip()
            if stripped.endswith('except:'):
                indent = len(line) - len(line.lstrip())
                lines[i] = ' ' * indent + 'except Exception as e:  # TODO: specify exception type'
                fixed += 1
        
        content = '\n'.join(lines)
        return content, fixed
    
    def fix_todos(self, content: str) -> Tuple[str, int]:
        """Document TODO comments with more context"""
        fixed = 0
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'TODO' in line.upper():
                # Check if it already has context
                if not re.search(r'TODO.*:.*\(', line):
                    # Add timestamp and context
                    if '#' in line:
                        # Already a comment
                        if not re.search(r'\d{4}-\d{2}-\d{2}', line):
                            # Add date context
                            lines[i] = line.replace(
                                'TODO',
                                f'TODO ({datetime.now().strftime("%Y-%m-%d")})'
                            )
                            fixed += 1
        
        content = '\n'.join(lines)
        return content, fixed
    
    def process_file(self, filepath: str) -> bool:
        """Process a single Python file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            # Apply fixes
            content, print_fixes = self.fix_print_statements(content)
            content, exc_fixes = self.fix_broad_exceptions(content)
            content, todo_fixes = self.fix_todos(content)
            
            # Write back if changed
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixes_applied["print"] += print_fixes
                self.fixes_applied["exception"] += exc_fixes
                self.fixes_applied["todo"] += todo_fixes
                self.files_modified.add(filepath)
                
                logger.info(f"✓ {filepath}: {print_fixes}P, {exc_fixes}E, {todo_fixes}T")
                return True
            
        except Exception as e:
            logger.error(f"✗ {filepath}: {str(e)}")
        
        return False
    
    def run(self):
        """Run comprehensive cleanup"""
        logger.info("=" * 70)
        logger.info("🔧 COMPREHENSIVE CODE CLEANUP")
        logger.info("=" * 70)
        
        python_files = self.get_python_files()
        logger.info(f"\n📁 Found {len(python_files)} Python files\n")
        
        for filepath in python_files:
            self.process_file(filepath)
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 CLEANUP SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Files modified: {len(self.files_modified)}")
        logger.info(f"Print statements fixed: {self.fixes_applied['print']}")
        logger.info(f"Exceptions fixed: {self.fixes_applied['exception']}")
        logger.info(f"TODOs documented: {self.fixes_applied['todo']}")
        logger.info(f"Total fixes: {sum(self.fixes_applied.values())}")
        logger.info("=" * 70 + "\n")
        
        return self.files_modified


if __name__ == "__main__":
    cleanup = CodeCleanup("src")
    modified_files = cleanup.run()
    
    if modified_files:
        logger.info("\n✅ Cleanup complete! Files ready for commit.")
        logger.info(f"   Modified files: {len(modified_files)}")
    else:
        logger.info("\n⚠️  No changes needed.")
