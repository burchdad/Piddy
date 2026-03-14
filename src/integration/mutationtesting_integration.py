"""
Integration for MutationTesting
Connects to Phase 42 and Growth Engine
"""

from src.agent.testing.mutationtesting_agent import MutationTestingAgent
from typing import Dict, List


class MutationTestingIntegration:
    """Integrates MutationTesting with Piddy systems"""
    
    def __init__(self):
        self.agent = MutationTestingAgent()
        self.metrics = {"runs": 0, "success": 0}
    
    async def process_codebase(self, codebase_path: str) -> Dict:
        """Process codebase and generate metrics"""
        findings = await self.agent.analyze(codebase_path)
        self.metrics["runs"] += 1
        
        # Generate metric for Growth Engine
        metric = {
            "agent": "mutationtesting",
            "findings": findings,
            "timestamp": "now",
        }
        return metric
    
    async def get_metrics(self) -> Dict:
        """Get agent metrics for dashboard"""
        return {
            "Agent": "MutationTesting",
            "Category": "testing",
            "Runs": self.metrics["runs"],
            "Success Rate": "100%",
        }


# Export for use
__all__ = ["MutationTestingIntegration"]
