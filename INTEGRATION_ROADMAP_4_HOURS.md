# 🔧 PIDDY INTEGRATION ROADMAP - Wire It All Together

## What We're Doing
Taking 5 existing, working systems and wiring them into ONE coherent safe execution pipeline.

Current state: **5 disconnected components**
Target state: **1 unified AI OS**

---

## The 4-Hour Integration Plan

### ⏱️ Hour 1: Nova → Phase 40 → Phase 50 (Planning Layer)

**Current Problem**:
```python
# Right now in nova_coordinator.py:
class NovaCoordinator:
    def create_proposal(self, task):
        # Creates proposal
        # Sends to slack
        # But NOTHING EXECUTES
        pass
```

**What we need**:
```python
# New behavior needed:
class NovaCoordinator:
    def create_proposal(self, task):
        # 1. Create proposal (existing)
        proposal = Proposal(task)
        
        # 2. RUN PHASE 40 SIMULATION
        simulator = Phase40Simulator()
        prediction = simulator.predict(task)
        # Returns: success_probability, risk_level, impact_summary
        
        # 3. PASS TO PHASE 50 VOTING
        consensus = Phase50Coordinator()
        vote_result = consensus.vote_on_proposal(proposal, prediction)
        # Returns: votes_dict, final_decision, confidence
        
        # 4. Store decision
        proposal.add_votes(vote_result)
        
        # 5. Return full context
        return {
            "proposal": proposal,
            "prediction": prediction,
            "consensus": vote_result
        }
```

**Files to modify**:
- `src/nova_coordinator.py` → Add phase 40 + phase 50 calls
- `src/phase40_mission_simulation.py` → Ensure predict() is callable
- `src/phase50_multi_agent_orchestration.py` → Ensure vote_on_proposal() is callable

**Time estimate**: 45 minutes
**Verification**: Run `nova propose refactor_auth` and see Phase 50 votes returned

---

### ⏱️ Hour 2: Phase 50 Approval → Nova Execution

**Current Problem**:
```python
# Right now:
Phase50 votes and says "APPROVED"
But nothing happens after that
```

**What we need**:
```python
class NovaExecutionFlow:
    async def execute_with_consensus(self, proposal):
        # Get consensus result
        vote_result = self.phase50_vote(proposal)
        
        if vote_result.decision != "APPROVED":
            return {"error": "consensus not reached"}
        
        # NOW ACTUALLY EXECUTE
        executor = NovaExecutor()
        result = await executor.execute_mission(proposal.task)
        
        # Return result
        return {
            "status": "success",
            "mission_id": proposal.id,
            "result": result,
            "voted_by": [agent.id for agent in vote_result.agents]
        }
```

**Files to modify**:
- `piddy/nova_executor.py` → Already built! Just wire the trigger
- `src/nova_coordinator.py` → Add execution trigger after voting

**Time estimate**: 30 minutes
**Verification**: Run `nova propose refactor_auth` → wait for unanimous vote → see code execute

---

### ⏱️ Hour 3: Execution Result → PR Generation → Push

**Current Problem**:
```python
# Nova executes code
# Result sits in memory
# Nothing pushes to GitHub
```

**What we need**:
```python
async def execute_with_consensus(self, proposal):
    # 1. Execute (from Hour 2)
    result = await executor.execute_mission(proposal.task)
    
    # 2. GENERATE PR WITH REASONING
    pr_gen = PRGenerator()
    pr_content = pr_gen.generate_pr_from_result(result)
    # Includes: detailed reasoning, changes, testing, review checklist
    
    # 3. CREATE AND PUSH PR
    pr_manager = PRManager()
    pr_result = pr_manager.create_pr(
        title=pr_content.title,
        description=pr_content.markdown_body,
        branch_name=result.branch_name,
        base_branch="main"
    )
    
    # 4. Return full audit trail
    return {
        "execution_result": result,
        "pr_created": pr_result.pr_url,
        "voted_by": [agent.id for agent in vote_result.agents],
        "timestamp": datetime.utcnow().isoformat()
    }
```

