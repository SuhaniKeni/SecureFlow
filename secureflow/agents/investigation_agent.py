import time
import datetime
from typing import Optional, List, Dict, Any
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
    InvestigationResult,
    AgentExecutionContext,
)
from secureflow.db.models import Transaction, Customer, Recipient

class InvestigationAgent(BaseSecurityAgent):
    """Specialist Security Agent for selective, dynamic secondary risk investigation.
    
    STRICT BOUNDARY:
      - Evaluates whether initial security signals are ambiguous and require targeted secondary checks.
      - Uses bounded, read-only internal query tools.
      - Does NOT fabricate evidence or execute payments.
    """

    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(
            agent_id="investigation_agent",
            agent_name="Dynamic Secondary Security Investigation Agent",
            version="1.0.0",
            capabilities=["selective_investigation", "velocity_analysis", "recipient_history_lookup", "behavior_context_query"]
        )
        self.db = db_session

    def _analyze(
        self, 
        request: AgentExecutionRequest, 
        context: AgentExecutionContext
    ) -> AgentExecutionResult:
        """Evaluates whether secondary investigation is required and executes bounded checks."""
        start_time = time.perf_counter()
        db = request.context_data.get("db_session") or self.db
        initial_evidence = request.context_data.get("initial_evidence", [])

        # 1. Evaluate Converging Threat vs Ambiguity Signals
        has_phishing_url = any(e.get("signal_type") == "phishing_domain" or e.get("severity") in ["high", "critical"] for e in initial_evidence if e.get("source") in ["url_intelligence_engine", "url_security_agent"])
        has_scam_nlp = any(e.get("signal_type") == "scam_context_detected" for e in initial_evidence if e.get("source") in ["scam_nlp_engine"])
        has_merchant_mismatch = any(e.get("signal_type") in ["merchant_identity_mismatch", "domain_mismatch"] for e in initial_evidence)
        
        is_high_value = request.amount >= 25000.00
        is_new_recipient = any(e.get("signal_type") in ["newly_observed_recipient", "unregistered_recipient", "unverified_destination"] for e in initial_evidence)

        requested_checks: List[str] = []
        findings: List[AgentFinding] = []
        evidence_items: List[AgentEvidenceItem] = []
        
        # 2. Decision Logic: Is secondary investigation necessary?
        if (has_phishing_url and has_scam_nlp) or (has_phishing_url and has_merchant_mismatch):
            # CASE A: Strong converging threat signals -> Investigation unnecessary
            investigation_required = False
            reason_summary = "Strong converging threat evidence already exists; additional secondary investigation is unnecessary."
            proposed_action = ProposedSecurityAction.BLOCK
        elif is_high_value or is_new_recipient:
            # CASE B: Ambiguous high-value / new recipient -> Targeted secondary investigation required
            investigation_required = True
            reason_summary = "Initial payment signals exhibit high-value or recipient ambiguity; performing targeted secondary checks."
            proposed_action = ProposedSecurityAction.INVESTIGATE
            
            # Execute bounded, read-only tools
            if db:
                if is_high_value:
                    requested_checks.append("customer_historical_baseline_query")
                    cust_findings, cust_ev = self.tool_query_customer_history(request.customer_id, request.amount, request.transaction_id, db)
                    findings.extend(cust_findings)
                    evidence_items.extend(cust_ev)

                requested_checks.append("recipient_velocity_history_query")
                rec_findings, rec_ev = self.tool_query_recipient_history(request.recipient_id, request.transaction_id, db)
                findings.extend(rec_findings)
                evidence_items.extend(rec_ev)
            else:
                reason_summary += " (Historical database session unavailable; using heuristic evidence parameters)."
        else:
            # CASE C: Clean legitimate payment -> Investigation unnecessary
            investigation_required = False
            reason_summary = "Payment parameters match expected low-risk baseline; secondary investigation not required."
            proposed_action = ProposedSecurityAction.NO_ACTION

        # 3. Create Primary Finding
        findings.append(
            AgentFinding(
                agent_id=self.agent_id,
                finding_type="secondary_investigation_evaluation",
                severity=SeverityLevel.INFO if not investigation_required else SeverityLevel.MEDIUM,
                confidence=0.90,
                evidence=reason_summary,
                source=self.agent_name,
                explanation=f"Investigation Required: {investigation_required}. Requested checks: {requested_checks or ['none']}.",
                recommended_next_investigation="Proceed to Evidence Aggregator for final policy evaluation.",
                transaction_id=request.transaction_id
            )
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 4. Construct InvestigationResult Sub-Schema
        inv_result = InvestigationResult(
            investigation_id=f"INV-{request.request_id}",
            requesting_agent_id="orchestrator",
            target_agent_id=self.agent_id,
            status=AgentStatus.COMPLETED,
            findings=findings,
            additional_evidence=evidence_items,
            execution_time_ms=elapsed_ms
        )

        return AgentExecutionResult(
            request_id=request.request_id,
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETED,
            proposed_action=proposed_action,
            findings=findings,
            evidence_items=evidence_items,
            execution_time_ms=elapsed_ms
        )

    # =========================================================================
    # SAFE READ-ONLY INTERNAL INVESTIGATION TOOLS
    # =========================================================================

    def tool_query_customer_history(
        self, 
        customer_id: str, 
        current_amount: float, 
        tx_id: str, 
        db: Session
    ) -> tuple[List[AgentFinding], List[AgentEvidenceItem]]:
        """Tool 1: Queries customer historical baseline and amount z-score (Read-Only)."""
        findings, items = [], []
        cust = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if cust:
            avg_amt = cust.normal_avg_amount or 1000.0
            std_amt = cust.normal_std_amount or 500.0
            z_score = abs(current_amount - avg_amt) / (std_amt + 1e-5)
            
            sev = SeverityLevel.HIGH if z_score > 5.0 else (SeverityLevel.MEDIUM if z_score > 2.5 else SeverityLevel.LOW)
            desc = f"Customer '{customer_id}' historical average Rs {avg_amt:.2f}. Current transaction Rs {current_amount:.2f} (Z-score: {z_score:.2f})."
            
            findings.append(
                AgentFinding(
                    agent_id=self.agent_id,
                    finding_type="behavioral_zscore_query",
                    severity=sev,
                    confidence=0.85,
                    evidence=desc,
                    source="Customer History Query Tool",
                    explanation="Secondary investigation queried customer transaction baseline.",
                    transaction_id=tx_id
                )
            )
            items.append(
                AgentEvidenceItem(
                    source_agent_or_engine=self.agent_id,
                    signal_type="customer_baseline_query",
                    severity=sev,
                    confidence=0.85,
                    description=desc,
                    is_agent_generated=True,
                    transaction_id=tx_id,
                    supporting_data={"z_score": z_score, "avg_amount": avg_amt}
                )
            )
        return findings, items

    def tool_query_recipient_history(
        self, 
        recipient_id: str, 
        tx_id: str, 
        db: Session
    ) -> tuple[List[AgentFinding], List[AgentEvidenceItem]]:
        """Tool 2: Queries recipient velocity and account history (Read-Only)."""
        findings, items = [], []
        rec = db.query(Recipient).filter(Recipient.recipient_id == recipient_id).first()
        account_age = rec.account_age_days if rec else 0
        
        tx_count = db.query(Transaction).filter(Transaction.recipient_id == recipient_id).count()
        sev = SeverityLevel.MEDIUM if account_age < 30 or tx_count < 5 else SeverityLevel.LOW
        desc = f"Recipient ID '{recipient_id}' account age: {account_age} days ({tx_count} prior system transactions)."

        findings.append(
            AgentFinding(
                agent_id=self.agent_id,
                finding_type="recipient_history_query",
                severity=sev,
                confidence=0.80,
                evidence=desc,
                source="Recipient History Query Tool",
                explanation="Secondary investigation queried recipient account age and transaction velocity.",
                transaction_id=tx_id
            )
        )
        items.append(
            AgentEvidenceItem(
                source_agent_or_engine=self.agent_id,
                signal_type="recipient_velocity_query",
                severity=sev,
                confidence=0.80,
                description=desc,
                is_agent_generated=True,
                transaction_id=tx_id,
                supporting_data={"account_age_days": account_age, "prior_transactions": tx_count}
            )
        )
        return findings, items
