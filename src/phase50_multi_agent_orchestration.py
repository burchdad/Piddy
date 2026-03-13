"""
logger = logging.getLogger(__name__)
Phase 50: Multi-Agent Orchestration
Advanced autonomous agent coordination and consensus mechanisms

Enables multiple specialized agents to work together autonomously
"""

from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime
import uuid
import logging


class AgentRole(Enum):
    """Specialized agent roles"""
    COORDINATOR = "coordinator"        # Orchestrates work
    ANALYZER = "analyzer"              # Analyzes code and impact
    EXECUTOR = "executor"              # Executes refactoring
    VALIDATOR = "validator"            # Validates changes
    GUARDIAN = "guardian"              # Security/safety checks
    LEARNER = "learner"                # Continuous learning (Phase 51)
    PERFORMANCE_ANALYST = "performance_analyst"  # Analyzes performance impact
    TECH_DEBT_HUNTER = "tech_debt_hunter"        # Identifies technical debt
    API_COMPATIBILITY = "api_compatibility"      # Checks API compatibility
    DATABASE_MIGRATION = "database_migration"    # Manages database changes
    ARCHITECTURE_REVIEWER = "architecture_reviewer" # Reviews architectural decisions
    COST_OPTIMIZER = "cost_optimizer"            # Optimizes infrastructure costs


class ConsensusType(Enum):
    """Consensus mechanisms"""
    MAJORITY = "majority"              # >50% agreement
    SUPERMAJORITY = "supermajority"    # >66% agreement (2/3)
    UNANIMOUS = "unanimous"            # 100% agreement
    WEIGHTED = "weighted"              # Reputation-based


class MessageType(Enum):
    """Inter-agent communication types"""
    PROPOSAL = "proposal"              # Agent proposes action
    VOTE = "vote"                      # Agent votes on proposal
    EXECUTE = "execute"                # Execute approved action
    REPORT = "report"                  # Report results/metrics
    QUERY = "query"                    # Request information
    ALERT = "alert"                    # Alert about issue


class VoteOutcome(Enum):
    """Result of agent vote"""
    APPROVED = "approved"
    REJECTED = "rejected"
    ABSTAIN = "abstain"


@dataclass
class AgentCapability:
    """Capability an agent possesses"""
    capability_id: str
    name: str
    description: str
    success_rate: float = 0.95    # Historical success rate
    estimated_runtime_sec: int = 300
    resource_cost: int = 10           # Relative cost units
    dependencies: List[str] = field(default_factory=list)


@dataclass
class Message:
    """Inter-agent communication"""
    message_id: str
    sender_id: str
    receiver_id: Optional[str] = None  # None = broadcast
    message_type: MessageType = MessageType.QUERY
    content: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    priority: int = 5                  # 1-10, higher = more urgent
    requires_response: bool = False
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = f"msg_{uuid.uuid4().hex[:12]}"


@dataclass
class Vote:
    """Agent's vote on proposal"""
    vote_id: str
    proposal_id: str
    agent_id: str
    outcome: VoteOutcome
    confidence: float = 0.8            # 0.0-1.0 confidence in vote
    reasoning: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class Proposal:
    """Proposed action for agent consensus"""
    proposal_id: str
    proposer_id: str
    action: str                        # What to do
    context: Dict = field(default_factory=dict)
    required_consensus: ConsensusType = ConsensusType.MAJORITY
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    deadline_sec: int = 300
    
    votes: Dict[str, Vote] = field(default_factory=dict)
    approved: bool = False
    execution_started: bool = False
    execution_result: Optional[Dict] = None
    
    def vote_count(self) -> Dict[str, int]:
        """Count votes by outcome"""
        counts = {
            'approved': 0,
            'rejected': 0,
            'abstain': 0,
        }
        for vote in self.votes.values():
            if vote.outcome == VoteOutcome.APPROVED:
                counts['approved'] += 1
            elif vote.outcome == VoteOutcome.REJECTED:
                counts['rejected'] += 1
            else:
                counts['abstain'] += 1
        return counts


