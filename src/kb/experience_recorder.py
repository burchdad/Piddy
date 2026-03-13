"""
KB Experience Recorder - Feed Piddy's own fixes back into the Knowledge Base

Integration between self-improving agent and KB system.
When Piddy solves a problem:
1. Bug detected
2. Fix generated
3. Human approved
4. Final patch applied
5. → FEED BACK INTO KB

Piddy becomes better at fixing YOUR specific codebase over time.
"""

import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Experience:
    """A learned experience/solution from Piddy's work."""
    experience_id: str
    title: str
    problem_description: str
    solution_code: str
    context: Dict[str, Any]  # file, function, etc.
    confidence: float  # 0-1: how confident Piddy is
    approval_count: int  # How many times human approved this pattern
    file_path: str
    timestamp: str
    tags: List[str]  # "bug-fix", "optimization", "pattern", etc.
    reasoning: str  # Why this works
    success_rate: float  # 0-1: success when applied
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_chunk_text(self) -> str:
        """Convert experience to knowledge chunk format."""
        return f"""
# {self.title}

## Problem
{self.problem_description}

## Solution
```python
{self.solution_code}
```

## Context
- **File**: {self.file_path}
- **Confidence**: {self.confidence * 100:.0f}%
- **Success Rate**: {self.success_rate * 100:.0f}%
- **Applied**: {self.approval_count} times
- **Tags**: {', '.join(self.tags)}

## Reasoning
{self.reasoning}

## Pattern
{self.metadata.get('pattern', 'N/A')}

---
*Experience learned by Piddy on {self.timestamp}*
"""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'experience_id': self.experience_id,
            'title': self.title,
            'problem': self.problem_description,
            'solution': self.solution_code,
            'confidence': self.confidence,
            'success_rate': self.success_rate,
            'approval_count': self.approval_count,
            'tags': self.tags,
            'timestamp': self.timestamp,
        }