**Files to modify**:
- `src/phase37_pr_generation.py` → Ensure generate_pr_from_result() exists
- `src/nova_coordinator.py` → Add PR generation after execution

**Time estimate**: 30 minutes
**Verification**: Full end-to-end: propose → vote → execute → PR created on GitHub

---

### ⏱️ Hour 4: User Input → Full Pipeline (Slack or Desktop)

**Current Problem**:
```
User can't easily trigger the full flow
Requires multiple manual steps
```

**What we need**:

#### Option A: Slack Command Handler
```python
@slack_handler.slash_command("nova")
async def nova_slash_command(command_text):
    # "nova refactor auth module"
    
    full_result = await novacon.execute_with_consensus(
        task=command_text,
        requester="slack_user"
    )
    
    # Send rich response to Slack
    slack.send_message({
        "blocks": [
            {"type": "section", "text": {"text": f"✅ Mission Approved", "type": "mrkdwn"}},
            {"type": "section", "text": {"text": f"Agents voted: {len(full_result['voted_by'])}/12 ✅\nConsensus: UNANIMOUS"}},
            {"type": "section", "text": {"text": f"Code executed ✅\nTests passing: 142/142 ✅"}},
            {"type": "section", "text": {"text": f"PR Created: {full_result['pr_url']}"}},
        ]
    })
```

#### Option B: Desktop RPC Endpoint
```python
@desktop_app.rpc_handler("nova.execute_with_consensus")
async def rpc_nova_execute(params):
    task = params.get("task")
    
    result = await novacon.execute_with_consensus(task=task)
    
    # Return result to desktop app
    return {
        "status": "success",
        "pr_url": result["pr_created"],
        "votes": result["voted_by"],
        "consensus": "UNANIMOUS"
    }
```

**Files to modify**:
- `piddy/slack_handler.py` → Add nova slash command
- `piddy/desktop_app.py` → Add nova RPC endpoint
- `src/nova_coordinator.py` → Expose execute_with_consensus

**Time estimate**: 45 minutes
**Verification**: `nova refactor auth module` → full pipeline runs → PR on GitHub

---

## Integration Spec: The Core Function

Create ONE function that wires everything:

**File to create**: `src/integrated_execution_pipeline.py`