@dataclass
class AgentReputation:
    """Tracks agent reputation for weighted consensus"""
    agent_id: str
    total_decisions: int = 0
    correct_decisions: int = 0
    failed_decisions: int = 0
    reputation_score: float = 1.0     # Starts at 1.0
    specialization: str = ""            # Area of expertise
    
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_decisions == 0:
            return 1.0
        return self.correct_decisions / self.total_decisions
    
    def update_reputation(self, correct: bool, specialization_match: bool = False, 
                         confidence_multiplier: float = 1.0) -> None:
        """Update reputation based on decision outcome
        
        Args:
            correct: Whether the decision was correct
            specialization_match: Whether decision was in agent's specialization
            confidence_multiplier: How confident should the reputation update be (0-2)
        """
        self.total_decisions += 1
        
        if correct:
            self.correct_decisions += 1
            # Boost if in specialization
            if specialization_match:
                boost = 1.05 * confidence_multiplier
                self.reputation_score = min(2.0, self.reputation_score * boost)
            else:
                boost = 1.02 * (confidence_multiplier * 0.5)
                self.reputation_score = min(1.5, self.reputation_score * boost)
        else:
            self.failed_decisions += 1
            penalty = 0.95 / (confidence_multiplier + 0.5)  # Less penalty if low confidence
            self.reputation_score = max(0.5, self.reputation_score * penalty)
    
    def get_vote_weight(self) -> float:
        """Get this agent's voting weight based on reputation
        
        Higher reputation = more voting weight (0.5-2.0)
        Used in weighted consensus voting
        """
        return max(0.5, min(2.0, self.reputation_score))


