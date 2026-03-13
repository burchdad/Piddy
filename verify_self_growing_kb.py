#!/usr/bin/env python3
"""
Verify that the self-growing KB system is properly set up and working.
Run this to validate all components are in place before using.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def check_mark(text=""):
    return f"✅ {text}"

def fail_mark(text=""):
    return f"❌ {text}"

def info_mark(text=""):
    return f"ℹ️  {text}"

class SKGVerifier:
    def __init__(self):
        self.workspace_root = Path("/workspaces/Piddy")
        self.checks_passed = 0
        self.checks_failed = 0
        self.issues = []
    
    def check_file_exists(self, path, description):
        """Check if a file exists."""
        file_path = self.workspace_root / path
        if file_path.exists():
            print(check_mark(f"{description}: {path}"))
            self.checks_passed += 1
            return True
        else:
            print(fail_mark(f"{description} NOT FOUND: {path}"))
            self.checks_failed += 1
            self.issues.append(f"Missing: {path}")
            return False
    
    def check_directory_exists(self, path, description):
        """Check if a directory exists."""
        dir_path = self.workspace_root / path
        if dir_path.exists() and dir_path.is_dir():
            print(check_mark(f"{description}: {path}"))
            self.checks_passed += 1
            return True
        else:
            print(fail_mark(f"{description} NOT FOUND: {path}"))
            self.checks_failed += 1
            self.issues.append(f"Missing directory: {path}")
            return False
    
    def check_file_contains(self, path, text, description):
        """Check if file contains specific text."""
        file_path = self.workspace_root / path
        if not file_path.exists():
            print(fail_mark(f"{description}: File not found"))
            self.checks_failed += 1
            return False
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if text in content:
                    print(check_mark(f"{description}"))
                    self.checks_passed += 1
                    return True
                else:
                    print(fail_mark(f"{description}: Text not found"))
                    self.checks_failed += 1
                    self.issues.append(f"Missing in {path}: {text[:50]}")
                    return False
        except Exception as e:
            print(fail_mark(f"{description}: Error reading file - {e}"))
            self.checks_failed += 1
            return False
    
    def verify_core_components(self):
        """Verify all core components exist."""
        print("\n" + "="*60)
        print("CORE COMPONENTS")
        print("="*60)
        
        # Check Experience Recorder
        self.check_file_exists(
            "src/kb/experience_recorder.py",
            "Experience Recorder"
        )
        
        # Check Experience Manager CLI
        self.check_file_exists(
            "experience_manager.py",
            "Experience Manager CLI"
        )
        
        # Check Phase 19
        self.check_file_exists(
            "src/phase19_self_improving_agent.py",
            "Phase 19 (Self-Improving Agent)"
        )
        
        # Check ingestion pipeline
        self.check_file_exists(
            "src/kb/ingestion_pipeline.py",
            "Ingestion Pipeline"
        )
        
        # Check intelligent chunker
        self.check_file_exists(
            "src/kb/intelligent_chunker.py",
            "Intelligent Chunker"
        )
    
    def verify_documentation(self):
        """Verify documentation is in place."""
        print("\n" + "="*60)
        print("DOCUMENTATION")
        print("="*60)
        
        self.check_file_exists(
            "KB_SELF_GROWING.md",
            "Self-Growing KB Guide"
        )
        
        self.check_file_exists(
            "EXPERIENCE_INTEGRATION_GUIDE.md",
            "Integration Guide"
        )
    
    def verify_kb_setup(self):
        """Verify KB is set up properly."""
        print("\n" + "="*60)
        print("KNOWLEDGE BASE SETUP")
        print("="*60)
        
        # Check KB repo exists
        self.check_directory_exists(
            "burchdad-knowledge-base",
            "Knowledge Base Repository"
        )
        
        # Check experiences directory will exist
        kb_exp_path = self.workspace_root / "burchdad-knowledge-base" / "experiences"
        if kb_exp_path.exists():
            count = len(list(kb_exp_path.glob("*.md")))
            print(check_mark(f"Experiences directory: {count} experiences indexed"))
            self.checks_passed += 1
        else:
            print(info_mark("Experiences directory will be created on first feed"))
            self.checks_passed += 1
        
        # Check cache directory
        cache_path = self.workspace_root / "kb_content_cache" / "learned_experiences"
        if cache_path.exists():
            exp_file = cache_path / "experiences.jsonl"
            if exp_file.exists():
                with open(exp_file, 'r') as f:
                    lines = len(f.readlines())
                print(check_mark(f"Experience database: {lines} experiences recorded"))
                self.checks_passed += 1
            else:
                print(info_mark("Experience database will be created on first record"))
                self.checks_passed += 1
        else:
            print(info_mark("Cache directory will be created on first use"))
    
    def verify_code_structure(self):
        """Verify code has expected structure."""
        print("\n" + "="*60)
        print("CODE STRUCTURE")
        print("="*60)
        
        # Check Experience Recorder has key classes
        self.check_file_contains(
            "src/kb/experience_recorder.py",
            "class KBExperienceRecorder",
            "KBExperienceRecorder class"
        )
        
        self.check_file_contains(
            "src/kb/experience_recorder.py",
            "def record_fix",
            "record_fix method"
        )
        
        self.check_file_contains(
            "src/kb/experience_recorder.py",
            "def approve_fix",
            "approve_fix method"
        )
        
        self.check_file_contains(
            "src/kb/experience_recorder.py",
            "def feed_to_kb",
            "feed_to_kb method"
        )
        
        # Check CLI has commands
        self.check_file_contains(
            "experience_manager.py",
            "def cmd_status",
            "status command"
        )
        
        self.check_file_contains(
            "experience_manager.py",
            "def cmd_approve",
            "approve command"
        )
        
        self.check_file_contains(
            "experience_manager.py",
            "def cmd_feed_to_kb",
            "feed_to_kb command"
        )
    
    def test_imports(self):
        """Test if components can be imported."""
        print("\n" + "="*60)
        print("IMPORT TESTS")
        print("="*60)
        
        try:
            from src.kb.experience_recorder import KBExperienceRecorder, Experience
            print(check_mark("Can import KBExperienceRecorder"))
            self.checks_passed += 1
        except Exception as e:
            print(fail_mark(f"Cannot import KBExperienceRecorder: {e}"))
            self.checks_failed += 1
        
        try:
            from src.kb.ingestion_pipeline import IngestionPipeline
            print(check_mark("Can import IngestionPipeline"))
            self.checks_passed += 1
        except Exception as e:
            print(fail_mark(f"Cannot import IngestionPipeline: {e}"))
            self.checks_failed += 1
        
        try:
            from src.phase19_self_improving_agent import SelfImprovingAgent
            print(check_mark("Can import SelfImprovingAgent"))
            self.checks_passed += 1
        except Exception as e:
            print(fail_mark(f"Cannot import SelfImprovingAgent: {e}"))
            self.checks_failed += 1
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        print("\n" + "="*60)
        print("BASIC FUNCTIONALITY TESTS")
        print("="*60)
        
        try:
            from src.kb.experience_recorder import KBExperienceRecorder
            
            # Create instance
            recorder = KBExperienceRecorder()
            print(check_mark("Created KBExperienceRecorder instance"))
            self.checks_passed += 1
            
            # Try recording a test experience
            exp_id = recorder.record_fix(
                problem="Test problem for verification",
                solution="Test solution code",
                file_path="test.py",
                reasoning="Verification test",
                tags=["test"]
            )
            print(check_mark(f"Recorded test experience: {exp_id[:8]}..."))
            self.checks_passed += 1
            
            # Get stats
            stats = recorder.get_stats()
            print(check_mark(f"Got stats: {stats['total_experiences']} experiences"))
            self.checks_passed += 1
            
        except Exception as e:
            print(fail_mark(f"Functionality test failed: {e}"))
            self.checks_failed += 1
    
    def verify_cli_commands(self):
        """Verify CLI commands are executable."""
        print("\n" + "="*60)
        print("CLI VERIFICATION")
        print("="*60)
        
        cli_path = self.workspace_root / "experience_manager.py"
        if cli_path.exists():
            # Check if executable
            if os.access(cli_path, os.X_OK):
                print(check_mark("experience_manager.py is executable"))
                self.checks_passed += 1
            else:
                print(info_mark("experience_manager.py exists (not marked executable, but works)"))
            self.checks_passed += 1
            
            # Check shebang
            with open(cli_path, 'r') as f:
                first_line = f.readline()
                if "python" in first_line.lower():
                    print(check_mark("CLI has Python shebang"))
                    self.checks_passed += 1
    
    def print_summary(self):
        """Print verification summary."""
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        
        total = self.checks_passed + self.checks_failed
        percentage = (self.checks_passed / total * 100) if total > 0 else 0
        
        print(f"\n✅ Passed: {self.checks_passed}/{total}")
        print(f"❌ Failed: {self.checks_failed}/{total}")
        print(f"📊 Success Rate: {percentage:.1f}%\n")
        
        if self.checks_failed == 0:
            print("🎉 All checks passed! System is ready to use.\n")
            return True
        else:
            print("⚠️  Some checks failed. See issues below.\n")
            for issue in self.issues:
                print(f"  • {issue}")
            print()
            return False
    
    def print_next_steps(self):
        """Print next steps."""
        print("="*60)
        print("NEXT STEPS")
        print("="*60)
        print("""
