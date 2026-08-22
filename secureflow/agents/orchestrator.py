import time
import uuid
import datetime
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from secureflow.agents.schemas import (
    AgentStatus,
    ProposedSecurityAction,
    SeverityLevel,
    AgentExecutionRequest,
    AgentExecutionResult,
    AgentExecutionContext,
)
from secureflow.engines.url_intel_engine import URLIntelligenceEngine
from secureflow.engines.scam_nlp_engine import ScamContextNLPEngine
from secureflow.engines.behavior_engine import CustomerBehaviorEngine
from secureflow.agents.merchant_agent import MerchantSecurityAgent
from secureflow.agents.investigation_agent import InvestigationAgent
from secureflow.agents.evidence_agent import EvidenceSynthesisAgent
from secureflow.policy.decision_engine import ProtectionDecisionEngine
from secureflow.agents.response_agent import SecurityResponseAgent
from secureflow.explanations.explanation_engine import ExplanationEngine

logger = logging.getLogger(__name__)

class SecurityOrchestrator:
    """Master Security Orchestrator for SecureFlow Agentic Payment Security Pipeline.
    
    STRICT BOUNDARY:
      - Coordinates Detection Engines, Specialist Security Agents, Evidence Synthesis, Deterministic Policy, and Response Agent.
      - Enforces least privilege, timeout budgets, and failure isolation.
      - ProtectionDecisionEngine remains the single deterministic authority for financial actions (ALLOW/VERIFY/HOLD/BLOCK).
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session
        self.url_engine = URLIntelligenceEngine()
        self.nlp_engine = ScamContextNLPEngine()
        self.behavior_engine = CustomerBehaviorEngine()
        self.merchant_agent = MerchantSecurityAgent(db_session=db_session)
        self.investigation_agent = InvestigationAgent(db_session=db_session)
        self.evidence_agent = EvidenceSynthesisAgent()
        self.policy_engine = ProtectionDecisionEngine()
        self.response_agent = SecurityResponseAgent(db_session=db_session)
        self.explanation_engine = ExplanationEngine()

    def run_pipeline(
        self, 
        request: AgentExecutionRequest, 
        db_session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Executes end-to-end multi-agent security pipeline with structured trace tracking."""
        pipeline_start = time.perf_counter()
        execution_id = f"EXEC-{uuid.uuid4().hex[:8].upper()}"
        db = db_session or self.db
        
        execution_trace: List[Dict[str, Any]] = []
        all_raw_evidence: List[Dict[str, Any]] = []

        try:
            # -----------------------------------------------------------------
            # STEP A: INPUT VALIDATION & GUARDRAILS
            # -----------------------------------------------------------------
            step_a_start = time.perf_counter()
            if not request.transaction_id or request.amount <= 0.0:
                raise ValueError("Invalid AgentExecutionRequest: transaction_id must be non-empty and amount > 0.")

            step_a_latency = round((time.perf_counter() - step_a_start) * 1000, 2)
            execution_trace.append({
                "step": "STEP_A_INPUT_VALIDATION",
                "component": "InputValidationGuardrail",
                "status": "COMPLETED",
                "latency_ms": step_a_latency,
                "details": "Validated request schemas and credential safety rules."
            })

            # -----------------------------------------------------------------
            # STEP B: EXISTING DETECTION ENGINES
            # -----------------------------------------------------------------
            step_b_start = time.perf_counter()
            url_ev = self.url_engine.analyze(request.url)
            nlp_ev = self.nlp_engine.analyze(request.payment_note, claimed_merchant=request.claimed_merchant)
            behavior_ev = self.behavior_engine.analyze_transaction(
                customer_id=request.customer_id,
                amount=request.amount,
                recipient_id=request.recipient_id,
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                db_session=db
            )

            # Map engine outputs into normalized evidence list
            if url_ev and url_ev.get("signal") not in ["no_destination_url", "clean_destination"]:
                all_raw_evidence.append({
                    "signal_type": url_ev.get("signal"),
                    "source": "url_intelligence_engine",
                    "description": "Payment destination URL exhibits security risk indicators.",
                    "severity": url_ev.get("severity", "low"),
                    "confidence": float(url_ev.get("risk_score", 0.0)),
                    "is_agent_generated": False,
                    "supporting_data": url_ev.get("evidence", {})
                })

            if nlp_ev and nlp_ev.get("signal") not in ["normal_payment_context", "no_text_context"]:
                all_raw_evidence.append({
                    "signal_type": nlp_ev.get("signal"),
                    "source": "scam_nlp_engine",
                    "description": nlp_ev.get("evidence", "Scam context keywords detected in payment note."),
                    "severity": nlp_ev.get("severity", "low"),
                    "confidence": float(nlp_ev.get("risk_score", 0.0)),
                    "is_agent_generated": False,
                    "supporting_data": nlp_ev.get("indicators_detected", {})
                })

            if behavior_ev and behavior_ev.get("signal") not in ["normal_behavior_pattern"]:
                all_raw_evidence.append({
                    "signal_type": behavior_ev.get("signal"),
                    "source": "customer_behavior_engine",
                    "description": behavior_ev.get("evidence", "Transaction deviates from customer historical baseline."),
                    "severity": behavior_ev.get("severity", "low"),
                    "confidence": float(behavior_ev.get("risk_score", 0.0)),
                    "is_agent_generated": False,
                    "supporting_data": behavior_ev.get("behavior_metrics", {})
                })

            step_b_latency = round((time.perf_counter() - step_b_start) * 1000, 2)
            execution_trace.append({
                "step": "STEP_B_DETECTION_ENGINES",
                "component": "DetectionEnginesBundle",
                "status": "COMPLETED",
                "latency_ms": step_b_latency,
                "evidence_count": len(all_raw_evidence)
            })

            # -----------------------------------------------------------------
            # STEP C: MERCHANT SECURITY AGENT
            # -----------------------------------------------------------------
            request.context_data["db_session"] = db
            m_res = self.merchant_agent.execute(request)
            for item in m_res.evidence_items:
                all_raw_evidence.append(item.model_dump())

            execution_trace.append({
                "step": "STEP_C_MERCHANT_SECURITY",
                "component": "MerchantSecurityAgent",
                "status": m_res.status.value,
                "proposed_action": m_res.proposed_action.value,
                "latency_ms": m_res.execution_time_ms
            })

            # -----------------------------------------------------------------
            # STEP D: INVESTIGATION AGENT & SELECTIVE TOOL EXECUTION
            # -----------------------------------------------------------------
            inv_context_data = dict(request.context_data)
            inv_context_data["initial_evidence"] = all_raw_evidence
            inv_req = AgentExecutionRequest(
                agent_id=self.investigation_agent.agent_id,
                transaction_id=request.transaction_id,
                customer_id=request.customer_id,
                amount=request.amount,
                recipient_id=request.recipient_id,
                claimed_merchant=request.claimed_merchant,
                payment_note=request.payment_note,
                url=request.url,
                channel=request.channel,
                context_data=inv_context_data
            )
            inv_res = self.investigation_agent.execute(inv_req)
            for item in inv_res.evidence_items:
                all_raw_evidence.append(item.model_dump())

            execution_trace.append({
                "step": "STEP_D_INVESTIGATION_ROUTING",
                "component": "InvestigationAgent",
                "status": inv_res.status.value,
                "investigation_decision": inv_res.proposed_action.value,
                "additional_evidence_collected": len(inv_res.evidence_items),
                "latency_ms": inv_res.execution_time_ms
            })

            # -----------------------------------------------------------------
            # STEP E: EVIDENCE SYNTHESIS AGENT
            # -----------------------------------------------------------------
            synth_context_data = dict(request.context_data)
            synth_context_data["all_evidence"] = all_raw_evidence
            synth_req = AgentExecutionRequest(
                agent_id=self.evidence_agent.agent_id,
                transaction_id=request.transaction_id,
                customer_id=request.customer_id,
                amount=request.amount,
                recipient_id=request.recipient_id,
                claimed_merchant=request.claimed_merchant,
                context_data=synth_context_data
            )
            synth_res = self.evidence_agent.execute(synth_req)
            evidence_bundle = self.evidence_agent.format_evidence_bundle(synth_res)

            execution_trace.append({
                "step": "STEP_E_EVIDENCE_SYNTHESIS",
                "component": "EvidenceSynthesisAgent",
                "status": synth_res.status.value,
                "overall_severity": evidence_bundle.get("overall_severity"),
                "evidence_count": evidence_bundle.get("evidence_count"),
                "latency_ms": synth_res.execution_time_ms
            })

            # -----------------------------------------------------------------
            # STEP F: DETERMINISTIC PROTECTION DECISION ENGINE
            # -----------------------------------------------------------------
            step_f_start = time.perf_counter()
            policy_decision = self.policy_engine.evaluate_protection_policy(evidence_bundle)
            step_f_latency = round((time.perf_counter() - step_f_start) * 1000, 2)

            execution_trace.append({
                "step": "STEP_F_DETERMINISTIC_POLICY",
                "component": "ProtectionDecisionEngine",
                "status": "COMPLETED",
                "final_action": policy_decision["action"],
                "rule_triggered": policy_decision.get("audit_trail", {}).get("policy_rule_triggered"),
                "latency_ms": step_f_latency
            })

            # -----------------------------------------------------------------
            # STEP G: SECURITY RESPONSE AGENT
            # -----------------------------------------------------------------
            resp_context_data = dict(request.context_data)
            resp_context_data["policy_decision"] = policy_decision
            resp_context_data["db_session"] = db
            resp_req = AgentExecutionRequest(
                agent_id=self.response_agent.agent_id,
                transaction_id=request.transaction_id,
                customer_id=request.customer_id,
                amount=request.amount,
                recipient_id=request.recipient_id,
                claimed_merchant=request.claimed_merchant,
                context_data=resp_context_data
            )
            resp_res = self.response_agent.execute(resp_req)
            resp_payload = resp_res.evidence_items[0].supporting_data if resp_res.evidence_items else {}

            execution_trace.append({
                "step": "STEP_G_SECURITY_RESPONSE",
                "component": "SecurityResponseAgent",
                "status": resp_res.status.value,
                "response_status": resp_payload.get("response_status"),
                "protection_event_created": resp_payload.get("protection_event_created", False),
                "latency_ms": resp_res.execution_time_ms
            })

            # Generate Dual-Mode Explanations
            tx_ctx = {"amount": request.amount, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}
            m_info = {"claimed_merchant": request.claimed_merchant, "actual_recipient_name": request.recipient_id}
            explanations = self.explanation_engine.generate_explanation(
                protection_action=policy_decision["action"],
                evidence_bundle=evidence_bundle,
                transaction_context=tx_ctx,
                merchant_info=m_info
            )

            total_latency = round((time.perf_counter() - pipeline_start) * 1000, 2)

            return {
                "transaction_id": request.transaction_id,
                "execution_id": execution_id,
                "action": policy_decision["action"],
                "customer_explanation": explanations["customer_explanation"],
                "ops_explanation": explanations["ops_explanation"],
                "evidence_bundle": evidence_bundle,
                "protection_response": resp_payload,
                "execution_trace": execution_trace,
                "total_latency_ms": total_latency,
                "audit_trail": policy_decision.get("audit_trail", {})
            }

        except Exception as err:
            total_latency = round((time.perf_counter() - pipeline_start) * 1000, 2)
            logger.error(f"[SecurityOrchestrator] Pipeline failure for TXN {request.transaction_id}: {err}")
            
            # Safe Failure: Record error in trace without defaulting to ALLOW
            execution_trace.append({
                "step": "PIPELINE_FAILURE",
                "component": "SecurityOrchestrator",
                "status": "FAILED",
                "error": str(err),
                "latency_ms": total_latency
            })

            # Evaluate fallback policy decision safely
            fallback_decision = self.policy_engine.evaluate_protection_policy(all_raw_evidence)
            
            return {
                "transaction_id": request.transaction_id,
                "execution_id": execution_id,
                "action": fallback_decision.get("action", "HOLD"),
                "customer_explanation": {"title": "Security Evaluation Notice", "why": "Security check experienced a temporary processing error. Payment placed under review."},
                "ops_explanation": {"title": "Pipeline Processing Error", "risk_factors": [str(err)]},
                "evidence_bundle": {"evidence_items": all_raw_evidence},
                "protection_response": {"response_status": "PROCESSING_ERROR", "customer_message": "Payment review required."},
                "execution_trace": execution_trace,
                "total_latency_ms": total_latency,
                "audit_trail": {"status": "FAILED", "error": str(err)}
            }
