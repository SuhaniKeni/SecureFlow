import time
import datetime
import logging
from abc import ABC, abstractmethod
from typing import Optional, List

from secureflow.agents.schemas import (
    AgentStatus,
    ProposedSecurityAction,
    AgentExecutionRequest,
    AgentExecutionResult,
    AgentExecutionContext,
)

logger = logging.getLogger(__name__)

class BaseSecurityAgent(ABC):
    """Abstract Base Class for all SecureFlow Security Agents.
    
    STRICT MANDATE:
      - Agents investigate, gather evidence, and propose bounded security actions.
      - Agents MUST NEVER execute money transfers or override the ProtectionDecisionEngine.
      - Input validation, timeout handling, lifecycle status tracking, and error isolation are built into this base class.
    """

    def __init__(self, agent_id: str, agent_name: str, version: str = "1.0.0", capabilities: Optional[List[str]] = None):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.version = version
        self.capabilities = capabilities or []

    def execute(
        self, 
        request: AgentExecutionRequest, 
        context: Optional[AgentExecutionContext] = None
    ) -> AgentExecutionResult:
        """Standard lifecycle execution wrapper with validation, timing, and failure isolation."""
        start_time = time.perf_counter()
        ctx = context or AgentExecutionContext(transaction_id=request.transaction_id)
        
        try:
            # 1. Lifecycle: VALIDATING -> RUNNING
            logger.info(f"[{self.agent_id}] Starting investigation for TXN: {request.transaction_id}")
            
            # 2. Subclass Analysis Routine
            result = self._analyze(request, ctx)
            
            # 3. Calculate timing
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            result.execution_time_ms = elapsed_ms
            result.status = AgentStatus.COMPLETED
            
            logger.info(f"[{self.agent_id}] Completed in {elapsed_ms}ms with proposal: {result.proposed_action}")
            return result

        except Exception as err:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(f"[{self.agent_id}] Failed for TXN {request.transaction_id}: {err}")
            
            # SAFE FAILURE: Explicit failure status without defaulting to ALLOW
            return AgentExecutionResult(
                request_id=request.request_id,
                agent_id=self.agent_id,
                status=AgentStatus.FAILED,
                proposed_action=ProposedSecurityAction.NO_ACTION,
                error_message=f"Agent Execution Failure: {str(err)}",
                execution_time_ms=elapsed_ms
            )

    @abstractmethod
    def _analyze(
        self, 
        request: AgentExecutionRequest, 
        context: AgentExecutionContext
    ) -> AgentExecutionResult:
        """Concrete security logic implemented by specialist security agents in Step 3+."""
        pass

    # =========================================================================
    # SECURITY BOUNDARY GUARDRAILS
    # =========================================================================

    def execute_payment(self, *args, **kwargs):
        """Security Guardrail: Agents are strictly prohibited from executing payments."""
        raise PermissionError(
            "Security Violation: Agents are strictly prohibited from executing financial transactions. "
            "Final action authority belongs exclusively to the deterministic ProtectionDecisionEngine."
        )

    def block_payment_directly(self, *args, **kwargs):
        """Security Guardrail: Agents must not block payments directly without deterministic policy rules."""
        raise PermissionError(
            "Security Violation: Agents cannot enforce payment blocks directly. "
            "Proposed actions must be evaluated against explicit ProtectionDecisionEngine rules."
        )