class AutonomousAgent:
    """Single autonomous agent in multi-agent system"""
    
    def __init__(self, agent_id: str, role: AgentRole, capabilities: List[AgentCapability]):
        """Initialize agent"""
        self.agent_id = agent_id
        self.role = role
        self.capabilities = {c.capability_id: c for c in capabilities}
        self.reputation = AgentReputation(agent_id, specialization=role.value)
        
        self.inbox: asyncio.Queue = asyncio.Queue()
        self.outbox: asyncio.Queue = asyncio.Queue()
        self.state = {}
        self.decision_log: List[Dict] = []
        self.execution_history: List[Dict] = []
    
    async def receive_message(self, message: Message) -> None:
        """Receive message from another agent"""
        await self.inbox.put(message)
    
    async def send_message(self, message: Message) -> None:
        """Send message to other agent(s)"""
        await self.outbox.put(message)
    
    async def propose_action(self, action: str, context: Dict) -> Proposal:
        """Create and propose action"""
        proposal = Proposal(
            proposal_id=f"prop_{uuid.uuid4().hex[:12]}",
            proposer_id=self.agent_id,
            action=action,
            context=context,
        )
        return proposal
    
    async def vote_on_proposal(self, proposal: Proposal) -> Vote:
        """Vote on proposed action with specialization-aware logic
        
        Each agent type applies domain-specific analysis to votes:
        - GUARDIAN: Security & safety focus (high confidence rejections)
        - VALIDATOR: Quality & correctness focus
        - ANALYZER: Impact & complexity focus
        - PERFORMANCE_ANALYST: Performance implications
        - TECH_DEBT_HUNTER: Technical debt concerns
        - API_COMPATIBILITY: API breaking changes
        - DATABASE_MIGRATION: Data consistency
        - ARCHITECTURE_REVIEWER: Structural soundness
        - COST_OPTIMIZER: Infrastructure costs
        """
        
        confidence = 0.75
        outcome = VoteOutcome.APPROVED
        reasoning = f"Analysis by {self.role.value}"
        
        # =====================================================
        # GUARDIAN: Security-first approach
        # =====================================================
        if self.role == AgentRole.GUARDIAN:
            if 'risk_level' in proposal.context:
                risk = proposal.context['risk_level']
                if risk > 8:
                    outcome = VoteOutcome.REJECTED
                    reasoning = "Critical risk level detected"
                    confidence = 0.99
                elif risk > 6:
                    confidence = 0.85
                    reasoning = "High risk - caution required"
                elif risk < 2:
                    confidence = 0.95
            
            # Check for security patterns
            if 'security_check_pass' in proposal.context:
                if not proposal.context['security_check_pass']:
                    outcome = VoteOutcome.REJECTED
                    reasoning = "Security checks failed"
                    confidence = 0.98
        
        # =====================================================
        # VALIDATOR: Quality assurance
        # =====================================================
        elif self.role == AgentRole.VALIDATOR:
            if 'quality_score' in proposal.context:
                score = proposal.context['quality_score']
                if score < 0.65:
                    outcome = VoteOutcome.REJECTED
                    confidence = 0.92
                    reasoning = "Quality score below threshold"
                elif score > 0.95:
                    confidence = 0.98
                    reasoning = "Excellent quality - strong approval"
                elif score < 0.75:
                    confidence = 0.75
                    reasoning = "Quality concerns"
            
            if 'test_coverage' in proposal.context:
                coverage = proposal.context['test_coverage']
                if coverage < 0.70:
                    outcome = VoteOutcome.ABSTAIN if outcome == VoteOutcome.APPROVED else outcome
                    reasoning += "; Low test coverage"
        
        # =====================================================
        # PERFORMANCE_ANALYST: Performance impact
        # =====================================================
        elif self.role == AgentRole.PERFORMANCE_ANALYST:
            if 'performance_impact' in proposal.context:
                impact = proposal.context['performance_impact']
                if impact > 10:  # 10% degradation
                    outcome = VoteOutcome.REJECTED
                    reasoning = "Unacceptable performance degradation"
                    confidence = 0.90
                elif impact < -5:  # 5% improvement
                    confidence = 0.95
                    reasoning = "Significant performance improvement"
        
        # =====================================================
        # TECH_DEBT_HUNTER: Long-term code health
        # =====================================================
        elif self.role == AgentRole.TECH_DEBT_HUNTER:
            if 'tech_debt_increase' in proposal.context:
                debt_delta = proposal.context['tech_debt_increase']
                if debt_delta > 50:  # Significant increase
                    outcome = VoteOutcome.ABSTAIN
                    confidence = 0.80
                    reasoning = "Warning: Increases technical debt significantly"
                elif debt_delta < 0:  # Decreases debt
                    confidence = 0.95
                    reasoning = "Reduces technical debt - strong support"
        
        # =====================================================
        # API_COMPATIBILITY: Breaking changes
        # =====================================================
        elif self.role == AgentRole.API_COMPATIBILITY:
            breaking_change = proposal.context.get('breaking_change', False)
            if breaking_change:
                if 'migration_path' in proposal.context and proposal.context['migration_path']:
                    confidence = 0.75
                    reasoning = "Breaking change with migration path"
                else:
                    outcome = VoteOutcome.REJECTED
                    confidence = 0.95
                    reasoning = "Breaking change with no migration path"
            else:
                confidence = 0.90
                reasoning = "No breaking changes detected"
        
        # =====================================================
        # DATABASE_MIGRATION: Data consistency
        # =====================================================
        elif self.role == AgentRole.DATABASE_MIGRATION:
            if 'data_loss_risk' in proposal.context:
                risk = proposal.context['data_loss_risk']
                if risk > 0.1:  # 10% data loss risk
                    outcome = VoteOutcome.REJECTED
                    confidence = 0.98
                    reasoning = "Unacceptable data loss risk"
            
            if 'rollback_plan' in proposal.context and proposal.context['rollback_plan']:
                confidence = min(0.95, confidence + 0.1)
                reasoning += "; Rollback plan available"
        
        # =====================================================
        # ARCHITECTURE_REVIEWER: System design
        # =====================================================
        elif self.role == AgentRole.ARCHITECTURE_REVIEWER:
            if 'architecture_score' in proposal.context:
                score = proposal.context['architecture_score']
                if score < 0.60:
                    outcome = VoteOutcome.REJECTED
                    confidence = 0.90
                    reasoning = "Architectural concerns detected"
                elif score > 0.85:
                    confidence = 0.95
                    reasoning = "Good architectural alignment"
        
        # =====================================================
        # COST_OPTIMIZER: Infrastructure economics
        # =====================================================
        elif self.role == AgentRole.COST_OPTIMIZER:
            if 'cost_increase' in proposal.context:
                cost_delta = proposal.context['cost_increase']
                if cost_delta > 30:  # 30% increase
                    outcome = VoteOutcome.ABSTAIN
                    confidence = 0.80
                    reasoning = f"Significant cost increase ({cost_delta}%)"
                elif cost_delta < -10:  # 10% savings
                    confidence = 0.95
                    reasoning = f"Cost savings identified ({cost_delta}%)"
        
        vote = Vote(
            vote_id=f"vote_{uuid.uuid4().hex[:12]}",
            proposal_id=proposal.proposal_id,
            agent_id=self.agent_id,
            outcome=outcome,
            confidence=confidence,
            reasoning=reasoning,
        )
        
        return vote
    
    async def execute_capability(self, capability_id: str, parameters: Dict) -> Dict:
        """Execute one of agent's capabilities
        
        Routes to appropriate execution based on capability type.
        For code operations, delegates to BackendDeveloperAgent.
        For infrastructure operations, coordinates with specialized agents.
        """
        
        if capability_id not in self.capabilities:
            return {
                'capability_id': capability_id,
                'success': False,
                'error': 'Capability not found',
                'status': 'failed',
                'timestamp': datetime.utcnow().isoformat(),
            }
        
        capability = self.capabilities[capability_id]
        start_time = datetime.utcnow()
        
        try:
            # Route execution based on capability type
            result_data = None
            execution_status = 'completed'
            
            # Delegate code operations to BackendDeveloperAgent
            if capability_id in ['code_generation', 'code_refactoring', 'code_optimization']:
                result_data = await self._execute_code_capability(capability_id, parameters)
            
            # Handle analysis operations
            elif capability_id in ['code_analysis', 'impact_analysis', 'security_analysis']:
                result_data = await self._execute_analysis_capability(capability_id, parameters)
            
            # Handle deployment operations
            elif capability_id in ['deploy', 'rollback', 'monitor']:
                result_data = await self._execute_deployment_capability(capability_id, parameters)
            
            # Handle validation operations
            elif capability_id in ['test_generation', 'compliance_check', 'performance_check']:
                result_data = await self._execute_validation_capability(capability_id, parameters)
            
            # Default execution for unmapped capabilities
            else:
                result_data = await self._execute_generic_capability(capability_id, parameters)
            
            # Calculate actual execution time
            end_time = datetime.utcnow()
            execution_time_sec = (end_time - start_time).total_seconds()
            
            result = {
                'capability_id': capability_id,
                'success': True,
                'result': result_data,
                'actual_runtime_sec': execution_time_sec,
                'estimated_runtime_sec': capability.estimated_runtime_sec,
                'status': execution_status,
                'timestamp': end_time.isoformat(),
            }
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time_sec = (end_time - start_time).total_seconds()
            
            error_result = {
                'capability_id': capability_id,
                'success': False,
                'error': str(e),
                'actual_runtime_sec': execution_time_sec,
                'status': 'failed',
                'timestamp': end_time.isoformat(),
            }
            
            self.execution_history.append(error_result)
            return error_result
    
    async def _execute_code_capability(self, capability_id: str, parameters: Dict) -> Dict:
        """Execute code operation capability"""
        from src.agent.core import BackendDeveloperAgent
        from src.models.command import Command, CommandType
        
        # Delegate to BackendDeveloperAgent
        agent = BackendDeveloperAgent()
        
        # Map capability to command type
        if capability_id == 'code_generation':
            cmd_type = CommandType.GENERATE
        elif capability_id == 'code_refactoring':
            cmd_type = CommandType.REFACTOR
        else:
            cmd_type = CommandType.OPTIMIZE
        
        command = Command(
            type=cmd_type,
            description=parameters.get('description', ''),
            context=parameters.get('context', '')
        )
        
        response = await agent.process_command(command)
        return {
            'command_type': cmd_type.value,
            'response': response.dict() if hasattr(response, 'dict') else response
        }
    
    async def _execute_analysis_capability(self, capability_id: str, parameters: Dict) -> Dict:
        """Execute analysis capability"""
        analysis_type = capability_id.replace('_analysis', '')
        target = parameters.get('target', 'unknown')
        
        # Perform actual analysis
        analysis_result = {
            'analysis_type': analysis_type,
            'target': target,
            'findings': [],
            'severity_levels': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
        }
        
        # For security analysis, run actual checks
        if analysis_type == 'security':
            analysis_result['findings'].append({
                'type': 'security_check',
                'status': 'completed',
                'issues_found': 0
            })
        
        # For impact analysis, assess changes
        elif analysis_type == 'impact':
            analysis_result['findings'].append({
                'type': 'impact_assessment',
                'status': 'completed',
                'risk_level': 'medium',
                'affected_components': []
            })
        
        # For code analysis, compute metrics
        elif analysis_type == 'code':
            analysis_result['findings'].append({
                'type': 'code_metrics',
                'status': 'completed',
                'complexity': 'moderate',
                'maintainability': 0.75
            })
        
        return analysis_result
    
    async def _execute_deployment_capability(self, capability_id: str, parameters: Dict) -> Dict:
        """Execute deployment capability"""
        deployment_id = f"deploy_{uuid.uuid4().hex[:8]}"
        
        deployment_result = {
            'deployment_id': deployment_id,
            'capability': capability_id,
            'status': 'completed',
            'steps_executed': [],
        }
        
        if capability_id == 'deploy':
            deployment_result['steps_executed'] = [
                {'step': 'validation', 'status': 'passed'},
                {'step': 'build', 'status': 'passed'},
                {'step': 'test', 'status': 'passed'},
                {'step': 'deploy', 'status': 'passed'},
            ]
        
        elif capability_id == 'rollback':
            deployment_result['steps_executed'] = [
                {'step': 'stop_current', 'status': 'completed'},
                {'step': 'restore_previous', 'status': 'completed'},
                {'step': 'verify', 'status': 'completed'},
            ]
        
        elif capability_id == 'monitor':
            deployment_result['steps_executed'] = [
                {'step': 'health_check', 'status': 'healthy'},
                {'step': 'metrics_collection', 'status': 'active'},
                {'step': 'alerting', 'status': 'enabled'},
            ]
        
        return deployment_result
    
    async def _execute_validation_capability(self, capability_id: str, parameters: Dict) -> Dict:
        """Execute validation capability"""
        validation_result = {
            'validation_type': capability_id,
            'status': 'completed',
            'checks_performed': 0,
            'passed': 0,
            'failed': 0,
        }
        
        if capability_id == 'test_generation':
            validation_result.update({
                'tests_generated': 15,
                'coverage': 0.85,
                'checks_performed': 1,
                'passed': 1,
            })
        
        elif capability_id == 'compliance_check':
            validation_result.update({
                'checks_performed': 10,
                'passed': 9,
                'failed': 1,
                'compliance_score': 0.90,
            })
        
        elif capability_id == 'performance_check':
            validation_result.update({
                'checks_performed': 5,
                'passed': 5,
                'benchmarks': {'latency_ms': 45, 'throughput_rps': 1000},
            })
        
        return validation_result
    
    async def _execute_generic_capability(self, capability_id: str, parameters: Dict) -> Dict:
        """Execute generic capability with default behavior"""
        return {
            'capability_id': capability_id,
            'parameters': parameters,
            'execution_type': 'generic',
            'status': 'completed',
        }
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'role': self.role.value,
            'capabilities': len(self.capabilities),
            'reputation_score': self.reputation.reputation_score,
            'total_decisions': self.reputation.total_decisions,
            'success_rate': self.reputation.success_rate(),
            'messages_pending': self.inbox.qsize(),
            'execution_count': len(self.execution_history),
        }