```python
"""
Integrated Nova Execution Pipeline
Combines Phase 40, Phase 50, Nova Executor, PR Generation, and Git Push
"""

from datetime import datetime
from typing import Dict, Optional
import asyncio

class IntegratedExecutionPipeline:
    """Full integrated execution with planning, voting, execution, and PR"""
    
    def __init__(self):
        self.phase40 = Phase40Simulator()
        self.phase50 = Phase50Coordinator()
        self.executor = NovaExecutor()
        self.pr_gen = PRGenerator()
        self.pr_mgr = PRManager()
        self.approval_mgr = ApprovalManager()
        
    async def execute_autonomous_mission(
        self,
        task: str,
        requester: str = "system",
        consensus_type: str = "WEIGHTED"
    ) -> Dict:
        """
        Execute a mission end-to-end with approvals and PR creation
        
        Args:
            task: What to do (e.g., "refactor auth module")
            requester: Who requested it
            consensus_type: UNANIMOUS, SUPERMAJORITY, MAJORITY, WEIGHTED
            
        Returns:
            {
                "mission_id": "abc123",
                "status": "success|failed|rejected",
                "planning": {},        # Phase 40 output
                "consensus": {},       # Phase 50 votes
                "execution": {},       # Code execution result
                "pr_url": "https://", # Created PR
                "audit_trail": {}      # Full log
            }
        """
        
        mission_id = f"mission_{datetime.utcnow().isoformat()}"
        audit = {
            "mission_id": mission_id,
            "requester": requester,
            "task": task,
            "steps": []
        }
        
        try:
            # ============================================================
            # STEP 1: Planning (Phase 40)
            # ============================================================
            
            print(f"[{mission_id}] Step 1: Running Phase 40 simulation...")
            
            planning = self.phase40.simulate_task(task)
            audit["steps"].append({
                "step": "planning",
                "status": "complete",
                "data": planning
            })
            
            print(f"  → Success probability: {planning['success_probability']}%")
            print(f"  → Risk level: {planning['risk_level']}")
            print(f"  → Impact: {planning['impact_summary']}")
            
            # If high risk, need approval
            high_risk = planning['risk_level'].upper() == "HIGH"
            
            # ============================================================
            # STEP 2: Agent Consensus Voting (Phase 50)
            # ============================================================
            
            print(f"\n[{mission_id}] Step 2: Getting Phase 50 consensus vote...")
            
            proposal = Proposal(
                proposal_id=mission_id,
                task=task,
                required_consensus=consensus_type,
                impact_data=planning
            )
            
            vote_result = self.phase50.vote_on_proposal(proposal)
            audit["steps"].append({
                "step": "voting",
                "status": "complete",
                "data": vote_result
            })
            
            print(f"  → Votes: {vote_result['approved_count']}/{vote_result['total_agents']}")
            print(f"  → Consensus: {vote_result['consensus_decision']}")
            
            if vote_result['consensus_decision'] != "APPROVED":
                print(f"  → ❌ REJECTED by consensus")
                return {
                    "mission_id": mission_id,
                    "status": "rejected",
                    "reason": "consensus_not_reached",
                    "audit_trail": audit
                }
            
            # ============================================================
            # STEP 3: Human Approval (if high risk)
            # ============================================================
            
            if high_risk:
                print(f"\n[{mission_id}] Step 3: Requesting human approval (HIGH RISK)...")
                
                approval_req = ApprovalRequest(
                    mission_id=mission_id,
                    mission_name=task,
                    risk_level=planning['risk_level'],
                    confidence=vote_result['confidence'],
                    prediction=planning
                )
                
                approval = await self.approval_mgr.request_approval(approval_req)
                audit["steps"].append({
                    "step": "human_approval",
                    "status": "complete",
                    "data": approval
                })
                
                if approval['status'] != "APPROVED":
                    print(f"  → ❌ Human rejected mission")
                    return {
                        "mission_id": mission_id,
                        "status": "rejected",
                        "reason": "human_rejection",
                        "audit_trail": audit
                    }
            
            # ============================================================
            # STEP 4: Execute Code (Nova Executor)
            # ============================================================
            
            print(f"\n[{mission_id}] Step 4: Executing mission...")
            
            execution_result = await self.executor.execute_mission(task)
            audit["steps"].append({
                "step": "execution",
                "status": "complete",
                "data": execution_result
            })
            
            print(f"  → Code generated: {execution_result['files_created']} files")
            print(f"  → Tests: {execution_result['tests_passed']}/{execution_result['tests_total']} passed")
            print(f"  → Branch: {execution_result['branch']}")
            
            if execution_result['tests_passed'] < execution_result['tests_total']:
                print(f"  → ⚠️  Some tests failed")
            
            # ============================================================
            # STEP 5: Generate PR with Reasoning (Phase 37)
            # ============================================================
            
            print(f"\n[{mission_id}] Step 5: Generating PR...")
            
            pr_content = self.pr_gen.generate_pr_from_execution(
                execution_result,
                planning,
                vote_result
            )
            audit["steps"].append({
                "step": "pr_generation",
                "status": "complete",
                "data": {
                    "title": pr_content.title,
                    "body_length": len(pr_content.markdown_body)
                }
            })
            
            print(f"  → PR Title: {pr_content.title}")
            print(f"  → Including: reasoning, validation, checklist")
            
            # ============================================================
            # STEP 6: Push to GitHub
            # ============================================================
            
            print(f"\n[{mission_id}] Step 6: Creating PR on GitHub...")
            
            pr_result = self.pr_mgr.create_pr(
                title=pr_content.title,
                description=pr_content.markdown_body,
                branch_name=execution_result['branch'],
                base_branch="main"
            )
            audit["steps"].append({
                "step": "pr_creation",
                "status": "complete",
                "data": pr_result
            })
            
            print(f"  → PR URL: {pr_result['html_url']}")
            print(f"  → ✅ Ready for review")
            
            # ============================================================
            # SUCCESS
            # ============================================================
            
            return {
                "mission_id": mission_id,
                "status": "success",
                "planning": planning,
                "consensus": vote_result,
                "votes": {agent['id']: agent['vote'] for agent in vote_result['agents']},
                "execution": execution_result,
                "pr_url": pr_result['html_url'],
                "pr_number": pr_result['number'],
                "audit_trail": audit
            }
            
        except Exception as e:
            print(f"  → ❌ ERROR: {str(e)}")
            audit["steps"].append({
                "step": "error",
                "status": "failed",
                "error": str(e)
            })
            
            return {
                "mission_id": mission_id,
                "status": "failed",
                "error": str(e),
                "audit_trail": audit
            }


# Usage Examples:

# From Slack:
async def handle_nova_command(command_text):
    pipeline = IntegratedExecutionPipeline()
    result = await pipeline.execute_autonomous_mission(
        task=command_text,
        requester="slack_user_123",
        consensus_type="WEIGHTED"
    )
    
    if result['status'] == 'success':
        slack.send(f"✅ Mission complete!\nPR: {result['pr_url']}")
    else:
        slack.send(f"❌ Mission failed: {result['reason']}")

# From Desktop:
@rpc_handler("nova.execute")
async def rpc_execute(task, requester):
    pipeline = IntegratedExecutionPipeline()
    result = await pipeline.execute_autonomous_mission(task, requester)
    return result

# Direct Python:
import asyncio

async def main():
    pipeline = IntegratedExecutionPipeline()
    
    result = await pipeline.execute_autonomous_mission(
        task="Refactor auth module to use async/await",
        requester="user@example.com",
        consensus_type="UNANIMOUS"
    )
    
    print(f"\n{'='*60}")
    print(f"MISSION COMPLETE")
    print(f"{'='*60}")
    print(f"Status: {result['status']}")
    print(f"PR: {result.get('pr_url', 'N/A')}")
    print(f"Voted by: {len(result.get('votes', {}))} agents")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## The 4-Hour Breakdown

| Hour | Task | Files | Effort | Verification |
|------|------|-------|--------|--------------|
| 1 | Wire Phase 40 → Phase 50 | nova_coordinator.py | 45 min | `nova propose task` returns votes |
| 2 | Add execution trigger | nova_executor.py | 30 min | Full execution after unanimous vote |
| 3 | PR generation → push | phase37_pr_generation.py, pr_manager.py | 30 min | PR created on GitHub |
| 4 | Slack/Desktop endpoints | slack_handler.py, desktop_app.py | 45 min | `nova refactor auth` works end-to-end |

**Total: ~3.25 hours actual work + 30 minutes testing = 4 hours**

---

## Success Criteria

After 4 hours, you should be able to:

```bash
# On Slack, type:
/nova refactor auth module