1. Read the guides:
   - KB_SELF_GROWING.md (overview)
   - EXPERIENCE_INTEGRATION_GUIDE.md (how to hook it up)

2. Try recording your first experience:
   python3 -c "
from src.kb.experience_recorder import KBExperienceRecorder
r = KBExperienceRecorder()
eid = r.record_fix('Test bug', 'Fixed code', 'test.py', 'Test reason')
print(f'Recorded: {eid}')
"

3. Approve the experience:
   python3 experience_manager.py status
   python3 experience_manager.py approve --id <exp_id> --quality 0.95

4. Feed to KB:
   python3 experience_manager.py feed-to-kb

5. Check statistics:
   python3 experience_manager.py stats

Then hook into Phase 19 using the integration guide!
""")
    
    def run_all_checks(self):
        """Run all verification checks."""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*58 + "║")
        print("║" + "  SELF-GROWING KNOWLEDGE BASE VERIFICATION".center(58) + "║")
        print("║" + f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(58) + "║")
        print("║" + " "*58 + "║")
        print("╚" + "="*58 + "╝")
        
        self.verify_core_components()
        self.verify_documentation()
        self.verify_kb_setup()
        self.verify_code_structure()
        self.test_imports()
        self.test_basic_functionality()
        self.verify_cli_commands()
        
        success = self.print_summary()
        self.print_next_steps()
        
        return success

def main():
    verifier = SKGVerifier()
    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