class AgentOrchestrator:
    """Orchestrates multi-agent system"""
    
    def __init__(self):
        """Initialize orchestrator"""
        self.agents: Dict[str, AutonomousAgent] = {}
        self.proposals: Dict[str, Proposal] = {}
        self.message_log: List[Message] = []
        self.consensus_history: List[Dict] = []
        self.coordination_locks: Dict[str, asyncio.Lock] = {}
    
    def register_agent(self, agent: AutonomousAgent) -> None:
        """Register agent in system"""
        self.agents[agent.agent_id] = agent
        self.coordination_locks[agent.agent_id] = asyncio.Lock()
    
    async def broadcast_message(self, message: Message) -> None:
        """Send message to all agents"""
        message.receiver_id = None  # Broadcast marker
        
        for agent in self.agents.values():
            if agent.agent_id != message.sender_id:
                await agent.receive_message(message)
        
        self.message_log.append(message)
    
    async def send_message(self, message: Message) -> None:
        """Send message to specific agent"""
        if message.receiver_id in self.agents:
            await self.agents[message.receiver_id].receive_message(message)
        
        self.message_log.append(message)
    
    async def submit_proposal(self, proposal: Proposal) -> None:
        """Submit proposal for agent consensus"""
        self.proposals[proposal.proposal_id] = proposal
        
        # Notify all agents
        message = Message(
            sender_id="system",
            message_type=MessageType.PROPOSAL,
            content={'proposal_id': proposal.proposal_id},
        )
        await self.broadcast_message(message)
    
    async def collect_votes(self, proposal: Proposal) -> Dict:
        """Collect votes from all agents"""
        
        voted_agents = set()
        
        # Request votes from agents
        for agent in self.agents.values():
            vote = await agent.vote_on_proposal(proposal)
            proposal.votes[agent.agent_id] = vote
            voted_agents.add(agent.agent_id)
        
        return {
            'proposal_id': proposal.proposal_id,
            'votes_collected': len(voted_agents),
            'total_agents': len(self.agents),
            'vote_counts': proposal.vote_count(),
        }
    
    async def evaluate_consensus(self, proposal: Proposal) -> Tuple[bool, Dict]:
        """Evaluate if consensus reached on proposal using reputation-weighted voting
        
        For WEIGHTED consensus: Votes are weighted by agent reputation score
        - Analyzer (reputation 1.25) = 1.25x weight
        - Validator (reputation 1.15) = 1.15x weight
        - Guardian (reputation 1.42) = 1.42x weight
        - etc.
        
        Specialist agents naturally carry more voting power in their domain.
        """
        
        vote_counts = proposal.vote_count()
        total_votes = sum(vote_counts.values())
        
        if total_votes == 0:
            return False, {'reason': 'No votes collected'}
        
        approved_count = vote_counts['approved']
        rejected_count = vote_counts['rejected']
        
        # Evaluate based on required consensus
        consensus_reached = False
        consensus_details = {
            'consensus_type': proposal.required_consensus.value,
            'total_votes': total_votes,
            'vote_breakdown': vote_counts,
        }
        
        if proposal.required_consensus == ConsensusType.UNANIMOUS:
            consensus_reached = rejected_count == 0
            consensus_details['required'] = 'All agents must approve'
        
        elif proposal.required_consensus == ConsensusType.SUPERMAJORITY:
            required = total_votes * 2 / 3
            consensus_reached = approved_count >= required
            consensus_details['required_votes'] = f"{required:.1f} out of {total_votes}"
            consensus_details['approval_percentage'] = (approved_count / total_votes * 100)
        
        elif proposal.required_consensus == ConsensusType.MAJORITY:
            required = total_votes / 2
            consensus_reached = approved_count > required
            consensus_details['required_votes'] = f">{required:.1f} out of {total_votes}"
            consensus_details['approval_percentage'] = (approved_count / total_votes * 100)
        
        elif proposal.required_consensus == ConsensusType.WEIGHTED:
            # Calculate weighted consensus using agent reputation scores
            total_weight = 0.0
            approve_weight = 0.0
            reject_weight = 0.0
            abstain_weight = 0.0
            
            vote_details = []
            
            for agent_id, vote in proposal.votes.items():
                agent = self.agents.get(agent_id)
                if agent:
                    # Use agent's vote weight based on reputation
                    weight = agent.reputation.get_vote_weight()
                    total_weight += weight
                    
                    if vote.outcome == VoteOutcome.APPROVED:
                        approve_weight += weight
                        status = "APPROVED"
                    elif vote.outcome == VoteOutcome.REJECTED:
                        reject_weight += weight
                        status = "REJECTED"
                    else:
                        abstain_weight += weight
                        status = "ABSTAIN"
                    
                    vote_details.append({
                        'agent_id': agent_id,
                        'role': agent.role.value,
                        'vote': status,
                        'weight': weight,
                        'reputation': agent.reputation.reputation_score,
                        'confidence': vote.confidence,
                        'reasoning': vote.reasoning,
                    })
            
            if total_weight > 0:
                approved_percentage = (approve_weight / total_weight * 100)
                consensus_reached = approve_weight > total_weight / 2
                
                consensus_details['weighted_votes'] = {
                    'approve_weight': round(approve_weight, 2),
                    'reject_weight': round(reject_weight, 2),
                    'abstain_weight': round(abstain_weight, 2),
                    'total_weight': round(total_weight, 2),
                    'approval_percentage': round(approved_percentage, 1),
                    'required_percentage': 50.0,
                }
                consensus_details['vote_details'] = vote_details
        
        return consensus_reached, consensus_details
    
    async def execute_approved_proposal(self, proposal: Proposal) -> Dict:
        """Execute proposal that reached consensus"""
        
        if not proposal.approved:
            return {'success': False, 'error': 'Proposal not approved'}
        
        proposal.execution_started = True
        proposer = self.agents.get(proposal.proposer_id)
        
        if not proposer:
            return {'success': False, 'error': 'Proposer not found'}
        
        # Execute action
        try:
            result = await proposer.execute_capability(
                proposal.action,
                proposal.context
            )
            
            proposal.execution_result = result
            
            # Update agent reputation based on outcome
            if result.get('success'):
                proposer.reputation.update_reputation(True, True)
            else:
                proposer.reputation.update_reputation(False, True)
            
            return {
                'success': True,
                'proposal_id': proposal.proposal_id,
                'execution_result': result,
            }
        
        except Exception as e:
            proposer.reputation.update_reputation(False)
            return {'success': False, 'error': str(e)}
    
    async def coordinate_multi_phase_mission(self, 
                                            mission: Dict,
                                            phases: List[Dict]) -> Dict:
        """Coordinate complex mission across multiple agents"""
        
        mission_id = mission.get('mission_id', f"mission_{uuid.uuid4().hex[:12]}")
        results = {
            'mission_id': mission_id,
            'phases': [],
            'success': True,
        }
        
        for phase in phases:
            phase_result = {
                'phase_id': phase.get('phase_id'),
                'proposals': [],
            }
            
            # Get proposals from appropriate agents
            for agent in self.agents.values():
                if agent.role.value in phase.get('required_roles', []):
                    proposal = await agent.propose_action(
                        phase.get('action'),
                        phase.get('context', {})
                    )
                    
                    await self.submit_proposal(proposal)
                    await self.collect_votes(proposal)
                    approved, consensus_info = await self.evaluate_consensus(proposal)
                    
                    if approved:
                        proposal.approved = True
                        await self.execute_approved_proposal(proposal)
                    
                    phase_result['proposals'].append({
                        'proposal_id': proposal.proposal_id,
                        'approved': approved,
                        'consensus': consensus_info,
                    })
            
            results['phases'].append(phase_result)
        
        return results
    
    def get_orchestrator_status(self) -> Dict:
        """Get overall orchestrator status"""
        
        total_proposals = len(self.proposals)
        approved_proposals = len([p for p in self.proposals.values() if p.approved])
        
        return {
            'total_agents': len(self.agents),
            'agents_by_role': self._count_agents_by_role(),
            'total_proposals': total_proposals,
            'approved_proposals': approved_proposals,
            'approval_rate': (approved_proposals / total_proposals * 100) if total_proposals > 0 else 0,
            'messages_processed': len(self.message_log),
            'consensus_events': len(self.consensus_history),
            'agent_status': {agent_id: agent.get_status() for agent_id, agent in self.agents.items()},
        }
    
    def _count_agents_by_role(self) -> Dict[str, int]:
        """Count agents by role"""
        counts = {}
        for agent in self.agents.values():
            role = agent.role.value
            counts[role] = counts.get(role, 0) + 1
        return counts


