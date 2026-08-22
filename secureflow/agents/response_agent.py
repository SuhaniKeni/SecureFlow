import uuid
import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from secureflow.agents.base import BaseSecurityAgent
from secureflow.agents.schemas import (
    AgentStatus,
    ProposedSecurityAction,
    SeverityLevel,
    AgentExecutionRequest,
    AgentExecutionResult,
    AgentFinding,
    AgentEvidenceItem,
    AgentExecutionContext,
)
from secureflow.db.models import ProtectionEvent, Transaction, Customer, Recipient

class SecurityResponseAgent(BaseSecurityAgent):
    """Specialist Security Agent for executing bounded operational security responses.
    
    STRICT BOUNDARY:
      - Receives the FINAL decision from the deterministic ProtectionDecisionEngine.
      - NEVER alters or overrides the policy decision.
      - Executes simulated/internal response workflows (protection event recording, customer notices, step-up verification requests).
      - ABSOLUTELY NO real money movement or external bank calls.
    """

    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(
            agent_id="response_agent",
            agent_name="Security Operational Response Agent",
            version="1.0.0",
            capabilities=["response_execution", "protection_event_logging", "customer_notice_generation", "policy_boundary_enforcement"]
        )
        self.db = db_session

    def _analyze(
        self, 
        request: AgentExecutionRequest, 
        context: AgentExecutionContext
    ) -> AgentExecutionResult:
        """Executes operational response workflow based strictly on the approved policy decision."""
        policy_decision = request.context_data.get("policy_decision", {})
        db = request.context_data.get("db_session")
        if db is None:
            db = self.db

        if not policy_decision or not isinstance(policy_decision, dict) or "action" not in policy_decision:
            raise ValueError("Security Violation: Response Agent requires a valid ProtectionDecisionEngine policy decision payload.")

        # 1. Enforce Policy Authority (Reject Policy Overrides)
        final_action_str = str(policy_decision.get("action", "BLOCK")).upper()
        
        # Validate action against supported enum
        try:
            approved_action = ProposedSecurityAction[final_action_str]
        except KeyError:
            raise ValueError(f"Unsupported policy decision action: '{final_action_str}'.")

        # 2. Execute Bounded Operational Response Workflows
        response_payload = self._execute_response_workflow(
            action=approved_action,
            policy_decision=policy_decision,
            request=request,
            db=db
        )

        # 3. Create Operational Finding
        finding = AgentFinding(
            agent_id=self.agent_id,
            finding_type=f"response_action_{approved_action.value.lower()}",
            severity=SeverityLevel.INFO if approved_action == ProposedSecurityAction.ALLOW else SeverityLevel.HIGH,
            confidence=1.0,
            evidence=response_payload["customer_message"],
            source=self.agent_name,
            explanation=(
                f"Executed operational response for policy action '{approved_action.value}'. "
                f"Protection Event Created: {response_payload.get('protection_event_created', False)}. "
                f"Rule Triggered: {policy_decision.get('audit_trail', {}).get('policy_rule_triggered', 'NONE')}."
            ),
            recommended_next_investigation=response_payload["remediation_recommendation"],
            transaction_id=request.transaction_id
        )

        # Store response details in context_data output
        result_evidence = AgentEvidenceItem(
            source_agent_or_engine=self.agent_id,
            signal_type=f"response_executed_{approved_action.value.lower()}",
            severity=SeverityLevel.INFO if approved_action == ProposedSecurityAction.ALLOW else SeverityLevel.HIGH,
            confidence=1.0,
            description=response_payload["customer_message"],
            is_agent_generated=True,
            transaction_id=request.transaction_id,
            supporting_data=response_payload
        )

        return AgentExecutionResult(
            request_id=request.request_id,
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETED,
            proposed_action=approved_action,
            findings=[finding],
            evidence_items=[result_evidence]
        )

    def _execute_response_workflow(
        self, 
        action: ProposedSecurityAction, 
        policy_decision: Dict[str, Any], 
        request: AgentExecutionRequest, 
        db: Optional[Session]
    ) -> Dict[str, Any]:
        """Executes operational response logic (recording protection events & generating notices)."""
        reasons = policy_decision.get("reasons", ["Payment context evaluated."])
        reason_summary = reasons[0] if reasons else "Payment context evaluated."
        event_id = None
        created_event = False

        if action == ProposedSecurityAction.ALLOW:
            customer_msg = "Payment verified and permitted."
            remediation = "Transaction completed cleanly."
            status_flag = "PERMITTED"

        elif action == ProposedSecurityAction.VERIFY:
            customer_msg = "Additional verification required before completing this payment."
            remediation = "Prompt customer for explicit two-step payment authorization."
            status_flag = "VERIFICATION_REQUIRED"

        elif action == ProposedSecurityAction.HOLD:
            customer_msg = "Payment is under security review due to recipient mismatch."
            remediation = "Flag transaction in Risk Operations Dashboard for analyst verification."
            status_flag = "HELD_FOR_REVIEW"
            event_id, created_event = self._record_protection_event(request, "HOLD", reason_summary, db)

        elif action == ProposedSecurityAction.BLOCK:
            customer_msg = "Payment stopped for customer protection."
            remediation = "Do not proceed with payment. Verify payee through official public channels."
            status_flag = "PAYMENT_BLOCKED"
            event_id, created_event = self._record_protection_event(request, "BLOCK", reason_summary, db)

        else:
            customer_msg = "Payment processing paused."
            remediation = "Awaiting security review."
            status_flag = "PAUSED"

        return {
            "transaction_id": request.transaction_id,
            "policy_action": action.value,
            "response_status": status_flag,
            "customer_message": customer_msg,
            "operational_explanation": reason_summary,
            "remediation_recommendation": remediation,
            "protection_event_created": created_event,
            "protection_event_id": event_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    def _record_protection_event(
        self, 
        request: AgentExecutionRequest, 
        action: str, 
        explanation: str, 
        db: Optional[Session]
    ) -> tuple[Optional[str], bool]:
        """Creates and persists a Protection Event record in SQLite DB if session is available."""
        event_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        if db:
            try:
                # 1. Check if Transaction record exists to satisfy FK constraint
                tx = db.query(Transaction).filter(Transaction.transaction_id == request.transaction_id).first()
                if not tx:
                    cust_id = request.customer_id if db.query(Customer).filter(Customer.customer_id == request.customer_id).first() else "CUST-001"
                    rec_id = request.recipient_id if db.query(Recipient).filter(Recipient.recipient_id == request.recipient_id).first() else "RCP-001"
                    tx = Transaction(
                        transaction_id=request.transaction_id,
                        customer_id=cust_id,
                        recipient_id=rec_id,
                        amount=request.amount,
                        status=action,
                        timestamp=datetime.datetime.now(datetime.timezone.utc)
                    )
                    db.add(tx)
                    db.flush()

                # 2. Record Protection Event
                evt = ProtectionEvent(
                    event_id=event_id,
                    transaction_id=request.transaction_id,
                    action=action,
                    evidence={"claimed_merchant": request.claimed_merchant, "amount": request.amount, "recipient_id": request.recipient_id},
                    explanation=explanation,
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                db.add(evt)
                db.commit()
                return event_id, True
            except Exception:
                db.rollback()
                return event_id, False
        return event_id, False
