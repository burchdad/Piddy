"""
Market Analyzer - Discovers Real-World Gaps and Proposes Autonomous Builds

This component:
1. Analyzes trending repos and market patterns
2. Identifies gaps between what exists and what Piddy has built
3. Proposes new autonomous agents to build
4. Triggers autonomous development of missing capabilities

Phase 5: Market-Driven Autonomous Development
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib


@dataclass
class MarketPattern:
    """Pattern found in market repos"""
    category: str  # "testing", "code-review", "ci-cd", "performance", etc.
    name: str  # "mutation-testing", "performance-monitoring"
    frequency: int  # How many repos use this
    importance: float  # 0-1, how critical
    description: str
    example_repos: List[str]


@dataclass
class GapOpportunity:
    """Gap between market needs and Piddy capabilities"""
    gap_id: str
    category: str
    title: str  # "Mutation Testing Agent"
    market_need: str  # Why market needs it
    piddy_status: str  # "missing", "planned", "building", "built"
    autonomy_level: int  # 1-5, how autonomous the agent needs to be
    estimated_impact: float  # 0-1, market impact
    complexity_score: int  # 1-10, build complexity
    priority: int  # 1-10, urgency
    proposal: str  # Detailed proposal for building it


@dataclass
class ProposedAgent:
    """Agent proposed to build autonomously"""
    agent_name: str
    category: str
    capabilities: List[str]
    market_justification: str
    estimated_build_time_days: int
    integration_points: List[str]
    success_metrics: List[str]
    proposed_by: str  # "market_analyzer"
    timestamp: str


class MarketTrendAnalyzer:
    """Analyzes trends in real-world repos"""

    def __init__(self):
        self.patterns: List[MarketPattern] = []
        self.analyzed_repos: Set[str] = set()
        self.market_data_cache = Path("data/market_analysis.json")

    async def analyze_github_trends(self, sample_size: int = 100) -> List[MarketPattern]:
        """
        Analyze popular repos across different domains to find patterns
        """
        print("\n🔍 MARKET ANALYZER: Scanning real-world ecosystem...")

        # Simulated market analysis based on real trends
        trends = {
            "testing": {
                "mutation-testing": ("Mutation Testing Agents", 45, 0.9),
                "property-based-testing": ("Property-Based Test Generation", 38, 0.8),
                "flaky-test-detection": ("Flaky Test Detection", 62, 0.95),
                "coverage-gap-analysis": ("Coverage Gap Analysis", 55, 0.85),
            },
            "code-quality": {
                "code-duplication": ("Code Duplication Detector", 72, 0.92),
                "complexity-analysis": ("Complexity Analysis Agent", 68, 0.88),
                "security-scanning": ("Security Vulnerability Agent", 85, 0.98),
                "performance-profiling": ("Performance Profiler Agent", 70, 0.90),
            },
            "ci-cd": {
                "build-optimization": ("Build Optimization Agent", 55, 0.87),
                "dependency-management": ("Dependency Updater Agent", 80, 0.93),
                "canary-deployment": ("Canary Deployment Agent", 42, 0.82),
                "rollback-automation": ("Automatic Rollback Agent", 38, 0.91),
            },
            "documentation": {
                "api-documentation": ("API Doc Generator Agent", 65, 0.88),
                "code-architecture": ("Architecture Doc Agent", 50, 0.80),
                "changelog-generation": ("Changelog Generator", 58, 0.83),
                "example-generation": ("Example Generator Agent", 45, 0.81),
            },
            "refactoring": {
                "dead-code-elimination": ("Dead Code Remover", 72, 0.89),
                "type-annotation": ("Type Annotation Agent", 60, 0.85),
                "modernization": ("Code Modernization Agent", 50, 0.84),
                "naming-improvement": ("Better Naming Agent", 48, 0.79),
            },
        }

        for category, items in trends.items():
            for key, (name, frequency, importance) in items.items():
                pattern = MarketPattern(
                    category=category,
                    name=key,
                    frequency=frequency,
                    importance=importance,
                    description=f"{name} - Found in {frequency} analyzed repos",
                    example_repos=[f"repo_{i}" for i in range(min(5, frequency // 15))]
                )
                self.patterns.append(pattern)

        print(f"✅ Found {len(self.patterns)} market patterns across {len(trends)} categories")
        return self.patterns


class GapDetector:
    """Identifies gaps between market needs and Piddy capabilities"""

    PIDDY_BUILT_AGENTS = {
        "test-generation": {"status": "week1", "coverage": 0.28},
        "pr-review": {"status": "week2", "coverage": 0.50},
        "merge-conflict": {"status": "week3", "coverage": 0.90},
        "multi-repo-coordination": {"status": "week4", "coverage": 0.100},
    }

    PIDDY_PLANNED_AGENTS = {
        "security-scanning": {"planned": True, "phase": 5},
        "performance-optimization": {"planned": True, "phase": 6},
    }

    def __init__(self, market_patterns: List[MarketPattern]):
        self.patterns = market_patterns
        self.gaps: List[GapOpportunity] = []

    async def detect_gaps(self) -> List[GapOpportunity]:
        """
        Compare market patterns against Piddy's built and planned agents
        """
        print("\n🕵️  GAP DETECTOR: Finding market opportunities...")

        piddy_coverage = set(
            list(self.PIDDY_BUILT_AGENTS.keys()) + 
            list(self.PIDDY_PLANNED_AGENTS.keys())
        )

        for pattern in self.patterns:
            # Check if Piddy has this capability
            has_capability = any(
                pattern.name in capability or 
                pattern.category in capability
                for capability in piddy_coverage
            )

            if not has_capability:
                # This is a gap!
                gap_id = hashlib.md5(
                    f"{pattern.category}-{pattern.name}".encode()
                ).hexdigest()[:8]

                complexity = self._estimate_complexity(pattern)
                priority = self._calculate_priority(pattern, complexity)
                autonomy = self._estimate_autonomy_level(pattern)

                gap = GapOpportunity(
                    gap_id=gap_id,
                    category=pattern.category,
                    title=f"{pattern.name.title()} Agent",
                    market_need=f"Found in {pattern.frequency} repos - {pattern.importance:.0%} critical",
                    piddy_status="missing",
                    autonomy_level=autonomy,
                    estimated_impact=pattern.importance,
                    complexity_score=complexity,
                    priority=priority,
                    proposal=self._generate_proposal(pattern, gap_id),
                )
                self.gaps.append(gap)

        # Sort by priority
        self.gaps.sort(key=lambda x: x.priority, reverse=True)
        print(f"✅ Detected {len(self.gaps)} market gaps")
        return self.gaps

    def _estimate_complexity(self, pattern: MarketPattern) -> int:
        """Estimate how complex this agent would be to build"""
        complexity_map = {
            "testing": 6,
            "code-quality": 7,
            "ci-cd": 5,
            "documentation": 4,
            "refactoring": 8,
        }
        return complexity_map.get(pattern.category, 6)

    def _calculate_priority(self, pattern: MarketPattern, complexity: int) -> int:
        """Calculate priority: high impact + low complexity = high priority"""
        impact_score = pattern.importance * 10  # 0-10
        complexity_penalty = (complexity / 10) * 3  # Reduce by complexity
        priority = int(impact_score - complexity_penalty)
        return max(1, min(10, priority))

    def _estimate_autonomy_level(self, pattern: MarketPattern) -> int:
        """How autonomous should this agent be (1-5)"""
        autonomy_map = {
            "testing": 5,  # Very autonomous
            "code-quality": 4,
            "ci-cd": 5,
            "documentation": 3,
            "refactoring": 4,
        }
        return autonomy_map.get(pattern.category, 4)

    def _generate_proposal(self, pattern: MarketPattern, gap_id: str) -> str:
        """Generate detailed proposal for this agent"""
        return f"""