# You should see (in Slack):
✅ Mission: Refactor auth module
  Planning (Phase 40): Success probability 92%
  Voting (Phase 50): 12/12 agents APPROVE ✅
  Execution: ✅ Complete (3 files, 87 tests passing)
  PR Created: https://github.com/burchdad/Piddy/pull/342
  Ready for code review
```

---

## What NOT To Do

- ❌ Don't rebuild approval system (it exists)
- ❌ Don't rebuild voting (it exists)
- ❌ Don't rebuild PR creation (it exists)
- ❌ Don't just build nova_executor separately (already done)
- ❌ Don't add more features (just wire what's there)

## What TO Do

- ✅ Create `integrated_execution_pipeline.py` (the glue)
- ✅ Add function calls in nova_coordinator.py
- ✅ Wire Slack endpoint to pipeline
- ✅ Wire Desktop RPC to pipeline
- ✅ Test end-to-end

---

## The 4-Hour Goal

**Transform Piddy from:**
- 5 disconnected systems
- Requires manual coordination
- No end-to-end flow

**Into:**
- 1 unified AI OS
- Fully autonomous execution
- Production-ready deployment

**One Slack command and you have a fully reasoned, voted-on, executed,documented, and pushed PR.**

That's the goal. 4 hours. Let's lock it in.

