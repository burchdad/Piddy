"""
Piddy Skills/Plugin Loader

Dynamically discovers and loads skill definitions from the library/ folder.
Skills are markdown files (SKILL.md or *.skill.md) that define capabilities
Piddy can use — drop a file in, Piddy learns it.

Skill file format (SKILL.md):
---
name: my-skill
description: What this skill does
version: 1.0
tags: [python, api]
---
# Detailed instructions for the skill...

Usage:
    from src.skills.loader import get_skill_registry
    registry = get_skill_registry()
    skill = registry.get("my-skill")
    print(skill.instructions)
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LIBRARY_DIR = PROJECT_ROOT / "library"
SKILLS_DIR = LIBRARY_DIR / "skills"


@dataclass
class Skill:
    """A loaded skill definition."""
    name: str
    description: str = ""
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    instructions: str = ""
    source_path: str = ""

    def matches_query(self, query: str) -> float:
        """Check if this skill is relevant to a query. Returns relevance score 0.0-1.0."""
        q = query.lower()
        q_words = set(q.split())
        score = 0.0

        # Exact name match is high signal
        if self.name.lower() in q:
            score += 0.6
        # Name words match (e.g. "java" in "Java Development")
        name_words = set(self.name.lower().replace('-', ' ').split())
        name_overlap = len(name_words & q_words)
        if name_overlap:
            score += 0.3 * (name_overlap / len(name_words))

        # Tag matches — strongest signal for topic relevance
        for tag in self.tags:
            tag_lower = tag.lower()
            if tag_lower in q:
                score += 0.4
            elif any(tag_lower in w or w in tag_lower for w in q_words if len(w) > 2):
                score += 0.2

        # Description word overlap
        if self.description:
            desc_words = set(self.description.lower().split())
            desc_overlap = len(desc_words & q_words)
            if desc_overlap:
                score += 0.1 * min(desc_overlap, 3)

        return min(score, 1.0)


def _parse_frontmatter(content: str) -> tuple:
    """Parse YAML-like frontmatter from a markdown file.
    
    Returns (metadata_dict, body_text).
    """
    metadata = {}
    body = content

    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if match:
        frontmatter_text = match.group(1)
        body = match.group(2)

        for line in frontmatter_text.split('\n'):
            line = line.strip()
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip().lower()
                value = value.strip()

                # Parse list values like [a, b, c]
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(',') if v.strip()]

                metadata[key] = value

    return metadata, body


def _discover_skill_files() -> List[Path]:
    """Find all skill files in the library directory tree."""
    skill_files = []

    # Primary: library/skills/*.skill.md and library/skills/*/SKILL.md
    if SKILLS_DIR.exists():
        skill_files.extend(SKILLS_DIR.glob("*.skill.md"))
        skill_files.extend(SKILLS_DIR.glob("*/SKILL.md"))
        skill_files.extend(SKILLS_DIR.glob("*/*.skill.md"))

    # Also check for SKILL.md anywhere in library/
    for skill_md in LIBRARY_DIR.rglob("SKILL.md"):
        if skill_md not in skill_files:
            skill_files.append(skill_md)

    # Check for .skill.md files anywhere in library/
    for skill_md in LIBRARY_DIR.rglob("*.skill.md"):
        if skill_md not in skill_files:
            skill_files.append(skill_md)

    return skill_files


def _load_skill(filepath: Path) -> Optional[Skill]:
    """Load a single skill file."""
    try:
        content = filepath.read_text(encoding="utf-8")
        metadata, body = _parse_frontmatter(content)

        name = metadata.get("name", filepath.stem)
        if name == "SKILL":
            # Use parent directory name for SKILL.md files
            name = filepath.parent.name

        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]

        return Skill(
            name=name,
            description=metadata.get("description", ""),
            version=metadata.get("version", "1.0"),
            tags=tags,
            instructions=body.strip(),
            source_path=str(filepath),
        )
    except Exception as e:
        logger.warning(f"Failed to load skill from {filepath}: {e}")
        return None


class SkillRegistry:
    """Registry of all loaded skills."""

    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._loaded = False

    def load(self) -> int:
        """Discover and load all skills. Returns count loaded."""
        self._skills.clear()
        files = _discover_skill_files()
        for f in files:
            skill = _load_skill(f)
            if skill:
                self._skills[skill.name] = skill
                logger.info(f"Loaded skill: {skill.name} ({skill.source_path})")
        self._loaded = True
        logger.info(f"Skills loaded: {len(self._skills)}")
        return len(self._skills)

    def reload(self) -> int:
        """Reload all skills (hot reload)."""
        return self.load()

    def get(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        if not self._loaded:
            self.load()
        return self._skills.get(name)

    def search(self, query: str) -> List[Skill]:
        """Find skills matching a query, ranked by relevance."""
        if not self._loaded:
            self.load()
        scored = [(s, s.matches_query(query)) for s in self._skills.values()]
        scored = [(s, score) for s, score in scored if score > 0.1]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored]

    def list_all(self) -> List[Skill]:
        """List all loaded skills."""
        if not self._loaded:
            self.load()
        return list(self._skills.values())

    def get_context_for_query(self, query: str, max_skills: int = 3) -> str:
        """Get combined skill instructions relevant to a query.
        
        This is what gets injected into the LLM prompt as extra context.
        """
        matching = self.search(query)[:max_skills]
        if not matching:
            return ""
        
        parts = []
        for skill in matching:
            parts.append(f"## Skill: {skill.name}\n{skill.instructions}")
        return "\n\n".join(parts)

    def to_dict_list(self) -> List[Dict]:
        """Serialize all skills for API responses."""
        return [
            {
                "name": s.name,
                "description": s.description,
                "version": s.version,
                "tags": s.tags,
                "source": s.source_path,
            }
            for s in self.list_all()
        ]


# Singleton
_registry: Optional[SkillRegistry] = None


def get_skill_registry() -> SkillRegistry:
    """Get the global skill registry (lazy-loaded)."""
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
        _registry.load()
    return _registry
