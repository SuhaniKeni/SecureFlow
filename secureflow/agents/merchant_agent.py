import datetime
from typing import Optional
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
from secureflow.engines.merchant_engine import MerchantConsistencyEngine

class MerchantSecurityAgent(BaseSecurityAgent):
    """Specialist Security Agent for evaluating merchant identity and destination consistency.
    
    STRICT BOUNDARY:
      - Investigates identity alignment between claimed merchant names and actual recipient account holders.
      - Produces structured AgentFinding and AgentEvidenceItem output.
      - MUST NEVER execute payments or override ProtectionDecisionEngine rules.
    """

    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(
            agent_id="merchant_security_agent",
            agent_name="Merchant & Recipient Security Specialist Agent",
            version="1.0.0",
            capabilities=["merchant_identity_resolution", "domain_consistency_check", "recipient_age_assessment"]
        )
        self.db = db_session
        self.engine = MerchantConsistencyEngine(db_session=db_session)

    def _analyze(
        self, 
        request: AgentExecutionRequest, 
        context: AgentExecutionContext
    ) -> AgentExecutionResult:
        """Executes merchant consistency investigation using bounded internal tools."""
        db = request.context_data.get("db_session") or self.db
        
        # 1. Execute Merchant Consistency Analysis Tool
        analysis = self.engine.analyze_consistency(
            claimed_merchant=request.claimed_merchant,
            recipient_id=request.recipient_id,
            destination_url=request.url,
            db_session=db
        )

        signal = analysis.get("signal", "unverified_destination")
        raw_sev = analysis.get("severity", "medium").upper()

        # Map severity string to SeverityLevel Enum
        try:
            severity = SeverityLevel[raw_sev]
        except KeyError:
            severity = SeverityLevel.MEDIUM

        confidence = float(analysis.get("risk_score", 0.50))
        # Ensure confidence is within valid range [0.0, 1.0]
        confidence = max(0.0, min(1.0, confidence))

        details = analysis.get("consistency_details", {})
        actual_name = details.get("actual_recipient_name", request.recipient_id)
        evidence_msg = analysis.get("evidence", f"Evaluated recipient '{request.recipient_id}'.")

        # 2. Determine Bounded Action Proposal
        if signal in ["merchant_identity_mismatch", "unregistered_recipient"]:
            proposed_action = ProposedSecurityAction.HOLD
            recommendation = "Investigate payee account identity and confirm business legitimacy."
        elif signal == "domain_mismatch":
            proposed_action = ProposedSecurityAction.BLOCK
            recommendation = "Verify destination URL domain matches official merchant domain."
        elif signal in ["newly_observed_recipient", "unverified_destination"]:
            proposed_action = ProposedSecurityAction.VERIFY
            recommendation = "Request customer step-up verification before completing payment."
        else:
            proposed_action = ProposedSecurityAction.ALLOW
            recommendation = "Merchant identity matches verified business profile."

        # 3. Create Structured Agent Finding
        finding = AgentFinding(
            agent_id=self.agent_id,
            finding_type=signal,
            severity=severity,
            confidence=confidence,
            evidence=evidence_msg,
            source=self.agent_name,
            explanation=(
                f"Claimed merchant '{request.claimed_merchant or 'Payee'}' assessed against actual payee '{actual_name}'. "
                f"Identity similarity score: {details.get('identity_similarity_score', 0.0)}."
            ),
            recommended_next_investigation=recommendation,
            transaction_id=request.transaction_id
        )

        # 4. Create Structured Agent Evidence Item (Traceable Provenance)
        evidence_item = AgentEvidenceItem(
            source_agent_or_engine=self.agent_id,
            signal_type=signal,
            severity=severity,
            confidence=confidence,
            description=evidence_msg,
            is_agent_generated=True,
            transaction_id=request.transaction_id,
            supporting_data=details
        )

        return AgentExecutionResult(
            request_id=request.request_id,
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETED,
            proposed_action=proposed_action,
            findings=[finding],
            evidence_items=[evidence_item]
        )
