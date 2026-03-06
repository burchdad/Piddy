"""
Phase 38: LLM-Assisted Planning

Enhances mission planning using large language models to:
- Analyze code changes with semantic understanding
- Generate intelligent priorities and strategies
- Suggest risk mitigation approaches
- Recommend task sequencing
- Provide domain-specific insights

This layer sits between diff analysis (Phase 36) and execution,
using LLM reasoning to make smarter planning decisions.

Integration flow:
Diff Analysis → LLM Reasoning → Enhanced Plan → Parallel Execution

Benefits:
- Context-aware task prioritization
- Intelligent risk mitigation
- Better test selection
- Semantic understanding of changes
- Adaptive strategy based on code patterns
"""

import json
import logging
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
import anthropic

logger = logging.getLogger(__name__)


class PlanStrategy(Enum):
    """Strategic approaches for mission execution"""
    CONSERVATIVE = "conservative"      # Large safety margin, thorough validation
    BALANCED = "balanced"              # Standard approach, proven track record
    AGGRESSIVE = "aggressive"          # Optimized for speed, calculated risk
    EXPLORATORY = "exploratory"        # Try new approaches, learn


@dataclass
class LLMAnalysisResult:
    """Result from LLM analysis of diff"""
    semantic_summary: str              # What the changes mean
    suggested_strategy: PlanStrategy   # Recommended approach
    risk_factors: List[str]            # Identified risks
    mitigation_strategies: List[str]   # How to address risks
    suggested_priority: str            # Priority level (low/normal/high/critical)
    task_recommendations: List[str]    # Specific tasks to include
    skip_opportunities: List[str]      # Tasks that can be skipped safely
    test_focus_areas: List[str]        # Which tests are most critical
    confidence_score: float            # 0-1 confidence in the analysis
    reasoning: str                     # Explanation of reasoning


@dataclass
class EnhancedPlan:
    """A plan enhanced with LLM insights"""
    base_plan: Dict
    llm_analysis: LLMAnalysisResult
    final_tasks: List[str]
    execution_order: List[str]
    estimated_duration: str
    confidence: float