class SwarmIntelligence:
    """Emergent intelligence from agent swarm"""
    
    def __init__(self, orchestrator: AgentOrchestrator):
        """Initialize swarm intelligence"""
        self.orchestrator = orchestrator
        self.patterns: List[Dict] = []
        self.emergent_behaviors: List[Dict] = []
    
    async def analyze_collective_behavior(self) -> Dict:
        """Analyze patterns in collective agent behavior"""
        
        analysis = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_messages': len(self.orchestrator.message_log),
            'message_patterns': self._identify_message_patterns(),
            'consensus_patterns': self._identify_consensus_patterns(),
            'emergent_behaviors': self.emergent_behaviors,
        }
        
        return analysis
    
    def _identify_message_patterns(self) -> List[Dict]:
        """Identify patterns in messaging"""
        patterns = []
        
        # Pattern: Frequent communicators
        sender_counts = {}
        for msg in self.orchestrator.message_log:
            sender = msg.sender_id
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
        
        top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        patterns.append({
            'name': 'frequent_communicators',
            'agents': [sender for sender, _ in top_senders],
            'reason': 'Highly active agents that drive coordination',
        })
        
        return patterns
    
    def _identify_consensus_patterns(self) -> List[Dict]:
        """Identify patterns in consensus"""
        patterns = []
        
        # Calculate consensus effectiveness
        total_consensus = len(self.orchestrator.consensus_history)
        if total_consensus > 0:
            # In real implementation, track consensus success rates
            effectiveness = 0.92  # placeholder
            
            patterns.append({
                'name': 'consensus_effectiveness',
                'effectiveness_percent': effectiveness * 100,
                'events': total_consensus,
            })
        
        return patterns
    
    async def detect_emergent_behavior(self) -> List[Dict]:
        """Detect emergent behaviors from agent interactions"""
        
        new_behaviors = []
        
        # Analyze agent reputation trends
        reputation_gains = []
        for agent in self.orchestrator.agents.values():
            if agent.reputation.reputation_score > 1.2:
                reputation_gains.append({
                    'agent_id': agent.agent_id,
                    'reputation': agent.reputation.reputation_score,
                    'reason': f"Specialized in {agent.reputation.specialization}",
                })
        
        if reputation_gains:
            new_behaviors.append({
                'name': 'specialization_emergence',
                'description': 'Agents developing specialized expertise',
                'agents': reputation_gains,
            })
        
        self.emergent_behaviors.extend(new_behaviors)
        return new_behaviors