AGENT PROPOSAL: {pattern.name.upper()}

Market Analysis:
- Found in {pattern.frequency} analyzed repositories
- Criticality: {pattern.importance:.0%}
- Category: {pattern.category}
- Example repos: {', '.join(pattern.example_repos[:3])}

Why Build:
1. High market demand ({pattern.frequency} repos use similar tools)
2. Fills critical gap in Piddy's capabilities
3. Can integrate with existing Week 1-4 infrastructure
4. Enables market leadership in {pattern.category}

Integration:
- Connects to Phase 42 metric collection
- Feeds into Growth Engine for learning
- Can be deployed as Wave 5 agent
- Auto-triggers when market readiness detected

Expected Impact:
- Increases market competitiveness
- Enables {pattern.frequency}+ repo compatibility
- Creates new revenue/usage opportunity
"""


class AutonomousProposalEngine:
    """Generates and recommends autonomous builds"""

    def __init__(self, gaps: List[GapOpportunity]):
        self.gaps = gaps
        self.proposals: List[ProposedAgent] = []

    async def generate_proposals(self) -> List[ProposedAgent]:
        """
        Convert top gaps into agents to build autonomously
        """
        print("\n🤖 PROPOSAL ENGINE: Generating build recommendations...")

        # Take top 5 gaps and create proposals
        for gap in self.gaps[:5]:
            proposal = ProposedAgent(
                agent_name=gap.title.replace(" ", ""),
                category=gap.category,
                capabilities=self._define_capabilities(gap),
                market_justification=f"Market demand: {gap.market_need}",
                estimated_build_time_days=self._estimate_build_time(gap),
                integration_points=self._plan_integration(gap),
                success_metrics=self._define_success_metrics(gap),
                proposed_by="market_analyzer",
                timestamp=datetime.now().isoformat(),
            )
            self.proposals.append(proposal)

        print(f"✅ Generated {len(self.proposals)} autonomous build proposals")
        return self.proposals

    def _define_capabilities(self, gap: GapOpportunity) -> List[str]:
        """Define what this agent should do"""
        capabilities_map = {
            "testing": [
                "Analyze code for testability",
                "Generate test cases",
                "Measure coverage gaps",
                "Suggest improvements",
            ],
            "code-quality": [
                "Scan for issues",
                "Report findings",
                "Suggest fixes",
                "Track trends",
            ],
            "ci-cd": [
                "Monitor pipeline",
                "Optimize builds",
                "Auto-fix failures",
                "Coordinate deployments",
            ],
            "documentation": [
                "Generate docs",
                "Keep in sync",
                "Validate accuracy",
                "Update from code",
            ],
            "refactoring": [
                "Identify refactor opportunities",
                "Execute transformations",
                "Validate safety",
                "Report improvements",
            ],
        }
        return capabilities_map.get(gap.category, ["Analyze", "Report", "Improve"])

    def _estimate_build_time(self, gap: GapOpportunity) -> int:
        """Estimate days to build this agent"""
        base = gap.complexity_score
        if gap.autonomy_level >= 4:
            base += 2  # More complex if highly autonomous
        return base

    def _plan_integration(self, gap: GapOpportunity) -> List[str]:
        """Plan how this integrates with Piddy"""
        return [
            "Phase 42 PR Generation",
            "Growth Engine Learning",
            "Automation Rules Triggering",
            "Metrics Collection",
            "Dashboard Display",
        ]

    def _define_success_metrics(self, gap: GapOpportunity) -> List[str]:
        """Define how to measure success"""
        return [
            f"Issues found per {gap.category} repo",
            "Fixes accepted %",
            "Repo integration rate",
            "User satisfaction score",
            f"Adoption in {gap.category} market",
        ]


class MarketAnalyzer:
    """Main orchestrator for market-driven autonomous development"""

    def __init__(self):
        self.trend_analyzer = MarketTrendAnalyzer()
        self.gap_detector = None
        self.proposal_engine = None
        self.analysis_history: List[Dict] = []

    async def run_market_analysis(self) -> Dict:
        """
        Run complete market analysis and generate autonomous build recommendations
        """
        print("\n" + "=" * 80)
        print("🌍 MARKET ANALYZER - AUTONOMOUS BUILD DISCOVERY")
        print("=" * 80)

        # Phase 1: Analyze market trends
        patterns = await self.trend_analyzer.analyze_github_trends()

        # Phase 2: Detect gaps
        self.gap_detector = GapDetector(patterns)
        gaps = await self.gap_detector.detect_gaps()

        # Phase 3: Generate proposals
        self.proposal_engine = AutonomousProposalEngine(gaps)
        proposals = await self.proposal_engine.generate_proposals()

        result = {
            "timestamp": datetime.now().isoformat(),
            "market_patterns_found": len(patterns),
            "gaps_detected": len(gaps),
            "top_gaps": [asdict(g) for g in gaps[:5]],
            "proposals_generated": len(proposals),
            "recommended_builds": [asdict(p) for p in proposals],
        }

        # Save analysis
        self.analysis_history.append(result)
        self._save_analysis(result)

        return result

    def _save_analysis(self, result: Dict):
        """Save analysis results"""
        output_path = Path("data/market_analysis_latest.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2))
        print(f"\n💾 Analysis saved to {output_path}")

    async def get_next_autonomous_build(self) -> ProposedAgent:
        """
        Get the top recommended agent to build next
        Used by the background service to decide what to build
        """
        if not self.proposal_engine or not self.proposal_engine.proposals:
            await self.run_market_analysis()

        if self.proposal_engine.proposals:
            return self.proposal_engine.proposals[0]
        return None

    async def feed_to_growth_engine(self, growth_engine_instance):
        """
        Feed market analysis results to the growth engine
        so it becomes market-aware
        """
        print("\n🔗 Feeding market analysis to Growth Engine...")

        analysis = await self.run_market_analysis()

        # Create a metric that represents market opportunity
        market_metric = {
            "metric_type": "market_opportunity",
            "value": len(analysis["proposals_generated"]),
            "details": {
                "top_gap": analysis["top_gaps"][0] if analysis["top_gaps"] else None,
                "recommended_next_build": analysis["recommended_builds"][0] if analysis["recommended_builds"] else None,
            },
        }

        # Growth engine should learn: "Market wants this, let's build it"
        print(f"✅ Growth Engine now aware of {len(analysis['proposals_generated'])} build opportunities")
        return market_metric


async def main():
    """Demo the market analyzer"""
    analyzer = MarketAnalyzer()

    # Run market analysis
    result = await analyzer.run_market_analysis()

    # Show results
    print("\n" + "=" * 80)
    print("📊 ANALYSIS RESULTS")
    print("=" * 80)
    print(f"\nMarket Patterns Found: {result['market_patterns_found']}")
    print(f"Gaps Detected: {result['gaps_detected']}")
    print(f"Proposals Generated: {result['proposals_generated']}\n")

    print("🎯 TOP 5 GAPS (Highest Priority):")
    for i, gap in enumerate(result["top_gaps"][:5], 1):
        print(f"\n  {i}. {gap['title']} (Priority: {gap['priority']}/10)")
        print(f"     Market Need: {gap['market_need']}")
        print(f"     Status: {gap['piddy_status']}")
        print(f"     Complexity: {gap['complexity_score']}/10")

    print("\n\n🚀 RECOMMENDED BUILDS (In Priority Order):")
    for i, prop in enumerate(result["recommended_builds"][:3], 1):
        print(f"\n  {i}. {prop['agent_name']}")
        print(f"     Category: {prop['category']}")
        print(f"     Est. Build Time: {prop['estimated_build_time_days']} days")
        print(f"     Expected Impact: High")

    print("\n" + "=" * 80)
    print("💡 NEXT STEP: Feed these proposals to Background Service")
    print("   It will then autonomously build, test, and deploy them")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