class KBExperienceRecorder:
    """Record and manage Piddy's learned experiences."""
    
    def __init__(self, kb_dir: str = "burchdad-knowledge-base",
                 cache_dir: str = "kb_content_cache"):
        """
        Initialize experience recorder.
        
        Args:
            kb_dir: Knowledge base repository directory
            cache_dir: Cache directory for experiences
        """
        self.kb_dir = Path(kb_dir)
        self.cache_dir = Path(cache_dir)
        self.experiences_dir = self.cache_dir / "learned_experiences"
        self.experiences_dir.mkdir(parents=True, exist_ok=True)
        
        # Experience storage
        self.experiences_file = self.experiences_dir / "experiences.jsonl"
        self.experiences = self._load_experiences()
        
        logger.info(f"📚 Experience Recorder initialized with {len(self.experiences)} experiences")
    
    def _load_experiences(self) -> Dict[str, Experience]:
        """Load previously saved experiences."""
        experiences = {}
        
        if not self.experiences_file.exists():
            return experiences
        
        try:
            with open(self.experiences_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        exp_id = data['experience_id']
                        experiences[exp_id] = data
        except Exception as e:
            logger.error(f"❌ Error loading experiences: {e}")
        
        return experiences
    
    def record_fix(self, problem: str, solution: str, file_path: str,
                  reasoning: str, context: Optional[Dict] = None,
                  tags: Optional[List[str]] = None,
                  confidence: float = 0.8) -> str:
        """
        Record a fix that Piddy generated.
        
        Args:
            problem: Description of the problem
            solution: The code solution
            file_path: File that was fixed
            reasoning: Why this solution works
            context: Additional context (file, function, etc.)
            tags: Tags like "bug-fix", "optimization", "pattern"
            confidence: Piddy's confidence (0-1)
            
        Returns:
            Experience ID
        """
        exp_id = self._generate_id(problem, solution, file_path)
        
        experience = Experience(
            experience_id=exp_id,
            title=self._generate_title(problem),
            problem_description=problem,
            solution_code=solution,
            file_path=file_path,
            reasoning=reasoning,
            context=context or {},
            confidence=min(confidence, 1.0),
            approval_count=0,
            tags=tags or ["auto-generated"],
            timestamp=datetime.now().isoformat(),
            success_rate=0.0  # Will update as we use it
        )
        
        # Save the experience to persistent storage
        exp_dict = asdict(experience)
        self._save_experience(exp_dict)
        
        logger.info(f"📝 Recorded fix: {experience.title}")
        
        return exp_id
    
    def approve_fix(self, experience_id: str, success: bool = True,
                   quality_score: float = 0.9) -> bool:
        """
        Human approves (or rejects) a fix.
        
        Args:
            experience_id: ID of the experience to approve
            success: Whether it worked
            quality_score: Quality of the fix (0-1)
            
        Returns:
            True if approved
        """
        if experience_id not in self.experiences:
            logger.warning(f"⚠️ Experience not found: {experience_id}")
            return False
        
        exp = self.experiences[experience_id]
        
        # Update counters
        exp['approval_count'] = exp.get('approval_count', 0) + 1
        
        if success:
            # Update success rate with exponential moving average
            old_rate = exp.get('success_rate', 0.0)
            exp['success_rate'] = 0.7 * old_rate + 0.3 * quality_score
            exp['confidence'] = min(exp.get('confidence', 0.8) + 0.05, 1.0)
            logger.info(f"✅ Fix approved: {experience_id} (success_rate: {exp['success_rate']:.2f})")
        else:
            # Decrease confidence on failure
            exp['confidence'] = max(exp.get('confidence', 0.8) - 0.1, 0.0)
            logger.warning(f"❌ Fix failed: {experience_id}")
        
        # Save updated experience
        self._save_experience(exp)
        return True
    
    def feed_to_kb(self, experience_id: str, min_confidence: float = 0.7) -> bool:
        """
        Feed a learned experience into the Knowledge Base.
        
        Args:
            experience_id: ID of experience to add to KB
            min_confidence: Only add if confidence >= this
            
        Returns:
            True if added to KB
        """
        if experience_id not in self.experiences:
            logger.warning(f"⚠️ Experience not found: {experience_id}")
            return False
        
        exp = self.experiences[experience_id]
        confidence = exp.get('confidence', 0.0)
        
        # Only add high-confidence experiences
        if confidence < min_confidence:
            logger.warning(f"⚠️ Confidence too low ({confidence:.2f}): {experience_id}")
            return False
        
        # Create markdown file for KB
        kb_experiences_dir = self.kb_dir / "experiences"
        kb_experiences_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate chunk
        chunk_text = self._experience_to_chunk(exp)
        
        # Save to KB
        chunk_file = kb_experiences_dir / f"{experience_id}.md"
        with open(chunk_file, 'w') as f:
            f.write(chunk_text)
        
        # Mark as in KB
        exp['in_kb'] = True
        exp['kb_file'] = str(chunk_file)
        self._save_experience(exp)
        
        logger.info(f"📚 Fed to KB: {experience_id}")
        return True
    
    def feed_all_approved_to_kb(self, min_approvals: int = 1,
                               min_confidence: float = 0.7) -> int:
        """
        Feed all sufficiently approved experiences to KB.
        
        Args:
            min_approvals: Only add if approved at least this many times
            min_confidence: Only add if confidence >= this
            
        Returns:
            Number added to KB
        """
        added = 0
        
        for exp_id, exp in self.experiences.items():
            if exp.get('in_kb'):
                continue  # Already in KB
            
            approvals = exp.get('approval_count', 0)
            confidence = exp.get('confidence', 0.0)
            
            if approvals >= min_approvals and confidence >= min_confidence:
                if self.feed_to_kb(exp_id, min_confidence):
                    added += 1
        
        logger.info(f"📚 Fed {added} experiences to KB")
        return added
    
    def get_experiences_by_tag(self, tag: str) -> List[Dict]:
        """Get all experiences with a specific tag."""
        return [
            exp for exp in self.experiences.values()
            if tag in exp.get('tags', [])
        ]
    
    def get_high_value_experiences(self, min_confidence: float = 0.8,
                                  min_approvals: int = 2) -> List[Dict]:
        """Get high-value experiences ready for KB."""
        return [
            exp for exp in self.experiences.values()
            if exp.get('confidence', 0.0) >= min_confidence
            and exp.get('approval_count', 0) >= min_approvals
            and not exp.get('in_kb', False)
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about recorded experiences."""
        total = len(self.experiences)
        in_kb = len([e for e in self.experiences.values() if e.get('in_kb')])
        approved = len([e for e in self.experiences.values() if e.get('approval_count', 0) > 0])
        high_confidence = len([e for e in self.experiences.values() if e.get('confidence', 0.0) >= 0.8])
        
        avg_success = 0.0
        if approved > 0:
            avg_success = sum(e.get('success_rate', 0.0) for e in self.experiences.values()) / total
        
        return {
            'total_experiences': total,
            'in_kb': in_kb,
            'approved': approved,
            'high_confidence': high_confidence,
            'avg_success_rate': avg_success,
            'approval_rate': approved / total if total > 0 else 0.0,
        }
    
    def _save_experience(self, experience: Dict):
        """Save an experience to file."""
        self.experiences[experience['experience_id']] = experience
        
        with open(self.experiences_file, 'a') as f:
            f.write(json.dumps(experience) + '\n')
    
    def _generate_id(self, problem: str, solution: str, file_path: str) -> str:
        """Generate unique ID for an experience."""
        combined = f"{problem}{solution}{file_path}{datetime.now().isoformat()}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def _generate_title(self, problem: str) -> str:
        """Generate title from problem description."""
        # Take first 60 chars and clean up
        title = problem[:60].strip()
        if len(problem) > 60:
            title += "..."
        return title
    
    def _experience_to_chunk(self, experience: Dict) -> str:
        """Convert experience to markdown chunk for KB."""
        return f"""# {experience['title']}

## Problem
{experience['problem_description']}

## Solution
```python
{experience['solution_code']}
```

## Context
- **File**: {experience['file_path']}
- **Confidence**: {experience.get('confidence', 0.0) * 100:.0f}%
- **Success Rate**: {experience.get('success_rate', 0.0) * 100:.0f}%
- **Applied Successfully**: {experience.get('approval_count', 0)} times
- **Tags**: {', '.join(experience.get('tags', []))}

## How It Works
{experience['reasoning']}

## Pattern
{experience.get('context', {}).get('pattern', 'General pattern')}

---
*Learned experience from Piddy on {experience['timestamp']}*
"""


class ExperienceIntegrator:
    """Integrate learned experiences into the ingestion pipeline."""
    
    def __init__(self, recorder: KBExperienceRecorder):
        """Initialize with experience recorder."""
        self.recorder = recorder
    
    def integrate_into_chunker(self) -> List[Dict]:
        """
        Get experiences ready to be chunked and indexed.
        
        Returns:
            List of experience chunks
        """
        high_value = self.recorder.get_high_value_experiences(
            min_confidence=0.75,
            min_approvals=1
        )
        
        chunks = []
        for exp in high_value:
            chunks.append({
                'content': self.recorder._experience_to_chunk(exp),
                'metadata': {
                    'source': 'learned_experience',
                    'experience_id': exp['experience_id'],
                    'confidence': exp.get('confidence', 0.0),
                    'tags': exp.get('tags', []),
                    'file': exp['file_path'],
                }
            })
        
        return chunks
    
    def get_priority_search_terms(self) -> List[str]:
        """Get search terms from experiences for priority matching."""
        terms = []
        
        for exp in self.recorder.experiences.values():
            if exp.get('in_kb') and exp.get('confidence', 0.0) > 0.8:
                # Extract key terms from problem
                problem = exp.get('problem_description', '')
                title = exp.get('title', '')
                tags = exp.get('tags', [])
                
                terms.append({
                    'term': title,
                    'priority': 'high',
                    'experience_id': exp['experience_id']
                })
                
                for tag in tags:
                    terms.append({
                        'term': tag,
                        'priority': 'medium',
                        'experience_id': exp['experience_id']
                    })
        
        return terms