class LLMPlanningAssistant:
    """Uses LLM to enhance mission planning"""
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        """Initialize LLM planning assistant
        
        Args:
            model: Claude model to use for planning analysis
        """
        self.client = anthropic.Anthropic()
        self.model = model
        self.conversation_history: List[Dict] = []
        
        logger.info(f"LLMPlanningAssistant initialized with model: {model}")
    
    def analyze_diff_semantically(self, diff_text: str, 
                                 file_paths: List[str],
                                 module_names: List[str]) -> LLMAnalysisResult:
        """
        Use LLM to semantically analyze code changes.
        
        Args:
            diff_text: Raw git diff output
            file_paths: Files affected by changes
            module_names: Module names affected
        
        Returns:
            LLMAnalysisResult with semantic analysis
        """
        prompt = f"""Analyze these code changes and provide strategic insights:

Changed Files: {', '.join(file_paths[:10])}
Affected Modules: {', '.join(module_names)}

Git Diff (first 2000 chars):
{diff_text[:2000]}

Provide analysis in JSON format with:
- semantic_summary: What these changes mean architecturally
- risk_level: "low", "medium", or "high"
- suggested_strategy: "conservative", "balanced", "aggressive", or "exploratory"  
- main_risks: List of 2-3 key risks
- mitigation_steps: How to address each risk
- critical_tests: Which areas MUST be tested
- can_skip: Which validation steps might be skipped safely
- confidence: 0-1 rating of this analysis

Format: {{
  "semantic_summary": "...",
  "risk_level": "...",
  "suggested_strategy": "...",
  "main_risks": [...],
  "mitigation_steps": [...],
  "critical_tests": [...],
  "can_skip": [...],
  "confidence": 0.XX
}}
"""
        
        logger.info("Running semantic diff analysis with LLM...")
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON from response
        try:
            analysis_json = self._extract_json(response_text)
            
            result = LLMAnalysisResult(
                semantic_summary=analysis_json.get("semantic_summary", ""),
                suggested_strategy=PlanStrategy(analysis_json.get("suggested_strategy", "balanced")),
                risk_factors=analysis_json.get("main_risks", []),
                mitigation_strategies=analysis_json.get("mitigation_steps", []),
                suggested_priority=self._risk_to_priority(analysis_json.get("risk_level", "medium")),
                task_recommendations=analysis_json.get("critical_tests", []),
                skip_opportunities=analysis_json.get("can_skip", []),
                test_focus_areas=analysis_json.get("critical_tests", []),
                confidence_score=float(analysis_json.get("confidence", 0.7)),
                reasoning=response_text
            )
            
            logger.info(f"Semantic analysis complete. Confidence: {result.confidence_score}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse LLM analysis: {e}")
            # Return safe default
            return self._create_default_analysis()
    
    def generate_optimized_tasks(self, mission_type: str,
                                 base_plan: Dict,
                                 llm_analysis: LLMAnalysisResult) -> List[str]:
        """
        Use LLM to generate optimized task list for mission.
        
        Args:
            mission_type: Type of mission (cleanup, refactor, etc.)
            base_plan: Base plan from diff analysis
            llm_analysis: Semantic analysis from LLM
        
        Returns:
            Optimized task list
        """
        prompt = f"""Given this mission context, suggest the optimal task sequence:

Mission Type: {mission_type}
Strategy: {llm_analysis.suggested_strategy.value}
Priority: {llm_analysis.suggested_priority}

Base Tasks (from diff analysis):
{json.dumps(base_plan.get('tasks', []), indent=2)}

Identified Risks:
{json.dumps(llm_analysis.risk_factors, indent=2)}

Mitigation Strategies:
{json.dumps(llm_analysis.mitigation_strategies, indent=2)}

Task Recommendations:
{json.dumps(llm_analysis.task_recommendations, indent=2)}

Can Skip (if high confidence):
{json.dumps(llm_analysis.skip_opportunities, indent=2)}

Return a JSON array of tasks in optimal execution order, like:
[
  "identify_risky_areas",
  "validate_type_safety",
  "execute_core_changes",
  "run_critical_tests",
  "generate_documentation"
]

Optimize for:
1. Strategy: {llm_analysis.suggested_strategy.value}
2. Risk factors: {len(llm_analysis.risk_factors)} identified
3. Speed (remove unnecessary steps if confidence > 0.8)
"""
        
        logger.info(f"Generating optimized tasks for {mission_type}...")
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        response_text = message.content[0].text
        
        try:
            tasks_json = self._extract_json(response_text)
            if isinstance(tasks_json, list):
                logger.info(f"Generated {len(tasks_json)} optimized tasks")
                return tasks_json
            
            return base_plan.get('tasks', [])
            
        except Exception as e:
            logger.error(f"Failed to parse task optimization: {e}")
            return base_plan.get('tasks', [])
    
    def suggest_test_selection(self, mission_type: str,
                              affected_modules: List[str],
                              llm_analysis: LLMAnalysisResult,
                              all_tests: Optional[List[str]] = None) -> Dict:
        """
        Use LLM to suggest which tests are most critical.
        
        Args:
            mission_type: Type of mission
            affected_modules: Modules affected by changes
            llm_analysis: Semantic analysis
            all_tests: All available tests (optional)
        
        Returns:
            Dict with must_run, should_run, can_skip test categories
        """
        prompt = f"""Suggest test prioritization for this mission:

Mission Type: {mission_type}
Affected Modules: {', '.join(affected_modules)}
Risk Level: {llm_analysis.suggested_priority}

Risk Factors:
{json.dumps(llm_analysis.risk_factors, indent=2)}

Critical Test Areas:
{json.dumps(llm_analysis.test_focus_areas, indent=2)}

Return JSON with three test categories:
{{
  "must_run": ["test_module_1", "test_integration_core", ...],
  "should_run": ["test_performance", "test_docs", ...],
  "can_skip": ["test_benchmarks", "test_slow_integration", ...],
  "reasoning": "Why these decisions"
}}

Optimize for both safety and speed.
"""
        
        logger.info("Suggesting optimized test selection...")
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        response_text = message.content[0].text
        
        try:
            test_selection = self._extract_json(response_text)
            logger.info(f"Test selection: {len(test_selection.get('must_run', []))} must-run, "
                       f"{len(test_selection.get('should_run', []))} should-run")
            return test_selection
            
        except Exception as e:
            logger.error(f"Failed to parse test selection: {e}")
            return {
                "must_run": affected_modules,
                "should_run": [],
                "can_skip": [],
                "reasoning": "Default selection due to parsing error"
            }
    
    def enhance_plan(self, base_plan: Dict,
                    diff_analysis: Dict,
                    mission_type: str) -> EnhancedPlan:
        """
        Enhance a base plan with LLM analysis.
        
        Args:
            base_plan: Original plan from Phase 36
            diff_analysis: Diff analysis results
            mission_type: Type of mission
        
        Returns:
            EnhancedPlan with LLM insights
        """
        logger.info(f"Enhancing plan for {mission_type} mission...")
        
        # Get diff text for analysis
        diff_text = diff_analysis.get('diff_text', '')[:5000]
        file_paths = diff_analysis.get('files_changed', [])
        modules = diff_analysis.get('affected_modules', [])
        
        # Run semantic analysis
        llm_analysis = self.analyze_diff_semantically(diff_text, file_paths, modules)
        
        # Generate optimized tasks
        optimized_tasks = self.generate_optimized_tasks(
            mission_type, 
            base_plan, 
            llm_analysis
        )
        
        # Suggest test selection
        test_selection = self.suggest_test_selection(
            mission_type,
            modules,
            llm_analysis
        )
        
        # Build enhanced plan
        enhanced_plan = EnhancedPlan(
            base_plan=base_plan,
            llm_analysis=llm_analysis,
            final_tasks=optimized_tasks,
            execution_order=self._order_tasks_by_strategy(
                optimized_tasks,
                llm_analysis.suggested_strategy
            ),
            estimated_duration=self._estimate_duration(optimized_tasks),
            confidence=llm_analysis.confidence_score
        )
        
        logger.info(f"Plan enhancement complete. Confidence: {enhanced_plan.confidence}")
        return enhanced_plan
    
    def generate_execution_summary(self, enhanced_plan: EnhancedPlan) -> str:
        """
        Generate a human-readable summary of the execution plan.
        
        Args:
            enhanced_plan: Enhanced plan with LLM insights
        
        Returns:
            Formatted summary string
        """
        summary = f"""
================================================================================
LLM-ENHANCED EXECUTION PLAN
================================================================================

SEMANTIC UNDERSTANDING:
{enhanced_plan.llm_analysis.semantic_summary}

STRATEGY: {enhanced_plan.llm_analysis.suggested_strategy.value.upper()}
PRIORITY: {enhanced_plan.llm_analysis.suggested_priority.upper()}
CONFIDENCE: {enhanced_plan.llm_analysis.confidence_score:.1%}

IDENTIFIED RISKS:
{chr(10).join(f"  • {risk}" for risk in enhanced_plan.llm_analysis.risk_factors)}

MITIGATION STRATEGIES:
{chr(10).join(f"  • {strat}" for strat in enhanced_plan.llm_analysis.mitigation_strategies)}

EXECUTION ORDER ({len(enhanced_plan.execution_order)} tasks):
{chr(10).join(f"  {i+1}. {task}" for i, task in enumerate(enhanced_plan.execution_order))}

SKIP OPPORTUNITIES (if confidence > 0.8):
{chr(10).join(f"  • {skip}" for skip in enhanced_plan.llm_analysis.skip_opportunities) if enhanced_plan.llm_analysis.skip_opportunities else "  None"}

ESTIMATED DURATION: {enhanced_plan.estimated_duration}
CONFIDENCE LEVEL: {enhanced_plan.llm_analysis.confidence_score:.1%}

================================================================================
"""
        return summary
    
    # Private methods
    
    def _extract_json(self, response: str) -> Dict:
        """Extract JSON from LLM response"""
        # Try to find JSON block
        import re
        json_match = re.search(r'\{.*?\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        # Try to find JSON array
        json_match = re.search(r'\[.*?\]', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        raise ValueError("No JSON found in response")
    
    def _risk_to_priority(self, risk_level: str) -> str:
        """Convert risk level to priority"""
        mapping = {
            "low": "normal",
            "medium": "high",
            "high": "critical"
        }
        return mapping.get(risk_level, "normal")
    
    def _order_tasks_by_strategy(self, tasks: List[str], 
                                strategy: PlanStrategy) -> List[str]:
        """Reorder tasks based on execution strategy"""
        if strategy == PlanStrategy.CONSERVATIVE:
            # Validation first, then execution
            validation_tasks = [t for t in tasks if 'validate' in t.lower()]
            execution_tasks = [t for t in tasks if 'validate' not in t.lower()]
            return validation_tasks + execution_tasks
        
        elif strategy == PlanStrategy.AGGRESSIVE:
            # Execution first, validation after
            execution_tasks = [t for t in tasks if 'validate' not in t.lower()]
            validation_tasks = [t for t in tasks if 'validate' in t.lower()]
            return execution_tasks + validation_tasks
        
        else:  # BALANCED or EXPLORATORY
            # Keep original order with some analysis first
            analysis_tasks = [t for t in tasks if 'analyze' in t.lower()]
            other_tasks = [t for t in tasks if 'analyze' not in t.lower()]
            return analysis_tasks + other_tasks
    
    def _estimate_duration(self, tasks: List[str]) -> str:
        """Estimate mission duration"""
        # Rough heuristic: ~30 seconds per task on average
        total_seconds = len(tasks) * 30
        
        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            return f"{total_seconds // 60}m {total_seconds % 60}s"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def _create_default_analysis(self) -> LLMAnalysisResult:
        """Create default/safe analysis when LLM fails"""
        return LLMAnalysisResult(
            semantic_summary="Unable to analyze changes. Using conservative defaults.",
            suggested_strategy=PlanStrategy.CONSERVATIVE,
            risk_factors=["Unknown change impact"],
            mitigation_strategies=["Run comprehensive validation"],
            suggested_priority="high",
            task_recommendations=["validate_all"],
            skip_opportunities=[],
            test_focus_areas=["all"],
            confidence_score=0.3,
            reasoning="Default analysis used due to processing error"
        )


class LLMPlanOptimizer:
    """Optimizes plan execution using LLM feedback"""
    
    def __init__(self, assistant: LLMPlanningAssistant):
        self.assistant = assistant
        self.optimization_history: List[Dict] = []
    
    def learn_from_execution(self, plan: EnhancedPlan, 
                            execution_result: Dict) -> Dict:
        """
        Learn from successful/failed execution to improve future plans.
        
        Args:
            plan: The plan that was executed
            execution_result: Results from execution
        
        Returns:
            Learning insights
        """
        prompt = f"""Analyze this mission execution and extract learnings:

Plan Strategy: {plan.llm_analysis.suggested_strategy.value}
Planned Tasks: {len(plan.final_tasks)}

Execution Result:
{json.dumps(execution_result, indent=2)[:1000]}

Provide insights in JSON format:
{{
  "what_worked": ["...", "..."],
  "what_didnt_work": ["...", "..."],
  "improvements_for_next_time": ["...", "..."],
  "strategy_adjustment": "Keep same / Adjust to X",
  "confidence_calibration": "Increase / Decrease / Keep"
}}
"""
        
        message = self.assistant.client.messages.create(
            model=self.assistant.model,
            max_tokens=512,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        try:
            insights = self.assistant._extract_json(message.content[0].text)
            self.optimization_history.append({
                'plan': asdict(plan.llm_analysis),
                'result': execution_result,
                'insights': insights
            })
            return insights
        except Exception as e:
            logger.error(f"Failed to extract learning insights: {e}")
            return {}


# Convenience functions

def create_llm_planner() -> LLMPlanningAssistant:
    """Create an LLM planning assistant"""
    return LLMPlanningAssistant()


def enhance_plan_with_llm(base_plan: Dict, 
                         diff_analysis: Dict,
                         mission_type: str) -> EnhancedPlan:
    """
    Convenience function to enhance a plan with LLM analysis.
    
    Args:
        base_plan: Original plan from Phase 36
        diff_analysis: Diff analysis results
        mission_type: Type of mission
    
    Returns:
        EnhancedPlan with LLM insights
    """
    planner = create_llm_planner()
    return planner.enhance_plan(base_plan, diff_analysis, mission_type)
